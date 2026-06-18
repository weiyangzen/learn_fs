# subset-b-008220 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/utils.py -->
# sources/object-store/openstack-swift/swift/common/ring/utils.py

## Purpose

This module is the command-line and serialization utility layer for Swift ring management. It supports ring-builder parsing, ring tier topology construction, device address normalization, local-device matching, device array serialization helpers, and dispersion reporting. The file is not a ring builder itself; it provides the reusable pieces that `swift-ring-builder`, ring validation, and ring serialization code use to keep device dictionaries, device IDs, and placement tiers consistent.

## Important APIs, types, and functions

`BYTES_TO_TYPE_CODE`, `none_dev_id`, `calc_dev_id_bytes`, `resize_array`, `network_order_array`, and `read_network_order_array` define how `replica2part2dev` arrays encode device IDs. `none_dev_id()` reserves the maximum value representable by a device-ID width as the sentinel for an unassigned part. `calc_dev_id_bytes()` chooses a 2-byte or 4-byte array item size and raises `DevIdBytesTooSmall` when the ID space is exhausted. `network_order_array()` mutates an array into network byte order for serialization and restores the original byte order on exit.

`tiers_for_dev()` and `build_tier_tree()` translate device dictionaries into Swift placement tiers: region, region/zone, region/zone/IP, and region/zone/IP/device-id. The returned tree is a `defaultdict(set)` keyed by parent tier and rooted at `()`. `format_device()`, `pretty_dev()`, and `get_tier_name()` convert tier/device data back into ring-builder display strings.

Address validation is split into `validate_and_normalize_ip()`, `validate_and_normalize_address()`, `is_valid_hostname()`, and `is_local_device()`. IP values are lower-cased and IPv6 addresses are expanded through `swift.common.utils.expand_ipv6`; hostnames are lower-cased and checked against an RFC1123-style label regex. `is_local_device()` may resolve hostnames with `socket.getaddrinfo()` and compares candidate IPs with the local IP set and optional server-per-port port matching.

Ring-builder CLI parsing is handled by `parse_search_value()`, `parse_search_values_from_opts()`, `parse_change_values_from_opts()`, `parse_add_value()`, `parse_address()`, `validate_args()`, `parse_args()`, `parse_builder_ring_filename_args()`, and `build_dev_from_opts()`. These functions parse compact legacy device strings such as `r1z2-10.1.2.3:6200/sdb1_meta`, newer option-parser fields, replication addresses, IPv6 bracket notation, weight, metadata, and change options. `validate_device_name()` rejects empty names and leading/trailing spaces.

`dispersion_report()` reads a builder dispersion graph and max-replica-by-tier model to calculate at-risk partitions and the worst tier. `validate_replicas_by_tier()` checks that a replicas-by-tier map sums back to the expected replica count for cluster, region, zone, server, and device tier depths.

## Control flow

The parsing functions all follow deterministic left-to-right token consumption. `parse_search_value()` peels optional `d`, `r`, and `z` numeric prefixes, optional IP and port, optional replication address after `R`, optional device name after `/`, and optional metadata after `_`; any unconsumed suffix raises `ValueError`. `parse_add_value()` is stricter: zone, primary address, port, and device are required, while region and replication address are optional. `parse_address()` handles bracketed IPv6 by removing a single bracket pair, scans until `R` or `/`, splits at the final colon, validates the port, and normalizes the IP.

Ring tier building is additive: each device contributes every tier from `tiers_for_dev()`, and `build_tier_tree()` records child tiers under each parent. Dispersion reporting refreshes the builder's dispersion graph when requested, skips tiers not matching a search regex, computes excess colocated replica counts above the allowed tier maximum, and optionally accumulates verbose per-tier graph data.

## State and persistence behavior

The module itself has no durable state. Its stateful behavior is limited to in-place byte swapping in `network_order_array()` and array resizing in `resize_array()`. The context manager intentionally mutates the supplied array rather than copying it, so the `finally` block is essential to avoid leaving live ring data in network order on little-endian systems. Ring-builder option parsing returns plain dictionaries that callers persist in builder files elsewhere.

## Dependencies and integration points

The module depends on `swift.common.exceptions` for ring-specific errors and on `swift.common.utils` IP helpers. It imports `optparse` because Swift ring-builder CLI compatibility predates `argparse`. Device dictionaries are expected to use the conventional ring keys `id`, `region`, `zone`, `ip`, `port`, `replication_ip`, `replication_port`, `device`, `weight`, and `meta`. `dispersion_report()` depends on private builder methods and fields (`_dispersion_graph`, `_build_dispersion_graph()`, `_build_max_replicas_by_tier()`, and `devs`), so builder internals and this utility must evolve together.

## Risks and edge cases

The compact parser is intentionally permissive in some places and strict in others. It recognizes IP literals, not hostnames, inside compact search/add strings, while option-based parsing accepts hostnames through `validate_and_normalize_address()`. Empty numeric prefixes such as `d` or malformed port suffixes can surface as `ValueError` from `int()`. IPv6 support depends on bracket handling and final-colon port splitting; tests should cover unbracketed IPv6 rejection for add values and normalized bracketed values.

`is_local_device()` performs DNS resolution for hostnames and returns false on `gaierror`; this avoids startup failures but may mask transient DNS problems. `calc_dev_id_bytes()` reserves the maximum value as the unassigned sentinel, so exact boundary tests around `none_dev_id(2)` and `none_dev_id(4)` are important. `network_order_array()` has mutation risk if callers retain references while serializing.

## Test signals

Useful tests include byte-order round trips, sentinel preservation across `resize_array()`, compact parser examples from the docstring, invalid add/search strings, hostname and IPv6 normalization, device-name validation, server-per-port matching when `my_port` is `None`, and dispersion calculations with a fake builder graph. The strongest integration signal is ring-builder CLI behavior: adding, searching, changing, and displaying devices should remain stable across legacy compact syntax and newer option syntax.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/ring/utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/splice.py -->
# sources/object-store/openstack-swift/swift/common/splice.py

## Purpose

This module provides small `ctypes` bindings for Linux `tee(2)` and `splice(2)`. Swift can use these zero-copy system calls to move data between file descriptors or duplicate pipe buffers without copying data through Python user space. The module exports instantiated callable objects, `tee` and `splice`, rather than the binding classes themselves.

## Important APIs, types, and functions

`tee(fd_in, fd_out, len_, flags)` wraps libc `tee`. File descriptors may be integer FDs or objects with `fileno()`. `flags` may be an integer bitmask or an iterable of flag constants. The call returns the kernel byte count. `tee.available` reports whether libc exposed the symbol on the current platform.

`splice(fd_in, off_in, fd_out, off_out, len_, flags)` wraps libc `splice`. It exposes `SPLICE_F_MOVE`, `SPLICE_F_NONBLOCK`, `SPLICE_F_MORE`, and `SPLICE_F_GIFT` constants copied from Linux fcntl headers. Offset arguments are either integer offsets, which are passed by pointer and returned with updated values, or `None`, which passes NULL and lets the kernel update the file offset. The return value is `(result, off_in_value, off_out_value)`.

`c_loff_t` is defined as `ctypes.c_long` and is used for offset pointers. Each wrapper installs `argtypes`, `restype`, and an `errcheck` callback on the libc function.

## Control flow

At import time the module instantiates `Tee()` and `Splice()`, loads libc with `ctypes.CDLL(ctypes.util.find_library('c'), use_errno=True)`, and looks for the relevant symbols. Missing symbols result in `_c_tee` or `_c_splice` being set to `None`; calls then raise `EnvironmentError` rather than failing during import. Present symbols are configured once, and every later call normalizes flags, obtains integer file descriptors, creates optional offset pointers, and invokes libc.

The errcheck path converts a kernel return value of `-1` into `IOError(errno, "...")`; successful `tee` returns the raw byte count, while successful `splice` returns the byte count plus possibly updated offsets.

## State and persistence behavior

The only module state is the two singleton binding objects and their cached libc function pointers. There is no persistent storage. Calls can change kernel-maintained file offsets when `off_in` or `off_out` is `None`, and can update explicit offset pointer values when offsets are supplied. The Python wrapper itself does not cache buffers or file descriptors.

## Dependencies and integration points

The module depends on Linux/glibc-like libc support, `ctypes`, and `os.strerror`. It is designed as a low-level optional accelerator for higher-level Swift data paths. Consumers must check `.available` or handle `EnvironmentError` when running on platforms without `tee` or `splice`.

## Risks and edge cases

The errno handling appears suspicious: `ctypes.set_errno(0)` sets errno to zero and returns the previous ctypes errno, but the usual pattern is `ctypes.get_errno()`. Tests should verify that raised `IOError.errno` is meaningful on failure. `c_loff_t = ctypes.c_long` assumes a compatible offset width; that is appropriate on common 64-bit Linux but should be validated on less common ABI targets. The wrappers do not retry on `EINTR` or handle partial transfers; callers must be prepared for short counts and nonblocking errors.

`tee` and `splice` require particular FD types, especially pipes for many operation modes. The Python signature does not enforce these constraints, so misuse is reported by the kernel. Passing `0` for offsets is not the same as passing `None`, and the docstring explicitly warns callers to use `None` for NULL offset pointers.

## Test signals

Tests should cover import on systems with and without libc symbols, `.available`, flag list folding, integer and file-object descriptors, explicit offset return values, NULL offset behavior, and error propagation with invalid descriptors. Integration tests can use pipes and temporary files to confirm byte movement while checking for partial-transfer semantics.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/splice.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/statsd_client.py -->
# sources/object-store/openstack-swift/swift/common/statsd_client.py

## Purpose

This module is Swift's UDP StatsD emission layer. It builds legacy metric names, supports optional labeled metrics in several collector dialects, applies sampling, and isolates metric-send failures from service request handling. It is used by loggers and service code that need counters, timings, and transfer-rate metrics without taking a dependency on a long-lived StatsD socket.

## Important APIs, types, and functions

`get_statsd_client(conf, tail_prefix, logger)` reads `log_statsd_host`, `log_statsd_port`, `log_statsd_default_sample_rate`, `log_statsd_sample_rate_factor`, `log_statsd_metric_prefix`, and `statsd_emit_legacy`, returning a `StatsdClient`. `get_labeled_statsd_client(conf, logger)` reads the same host/port/sample settings plus `statsd_label_mode` and user labels whose config keys start with `statsd_user_label_`.

Formatting helpers include `_build_line_parts()` and dialect functions `librato()`, `influxdb()`, `graphite()`, and `dogstatsd()`. `LABEL_MODES` maps mode names to formatter callables, while `_get_labeled_statsd_formatter()` validates the configured mode.

`AbstractStatsdClient` owns host/port configuration, DNS-family detection, sampling, socket creation, send error handling, and common metric methods. `_is_emitted()` applies default sample rate and sample-rate factor and uses an injectable `random` function for tests. `_send_line()` opens a UDP socket for each datagram, sends UTF-8 bytes, and logs warnings without propagating send errors.

`StatsdClient` implements legacy unlabeled metrics with optional `base_prefix` and `tail_prefix`. It preserves older positional `sample_rate` arguments on `update_stats()`, `increment()`, `decrement()`, `timing()`, `timing_since()`, and `transfer_rate()`. `LabeledStatsdClient` emits labeled lines with keyword-only `labels` and `sample_rate`, merges caller labels with configured default labels, sorts labels for deterministic output, and disables output when `statsd_label_mode` is `disabled`.

## Control flow

Client construction resolves the target socket family by trying IPv4 and then IPv6 `getaddrinfo()`. If both fail, startup continues with an IPv4 family and the original host, allowing later `sendto()` name resolution to succeed. A metric method funnels through `_send()`, then `_is_emitted()`, then line formatting, then `_send_line()`. Sampling short-circuits before formatting when the adjusted sample rate is below a random draw. `transfer_rate()` emits only when `byte_xfer` is non-zero, calculating milliseconds per kilobyte-like unit from elapsed time and transferred bytes.

For labeled clients, default user labels are validated at configuration load time: label names allow only ASCII alphanumerics and underscore, and label values additionally allow periods. The configured names are prefixed with `user_` to avoid collisions with internal label namespaces.

## State and persistence behavior

The clients hold only in-memory configuration and do not persist metrics. They intentionally do not cache sockets because a shared socket would be unsafe across Swift green threads. `_target` preserves the configured host instead of pinning a resolved address, so DNS changes can take effect through normal resolver behavior. `StatsdClient.set_prefix()` mutates the legacy metric prefix and emits a deprecation warning.

## Dependencies and integration points

The module imports `socket` from `swift.common.concurrency`, so the socket implementation follows Swift's eventlet/concurrency abstraction. It uses `config_true_value()` for boolean config parsing. The clients are typically constructed by Swift logger setup and passed into service components; metric methods are deliberately narrow enough to be used from hot request paths.

StatsD label syntax is collector-specific. Librato appends `#k=v`, InfluxDB appends `,k=v` to the measurement name, Graphite appends `;k=v`, and DogStatsD appends `|#k:v` after the base StatsD line.

## Risks and edge cases

There is no explicit validation that sample rates are between 0 and 1. Values above 1 omit the `|@` suffix and always emit; negative values effectively never emit but have surprising semantics. UDP send failures are logged and swallowed, which is operationally appropriate but means metric loss is silent unless warnings are observed. Opening a socket per metric avoids green-thread sharing but adds overhead in high-volume paths.

Labeled and legacy clients intentionally expose different call signatures: legacy accepts positional `sample_rate`, while labeled uses keyword-only labels and sample rate. Callers migrating between them need tests. Label validation covers configured user labels but not per-call labels, so caller-provided labels can still contain dialect-breaking characters or high-cardinality values.

## Test signals

Strong tests include formatter output for each label mode, invalid label-mode errors, user-label validation failures, prefix construction, sampling boundaries with a deterministic `random`, disabled host behavior, DNS fallback behavior, UDP send error logging, deprecated `set_prefix()` warnings, and compatibility of legacy positional `sample_rate`. Labeled-client tests should verify deterministic label sorting and default-label override behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/statsd_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/storage_policy.py -->
# sources/object-store/openstack-swift/swift/common/storage_policy.py

## Purpose

This module defines Swift storage policy configuration, validation, lookup, ring loading, and policy-specific behavior. Storage policies are the cluster-wide abstraction that maps object data to different object rings and diskfile implementations, including replicated and erasure-coded storage. The module also owns the process-wide `POLICIES` singleton loaded from `swift.conf`.

## Important APIs, types, and functions

`BindPortsCache` scans all configured object rings and returns the bind ports that belong to the local node IP set. It caches ring file mtimes and metadata-only ring device port sets by ring path, avoiding full ring loads.

`PolicyError` is the main validation exception. `get_policy_string(base, policy_or_index)` and `split_policy_string(policy_string)` encode and decode policy indices in names such as object ring filenames and on-disk directories, using policy zero as the legacy no-suffix form through `get_zero_indexed_base_string()`.

`BaseStoragePolicy` validates common fields: non-negative integer index, name and aliases, deprecation/default flags, registered policy type, ring name, and diskfile module. It supplies name/alias manipulation, `from_config()`, `get_info()`, lazy `load_ring()`, `validate_ring_data()` hook, abstract `quorum`, and `get_diskfile_manager()`. The diskfile manager is loaded through Swift's package resource loader and checked against the policy.

`StoragePolicy` is the replicated policy class registered as `policy_type = replication`; its quorum is `floor(replica_count / 2) + 1` via `quorum_size()`. `ECStoragePolicy` is registered as `erasure_coding`; it validates PyECLib type, data/parity counts, object segment size, duplication factor, and a known-dangerous ISA-L configuration. It constructs an `ECDriver`, calculates EC quorum, exposes EC properties, computes fragment size lazily, validates that the object ring replica count equals `(data + parity) * duplication_factor`, and maps ring node index to backend fragment index.

`StoragePolicyCollection` indexes policies by case-insensitive name and integer index, enforces uniqueness and default/deprecation rules, supplies lookup by name/index/name-or-index, exposes the legacy policy, lazily loads object rings, emits public `/info` policy data, and supports alias add/remove/primary-name changes.

`parse_storage_policies(conf)` builds policy objects from `storage-policy:<index>` sections. `reload_storage_policies()` reads `utils.SWIFT_CONF_FILE`, parses policies, and updates `_POLICIES`; `POLICIES` is a `StoragePolicySingleton` proxy so code that imported `POLICIES` continues to see the current `_POLICIES` object after reload.

## Control flow

At import time `_POLICIES` is initialized by `reload_storage_policies()`, then `POLICIES` is created as a proxy. Config parsing iterates storage-policy sections, selects a policy class from `BaseStoragePolicy.policy_type_to_policy_cls`, maps config option names to constructor parameters, and constructs a collection. Collection validation first checks duplicates/defaults while adding supplied policies, then creates policy zero automatically only if no policies were provided, rejects multi-policy configurations without explicit index zero, rejects all-deprecated configurations, and requires exactly one default when multiple policies exist.

Ring loading is lazy. Services ask `POLICIES.get_object_ring(policy_idx, swift_dir)`, which finds a policy, calls `policy.load_ring(swift_dir)` if necessary, and returns the policy's `object_ring`. EC policies pass `validate_ring_data()` into `Ring()` so invalid replica counts fail during ring load.

## State and persistence behavior

The durable source of truth is `swift.conf` plus ring files under `swift_dir`; this module keeps in-memory policy objects and cached ring objects. `BaseStoragePolicy.object_ring` is loaded once unless tests inject an object ring or callers set ring reload behavior. `BindPortsCache` stores ring mtimes and port sets and refreshes each ring path when mtime changes. Alias mutation methods update both the policy alias list and the collection's `by_name` index, but these runtime mutations are not written back to config.

## Dependencies and integration points

The module integrates with `swift.common.ring.Ring` and `RingData`, `swift.common.utils` config parsing helpers, `swift.common.exceptions.RingLoadError`, and PyECLib (`ECDriver`, `VALID_EC_TYPES`). It is central to proxy, object-server, diskfile, recon, and `/info` behavior because policy index and type affect ring lookup, quorum, diskfile implementation, EC fragment math, object metadata, and operator-visible policy information.

Diskfile integration is pluggable through entry points such as `egg:swift#replication.fs` and `egg:swift#erasure_coding.fs`. Public policy info intentionally omits policy type, diskfile module, and detailed EC parameters unless config output is requested.

## Risks and edge cases

Import-time config parsing can raise `SystemExit` on invalid `swift.conf`, so tests and tools that import this module need controlled config fixtures. `parse_storage_policies()` indexes `policy_type_to_policy_cls` directly; an unknown `policy_type` raises `KeyError` rather than `PolicyError`. Name validation is restrictive because names become HTTP headers; aliases are case-insensitive in collection indexes but stored with original case in the policy.

EC policy correctness is high risk. The ring replica count must exactly match unique fragments times duplication factor; too few or too many replicas break proxy/object assumptions. The `isa_l_rs_vand` parity warning includes a hard validation requirement that affected policies be deprecated. Fragment size calculation deliberately asks PyECLib for segment-sized data even when ranged GETs may not know the full object size; regressions there affect EC range reads.

Policy zero is special throughout name encoding and config defaults. Tests should cover `None`, empty string, string index, integer index, and unknown index lookups to avoid breaking legacy paths.

## Test signals

Tests should exercise empty config default policy creation, multi-policy validation errors, default/deprecated conflicts, duplicate names and indexes, alias lifecycle, policy string encoding/decoding, public vs config `get_info()`, singleton reload behavior, diskfile manager loading/check failures, ring lazy loading, `BindPortsCache` mtime refresh, replicated quorum, EC constructor validation, EC ring replica validation, EC backend index modulo behavior, and known-dangerous EC configuration handling.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/storage_policy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/swob.py -->
# sources/object-store/openstack-swift/swift/common/swob.py

## Purpose

`swob.py` is Swift's in-tree WebOb-like WSGI request and response library. It wraps WSGI environ dictionaries, request bodies, response headers, conditional responses, HTTP range handling, WSGI string/byte conversions, and HTTP exception factories. Swift uses it to avoid external WebOb API churn while preserving a familiar interface for middleware, proxy controllers, object/container/account servers, and tests.

## Important APIs, types, and functions

`RESPONSE_REASONS` maps HTTP status codes to reason phrases and default explanatory bodies, including Swift-specific codes such as 499, 507, and 529. `WsgiBytesIO` is a `BytesIO` stand-in for `wsgi.input` that exposes eventlet-style 100-continue methods as no-ops.

Date and header helpers include `date_header_format()`, `parse_date_header()`, `_datetime_property()`, `_header_property()`, `_header_int_property()`, `header_to_environ_key()`, and `HeaderEnvironProxy`. These implement case-insensitive-ish HTTP header access over WSGI environ keys while preserving Python 3 WSGI latin-1 rules.

WSGI conversion helpers (`wsgi_to_bytes()`, `wsgi_to_str()`, `bytes_to_wsgi()`, `str_to_wsgi()`, `wsgi_quote()`, `wsgi_unquote()`, `wsgi_quote_plus()`, and `wsgi_unquote_plus()`) explicitly handle the split between native strings, bytes on the wire, latin-1 WSGI strings, and UTF-8 strings with surrogate escape.

`Range`, `Match`, and `Accept` wrap request headers. `Range` parses `bytes=` headers and converts them into satisfiable half-open ranges with DoS protections (`MAX_RANGES`, `MAX_RANGE_OVERLAPS`, and `MAX_NONASCENDING_RANGES`). `Match` implements ETag set membership with wildcard handling. `Accept.best_match()` parses media ranges, q values, and wildcards to choose a server option.

`Request` exposes WSGI request properties such as `method`, `path_info`, `headers`, `params`, `timestamp`, `range`, `if_match`, `if_none_match`, `accept`, `body`, `message_length()`, `split_path()`, `call_application()`, and `get_response()`. `Request.blank()` constructs test or subrequest environ dictionaries from URLs, headers, body, and request-property keyword arguments. `ensure_x_timestamp()` validates or creates `X-Timestamp` and normalizes it to Swift's internal timestamp format.

`Response` owns response headers, body/app_iter, status, content properties, conditional handling, range serving, default error bodies, relative-location absolutizing, and WSGI callable behavior. It supports single and multipart byte ranges through `app_iter_range`, `app_iter_ranges`, body slicing, `content_range_header_value()`, `content_range_header()`, and `multi_range_iterator()`. `HTTPException` combines `Response` and `Exception`, `wsgify()` adapts request-taking functions to WSGI callables, and `status_map` plus constants such as `HTTPOk`, `HTTPBadRequest`, and `HTTPServiceUnavailable` provide exception factories.

## Control flow

Request construction wraps a caller-provided environ and lazily derives values from it. `Request.blank()` parses the supplied path, fills standard WSGI keys, installs a `WsgiBytesIO`, applies headers through `HeaderEnvironProxy`, and applies supported property kwargs. Request body access consumes `wsgi.input`, then replaces it with a new `WsgiBytesIO` containing the consumed bytes so later consumers can read again.

`Request.call_application()` invokes a WSGI app, captures `start_response`, handles apps that use the returned write callable, reiterates the app iterator if needed to force late `start_response`, and raises if `start_response` never happens. `get_response()` wraps that tuple in a `Response`.

`Response.__call__()` ensures there is a request object, computes `response_iter` once through `_response_iter()`, converts relative `Location` to absolute unless `swift.leave_relative_location` is set, calls `start_response`, and returns the iterable. `_response_iter()` first evaluates conditional request headers, then HEAD behavior, then range behavior, then falls back to app_iter, body, default status body, or an empty body. Failed preconditions close the original iterator without draining it; HEAD uses `friendly_close()` to release resources politely.

Range handling asks the request `Range` object for satisfiable ranges against the current content length. Unsatisfiable ranges become 416 with `Content-Range: bytes */<length>`. Single ranges can be delegated to an app iterator's `app_iter_range()` or served by slicing an in-memory body. Multiple ranges require `app_iter_ranges()` or an in-memory body and produce a multipart/byteranges response with a random boundary and precomputed content length.

## State and persistence behavior

All state is per request/response object and in-memory. `HeaderEnvironProxy` writes directly into the WSGI environ. `Request.params` is cached until the setter changes `QUERY_STRING`. `Request._timestamp` caches parsed timestamp state. `Response.body` may consume and close `app_iter`; assigning `app_iter` closes any previous iterator and may clear content length. `Response.response_iter` is cached after conditional/range processing, so changing headers/body after calling `fix_conditional_response()` or `__call__()` can produce stale output.

There is no durable persistence, but the module is a gateway for protocol state: it mutates headers, environ values, body streams, status, and iterators that higher Swift layers depend on.

## Dependencies and integration points

The module depends on `HeaderKeyDict`, utilities such as `reiterate`, `split_path`, `pairs`, `close_if_possible`, `closing_if_possible`, `config_true_value`, and `friendly_close`, plus Swift timestamp classes and `InvalidTimestamp`. It is integrated across Swift's WSGI pipeline: middleware decorators use `wsgify()`, controllers raise HTTP exception factories, tests use `Request.blank()`, and object responses rely on range and conditional handling.

The code intentionally mirrors parts of WebOb while following Swift-specific protocol needs, including internal timestamps, conditional EC ETag support through `conditional_etag`, reserved-name backend headers, relative-location override, and eventlet-compatible WSGI input behavior.

## Risks and edge cases

This module is protocol-critical. WSGI string conversion must preserve arbitrary bytes from HTTP paths and headers; mistakes can corrupt non-ASCII object names. Header mapping uppercases bytes before converting back to WSGI strings to avoid Python 3 Unicode case-folding surprises. `Request.blank()` rejects unsupported URL schemes and validates latin-1 path compatibility.

Range parsing is a security-sensitive area. The module rejects syntactically invalid range headers by raising `ValueError`, ignores impossible ranges in some cases, and returns an empty range list as the signal for 416 or DoS rejection. Tests must cover suffix ranges, zero-length bodies, overlapping ranges, non-ascending ranges, too many ranges, and delegation to app iterators. Conditional response logic combines ETag and date conditions; ordering changes can alter HTTP semantics.

Response body/app_iter ownership is another risk. Accessing `Response.body` drains streaming iterators into memory. HEAD and failed conditional handling close iterators differently. `Response.__call__()` caches `response_iter`, so response mutation after first call is unsafe. Default error body interpolation uses response attributes for messages such as 507 drive names, so missing attributes become `unknown`.

## Test signals

High-value tests include WSGI byte/string round trips, header environ mapping for content headers and unusual bytes, date parsing/formatting, request path/query construction, body read reset behavior, `message_length()` with content-length and transfer-encoding cases, timestamp validation and normalization, `split_path()` integration, WSGI app invocation paths, Accept best-match sorting and invalid headers, ETag matching, conditional 304/412 responses, HEAD iterator closure, single and multipart ranges over app_iter and body, 416 responses, relative Location absolutizing, `www_authenticate()` realm selection, `wsgify()` exception handling, and every exported HTTP exception factory status.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/swob.py -->
