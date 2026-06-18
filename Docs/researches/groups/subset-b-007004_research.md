# Research: subset-b-007004

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.cc

Purpose: Implements the RADOS/system-object backed bucket sync service for RGW bucket sync policy handlers and bucket sync hint indexes. It connects bucket instance metadata, zone sync policies, object cache chaining, and persistent hint objects that allow related buckets to discover potential sources and destinations.

Important APIs, types, and functions: `RGWSI_Bucket_Sync_SObj::init()` wires zone, sysobj, cache, and bucket services. `do_start()` creates a `RGWChainedCacheImpl<bucket_sync_policy_cache_entry>`. `get_policy_handler()` and `do_get_policy_handler()` resolve a zone/bucket to a `RGWBucketSyncPolicyHandlerRef`, reading entrypoint or instance metadata as needed. `resolve_policy_hints()` expands bucket-level source/target hints through zone policy reflection. `RGWSI_Bucket_Sync_SObj_HintIndexManager` maps buckets to `bucket.sync-source-hints.*` and `bucket.sync-target-hints.*` system objects. `RGWSI_BS_SObj_HintIndexObj` owns the encoded hint map, version tracker, read/flush/update loop, and nested `bi_entry`, `single_instance_info`, and `info_map` encoders.

Control flow: Policy lookup first normalizes a bucket by resolving its entrypoint if `bucket_id` is empty, then reads bucket instance info and attrs, builds a child sync policy handler from the zone policy handler, initializes it, resolves relaxed source/target hints, and chains it into the sysobj cache using the bucket metadata cache info. Hint updates compute added and removed source/destination bucket sets from old and new policies, update the local source/destination index, and update reciprocal indexes on related buckets. Reads of hints load the source and/or target hint object and return entries for both the instance-specific bucket key and the bucket key with `bucket_id` cleared.

State and persistence: Policy handlers are cached in memory and invalidated through chained cache entries tied to underlying bucket metadata. Hint indexes are stored as encoded maps in the zone log pool under deterministic object names. Updates use `RGWObjVersionTracker` and retry on `-ECANCELED` up to `MAX_RETRIES` to handle concurrent writers. Empty hint maps remove the backing object.

Dependencies and integration points: Depends on `RGWSI_Zone`, `RGWSI_SysObj`, `RGWSI_SysObj_Cache`, `RGWSI_Bucket_SObj`, `RGWBucketSyncPolicyHandler`, `rgw_sync_bucket_entity`, and `rgw_sync_bucket_pipe`. It is called by bucket metadata update/removal paths through the `RGWSI_Bucket_Sync` interface and uses sysobj/cache services for persistence and invalidation.

Risks and test signals: Correctness depends on ordered `rgw_bucket` comparison, monotonic object versions, reciprocal index updates, and cache invalidation. Decode errors on hint objects are treated as empty/ignored during reads, which can drop hint state. Multi-zone bucket sync tests should verify policy handler cache invalidation, concurrent hint updates, bucket deletion cleanup, source/destination reciprocal lookups, and behavior for buckets with and without instance ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.h

Purpose: Declares the concrete system-object backed implementation of the RGW bucket sync service.

Important APIs, types, and functions: `RGWSI_Bucket_Sync_SObj` derives from `RGWSI_Bucket_Sync`. It stores a chained cache of bucket sync policy handlers and a hint index manager. The public API exposes `init()`, `get_policy_handler()`, `handle_bi_update()`, `handle_bi_removal()`, and `get_bucket_sync_hints()`. The private `optional_zone_bucket` key supports caching temporary policy handlers during recursive hint resolution.

Control flow: Callers initialize dependencies, service startup creates the cache, bucket metadata changes enter through `handle_bi_update()`/`handle_bi_removal()`, and sync workers/admin paths can ask for policy handlers or related bucket hints. Private helpers resolve policy hints and recursively load hinted bucket handlers while avoiding repeated loads through a temporary map.

State and persistence: The header declares in-memory cache ownership and service pointers only; persistent state is in the implementation's sysobj hint indexes and bucket metadata objects.

Dependencies and integration points: Depends on RGW service infrastructure, bucket sync base interface, zone/sysobj/cache/bucket services, and sync policy handler types from RGW bucket sync. It is part of the RGW service graph created by `RGWServices_Def`.

Risks and test signals: The contract assumes `init()` is called before `do_start()` and before any policy/hint operation. Tests should exercise the virtual base interface through this implementation and verify null optional zone/bucket cases as well as bucket-instance normalization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync_sobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_cls.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_cls.cc

Purpose: Implements RGW wrappers around RADOS cls object classes for OTP/MFA, time-indexed logs, and distributed locks.

Important APIs, types, and functions: `RGWSI_Cls::do_start()` starts the MFA subservice. `MFA::get_mfa_ref()`, `check_mfa()`, `create_mfa()`, `remove_mfa()`, `get_mfa()`, `list_mfa()`, `otp_get_current_time()`, `set_mfa()`, and the oid-based `list_mfa()` wrap `cls_otp_client`. `TimeLog::prepare_entry()`, `add()`, `list()`, `info()`, `info_async()`, and `trim()` wrap `cls_log_client`. `Lock::lock_exclusive()` and `unlock()` wrap `cls_lock_client` with a default `rgw_log_lock` name.

Control flow: MFA methods resolve the per-user OTP object in `zone_params.otp_pool`, prepare versioned writes when needed, run cls operations, and translate OTP check failure to `-EACCES`. TimeLog methods resolve log objects in `zone_params.log_pool`, build cls log read/write operations, and run them synchronously or with librados aio completions. Lock methods initialize an IoCtx for the target pool, configure lock duration, cookie, tag, and optional lock name, then call cls lock APIs.

State and persistence: MFA entries are stored in per-user objects named `user:<uid>` in the OTP pool with version tracker and mtime handling. Time logs persist as cls log entries in log pool objects. Locks persist in RADOS object class lock state and are tagged with zone and owner ids.

Dependencies and integration points: Depends on `RGWSI_Zone` for pool selection, `librados::Rados`, `rgw_rados_ref`, `RGWObjVersionTracker`, and Ceph cls clients for otp/log/lock. MDLog and other services use `TimeLog` and `Lock` for metadata log operations.

Risks and test signals: MFA writes depend on correct version tracker progression and object reset semantics in `set_mfa()`. TimeLog async calls depend on caller-owned `AioCompletion` lifetime. Lock renewal and unlock require consistent tag/cookie. Unit or integration tests should cover OTP CRUD/check failures, metadata log add/list/trim, async info completion, and lock contention/unlock errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_cls.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_cls.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_cls.h

Purpose: Declares `RGWSI_Cls`, the RGW service facade for selected RADOS object-class features.

Important APIs, types, and functions: The service owns nested subservices `MFA`, `TimeLog`, and `Lock`, all derived from `ClsSubService` so they can reach the parent `RGWSI_Cls`. The header declares all MFA OTP APIs, time-log add/list/info/trim APIs, and lock/unlock APIs. `init()` binds `RGWSI_Zone` and `librados::Rados` and initializes subservices.

Control flow: Consumers call `RGWSI_Cls::init()`, then start the service, then use `mfa`, `timelog`, and `lock` members directly. Subservices delegate pool lookup to the parent zone service and execute cls operations in the implementation.

State and persistence: The header holds only pointers to zone and RADOS services plus subservice instances. Persistent state lives in RADOS object class objects.

Dependencies and integration points: Depends on cls OTP/log types, RGW service base, and RGW RADOS helpers. It is a common dependency for metadata log and security operations.

Risks and test signals: Because subservices are public members, lifetime/order bugs can occur if they are used before `init()` or service startup. Compile tests should verify cls type availability; integration tests should validate each subservice against real RADOS pools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_cls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_config_key.h

Purpose: Defines the abstract RGW service interface for reading monitor config-key values.

Important APIs, types, and functions: `RGWSI_ConfigKey` derives from `RGWServiceInstance` and declares pure virtual `get(const std::string& key, bool secure, bufferlist *result)`.

Control flow: Concrete backends implement `get()`; callers pass `secure=true` when the fetched value is sensitive and should trigger transport security checks or warnings.

State and persistence: This interface has no state beyond RGW service lifetime. Config-key values are persisted by the Ceph monitor config-key store.

Dependencies and integration points: Depends on RGW service base and Ceph `bufferlist`. The RADOS implementation uses monitor commands.

Risks and test signals: The key contract is intentionally minimal, so backend behavior around secure reads is important. Tests should mock or run a monitor command path and confirm errors and sensitive-key warnings are surfaced by the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.cc

Purpose: Implements monitor config-key reads through `librados::Rados::mon_command()`.

Important APIs, types, and functions: `do_start()` records whether the monitor connection may be insecure via `rgw_check_secure_mon_conn()`. `warn_if_insecure()` emits a cluster log and local error log at most once using `atomic_flag`. `get()` builds a JSON `config-key get` command and returns the monitor response in a `bufferlist`.

Control flow: Startup checks monitor transport security. Each `get()` sends a monitor command. If the monitor returns an error, it is propagated. If the caller marked the key as secure, the service emits a one-time warning when the monitor connection is potentially insecure.

State and persistence: The service stores a RADOS pointer, a boolean for insecure-connection possibility, and an atomic one-shot warning flag. The fetched config-key data remains monitor-persisted.

Dependencies and integration points: Depends on `rgw_check_secure_mon_conn()`, `rgw_clog_warn()`, `librados::Rados`, and Ceph monitor command JSON format.

Risks and test signals: The JSON command is string-concatenated, so unusual key strings need validation at higher layers or escaping assumptions from monitor APIs. Secure reads over insecure monitor connections only warn; they do not fail. Tests should cover missing keys, successful values, secure warning once, and startup with secure/insecure monitor modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.h

Purpose: Declares the RADOS-backed implementation of the config-key service.

Important APIs, types, and functions: `RGWSI_ConfigKey_RADOS` derives from `RGWSI_ConfigKey`, owns `maybe_insecure_mon_conn`, `warned_insecure`, and a public `librados::Rados*`. It declares `init()`, `do_start()`, `warn_if_insecure()`, destructor, and override `get()`.

Control flow: `init()` binds RADOS, startup probes connection security, and `get()` performs monitor command reads.

State and persistence: Only in-memory warning and RADOS dependency state is declared here. Config-key values remain in monitor storage.

Dependencies and integration points: Depends on `<atomic>`, RGW service base, the abstract config-key service, and librados.

Risks and test signals: Callers must initialize `rados` before use. Tests should confirm the service can be started in the RGW service graph and that `secure` reads interact with the warning state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_config_key_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.cc

Purpose: Implements the RGW metadata log service, including period-aware metadata log selection, oldest-log-period history persistence, coroutine wrappers for async system-object reads/writes, and metadata log entry completion.

Important APIs, types, and functions: `RGWSI_MDLog::init()` wires RADOS, zone, sysobj, cls, and async processor. `do_start()` creates the current period log, `RGWPeriodPuller`, and `RGWPeriodHistory`. `read_history()` and `write_history()` serialize `RGWMetadataLogHistory`. The `mdlog` namespace defines `SysObjReadCR`, `SysObjWriteCR`, `ReadHistoryCR`, `WriteHistoryCR`, and `TrimHistoryCR`. Public operations include `find_oldest_period()`, `init_oldest_log_period()`, `read_oldest_log_period()`, `read_oldest_log_period_cr()`, `trim_log_period_cr()`, `get_log()`, `add_entry()`, `complete_entry()`, `get_shard_id()`, and `pull_period()`.

Control flow: Startup obtains the zone's current period, creates or retrieves the associated `RGWMetadataLog`, and initializes period history. If sync is enabled and the zone needs sync, it initializes oldest-log history. Synchronous history reads fetch `RGWMetadataLogHistory::oid` from the log pool, decode it, and remove empty corrupt objects. Coroutine history reads/writes queue async sysobj operations and update cursors or object versions. Trimming reads existing history, rejects older trim attempts, then writes the next cursor. Metadata completion encodes `RGWMetadataLogData` with `MDLOG_STATUS_COMPLETE` and appends it to the current log using a hash key of `section:key`.

State and persistence: `md_logs` caches per-period `RGWMetadataLog` objects in memory. `current_log` points to the current period log. `RGWMetadataLogHistory` persists oldest period id and realm epoch in the zone log pool. Metadata entries persist in cls log-backed metadata log shards. Version trackers protect history updates.

Dependencies and integration points: Depends on `RGWSI_Zone`, `RGWSI_SysObj`, `RGWSI_Cls`, `RGWAsyncRadosProcessor`, `RGWMetadataLog`, `RGWPeriodHistory`, `RGWPeriodPuller`, `RGWCoroutine`, and config store period reads. User and metadata services call `complete_entry()` when metadata object mutations are committed.

Risks and test signals: `init_oldest_log_period()` contains an early return after the rewrite path in this snapshot, leaving the later pull-by-period-id block unreachable from visible control flow. History corruption, empty history objects, concurrent trims, and missing predecessor periods are high-risk cases. Tests should cover single-period and multi-period startup, sync-enabled oldest period initialization, concurrent trim conflict (`-ECANCELED`), metadata completion shard selection, and decode failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.h

Purpose: Declares RGW's metadata log service and its period-history API.

Important APIs, types, and functions: `RGWSI_MDLog` derives from `RGWServiceInstance`, owns a map of per-period `RGWMetadataLog` objects, the current log pointer, sync flags, period puller/history, config store, RADOS and async processor pointers, and service dependencies. It exposes lifecycle setup, oldest-period discovery/init/read/trim coroutine APIs, history read/write, entry add/complete, shard lookup, period pull, and `get_log()`.

Control flow: Consumers initialize the service with zone/sysobj/cls/async dependencies, start it, then use `add_entry()` or `complete_entry()` for current-period mutations and the period-history APIs for sync trimming.

State and persistence: In-memory state tracks loaded period logs and period history helpers. Persistent state is metadata log objects and the metadata log history object in the log pool.

Dependencies and integration points: Depends on RGW period history/puller, metadata log classes, coroutine type, zone/sysobj/cls services, and SAL config store.

Risks and test signals: The API assumes `current_log` is initialized before add/shard calls. Service-order tests should verify zone and sysobj startup precede mdlog use; sync tests should verify coroutine paths update object versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_mdlog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_notify.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_notify.cc

Purpose: Implements RGW's RADOS watch/notify service for distributing cache invalidation/update messages across RGW instances.

Important APIs, types, and functions: `RGWWatcher` implements `librados::WatchCtx2` and `DoutPrefixProvider`, handling notify callbacks, errors, watch registration, unregistration, and reinitialization. `RGWSI_Notify::init_watch()` creates control objects and registers watchers. `finalize_watch()` unregisters them. `do_start()`, `shutdown()`, `add_watcher()`, `remove_watcher()`, `watch_cb()`, `distribute()`, `robust_notify()`, `register_watch_cb()`, and `schedule_context()` provide the service behavior. `decode_timeouts()` parses librados notify replies to report timed-out watchers.

Control flow: Startup starts zone service, starts a `Finisher`, reads notify timeout injection and retry settings, chooses the control pool, creates control objects, and registers one watcher per configured control oid using spawn throttle. A watcher receiving a notification calls the registered callback and acks. Watch errors remove the watcher, disable the cache if the full watcher set was previously active, and schedule reinit through the finisher. `distribute()` hashes a key to a control object and sends a robust notify. On timeout, `robust_notify()` retries with an invalidation-only payload up to the configured limit.

State and persistence: Control objects live in the zone control pool under `notify` or `notify.<n>`. In-memory state tracks watcher vector, active watcher set, callback, enabled state, retry counters, finisher, and finalized flag. Notification payloads are transient bufferlists.

Dependencies and integration points: Depends on `RGWSI_Zone`, `librados`, `RGWCacheNotifyInfo`, Ceph async spawn throttle, `Finisher`, and object cache callbacks. `RGWSI_SysObj_Cache` registers as a callback consumer.

Risks and test signals: Reinit loops abort after more than 100 retries. Cache is enabled only when all watchers are active and disabled on loss. `distribute()` guards against division by zero before watchers initialize. Tests should cover multi-control-object startup, watcher loss/reinit, cache enable/disable callback propagation, notify timeout retry/invalidation behavior, injected timeout probability, and clean shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_notify.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_notify.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_notify.h

Purpose: Declares the RGW notify service interface and callback contract for watch/notify-driven cache coherency.

Important APIs, types, and functions: `RGWSI_Notify` owns zone/RADOS pointers, a `Finisher`, watcher synchronization, control pool, watcher collection, retry settings, callback pointer, and lifecycle helpers. Nested abstract `CB` declares `watch_cb()` and `set_enabled()`. Public API includes constructor, destructor, `distribute()`, and `register_watch_cb()`.

Control flow: The service is initialized by `RGWServices_Def`, started to register watchers, and used by cache services to distribute `RGWCacheNotifyInfo` messages. Registered callbacks receive watch events and enabled-state transitions.

State and persistence: Watcher state is in memory; control objects are persistent RADOS objects in the control pool. The callback is not owned by this service.

Dependencies and integration points: Depends on RGW service base, `Finisher`, RADOS helpers, and `RGWCacheNotifyInfo`. Integrated with `RGWSI_SysObj_Cache`.

Risks and test signals: Callback lifetime must exceed registration or be cleared by service shutdown order. Tests should check startup/shutdown idempotence and callback behavior when watchers are partially registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_quota.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_quota.cc

Purpose: Implements accessors for current period bucket and user quota configuration.

Important APIs, types, and functions: `get_bucket_quota()` returns `zone_svc->get_current_period().get_config().quota.bucket_quota`. `get_user_quota()` returns the corresponding user quota.

Control flow: Callers initialize the service with a zone service and then read immutable references to quota config from the current period.

State and persistence: No persistence is owned here; quota data comes from the current period configuration maintained by the zone service.

Dependencies and integration points: Depends on `RGWSI_Zone` and `RGWQuotaInfo`. Bucket/user operation code can use this service to apply period-wide defaults.

Risks and test signals: References become invalid if the underlying period object lifetime changes unexpectedly. Tests should verify quota values reflect period config and service order initializes zone before quota use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_quota.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_quota.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_quota.h

Purpose: Declares the RGW quota service wrapper around zone period quota configuration.

Important APIs, types, and functions: `RGWSI_Quota` derives from `RGWServiceInstance`, stores an `RGWSI_Zone*`, and exposes `init()`, `get_bucket_quota()`, and `get_user_quota()`.

Control flow: The service is initialized with zone dependency and then read by quota enforcement paths.

State and persistence: No owned persistent state. It exposes references into zone current period config.

Dependencies and integration points: Depends on RGW service base and zone service.

Risks and test signals: Null `zone_svc` before `init()` is the main local risk. Compile and service-graph tests should catch dependency wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.cc

Purpose: Implements creation and startup of RGW sync module instances for the local zone tier type.

Important APIs, types, and functions: `init()` creates `RGWSyncModulesManager` and registers built-in sync modules through `rgw_register_sync_modules()`. `do_start()` reads the zone's public config tier type and zone params tier config, then calls `create_instance()`. The destructor deletes the manager.

Control flow: After initialization with zone service, startup creates the module instance. On `-ENOENT`, it logs registered module names for diagnostics. On success, `sync_module` is available through the header accessor.

State and persistence: In-memory manager and module instance only. Persistent tier config comes from zone params.

Dependencies and integration points: Depends on `RGWSI_Zone`, `RGWSyncModulesManager`, sync module registration, and tier config. Zone startup later queries manager capabilities and module instance behavior.

Risks and test signals: Missing or misspelled tier types prevent RGW startup. Tests should verify default tier starts, invalid tier returns `-ENOENT` with useful diagnostics, and module capability flags match zone decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.h

Purpose: Declares RGW's sync module service.

Important APIs, types, and functions: `RGWSI_SyncModules` derives from `RGWServiceInstance`, owns `RGWSyncModulesManager*`, `RGWSyncModuleInstanceRef`, and a zone service pointer. It exposes `get_manager()`, `init()`, `do_start()`, and `get_sync_module()`.

Control flow: `init()` registers modules, startup creates the configured module instance, and other services query the manager or active module reference.

State and persistence: The service owns only in-memory module registry and module instance. Zone config persists the selected tier type/config.

Dependencies and integration points: Depends on RGW sync module framework and zone service. Zone service uses it to determine write/data-export support and to build sync relationships.

Risks and test signals: Manual `new`/`delete` manager ownership is simple but order-sensitive. Tests should cover destructor after partial initialization and startup failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sync_modules.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.cc

Purpose: Implements the high-level fluent system-object facade that forwards read, write, omap, notify, and pool-list operations to the configured core backend.

Important APIs, types, and functions: `RGWSI_SysObj::get_obj()` creates an `Obj`. `Obj::ROp` methods call `stat()`, `read()`, and `get_attr()` on the core. `Obj::WOp` methods call `remove()`, `write()`, `write_data()`, `set_attrs()`, and single-attr writes. `Obj::OmapOp` methods call omap get/set/delete. `Obj::WNOp::notify()` forwards notify. `Pool` and `Pool::Op` forward prefix-list and paginated list operations. `get_zone_svc()` exposes the core's zone service.

Control flow: Callers construct lightweight operation objects from `Obj` or `Pool`, set optional parameters on the operation object, then call the terminal method. The operation object collects parameters and delegates to the backend core, which may be cached or uncached.

State and persistence: Operation objects hold transient pointers to version trackers, attrs, flags, and list contexts. Persistent state is in RADOS system objects managed by the core backend.

Dependencies and integration points: Depends on `RGWSI_SysObj_Core`, zone service, RGW raw object and pool types, `RGWObjVersionTracker`, and cache info. This facade is used by user, mdlog, bucket sync, zone, and other RGW metadata services.

Risks and test signals: Because operations store raw pointers supplied by callers, lifetime is caller-managed. Tests should exercise fluent setters, stat/read/write attr behavior, omap operations, notify, and paginated pool listing through both core and cache backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.h

Purpose: Declares the system-object service abstraction used by RGW metadata code to avoid direct RADOS operations at call sites.

Important APIs, types, and functions: `RGWSI_SysObj` derives from `RGWServiceInstance` and declares nested `Obj`, `Obj::ROp`, `Obj::WOp`, `Obj::OmapOp`, `Obj::WNOp`, `Pool`, `Pool::Op`, and list context types. The API provides setters for version trackers, attrs, mtime, exclusive create, raw attrs, refresh versions, cache info, omap must-exist, and pool listing markers/prefixes.

Control flow: Service graph initializes `RGWSI_SysObj` with a RADOS pointer and concrete `RGWSI_SysObj_Core`. Consumers get an object or pool handle and build operation objects for read/write/list operations.

State and persistence: The service holds RADOS and core pointers only. Operation structs hold transient call configuration and use `static_ptr` to host backend-specific state.

Dependencies and integration points: Depends on RGW service base, sysobj type headers, core type headers, `rgw_raw_obj`, `rgw_pool`, and cache entry info. It is a central integration point for most RGW service metadata persistence.

Risks and test signals: Backend-specific state size in `static_ptr` must remain large enough for derived state types. Tests should compile with all backend state types and exercise operation APIs through `RGWSysObj` alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.cc

Purpose: Implements the cached system-object backend, including object cache reads/writes, distributed cache update/invalidation through notify service, chained cache support, and admin-socket cache inspection commands.

Important APIs, types, and functions: `RGWSI_SysObj_Cache_CB` adapts notify callbacks. `do_start()` starts admin socket, core, notify service, and registers callback. Overrides include `remove()`, `read()`, `get_attr()`, `set_attrs()`, `write()`, `write_data()`, and `raw_stat()`. `distribute_cache()` sends `RGWCacheNotifyInfo`. `watch_cb()` applies incoming `UPDATE_OBJ` or `INVALIDATE_OBJ`. Chained cache functions register, unregister, and chain entries. `RGWSI_SysObj_Cache_ASocketHook` and `ASocketHandler` implement `cache list`, `cache inspect`, `cache erase`, and `cache zap`.

Control flow: Reads with offset zero try the object cache first using requested flags for data, obj version, metadata, and xattrs. Cache miss falls through to core read, then caches complete data unless the read probably truncated at `end + 1`. Writes/removes execute the core operation first, then update or invalidate local cache and distribute a notify message. Incoming notifications update or invalidate local cache. Admin socket calls iterate, inspect, erase, or clear cache entries.

State and persistence: In-memory `ObjectCache` stores data, xattrs, metadata, status, and object versions keyed by normalized `pool+namespace+oid`. Persistent metadata remains in RADOS via core operations. Notify control objects carry transient invalidation/update messages. Chained cache entries are invalidated with their source cache entries.

Dependencies and integration points: Depends on `RGWSI_SysObj_Core`, `RGWSI_Notify`, `ObjectCache`, `RGWCacheNotifyInfo`, admin socket framework, and zone params for object normalization when oid is empty. Bucket sync and user services use chained caches through this service.

Risks and test signals: Cache coherency depends on successful notify distribution, but distribution failures are logged and nonfatal after local writes. Partial reads and refresh-version checks affect caching behavior. Tests should cover cache hit/miss, ENOENT negative caching, write/update propagation, remove invalidation, raw/stat xattr filtering, watcher callback decode errors, chained cache invalidation, and admin socket commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.h

Purpose: Declares the cached sysobj backend and generic chained cache helper.

Important APIs, types, and functions: `RGWSI_SysObj_Cache` derives from `RGWSI_SysObj_Core`, owns notify service pointer, `ObjectCache`, callback, and `ASocketHandler`. It overrides core read/write/stat/attr/remove paths and exposes `chain_cache_entry()`, `register_chained_cache()`, and `unregister_chained_cache()`. `RGWChainedCacheImpl<T>` stores keyed entries with optional expiry, registers with sysobj cache, supports `find()`, `put()`, `chain_cb()`, `invalidate()`, and `invalidate_all()`.

Control flow: Backend methods cache sysobj operations and use notify callbacks for coherency. Chained caches are populated only while the object cache lock can safely invoke chain callbacks, preserving lock ordering.

State and persistence: `ObjectCache` and chained cache maps are in memory. Entries may expire based on `rgw_cache_expiry_interval`. Persistent system-object state remains in RADOS.

Dependencies and integration points: Depends on `ObjectCache`, `RGWChainedCache`, `RWLock`, notify service, sysobj core, and admin socket support. Policy and user-index caches use `RGWChainedCacheImpl`.

Risks and test signals: Lock ordering and expiry are key correctness points. Tests should cover chained cache registration/unregistration, expiry, invalidation on source object changes, and cache admin commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.cc

Purpose: Implements the uncached RADOS backend for RGW system-object operations.

Important APIs, types, and functions: `RGWSI_SysObj_Core_GetObjState::get_rados_obj()` lazily resolves a `rgw_rados_ref`. Core methods include `get_rados_obj()`, `raw_stat()`, `stat()`, `read()`, `get_attr()`, `set_attrs()`, `omap_get_vals()`, `omap_get_all()`, `omap_set()`, `omap_del()`, `notify()`, `remove()`, `write()`, `write_data()`, and pool listing methods.

Control flow: Each operation resolves an object or IoCtx, builds a `librados::ObjectReadOperation` or `ObjectWriteOperation`, applies version tracker hooks when provided, executes via RADOS helpers, and returns negative errno or data length. Reads track the RADOS operation version in read state and return `-ECANCELED` if a later read on the same state observes a different version. Full writes remove and recreate nonexclusive objects, set mtime, write data and attrs, and apply write versions.

State and persistence: Persistent state is RADOS object data, xattrs, omap entries, and object versions. The core holds RADOS and zone service pointers. Pool listing context stores IoCtx, prefix filter, and marker.

Dependencies and integration points: Depends on `rgw_get_rados_ref()`, `rgw_rados_operate()`, `rgw_init_ioctx()`, `rgw_list_pool()`, `RGWObjVersionTracker`, RGW attr filtering, and librados operations. It underlies both direct sysobj service use and the cache backend.

Risks and test signals: Empty object ids return `-EINVAL`. Nonexclusive `write()` replaces the whole object, so callers must choose `write_data()` or attr writes carefully. `get_attr()` ignores the per-op `rval` and returns success if the object operation succeeds, which relies on librados operation error propagation. Tests should cover version race detection, xattr filtering, omap pagination, exclusive create, remove ENOENT behavior, notify, and pool marker progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.h

Purpose: Declares the virtual backend contract for system-object operations and the default RADOS core implementation.

Important APIs, types, and functions: `RGWSI_SysObj_Core` derives from `RGWServiceInstance`, owns RADOS and zone pointers, provides `core_init()`, object resolution, virtual raw/stat/read/write/remove/attr/omap/notify/list operations, and `get_zone_svc()`.

Control flow: `RGWSI_SysObj` facade calls these protected virtual methods. Cached backends override selected methods and call base core on misses or after cache handling.

State and persistence: The core stores only dependency pointers. Persistent state is owned by backend RADOS operations.

Dependencies and integration points: Depends on sysobj facade and core type headers, RGW service base, RADOS, and zone service.

Risks and test signals: The virtual interface is broad, so derived classes must preserve version tracker and error semantics. Tests should run shared sysobj behavior against both core and cached implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core_types.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core_types.h

Purpose: Defines backend-specific state structures used by `RGWSI_SysObj_Core` operations.

Important APIs, types, and functions: `RGWSI_SysObj_Core_GetObjState` extends the generic object read state with cached `rgw_rados_ref`, `has_rados_obj`, and `last_ver`, plus `get_rados_obj()`. `RGWSI_SysObj_Core_PoolListImplInfo` extends pool-list state with `librados::IoCtx`, `rgw::AccessListFilter`, and marker.

Control flow: Read operations keep a core get-state object inside `static_ptr`; pool list operations keep list context inside `static_ptr`.

State and persistence: These structures are transient per-operation/per-list state. They do not own persistent data.

Dependencies and integration points: Depends on RGW RADOS tools, service base, sysobj generic state, librados, and access-list filters.

Risks and test signals: `static_ptr` sizing in `svc_sys_obj.h` must accommodate these types. Tests should compile and execute repeated reads and paginated listings that reuse the state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_types.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_types.h

Purpose: Provides generic empty base types for sysobj backend state.

Important APIs, types, and functions: `RGWSI_SysObj_Obj_GetObjState` and `RGWSI_SysObj_Pool_ListInfo` are marker/base structs.

Control flow: Concrete backend state types inherit these bases and are stored by the sysobj facade without exposing backend implementation details.

State and persistence: No owned state or persistence.

Dependencies and integration points: Depends only on RGW service base. Used by sysobj facade and core/cache backends.

Risks and test signals: Because the base types are empty, all behavior depends on correct static casting to concrete types by the active backend. Compile-time and backend integration tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_tier_rados.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_tier_rados.h

Purpose: Declares small RADOS tier helpers for multipart object naming and raw-object-to-RGW-object conversion.

Important APIs, types, and functions: `RGWMPObj` builds multipart meta object names and part object names from object id and upload id, parses meta names with `from_meta()`, exposes `get_meta()`, `get_part()`, `get_upload_id()`, `get_key()`, `clear()`, and stream output. `RGWSI_Tier_RADOS` stores a zone pointer and exposes static `raw_obj_to_obj()` for converting raw object oids back to `rgw_obj`.

Control flow: Multipart code initializes name components with `<oid>.<upload_id>.meta` and part prefixes. `raw_obj_to_obj()` finds an underscore after the bucket marker and parses the suffix as a raw object key.

State and persistence: `RGWMPObj` stores only derived strings. The object names refer to persisted RADOS multipart metadata and part objects elsewhere.

Dependencies and integration points: Depends on multipart meta suffix definitions, RGW service base, `rgw_bucket`, `rgw_raw_obj`, and `rgw_obj_key` parsing. Used by RADOS tier/object listing code.

Risks and test signals: `from_meta()` uses `int` positions from `rfind()` results, so malformed names must be tested. `raw_obj_to_obj()` depends on marker placement and raw oid format. Tests should cover multipart naming round trips, optional upload id parsing, malformed meta names, and bucket marker conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_tier_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_user.cc

Purpose: Provides the trivial constructor/destructor implementation for the abstract user service base.

Important APIs, types, and functions: `RGWSI_User::RGWSI_User(CephContext*)` forwards to `RGWServiceInstance`; `~RGWSI_User()` is empty.

Control flow: Concrete user services derive from this base and implement all persistence/index operations.

State and persistence: No state or persistence in this file.

Dependencies and integration points: Depends on `svc_user.h`. Used by `RGWSI_User_RADOS`.

Risks and test signals: Minimal risk. Compile/link tests ensure the abstract base has a definition for constructor/destructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_user.h

Purpose: Declares the abstract RGW user metadata service interface.

Important APIs, types, and functions: Static helpers map between `rgw_user` and metadata keys. Pure virtual operations cover buckets object location, metadata listing, user info read/store/remove, lookup by email/Swift/access key, and raw email index reads.

Control flow: Higher-level RGW user/account code uses this interface independent of storage backend. Concrete implementations must maintain UID records and secondary indexes consistently.

State and persistence: The base class has no persistent state. Implementations persist user info and indexes.

Dependencies and integration points: Depends on RGW service base, SAL forward declarations, `RGWMetadataLister`, `RGWUserInfo`, `RGWUID`, `RGWObjVersionTracker`, cache info, attrs, and optional yields.

Risks and test signals: Since store/remove are multi-index operations, implementations must define ordering and failure behavior. Backend tests should verify all lookup paths after create/update/remove and metadata lister filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.cc

Purpose: Implements RADOS-backed RGW user metadata storage, secondary indexes, metadata listing, chained lookup caching, account/group membership links, and mdlog completion.

Important APIs, types, and functions: `init()` wires RADOS, zone, mdlog, sysobj, and cache services. `do_start()` initializes `uinfo_cache`. `get_buckets_obj()` maps a user to `<uid>.buckets`. `UserLister` filters `.buckets` objects. `read_user_info()` reads and decodes UID records. `PutOperation` performs store preparation, primary object write, mdlog completion, secondary index writes, old index cleanup, and account/group links. Public methods implement `store_user_info()`, `remove_user_info()`, index removals, `remove_uid_index()`, `get_user_info_from_index()`, lookup by email/Swift/access key, and `read_email_index()`.

Control flow: Store first prepares a write version and checks uniqueness of active Swift keys, active S3 keys, and account display names. It writes the primary UID object containing `RGWUID` then `RGWUserInfo`, completes a user mdlog entry, writes email/key/Swift secondary indexes to link back to UID, removes stale old indexes, and updates account/group user lists. Remove deletes active key indexes, Swift indexes, email index, user buckets index or account link, group links, then UID object and mdlog entry. Lookups by secondary index read a UID object from the appropriate pool, ignore account ids that are not users, read the primary user info, then chain-cache the result using primary metadata cache info.

State and persistence: User primary records persist in `user_uid_pool`; secondary indexes persist in email, keys, and Swift pools; per-user bucket indexes use `<uid>.buckets`; account/group links use `rgwrados::users` objects; UID removals and stores write metadata log completion entries. `uinfo_cache` caches resolved user info keyed by `pool/key` and invalidates through sysobj cache chaining.

Dependencies and integration points: Depends on `RGWSI_Zone`, `RGWSI_MDLog`, `RGWSI_SysObj`, `RGWSI_SysObj_Cache`, `RGWChainedCacheImpl`, `rgw_user`, `rgw_account`, `rgwrados::account`, `rgwrados::group`, `rgwrados::users`, and metadata lister. It backs RGW authentication, admin user APIs, account membership, and metadata sync.

Risks and test signals: Store is multi-step and can leave partial secondary indexes if later operations fail. `PutOperation::set_err_msg()` appears to assign only when `err_msg` is not empty, so error message capture may be ineffective. Email lookup is case-insensitive through lowercase oids. Tests should cover duplicate active keys, Swift id conflicts, account display-name conflicts, rename/tenant mismatch, old index cleanup, group/account link updates, remove idempotence on ENOENT, chained cache invalidation, and mdlog entries on primary changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.h

Purpose: Declares the concrete RADOS-backed user service.

Important APIs, types, and functions: `RGWSI_User_RADOS` derives from `RGWSI_User`, owns a `user_info_cache_entry` chained cache, RADOS pointer, and service dependency struct. It declares helper methods for bucket object naming, secondary-index lookup, UID/index removals, lifecycle startup, and all base user service overrides.

Control flow: Service graph initializes dependencies, startup creates the chained cache, and public methods read/write/remove user metadata and resolve secondary indexes.

State and persistence: Header state is in-memory cache and service pointers. Persistent user data lives in RADOS pools selected from zone params and is maintained by implementation.

Dependencies and integration points: Depends on user base, RGW bucket header for subclass dependency, mdlog/zone/sysobj/cache services, and `RGWChainedCacheImpl`.

Risks and test signals: Friend `PutOperation` accesses internals, so store logic is tightly coupled to the class state. Tests should verify all virtual user service operations through a `RGWSI_User*` reference and cache behavior through secondary lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_zone.cc

Purpose: Implements RGW zone service startup, period/local zonegroup initialization, sync-policy handler construction, REST connection maps, zone relationship queries, system object listing helpers, and bucket placement selection.

Important APIs, types, and functions: Constructor stores config store and site config. `init()` allocates realm, zonegroup, zone public config, zone params, and current period. `do_start()` loads site config, initializes zonegroup from period or local config, starts sync modules, builds policy handlers and connection maps, and records zone capabilities. Listing methods enumerate regions, zonegroups, zones, realms, and periods. `init_zg_from_period()` and `init_zg_from_local()` establish master connections and repair single-zone missing master_zone config. Accessors include `get_zone_params()`, `get_zone()`, `get_zonegroup()`, `get_realm()`, `get_current_period()`, `get_zone_short_id()`, and connection lookup methods. Policy and sync helpers include `zone_syncs_from()`, `need_to_sync()`, `is_meta_master()`, `need_to_log_metadata()`, `can_reshard()`, and `is_syncing_bucket_meta()`. Placement helpers include `select_new_bucket_location()`, `select_bucket_location_by_rule()`, and `select_bucket_placement()`.

Control flow: Startup starts sysobj, copies realm/period/zonegroup/zone/zone params from `SiteConfig`, chooses period or local initialization, reads period config if needed, computes zone short id, builds per-zone bucket sync policy handlers, reflects local sync policy to discover source/target zones, starts sync modules, reads tier capabilities, indexes zones by id/name, and creates `RGWRESTConn` objects for remote zones and zonegroups. Placement selection follows request rule, then user default, then zonegroup default; verifies user tags; resolves storage class; then checks local zone placement pools.

State and persistence: The service owns heap-allocated copies of realm, zonegroup, zone config, zone params, and current period plus in-memory connection maps and sync policy handlers. Persistent configuration is read through `SiteConfig`/config store and system objects. `init_zg_from_period()` may persist repaired zonegroup master_zone values.

Dependencies and integration points: Depends on sysobj, sync modules, bucket sync, config store, `RGWRESTConn`, `RGWBucketSyncPolicyHandler`, period/realm/zone classes, sync module manager, and RGW placement types. It is a core dependency for most RGW services.

Risks and test signals: Startup is order-sensitive and allocates/deletes raw pointers. Missing endpoints prevent remote connections. Missing tier modules or absent local zone in zonegroup can break startup or reduce sync. Placement errors must match S3 location constraints. Tests should cover period and no-period configurations, single-zone master repair, multi-zone source/target maps, invalid tier types, redirect endpoints, placement rule priority/tag/storage-class validation, reshard capability decisions, and shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_zone.h

Purpose: Declares RGW's central zone/period configuration service.

Important APIs, types, and functions: `RGWSI_Zone` derives from `RGWServiceInstance`, stores sysobj/RADOS/sync/bucket-sync dependencies, realm/zonegroup/zone/zone_params/current_period objects, zone ids, capability flags, sync policy handlers, REST connection maps, zone indexes, sync policy, config store, and site config. Public API exposes configuration accessors, sync policy handler lookup, zone id/name helpers, sync/write/logging capability queries, connection maps, placement selection, and metadata listing.

Control flow: The service is initialized by the service graph, started early, and then queried by nearly every other RGW service for pool locations, sync relationships, placement decisions, and remote REST connections.

State and persistence: In-memory loaded site/period configuration and connection maps are declared here. Persistent state lives in RGW zone/period system objects and config store.

Dependencies and integration points: Depends on RGW service base, sysobj, sync modules, bucket sync, realm/zone/period types, sync policy info, REST connections, and SAL config store.

Risks and test signals: Raw pointer ownership makes startup/shutdown paths important. Tests should verify getters are valid after start, connection maps are stable, and absent optional realm/period cases behave correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.cc

Purpose: Implements utility functions for RGW host ids, unique ids, and Swift-compatible transaction ids.

Important APIs, types, and functions: `do_start()` initializes transaction id suffix dependencies. `gen_host_id()` returns `<rados instance>-<zone name>-<zonegroup name>`. `unique_id()` returns `<zone id>.<rados instance>.<unique_num>`. `init_unique_trans_id_deps()` URL-encodes a suffix of instance id and zone name. `unique_trans_id()` formats `tx%021llx-%010llx` from a unique number and current timestamp and appends the suffix.

Control flow: Startup precomputes suffix. Runtime calls format identifiers using RADOS instance id and zone service config.

State and persistence: Only `trans_id_suffix` is stored in memory. No persistent state is modified.

Dependencies and integration points: Depends on RADOS instance id, `RGWSI_Zone`, `url_encode()`, fmt formatting, and Swift API transaction id compatibility requirements.

Risks and test signals: Uses `time(NULL)` and caller-supplied uniqueness, so uniqueness depends on the caller's counter. Tests should verify transaction id format, URL-encoded suffix, and stability across zone names with special characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.h

Purpose: Declares zone utility service for generating identifiers.

Important APIs, types, and functions: `RGWSI_ZoneUtils` derives from `RGWServiceInstance`, stores RADOS and zone pointers plus `trans_id_suffix`, and declares `gen_host_id()`, `unique_id()`, and `unique_trans_id()`.

Control flow: Service graph initializes RADOS/zone dependencies, startup computes suffix, and request paths use the generated ids.

State and persistence: In-memory suffix only; no persistence.

Dependencies and integration points: Depends on RGW service base, RADOS pointer, and zone service.

Risks and test signals: Null dependencies before startup are the main local risk. Unit tests can validate formatting against fixed fake instance/zone data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_zone_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc64.c -->
# sources/distributed-fs/ceph/src/rgw/spdk/crc64.c

Purpose: Provides SPDK-compatible CRC-64 Rocksoft/NVMe checksum implementation for RGW.

Important APIs, types, and functions: Public `spdk_crc64_nvme(const void *buf, size_t len, uint64_t crc)` is implemented either by ISA-L `crc64_rocksoft_refl()` when `SPDK_CONFIG_ISAL` is defined or by local table-driven fallback. The fallback uses `crc64_rocksoft_refl_table[256]` and `crc64_rocksoft_refl_base()`.

Control flow: Compile-time configuration selects ISA-L or fallback. Fallback complements the seed, iterates bytes, updates CRC using table lookup of low CRC byte xor input byte and right shift, then returns complemented CRC.

State and persistence: The only state is a static constant lookup table. No persistence.

Dependencies and integration points: Depends on `crc_internal.h`, `crc64.h`, optional ISA-L `crc64.h`, and standard integer types. Used by RGW code needing NVMe protection information CRC compatibility.

Risks and test signals: Hardware/library and fallback paths must produce identical output. Tests should include known CRC-64 Rocksoft vectors, incremental CRC updates, empty buffers, unaligned buffers, and builds with and without ISA-L.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc64.h -->
# sources/distributed-fs/ceph/src/rgw/spdk/crc64.h

Purpose: Declares the SPDK CRC-64 NVMe checksum API.

Important APIs, types, and functions: Exposes C-linkage `uint64_t spdk_crc64_nvme(const void *buf, size_t len, uint64_t crc)`.

Control flow: C and C++ callers include this header and pass a buffer, length, and previous CRC seed for one-shot or incremental checksum calculation.

State and persistence: No state or persistence.

Dependencies and integration points: Includes standard integer and size types directly in this Ceph copy, with original SPDK config includes disabled by `#if 0`. Used by `crc64.c` and any RGW checksum callers.

Risks and test signals: API compatibility with upstream SPDK matters. Compile tests should include both C and C++ callers; checksum tests should validate incremental use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc_internal.h -->
# sources/distributed-fs/ceph/src/rgw/spdk/crc_internal.h

Purpose: Provides compile-time feature detection for optional CRC acceleration backends in the vendored SPDK CRC code.

Important APIs, types, and functions: Defines `SPDK_HAVE_ISAL` when `SPDK_CONFIG_ISAL` is set, `SPDK_HAVE_ARM_CRC` on ARMv8 CRC-capable builds, and `SPDK_HAVE_SSE4_2` on x86_64 SSE4.2 builds. It includes the associated ISA-L, ARM ACLE, or x86 intrinsics headers.

Control flow: Included before CRC implementation code so compile-time macros select optimized or fallback implementations.

State and persistence: No state or persistence.

Dependencies and integration points: Depends on compiler target macros and optional external ISA-L headers. Original SPDK config include is disabled in this local copy.

Risks and test signals: Incorrect feature macros can break cross-compiles or include unavailable intrinsic headers. Build matrix should cover x86_64, aarch64, ISA-L enabled/disabled, and fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/spdk/crc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/Makefile.am -->
# sources/distributed-fs/coda/coda-src/Makefile.am

Purpose: Top-level Automake subdirectory list for the Coda source tree.

Important APIs, types, and functions: Declares `SUBDIRS` including scripts, kernel dependency helpers, utilities, RPC definitions, directory/access-list/auth/volume/venus/vice/update/resolution/tooling modules, monitors, and launchers.

Control flow: Automake descends into subdirectories in the listed order when generating and running recursive build targets.

State and persistence: No runtime state. Build outputs are generated by subdirectory makefiles.

Dependencies and integration points: Integrates all Coda `coda-src` components into the build system. Ordering matters where libraries are built before consumers.

Risks and test signals: Missing or misordered subdirectories can break recursive builds. Test signal is successful `autoreconf`/configure and recursive `make` over the Coda source tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/Makefile.am -->
# sources/distributed-fs/coda/coda-src/al/Makefile.am

Purpose: Automake definition for Coda's access-list/protection database support library and `pdbtool`.

Important APIs, types, and functions: Under `BUILD_SERVER`, builds `libal.la`, installs/declares `pdbtool` as an sbin program, and distributes `pdbtool.8`. Headers include `al.h`, `prs.h`, `pdb.h`, and `pdbarray.h`. Library sources include `pdbdb.c`, `pdbpack.c`, `alprocs.c`, `pdb.c`, `pdbprofile.c`, and `pdbarray.c`, with `pdbdb.c` and `pdbpack.c` listed twice. `AM_CPPFLAGS` adds RPC2, base, rwcdb, and util include paths. `LDADD` links local libal, util, rwcdb, base, readline, and termcap.

Control flow: Server builds compile the internal access-list library and pdb management tool; non-server builds still expose header lists but do not build the server-only artifacts.

State and persistence: No runtime state here. The compiled library/tool operate on Coda protection database state elsewhere.

Dependencies and integration points: Integrates access-list code with util, base, rwcdb, RPC2, readline, and termcap libraries. `pdbtool` is the administrative interface to protection database data.

Risks and test signals: Duplicate source entries may cause redundant compilation or Automake warnings depending on toolchain. Conditional build paths should be tested with `BUILD_SERVER` enabled and disabled. Link tests should validate readline/termcap and internal library ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/al.h -->
# sources/distributed-fs/coda/coda-src/al/al.h

Purpose: Declares Coda access-list data structures and the access-list/protection-set API used by VICE/server code.

Important APIs, types, and functions: Defines `AL_VERSION`, `AL_AccessEntry` with internal id and rights mask, `AL_AccessList` with serialized size/version/counts and flexible `ActualEntries`, `AL_MAXEXTENTRIES`, `AL_ExternalAccessList`, global `AL_MaxExtEntries`, and `AL_DebugLevel`. Public functions allocate/free and byte-swap access lists and CPS objects, externalize/internalize ACLs, check rights against a CPS, initialize the library, map names to ids and ids to names, fetch internal/external CPS, test membership, print ACLs, enable/disable groups, and compare plus/minus entries.

Control flow: Callers initialize the AL library, convert external text ACLs to internal `AL_AccessList`, convert host/network byte order for storage, obtain CPS membership for users/groups, and call `AL_CheckRights()` to compute effective rights. Plus entries grant rights and minus entries remove rights according to comparator/order semantics implemented elsewhere.

State and persistence: `AL_AccessList` is the on-secondary-storage format for VICE ACLs. `AL_ExternalAccessList` is a textual format with plus/minus counts and name/right lines. Global limits and debug level influence parsing/allocation behavior.

Dependencies and integration points: Depends on `PRS_InternalCPS` and `PRS_ExternalCPS` from `prs.h` included by users of this header or related code. Integrates with Coda protection database name/id lookup and VICE ACL enforcement.

Risks and test signals: The one-element trailing array requires careful allocation by `AL_NewAlist()`. External ACL parsing depends on `AL_MaxExtEntries` and exact text format. Byte-order conversion is required before/after storage. Tests should cover ACL allocation sizes, external/internal round trips, network byte order conversion, rights computation with plus and minus entries, group enable/disable membership, and name/id lookup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/al/al.h -->
