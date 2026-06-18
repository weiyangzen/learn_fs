# subset-b-006975 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rados.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rados.h

## Purpose
This header is the central RADOS-backed RGW storage surface. It declares `RGWRados`, the object and bucket helper classes nested under it, serialized helper structs, raw object state caches, bucket index accessors, background service ownership, and integration hooks used by the RADOS SAL driver. Most implementation lives in companion `.cc` files; this file defines the API contract that object I/O, bucket index mutation, lifecycle, GC, sync, quota, restore, and reshard code depend on.

## Important APIs, Types, And Functions
- `RGWOLHInfo`, `RGWOLHPendingInfo`, and `objexp_hint_entry` are encoded metadata records for object-logical-head tracking and object expiration hints. They expose `encode()`, `decode()`, `dump()`, and `generate_test_instances()`, which signals Ceph's usual encode/decode compatibility tests.
- `RGWUsageBatch` aggregates `rgw_usage_log_entry` values by `ceph::real_time` and reports whether a timestamp was newly accounted.
- `RGWFetchObjFilter` and `RGWFetchObjFilter_Default` allow copy/fetch paths to adjust destination owner and placement rule based on source object attributes.
- `RGWObjectCtx` is a non-copyable, non-movable per-request object-state cache keyed by `rgw_obj`. It stores `RGWObjStateManifest`, exposes atomic/compressed/prefetch flags, and has explicit invalidation.
- `RGWRawObjState`, `RGWPoolIterCtx`, and `RGWListRawObjsCtx` hold raw RADOS state and pool iteration cursors.
- `RGWRados` owns pool IoCtxs, core services (`RGWServices`, `RGWCtl`), background workers, caches, sync managers, and the RADOS object API. It exposes initialization/finalization, service map updates, raw pool listing, log usage, bucket creation/deletion, object stat/read/write/delete/copy/transition/restore, bucket index operations, OLH repair/update, GC/lifecycle/quota/reshard helpers, and async object removal.
- Nested `RGWRados::Object::{Read,Write,Delete,Stat}` packages per-object I/O parameters and result state. Nested `RGWRados::Bucket::{UpdateIndex,List}` packages bucket index mutation and listing behavior.
- `get_obj_data` coordinates asynchronous object read completions, client callbacks, optional D3N cache write bypass, cancellation, and drain/flush sequencing.

## Control Flow
Callers initialize the store through `init_begin()`, `init_svc()`, `init_rados()`, and `init_complete()`, then use the exposed helpers through the RADOS SAL driver. Object flow typically starts with `RGWObjectCtx` and `RGWRados::Object`, resolves bucket shard and manifest state, applies preconditions, then drives `Read`, `Write`, `Delete`, or `Stat`. Bucket mutation flows through `Bucket::UpdateIndex::prepare()`, `complete()`, `complete_del()`, or `cancel()`, with `guard_reshard()` and `block_while_resharding()` protecting index operations while resharding is active. Listing flow chooses ordered or unordered listing based on `List::Params::allow_unordered`, then uses cls bucket list APIs and stores the next marker.

## State And Persistence Behavior
The class persists almost all RGW metadata through RADOS pools and cls helpers. It owns IoCtxs for root, GC, lifecycle, restore, object expiration, reshard, notification, and logging pools. Object state is cached in `RGWObjectCtx`, bucket metadata may be cached through chained caches, tombstones use an LRU map, and bucket topics have a separate cache. Persistent bucket instance state is read/written by `get_bucket_instance_info()`, `put_bucket_instance_info()`, `put_linked_bucket_info()`, and bucket entry name helpers. Bucket index entries and bilog records are maintained with `cls_obj_prepare_op()`, `cls_obj_complete_*()`, `bi_*()` functions, and OLH helpers. The API also exposes data/log sync wakeups and reshard queue integration, so bucket layout and log-generation metadata are part of the persistent contract.

## Dependencies And Integration Points
This header depends on librados, cls rgw/version/log/timeindex/otp types, RGW metadata, quota, log, sync, restore, cache, pubsub, SAL, and service headers. It friends GC, notifiers, expirer, sync processors, resharding, bucket index locking, serializers, and `rgw::sal::RadosStore`, showing that it is a low-level integration hub rather than an isolated abstraction. It also integrates with D3N data cache, neorados restore context, Ceph timers, async context pools, and trace contexts.

## Risks And Edge Cases
The API surface is large and has many cross-module invariants: object manifest state must match bucket index accounting, OLH updates must be idempotent across versioning modes, reshard guards must prevent writes to the wrong shard generation, and async read/delete paths must drain completions without leaking or double-accounting. The raw-state copy constructor intentionally omits `attrset` copying, so code assuming full state copies could be wrong. The file also contains many optional-yield paths; callers must preserve coroutine/blocking semantics. Misuse of `force`, `skip_olh_obj_update`, or `log_op` can leave index, bilog, or sync state inconsistent.

## Test Signals
The encoded helper structs provide `generate_test_instances()`, which supports Ceph encode/decode compatibility tests. High-value tests should cover bucket index prepare/complete/cancel, versioned delete and OLH repair, reshard guard behavior, ordered and unordered listing markers, quota accounting, raw object stat/listing, GC deferral, object copy attribute modes, and async read drain/cancel with and without D3N data cache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_reshard.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_reshard.cc

## Purpose
This file implements dynamic and administrator-triggered bucket index resharding for the RADOS RGW backend. It calculates preferred shard counts, prepares new index generations, copies or replays bucket index entries into target shards, updates bucket layout metadata, maintains a reshard queue in RADOS objects, and runs the background reshard worker.

## Important APIs, Types, And Functions
- `RGWBucketReshard::calculate_preferred_shards()` decides whether expansion or reduction is needed based on object count, current shard count, max/min objects per shard, multisite multiplier, layout minimums, and optional prime shard preference.
- `BucketReshardShard` batches entries for one target shard, tracks category stats, writes cls operations asynchronously, and waits for completions.
- `BucketReshardManager` owns all target shards for a target layout and flushes/waits them as a unit.
- `init_target_index()`, `init_target_layout()`, `revert_target_layout()`, `init_reshard()`, `change_reshard_state()`, `cancel_reshard()`, `commit_target_layout()`, and `commit_reshard()` form the persistent reshard state machine.
- `RGWBucketReshardLock` wraps cls lock acquisition, release, and renewal over the reshard pool.
- `RGWBucketReshard::reshard_process()`, `do_reshard()`, and `execute()` implement the actual migration.
- `RGWReshard::{add,update,list,get,remove,process_entry,process_single_logshard,process_all_logshards}` implement the persistent queue and worker processing.
- `RGWReshardWait` provides blocking or coroutine-aware waits that can be canceled on shutdown.

## Control Flow
Dynamic shard calculation first determines whether expansion or reduction is warranted. Queue insertion hashes tenant and bucket name to a reshard log shard object. The background worker scans every log shard under a log-shard lock, lists queue entries, and calls `process_entry()`. Entry processing reloads current bucket info, drops stale queue records, performs extra safety checks for dynamic reductions, enforces multisite bilog-history limits, then constructs `RGWBucketReshard` and calls `execute()`.

`execute()` takes the bucket lock, optionally updates the queue entry initiator, calls `init_reshard()` to create target index objects and write target layout metadata, performs migration, and commits. If logrecord is supported, migration has two phases: `InLogrecord` copies the inventory while client writes record reshard log entries, then `change_reshard_state()` switches to `InProgress` to block writes and `reshard_process()` replays incremental records. If logrecord is unsupported, writes are blocked first and the inventory is copied once. Commit promotes `target_index` to `current_index`, appends a new log layout, optionally writes datalog entries for old shards, and deletes old index objects when no retained bilog layout references them.

## State And Persistence Behavior
Persistent state is split across bucket instance metadata, bucket index shard objects, reshard pool queue objects, cls lock objects, bucket index reshard status, reshard log entries, and data/bucket log layouts. `init_target_layout()` writes `layout.target_index`, increments the generation, and sets `layout.resharding` to either `InLogrecord` or `InProgress`. `revert_target_layout()` removes target index objects, trims reshard log entries, and clears target metadata. `commit_reshard()` writes the new current layout and cleans old index state only after commit. Many metadata updates retry `-ECANCELED` races up to ten times by rereading bucket info and checking that the expected current layout remains unchanged.

## Dependencies And Integration Points
The implementation depends on bucket index services (`svc()->bi`, `svc()->bi_rados`, `svc()->bilog_rados`), datalog service, zone service, `RGWRados` bucket info/index helpers, cls rgw client operations, cls lock client, Ceph config values, and `RadosStore`. It integrates with multisite sync through bilog history and datalog wakeup entries, and with fault injection through `ReshardFaultInjector` keys such as `init_index`, `set_target_layout`, `trim_reshard_log_entries`, `change_reshard_state`, `block_writes`, `commit_target_layout`, and `do_reshard`.

## Risks And Edge Cases
Resharding is sensitive to races with bucket metadata writes, expired locks, partial target index creation, and logrecord feature support. Errors during commit can leave writes unblocked but target metadata still present if cleanup also fails. Dynamic reduction deliberately waits and rechecks stats to avoid oscillation; changing config can drop queued reductions. Multisite buckets cannot reshard when retained log history is already too deep. `process_single_logshard()` ignores the return value of `process_entry()`, so one failing bucket does not stop the shard scan. Old bogus OLH entries with empty names are filtered during migration.

## Test Signals
Strong tests should cover prime shard selection, expansion and reduction thresholds, logrecord-supported and fallback block-reshard paths, injected failures at every state transition, retry behavior on `-ECANCELED`, cleanup of stale target layouts, lock renewal under long migrations, dynamic reduction wait logic, multisite bilog-history refusal, stale queue cleanup, and preservation of bucket stats and markers across source and target shards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_reshard.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_reshard.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_reshard.h

## Purpose
This header declares the RADOS RGW bucket resharding interfaces. It separates per-bucket reshard execution, the persistent reshard queue processor, and a wait helper used by callers that must pause while resharding blocks index access.

## Important APIs, Types, And Functions
- `ReshardFaultInjector` is a `FaultInjector<std::string_view>` used to force specific state-machine failures.
- `RGWBucketReshardLock` stores a `RadosStore`, lock oid, ephemeral flag, cls lock object, duration, start time, and renew threshold. Its public API is `lock()`, `unlock()`, `renew()`, and `should_renew()`.
- `RGWBucketReshard` exposes `execute()`, `get_status()`, `cancel()`, `renew_lock_if_needed()`, `clear_resharding()`, prime-shard helpers, `calculate_preferred_shards()`, and `should_zone_reshard_now()`. Private helpers calculate target shard assignment and process source entries.
- `RGWReshard` exposes queue operations (`add`, `update`, `get`, `remove`, `list`) and processor operations (`process_entry`, `process_single_logshard`, `process_all_logshards`, `start_processor`, `stop_processor`).
- `RGWReshard::ReshardWorker` is a `Thread` and `DoutPrefixProvider` wrapper around periodic queue scans.
- `RGWReshardWait` supports blocking and coroutine waits with stop-time cancellation.

## Control Flow
Callers create `RGWBucketReshard` for an already loaded bucket and call `execute()` with a target shard count, fault injector, max entries per operation, and initiator. Background resharding is driven through `RGWReshard`, which hashes bucket names into queue shards and processes them under locks. Code that encounters an active reshard can use `RGWReshardWait::wait()` to delay and retry, and shutdown calls `stop()` to wake all waiters.

## State And Persistence Behavior
The header identifies the objects whose state is persisted by implementation: bucket layout and attrs inside `RGWBucketInfo`, cls lock records in the reshard pool, queue entries of type `cls_rgw_reshard_entry`, bucket instance reshard status entries, and retained log generations. `RGWBucketReshard::max_bilog_history` caps retained old log generations for multisite safety.

## Dependencies And Integration Points
The declarations depend on librados, cls rgw types, cls lock client, Ceph time/yield, intrusive lists, Boost.Asio timers, fault injection, `RGWBucketInfo`, and `rgw::sal::RadosStore`. They are consumed by the RADOS store, bucket index guard paths, admin operations, and background service initialization.

## Risks And Edge Cases
The destructor of `RGWReshardWait` asserts that `stop()` was called, so lifecycle ordering matters. Lock duration and renewal thresholds must align with long-running copy batches. The prime helper list is finite and returns zero for requests above the supported max when asking for greater-or-equal, so callers must handle fallback. Queue processing and per-bucket resharding share lock renewal assumptions; outer lock duration must be at least as long as the bucket lock duration.

## Test Signals
Tests should instantiate prime helper edge cases, lock renewal threshold behavior, queue shard oid hashing stability, `RGWReshardWait` cancellation for coroutine and blocking callers, public cancel behavior for non-resharding buckets, and compile-time coverage of the worker thread prefix/cct/subsys methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_reshard.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_bucket.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_bucket.cc

## Purpose
This file implements RADOS-backed RGW admin REST operations for bucket management. It translates `/admin/bucket` HTTP methods and subresources into `RGWBucketAdminOp` calls, parses request arguments into `RGWBucketAdminOpState`, enforces bucket caps, and handles master-zone forwarding for selected metadata mutations.

## Important APIs, Types, And Functions
- `RGWOp_Bucket_Info` reads bucket information and optional stats/restore stats.
- `RGWOp_Get_Policy` reads bucket or object policy.
- `RGWOp_Check_Bucket_Index` checks or repairs bucket index state and optionally checks objects.
- `RGWOp_Bucket_Link` and `RGWOp_Bucket_Unlink` link/unlink buckets to users or accounts, forwarding to the master first.
- `RGWOp_Bucket_Remove` removes buckets, supports purge and bypass-GC flags, and maps `-ENOENT` to `-ERR_NO_SUCH_BUCKET`.
- `RGWOp_Set_Bucket_Quota` sets per-bucket quota from JSON body, chunked fallback, or HTTP args.
- `RGWOp_Sync_Bucket` toggles bucket sync.
- `RGWOp_Object_Remove` removes one object through bucket admin code.
- `RGWHandler_Bucket::{op_get,op_put,op_post,op_delete}` routes methods and subresources.

## Control Flow
GET dispatches to policy, index check, or bucket info. PUT dispatches to quota, sync, or link. POST unlinks. DELETE removes an object when `object` subresource is present, otherwise removes a bucket. Each operation parses strings/bools/integers from `RESTArgs`, fills `RGWBucketAdminOpState`, and invokes the corresponding admin operation on `driver`. Link and unlink forward the request to the metadata master before applying local admin code. Quota setting chooses JSON input when a body or chunked transfer is present, otherwise loads the current bucket and overlays request parameters on the existing quota.

## State And Persistence Behavior
The file itself does not write RADOS directly; persistence is delegated to `RGWBucketAdminOp` and the SAL driver. The operations can mutate bucket-user/account links, bucket instance metadata, bucket quota fields, bucket sync state, bucket index repair state, object index/data state, and GC scheduling depending on flags. Forwarded requests use site metadata-master logic to keep multisite metadata authoritative.

## Dependencies And Integration Points
It depends on `rgw_op.h`, `driver/rados/rgw_bucket.h`, `rgw_process_env.h`, `rgw_rest_bucket.h`, SAL, zone service, sysobj service, and REST argument helpers. It integrates with the admin caps system through `buckets=read` and `buckets=write`, with `rgw_forward_request_to_master()`, and with `RGWFormatterFlusher` for output.

## Risks And Edge Cases
Quota setting requires both `uid` and `bucket`; missing either returns `-EINVAL`. HTTP-parameter quota updates first load current bucket quota, so load failures abort before mutation. Bucket removal treats forwarded admin requests by checking the `rgwx-zonegroup` system argument rather than only `system_request`. `bypass-gc` is powerful and can remove data without normal GC safety. Index repair can be expensive and optionally object-checking can touch object data.

## Test Signals
Endpoint tests should cover method/subresource dispatch, cap failures, missing required quota arguments, JSON quota and HTTP-argument quota paths, master forwarding failures for link/unlink, bucket removal error mapping, forwarded-zonegroup detection, index check with fix/check-objects flags, and object removal routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_bucket.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_bucket.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_bucket.h

## Purpose
This header declares the REST handler and manager for the RADOS bucket admin resource.

## Important APIs, Types, And Functions
- `RGWHandler_Bucket` derives from `RGWHandler_Auth_S3` and overrides `op_get()`, `op_put()`, `op_post()`, and `op_delete()` to select the concrete bucket admin operation implemented in `rgw_rest_bucket.cc`.
- `read_permissions()` returns zero, leaving authorization to each operation's `check_caps()`.
- `RGWRESTMgr_Bucket::get_handler()` constructs `RGWHandler_Bucket` with the configured auth registry.

## Control Flow
The REST manager is registered for an admin bucket resource. On each request it creates a handler, the handler reads method and subresource state from `req_state`, and the selected `RGWRESTOp` parses arguments and executes.

## State And Persistence Behavior
This file has no direct persistence. It controls routing into operations that mutate or read bucket metadata, quotas, sync flags, bucket links, index state, and objects.

## Dependencies And Integration Points
The header depends on the generic REST framework and S3-authenticated REST handler base. It is integrated by the admin REST resource registration layer.

## Risks And Edge Cases
Returning zero from `read_permissions()` is intentional but means every new operation added to the handler must implement correct cap checks. `get_handler()` ignores the path string and driver at construction time, so operation code must rely on the base framework to attach request state and driver later.

## Test Signals
Tests should verify that each HTTP method reaches the intended operation and that operation-level cap checks are enforced despite permissive handler-level permission reading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_bucket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_log.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_log.cc

## Purpose
This file implements admin REST operations for RGW metadata logs, bucket index logs, and data change logs. It supports listing, info, shard info, trimming, locking/unlocking metadata log shards, notify wakeups, and sync status reads for multisite replication.

## Important APIs, Types, And Functions
- Metadata log operations: `RGWOp_MDLog_List`, `Info`, `ShardInfo`, `Delete`, `Lock`, `Unlock`, `Notify`, and internal `Status`.
- Bucket index log operations: `RGWOp_BILog_List`, `Info`, `Delete`, and internal `Status`.
- Data log operations: `RGWOp_DATALog_List`, `Info`, `ShardInfo`, `Delete`, `Notify`, `Notify2`, and internal `Status`.
- `RGWHandler_Log::{op_get,op_delete,op_post}` dispatches on `type=metadata`, `type=bucket-index`, or `type=data`, plus `id`, `info`, `status`, `lock`, `unlock`, `notify`, and `notify2` arguments.

## Control Flow
Metadata list/info/shard-info build `RGWMetadataLog` for the requested or current period and operate on a parsed shard id. Metadata delete trims to a marker and rejects legacy `start-time`, `end-time`, and `start-marker`; `end-marker` is accepted only when `marker` is absent. Metadata lock/unlock require period, shard id, duration or locker id, and zone id. Metadata notify reads up to 128 KiB of JSON, decodes updated shard ids, and wakes metadata sync shards.

Bucket-index log list loads a bucket by name or bucket instance, selects a log generation, streams the response header early, lists bilog entries until truncated or max count, and optionally emits version-2 metadata about truncation and the next log. Bilog info reads bucket stats against the latest log-derived index and returns retained generations. Bilog delete trims by generation, shard id, and marker range. Bilog status reads full and incremental bucket sync status for one pipe, or merges status across all local destinations when `options=merge`.

Data log list parses shard id and max entries, uses coroutine wrappers to list entries and read shard info, and returns marker, last update, truncation, and entries. Data notify variants decode updated shard maps and wake data sync shards. Data delete trims entries to a marker.

## State And Persistence Behavior
The operations read and mutate log objects stored in RADOS through metadata log services, bilog RADOS service, and datalog RADOS service. Trim operations permanently advance log retention markers. Lock/unlock stores cls lock state on mdlog shards. Notify operations do not persist log data directly but trigger in-memory sync processors via `driver->wakeup_meta_sync_shards()` and `driver->wakeup_data_sync_shards()`. Status operations read persistent sync status objects maintained by metadata and data sync managers.

## Dependencies And Integration Points
This file depends on JSON helpers, strict numeric parsing, async coroutine utilities, RGW sync and data sync types, mdlog and bilog services, datalog notify decoders, bucket parsing helpers, and SAL `RadosStore`. It integrates with multisite period history, bucket sync policy handlers, full and incremental bucket sync status helpers, and admin caps: `mdlog`, `bilog`, and `datalog` read/write.

## Risks And Edge Cases
Many endpoints parse numeric shard ids from free-form strings and return `-EINVAL` on parse errors. Several legacy time and marker parameters are rejected to avoid ambiguous trims. `RGWOp_DATALog_List::execute()` assigns `op_ret` after listing, then overwrites it with `get_info()`; a get-info failure can hide successful listing, and a list failure may still be followed by info read. Streaming bilog list sends headers before all list calls finish, so later list errors cannot be represented as a normal error response. Merge status requires equal shard counts across destinations or returns `-EINVAL`. Notify bodies are capped at 128 KiB.

## Test Signals
Tests should cover dispatch by `type`, cap enforcement, shard/max parsing errors, current-period fallback, legacy parameter rejection, mdlog lock busy mapping to `-ERR_LOCKED`, bilog generation selection and next-log response, streaming bilog truncation, bilog trim marker validation, data notify JSON v1 and notify2 formats, sync status merge with mismatched shard counts, and status behavior when sync managers are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_log.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_log.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_log.h

## Purpose
This header declares the admin REST operation classes for RGW metadata, bucket index, and data logs, plus the REST handler and manager that dispatch log requests.

## Important APIs, Types, And Functions
- `RGWOp_BILog_List`, `Info`, and `Delete` expose bucket-index log list/info/trim behavior and require `bilog` read or write caps.
- `RGWOp_MDLog_List`, `Info`, `ShardInfo`, `Lock`, `Unlock`, `Notify`, and `Delete` expose metadata-log operations and require `mdlog` caps.
- `RGWOp_DATALog_List`, `Info`, `ShardInfo`, `Notify`, `Notify2`, and `Delete` expose data-log operations and require `datalog` caps.
- `RGWHandler_Log` routes GET, DELETE, and POST to the correct log operation and lets each operation enforce permissions.
- `RGWRESTMgr_Log::get_handler()` constructs the authenticated log handler.

## Control Flow
The classes store response state such as entries, markers, truncation flags, log info, notify payloads, and sync format version. Concrete `execute()` and `send_response()` implementations in `rgw_rest_log.cc` parse request arguments, call the relevant service, and serialize JSON responses.

## State And Persistence Behavior
The header itself does not persist state, but the declared operations map to persistent mdlog, bilog, datalog, log-lock, and sync-status objects. Notify operations affect in-memory sync scheduling rather than direct persistence.

## Dependencies And Integration Points
It depends on datalog, REST/S3 auth, metadata, mdlog, and data sync headers. It is intentionally lighter than the `.cc` for some status operations, which are declared locally in the implementation to avoid pulling heavier sync headers into this header.

## Risks And Edge Cases
The operation classes expose `verify_permission()` methods that directly call caps on `s->user`; tests must ensure `s->user` is initialized for all log routes. Adding new routes requires matching both handler dispatch and cap checks. `RGWOp_BILog_List` maintains streaming response state (`sent_header`), so response methods must be called in the expected order.

## Test Signals
Header-level coverage should compile all operation classes, verify their `name()` strings and operation types for notify operations, and exercise handler dispatch through the public method overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_realm.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_realm.cc

## Purpose
This file implements admin REST operations for realms and periods in the RADOS-backed RGW configuration store. It supports reading realms, listing realms, reading periods, committing periods on the master, accepting period pushes from other zones, updating local period history, and notifying the realm after successful period changes.

## Important APIs, Types, And Functions
- `RGWOp_Period_Base` centralizes period JSON response and error-stream reporting.
- `RGWOp_Period_Get` reads a period from the config store.
- `RGWOp_Period_Post` decodes a submitted period, commits new periods, accepts pushed period epochs, updates latest epoch/current period, reflects period data, and triggers realm notification.
- `RGWHandler_Period` and `RGWRESTMgr_Period` route `/admin/realm/period`.
- `RGWOp_Realm_Get` reads one realm by id or name.
- `RGWOp_Realm_List` reads the default realm id and lists known realms.
- `RGWHandler_Realm` and `RGWRESTMgr_Realm` route `/admin/realm` and register the `period` subresource.

## Control Flow
GET `/admin/realm/period` parses realm, period, and epoch arguments but ultimately reads by period id through `cfgstore->read_period()`. POST `/admin/realm/period` reads JSON into an `RGWPeriod`, rejects periods for a different realm, reloads the realm and current period from the config store, and then splits behavior. If the submitted period id is empty, it treats the request as a period commit and calls `rgw::commit_period()`, accepting `-EEXIST` as idempotent success. If the submitted period has an id, the current master zone rejects pushes whose master zone is itself. Otherwise it creates the period, updates latest epoch, attaches history if this is a new period id, may set the realm current period, or reflects a newer epoch of the current period into local objects. Responses are sent before `realm_notify_new_period()` to avoid racing connection closure.

## State And Persistence Behavior
Realm and period data persist in `s->penv.cfgstore`. POST can create period objects, update latest period epoch, update the realm's current period, reflect period data into local config objects, update in-memory period history, and send realm notifications. The `PERIOD_HISTORY_FETCH_MAX` limit prevents accepting period pushes too far ahead of local history, bounding how much intermediate history a receiver may need to fetch.

## Dependencies And Integration Points
This file depends on REST config, zone, RADOS SAL, config store, process environment, zone and mdlog services, realm writer helpers, period commit/reflect functions, and `RGWPeriodHistory`. Authorization uses `zone=read` for GET/list and `zone=write` for period POST.

## Risks And Edge Cases
`RGWOp_Period_Get` parses `realm_id` and `epoch` but reads only by `period_id` with no explicit epoch selection in this code path. POST handles idempotent retries for commit and latest-epoch updates, but period history gaps return errors. Pushed periods older than current are acknowledged without changing state; periods too far ahead return `-ENOENT`. Master-zone rejection uses `-EINVAL`, marked as a rough error code. Realm notification after response means state can be committed even if notification later fails.

## Test Signals
Tests should cover realm get/list, period get, commit with empty period id, idempotent `-EEXIST`, realm mismatch, master-zone push rejection, old period discard, too-far future rejection, missing intermediate period history, current-period update, same-period epoch reflection, and post-response notification triggering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_realm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_realm.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_realm.h

## Purpose
This header declares the REST manager for the RADOS RGW realm admin resource.

## Important APIs, Types, And Functions
- `RGWRESTMgr_Realm::RGWRESTMgr_Realm()` registers realm subresources such as `period`.
- `RGWRESTMgr_Realm::get_handler()` constructs the authenticated realm handler implemented in the `.cc` file.

## Control Flow
Admin REST registration instantiates this manager for `/admin/realm`. The manager creates a handler per request, and the handler selects realm get/list operations or delegates to the registered period resource.

## State And Persistence Behavior
The header has no direct state. Its implementation routes to operations that read and mutate config-store realm and period objects.

## Dependencies And Integration Points
It depends only on the generic REST manager header, keeping realm operation details in the implementation file. It integrates with the admin REST resource registry.

## Risks And Edge Cases
Because the concrete handler is hidden in the implementation, route additions require constructor registration and handler dispatch updates together. `get_handler()` ignores the frontend path string, so path validation is handled by the resource manager tree.

## Test Signals
Tests should verify manager construction registers `period`, handler creation succeeds with an auth registry, and `/admin/realm?list` versus `/admin/realm/period` dispatch remains stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_realm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_user.cc -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_user.cc

## Purpose
This file implements RADOS-backed RGW admin REST operations for users, subusers, access keys, user caps, and user/bucket quotas. It parses `/admin/user` request parameters, enforces user caps, forwards selected metadata changes to the master zone, and delegates persistent updates to user admin operation classes or `RGWUser`.

## Important APIs, Types, And Functions
- `fetch_access_keys_from_master()` forwards a request to the master and decodes returned `RGWUserInfo` keys/create date for non-master user create/modify.
- User operations: `RGWOp_User_List`, `Info`, `Create`, `Modify`, and `Remove`.
- Subuser operations: `RGWOp_Subuser_Create`, `Modify`, and `Remove`.
- Key operations: `RGWOp_Key_Create` and `Remove`.
- Capability operations: `RGWOp_Caps_Add` and `Remove`.
- `UserQuotas`, `RGWOp_Quota_Info`, and `RGWOp_Quota_Set` encode/decode and mutate quota information.
- `RGWHandler_User::{op_get,op_put,op_post,op_delete}` routes subresources to operations.

## Control Flow
GET dispatches to quota info, list, or user info. PUT dispatches to subuser create, key create, caps add, quota set, or user create. POST dispatches to subuser modify or user modify. DELETE dispatches to subuser removal, key removal, caps removal, or user removal. Each operation fills `RGWUserAdminOpState` from REST args and calls the relevant `RGWUserAdminOp_*` method or `RGWUser::modify()`.

User info requires either `uid` or `access-key`; it suppresses keys unless the caller has `users=read`, is a system request, or is admin, while `user-info-without-keys=read` can authorize keyless reads. User create/modify validate that only system users can set the system flag, parse operation masks, key type, placement, storage class, placement tags, account fields, max buckets, suspension, account-root, and generated key flags. On non-meta-master zones, create/modify fetch keys from the master and suppress local generation. Removal, subuser mutations, and cap mutations forward to the master before applying local admin operations. Key create/remove do not use the explicit forwarding path in this file.

Quota info validates `uid` and quota type, initializes `RGWUser`, confirms the user exists, and returns all, user, or bucket quota. Quota set supports JSON body for all quotas or one quota, and HTTP args for one quota type. HTTP-arg mode overlays values on current quota, including `max-size-kb` conversion to bytes, then calls `RGWUser::modify()`.

## State And Persistence Behavior
Persistent user state is held in RGW user metadata through `RGWUserAdminOp_*` and `RGWUser`. Operations can mutate user info, display name, email, access keys, subusers, Swift/S3 key types, caps, suspension, system/account-root flags, account id/path, placement preferences, max bucket limits, and quota fields. Forwarding to the master zone preserves metadata-master authority in multisite deployments; non-master create/modify also import master-generated keys to keep access credentials consistent.

## Dependencies And Integration Points
The file depends on JSON helpers, user admin code, process environment, REST user header, SAL, zone and sysobj services, string-list parsing, op-mask parsing, placement validation, and `rgw_forward_request_to_master()`. It integrates with caps categories `users` and `user-info-without-keys`, with admin identity checks, and with `RGWFormatterFlusher`.

## Risks And Edge Cases
Missing `uid` and `access-key` on user info returns `-EINVAL` to avoid accidentally querying anonymous user. `RGWOp_User_Modify` parses `op-mask` twice, which is redundant and can duplicate validation work. Non-system callers cannot set `system=true`, but other sensitive fields depend on downstream admin validation. Quota HTTP-arg mode cannot set both user and bucket quotas at once without JSON. Forward-to-master failures abort local mutations, but operations that do not forward here rely on lower layers or deployment assumptions. Key visibility is intentionally conditional and must not regress.

## Test Signals
Tests should cover method/subresource dispatch, cap checks including keyless user-info permission, key redaction rules, required uid/access-key validation, system flag rejection for non-system users, op-mask parsing failure, invalid placement rejection, non-master key fetch behavior, master forwarding failures, user/subuser/key/caps CRUD argument mapping, quota JSON and HTTP-arg modes, invalid quota types, missing users, and max-size-kb conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_user.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_user.h -->
# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_user.h

## Purpose
This header declares the REST handler and manager for the RADOS RGW user admin resource.

## Important APIs, Types, And Functions
- `RGWHandler_User` derives from `RGWHandler_Auth_S3`, overrides the HTTP method operation selectors, and returns zero from `read_permissions()`.
- `RGWRESTMgr_User::get_handler()` constructs a user handler with the auth strategy registry.

## Control Flow
The admin REST resource manager creates `RGWHandler_User` for `/admin/user` requests. The handler inspects method and subresource state, then returns the concrete operation implemented in `rgw_rest_user.cc`.

## State And Persistence Behavior
This header does not persist state. It routes to operations that read and mutate persistent user, subuser, access-key, caps, and quota metadata.

## Dependencies And Integration Points
It depends on the generic REST framework and S3-authenticated handler base. It integrates with admin REST registration and operation-level cap checks.

## Risks And Edge Cases
Like other admin handlers in this directory, permissive `read_permissions()` places responsibility on every concrete operation to implement cap checks. New subresources must be added in both the handler dispatch and implementation with correct authorization.

## Test Signals
Tests should verify handler construction, dispatch for GET/PUT/POST/DELETE subresources, and cap enforcement at the operation level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_rest_user.h -->
