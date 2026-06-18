# Research: subset-b-008221

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/__init__.py -->
# sources/object-store/openstack-swift/swift/common/utils/__init__.py

## Purpose

This module is the broad compatibility and convenience surface for `swift.common.utils`. It re-exports selected helpers from the newer split modules (`base`, `config`, `libc`, `timestamp`, `ipaddrs`, and logging utilities), preserves older import paths used by Swift and third-party middleware, and defines many of Swift's core operational helpers in one place. The file covers logging/statistics adapter construction, hash-path setup, durable filesystem operations, lock management, daemon option parsing, request/path/header parsing, iterator wrappers, rate limiting, async green-thread helpers, recon cache persistence, namespace and shard-range models, partition/path utilities, package entry-point loading, systemd notification, and watchdog timeout scheduling.

## Important APIs, Types, And Functions

- Re-exported APIs include `md5`, `quote`, `split_path`, config parsers/validators, libc wrappers, timestamp helpers, and IP helpers. Many callers still import these names directly from `swift.common.utils`.
- Logging entry points are `_patch_statsd_methods()`, `get_logger()`, and `get_prefixed_logger()`, which return Swift log adapters patched with legacy StatsD-like methods.
- Hash and configuration globals include `HASH_PATH_SUFFIX`, `HASH_PATH_PREFIX`, `SWIFT_CONF_FILE`, `set_swift_dir()`, `validate_hash_conf()`, `validate_configuration()`, and `hash_path()`.
- Filesystem and durability helpers include `fs_has_free_space()`, `fallocate()`, `punch_hole()`, `fsync()`, `fdatasync()`, `fsync_dir()`, `mkdirs()`, `makedirs_count()`, `renamer()`, `link_fd_to_path()`, `write_file()`, `remove_file()`, `remove_directory()`, `is_file_older()`, `listdir()`, `ismount()`, and `ismount_raw()`.
- Locking and process helpers include `lock_path()`, `lock_file()`, `lock_parent_directory()`, `drop_privileges()`, `clean_up_daemon_hygiene()`, `parse_options()`, `get_hub()`, `get_pid_notify_socket()`, `NotificationServer`, `systemd_notify()`, `Watchdog`, `WatchdogTimeout`, and `get_ppid()`.
- Request and object-storage helpers include `generate_trans_id()`, `get_trans_id_time()`, `select_ip_port()`, `node_to_string()`, `storage_directory()`, `validate_device_partition()`, `validate_sync_to()`, `get_remote_client()`, `public()`, `private()`, `replication()`, `majority_size()`, `quorum_size()`, `rsync_ip()`, and `rsync_module_interpolation()`.
- Iterator, WSGI, and stream wrappers include `FileLikeIter`, `RateLimitedIterator`, `GreenthreadSafeIterator`, `CooperativeCachePopulator`, `AbstractRateLimiter`, `EventletRateLimiter`, `ContextPool`, `GreenAsyncPile`, `StreamingPile`, `ClosingIterator`, `ClosingMapper`, `CloseableChain`, `StringAlong`, `InputProxy`, `LRUCache`, `Spliterator`, and `CooperativeIterator`.
- Header and MIME helpers include `parse_content_range()`, `parse_content_type()`, `parse_header()`, `extract_swift_bytes()`, `override_bytes_from_content_type()`, `clean_content_type()`, `_MultipartMimeFileLikeObject`, `iter_multipart_mime_documents()`, `parse_mime_headers()`, `mime_to_document_iters()`, `maybe_multipart_byteranges_to_document_iters()`, `document_iters_to_multipart_byteranges()`, `document_iters_to_http_response_body()`, `multipart_byteranges_to_document_iters()`, and `parse_content_disposition()`.
- Namespace/sharding types are `NamespaceOuterBound`, `Namespace`, `NamespaceBoundList`, `ShardName`, `ShardRange`, and `ShardRangeList`, plus helpers `find_namespace()` and `filter_namespaces()`.
- Miscellaneous data helpers include `safe_json_loads()`, `strict_b64decode()`, `base64_str()`, `cap_length()`, `md5_hash_for_file()`, `get_partition_for_hash()`, `get_partition_from_path()`, `replace_partition_in_path()`, `load_pkg_resource()`, `round_robin_iter()`, `parse_override_options()`, `distribute_evenly()`, `get_redirect_data()`, `parse_db_filename()`, `make_db_file_path()`, and `get_db_files()`.

## Control Flow And Behavior

Import-time work loads the hash configuration lazily if `/etc/swift/swift.conf` exists, initializes split-module exports, defines global constants, and constructs lazy libc wrappers for `fallocate` and `posix_fallocate`. The module deliberately tolerates missing hash configuration at import time so tests and tools can monkey patch or call `set_swift_dir()` later.

`get_logger()` builds a Swift logger, creates a `StatsdClient`, attaches that client to the underlying core logger, then patches a legacy StatsD method interface onto the returned adapter. `get_prefixed_logger()` clones an adapter and reuses the original StatsD source when available, so callers can preserve metric emission while adding a log prefix.

Hash-path flow is global-state based. `set_swift_dir()` changes `SWIFT_CONF_FILE`, clears cached prefix/suffix bytes, and revalidates configuration. `validate_hash_conf()` reads `[swift-hash]` values with Latin-1 encoding, requiring at least one of suffix or prefix. `hash_path()` encodes account/container/object names, adds the configured secret bytes, and returns an MD5 hex digest or raw digest.

Filesystem write flow emphasizes durability. `renamer()` makes destination directories, retries after directory races, renames, then fsyncs the target leaf directory and each newly created parent directory. `link_fd_to_path()` links an unnamed or open fd via `/proc/self/fd/<fd>`, unlinks an existing target if needed, retries directory races, and optionally fsyncs directories. `fallocate()` validates offset/size, optionally enforces `FALLOCATE_RESERVE`, then calls Linux `fallocate`, POSIX `posix_fallocate`, or logs a one-time no-op warning if neither exists. `punch_hole()` requires Linux `fallocate` with `FALLOC_FL_PUNCH_HOLE`.

Lock flow uses eventlet-aware waiting. `lock_path()` creates one or more `.lock` files, tries non-blocking exclusive `flock()` across them, sleeps cooperatively until acquired or `LockTimeout` expires, and closes all lock fds on exit. `lock_file()` opens the lock target, acquires `flock()`, verifies the inode still matches the path to handle unlink/recreate races, yields a file object, optionally unlinks at the end, and retries if it detected a stale fd.

Stream and iterator helpers generally wrap existing iterables to add accounting, rate limiting, close semantics, cooperative sleeps, or file-like `read()`/`readline()` behavior. `GreenAsyncPile` and `StreamingPile` feed jobs into eventlet green pools and return results as they become available; exceptions inside jobs are converted to a private `DEAD` sentinel and skipped unless eventlet debug exception printing is enabled.

MIME/range flow parses and emits multipart bodies lazily. `iter_multipart_mime_documents()` checks the starting boundary, then yields `_MultipartMimeFileLikeObject` instances whose `read()`/`readline()` stop at boundaries. Higher-level helpers parse MIME headers into `HeaderKeyDict`, translate multipart byte ranges into body iterators, and construct single-part or multipart HTTP response bodies while preserving resource closure.

Namespace flow models object-name ranges as half-open/closed intervals `(lower, upper]`, with singleton minimum and maximum sentinels for outer bounds. `NamespaceBoundList` stores compact lower-bound/name pairs and recreates contiguous `Namespace` objects by using the next lower bound as the previous namespace's upper bound. `ShardRange` extends `Namespace` with persisted container-sharding state, conflict-resolution timestamps, object/byte/tombstone counters, deleted/reported flags, and state-machine constants. `ShardRangeList` adds aggregation and filtering convenience.

Watchdog flow centralizes many timeout expirations in one green thread. `Watchdog.start()` records timeout metadata keyed by object id and wakes the scheduler only when the new timeout expires earlier than the current next expiration. `Watchdog._run()` throws timeout exceptions into caller greenthreads through eventlet's hub when deadlines pass.

## State And Persistence

Persistent state touched by this module includes Swift config files, recon cache JSON files, object/account/container DB file names, device paths, lock files, mount marker stub files, systemd/Swift notification sockets, and process `/proc` metadata. Mutable module globals include hash prefix/suffix and config path, fallocate feature switches and warning state, lazy libc wrapper objects, and constants controlling drain/lock defaults. `CooperativeCachePopulator` also coordinates distributed state through memcached token and data keys. Namespace and `ShardRange` objects are serializable through `__iter__()` and `from_dict()` for database rows and JSON-like transport.

## Dependencies And Integration Points

The module depends on eventlet abstractions from `swift.common.concurrency`, logging classes from `swift.common.utils.logs`, `StatsdClient`, `HeaderKeyDict`, `swift.common.exceptions`, `swift.common.linkat`, timestamp helpers, config helpers, libc helpers, and IP helpers. It integrates with nearly every major Swift subsystem: account/container/object servers use `hash_path()`, `storage_directory()`, `config_true_value()`, durability helpers, and decorators; daemon and WSGI startup use `readconf()`, `modify_priority()`, `drop_privileges()`, and eventlet/log monkey patching; proxy controllers use range, multipart, close/drain, sharding, and redirect helpers; replicators, reconstructors, auditors, relinkers, and sharder code use device scanning, rate limiting, recon cache, namespace, and override parsing helpers. S3 middleware uses checksum-related imports from the sibling module and public decorators from this module.

## Risks And Edge Cases

- Importing this module has a wide blast radius because it is the historical `swift.common.utils` compatibility surface; behavior changes can affect out-of-tree middleware.
- Global hash configuration must be valid and stable. Changing `HASH_PATH_PREFIX/SUFFIX` changes ring/object placement hashes and can make existing data unreachable.
- Filesystem helpers depend on Linux-specific behavior such as `/proc/self/fd`, `O_TMPFILE`, fallocate flags, mount inode checks, and optional `.ismount` stubs. Portability and containerized mount detection are explicit risk areas.
- `fallocate()` error handling intentionally ignores unsupported-function errors but raises for other errno values. Incorrect errno handling can turn allocation failures into silent data-placement or ENOSPC issues.
- `lock_file()` and `lock_path()` rely on advisory locks and eventlet scheduling; misuse with non-cooperative code can still deadlock or starve.
- Multipart parsing is boundary-buffer based and caller-facing; malformed client input can produce `MimeInvalid` or `ChunkReadError`, while large or adversarial boundaries may stress buffering assumptions.
- `streq_const_time()` assumes string-like inputs whose elements can be passed to `ord()`. Passing bytes in Python 3 would produce ints and break.
- `LRUCache` stores state in the decorator instance and is not explicitly synchronized; shared use across native threads would be unsafe.
- `NamespaceBoundList.get_namespace()` assumes non-empty bounds and that the item maps at or after the first lower bound; bad or gapped inputs can map to the preceding namespace by design.
- `ShardRange` is mutable but intentionally hashable by identity despite equality comparing bounds, which is useful for internal maps but violates common hash/equality expectations.
- `Watchdog` uses eventlet hub internals and caller greenthread references; leaked or uncancelled timeouts can hold references and throw into unexpected greenthread lifecycles.

## Test Signals

The local OpenStack Swift snapshot under `sources/object-store/openstack-swift` does not include a `test` or `tests` tree, so no runnable in-repo tests were available for this research item. Strong expected coverage would include unit tests for hash config loading and `hash_path()`, fallocate and hole-punch error paths with mocked libc wrappers, lock race handling, recon cache atomic updates, MIME/range parser round trips, `LRUCache` timeout eviction, `Spliterator` slicing, namespace and shard-range ordering/serialization, systemd notification socket behavior, and watchdog timeout scheduling. Integration signals are widespread imports from account/container/object servers, proxy controllers, daemon/wsgi startup, sharder/reconciler/relinker, middleware, and CLI commands.

<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/base.py -->
# sources/object-store/openstack-swift/swift/common/utils/base.py

## Purpose

`base.py` holds low-level utility functions that other `swift.common.utils` split modules may import without creating circular dependencies. It intentionally imports only standard-library modules and is used by `__init__.py`, logging utilities, CLI code, and request/path parsing code.

## Important APIs, Types, And Functions

- `md5(string=b'', usedforsecurity=True)` wraps `hashlib.md5`, preserving support for Python distributions that accept the `usedforsecurity` keyword while falling back gracefully on distributions that do not.
- `get_valid_utf8_str(str_or_unicode)` accepts bytes or text, decodes invalid UTF-8 with replacement if needed, collapses surrogate pairs through UTF-16 encode/decode, and returns valid UTF-8 bytes.
- `quote(value, safe='/')` URL-quotes values after UTF-8 normalization and returns bytes when the caller passed bytes, preserving legacy behavior.
- `split_path(path, minsegs=1, maxsegs=None, rest_with_last=False)` validates and splits Swift HTTP paths into account/container/object-style segments, padding missing trailing segments with `None`.

## Control Flow And Behavior

At import time, the module probes whether `hashlib.md5(usedforsecurity=False)` is accepted. The successful branch forwards the keyword, while the fallback branch ignores it. This lets Swift use MD5 for non-security storage hashing on FIPS-aware Python builds while retaining older Python compatibility.

`get_valid_utf8_str()` first decodes bytes with `surrogatepass`; on decode failure it uses replacement. It then encodes through UTF-16 with surrogate pass and decodes with replacement to collapse invalid surrogate content before returning UTF-8 bytes. `quote()` feeds those bytes into `urllib.parse.quote` and preserves byte-return behavior for byte input.

`split_path()` enforces a leading slash, minimum and maximum segment counts, and optional "rest with last" behavior for object names containing slashes. It uses `quote(path)` in error messages so invalid or unsafe paths are printable. It rejects empty required segments, rejects extra trailing data unless `rest_with_last` is enabled, and pads the result to the requested maximum segment count.

## State And Persistence

The module has no persistent state. Import-time state is limited to decoder/encoder function objects and the selected `md5` wrapper implementation.

## Dependencies And Integration Points

Dependencies are standard library `codecs`, `hashlib`, and `urllib.parse.quote`. `__init__.py` re-exports all four public helpers. `swift.common.utils.logs` imports `md5`, `quote`, and `split_path`; CLI tools and middleware use `md5` and `split_path`; request parsing throughout account/container/object/proxy paths depends on the exact validation behavior.

## Risks And Edge Cases

- `split_path()` returns a fixed-length list padded with `None`; callers that assume only actual path components may mis-handle optional segments.
- With `rest_with_last=True`, the final returned segment may contain slashes by design.
- The bytes/text preservation in `quote()` is legacy-sensitive; changing return type would break callers that compare or concatenate bytes.
- `get_valid_utf8_str()` intentionally replaces invalid data rather than raising, which is useful for logging/quoting but should not be treated as lossless validation.
- The MD5 wrapper is explicitly for non-security uses. Passing `usedforsecurity=True` on a FIPS-restricted platform can still be rejected by the underlying Python/OpenSSL stack.

## Test Signals

No local test tree is present in this source snapshot. Expected test cases include `md5()` with and without `usedforsecurity` support, invalid UTF-8 and surrogate normalization, `quote()` return type for bytes versus str, and `split_path()` boundary cases for missing leading slash, empty required segments, excessive segments, padded optional segments, and object names containing slash separators.

<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/checksum.py -->
# sources/object-store/openstack-swift/swift/common/utils/checksum.py

## Purpose

`checksum.py` provides hashlib-like CRC hashers for Swift checksum use cases, especially S3 checksum headers. It chooses the fastest available implementation for CRC32C and CRC64-NVME across optional `anycrc`, ISA-L, and Linux kernel AF_ALG support, while always providing CRC32 through `zlib.crc32`.

## Important APIs, Types, And Functions

- `find_isal()` locates an ISA-L shared library either system-wide through `ctypes.util.find_library('isal')` or inside a `pyeclib` package installation.
- Optional implementation functions are `crc32c_isal`, `crc64nvme_isal`, `crc32c_kern`, `crc32c_anycrc`, and `crc64nvme_anycrc`.
- `_select_crc32c_impl()` chooses `crc32c_isal`, then kernel AF_ALG, then `anycrc`, raising `NotImplementedError` if none are present.
- `_select_crc64nvme_impl()` chooses ISA-L, then `anycrc`, raising `NotImplementedError` if neither is present.
- `CRCHasher` is a hashlib-style wrapper with `update()`, `digest()`, `hexdigest()`, `copy()`, `digest_size`, and `digest_fmt`.
- `crc32(data=None, initial_value=0)`, `crc32c(data=None, initial_value=0)`, and `crc64nvme(data=None, initial_value=0)` create `CRCHasher` instances.
- `log_selected_implementation(logger)` emits info/warning lines for the selected CRC32C and CRC64-NVME implementations.

## Control Flow And Behavior

Import-time detection first tries `anycrc` and creates callable model calculators when available. `find_isal()` then attempts to load ISA-L. If ISA-L exposes `crc32_iscsi`, the module configures ctypes signatures and defines `crc32c_isal()` with the required XOR pre/post processing. If ISA-L exposes `crc64_rocksoft_refl`, it configures and defines `crc64nvme_isal()`. Finally, it probes Linux AF_ALG support for `"hash", "crc32c"`; if available, `crc32c_kern()` creates a keyed AF_ALG socket per computation, sends data, and returns the kernel digest value.

`CRCHasher` stores the selected CRC function, current integer CRC, name, and width. `update()` folds new data into `self.crc`, `digest()` packs the current integer as big-endian 32-bit or 64-bit bytes, `hexdigest()` hex-encodes that packed value, and `copy()` creates a new hasher with the same function and current CRC. The public factory functions mirror hashlib constructors by accepting optional initial data.

## State And Persistence

The module keeps process-global feature-detection state: loaded ISA-L handle, optional implementation callables, and selected functions. `CRCHasher` instances hold only in-memory checksum state. There is no disk persistence.

## Dependencies And Integration Points

Dependencies include optional `anycrc`, optional `pyeclib`, `ctypes`, `ctypes.util`, `importlib.metadata`, Linux `socket.AF_ALG`, `struct`, `binascii`, and `zlib`. S3 middleware imports `swift.common.utils.checksum` for `x-amz-checksum-crc32c` and `x-amz-checksum-crc64nvme` handling. Operators can use `log_selected_implementation()` to expose runtime checksum capability.

## Risks And Edge Cases

- `hasattr(isal, ...)` is called even when `find_isal()` returns `None`; this is safe because `hasattr(None, ...)` is false, but later code depends on those globals being set to `None`.
- Kernel AF_ALG probing closes `_sock` only for the ENOENT branch; unsupported address family and successful probe paths do not retain an explicit global socket, but the temporary object is left to normal cleanup.
- CRC32C implementation selection happens on each hasher creation, so a missing optional library raises at call time rather than import time.
- `CRCHasher.digest_size` returns `self.width / 8`, a float in Python 3, unlike hashlib's integer `digest_size`.
- `update()` expects bytes-like input accepted by the selected backend; passing text will fail differently depending on backend.
- AF_ALG setup per `crc32c_kern()` call is slower but intentionally lower priority than ISA-L.
- CRC64-NVME support depends on ISA-L >= 2.31.0 or `anycrc`; older deployments will raise `NotImplementedError`.

## Test Signals

The local source snapshot has no tests directory. Expected coverage should compare known CRC32, CRC32C, and CRC64-NVME vectors across initial values and incremental `update()` calls; validate `copy()` state independence; mock ISA-L, AF_ALG, and `anycrc` availability to confirm implementation preference and `NotImplementedError` paths; assert `log_selected_implementation()` emits useful warnings; and verify S3 middleware rejects unsupported checksums predictably when optional backends are absent.

<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/checksum.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/config.py -->
# sources/object-store/openstack-swift/swift/common/utils/config.py

## Purpose

`config.py` centralizes Swift configuration parsing and validation helpers. It converts string values from `.conf` files into booleans, numbers, percentages, request-node-count functions, fallocate reserve settings, reseller-prefix option maps, affinity sort/predicate functions, and section dictionaries from one config file or a directory of config files.

## Important APIs, Types, And Functions

- `TRUE_VALUES` defines string truth values: `true`, `1`, `yes`, `on`, `t`, and `y`.
- Boolean and numeric validators include `config_true_value()`, `non_negative_float()`, `non_negative_int()`, `config_positive_int_value()`, `config_positive_float_value()`, `config_float_value()`, `config_auto_int_value()`, and `config_percent_value()`.
- Ring/request behavior parsers include `config_request_node_count_value()` and `config_fallocate_value()`.
- Prefix helpers include `config_read_prefixed_options()`, `append_underscore()`, and `config_read_reseller_options()`.
- Ring-affinity helpers include `affinity_key_function()` and `affinity_locality_predicate()`.
- File readers include `read_conf_dir()`, `NicerInterpolation`, `readconf()`, and `parse_prefixed_conf()`.

## Control Flow And Behavior

The small validators parse input, enforce bounds, and raise `ValueError` with configuration-oriented messages. `config_auto_int_value()` returns a caller-provided default for `None` or `"auto"`, while `config_percent_value()` returns a fraction between `0.0` and `1.0`. `config_request_node_count_value()` returns a closure that maps replica count to either a constant or `N * replicas`.

Reseller-prefix flow reads `reseller_prefix`, treats `"''"` as an empty prefix, ensures prefixes end with underscores, deduplicates them, then builds per-prefix option dictionaries by applying unprefixed options followed by prefix-specific overrides. `config_read_prefixed_options()` recognizes list defaults by splitting lower-cased comma-separated values; scalar defaults are stripped strings.

Affinity flow parses strings such as `r1=1` or `r2z7=2`, builds matcher dictionaries, sorts by priority, and returns a key function that places matching ring nodes ahead of unmatched nodes. Locality flow parses strings such as `r1` or `r2z2` and returns a predicate that accepts ring nodes matching any configured region/zone.

`readconf()` chooses `RawConfigParser` when raw mode is requested and otherwise uses `ConfigParser` with `NicerInterpolation`. The custom interpolation bypasses interpolation work unless the value contains `"%("`, preserving common Swift values like `1%` while still allowing legacy interpolation. It preserves option-case with `optionxform = str`, reads from file-like objects, single files, or sorted `.conf` files in a directory, and returns either one section dict with `log_name` or an all-sections mapping plus `__file__`.

## State And Persistence

The module has no mutable persistent state beyond `TRUE_VALUES`. It reads configuration files and directories but does not write them. Returned dictionaries include `__file__` pointing back to the original `conf_path`.

## Dependencies And Integration Points

Dependencies are standard `os`, `operator`, `re`, and `configparser`. `__init__.py` re-exports these helpers. They are used throughout Swift: daemon and WSGI startup read `.conf` files and parse daemonization/fallocate/eventlet settings; servers and middleware parse booleans; storage policy code parses deprecation/default flags; proxy code parses behavior toggles; backend-rate-limit and keymaster middleware read specific config sections; ring and proxy logic use affinity functions.

## Risks And Edge Cases

- `config_true_value()` only returns true for literal `True` or recognized strings; numeric `1` is false unless represented as `"1"`.
- `config_fallocate_value()` indexes `reserve_value[-1:]`, so callers must pass a sliceable value, usually a string.
- `config_read_prefixed_options()` ignores falsey values entirely, so an explicit empty string cannot override a default.
- `config_request_node_count_value()` returns closures; callers must remember to call the returned function with replica count.
- Affinity parsing is strict and raises for malformed pieces; deployment typos can prevent service startup.
- `read_conf_dir()` reads sorted visible `.conf` files only, so hidden files and non-`.conf` suffixes are intentionally ignored.
- `readconf()` all-sections mode returns a nested mapping keyed by section names and also a top-level `log_name`, so callers must distinguish section names from metadata.
- `NicerInterpolation` preserves `1%`-style values by bypassing interpolation unless `"%("` is present; this is compatibility-sensitive.

## Test Signals

No local tests are available in this source snapshot. Expected coverage includes truth table tests for boolean parsing; numeric validator bounds and error messages; `"auto"` handling; percentage conversion; request-node-count closures; fallocate byte/percent parsing; reseller-prefix empty-prefix and override behavior; affinity key ordering and locality predicate validation; `readconf()` file, directory, file-like, raw, missing-section, missing-file, and interpolation cases; and `parse_prefixed_conf()` section filtering.

<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/ipaddrs.py -->
# sources/object-store/openstack-swift/swift/common/utils/ipaddrs.py

## Purpose

`ipaddrs.py` provides IP address validation, IPv6 normalization, local interface address discovery, and host/port parsing for Swift service and middleware configuration. It is split out so network-address helpers can be reused without importing the full `swift.common.utils` compatibility module.

## Important APIs, Types, And Functions

- `IPV6_RE` validates bracketed IPv6 host literals with an optional port.
- `is_valid_ip()`, `is_valid_ipv4()`, and `is_valid_ipv6()` validate textual addresses using `socket.inet_pton`.
- `expand_ipv6(address)` round-trips through `inet_pton`/`inet_ntop` to normalize a valid IPv6 address.
- `errcheck()` is a ctypes error checker for `getifaddrs`.
- ctypes structures `sockaddr_in4`, `sockaddr_in6`, and `ifaddrs` model the subset of libc interface-address structures Swift needs, with Linux versus BSD/macOS field layouts.
- `whataremyips(ring_ip=None)` returns the service's relevant IPs, either a specific configured bind/ring IP or all local interface IPv4/IPv6 addresses when binding to wildcard addresses.
- `parse_socket_string(socket_string, default_port)` parses DNS names, IPv4 addresses, or bracketed IPv6 literals with optional port into `(host, port)`.

## Control Flow And Behavior

Import-time code loads libc with `use_errno=True`, binds `getifaddrs` and `freeifaddrs`, and installs `errcheck()` on `getifaddrs`. Structure definitions switch on `platform.system()` so Linux uses 16-bit address-family fields while BSD/macOS include leading length bytes.

`whataremyips()` first handles a configured `ring_ip`. If it can be resolved as a numeric host and is not `0.0.0.0` or `::`, it returns that value directly. Otherwise, it calls `getifaddrs()`, iterates the linked list, skips entries without addresses, converts IPv4 and IPv6 addresses with `inet_ntop`, and frees the linked list in a `finally` block.

`parse_socket_string()` defaults the port, requires IPv6 literals to start with `[`, applies `IPV6_RE` to bracketed hosts, rejects unbracketed strings with more than one colon as ambiguous IPv6, and otherwise splits `host:port` or returns the bare host with default port.

## State And Persistence

The module holds process-global ctypes handles for libc functions. It reads kernel/network interface state through `getifaddrs()` but does not persist anything.

## Dependencies And Integration Points

Dependencies are `ctypes`, `ctypes.util`, `os`, `platform`, `re`, and `socket`. `__init__.py` re-exports the public helpers. `whataremyips()` is used by storage policy, account/container services, replicators, reconstructors, reapers, sharder, and sync code to decide local-device ownership and bind/listen identity. `parse_socket_string()` is used by memcached and cname lookup configuration parsing. Validation helpers are used by rsync formatting and network option handling.

## Risks And Edge Cases

- `errcheck()` calls `ctypes.set_errno(0)` rather than `ctypes.get_errno()`, which appears unusual for reporting the actual libc errno.
- ctypes structure layouts must match platform ABI. The module assumes any non-Linux platform is BSD/macOS-like.
- `whataremyips()` returns the configured `ring_ip` directly when it is specific, even if that value is a hostname rather than an IP after `getaddrinfo()` failure.
- The returned address list may include duplicates, loopback addresses, IPv6 link-local addresses, and interface-order-dependent values.
- `parse_socket_string()` returns `port` as whatever string/default was provided; it does not coerce to int or validate port range.
- Bracketed IPv6 parsing validates bracket syntax but does not call `is_valid_ipv6()` on the captured address.

## Test Signals

No local test tree is present. Expected coverage should mock `socket.inet_pton`, `socket.getaddrinfo`, and `getifaddrs()` linked-list data; validate IPv4/IPv6 positive and negative cases; verify wildcard versus specific `ring_ip` behavior; confirm `freeifaddrs()` is called on success and error; and exercise `parse_socket_string()` for hostnames, IPv4 with port, bracketed IPv6 with and without port, unbracketed IPv6 rejection, and default-port preservation.

<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/ipaddrs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/libc.py -->
# sources/object-store/openstack-swift/swift/common/utils/libc.py

## Purpose

`libc.py` isolates Swift's direct interactions with libc and Linux-specific low-level APIs. It provides lazy libc function lookup, cache-dropping advisory calls, Linux AF_ALG MD5 socket setup, process nice/ionice priority modification, and exported constants used by diskfile and daemon code.

## Important APIs, Types, And Functions

- Global lazy handles include `_posix_fadvise`, `_libc_socket`, `_libc_bind`, `_libc_accept`, `_libc_setpriority`, and `_posix_syscall`.
- `NR_ioprio_set()` returns the architecture-specific Linux syscall number for `ioprio_set` on x86_64 and aarch64, otherwise raises `OSError`.
- `IOPRIO_PRIO_VALUE(class_, data)` composes Linux ionice class and priority bits.
- Constants include `PRIO_PROCESS`, `IOPRIO_WHO_PROCESS`, `IO_CLASS_ENUM`, `IOPRIO_CLASS_SHIFT`, `AF_ALG`, and `F_SETPIPE_SZ`.
- `noop_libc_function()` is the no-op fallback for missing optional functions.
- `load_libc_function(func_name, log_error=True, fail_if_missing=False, errcheck=False)` loads a libc function, optionally raising when absent and optionally adding an errno-checking `errcheck`.
- `_LibcWrapper` is a lazy callable wrapper exposing `.available` and raising `NotImplementedError` when the function cannot be loaded.
- `drop_buffer_cache(fd, offset, length)` calls `posix_fadvise64(..., POSIX_FADV_DONTNEED)`.
- `sockaddr_alg` models Linux AF_ALG socket address data.
- `get_md5_socket()` returns an accepted AF_ALG MD5 socket fd for callers to write data and read a 16-byte digest.
- `modify_priority(conf, logger)` applies `nice_priority`, `ionice_class`, and `ionice_priority` settings to the current process.

## Control Flow And Behavior

`load_libc_function()` loads libc with `use_errno=True` each time it needs a symbol. Missing functions either raise `AttributeError`, log a warning and return `noop_libc_function`, or silently return the no-op depending on arguments. When `errcheck=True`, a wrapper raises `OSError(ctypes.get_errno(), os.strerror(errcode))` for `-1` results.

`_LibcWrapper` defers symbol lookup until `.available` or `__call__()` is used. It marks itself loaded after the first attempt and caches the handle when found. Missing functions make `.available` false and calls raise `NotImplementedError`, which lets higher-level code choose fallbacks without repeated libc lookups.

`drop_buffer_cache()` lazily loads `posix_fadvise64`, calls it with offset/length as unsigned 64-bit values and advice `4` (`POSIX_FADV_DONTNEED`), and logs a warning for nonzero return values.

`get_md5_socket()` lazily loads `accept`, `socket`, and `bind`. On the first call it creates one bound AF_ALG `"hash"`/`"md5"` socket and stores it in `_bound_md5_sockfd`. Each call then accepts a new operation socket from the bound socket and returns the raw fd. Callers are responsible for closing returned fds.

`modify_priority()` lazily loads `setpriority` with errno checking and applies `nice_priority` if configured. It then lazily loads `syscall` and, when `ionice_class` is configured, computes the Linux `ioprio_set` argument and calls the syscall for the current pid. Invalid classes, priorities, unsupported architectures, and OS errors are caught, printed as warnings, and logged with exceptions.

## State And Persistence

The module holds process-global cached libc handles and one cached bound MD5 AF_ALG socket fd. It mutates process scheduling state through `setpriority` and `ioprio_set`. It issues advisory kernel calls for page cache dropping. It does not write persistent files, but leaked raw fds would persist for the process lifetime.

## Dependencies And Integration Points

Dependencies are standard `ctypes`, `ctypes.util`, `fcntl`, `logging`, `os`, `platform`, and `socket`. `__init__.py` re-exports `F_SETPIPE_SZ`, `load_libc_function`, `drop_buffer_cache`, `get_md5_socket`, `modify_priority`, and `_LibcWrapper`. Object diskfile code imports `get_md5_socket` and `F_SETPIPE_SZ`; daemon and WSGI startup call `modify_priority`; common utils uses `_LibcWrapper` for fallocate wrappers; diskfile or storage code can call `drop_buffer_cache()` after streaming file data.

## Risks And Edge Cases

- The module is Linux-heavy. `NR_ioprio_set()` only supports x86_64 and aarch64 64-bit systems.
- `get_md5_socket()` exposes a raw file descriptor; callers must close it exactly once. Failure leaks fds.
- AF_ALG constants and `sockaddr_alg` structure are Linux-specific; unsupported kernels or missing algorithms raise IOErrors during setup.
- `_bound_md5_sockfd` is shared process-wide and never explicitly closed; this is intentional for reuse but must be acceptable for daemon lifecycle.
- `load_libc_function()` catches only `AttributeError`, not failures to load libc itself.
- `drop_buffer_cache()` treats missing `posix_fadvise64` as a no-op via `load_libc_function()` but still logs return-code warnings for real calls.
- `modify_priority()` prints to stdout/stderr as well as logging exceptions, which can be noisy in daemonized contexts but preserves operator visibility.
- `IOPRIO_PRIO_VALUE()` and `IO_CLASS_ENUM` do not validate Linux priority range beyond integer conversion.

## Test Signals

No local tests are present in this snapshot. Expected coverage should mock libc loading and function return values for `load_libc_function()` and `_LibcWrapper`, verify errno propagation, test `NR_ioprio_set()` architecture branches, confirm `drop_buffer_cache()` argument conversion and warning behavior, simulate AF_ALG socket/bind/accept failures and success in `get_md5_socket()`, and assert `modify_priority()` handles valid settings, invalid class/priority, unsupported architecture, and syscall errors without crashing daemon startup.

<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/libc.py -->
