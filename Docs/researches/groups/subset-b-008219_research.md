# subset-b-008219 research

Work item: `subset-b-008219`

This grouped report covers the requested OpenStack Swift profiling, recon, registry, request-helper, and ring files. Each source file section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/x_profile/html_viewer.py -->
# sources/object-store/openstack-swift/swift/common/middleware/x_profile/html_viewer.py

## Purpose
`html_viewer.py` is the presentation and export layer for Swift's development-only profiling middleware. It turns profile dumps collected by `ProfileLog` into an HTML form, HTML statistics table, raw profile output, JSON, CSV, ODS, source-code snippets, and optional matplotlib plots. It does not collect profiles itself; it sits behind `ProfileMiddleware` and delegates profile parsing and serialization to `Stats2`.

## Important APIs, types, and functions
The main type is `HTMLViewer(app_path, profile_module, profile_log)`. `render()` routes profiling UI/API requests based on WSGI method and `path_entry`: index requests, downloads, plots, clearing profiles, listing profile IDs, and per-function downloads. `index_page()` builds the HTML form and stats table. `download()` serializes profile data to `default`, `json`, `csv`, `ods`, or `python` source-view formats. `plot()` renders bar or pie charts from selected profile metrics. `format_source_code()` returns escaped source HTML for a `filename:lineno(function)` selector. `generate_stats_html()` emits the profile statistics table and links to per-function JSON and source views. Module templates define select boxes, form fields, and page layout; `format_dict` maps export formats to content types.

## Control flow and state behavior
`render()` normalizes query parameters with `_get_param()`, determines whether the action is `plot`, `download`, or `clear`, then resolves profile log files via `profile_log.get_logfiles()`. `/__profile__` GET/POST requests render a page or perform a form action. `/__profile__/...` GET requests either list profile IDs as JSON or download a selected profile/function. Clearing a profile calls `profile_log.clear()` and then the middleware-provided callback to renew the profiler.

The module has little durable state of its own. Persistent state is profile files on disk, owned by `ProfileLog`. Temporary state includes in-memory `Stats2` instances and, for plots, a temporary file used by matplotlib. Source-code formatting reads arbitrary `.py` files referenced by profile data and returns escaped HTML.

## Dependencies and integration points
It imports profile exceptions, `Stats2`, `html`, `os`, `re`, `string.Template`, `tempfile`, and optional `matplotlib`. It is constructed by `swift.common.middleware.xprofile.ProfileMiddleware` with the configured profile path, profiler module name, and shared `ProfileLog`. `Stats2` handles profile loading and output serialization. `ODFLIBNotInstalled`, `PLOTLIBNotInstalled`, `DataLoadFailure`, `NotFoundException`, `MethodNotAllowed`, and `ProfileException` become HTTP responses in the middleware.

## Risks and edge cases
The source-code view explicitly notes a security weakness: `format_source_code()` opens a profile-derived path if it ends in `.py`, so path disclosure/read risk depends on profile contents and local filesystem visibility. HTML generation mostly escapes function/source labels but template option values and filters should be treated carefully. Plot responses declare `image/jpg` while saving PNG bytes. `download()` wraps broad exceptions in `ProfileException`, which may obscure specific failures. `render()` appends CORS headers to direct GET downloads, exposing profile data to any origin. Missing optional dependencies disable plot or ODS export. Invalid `output_format` values can raise when indexing `format_dict`.

## Test signals
Useful tests should cover routing for index, profile-list JSON, direct download, per-function filters, clear callbacks, unsupported methods, missing log files, bad profile data, and optional dependency failures. Rendering tests should assert HTML escaping for function/source strings, selected option preservation, and source-code formatting behavior for invalid paths, non-Python files, missing files, and valid highlighted lines.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/x_profile/html_viewer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/x_profile/profile_model.py -->
# sources/object-store/openstack-swift/swift/common/middleware/x_profile/profile_model.py

## Purpose
`profile_model.py` provides the data model for xprofile output. `Stats2` extends `pstats.Stats` with JSON, CSV, and ODS serializers, while `ProfileLog` manages profile dump discovery, selection, atomic dump writes, and deletion. Together they are the persistence and serialization layer consumed by `HTMLViewer` and `ProfileMiddleware`.

## Important APIs, types, and functions
`Stats2` preserves the `pstats.Stats` API and adds `func_to_dict()`, `func_std_string()`, `to_json()`, `to_csv()`, and `to_ods()`. `to_json()` includes summary fields, selected functions, callees, callers, and timing metrics. `to_csv()` writes a simple CRLF-separated profile table. `to_ods()` creates an OpenDocument spreadsheet through optional `odfpy`. `ProfileLog(log_filename_prefix, dump_timestamp)` exposes `get_all_pids()`, `get_logfiles(id_or_name)`, `dump_profile(profiler, pid)`, and `clear(id_or_name)`.

## Control flow and state behavior
`Stats2` loads profile files through its `pstats.Stats` superclass. Each serializer starts from either the sorted function list or all stats keys, applies selection arguments with `eval_print_amount()`, then walks `self.stats`. `to_json()` calls `calc_callees()` and serializes nested caller/callee metrics, accommodating eventlet metrics that may be a tuple or a scalar. `ProfileLog` treats profile files as names beginning with `log_filename_prefix`; timestamped dumps use `PREFIX + pid + "-" + time.time()`. Dumps are written to `.tmp` first via `profiler.dump_stats()` and then renamed into place.

`get_logfiles('all')` returns either every non-temp profile file or, when `dump_timestamp` is true, the latest file per process id according to reverse-sorted profile ID strings. `current` maps to `os.getpid()`. `clear()` deletes the selected files if they exist.

## Dependencies and integration points
Dependencies include `glob`, `json`, `os`, `pstats`, `tempfile`, `time`, and optional `odfpy`. `HTMLViewer` constructs `Stats2` to render pages and exports. `ProfileMiddleware.dump_checkpoint()` calls `ProfileLog.dump_profile()` asynchronously from a green pool; `ProfileMiddleware.__del__()` and clear actions call `ProfileLog.clear()`.

## Risks and edge cases
The profile file selection logic assumes names after the prefix split cleanly into `process_id-timestamp`; malformed names can break `get_logfiles('all')` when timestamp mode is enabled. Reverse string sorting of timestamps generally works for decimal epoch strings but is not as explicit as numeric sorting. Profile files are trusted input to `pstats.Stats`, so corrupt files raise load failures upstream. `to_csv()` performs manual CSV construction without quoting function names. `to_ods()` depends on optional `odfpy` and writes values with mixed numeric/string types. Clear operations unlink whatever files match the prefix and selected profile id.

## Test signals
Tests should exercise non-timestamped and timestamped profile discovery, current/all/specific id selection, `.tmp` exclusion, atomic dump rename behavior, clear semantics, JSON caller/callee output for tuple and scalar metrics, CSV formatting, ODS dependency failure, and serializer selection filtering.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/x_profile/profile_model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/xprofile.py -->
# sources/object-store/openstack-swift/swift/common/middleware/xprofile.py

## Purpose
`xprofile.py` implements Swift's profiling WSGI middleware. It profiles normal application requests, periodically dumps profile data to disk, and exposes a small unauthenticated development UI/API under a configurable path such as `/__profile__`. The module docstring warns it is intended for development and testing, not production.

## Important APIs, types, and functions
`ProfileMiddleware(app, conf)` is the WSGI filter. It parses configuration such as `log_filename_prefix`, `dump_interval`, `dump_timestamp`, `flush_at_shutdown`, `path`, `unwind`, and `profile_module`. `__call__()` dispatches favicon requests, profile UI/API requests, and normal application requests. `_combine_body_qs()` merges request query parameters with URL-encoded POST body fields. `dump_checkpoint()` schedules periodic `ProfileLog.dump_profile()` calls. `renew_profile()` reinstantiates the configured profiler. `get_profiler(profile_module)` imports and creates a profiler, monkey-patching eventlet profile behavior when needed. `filter_factory()` is the paste-deploy entry point.

The module also defines `new_setup()`, `new_runctx()`, and `new_runcall()` monkey patches for `eventlet.green.profile.Profile`, plus two code strings: eager profiling consumes and closes the app iterator, lazy profiling profiles only iterator construction.

## Control flow and state behavior
Initialization creates the profile directory if missing, gets a Swift logger, constructs `ProfileLog` and `HTMLViewer`, creates a large green pool for asynchronous dumps, and delays the first dump until a request arrives. For profile UI requests, `__call__()` dumps a checkpoint, combines query/body parameters, calls `viewer.render()`, translates profile exceptions to HTTP status codes, encodes string content to bytes, and returns a one-element body list. For non-profile requests, the middleware runs either eager or lazy app execution under `self.profiler.runctx()`, then dumps a checkpoint and returns the profiled iterator.

Persistent state is the profile dump files written by `ProfileLog`. Runtime state includes the profiler object, dump timing, and green-pool tasks. `flush_at_shutdown` is unusual: `__del__()` clears the current process profile rather than forcing a dump.

## Dependencies and integration points
The middleware integrates with Swift WSGI paste configuration, `swift.common.swob.Request`, `swift.common.utils.get_logger`, `config_true_value`, eventlet concurrency/profile modules, and the x_profile viewer/model classes. Its output files are later parsed by `Stats2` and exposed by `HTMLViewer`. It uses the original `_thread` module via eventlet patcher to avoid monkey-patched thread identity in profiler setup.

## Risks and edge cases
The UI has no authentication, exposes profiling data, and accepts clear requests, so deployment in production is risky. `_combine_body_qs()` reads the entire request body for profile POSTs. Lazy mode may miss work done during iterator consumption; eager mode changes streaming behavior and resource use by materializing the entire app iterator. Monkey-patching eventlet profiler methods is process-global. `__call__()` returns plain strings in some error paths, which may rely on WSGI/server tolerance. Directory creation can fail on permissions. Asynchronous dump tasks may overlap under high request rates if dump intervals are small.

## Test signals
Tests should cover paste factory construction, normal request profiling in lazy and eager modes, profile path routing, exception-to-status mapping, dump throttling, POST body parameter merging, clear-and-renew behavior, eventlet monkey patch installation, directory creation failures, and profiler module import errors.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/xprofile.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/recon.py -->
# sources/object-store/openstack-swift/swift/common/recon.py

## Purpose
`recon.py` centralizes constants for Swift recon cache file names and the default recon cache directory. Recon files are small JSON-like operational status caches consumed by recon middleware/tools elsewhere in Swift.

## Important APIs, types, and functions
Constants include `RECON_RELINKER_FILE`, `RECON_OBJECT_FILE`, `RECON_CONTAINER_FILE`, `RECON_ACCOUNT_FILE`, `RECON_DRIVE_FILE`, and `DEFAULT_RECON_CACHE_PATH`. The only function, `server_type_to_recon_file(server_type)`, validates a server type and returns the corresponding `<server_type>.recon` filename.

## Control flow and state behavior
There is no mutable state or persistence in this module. `server_type_to_recon_file()` requires `server_type` to be a string whose lower-case value is one of `account`, `container`, or `object`; invalid values raise `ValueError`. Valid values are normalized to lower-case in the returned file name.

## Dependencies and integration points
The module has no imports. It is a shared naming point for object, container, account, drive, relinker, and recon cache code that need stable file names under `/var/cache/swift` unless configured otherwise.

## Risks and edge cases
The validation intentionally excludes `drive` and `relinker` from `server_type_to_recon_file()` even though constants exist for those recon files; callers must use constants for those. Non-string values, empty strings, and unknown server types raise a generic `ValueError('Invalid server_type')`.

## Test signals
Tests should assert case-insensitive mapping for account/container/object, rejection of drive/relinker/unknown values, rejection of non-string values, and stability of the exported constants.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/recon.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/registry.py -->
# sources/object-store/openstack-swift/swift/common/registry.py

## Purpose
`registry.py` is a small process-local registry for cluster capability information and logging redaction metadata. Middleware and subsystems register public and admin-only `/info` data, sensitive headers, and sensitive query parameters; consumers retrieve defensive copies or frozen views.

## Important APIs, types, and functions
`get_swift_info(admin=False, disallowed_sections=None)` returns a deep copy of `_swift_info`, optionally with an `admin` section containing `_swift_admin_info` and the requested disallowed sections. `register_swift_info(name='swift', admin=False, **kwargs)` registers key/value data in either public or admin storage. `get_sensitive_headers()` and `get_sensitive_params()` return frozensets. `register_sensitive_header(header)` lowercases and stores ASCII header names. `register_sensitive_param(query_param)` stores ASCII query parameter names case-sensitively.

## Control flow and state behavior
The module stores mutable process globals: `_swift_info`, `_swift_admin_info`, `_sensitive_headers`, and `_sensitive_params`. Public and admin info are nested by section name. `get_swift_info()` deep-copies public info, then walks dotted disallowed section paths and removes matching leaf keys before optionally attaching admin metadata. Registration rejects reserved section names and any dots in section names or keys, because dots are used only for disallowed-section path traversal.

Sensitive header/param registration validates type and ASCII encodability. Headers are normalized to lower-case for case-insensitive matching; query parameters preserve case.

## Dependencies and integration points
The only import is `copy.deepcopy`. The registry is used by Swift info endpoints and proxy logging redaction. The docstrings reference `swift.common.middleware.proxy_logging`, which reads sensitive header and parameter sets before logging. Middleware such as auth, tempurl, or s3api can register sensitive fields and capability details.

## Risks and edge cases
This is process-local mutable global state, so registrations depend on import/filter initialization order and are not automatically synchronized across worker processes. `get_swift_info()` protects callers from mutating public info by deep-copying, but admin info is copied with `dict()` rather than deep-copied. Dotted disallowed traversal silently ignores missing paths and non-dict intermediates. ASCII validation raises `UnicodeEncodeError`, not a Swift-specific error. Re-registering existing keys overwrites values.

## Test signals
Tests should cover public/admin registration, reserved name rejection, dotted key rejection, deep-copy isolation, disallowed top-level and nested removal, admin disallowed echoing, case normalization for headers, case-sensitive query parameters, non-string type errors, non-ASCII failures, and overwrite behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/registry.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/request_helpers.py -->
# sources/object-store/openstack-swift/swift/common/request_helpers.py

## Purpose
`request_helpers.py` collects HTTP request and response utilities that need `swob` types without creating circular imports in `swift.common.utils`. It supports parameter validation, internal/reserved namespace validation, metadata header classification, large-object segment streaming, range/multipart translation, backend etag/range control headers, replication-network selection, expired-object access checks, log-info accumulation, and heartbeat response formatting.

## Important APIs, types, and functions
Parameter helpers include `get_param()`, `get_valid_part_num()`, `validate_params()`, `constrain_req_limit()`, and `validate_container_params()`. Path and placement helpers include `get_name_and_placement()` and `split_and_validate_path()`. Metadata helpers include `is_user_meta()`, `is_sys_meta()`, `is_sys_or_user_meta()`, transient sysmeta checks/strippers, prefix constructors, `get_container_update_override_key()`, `get_reserved_name()`, and `split_reserved_name()`. Header utilities include `remove_items()`, `copy_header_subset()`, and `check_path_header()`.

`SegmentedIterable` is the central class for serving static/segmented large objects. It coalesces adjacent segment subrequests, retrieves segment bytes from the WSGI app, validates status, etag, length, MD5, total response length, and max GET time, supports swob range hooks, validates the first segment early, and closes backend iterators. Remaining helpers include `http_response_to_document_iters()`, etag-is-at update/resolve functions, ignore-range update/resolve functions, `is_use_replication_network()`, `get_ip_port()`, `is_open_expired()`, `is_backend_open_expired()`, `append_log_info()`, `get_log_info()`, and `get_heartbeat_response_body()`.

## Control flow and state behavior
Most functions are stateless transformations over requests, headers, metadata, or iterables. Parameter functions decode WSGI strings into native UTF-8 and raise `HTTPBadRequest` or `HTTPPreconditionFailed` for client errors. Internal namespace validation enforces reserved-name placement rules across account/container/object paths.

`SegmentedIterable` maintains iterator state: the original request/app/listing iterator, current backend response, a peeked chunk for first-segment validation, and a validated flag. Its internal pipeline is `_coalesce_requests()` -> `_requests_to_bytes_iter()` -> `_byte_counting_iter()` -> `_time_limited_iter()` -> `_internal_iter()`. It yields bytes lazily, but can be primed by `validate_first_segment()` before response headers are finalized. It closes response iterators on errors, normal completion, and explicit `close()`.

## Dependencies and integration points
This module depends heavily on `swift.common.swob`, `swift.common.utils`, `swift.common.constraints`, `swift.common.storage_policy.POLICIES`, `swift.common.exceptions`, `swift.common.http`, `swift.common.wsgi.make_subrequest`, and `HeaderKeyDict`. It is used by proxy controllers and large-object middleware to validate requests, build backend subrequests, stream SLO/DLO segment bodies, resolve alternate etags from encryption or erasure-coding metadata, and select replication IP/port.

## Risks and edge cases
`SegmentedIterable` must preserve backend iterator closure across many error paths; leaks would hold sockets. Coalesced range construction can be rejected by `Range.ranges_for_length()`, falling back to separate requests. Length and MD5 checks are intentionally skipped or changed for range responses. Once the first segment is validated, later listing/segment errors are logged but may not propagate to the client because bytes may already have been sent. `get_param()` only validates present truthy values, so empty values pass through as defaults. CSV-like etag header handling forbids commas in header names. Heartbeat XML is manually assembled but escapes keys/values.

## Test signals
Important tests include invalid UTF-8 parameters, part-number/range conflicts, container limit constraints, reserved namespace combinations, metadata prefix stripping errors, header subset copy/removal, path-header validation, segment coalescing for raw and object-backed segments, backend 4xx/5xx handling, etag/length/MD5 mismatches, byte-count truncation, max-time failures, first-segment validation behavior, range hooks, multipart response parsing, etag override priority, ignore-range removal, replication-network selection, expired-object flags, and JSON/XML/text heartbeat formatting.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/request_helpers.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/__init__.py -->
# sources/object-store/openstack-swift/swift/common/ring/__init__.py

## Purpose
`swift.common.ring.__init__` provides the package-level public imports for Swift ring functionality. It makes the runtime ring data model, runtime ring lookup object, and ring builder available from `swift.common.ring`.

## Important APIs, types, and functions
The module imports `RingData` and `Ring` from `swift.common.ring.ring`, imports `RingBuilder` from `swift.common.ring.builder`, and defines `__all__ = ['RingData', 'Ring', 'RingBuilder']`.

## Control flow and state behavior
There is no executable control flow beyond imports and no state beyond the exported names. Importing this package may import substantial ring implementation code and its dependencies.

## Dependencies and integration points
This package initializer supports callers that use `from swift.common.ring import Ring, RingData, RingBuilder`, including the composite builder module and external Swift tools such as ring-builder commands. It preserves stable public API import paths while implementations live in submodules.

## Risks and edge cases
Because imports are eager, import-time failures in `ring.py` or `builder.py` surface when importing the package. The initializer does not export `RingReader`, `RingWriter`, or composite-ring helpers; callers must import those from their specific modules.

## Test signals
Tests should assert that package-level imports return the expected classes and that `__all__` contains only `RingData`, `Ring`, and `RingBuilder`.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/builder.py -->
# sources/object-store/openstack-swift/swift/common/ring/builder.py

## Purpose
`builder.py` implements Swift's ring-building algorithm. `RingBuilder` tracks devices, partition assignments, movement history, replica count, dispersion, balance, overload, and partition-power-increase state. It can rebalance assignments according to device weights and failure-domain tiers, validate the resulting ring, serialize/deserialize builder state, and produce `RingData` for runtime use.

## Important APIs, types, and functions
The central type is `RingBuilder(part_power, replicas, min_part_hours)`. Public mutation methods include `add_dev()`, `remove_dev()`, `set_dev_weight()`, `set_dev_region()`, `set_dev_zone()`, `set_replicas()`, `set_overload()`, and `change_min_part_hours()`. Operational methods include `rebalance(seed=None)`, `validate(stats=False)`, `get_balance()`, `get_required_overload()`, `pretend_min_part_hours_passed()`, `get_part_devices()`, `get_ring()`, `search_devs()`, and partition-power lifecycle methods `prepare_increase_partition_power()`, `increase_partition_power()`, `cancel_increase_partition_power()`, and `finish_increase_partition_power()`. Persistence is handled by `load()` and `save()`. Supporting internals build replica plans, gather partitions from failed/overweight/undispersed devices, reassign partitions, compute dispersion graphs, and maintain movement bitmaps.

## Control flow and state behavior
Initialization validates `part_power`, `replicas`, and `min_part_hours`, then creates device lists, version counters, movement arrays, dispersion data, and builder id storage. Device changes mark `devs_changed`, increment `version`, and invalidate cached ring data. `rebalance()` is the main flow: annotate devices with tiers, reject too few weighted devices, snapshot old assignments, update movement ages, build a tier replica plan, set per-device `parts_wanted`, adjust replica table sizes, gather assignments from removed devices and dispersion violations, remove failed devices, gather overweight parts over several attempts, reassign gathered partitions to the most appropriate weighted devices, compute dispersion/changed-parts, and clear temporary tier metadata.

Builder persistence uses pickle protocol 2 over the builder dict. `save()` assigns a UUID builder id if absent and rolls it back on failed save. Runtime ring output is cached in `_ring` until state changes. Partition-power increase is staged through `next_part_power`: prepare records the future power, increase duplicates assignment and movement arrays, cancel records a cleanup state, and finish clears the transition marker.

## Dependencies and integration points
The builder depends on `swift.common.exceptions`, `swift.common.ring.ring.RingData`, and ring utility functions for tier construction, address normalization, replica validation, device id sizing, and array resizing. It is consumed by `swift-ring-builder`, composite-ring code, tests, and operational tooling. `RingData.save()` later writes the generated ring for runtime `Ring` instances.

## Risks and edge cases
This file contains the highest-risk algorithmic code in the batch. Rebalance must honor `min_part_hours`, avoid duplicate device assignments per partition, handle fractional replicas, drain removed/zero-weight devices, and avoid poor dispersion under constrained topologies. Pickle loading is unsafe for untrusted files and is intentionally marked nosec. Device id byte resizing must not corrupt existing assignments. `increase_partition_power()` converts `_last_part_moves` to a plain list, which code must continue to tolerate. Randomized sort keys affect determinism unless a seed is supplied. `get_required_overload()` can raise if zero-weight devices still want replicas.

## Test signals
Tests should cover constructor validation, device add/remove/update validation, rebalance initial and incremental behavior, fractional replica table lengths, min-part-hours enforcement, removed-device reassignment, dispersion graph correctness, duplicate assignment detection, balance calculations, overload planning, seed repeatability, builder id persistence and rollback, legacy builder loading, search filtering including IP normalization, device id byte grow/shrink, and each partition-power-increase lifecycle state.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/builder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/composite_builder.py -->
# sources/object-store/openstack-swift/swift/common/ring/composite_builder.py

## Purpose
`composite_builder.py` builds and manages composite Swift rings made from multiple independently-built component rings. Composite rings provide stronger placement guarantees across failure domains, such as ensuring replicas/fragments are split across regions, by concatenating component assignment tables while preserving component order.

## Important APIs, types, and functions
Validation helpers include `pre_validate_all_builders()`, `check_for_dev_uniqueness()`, `check_builder_ids()`, `check_same_builder()`, `is_builder_newer()`, and `check_against_existing()`. Composition helpers include `_make_composite_ring()`, `compose_rings()`, `_make_component_meta()`, and `_make_composite_metadata()`. `CompositeRingBuilder` loads component builders, composes ring data, persists composite metadata, validates component consistency, cooperatively rebalances components, and coordinates partition movement. `CooperativeRingBuilder` subclasses `RingBuilder` so component builders delegate movement checks to the parent composite builder.

## Control flow and state behavior
Composition begins by validating that at least two builders exist, all have matching `part_power`, replica counts are integers, no builder has unapplied device changes, regions are not shared across builders, and no `ip/port/device` tuple appears in multiple builders. `_make_composite_ring()` deep-copies component devices and assignment arrays, resizes device-id arrays if needed, offsets device ids by cumulative device count, concatenates assignment tables, and returns `RingData`.

`CompositeRingBuilder` persists metadata as JSON with component id/version/replica information and builder-file paths. Loading reconstructs the builder-file list from metadata. `_load_components()` loads `CooperativeRingBuilder` instances, validates builder ids, and checks that existing composite metadata still matches unless forced. `compose()` updates ring data, version, and component metadata. `rebalance()` loads components, synchronizes last-part-move epochs, shuffles rebalance order, rebalances and validates each component, saves all builders, and returns results in component order.

## Dependencies and integration points
The module depends on `RingBuilder`, `RingData`, `RingBuilderError`, ring utility functions `calc_dev_id_bytes` and `resize_array`, plus standard `copy`, `json`, `os`, `shuffle`, `defaultdict`, and `combinations`. It is used by Swift ring-building tools for multi-region or duplicated erasure-code placement policies. The resulting `RingData` is saved and loaded by the normal ring runtime.

## Risks and edge cases
Component order is critical because primary-node indexes change if order changes, which can move erasure-coded fragments. Existing-composite checks enforce builder id and replica equality but require builders to have persisted ids. Region uniqueness is stricter than normal rings and may surprise operators. Device uniqueness only checks `ip`, `port`, and `device`, not replication addresses. JSON metadata writes are not atomic. Cooperative rebalancing saves component builders only after all rebalance/validation passes, but an exception while saving later files can leave earlier files persisted.

## Test signals
Tests should cover validation errors for too few builders, mismatched part power, fractional replicas, dirty builders, shared regions, duplicate devices, missing/duplicate builder ids, old/new component metadata comparisons, device id offsetting, dev-id-byte resizing, metadata save/load, compose force and require-modified modes, cooperative `can_part_move()` behavior, shuffled rebalance with ordered results, and component save failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/composite_builder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/io.py -->
# sources/object-store/openstack-swift/swift/common/ring/io.py

## Purpose
`io.py` implements low-level ring file I/O. It wraps gzip streams to support deterministic atomic writes, seekable reads at full-flush boundaries, version detection, v2 named sections, section checksums, length-value blobs, JSON blobs, and network-order ring assignment tables.

## Important APIs, types, and functions
`_RingGzReader` reads bounded amounts from a gzip/deflate stream and supports compressed-position seeking. `SectionReader` limits reads to a section and verifies full consumption and checksum on close. `IndexEntry` records compressed/uncompressed section offsets and checksum metadata. `RingReader` validates the `R1NG` magic, records version, loads v2 indexes, reads blobs, and opens named sections. `_RingGzWriter` writes gzip data to a temporary file and atomically renames it on successful close. `RingWriter` adds magic/version writing, named `section()` contexts, `write_size()`, `write_blob()`, `write_json()`, `write_ring_table()`, and `write_index()`.

## Control flow and state behavior
Readers buffer compressed input until zlib full-flush markers so they can reset decompressors and seek to section boundaries. `RingReader.__init__()` reads magic/version, records gzip sizes, loads the v2 index if present, then seeks back to the beginning. For v2, the index start is found near the gzip tail; entries are sorted by compressed offset and stored as an ordered dict. Opening a section seeks to the compressed start, verifies the blob length against index metadata, creates the requested checksum, and yields a `SectionReader`.

Writers create a temp file in the destination directory, finalize gzip only on successful context exit, fsync, chmod to `0644`, and rename atomically. `RingWriter.section()` prevents nested/duplicate/invalid sections, records start offsets, hashes data written in the section, and records end offsets/checksum. If any sections exist, `close()` writes a JSON index and both uncompressed and compressed index offsets at the end.

## Dependencies and integration points
This module depends on `gzip`, `zlib`, `hashlib`, `json`, `struct`, `dataclasses`, `tempfile`, and ring utility functions for network-order arrays. `RingData.load()` and `RingData.save()` use `RingReader` and `RingWriter`. V2 sections are named `swift/ring/metadata`, `swift/ring/devices`, and `swift/ring/assignments` by `ring.py`.

## Risks and edge cases
The reader refuses greedy `read(-1)`, so callers must know sizes. Seeking only works safely to full-flush boundaries; recompressing a ring can break v2 index seeking. `SectionReader.read()` assumes a checksum object is present and updates it unconditionally. `IndexEntry.compression_ratio` can divide by zero for empty sections. Section names are limited to letters, digits, slash, and hyphen. Atomic rename is local-filesystem safe but still depends on directory fsync semantics not represented here. Unsupported checksum methods fail at read time.

## Test signals
Tests should cover v1/v2 magic detection, unsupported versions, bad magic, bounded reads, compressed seeking at flush boundaries, index load failures after recompression, section size mismatch, checksum mismatch, section full-read enforcement, atomic rename and temp cleanup on failure, duplicate/nested/invalid section names, deterministic gzip mtime, JSON/blob/table round trips, and network-order assignment compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/io.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/ring.py -->
# sources/object-store/openstack-swift/swift/common/ring/ring.py

## Purpose
`ring.py` contains the runtime ring data representation and lookup object. `RingData` serializes/deserializes partition-to-device assignments and device metadata. `Ring` loads a serialized ring, reloads when the file changes, hashes account/container/object names to partitions, returns primary nodes, and generates handoff nodes for hinted handoff.

## Important APIs, types, and functions
Module helpers are `calc_replica_count()` for full/fractional replica tables and `normalize_devices()` for legacy replication IP/port defaults. `RingData` exposes `replica_count`, `part_power`, `dev_id_bytes`, `load()`, `from_dict()`, `serialize_v1()`, `serialize_v2()`, `save()`, and `to_dict()`. `Ring` exposes properties for device id bytes, next partition power, part power, version, compressed/raw size, replica count, partition count, device counts, and devices. Lookup methods include `has_changed()`, `get_part()`, `get_part_nodes()`, `get_nodes()`, and `get_more_nodes()`.

## Control flow and state behavior
`RingData.__init__()` normalizes devices, converts assignment rows to arrays, stores part shift, optional next part power/version, and metadata needed for metadata-only loads. V1 serialization writes magic, metadata JSON, and 2-byte assignment rows. V2 writes named sections for metadata, devices, and assignments using `RingWriter`. Loading opens a `RingReader`, dispatches by version through `RING_CODECS`, optionally skips assignments/devices, and records compressed and raw sizes.

`Ring.__init__()` validates global hash configuration, resolves the ring file path, stores reload timing, and forces an initial load. `_reload()` only replaces runtime state if the file changed and the optional validation hook accepts the new data; invalid reloads are ignored after initial load. Bookkeeping counts assigned/weighted devices and distinct regions/zones/IPs with assignments. `get_part()` hashes the request path and shifts the high 32 bits by `part_shift`. `get_more_nodes()` scans deterministic handoff partitions in phases: first unused regions, then zones, then IPs, then any remaining assigned devices.

## Dependencies and integration points
The module depends on `array`, `json`, `struct`, `time`, `os.path.getmtime`, `itertools`, `RingReader`, `RingWriter`, `hash_path`, `validate_configuration`, `md5`, `tiers_for_dev`, and Swift exceptions. Runtime servers and proxy controllers use `Ring` to route account/container/object requests. Ring-builder tooling uses `RingData` for persisted ring output.

## Risks and edge cases
V1 rings only support 2-byte device ids; larger rings need v2. Metadata-only loads must preserve replica count and device-id-byte fields without assignment rows. `has_changed()` relies only on mtime, so content changes without mtime changes are invisible. Runtime reload ignores invalid changed rings, preserving availability but possibly hiding operator mistakes. `get_more_nodes()` only considers assigned devices for early termination, so unassigned weighted devices are excluded until a new ring assigns them. Duplicate primary dev ids are collapsed, which matters for partial/fractional replicas. Hash configuration must be present before construction.

## Test signals
Tests should cover replica count math for fractional tables, legacy device normalization, v1/v2 serialization round trips, metadata-only and include-devices false loads, v1 device-id-size rejection, deterministic saves, validation hook failure on initial and runtime reload, mtime reload behavior, partition hashing, primary-node duplicate filtering and indexes, device/bookkeeping counts, tier data rebuild, handoff ordering across region/zone/IP/device phases, and next-part-power exposure.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/ring.py -->
