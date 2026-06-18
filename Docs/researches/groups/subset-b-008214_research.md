# subset-b-008214 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/db_replicator.py -->
# sources/object-store/openstack-swift/swift/common/db_replicator.py

Purpose: implements the shared database replication engine used by account and container services. It scans local storage-device database trees, compares local broker state with peer replicas, syncs by row diffs or rsync, reclaims deleted/old rows, removes handoff copies when safe, and exposes the server-side RPC operations used by remote replicators.

Important APIs/types/functions: `quarantine_db` moves corrupt DB hash directories into a quarantine tree; `roundrobin_datadirs` walks partition/suffix/hash directories fairly across devices; `ReplConnection.replicate` sends JSON `REPLICATE` RPC calls; `BrokerAnnotatedLogger` adds broker path and db file context to logs; `Replicator` owns config, ring lookup, scanning, sync-mode selection, stats, recon cache output, and handoff cleanup; `ReplicatorRpc` handles incoming `sync`, `merge_items`, `merge_syncs`, `complete_rsync`, and `rsync_then_merge` requests. Subclasses are expected to provide `server_type`, `default_port`, `datadir`, and `brokerclass`.

Control flow: `run_forever` sleeps a jittered interval and repeatedly calls `run_once`. `run_once` resolves local devices from the ring, validates mounts, cleans tmp files, builds per-device datadir iterators, and spawns `_replicate_object` work in a green pool. `_replicate_object` opens the broker, reclaims old rows, verifies the partition, gathers primary and handoff peers, and calls `_repl_to_node` for each peer. The peer response drives `_handle_sync_response`: missing remote DBs trigger `_rsync_db`, matching hashes/sync points are no-ops, large divergence uses `rsync_then_merge`, and normal divergence sends batches through `_usync_db`. Incoming RPCs mirror this protocol by returning replication info, merging items/syncs, or atomically renaming rsynced temporary DBs into place.

State and persistence: state lives in SQLite broker files under device datadirs, sync tables, metadata/timestamp fields, tmp rsync files, quarantine directories, removed handoff hash directories, and recon cache JSON. Runtime stats are in memory and written to recon after each pass. Handoff deletion is conservative: local copies are only removed when no rows were added during the pass and enough peer syncs succeeded.

Dependencies and integration: integrates with Swift ring placement, storage directory layout, DB broker APIs, rsync modules, eventlet-style timeouts/green pools, mount checks, recon, and HTTP `REPLICATE` routing. Account and container replicator daemons subclass this common engine.

Risks: corruption handling relies on exception string matching for "no such table"; rsync success followed by broker mutation requires the second locked rsync pass; `max_diffs` caps can defer convergence; handoff deletion policy must match replica count and operator intent; remote 507 handling depends on enough handoff nodes; race windows around tmp files and existing DBs are mitigated but still central to correctness. Tests should cover corrupt DB quarantine, partition mismatch cleanup, hash-match fast path, row-diff batching, rsync/merge paths, handoff delete thresholds, mount failures, and RPC response semantics.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/db_replicator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/digest.py -->
# sources/object-store/openstack-swift/swift/common/digest.py

Purpose: centralizes digest algorithm selection and client-supplied digest parsing for Swift features such as temporary URLs and checksum headers.

Important APIs/types/functions: `DEFAULT_ALLOWED_DIGESTS` names sha1, sha256, and sha512; `DEPRECATED_DIGESTS` marks sha1; `SUPPORTED_DIGESTS` is the supported set; `get_hmac` builds a newline-delimited HMAC message from request method, expiry, path, and optional `ip=<range>` prefix; `get_allowed_digests` normalizes configured algorithms, filters unsupported entries, warns on deprecated entries, and errors when nothing valid remains; `extract_digest_and_algorithm` accepts either plain hex digests or `algorithm:base64-digest` values and returns `(algorithm, hex_digest)`.

Control flow: HMAC creation first builds ordered message parts, optionally inserts IP range ahead of the method to avoid path-newline ambiguity, converts keys and parts to bytes, and delegates to `hmac.new`. Digest config handling lowercases input, defaults empty config to the supported set, subtracts unsupported algorithms, logs warnings, then returns valid and deprecated subsets. Digest extraction branches on `:`, decoding standard or URL-safe base64 when an algorithm is explicit, otherwise validates hex and infers algorithm from digest length.

State and persistence: stateless; constants are module-level policy. No persistent data is modified.

Dependencies and integration: uses `hmac`, `binascii`, and Swift `strict_b64decode`. Called by middleware and request validation paths that need compatible HMAC and digest parsing.

Risks: empty configured digest list currently allows deprecated sha1 by default; callers must enforce allowed algorithms after `extract_digest_and_algorithm`; base64 decoding pads with `==`, which is permissive by design; IP range ordering is security-sensitive for temporary URL signatures. Tests should cover allowed/deprecated logging, unsupported-only failure, hex length inference, URL-safe base64, bad base64/hex input, and HMAC compatibility with existing tempurl signatures.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/digest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/direct_client.py -->
# sources/object-store/openstack-swift/swift/common/direct_client.py

Purpose: provides low-level helpers for Swift internal tools and daemons to call account, container, object, replication, and recon servers directly, bypassing the proxy path.

Important APIs/types/functions: `DirectClientException` and `DirectClientReconException` wrap failed backend responses with host, device, status, reason, and headers. `_make_req` is the common request/send/read helper for most methods. `_get_direct_account_container` implements JSON listings. `gen_headers` adds direct-client user agent and reserved-name allowance. Public helpers include `direct_get_account`, container CRUD/listing methods, object HEAD/GET/PUT/POST/DELETE, `direct_get_suffix_hashes`, `direct_get_recon`, and `retry`.

Control flow: path helpers quote Swift path components, `get_ip_port` selects normal or replication network endpoint from node/header inputs, and `http_connect` or `http_connect_raw` opens the backend connection under connect timeout. `_make_req` handles optional bodies by setting `Content-Length` or chunked transfer encoding, streams body chunks under send timeout, reads the full response under response timeout, and raises on non-2xx statuses. Listing helpers force `format=json`, add marker/limit/prefix/delimiter/end_marker/reverse parameters, and return `HeaderKeyDict` plus decoded JSON or empty listing on 204. `retry` retries socket, HTTP, timeout, and retryable 5xx client exceptions with exponential backoff, but not 507.

State and persistence: no durable state; side effects are backend HTTP operations that create/update/delete Swift DB and object state. Request defaults add current timestamps and reserved-name headers.

Dependencies and integration: depends on Swift buffered HTTP connections, eventlet-style timeouts, ring node dicts, `HeaderKeyDict`, `Timestamp`, `FileLikeIter`, pickle loading for suffix hashes, and Swift HTTP status helpers. It is used by replication, dispersion, recon, and operational code needing direct storage-node access.

Risks: direct calls bypass proxy middleware and must provide correct backend headers; GET with `resp_chunk_size` returns a generator tied to an open response; `_make_req` drains responses before returning, so it is not suitable for streaming reads; chunked request body framing must remain exact; retry can amplify load during outages. Tests should cover query duplicate detection, header normalization, chunked and fixed-length PUTs, exception metadata, replication-network suffix hash calls, retry stop conditions, and recon JSON failures.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/direct_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/error_limiter.py -->
# sources/object-store/openstack-swift/swift/common/error_limiter.py

Purpose: tracks recent backend node errors and suppresses use of nodes that exceed a configured error count for a configured interval.

Important APIs/types/functions: `ErrorLimiter` stores `suppression_interval`, `suppression_limit`, and a `stats` mapping keyed by `node_to_string`. `is_limited` reports and expires suppression state, `limit` immediately forces a node over the threshold, and `increment` records one error and reports whether the threshold is exceeded.

Control flow: `increment` and `limit` update `errors` and `last_error` for a node. `is_limited` returns false if no errors exist, removes stale entries when the last error is older than the interval, and otherwise checks `errors > suppression_limit`.

State and persistence: all state is in-memory per process; suppression resets on process restart. The map can grow with distinct nodes until entries are checked and expired.

Dependencies and integration: depends on `time.time` and Swift `node_to_string`. Used by proxy/backend selection code to avoid repeatedly selecting unhealthy storage nodes.

Risks: no locking is used, so concurrent green threads share mutable dictionaries cooperatively; stale entries only disappear when checked; threshold is strictly greater than the limit, so a limit of N allows N errors and suppresses on N+1; key stability depends on `node_to_string`. Tests should cover threshold boundary, immediate limit, expiry cleanup, and node key normalization.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/error_limiter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/exceptions.py -->
# sources/object-store/openstack-swift/swift/common/exceptions.py

Purpose: defines Swift's shared exception taxonomy for disk files, rings, replication, memcache, clients, timeouts, listing iterators, encryption, and process management.

Important APIs/types/functions: `MessageTimeout` extends Swift `Timeout` with a message; `SwiftException` is the base for many domain exceptions; disk-file exceptions distinguish missing, deleted, expired, quarantined, collision, no space, unavailable device, xattr, and metadata checksum states; ring exceptions distinguish load/build/validation problems; replication lock and partition lock exceptions specialize `LockTimeout`; memcache exceptions communicate connection, incr race, and pool timeout failures; `ClientException` carries HTTP scheme/host/port/path/query/status/reason/device/body/headers and formats them into a useful string; `InvalidPidFileException` protects process management.

Control flow: most classes are markers. `DiskFileDeleted` derives a `Timestamp` from metadata or zero. `ListingIterNotAuthorized` stores the auth response. `ClientException.__str__` incrementally appends URL, status, reason, device, and short response content to the base message.

State and persistence: exception instances store transient context only. No persistent state is modified.

Dependencies and integration: imports Swift concurrency `Timeout` and timestamp handling. These exceptions are used throughout storage, proxy, ring, replication, memcache, and manager code to communicate typed failures without circular definitions.

Risks: marker classes rely on callers catching the correct subclass; some names intentionally shadow Python built-ins (`FileNotFoundError`, `PermissionError`) within this module; `ClientException` only includes the first 60 response chars; `PutterConnectError` does not call `Exception.__init__`. Tests should cover string formatting, deleted timestamp defaults, timeout string formatting, and catch hierarchies expected by diskfile, proxy, and replication code.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/exceptions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/header_key_dict.py -->
# sources/object-store/openstack-swift/swift/common/header_key_dict.py

Purpose: implements a small HTTP header dictionary that normalizes keys to title case and treats lookups as case-insensitive for Swift WSGI-string headers.

Important APIs/types/functions: `HeaderKeyDict` overrides `update`, `__getitem__`, `__setitem__`, `__contains__`, `__delitem__`, `get`, `setdefault`, and `pop`. `_title` encodes Latin-1, applies byte title-casing, and decodes back to Latin-1.

Control flow: construction updates from an optional mapping/iterable and kwargs. Setting a value title-cases the key, removes the header when value is `None`, decodes byte values as Latin-1, and stringifies other values. Reads and deletes title-case the requested key before delegating to `dict`.

State and persistence: state is the in-memory dict contents. There is no persistence.

Dependencies and integration: self-contained and used by direct-client and HTTP response handling paths that need case-insensitive header access while preserving WSGI string behavior.

Risks: unlike a full multi-dict, repeated headers collapse to one value; `__getitem__` returns `None` instead of raising `KeyError`; title-casing may not preserve original spelling such as `ETag`; all non-byte values are coerced with `str`. Tests should cover mixed-case lookup, bytes values, deletion by `None`, iterable updates, and behavior for missing keys.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/header_key_dict.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/http.py -->
# sources/object-store/openstack-swift/swift/common/http.py

Purpose: provides common HTTP status classifiers and named status-code constants used across Swift without repeatedly importing larger HTTP frameworks.

Important APIs/types/functions: `is_informational`, `is_success`, `is_redirection`, `is_client_error`, and `is_server_error` check status-code ranges. Constants cover common 1xx through 5xx codes plus Swift/vendor-specific values such as 498, 499, 529 consumers via other modules, and network timeout pseudo-codes 598/599.

Control flow: classifier functions are direct numeric range checks. The rest of the file is constant definitions grouped by status class.

State and persistence: no mutable or persistent state.

Dependencies and integration: self-contained. Imported by clients, middleware, proxy, object, container, account, and tests for readable status comparisons.

Risks: constants are manually maintained, including misspellings kept for compatibility such as `HTTP_UPGRADE_REQUIED`; classifiers assume integer status inputs; non-standard codes are intentionally included and may not match external libraries. Tests should verify range helpers and any code paths depending on non-standard constants.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/http.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/http_protocol.py -->
# sources/object-store/openstack-swift/swift/common/http_protocol.py

Purpose: customizes eventlet's WSGI HTTP protocol for Swift's proxy/server edge behavior, including request parsing, header quirks, error responses with transaction IDs, eventlet compatibility fixes, and optional HAProxy PROXY protocol support.

Important APIs/types/functions: `SwiftHttpProtocol` overrides request logging, message logging, `parse_request`, `get_environ`, request-state handling, and `send_error`. Its nested `MessageClass` suppresses default content type. `SwiftHttpProxiedProtocol` consumes the first PROXY protocol line, rewrites client/server address metadata, and then delegates normal HTTP handling.

Control flow: `parse_request` decodes the raw line as ISO-8859-1, splits on literal spaces, validates HTTP version, rejects HTTP/2+, strips absolute URI scheme/host to a path, parses headers with eventlet's green HTTP parser, handles connection semantics, and processes `Expect: 100-continue`. `get_environ` compensates for Python/email parser payload bugs by recovering header lines from payload text, updating `headers_raw`, WSGI variables, chunked/content-length flags, and continue handling. `send_error` obtains or generates a transaction ID, logs, sends a close response, omits bodies for no-body status classes, and adds Swift request ID headers. The proxied protocol validates `PROXY TCP4/TCP6` or `UNKNOWN`, updates addresses, or sends a 400 and stops processing.

State and persistence: per-connection/request state includes parsed command/path/version/headers, close flags, connection state, client/proxy addresses, and logger transaction ID. No durable persistence.

Dependencies and integration: depends on Swift concurrency wrappers for eventlet WSGI/websocket/HTTP parser, Swift transaction ID generation, HTTP constants, and `html.escape`. It is selected by Swift WSGI server setup when serving HTTP or PROXY-protocol traffic.

Risks: request parsing is security-sensitive; compatibility workarounds for Python email parsing and eventlet state changes must track upstream behavior; absolute URI stripping affects proxy-style requests; PROXY parsing trusts the immediate peer to provide client address data; error output must avoid XSS and body-forbidden statuses. Tests should cover malformed versions, header limits, header payload recovery, expect-continue, no-body errors, transaction ID headers, and valid/invalid PROXY lines.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/http_protocol.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/internal_client.py -->
# sources/object-store/openstack-swift/swift/common/internal_client.py

Purpose: offers Swift-internal clients that interact with a loaded proxy WSGI app or simple HTTP endpoints for operational daemons, dispersion tools, and container sync.

Important APIs/types/functions: `UnexpectedResponse` carries the failed response; `CompressingFileReader` streams gzip-compatible compressed data from a file object; `InternalClient` loads or accepts a proxy app and exposes account, container, and object CRUD/listing/metadata helpers; `get_auth` implements auth v1.0 token retrieval; `SimpleClient` is a urllib-based retrying client; module-level `head_object`, `put_object`, and `delete_object` wrap `SimpleClient`.

Control flow: `InternalClient.__init__` loads the proxy pipeline, rejects gatekeeper middleware, sets the backend user agent, caches rings, and optionally enables replication-network backend headers. `make_request` builds a `swob.Request`, attaches body files and params, executes `get_response` in a separate green thread to isolate corolocals, accepts explicit or class status codes, retries server errors/exceptions with exponential sleep, drains or closes response bodies between attempts, and raises `UnexpectedResponse` or the last exception. Listing methods repeatedly GET JSON with markers. Object helpers stream app iterators, iterate text lines with optional gzip decompression, and upload chunked when content length is absent. `SimpleClient` builds urllib requests, optionally fetches full listings by marker, logs transfer timing, and retries non-client failures.

State and persistence: client objects store app, user agent, retry settings, replication-network preference, ring references, auth URL/token, and retry attempt counters. Persistent effects are Swift requests made through the proxy app or external URL.

Dependencies and integration: integrates with Swift WSGI loading, `swob.Request`, gatekeeper policy, request helper headers, Swift HTTP status helpers, eventlet concurrency, urllib, JSON, and zlib. Used by internal daemons and tools that need proxy semantics without an external client dependency.

Risks: gatekeeper must stay absent so internal `X-Backend-*` headers survive; response iterators returned by `get_object` must be consumed/closed by callers; retries can replay non-idempotent operations if misused; chunked upload depends on downstream support; `get_auth` exits for non-v1 auth; `CompressingFileReader.seek` only supports rewind. Tests should cover retry and drain behavior, acceptable status classes, gatekeeper rejection, metadata prefix mapping, listing pagination, gzip line iteration, chunked upload headers, and simple-client retry classification.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/internal_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/linkat.py -->
# sources/object-store/openstack-swift/swift/common/linkat.py

Purpose: exposes Linux `linkat(2)` hard-link functionality to Swift code through a small ctypes wrapper.

Important APIs/types/functions: the internal `Linkat` class defines `AT_FDCWD`, `AT_SYMLINK_FOLLOW`, `available`, and `__call__`; the module exports a singleton `linkat` and deletes the class name from the module namespace.

Control flow: construction loads libc via `find_library('c')`, looks up `linkat`, configures ctypes argument and return types, and attaches an error checker that raises `IOError` with errno text when libc returns -1. Calling validates directory fds are integers, encodes string paths as UTF-8, checks availability, and invokes libc.

State and persistence: stores the resolved libc function pointer. The syscall creates a durable hard link when successful; the wrapper itself has no persistent state.

Dependencies and integration: depends on `ctypes`, `ctypes.util.find_library`, and `os.strerror`. Used where Swift needs atomic/relative hard-link operations not provided portably by Python.

Risks: only available on platforms with libc `linkat`; path encoding is fixed to UTF-8; errno capture depends on ctypes `use_errno`; callers must understand hard-link semantics, permissions, and cross-filesystem limitations. Tests should cover unavailable fallback, fd type validation, string/bytes paths, successful links, and errno propagation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/linkat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/manager.py -->
# sources/object-store/openstack-swift/swift/common/manager.py

Purpose: implements the `swift-init` style process manager for starting, stopping, reloading, status-checking, and running Swift service daemons from configuration files and pid files.

Important APIs/types/functions: constants define known servers, aliases, graceful/seamless shutdown support, resource limits, and filesystem roots. `setup_env` raises process limits. `command` exposes `Manager` methods as CLI commands. `watch_server_pids`, `safe_kill`, `kill_group`, and `get_child_pids` manage process signaling. `Manager` expands aliases/globs and dispatches commands. `Server` maps service names to binaries, config files, pid files, running pids, subprocess spawning, waiting, and signaling. `main` parses CLI options and executes commands.

Control flow: CLI arguments resolve to server names plus a command. `Manager` expands aliases such as `all`, `main`, and `rest`, verifies binaries, builds `Server` objects, and calls decorated command methods. `start` sets resource limits, launches each server's config files, optionally waits for startup output, or interacts in no-daemon mode. `stop` signals pid-file processes, polls until they disappear, and optionally sends SIGKILL to process groups after timeout. `reload`, `reload_seamless`, `shutdown`, `once`, and `kill` compose start/stop variants. `Server.conf_files` searches Swift config trees, including special object-expirer and standalone cases; `pid_files` maps run-dir state back to config choices.

State and persistence: persistent state is pid files under the run directory and daemon processes. The manager also reads Swift configuration files and `/proc` command lines to avoid killing reused PIDs.

Dependencies and integration: uses Swift utility `search_tree`, `write_file`, `remove_file`, and `readconf`; Swift `InvalidPidFileException`; system `resource`, `signal`, `subprocess`, `/proc`, and executable lookup. It is the operational control plane for installed Swift services.

Risks: stale or incorrect pid files can target wrong processes, mitigated by command-line checks only for noop checks; process-group SIGKILL can affect all children; config search rules have legacy object-expirer behavior; strict/non-strict exit behavior changes automation semantics; writing pid files immediately after spawning assumes daemon startup succeeds. Tests should cover alias/glob expansion, config and pid mapping, stale pid removal, signal selection, start-once restrictions, object-expirer config preference, command visibility, and CLI command/server argument swapping.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/manager.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/memcached.py -->
# sources/object-store/openstack-swift/swift/common/memcached.py

Purpose: implements Swift's eventlet-compatible, consistent-hash memcache client with per-server connection pools, JSON serialization, TLS support, retry/failover, and server error suppression.

Important APIs/types/functions: `md5hash`, `sanitize_timeout`, and `set_msg` support protocol encoding. `MemcacheConnPool` owns socket/file creation for one server. `MemcacheCommand` stores method, original key, memcache command bytes, hash key, and logging prefix. `MemcacheRing` exposes `set`, `get`, `incr`, `decr`, `delete`, `set_multi`, and `get_multi`. `load_memcache` merges proxy/filter config with optional `memcache.conf` and returns a configured ring.

Control flow: `MemcacheRing.__init__` builds weighted hash points for each server, per-server pools, error tracking maps, timeout settings, and sample-rate logging. `_get_conns` picks servers from the ring after the key hash, skips currently error-limited servers, acquires a pooled connection under pool timeout, and yields up to the configured try count. Operations send ASCII memcached protocol commands under IO timeout, parse response lines, return connections on success, and route exceptions through `_exception_occurred`, which logs, closes sockets, returns a placeholder to the pool, and may error-limit the server. `incr`/`decr` add missing keys and retry the increment to handle concurrent creation. Multi operations force all keys to the server selected by `server_key`.

State and persistence: in-memory state includes the consistent hash ring, connection pools, per-server recent error timestamps, error-limited deadlines, and logger config. Memcached itself stores transient cache entries; JSON is the active serialization flag, while pickled entries are treated as misses.

Dependencies and integration: depends on Swift concurrency sockets/SSL/pools/timeouts, config parsing, Swift utils for MD5, socket parsing, human-readable sizes, and timing stats, plus Swift memcache exception classes. Used by proxy middleware and services for auth, listings, rate limits, shard state, and other cache-backed coordination.

Risks: memcache protocol parsing must handle partial/empty reads; error-limiting can reduce cache availability if thresholds are too low; `set_multi` assumes values are bytes when `serialize=False`; item-size warnings are advisory only; consistent hash changes still remap keys when server list changes; TLS config errors surface at connection time. Tests should cover hashing stability, timeout sanitization above 30 days, JSON round trips, pickle flag miss behavior, incr add races, server failover/error limiting, connection pool timeout handling, TLS config loading, and multi-key ordering.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/memcached.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/__init__.py -->
# sources/object-store/openstack-swift/swift/common/middleware/__init__.py

Purpose: provides shared helpers for Swift middleware modules, currently app attribute forwarding and response-location rewriting support.

Important APIs/types/functions: `app_property(name)` creates a property that forwards access to the wrapped WSGI app. `RewriteContext` extends `WSGIContext` and rewrites `Location` and `Content-Location` response headers from an internal rewritten path back to the originally requested path using a subclass-provided `base_re`.

Control flow: `RewriteContext.__init__` stores requested and rewritten values and compiles a regex from `base_re`. `handle_request` calls the downstream app, scans captured response headers, substitutes matching location values, then calls `start_response` with modified headers and returns the original response iterable.

State and persistence: per-request context stores requested path and compiled rewrite regex. No persistence.

Dependencies and integration: depends on `re` and Swift `WSGIContext`. Used by middleware that internally rewrites request paths but must preserve externally visible redirects or content locations.

Risks: subclasses must provide a correct `base_re`; only `Location` and `Content-Location` headers are rewritten; regex substitution must avoid accidental changes outside the intended URL component; captured response iterators still need normal WSGI close handling. Tests should cover app property forwarding, both rewritten headers, no-match behavior, and subclass regex correctness.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/account_quotas.py -->
# sources/object-store/openstack-swift/swift/common/middleware/account_quotas.py

Purpose: WSGI middleware that lets reseller requests set account-wide and per-storage-policy byte/object quotas, exposes those quotas as account headers, and blocks non-reseller object PUTs that would exceed them.

Important APIs/types/functions: `AccountQuotaMiddleware.quota_exceeded` returns or defers a 413 response; `validate_and_translate_quotas` validates user-facing quota headers and maps them to account sysmeta; `handle_account` manages quota header translation and response exposure; `__call__` parses request paths and enforces quotas; `filter_factory` registers Swift info and returns the paste filter.

Control flow: account PUT/POST requests first translate legacy `X-Account-Meta-Quota-Bytes`, validate global and per-policy quota bytes/count headers, require `reseller_request` for any quota mutation, and write sysmeta headers. Account responses copy sysmeta quotas back to user-visible headers. For object PUTs, reseller requests bypass enforcement. Other requests fetch account info, check global bytes and count quotas using current aggregate stats plus incoming content length/default one object, fetch container info for storage policy, then check per-policy bytes and count. When a quota is exceeded and authorization is delayed, `quota_exceeded` wraps `swift.authorize` so normal auth still runs before returning 413.

State and persistence: quotas persist as account sysmeta, while enforcement reads eventually consistent account and storage-policy counters. No local durable state.

Dependencies and integration: uses Swift `swob` HTTP exceptions and `wsgify`, storage `POLICIES`, registry `register_swift_info`, and proxy controller `get_account_info`/`get_container_info`. Intended placement is after auth middleware and before proxy-server.

Risks: eventual consistency can allow temporary over-quota writes; uploads without content length only compare current usage plus zero bytes; per-policy quotas are independent of global quota; malformed stored quotas are treated as disabled; delayed authorization wrapping must preserve auth semantics. Tests should cover reseller/non-reseller quota updates, legacy header translation, quota removal dominance, response exposure, object PUT global and per-policy byte/count rejection, missing account/container info pass-through, and delayed-authorize behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/account_quotas.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/acl.py -->
# sources/object-store/openstack-swift/swift/common/middleware/acl.py

Purpose: formats, parses, normalizes, and evaluates Swift ACL header values, supporting legacy comma-delimited ACLs and JSON version-2 account ACLs.

Important APIs/types/functions: `clean_acl` validates and canonicalizes v1 ACL strings; `format_acl_v1`, `format_acl_v2`, and `format_acl` produce header values; `parse_acl_v1`, `parse_acl_v2`, and `parse_acl` decode them; `referrer_allowed` evaluates referer host rules; `acls_from_account_info` extracts account ACLs from sysmeta.

Control flow: `clean_acl` splits on commas, trims whitespace, preserves plain groups, normalizes referrer aliases to `.r:`, rejects referrers on write ACLs, handles negated hosts and wildcard/domain shorthand, and rejects unknown designators or empty hosts. V1 parse splits referrers from groups and URL-decodes groups. V2 format emits compact ASCII JSON with sorted keys, while V2 parse returns a dict, `{}` for empty string, or `None` for absent/invalid/non-dict input. `referrer_allowed` walks ACL entries in order so later allow/deny matches update the decision. `acls_from_account_info` reads `core-access-control` sysmeta and returns only populated admin/read-write/read-only lists.

State and persistence: stateless parsing logic. ACL persistence occurs elsewhere as headers/sysmeta.

Dependencies and integration: uses JSON and `urllib.parse` for unquoting and host parsing. Used by auth and proxy middleware to interpret account/container ACL headers and referer grants.

Risks: comma and colon parsing is intentionally simple and tied to v1 syntax; referer-based access depends on client-provided headers and should not be treated like authentication; ordering of allow/deny rules is significant; `parse_acl_v2` silently returns `None` for invalid data. Tests should cover messy normalization, invalid designators, write ACL referrer rejection, wildcard/domain/negative referrers, v2 JSON round trips, invalid v2 data, and account ACL extraction.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/acl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/backend_ratelimit.py -->
# sources/object-store/openstack-swift/swift/common/middleware/backend_ratelimit.py

Purpose: backend WSGI middleware that rate-limits storage-node requests per device and per `(device, method)` to protect backend disks from request bursts.

Important APIs/types/functions: constants define rate-limited methods, config section/file names, reload interval, default rates, and rate buffer. `BackendRateLimitMiddleware` owns config state, rate limiter maps, config reloads, limiter creation, allow checks, and WSGI request handling. `filter_factory` merges paste config and returns the filter.

Control flow: initialization reads startup filter config, identifies the optional external `backend-ratelimit.conf`, applies defaults and method-specific rates, and attempts to load file overrides. `_apply_config` builds a `{None: aggregate, METHOD: per-method}` rate map and refreshes existing limiter rates when changed. `_maybe_reload_config` periodically reloads config and always advances the attempt timestamp to avoid retry storms. On each request, `__call__` reloads if due, wraps the env as a `Request`, and if any limit is configured and the method is limited, validates the backend path as device/partition. Requests without valid backend device paths pass through. Valid backend requests must pass both aggregate device and per-method limiters; failures increment `backend.ratelimit` and return `HTTPTooManyBackendRequests` (529).

State and persistence: in-memory config, limiter token state, last reload time, and expected-file flag. Optional persistent config lives in `backend-ratelimit.conf`.

Dependencies and integration: depends on Swift request path validation, `swob` request/HTTP exceptions, logging, `non_negative_float`, `EventletRateLimiter`, and `readconf`. It runs in backend server pipelines for account, container, and object services.

Risks: limiter keys retain entries for removed devices; aggregate and method limits both consume limiter state, so checks must remain ordered intentionally; invalid config leaves prior config active; reload interval zero disables reload; all methods not listed bypass rate limiting. Tests should cover default disabled behavior, external config load/reload/failure, aggregate and method-specific throttling, path parse pass-through, limiter refresh on config change, invalid numeric config, and 529 metric increments.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/middleware/backend_ratelimit.py -->
