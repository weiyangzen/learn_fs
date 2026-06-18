# Research: subset-b-006994

This grouped report covers the RGW operation, period propagation, request processing, S3 policy, public-access, placement/pool type, performance-counter, OPA, and pubsub files assigned to `subset-b-006994`. Each section preserves its source path for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_op.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_op.h

## Purpose
`rgw_op.h` is the central abstract operation surface for RADOS Gateway requests. It declares `RGWOp`, `RGWHandler`, data filters, metadata helpers, and most concrete operation base classes used by S3, Swift, admin, lifecycle, multipart, tagging, replication, object-lock, bucket policy, public-access, and metadata-search frontends. The file does not implement most behavior; instead it defines the contracts implemented by protocol-specific REST classes and the common execution path in `rgw_process.cc`.

## Important APIs, Types, And Functions
`RGWHandler` owns dialect-specific request initialization, permission setup, retargeting, authorization, and post-auth initialization. `RGWOp` owns request state, driver access, quota initialization, CORS state, return status, request verification hooks, execution hooks, response hooks, op masks, dmclock classification, and operation naming. Derived classes map API verbs/resources to common RGW behavior, including `RGWGetObj`, `RGWPutObj`, `RGWPostObj`, `RGWCopyObj`, multipart operations, bucket metadata operations, ACL/CORS/lifecycle operations, object-lock operations, and bucket public-access block operations.

Helper APIs include `rgw_rest_read_all_input()`, `rgw_rest_get_json_input()`, `retry_raced_bucket_write()`, `get_system_versioning_params()`, `rgw_get_request_metadata()`, `encode_delete_at_attr()`, `encode_obj_tags_attr()`, `encode_dlo_manifest_attr()`, `complete_etag()`, `parse_value_and_bound()`, `rgw_policy_from_attrset()`, and the generic `get_decrypt_filter()`.

## Control Flow
The intended flow is: handler creates an op, `process_request()` authenticates requester, `rgw_process_authenticated()` initializes permissions, optionally retargets, reads ACL/policy state, runs `init_processing()`, checks op masks and permissions, calls `verify_params()`, `pre_exec()`, `execute()`, then `complete()`/`send_response()`. `RGWOp::read_all_input()` and `get_json_input()` complete AWS v4 authentication after reading the body. `RGWGetObj_Filter` chains data transformations; `DataProcessorFilter` bridges get-object streaming into a SAL data processor.

## State And Persistence
Most persistent state is indirect through SAL objects and encoded attrs. The header defines attr serialization helpers for HTTP metadata, delete-at timestamps, object tags, DLO manifests, SLO entries, and SLO manifests. Operation objects keep transient request state such as ranges, encryption/decryption filters, multipart ids, ACLs, CORS configs, object-lock state, checksum state, and response tracking. `retry_raced_bucket_write()` exists because bucket info writes can fail with `-ECANCELED` if bucket metadata changed concurrently.

## Dependencies And Integration Points
This file ties together `req_state`, SAL driver/user/bucket/object abstractions, ACL, CORS, quota, lifecycle, tags, object-lock, bucket encryption, compression, logging, tracing, dmclock scheduling, and RGW-specific attributes. `rgw_process.cc` consumes the virtual hooks. Protocol frontends subclass these base operations to parse parameters and send protocol-specific responses.

## Risks And Test Signals
Risk concentrates in virtual-contract drift, missing `op_mask()` coverage, body-read/AWS4 ordering, attr size/name enforcement, metadata header blocklists, storage-class parsing, and races around bucket attr updates. Useful tests exercise each operation through REST protocol tests, multipart/copy/range/encryption paths, object-lock and public-access block cases, invalid metadata bounds, stale bucket-info retries, and dmclock client classification for data versus metadata operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_op.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_op_type.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_op_type.h

## Purpose
`rgw_op_type.h` defines the `RGWOpType` enum used to classify RGW operations independently of concrete C++ class names. It is consumed by request processing, logging, tracing, rate-limit bypasses, protocol handlers, and feature-specific logic such as health-check handling and public-access operations.

## Important APIs, Types, And Functions
The only exported type is `enum RGWOpType`. It starts with core object, bucket, metadata, ACL, CORS, encryption, request-payment, multipart, bulk, attr, health, lifecycle, object-lock, and ownership-control values. Later ranges cover IAM, RGW admin/sync/period operations, STS operations, pubsub topic/subscription/notification operations, bucket tagging/replication, public-access block APIs, and OIDC provider operations.

## Control Flow
Concrete `RGWOp::get_type()` overrides return values from this enum. `process_request()` stores the type in `req_state::op_type`; `rate_limit()` uses it to exempt health checks, and other RGW code can switch on it without RTTI. The enum is append-only in practice because many components may persist or report numeric operation ids.

## State And Persistence
The enum itself has no runtime state. Its persistence risk is compatibility: logs, metrics, traces, and external consumers may infer meaning from numeric values. Reordering existing values would break that assumption.

## Dependencies And Integration Points
`rgw_op.h` includes this enum through common operation headers. Request-processing, REST handler, admin, IAM, STS, sync, pubsub, and public-access implementations all integrate by returning a stable type.

## Risks And Test Signals
Risks include forgetting to assign new operations a specific enum, duplicate/ambiguous classification, and reordering values. Test signals include operation-specific request tests confirming `req_state::op_type`, logging/tracing classification, rate-limit bypass behavior for health checks, and compile coverage for all new `get_type()` overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_op_type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_opa.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_opa.cc

## Purpose
`rgw_opa.cc` implements optional Open Policy Agent authorization for RGW requests. When enabled in `rgw_process.cc`, it serializes request context into JSON, POSTs it to the configured OPA endpoint, and allows the operation only when OPA returns a JSON `result: true`.

## Important APIs, Types, And Functions
`rgw_opa_authorize(RGWOp*& op, req_state* s)` is the single exported function. It reads `rgw_opa_url`, `rgw_opa_token`, and `rgw_opa_verify_ssl` from config, uses `RGWHTTPTransceiver`, and serializes request method, URIs, query params, AWS4 URI, object name, subuser, user info, and bucket info using `JSONFormatter`.

## Control Flow
The function validates that an OPA URL exists, builds a POST with `X-Auth-Token`, JSON content type, and `Expect: 100-continue`, sends the body with `req.process(op, s->yield)`, parses the returned bufferlist as JSON, decodes boolean `result`, and returns `0` for allow or `-EPERM` for deny. Transport errors and malformed JSON propagate as negative errors.

## State And Persistence
No local persistent state is modified. It sends potentially sensitive request and identity metadata to an external policy service. Authorization outcome is transient and bound to the current request.

## Dependencies And Integration Points
The function depends on `rgw_http_client.h`, `req_state`, `RGWOp` logging, Ceph config, JSON formatting/parsing, and the RGW coroutine yield path. It is called after op mask verification and before native `verify_permission()` in `rgw_process_authenticated()`.

## Risks And Test Signals
Risks include missing `rgw_opa_url`, OPA outage becoming request failure, schema drift between RGW and OPA policy, unchecked absence/type mismatch of `result`, sensitive data exposure, and SSL verification misconfiguration. Test signals should cover allow/deny responses, malformed JSON, missing URL, HTTP errors, SSL verify toggles, token header presence, and requests with/without user, bucket, object, and auth identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_opa.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_opa.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_opa.h

## Purpose
`rgw_opa.h` declares the OPA authorization hook used by RGW request processing.

## Important APIs, Types, And Functions
It includes `rgw_common.h` and `rgw_op.h`, then declares `int rgw_opa_authorize(RGWOp*& op, req_state* s)`. Passing `RGWOp*&` lets the implementation log through the active operation and preserve the calling signature used in request processing.

## Control Flow
There is no control flow in the header. The declaration is consumed by `rgw_process.cc`, which conditionally calls it when `rgw_use_opa_authz` is true.

## State And Persistence
No state is stored here. All state is request-local in `req_state` or config-driven in the implementation.

## Dependencies And Integration Points
This header is the integration point between the request pipeline and `rgw_opa.cc`. Its dependency on `rgw_op.h` means consumers need the full `RGWOp` type rather than a lightweight forward declaration.

## Risks And Test Signals
The main risk is include coupling: any broad changes in `rgw_op.h` can increase compile impact for OPA consumers. Test signals are compile/link coverage with OPA enabled and request-processing tests with `rgw_use_opa_authz`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_opa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_os_lib.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_os_lib.cc

## Purpose
`rgw_os_lib.cc` implements lib-rgw request target parsing for `RGWHandler_Lib`. It maps a library frontend request URI into `req_state` bucket and object fields without the normal HTTP frontend assumptions.

## Important APIs, Types, And Functions
The only function is `rgw::RGWHandler_Lib::init_from_header(rgw::sal::Driver* driver, req_state* s)`. It parses `s->relative_uri`, initializes `s->info.args`, assigns `s->bucket_name`, `s->object_key.name`, `s->object_key.instance`, and creates `s->object` through `driver->get_object()`.

## Control Flow
The function treats leading `?` as a request-parameter-only URI, otherwise uses `s->info.request_params`; it parses args, strips a leading slash, derives the first path segment as bucket when no bucket is already set, and treats the remainder or full path as the object key. It also reads the `versionId` query arg into the object key instance.

## State And Persistence
It mutates only request-local `req_state`. No persistent bucket or object metadata is written. The object pointer is a SAL handle, not a read of object data.

## Dependencies And Integration Points
It depends on `rgw_rest*`, `rgw_file_int.h`, `rgw_lib_frontend.h`, and SAL driver object creation. It is specific to the RGW library/file frontend, where requests may not arrive as normal HTTP path-style or virtual-hosted S3 requests.

## Risks And Test Signals
Risks include ambiguous parsing for empty paths, paths without a leading slash, request params embedded in `relative_uri`, and version-id propagation. Tests should cover bucket-only, bucket/object, preselected bucket plus object path, query-only paths, versioned object access, and paths with nested object keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_os_lib.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_os_lib.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_os_lib.h

## Purpose
`rgw_os_lib.h` is a lightweight header for lib-rgw integration. It pulls in common RGW definitions and `rgw_lib.h` so the library frontend can expose handler functionality implemented in `rgw_os_lib.cc`.

## Important APIs, Types, And Functions
The header itself declares no new functions or classes. Its important role is include aggregation for `rgw_common.h` and `rgw_lib.h`.

## Control Flow
There is no runtime control flow.

## State And Persistence
There is no state or persistence behavior in the header.

## Dependencies And Integration Points
The header is part of the lib-rgw/frontend boundary. It intentionally keeps behavior out of the header and relies on `rgw_os_lib.cc` for request parsing.

## Risks And Test Signals
Risk is low and mostly compile-time: include churn in `rgw_lib.h` or `rgw_common.h` can affect users of this header. Build coverage of the lib-rgw frontend is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_os_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_perf_counters.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_perf_counters.cc

## Purpose
`rgw_perf_counters.cc` registers and manages RGW performance counters for frontend requests, operation-level per-user/per-bucket/global metrics, persistent topic queue metrics, and lifecycle per-bucket metrics.

## Important APIs, Types, And Functions
It defines global `PerfCounters *perfcounter`, builder helpers `add_rgw_frontend_counters()`, `add_rgw_op_counters()`, `add_rgw_topic_counters()`, lifecycle builder `add_lc_counters()`, init/stop APIs `rgw_perf_start()` and `rgw_perf_stop()`, operation counter cache helpers in `rgw::op_counters`, `persistent_topic_counters::CountersManager`, and `lc_counters::get()`.

## Control Flow
Startup calls `frontend_counters_init()`, optionally creates user, bucket, and lifecycle `PerfCountersCache` objects based on config, then initializes global op counters. Operation code asks `rgw::op_counters::get(req_state*)` for cached user and bucket counters and updates user, bucket, and global counters through `inc()`/`tinc()`. Topic counters are created per topic and removed in the manager destructor. Shutdown removes and deletes registered counters and caches.

## State And Persistence
Counters are in-memory perf-counter objects registered with Ceph's perf counter collection, not durable metadata. Label keys are built from users, tenants, buckets, and topics. Lifecycle per-bucket counters are debug-priority because labeled counters are not always exposed by mgr Prometheus paths.

## Dependencies And Integration Points
This file depends on `common/perf_counters`, `PerfCountersCache`, `perf_counters_key`, `CephContext`, config options, and `req_state` user/bucket fields. `rgw_process.cc` increments frontend queue and request counters. Pubsub and lifecycle paths consume the topic/lifecycle counters.

## Risks And Test Signals
Risks include counter id mismatches with the header enum, leaks or dangling registration on shutdown, null user/bucket assumptions in `get()`, cache key cardinality, and negative increments represented as unsigned counter operations. Test signals include daemon startup/shutdown under counter caches enabled/disabled, per-user/per-bucket metric creation with tenants, persistent-topic counter lifecycle, lifecycle counter lookup, and metric name/id stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_perf_counters.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_perf_counters.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_perf_counters.h

## Purpose
`rgw_perf_counters.h` declares the RGW perf counter id ranges and counter-management APIs used by the daemon and feature modules.

## Important APIs, Types, And Functions
It exports `perfcounter`, `rgw_perf_start()`, and `rgw_perf_stop()`. Enum ranges define frontend counters (`l_rgw_*`), operation counters (`l_rgw_op_*`), persistent topic counters (`l_rgw_persistent_topic_*`), and lifecycle per-bucket counters (`l_rgw_lc_per_bucket_*`). `rgw::op_counters::CountersContainer` carries optional user and bucket counter handles, with `get()`, `inc()`, and `tinc()` helpers. `rgw::persistent_topic_counters::CountersManager` owns a topic counter object. `rgw::lc_counters::get()` returns per-bucket lifecycle counters.

## Control Flow
The header establishes ids consumed by builder functions in the `.cc` file. Callers do not construct counters directly except through manager/helper APIs.

## State And Persistence
The header defines no state besides external declarations. Numeric ids are effectively ABI-like inside the daemon because they must match builder registration and metric consumers.

## Dependencies And Integration Points
It depends on common forward declarations, `rgw_common.h`, `PerfCountersCache`, and perf-counter key helpers. Request processing, lifecycle, pubsub, and operation implementations integrate through these declarations.

## Risks And Test Signals
Risks include adding ids outside ranges, changing order without updating builders, or calling helpers before `rgw_perf_start()`. Tests should verify startup registration, metric availability, and counter increments from representative object, bucket, lifecycle, and pubsub flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_perf_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_period.cc

## Purpose
`rgw_period.cc` implements selected `RGWPeriod` behavior for multisite realm periods: zonegroup lookup, sync-status capture, pool selection, JSON serialization, and test instances.

## Important APIs, Types, And Functions
Important functions are `RGWPeriod::get_zonegroup()`, `RGWPeriod::update_sync_status()`, `RGWPeriod::find_zone()`, `RGWPeriod::get_pool()`, `dump()`, and `decode_json()`. Internal `read_sync_status()` uses `RGWMetaSyncStatusManager` under `WITH_RADOSGW_RADOS`.

## Control Flow
`update_sync_status()` reads current metadata sync status, compares the current period realm epoch with sync status, and either rejects stale promotion unless forced, records empty shard markers for skipped periods, or copies shard markers for the current epoch. `get_zonegroup()` selects a requested id or `default`. `find_zone()` delegates to period-map lookup.

## State And Persistence
`update_sync_status()` mutates the period's `sync_status` vector. `get_pool()` chooses the period root pool from config or the default. Serialization persists period fields such as id, epoch, predecessor, sync status, period map, master zonegroup/zone, config, realm id, and realm epoch.

## Dependencies And Integration Points
This file integrates with SAL drivers, RADOS sync status manager, `rgw_meta_sync_status`, `rgw_zone`, and config-store consumers that read/write periods. Period pusher/puller/history code uses the period identity, predecessor, epoch, and JSON encoding.

## Risks And Test Signals
Risks include promoting a stale zone and losing metadata updates, marker count mismatches, build behavior without RADOS support returning `-ENOTSUP`, and JSON compatibility. Tests should cover stale and forced promotion, current-epoch marker filtering, missing/default zonegroup lookup, configured/default period root pools, and JSON round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_history.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_period_history.cc

## Purpose
`rgw_period_history.cc` implements an in-memory, thread-safe history manager for RGW realm periods. It tracks consecutive ranges of periods, detects forks, merges adjacent histories, and fetches missing predecessor periods through a pluggable `Puller`.

## Important APIs, Types, And Functions
Internal `History` stores a deque of consecutive `RGWPeriod` objects and exposes oldest/newest epoch, containment, indexed lookup, and predecessor id. `RGWPeriodHistory::Impl` owns a boost intrusive AVL set of disjoint histories. Public methods are `get_current()`, `attach()`, `insert()`, and `lookup()`. `Cursor` exposes period access and forward/backward navigation.

## Control Flow
Construction seeds the current history from the current period if available. `insert_locked()` places a period into an existing range, prepends/appends to adjacent ranges, creates a new disjoint range, updates an existing period if its period epoch is newer, or returns `-EEXIST` on same realm epoch with different period id. `attach()` inserts the requested period, then repeatedly pulls predecessor periods outside the mutex until the requested epoch connects to current history.

## State And Persistence
All state is in memory: intrusive set nodes own `History` allocations and deques. The destructor clears and deletes histories. Persistence is delegated to the `Puller` implementation, typically `RGWPeriodPuller`, which can read local config-store state or pull from the master zone.

## Dependencies And Integration Points
The implementation depends on `RGWPeriod`, `RGWPeriodHistory::Puller`, boost intrusive AVL set, mutex locking, Ceph logging, and config-store references passed to `attach()`. Multisite sync code can use cursors only when periods are connected to the current period.

## Risks And Test Signals
Risks include cursor invalidation for disjoint histories, fork detection, empty predecessor chains, locking mistakes around external pulls, and merge correctness when current history is the source or destination. Tests should cover insert before/after current, merging two ranges, duplicate epoch same/different id, attach with missing predecessors, current-period-empty construction, cursor traversal, and concurrent lookup/insert behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_history.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_history.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_period_history.h

## Purpose
`rgw_period_history.h` declares `RGWPeriodHistory`, the abstraction that lets multisite code traverse a connected period history around the realm's current period while hiding storage/pull details behind a `Puller`.

## Important APIs, Types, And Functions
`RGWPeriodHistory::Puller` declares `pull()` for retrieving periods by id. `RGWPeriodHistory::Cursor` represents a valid position in connected history and exposes `get_error()`, bool conversion, `get_epoch()`, `get_period()`, `has_prev()`, `has_next()`, `prev()`, and `next()`. Top-level APIs are constructor, destructor, `get_current()`, `attach()`, `insert()`, and `lookup()`.

## Control Flow
The header documents the key contract: only periods connected to `current_period` are reachable through a valid cursor. `attach()` may fetch missing periods; `insert()` does not fetch; `lookup()` succeeds only inside current history.

## State And Persistence
The public class owns a private `Impl`. Cursor state stores a history pointer, mutex pointer, epoch, and optional error code. No durable state is stored by the header; persistence depends on the `Puller`.

## Dependencies And Integration Points
It depends on `RGWPeriod`, `optional_yield`, `DoutPrefixProvider`, `rgw::sal::ConfigStore`, boost intrusive forward declarations, and Ceph epoch types. `RGWPeriodPuller` implements the `Puller` interface.

## Risks And Test Signals
Risks are mostly contract misuse: holding cursors from disconnected histories, using default/error cursors, or assuming `insert()` fetches predecessors. Unit tests should validate cursor bool/error behavior, traversal boundaries, attach versus insert semantics, and mock-puller failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_history.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_puller.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_period_puller.cc

## Purpose
`rgw_period_puller.cc` implements `RGWPeriodPuller`, the `RGWPeriodHistory::Puller` used to obtain missing periods locally or from the multisite master zone.

## Important APIs, Types, And Functions
`RGWPeriodPuller::pull()` is the public implementation. Internal `pull_period()` builds a synthetic admin REST GET for `/admin/realm/period`, forwards it through an `RGWRESTConn`, parses the JSON response, and decodes an `RGWPeriod`.

## Control Flow
`pull()` first tries `cfgstore->read_period()`. If local read fails and this zone is metadata master, it returns the failure. Otherwise it forwards a request to the master connection, rewrites the pulled period to a new local id and first epoch, creates it locally with exclusive create, updates latest epoch, optionally reflects it if it is the realm's current period, and tolerates `-EEXIST` for already-stored periods or latest epochs.

## State And Persistence
The function writes pulled periods into the local config store and updates latest-epoch metadata. It can also call `rgw::reflect_period()` to update local reflected realm/zone config for the latest current period.

## Dependencies And Integration Points
It depends on zone services, sysobj service references, `RGWRESTConn`, admin REST forwarding, HTTP error translation, JSON parsing, and config-store period APIs. `RGWPeriodHistory::attach()` calls it when predecessor periods are missing.

## Risks And Test Signals
Risks include master-zone unavailability, response size cap (`128 KiB`), malformed JSON, id/epoch rewriting assumptions, races with concurrent period creation, and reflection failure after storage succeeds. Tests should cover local hit, local miss on master zone, remote pull success, remote HTTP/JSON/decode failures, duplicate create/latest epoch, and current-period reflection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_puller.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_puller.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_period_puller.h

## Purpose
`rgw_period_puller.h` declares the concrete period-history puller backed by RGW zone services and config-store storage.

## Important APIs, Types, And Functions
`RGWPeriodPuller` derives from `RGWPeriodHistory::Puller`. It stores `CephContext*` and service pointers for `RGWSI_Zone` and `RGWSI_SysObj`. It exposes a constructor and overrides `pull()`.

## Control Flow
The header defines only the interface. Runtime behavior is in `rgw_period_puller.cc`.

## State And Persistence
The class retains service pointers but owns no durable state. Persistence occurs through `pull()` writing to the config store.

## Dependencies And Integration Points
It includes `rgw_period_history.h`, common forward declarations, and sysobj service headers. It is the bridge between in-memory period history and multisite services.

## Risks And Test Signals
Risks include service lifetime assumptions and null service pointers. Tests should instantiate with mock or fixture services and verify `RGWPeriodHistory` integration through the `Puller` interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_puller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_pusher.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_period_pusher.cc

## Purpose
`rgw_period_pusher.cc` implements background propagation of realm period updates from zone masters to peer zones and zonegroups. It responds to realm notifications, decides which peers need a period, and posts the period over REST with retry/backoff.

## Important APIs, Types, And Functions
`PushAndRetryCR` posts one period to one `RGWRESTConn` with exponential backoff. `PushAllCR` spawns a push coroutine per connection and drains them. `RGWPeriodPusher::CRThread` runs the coroutine manager and HTTP manager in a background thread. `RGWPeriodPusher` handles notifications, pause/resume during realm reload, and startup push of current period.

## Control Flow
Construction reads the current period and immediately processes it. `handle_notify()` decodes a `RGWPeriod`, queues notifications while paused, rejects stale period/realm epochs, verifies this zone's zonegroup, exits if this zone is not the master, builds connections to peer zonegroups if it is also the master zonegroup, builds connections to peer zones in its zonegroup, updates epoch tracking, and replaces the active coroutine thread. Each push retries every endpoint before sleeping, with exponential backoff bounded by config.

## State And Persistence
The pusher does not persist data locally; it transmits already-persisted period objects to peers. State includes current realm/period epoch sent, pending notifications while paused, a driver pointer that can be nulled during reconfiguration, and the active coroutine thread.

## Dependencies And Integration Points
It depends on realm watcher/reloader interfaces, SAL driver/zone config, `RGWRESTConn`, `RGWPostRESTResourceCR`, coroutine manager, HTTP manager, period JSON encoding, and config options `rgw_period_push_interval*`. It complements `RGWPeriodPuller`: peers may receive pushes or later pull missing periods.

## Risks And Test Signals
Risks include infinite retry on permanently unreachable peers, replacing active threads while pushes are in flight, driver access during reload, stale notification suppression, and incomplete peer selection. Tests should cover stale/newer notifications, master versus non-master zones, peer zonegroup and zone connection construction, pause/resume queue drain, retry/backoff behavior, and thread cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_pusher.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_pusher.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_period_pusher.h

## Purpose
`rgw_period_pusher.h` declares `RGWPeriodPusher`, the realm watcher/reloader participant responsible for pushing period updates to other zones.

## Important APIs, Types, And Functions
It aliases `RGWZonesNeedPeriod` to `RGWPeriod`, declares `RGWPeriodPusher final` deriving from `RGWRealmWatcher::Watcher` and `RGWRealmReloader::Pauser`, and exposes constructor, destructor, `handle_notify()`, `pause()`, and `resume()`.

## Control Flow
The header documents the high-level flow: notifications trigger period pushes; pause prevents access to stale driver state during dynamic reconfiguration; resume processes queued notifications with a new driver.

## State And Persistence
Member state includes `CephContext`, mutable driver pointer, mutex, current realm/period epochs, pending period notifications, and an opaque `CRThread`. Persistence is remote side effect through the `.cc` implementation.

## Dependencies And Integration Points
It depends on `rgw_realm_reloader.h`, SAL forward declarations, async yield, and epoch types. It integrates directly with realm watch/notify and reload orchestration.

## Risks And Test Signals
Risks include lock ordering with reloader callbacks, driver lifetime, and pending notification growth during long pauses. Tests should cover pauser lifecycle and notification handling during reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_period_pusher.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_placement_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_placement_types.h

## Purpose
`rgw_placement_types.h` defines `rgw_placement_rule`, the serialized representation of a placement target name plus storage class used by RGW buckets and object placement decisions.

## Important APIs, Types, And Functions
`rgw_placement_rule` stores `name` and `storage_class`, provides constructors, `empty()`, `inherit_from()`, `clear()`, `init()`, canonical storage-class helpers, comparison/equality, encoder/decoder, JSON dump, test instances, `to_str()`, `to_str_explicit()`, `from_str()`, and `standard_storage_class()`. `RGW_STORAGE_CLASS_STANDARD` is the default canonical class.

## Control Flow
Serialization encodes a single string for backward compatibility rather than an encoded struct envelope. `to_str()` omits `/STANDARD` for standard storage class, while `to_str_explicit()` always includes a slash. `from_str()` splits on the first slash and treats no slash as standard class.

## State And Persistence
Placement rules are persisted in bucket/zone placement metadata through their string encoding. Empty `storage_class` and explicit `STANDARD` compare equivalent through `get_storage_class()`.

## Dependencies And Integration Points
The type is used by bucket creation, metadata update, copy/storage-class checks, zone placement config, and data placement targets. It depends only on core types, buffer encoding, and formatter support.

## Risks And Test Signals
Risks include slash handling in placement names, the non-const global string definition in a header, compatibility of string-only encoding, and standard-class equivalence. Tests should cover encode/decode, `STANDARD` versus empty equality, non-standard storage classes, inherited placement, and sorting/compare semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_placement_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_policy_s3.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_policy_s3.cc

## Purpose
`rgw_policy_s3.cc` parses and evaluates S3 browser-upload POST policies. It validates expiration, exact-match and prefix conditions, content-length ranges, and ensures request variables are represented in policy conditions.

## Important APIs, Types, And Functions
Internal `RGWPolicyCondition` resolves literal or `$variable` operands through `RGWPolicyEnv` and delegates to derived checks. Implementations are `RGWPolicyCondition_StrEqual` and `RGWPolicyCondition_StrStartsWith`. `RGWPolicyEnv` stores case-insensitive variables. `RGWPolicy` implements `set_expires()`, `add_condition()`, `check()`, and `from_json()`.

## Control Flow
`from_json()` parses a bufferlist as JSON, requires `expiration`, parses ISO8601 time, requires `conditions`, and accepts either three-element condition arrays or simple object equality checks. `add_condition()` handles `eq`, `starts-with`, and `content-length-range`, updating min/max length for the latter. `check()` rejects expired policies, verifies simple checks, evaluates conditions, and finally asks the environment whether every non-ignored, non-checksum variable was covered.

## State And Persistence
Policy objects are in-memory request validators. They retain expiration string/time, condition pointers, simple checks, checked variable names, and min/max content length. No policy is persisted by this file.

## Dependencies And Integration Points
It depends on Ceph JSON parsing, clock/time parsing, string helpers, sanitized logging for policy values, checksum header recognition, and POST object request handling from `rgw_op.h`/protocol subclasses.

## Risks And Test Signals
Risks include manual ownership of condition pointers, overly strict missing-condition checks, variable case handling, time parsing, length bounds, and malformed JSON arrays. Tests should cover expired policies, valid/invalid `eq` and `starts-with`, content-length range narrowing, `$variable` resolution, ignored/checksum variables, malformed condition arrays, and sanitized logging paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_policy_s3.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_policy_s3.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_policy_s3.h

## Purpose
`rgw_policy_s3.h` declares the in-memory environment and policy evaluator for S3 POST policy validation.

## Important APIs, Types, And Functions
`RGWPolicyEnv` exposes `add_var()`, `get_var()`, `get_value()`, and `match_policy_vars()` over a case-insensitive variable map. `RGWPolicy` exposes `set_expires()`, `set_var_checked()`, `add_condition()`, `add_simple_check()`, `check()`, and `from_json()`, plus public `min_length` and `max_length` fields.

## Control Flow
The header defines a two-stage pattern: parse JSON into `RGWPolicy`, populate `RGWPolicyEnv` from request fields, then call `check()` to validate both explicit conditions and coverage of request variables.

## State And Persistence
`RGWPolicy` owns condition pointers and request-independent parsed policy state. It is not persisted by the header; it is constructed per policy validation.

## Dependencies And Integration Points
It depends on `rgw_string.h` for case-insensitive comparators and Ceph bufferlist declarations. `RGWPostObj` implementations are the primary consumers.

## Risks And Test Signals
Risks include public mutable length fields, pointer ownership, and the need to call `from_json()` before `check()`. Tests should validate parser/evaluator lifecycle and destructor cleanup under parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_policy_s3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_polparser.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_polparser.cc

## Purpose
`rgw_polparser.cc` is a small command-line utility that validates RGW IAM policy JSON files, optionally under a tenant context.

## Important APIs, Types, And Functions
`parse()` reads an input stream into a bufferlist and constructs `rgw::IAM::Policy`, reporting parse exceptions. `usage()` and `helpful_exit()` handle CLI messaging. `main()` initializes a Ceph context without daemon actions or monitor config, parses `--tenant/-t`, then parses stdin or listed files.

## Control Flow
The utility starts Ceph global initialization, processes help and tenant args, then iterates remaining file args. Missing files and parse failures set `success=false`; exit status is `0` only when all inputs parse.

## State And Persistence
It reads policy files/stdin only. No cluster metadata is written. Runtime state is limited to the Ceph context and optional tenant string.

## Dependencies And Integration Points
It depends on Ceph argument parsing, common/global init, bufferlist, and `rgw_iam_policy.h`. It is useful for developer/admin validation of IAM policy syntax and principal checks using `rgw_policy_reject_invalid_principals`.

## Risks And Test Signals
Risks include incomplete CLI validation, opening a missing file then still invoking parse on an unopened stream, and config-dependent principal validation. Tests should cover stdin, multiple files, unreadable files, tenant option, `-h`, invalid JSON, invalid principals, and exception reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_polparser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_pool_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_pool_types.h

## Purpose
`rgw_pool_types.h` defines fundamental serialized pool and data-placement types shared outside RGW-only contexts. The header explicitly avoids dependencies that require radosgw or OSD-only compilation contexts.

## Important APIs, Types, And Functions
`rgw_pool` stores pool `name` and namespace `ns`, with string conversion, initialization, comparison, encoding/decoding, JSON dump, test instances, and stream output. It includes legacy decode compatibility with older `rgw_bucket`-shaped encodings. `rgw_data_placement_target` stores data, data-extra, and index pools, exposes `get_data_extra_pool()`, comparison, dump, and JSON decode declarations.

## Control Flow
`rgw_pool::decode()` uses `DECODE_START_LEGACY_COMPAT_LEN(10, 3, 3)` and decodes only `name` for old versions, adding `ns` for version 10+. `get_data_extra_pool()` falls back to `data_pool` when the extra pool is empty.

## State And Persistence
These are serialized metadata types used in zone/bucket placement configuration. Compatibility behavior is central: old encodings must continue to decode correctly, and string forms are used in configuration and formatting.

## Dependencies And Integration Points
The header depends on core encoding, types, and formatter support. Placement, bucket metadata, period maps, and zone config use these types.

## Risks And Test Signals
Risks include breaking legacy decode, inconsistent `to_str()/from_str()` behavior in implementations, namespace comparison errors, and fallback semantics for data-extra pools. Tests should cover encode/decode across versions, namespace round trips, ordering/equality, JSON decode/dump, and data-extra fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_pool_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_process.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_process.cc

## Purpose
`rgw_process.cc` implements RGW request queue processing and the main authenticated request pipeline. It ties frontend I/O, REST handler selection, authentication, authorization, OPA, Lua hooks, dmclock scheduling, rate limiting, tracing, logging, bucket logging, and operation execution together.

## Important APIs, Types, And Functions
`RGWProcess::RGWWQ` implements enqueue/dequeue/process for the thread pool. `schedule_request()` integrates dmclock. `rate_limit()` checks global, user, anonymous, and bucket rate-limit settings. `rgw_process_authenticated()` runs the post-auth operation pipeline. `process_request()` handles the full request lifecycle from client I/O init to cleanup and logging.

## Control Flow
`process_request()` initializes client I/O, creates `req_state`, sets user and ids, gets a REST handler/op, schedules through dmclock, verifies requester, transforms legacy auth if needed, runs `postauth_init()`, rejects suspended users, executes pre-request Lua, starts tracing, and delegates to `rgw_process_authenticated()`. That function initializes permissions, retargets, reads permissions, initializes op/quota, checks op mask, optionally calls OPA, verifies permissions and params, runs `pre_exec()`, checks rate limits, runs post-auth Lua, executes the op, and completes the response. The done path runs post-request Lua, completes client I/O, logs ops and bucket logs, records tracing attrs, returns status, and releases handler/op.

## State And Persistence
Request state is transient but may trigger persistent effects through operations, rate-limit token accounting, user attr reads for STS users, ops logs, bucket logs, and Lua side effects. Perf counters track request count, queue length, and active queue count.

## Dependencies And Integration Points
This file depends on auth registry, REST handlers, RGW operations, OPA, perf counters, Lua, tracing, ratelimit, bucket logging, dmclock scheduler, frontend I/O, and SAL driver/user/bucket/object abstractions.

## Risks And Test Signals
Risks include goto cleanup correctness, null identity assumptions, OPA ordering versus native permissions, Lua failure policy, rate-limit token giveback, queue counter underflow on exceptions, health-check bypasses, and trace/log consistency on early abort. Tests should cover successful and aborted requests, auth failures, suspended users, OPA allow/deny, pre/post Lua deny and failure, dmclock `-EAGAIN`, user/bucket/anonymous rate limits, STS attr reads, health checks, and client I/O completion exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_process.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_process.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_process.h

## Purpose
`rgw_process.h` declares the RGW process abstraction, work queue, load generator process, and request-processing entry points.

## Important APIs, Types, And Functions
`RGWProcess` owns `CephContext`, `RGWProcessEnv`, thread pool, request throttle, frontend config, socket fd, URI prefix, and nested `RGWWQ`. It exposes `run()`, `handle_request()`, `pause()`, `unpause_with_new_config()`, and `close_fd()`. `RGWProcessControlThread` runs a process. `RGWLoadGenProcess` generates loadgen requests. Free functions `process_request()` and `rgw_process_authenticated()` expose the main pipeline.

## Control Flow
Concrete frontends subclass `RGWProcess` and enqueue requests into `RGWWQ`; worker threads call `handle_request()`, which typically calls `process_request()`. Pause/unpause controls the thread pool during config reload.

## State And Persistence
The class stores only runtime process state. Persistence occurs through operations invoked by `process_request()`, not the process wrapper itself.

## Dependencies And Integration Points
It depends on work queues, throttle, REST, ACL/user types, frontend config, dmclock scheduler, client I/O, and `RGWProcessEnv`. All RGW frontends use this interface to normalize request execution.

## Risks And Test Signals
Risks include throttle sizing, socket lifetime, pause/unpause interaction with live requests, queue ownership, and virtual `handle_request()` correctness in each frontend. Tests should cover queue operations, close fd idempotence, loadgen request generation, frontend-specific subclasses, and `process_request()` integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_process.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_process_env.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_process_env.h

## Purpose
`rgw_process_env.h` defines the shared runtime dependency bundle passed into RGW request processing and frontends.

## Important APIs, Types, And Functions
`RGWLuaProcessEnv` stores Lua background and a SAL Lua manager. `RGWProcessEnv` stores pointers/owners for config store, SAL driver, site config, REST dispatcher, ops log sink, auth strategy registry, active rate limiter, KMS cache, and optional Arrow Flight server/store.

## Control Flow
There are no methods. `process_request()` and operation code read dependencies from `req_state::penv`, which references this structure.

## State And Persistence
The struct owns some services via `std::unique_ptr` and references others by raw pointer. It is process-lifetime state, not serialized metadata.

## Dependencies And Integration Points
It connects request processing to auth, Lua, KMS, ratelimiting, REST, config store, SAL driver, site config, ops logging, dedup background declarations, and optional Arrow Flight integration.

## Risks And Test Signals
Risks include raw pointer lifetime, partially initialized environments, optional feature fields, and config reload replacement semantics. Tests should construct minimal process environments for request tests and verify null handling or required-field assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_process_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_public_access.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_public_access.cc

## Purpose
`rgw_public_access.cc` implements XML serialization, stream output, and union logic for S3 Public Access Block configuration.

## Important APIs, Types, And Functions
`PublicAccessBlockConfiguration::decode_xml()` reads `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, and `RestrictPublicBuckets`. `dump_xml()` emits the same under `PublicAccessBlockConfiguration`. `operator<<` prints a human-readable boolalpha form. `config_union()` combines two configs by memberwise logical OR.

## Control Flow
The file is straightforward: decode from XML into bools, dump bools for response XML, or union account-level and bucket-level settings so any enabled restriction remains enabled.

## State And Persistence
The functions operate on the serializable configuration struct. Persistence is via the struct's buffer encoding in the header and bucket/account attrs handled elsewhere.

## Dependencies And Integration Points
It depends on `rgw_xml.h` and Ceph `Formatter`. `RGWPut/Get/DeleteBucketPublicAccessBlock` in `rgw_op.h` use this type, and public policy-status logic can combine account and bucket settings with `config_union()`.

## Risks And Test Signals
Risks include XML name mismatches with S3 clients, bool formatting expectations, and a minor stream-output formatting omission before two field values. Tests should cover XML decode/dump round trips, union truth table, buffer encode/decode from the header, and S3 API compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_public_access.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_public_access.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_public_access.h

## Purpose
`rgw_public_access.h` defines the serializable representation of S3 Public Access Block settings.

## Important APIs, Types, And Functions
`PublicAccessBlockConfiguration` has four bool fields: `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, and `RestrictPublicBuckets`. It implements Ceph buffer encode/decode version 1, declares XML decode/dump, and has a `WRITE_CLASS_ENCODER`. The header also declares `operator<<` and `config_union()`.

## Control Flow
There is no complex control flow. Encoding writes all four bools in fixed order; decoding reads the same order.

## State And Persistence
This struct is the durable attr payload for public-access block configuration. Default construction disables all restrictions.

## Dependencies And Integration Points
It depends on Ceph encoding and XML/formatter forward declarations. RGW bucket public-access operations and policy-status calculations use it.

## Risks And Test Signals
Risks include changing field order/version incorrectly, default false semantics, and mismatch between buffer and XML representations. Tests should cover default config, encode/decode, XML parse/dump, account/bucket union, and request behavior for each flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_public_access.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_pubsub.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_pubsub.cc

## Purpose
`rgw_pubsub.cc` implements RGW bucket notification and pubsub topic metadata behavior, including S3 notification XML parsing/dumping, topic/destination JSON/XML formatting, v1/v2 topic storage, bucket notification attr updates, account topic listing, persistent-topic shard cleanup, and notification removal.

## Important APIs, Types, And Functions
Utility functions format and parse topic metadata keys (`tenant:topic[.shard]`), generate event ids, match event lists, and decode XML event lists. `rgw_pubsub_s3_notification(s)` handles S3 `NotificationConfiguration`. `rgw_pubsub_s3_event`, `rgw::notify::event_entry_t`, `rgw_pubsub_topic`, `rgw_pubsub_topic_filter`, `rgw_pubsub_bucket_topics`, `rgw_pubsub_topics`, and `rgw_pubsub_dest` dump or decode notification structures. `RGWPubSub` implements topic listing, topic get/create/remove, and nested `Bucket` notification operations. Helper functions manage bucket notification attrs and topic-bucket mappings.

## Control Flow
The constructor determines whether notification v2 is supported by all zonegroups. Topic reads use v2 metadata when enabled and v1 migration state is absent; otherwise they read tenant topic aggregates. Bucket writes in v2 refuse service while v1 topic migration is present or indeterminate. Creating a bucket notification reads the topic, reads existing bucket topics with an object-version tracker, inserts/updates a filter, and writes back. V2 notification deletion edits `RGW_ATTR_BUCKET_NOTIFICATION` and updates mapping metadata. Topic deletion removes persistent queue shards before deleting topic metadata.

## State And Persistence
Persistent state includes topic metadata objects, v1 tenant topic aggregates, bucket topic objects, `RGW_ATTR_BUCKET_NOTIFICATION` attrs, bucket-topic mapping omaps, and persistent topic queues/shards. Version trackers protect some writes. The code tolerates absent metadata as no-op in several delete/read paths.

## Dependencies And Integration Points
It depends on SAL driver topic APIs, bucket attr APIs, `rgw_notify`, zone feature detection, account id validation, ARN/topic structs, XML/JSON formatters, notification event type conversion, and common errno handling. Operation classes declared elsewhere call these APIs for S3-compatible topic and bucket notification endpoints.

## Risks And Test Signals
Risks include v1/v2 migration gating, partial failure between bucket attr writes and mapping updates, shard-name parsing/removal, tenant/account key filtering, missing topic treatment, object-version race handling, event/filter XML compatibility, and cleanup of persistent queues. Tests should cover v1 and v2 topic create/list/get/delete, migration-in-progress service-unavailable behavior, account topic listing, bucket notification create/remove by topic and id, delete-all behavior, attr decode failures, persistent topic shard cleanup, event XML defaults, and topic metadata key parsing with tenants and shard suffixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_pubsub.cc -->
