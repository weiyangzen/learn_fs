# Research: subset-b-008226

Grouped research for the requested OpenStack Swift object-updater, object-auditor watcher, and proxy-controller files. Each section preserves its source path for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/updater.py -->
# sources/object-store/openstack-swift/swift/obj/updater.py

## Purpose
This module implements Swift's object-updater daemon, which drains async-pending update pickles from object devices and sends the corresponding object `PUT`/`DELETE` updates to the correct container-server replicas. It is the repair path for container listings when object-server writes could not synchronously update container databases. It also records recon data about update lag and failed account/container pairs.

## Important APIs, Types, and Functions
`RateLimiterBucket` extends `EventletRateLimiter` with a deferral deque and ordering by readiness time. `BucketizedUpdateSkippingLimiter` wraps an async-pending iterator and applies per-account/container rate limits, deferring or skipping updates while maintaining `SweepStats.deferrals`, `skips`, and `drains`. `OldestAsyncPendingTracker` records the oldest failed async-pending timestamp per `(account, container)` pair and reports oldest entries, age, and approximate memory use for recon. `SweepStats` is the mutable per-sweep counter bucket.

`split_update_path()` resolves the account/container target, honoring `update['container_path']` for sharded-container redirects. `ObjectUpdater` is the daemon entry point. Its major methods are `run_forever()`, `run_once()`, `_process_devices()`, `object_sweep()`, `_iter_async_pendings()`, `process_object_update()`, and `object_update()`. `main()` parses daemon options and calls `run_daemon(ObjectUpdater, ...)`.

## Control Flow
`run_forever()` sleeps a randomized initial interval, then repeatedly calls `run_once()`. `run_once()` lists devices under `devices`, calls `_process_devices()`, logs elapsed time, and aggregates recon. `_process_devices()` refreshes the container ring, validates each drive with `check_drive()`, forks up to `updater_workers` child processes, and each child runs `_process_device_in_child()`. In the child, signal handling is reset, systemd notify state is removed, eventlet monkey patching is applied, stats and oldest trackers are reset, then `object_sweep()` walks the device.

`_iter_async_pendings()` scans directories named from `ASYNCDIR_BASE`, validates storage policy suffixes, randomizes prefix directories, and sorts async-pending filenames newest-first. For multiple files for the same object hash it yields only the newest update and unlinks older pending files as obsolete. Broken or unreadable pickles are quarantined by `_load_update()`. `object_sweep()` wraps this iterator in a global `RateLimitedIterator` and the bucketized per-container limiter, then sends each update through a `ContextPool` with `concurrency` greenthreads.

`process_object_update()` builds backend headers, asks the container ring for nodes, and spawns `object_update()` to each replica that has not already succeeded according to the update pickle's `successes` list. Full success unlinks the async-pending file and tries to remove its directory. Partial success persists new `successes` into the pickle. A redirect from a container server rewrites `container_path` and retries once immediately; repeated redirect history resets the update back to the root container to avoid loops. `object_update()` performs the HTTP request to the container server, handles 301 redirect metadata, logs non-successes, and emits timing metrics by status.

## State and Persistence Behavior
The primary persisted state is the async-pending pickle tree on object devices. Successful updates remove pickle files; partial replica success rewrites the pickle under the device's policy temp dir using `write_pickle()`. Quarantined corrupt files are moved into `<device>/quarantined/objects/`. Stale async-pending files for the same object hash are unlinked. Recon state is persisted in `RECON_OBJECT_FILE` under `recon_cache_path`; per-device child dumps are later aggregated into `object_updater_stats`, `object_updater_sweep`, and `object_updater_last`. In-memory state includes rate limiter buckets, sweep counters, oldest-failure trackers, the lazily-loaded container ring, and per-update redirect history.

## Dependencies and Integration Points
The updater integrates with Swift rings, storage policies, diskfile async directories, buffered HTTP, recon cache utilities, eventlet concurrency, and container-server redirect behavior for sharding. It depends on pickle helpers for safe async update serialization, `HeaderKeyDict` for case-insensitive backend headers, and Swift's daemon framework for CLI and lifecycle. Container servers must understand backend headers such as `X-Backend-Storage-Policy-Index`, `X-Backend-Accept-Redirect`, and `X-Backend-Accept-Quoted-Location`.

## Risks and Edge Cases
The module is sensitive to filesystem races: async files may disappear while scanning, directories may be removed concurrently, and corrupt pickles must not crash the sweep. Rate limiting deliberately skips deferred updates when queues fill or the sweep interval expires; correctness relies on newer async-pending files superseding older state. Forked workers share no live Python state, so recon aggregation must tolerate missing or stale per-device data. Redirect handling must avoid shard redirect loops while still converging on the correct shard. `object_update()` returns `HTTP_INTERNAL_SERVER_ERROR` as the success flag on exception, which is falsey only by status semantics not boolean identity, so callers rely on `event_success is True`.

## Test Signals
High-value tests include stale async-pending unlink order, corrupt pickle quarantine, partial success pickle rewrite, redirect retry and loop reset, per-container limiter accounting invariants, recon aggregation across devices, `check_drive()` skip behavior, and timeout/error handling in `object_update()`. Probe-style tests should verify container sharding redirects and eventual listing repair after object-server async update failures.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/updater.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/watchers/__init__.py -->
# sources/object-store/openstack-swift/swift/obj/watchers/__init__.py

## Purpose
This is an empty package initializer for `swift.obj.watchers`. Its presence makes the watcher directory importable as a Python package and allows watcher modules such as `dark_data.py` to be discovered or imported through Swift's watcher/plugin loading path.

## Important APIs, Types, and Functions
The file defines no symbols, classes, functions, imports, or module-level state.

## Control Flow
There is no runtime control flow in this file. Importing it has no side effects beyond normal package initialization.

## State and Persistence Behavior
No state is created or persisted.

## Dependencies and Integration Points
The integration point is structural: object auditor watcher code can live under this package and be loaded by plugin machinery or direct import paths.

## Risks and Edge Cases
The main risk is accidental addition of import-time side effects that would affect object-auditor startup or third-party watcher discovery. Keeping the file empty is intentional.

## Test Signals
Tests only need import/package discovery coverage when watcher loading is exercised.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/watchers/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/watchers/dark_data.py -->
# sources/object-store/openstack-swift/swift/obj/watchers/dark_data.py

## Purpose
This module implements an optional object-auditor watcher that detects "dark data": object data files present on object nodes but absent from container listings. The watcher is disabled by default and must be enabled in object-server configuration. It can log, delete, or quarantine dark objects, but its own comments warn about significant performance impact and recommend starting with logging.

## Important APIs, Types, and Functions
`ContainerError` marks container lookup uncertainty. `DarkDataWatcher` is the plugin class with the auditor watcher lifecycle methods `start()`, `see_object()`, and `end()`, plus `policy_based_object_handling()`. `get_info_1(container_ring, obj_path)` is the lookup helper that queries container servers, follows shard namespaces recursively, and returns an object row, `None`, or raises `ContainerError`.

## Control Flow
Construction loads the container ring from `/etc/swift`, normalizes `action` to `log`, `delete`, or `quarantine`, and reads `grace_age` with a default of one week. `start()` records whether the auditor pass is a zero-byte-file pass (`ZBF`) and resets counters. `see_object()` ignores ZBF passes, skips recently written objects still within the grace age, then asks `get_info_1()` whether the object name appears in the appropriate container or shard. Unknown container-server state increments `tot_unknown`. Missing rows increment `tot_dark` and invoke the configured action. Found rows increment `tot_okay`. `end()` logs totals for non-ZBF passes.

`get_info_1()` splits the object path into account, container, and object. Its nested `check_container()` asks all container nodes for either automatic records or, on repeated visits, object records to break shard loops. It uses `direct_get_container()` with `prefix`, `limit=1`, `includes`, `states=listing`, and `X-Backend-Record-Type`. Shard responses are converted to `Namespace` objects and recursively queried. Only if every contacted container server agrees that the object is absent does it return `None`; any client/timeout errors raise `ContainerError`.

## State and Persistence Behavior
The watcher maintains per-pass counters in memory. The configured `delete` action removes the entire object data directory with `shutil.rmtree()`. The `quarantine` action raises `QuarantineRequest` so auditor infrastructure handles quarantine. The `log` action is non-mutating. No cache or database state is written by this module.

## Dependencies and Integration Points
It integrates with object auditor watcher hooks, direct container-client calls, the container ring, Swift `Namespace` shard records, object metadata fields `name` and `X-Timestamp`, and auditor quarantine semantics. It assumes object nodes have access to container ring data.

## Risks and Edge Cases
The performance risk is high because each eligible object may fan out to all container replicas and possibly shard containers. Container-server errors intentionally suppress dark-data decisions, so outages create false negatives. Sharded containers can produce misplaced rows or loops; the visited set and forced object-record lookup mitigate loops but not all stale namespace cases. The hardcoded `/etc/swift` ring path ignores a configured `swift_dir`. Deleting dark data is destructive, particularly if container listings are stale or sharding is in transition.

## Test Signals
Useful tests cover grace-age skipping, ZBF no-op behavior, action handling, unknown action fallback, all-replica absence, partial container failure returning unknown, shard recursion, loop prevention with repeated containers, and destructive action isolation. Probe tests should exercise sharded containers before enabling delete behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/watchers/dark_data.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/__init__.py -->
# sources/object-store/openstack-swift/swift/proxy/__init__.py

## Purpose
This is an empty package initializer for `swift.proxy`. It marks the proxy package for Python import machinery.

## Important APIs, Types, and Functions
The file defines no APIs, symbols, imports, or module-level constants.

## Control Flow
There is no control flow beyond package import initialization.

## State and Persistence Behavior
No state is created or persisted.

## Dependencies and Integration Points
It enables imports of proxy modules such as `swift.proxy.server` and `swift.proxy.controllers`.

## Risks and Edge Cases
Adding side effects here would affect every proxy import and could change startup behavior. Its empty state is low risk and intentional.

## Test Signals
Package import tests indirectly cover this file.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/__init__.py -->
# sources/object-store/openstack-swift/swift/proxy/controllers/__init__.py

## Purpose
This package initializer provides the public controller import surface for Swift proxy controllers. It imports the base `Controller`, concrete `InfoController`, `ObjectControllerRouter`, `AccountController`, and `ContainerController`, and publishes them through `__all__`.

## Important APIs, Types, and Functions
The file exports `AccountController`, `ContainerController`, `Controller`, `InfoController`, and `ObjectControllerRouter`. It defines no functions or classes itself.

## Control Flow
Importing this module imports each listed controller module. That makes controller classes available from `swift.proxy.controllers` but also means import-time errors in any concrete controller affect package import.

## State and Persistence Behavior
The only state is the module-level `__all__` list. No persistence or runtime mutation is performed.

## Dependencies and Integration Points
It ties together controller implementations used by the proxy server routing layer. It depends on `base.py`, `info.py`, `obj.py`, `account.py`, and `container.py`.

## Risks and Edge Cases
Because it imports `ObjectControllerRouter`, package import may load object-controller dependencies even when a caller only needs account or container controllers. Keep exports synchronized with real controller class names.

## Test Signals
Import-surface tests should verify `from swift.proxy.controllers import ...` works for every `__all__` symbol.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/account.py -->
# sources/object-store/openstack-swift/swift/proxy/controllers/account.py

## Purpose
This module implements the proxy controller for account-level requests. It validates account operations, fans requests out to account-server replicas, manages account info cache entries, handles account autocreate behavior, and controls which owner-only headers/ACLs are exposed.

## Important APIs, Types, and Functions
`AccountController` extends `Controller` with `server_type = 'Account'`. Its public request handlers are `GETorHEAD()`, `PUT()`, `POST()`, and `DELETE()`. `add_acls_from_sys_metadata()` converts internally stored account ACL sysmeta into external `x-account-access-control` when the requester is a Swift owner.

## Control Flow
Construction unquotes the account name and, if account management is disabled, removes `PUT` and `DELETE` from the controller's allowed methods. `GETorHEAD()` validates the account-name length, builds a `NodeIter`, forces JSON listing format, and delegates backend reads to `GETorHEAD_base()`. A backend 404 with deleted status becomes 410. If account autocreate is enabled, missing accounts can return a fake account listing marked by `X-Backend-Fake-Account-Listing`. The response is cached via `set_info_cache()`, owner ACLs are translated for owners, and owner-only headers are stripped for non-owners.

`PUT()` and `POST()` validate metadata and name length, generate backend headers, clear the account info cache, and call `make_requests()` against the account ring. `POST()` can autocreate a missing account and retry. `DELETE()` rejects any query string as a safety guard, checks management permission, clears cache, and fans out `DELETE`.

## State and Persistence Behavior
The controller does not persist directly; account servers persist account DB changes. Proxy-side state changes are cache invalidation (`clear_info_cache`) before mutating methods and cache population after account reads. It also mutates response headers to hide or expose owner-only metadata.

## Dependencies and Integration Points
It relies on the base controller fan-out/quorum machinery, account ring, listing format middleware, ACL parsing/formatting helpers, metadata validation, and Swift app flags including `allow_account_management`, `account_autocreate`, `swift_owner_headers`, and `recheck_account_existence`.

## Risks and Edge Cases
Fake account listings are intentionally not proof of actual account DB existence; downstream container PUT logic must respect `X-Backend-Fake-Account-Listing`. Owner-only header stripping is security-sensitive. Management-disabled deployments must not expose PUT/DELETE. Query-string rejection on DELETE protects middleware conventions. Account name length limits may be doubled for auto-create accounts through inherited base logic.

## Test Signals
Tests should cover GET/HEAD cache population, deleted account 410 mapping, fake autocreate listings, metadata validation failures, ACL sysmeta translation, owner header stripping, management-disabled method rejection, POST autocreate retry, DELETE query-string rejection, and quorum response selection from account replicas.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/account.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/base.py -->
# sources/object-store/openstack-swift/swift/proxy/controllers/base.py

## Purpose
This module is the shared foundation for Swift proxy controllers. It converts backend headers into cacheable info dictionaries, manages account/container/object info caches, provides CORS and authorization-delay decorators, implements backend GET/HEAD source selection and failover, yields ring nodes with handoff/error-limit handling, and supplies controller fan-out/quorum response logic.

## Important APIs, Types, and Functions
Header/info helpers include `update_headers()`, `_prep_headers_to_info()`, `headers_to_account_info()`, `headers_to_container_info()`, `headers_from_container_info()`, and `headers_to_object_info()`. Cache helpers include `get_account_info()`, `get_container_info()`, `get_object_info()`, `get_info()`, `get_cache_key()`, `set_info_cache()`, `set_object_info_cache()`, `clear_info_cache()`, `_get_info_from_infocache()`, `_get_info_from_memcache()`, `_get_info_from_caches()`, and `record_cache_op_metrics()`. Shard namespace cache helpers include `namespace_bounds_to_list()`, `namespace_list_to_bounds()`, `get_namespaces_from_cache()`, and `set_namespaces_in_cache()`.

Request/response helpers include `delay_denial`, `cors_validation`, `_prepare_pre_auth_info_request()`, `close_swift_conn()`, `bytes_to_skip()`, `is_good_source()`, and `is_useful_response()`. Streaming and source-selection types include `ByteCountEnforcer`, `GetterSource`, `GetterBase`, and `GetOrHeadHandler`. `NodeIter` yields primary and handoff nodes while respecting error limiting. `Controller` is the base class used by account, container, object, and info controllers.

## Control Flow
Info lookup first checks `env['swift.infocache']`, then memcache unless skipped, then makes a pre-authorized HEAD subrequest when allowed. Account and container info cache entries are normalized into dictionaries and type-coerced before returning; object info is only cached per request. Container info lookup also verifies account existence unless the account is auto-createable and may include bytes from a versions container.

`GetOrHeadHandler.get_working_response()` repeatedly finds a suitable backend source with `_find_source()`. `_make_node_request()` connects to nodes, records successful sources, filters stale object copies behind tombstones, suppresses some handoff 404/5xx responses, and tracks latest 404 timestamps. For object GETs without `x-newest`, read failures can fast-forward the Range header and replace the source to resume from another node with the same ETag. Multipart/range responses are converted into response body iterators and backend sockets are forcibly closed on completion.

`Controller.make_requests()` runs backend requests concurrently using `GreenAsyncPile`, stops when quorum is reached, waits briefly for post-quorum responses, fills missing responses with 503 stubs, and returns `best_response()`. `best_response()` chooses the strongest quorum class among 2xx, 3xx, and 4xx groups, applies optional status overrides, and falls back to 503 with logging. `OPTIONS()` implements CORS preflight support. Listing helper methods fetch and parse JSON container listings and convert shard records to `Namespace` objects.

## State and Persistence Behavior
This file manages request-scoped `swift.infocache` and optional memcache entries for account/container info and shard namespace bounds. It does not directly persist storage data; it influences backend persistence through generated request headers and fan-out methods. It mutates backend Range headers during GET resume, response headers during cache/header conversion, and node timing/error state through `app` callbacks. Cache TTLs are controlled by backend recheck headers or defaults.

## Dependencies and Integration Points
It is deeply integrated with Swift's WSGI request helpers, memcache abstraction, ring/node selection, buffered HTTP client, storage policies, CORS config, request metadata helpers, namespace/sharding utilities, and swob response classes. Controllers depend on app-provided settings such as timeouts, concurrency, request node counts, CORS allowlists, cache skip probabilities, error limiting, backend user agent, and policy options.

## Risks and Edge Cases
Cache correctness is central: stale account/container info can change authorization, object versioning byte counts, sharding decisions, and write preconditions. Cache skip/error states must be accurately recorded for observability. GET resume logic must not switch between different object versions; the saved ETag guard is critical. Handoff 404 handling avoids false negatives during rebalance but can delay authoritative errors. `cors_validation()` assumes `cors_info['allow_origin']` exists when an Origin is present; malformed container info would be risky. `set_namespaces_in_cache()` rejects `shard-updating` keys because updating caches use a different cooperative path.

## Test Signals
Targeted tests should cover header-to-info normalization, metadata/sysmeta stripping, cache hit/miss/skip/error behavior, negative cache TTL scaling, object info request-only caching, namespace cache round trips, CORS simple and preflight responses, `bytes_to_skip()`, `ByteCountEnforcer` short-read errors, GET source failover and Range rewriting, tombstone/newest selection, NodeIter handoff logging, quorum grouping/overrides, and owner-only preauth info request behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/base.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/container.py -->
# sources/object-store/openstack-swift/swift/proxy/controllers/container.py

## Purpose
This module implements the proxy controller for container-level requests. It handles container metadata and ACL operations, storage-policy selection, account existence checks, container info cache invalidation, sharded-container listing assembly, shard namespace caching, and internal bulk `UPDATE` forwarding.

## Important APIs, Types, and Functions
`ContainerController` extends `Controller` with `server_type = 'Container'` and passes through container ACL, sync, and versions headers. Key helpers are `_convert_policy_to_index()`, `clean_acls()`, `_clear_container_info_cache()`, `_GETorHEAD_from_backend()`, `_filter_complete_listing()`, `_get_listing_namespaces_from_cache()`, `_set_listing_namespaces_in_cache()`, `_get_listing_namespaces_from_backend()`, `_record_shard_listing_cache_metrics()`, `_GET_auto()`, `_get_or_head_pre_check()`, `_get_or_head_post_check()`, `_get_from_shards()`, and `_backend_requests()`. Public methods are `GET()`, `HEAD()`, `PUT()`, `POST()`, `DELETE()`, plus private `UPDATE()`.

## Control Flow
GET validates listing parameters, checks account existence and authorization preconditions, forces JSON format, then either goes directly to container servers for explicit `object`/`shard` record requests or calls `_GET_auto()` for client-style listings. `_GET_auto()` attempts to use cached shard namespaces when the container is known sharded and cache is enabled; otherwise it asks the backend for `auto` records with namespace format. Successful complete namespace responses for sharded containers are compacted into `NamespaceBoundList` and cached. When namespaces are available, `_get_from_shards()` recursively fetches object listings from shard containers, prevents loops through request history, preserves root storage policy, applies marker/end-marker/reverse/prefix constraints, stops at limit, and may update object-count/bytes headers for unconstrained complete listings.

HEAD performs account precheck, backend HEAD, and postcheck. PUT cleans ACLs and metadata, converts `X-Storage-Policy` to a backend policy index, hides owner-only headers from non-owners, maps reseller `X-Container-Sharding` to sysmeta, checks container-name length, autocreates missing accounts when configured, enforces per-account container limits, builds account update headers, sends container PUTs, and clears caches. POST updates metadata after account existence validation. DELETE sends container DELETEs and maps 202 Accepted to 404 when no server had the container. Private UPDATE forwards request bodies to container servers for internal merge-style operations using a caller-supplied storage policy index.

## State and Persistence Behavior
Persistent effects happen on account/container servers, not locally. The controller mutates request headers for backend policy, sharding, record type, and account update information. It clears container metadata and listing namespace cache entries on writes/deletes/posts. It can populate container info cache after successful reads and namespace caches for complete sharded listings. Shard listing history is request-scoped in `swift.shard_listing_history`.

## Dependencies and Integration Points
It integrates with base controller fan-out, account/container rings, storage policy registry, metadata and listing parameter validators, ACL cleaners from middleware, namespace cache helpers, container sharder semantics, listing format middleware, app settings for shard cache recheck/skip, max containers per account, account autocreate, and owner/reseller request flags.

## Risks and Edge Cases
Shard listings are the most complex area: stale namespace caches can omit or duplicate objects, policy mismatches abort listings, loops must be forced to object listings, and misplaced objects around namespace bounds require careful marker/end-marker handling. Container limit enforcement must allow existing containers while blocking new ones. `PUT` must reject deprecated or unknown storage policies. Cache invalidation currently does not purge updating-shard caches, noted by a TODO. Private UPDATE trusts backend headers and must remain gated by private-method authorization outside this file.

## Test Signals
Tests should cover policy name conversion and deprecated policies, ACL cleaning, cache clearing on mutations, auto vs explicit record-type GET paths, namespace cache hit/miss/force-skip/disabled metrics, shard listing recursion and loop prevention, policy mismatch 503, marker/end-marker/reverse/prefix behavior, object count inference, account autocreate on PUT, max-container limit enforcement, owner/reseller header handling, DELETE 202-to-404 mapping, and private UPDATE body fan-out.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/container.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/info.py -->
# sources/object-store/openstack-swift/swift/proxy/controllers/info.py

## Purpose
This module implements the proxy `/info` controller, which returns public Swift capability/configuration data and optional admin-only sections when a valid HMAC-signed request is supplied.

## Important APIs, Types, and Functions
`InfoController` extends `Controller` with `server_type = 'Info'`. It exposes public `GET()`, `HEAD()`, and `OPTIONS()` methods decorated with `delay_denial`. `GETorHEAD()` performs the actual authorization and response generation. Constructor parameters include `expose_info`, `disallowed_sections`, and `admin_key`.

## Control Flow
GET and HEAD delegate to `GETorHEAD()`. OPTIONS returns an immediate 200 with `Allow: HEAD, GET, OPTIONS`. `GETorHEAD()` rejects all requests with 403 when info exposure is disabled. If either `swiftinfo_sig` or `swiftinfo_expires` is present, the request becomes an admin request: an admin key must exist, expiry must parse as an integer and be in the future, and the signature must match a constant-time comparison against HMACs for allowed methods (`GET` for GET, `HEAD` or `GET` for HEAD). Valid admin requests call `get_swift_info(admin=True, ...)`; normal requests call it with `admin=False`. CORS response headers are echoed when an Origin is present.

## State and Persistence Behavior
The controller is stateless per request. It reads registry data from `get_swift_info()` and serializes it as ASCII JSON. No cache or persistent data is written.

## Dependencies and Integration Points
It depends on Swift's registry of capability info, HMAC helper, constant-time string comparison, and swob response classes. Its delay-denial decorators allow auth middleware to run after request context is prepared, matching other public controller methods.

## Risks and Edge Cases
Admin access depends entirely on secrecy of `admin_key`, expiry validation, and constant-time signature comparison. HEAD accepts signatures generated for either HEAD or GET, which is intentional compatibility behavior. If either signature or expiry is partially supplied, the request is treated as admin and may return 401/403 rather than public info. CORS is permissive for `/info`, echoing the Origin and exposing only `x-trans-id`.

## Test Signals
Tests should cover disabled exposure, public GET/HEAD, OPTIONS allow header, valid and expired admin signatures, missing admin key, invalid expiry, invalid signature, HEAD signed as GET, disallowed section filtering, and CORS headers.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/proxy/controllers/info.py -->
