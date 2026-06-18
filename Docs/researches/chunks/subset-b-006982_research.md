# sources/distributed-fs/ceph/src/rgw/radosgw-admin/radosgw-admin.cc lines 6911-12759

## Scope

This chunk covers the bulk of `radosgw-admin`'s command dispatch inside `main()`. It starts in the middle of zone placement add/modify validation, at the point where the command requires an index pool and a data pool, and continues through the final `GLOBAL_CORS_GET` handler and `main()`'s `return 0`.

The range is command-family oriented rather than abstraction oriented. It wires parsed CLI state into RGW admin operations for:

- Zone placement list/get and the tail of zone placement add/modify/remove.
- User, subuser, key, caps, role, role policy, account, quota, and rate-limit administration.
- Period update/commit/push and multisite sync, metadata log, bucket index log, data log, sync error log, sync policy, and bucket sync administration.
- Bucket/object inspection, repair, removal, rewrite, reindex, resharding, lifecycle, garbage collection, usage, and statistics operations.
- RADOS-only bucket index, OLH, log, dedup, orphan, MFA, reshard-log, persistent notification queue, and low-level metadata operations.
- Pubsub notification/topic operations, Lua script/package operations, restore status/list, and global CORS inspection.

Most branches are under `if (opt_cmd == OPT::...)` checks after a smaller `switch (opt_cmd)` handles user/role/period operations. Many sections are guarded by `#ifdef WITH_RADOSGW_RADOS` because they require direct access to RADOS-specific services below the SAL driver.

## Purpose

The purpose of this chunk is to turn an already parsed `OPT` command and its option variables into concrete RGW admin actions. It is the main imperative bridge between the `radosgw-admin` CLI and backend services such as `rgw::sal::Driver`, `RGWBucketAdminOp`, `RGWRados`, metadata managers, lifecycle processors, resharding helpers, sync managers, account helpers, IAM role/user policy helpers, pubsub helpers, Lua managers, and restore helpers.

The chunk also implements safety policy around destructive or topology-sensitive operations. Examples include refusing metadata-mutating user/account/bucket-link operations on non-master zones unless `--yes-i-really-mean-it` was supplied, requiring confirmation before global usage trim/clear, full dedup execution, inconsistent-index bucket removal, stale reshard instance inspection/deletion, or deprecated orphan search operations, and rejecting commands that require RADOS when the active driver is not a `RadosStore`.

## Important APIs, Types, and Helpers

### Shared admin state

The early part of the chunk populates reusable operation state:

- `RGWUserAdminOpState user_op` receives user id, new user id, display name, email, keys, subuser, caps, purge flags, generated key flags, max buckets, admin/system/account-root flags, permissions, temp URL keys, op mask, key type, key active flag, suspension flag, default placement, placement tags, path, and account id.
- `RGWBucketAdminOpState bucket_op` receives user id, account id, bucket name, object name, object checking flags, child deletion/fix-index flags, AIO limit, min age, key dumping/progress flags, sync-bucket flag, and quota/rate-limit context in later branches.
- `RGWUser ruser` is initialized when a user, access key, or subuser operation needs loaded user context.
- `std::unique_ptr<rgw::sal::Bucket> bucket` is repeatedly initialized by `init_bucket()` or `init_bucket_for_sync()` for bucket-scoped operations.
- `Formatter` instances (`formatter`, `zone_formatter`) and `stream_flusher` are used for JSON/XML/plain output.
- `dpp()` and `null_yield` are passed through almost every backend call for logging and coroutine/yield integration.

### User, role, account, quota, and rate-limit APIs

User operations go through `RGWUser` subcomponents:

- `ruser.add/remove/rename/modify/info()`.
- `ruser.subusers.add/modify/remove()`.
- `ruser.caps.add/remove()`.
- `ruser.keys.add/remove()`.

Role operations use the SAL role interface:

- `driver->get_role(...)`, `RGWRole::create()`, `delete_obj()`, `load_by_name()`, `load_by_id()`, `store_info()`, `update_trust_policy()`, `set_perm_policy()`, `get_role_policy()`, `delete_policy()`, `update_max_session_duration()`.
- IAM policy parsing and managed policy validation use `rgw::IAM::Policy` and `rgw::IAM::get_managed_policy()`.

Account operations use `rgw::account::AdminOpState` with `rgw::account::create()`, `modify()`, `info()`, `stats()`, `remove()`, and `list_users()`.

Quota and rate-limit operations dispatch to helper functions such as `set_bucket_quota()`, `set_user_bucket_quota()`, `set_user_quota()`, `set_bucket_ratelimit()`, `set_user_ratelimit()`, `show_bucket_ratelimit()`, and `show_user_ratelimit()`.

### Bucket, object, and storage maintenance APIs

Bucket and object administration is split between portable SAL/admin helpers and RADOS-only helpers:

- `RGWBucketAdminOp::info()`, `limit_check()`, `link()`, `unlink()`, `chown()`, `check_index()`, `check_index_olh()`, `check_index_unlinked()`, `remove_bucket()`, `fix_obj_expiry()`, `fix_lc_shards()`, `sync_bucket()`, `list_stale_instances()`, and `clear_stale_instances()`.
- `rgw::sal::Bucket::list()`, `put_info()`, `remove_objs_from_index()`, `sync_owner_stats()`, `get_object()`, `get_logging_object_name()`.
- `rgw::sal::Object::get_obj_attrs()`, `load_obj_state()`, `put()` through `RGWDataAccess`, and low-level object removal through `rgw_remove_object()`.
- `RGWRados` operations for bucket index get/put/list/purge, OLH read, object rewrite/reindex, bucket rewrite, bucket reshard, reshard queue processing, GC, access logs, bilog, datalog, and notification queues.

### Multisite and log APIs

The chunk coordinates several multisite/log managers:

- Period commands use `update_period()`, `commit_period()`, `cfgstore->read_period()`, `rgw::read_realm()`, `rgw::get_staging_period_id()`, and `send_to_remote_or_url()`.
- Metadata sync uses `RGWMetaSyncStatusManager`.
- Data sync uses `RGWDataSyncStatusManager`, sync module creation from `svc()->sync_modules`, and source-zone validation.
- Bucket pipe sync uses `RGWBucketPipeSyncStatusManager::construct()`, `init_sync_status()`, `read_sync_status()`, `run()`, and `rgw_bucket_sync_checkpoint()`.
- Metadata log operations use `RGWMetadataLog`, `svc()->mdlog`, and metadata manager log-entry dumping.
- Bucket index log operations use `svc()->bilog_rados`, `bilog_trim()`, and `rgw::BucketTrimManager`.
- Data log operations use coroutine helpers around `svc()->datalog_rados` for list/status/trim/format/prune/semaphore operations.
- Sync error log operations use `RGWSyncErrorLogger`, `svc()->cls->timelog`, and `trim_sync_error_log()`.

### Policy, pubsub, Lua, MFA, and restore APIs

Other command families are integrated through domain helpers:

- Sync policy mutations use `SyncPolicyContext`, `rgw_sync_policy_info`, `rgw_sync_policy_group`, `rgw_sync_symmetric_group`, `rgw_sync_directional_rule`, and `rgw_sync_bucket_pipes`.
- Pubsub uses `RGWPubSub`, `RGWPubSub::Bucket`, v2 helpers such as `get_bucket_notifications()`, `remove_notification_v2()`, `show_topics_info_v2()`, and persistent queue helpers under `rgw::notify`.
- Lua script/package operations use `driver->get_lua_manager()`, `rgw::lua::verify()`, `to_context()`, `write_script()`, `read_script()`, `delete_script()`, and package allowlist/reload helpers behind `WITH_RADOSGW_LUA_PACKAGES`.
- MFA/TOTP operations use `rados::cls::otp::otp_info_t`, `svc()->cls->mfa`, `ctl()->meta.mgr->mutate()`, `rgwrados::otp::get_meta_key()`, and `scan_totp()`.
- Restore operations use `driver->get_rgwrestore()->status()` and `list()`.

## Control Flow

The chunk first completes zone placement handling. Add/modify validates that an index pool and data pool are available, optionally inherits an existing storage class data pool, sets storage class data/compression, data extra pool, index type, inline-data settings, validates omap support, writes the zone, and emits JSON. Remove erases either an entire placement target or a single storage class. List/get read `RGWZoneParams` and print placement pools.

Before the general dispatcher, the code resolves zone names to ids, builds a set of operations that must run on the metadata master zone, and blocks those commands on non-master zones unless forced. It then transfers parsed option values into `user_op` and `bucket_op`, initializes `RGWUser` when required, and enters a switch for user, period, and role commands. User commands mutate users/subusers/caps/keys and optionally print resulting user info. Period commands push, update, or commit realm periods. Role commands create/delete/get/list roles, validate trust and permission policies, manage inline role policies, attach/detach/list managed policies, and update maximum session duration.

After the switch, the rest of the function is a long sequence of independent `if (opt_cmd == ...)` branches. Each branch validates required arguments, initializes the necessary bucket/user/account/backend objects, invokes one backend operation or a short loop, prints output through the formatter, and returns on fatal errors. Some branches intentionally return immediately after completion, while many fall through to the final `return 0` because only one `opt_cmd` branch should match.

The major loops are pagination loops: user/account/metadata key listing through `driver->meta_list_keys_*`, bucket object listing through `bucket->list()`, bucket index listing through shard iteration plus `bi_list()`, reshard queue listing across log shards, log listing across shards and markers, role listing with `next_marker`, pubsub topic v2 listing with `next_token`, persistent queue dumping over topic shards, and datalog/bilog/mdlog/sync-error-log listings.

## State and Persistence Behavior

This chunk has extensive persistent side effects:

- Zone placement writes persist through the zone writer into realm/zone configuration.
- User, subuser, cap, key, account, quota, rate-limit, managed policy, and MFA commands update user/account metadata objects and may write metadata log entries.
- Role creation, deletion, policy modification, managed policy attachment, and max-session changes persist role metadata.
- Period update/commit/push changes or distributes multisite period state.
- Bucket link/unlink/chown/rm/sync-bucket/quota/rate-limit operations alter bucket metadata, bucket ownership, or bucket settings.
- Bucket/object put/remove/rewrite/reindex/unlink/check/fix commands alter object data, object metadata, bucket index entries, or repair stale metadata.
- Usage trim/clear, GC process/list, lifecycle processing, dedup control, orphan search, reshard queue operations, stale instance cleanup, and log trimming operate on cluster-maintenance state in RADOS pools.
- Metadata put/remove and mdlog/datalog/bilog/sync-error trim commands directly mutate low-level multisite log or metadata objects.
- Pubsub topic/notification removal and Lua script/package operations update RGW metadata used by runtime request handling.
- Global CORS get is read-only and builds a `RGWCORSRule` from live config values.

Read-only or mostly read-only branches still expose backend state, including bucket layout/stats, object stat/manifest metadata, logs, sync status, role/user/account info, policy listings, usage, lifecycle state, pubsub topics, notification queues, and restore status.

## Dependencies and Integration Points

The chunk depends on the SAL driver abstraction for portable user, bucket, account, role, lifecycle, restore, Lua, and pubsub operations. It narrows to `rgw::sal::RadosStore` for commands that require raw RADOS services, class methods, pool ioctxs, bucket index shards, log shards, reshard internals, notification queues, or OSD-side OTP objects.

Important integration surfaces include:

- `cfgstore`, realm, period, zone, zonegroup, and sync-policy configuration for multisite control.
- Metadata log and data/bucket index log services for replication and trim operations.
- RADOS cls helpers for bucket index, GC, datalog, timelog, queue, dedup, and OTP/MFA state.
- IAM policy parsing for role trust/permission policies and managed policy validation.
- `RGWBucketAdminOp` as the main shared bucket-admin facade used by this CLI and likely by admin APIs/tests.
- `Formatter` JSON/XML output contracts consumed by operators, scripts, and tests.
- Compile-time feature gates `WITH_RADOSGW_RADOS`, `FULL_DEDUP_SUPPORT`, and `WITH_RADOSGW_LUA_PACKAGES`, which change available command behavior.

## Risks

- The dispatcher uses many sequential `if` branches with mixed positive and negative errno return conventions. Several helpers return negative errno while the CLI often returns positive shell-style errno; mistakes can invert success/failure or print misleading errors.
- Many RADOS-only branches use `static_cast<rgw::sal::RadosStore*>(driver)` after assuming compile-time RADOS support. Some commands check `dynamic_cast` or `driver->get_name()`, but others rely on earlier command filtering or deployment assumptions.
- Destructive commands are concentrated here: bucket removal, object removal, bucket index purge, usage clear/trim, metadata remove/put, log trim, stale instance deletion, GC processing, dedup execution, Lua package changes, MFA updates, and pubsub removal. Missing confirmation or master-zone checks can cause data loss or multisite divergence.
- Multisite commands are sensitive to period ids, source/destination zones, bucket sync policy, mdlog/bilog/datalog markers, and shard ids. Incorrect markers or trims can break replication catch-up or hide diagnostic history.
- Several loops paginate by markers and mutate the same `marker` variable. Incorrect marker handling could duplicate entries, skip entries, or loop indefinitely.
- Some commands update two related states separately. MFA create/remove updates both OTP backend metadata and `user_info.mfa_ids`; partial failure can leave backend/user metadata inconsistent. Managed policy attachment writes encoded attrs after in-memory changes. Reshard cancel tries both in-progress cancellation and queue removal.
- Object and bucket repair commands bypass ordinary S3 semantics and may alter bucket indexes, manifests, or replication logs directly. They require accurate bucket ids, object versions, shard ids, and feature checks.
- Pubsub topic/notification behavior forks between v1 and v2 depending on zone feature support and `stat_topics_v1()`. Migration-in-progress handling is therefore a compatibility risk.
- Lua script writes verify syntax and context, but persisted scripts affect request/runtime behavior outside this admin command. Package operations are feature-gated but affect allowed runtime dependencies.

## Test and Validation Signals

Useful validation should be command-family specific:

- CLI unit/teuthology tests should cover required-argument failures, errno polarity, formatter output, pagination, and confirmation gates for destructive commands.
- Multisite tests should cover non-master rejection, period update/commit/push, metadata/data/bucket sync status/init/run, sync policy group/flow/pipe create/modify/remove, mdlog/bilog/datalog listing and trimming, and sync error log handling.
- User/account/IAM tests should cover user/subuser/key/caps create/modify/remove, role trust/permission policy parsing failures, managed policy attach/detach/list for account-scoped users/roles, account quota/stat/list behavior, and max-session-duration validation.
- Bucket/object tests should cover list/stats/layout/chown/link/unlink/remove, object stat/manifest/put/remove/rewrite/reindex, bucket index get/put/list/purge, OLH get/readlog, lifecycle get/list/process/fix, and logging flush/info/list.
- Reshard tests should cover direct reshard execution, queue add/list/process/status/cancel, minimum shard updates, reshard log list/purge, and stale instance list/delete with multisite safety checks.
- Maintenance tests should cover usage show/trim/clear, GC list/process, dedup stats/throttle/pause/resume/abort/estimate/exec gates, deprecated orphan commands, and restore status/list.
- Pubsub tests should cover v1 and v2 topic/notification list/get/remove paths, topic owner filtering, bucket-topic mapping lookup, persistent queue stats/dump, and migration-in-progress errors.
- Lua and MFA tests should cover script context validation, tenant restrictions for background scripts, package feature-gate errors, TOTP seed type validation, MFA create/get/list/check/resync/remove, and partial-failure recovery.
- Build matrix coverage should include RADOS and non-RADOS builds, Lua package enabled/disabled builds, and full-dedup disabled builds to catch feature-gated branch regressions.
