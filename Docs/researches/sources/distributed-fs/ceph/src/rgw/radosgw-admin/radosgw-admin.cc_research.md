# Research: sources/distributed-fs/ceph/src/rgw/radosgw-admin/radosgw-admin.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006981`: lines 1-6910, `Docs/researches/chunks/subset-b-006981_research.md`
- `subset-b-006982`: lines 6911-12759, `Docs/researches/chunks/subset-b-006982_research.md`

## Chunk Research

### subset-b-006981: lines 1-6910

# sources/distributed-fs/ceph/src/rgw/radosgw-admin/radosgw-admin.cc lines 1-6910

## Scope and Purpose

This chunk covers the first 6910 lines of `radosgw-admin.cc`, the front half of Ceph RGW's `radosgw-admin` command-line utility. It establishes global RGW/SAL access, prints the public CLI surface, parses command words and flags, initializes storage/config backends, and implements the early command dispatch for raw realm, period, zonegroup, zone, quota, rate-limit, sync-status, and placement administration.

The source is a broad integration point rather than a narrow library. It binds many RGW subsystems into one process: SAL drivers, config-store writers, RADOS-specific services, realm/period topology objects, bucket sync policy handlers, metadata/data sync status managers, REST forwarding, JSON/XML formatters, lifecycle/logging/dedup headers for later dispatch, and external TOTP support through `liboath`.

## Important APIs, Types, and Helpers

`driver` is a file-global `rgw::sal::Driver*` used by nearly every helper. `dpp()` returns a static `DoutPrefixProvider` around `g_ceph_context` and `ceph_subsys_rgw`, giving helper code a uniform logging prefix without threading a provider everywhere. `StoreDestructor` owns shutdown side effects for the global driver, async context pool, storage manager, and HTTP client cleanup.

`usage()` prints the administrative command matrix and option help. The visible surface includes users, accounts, buckets, bucket sync, bucket logging, object actions, realm/period/zone topology, quotas, rate limits, metadata/data/bucket-index logs, sync policies, roles, resharding, MFA, pubsub notifications, Lua script packages, restore status, and global CORS options.

`SimpleCmd` is the command-word parser. It builds a trie from `all_cmds`, normalizes aliases from `cmd_aliases`, supports optional trailing command parameters through `[*]`, returns the parsed `OPT` enum value in `std::any`, and reports expected next tokens for diagnostics. This parser separates command words from flag parsing: flags are stripped with `ceph_argparse_*` first, then the residual positional words are matched against the trie.

`rgw_admin::OPT` is the central command enum. The chunk defines the complete command-id namespace used by this file, with many entries guarded by `WITH_RADOSGW_RADOS`. `all_cmds` maps user-visible command strings to these enum values, including synonyms such as `buckets list`/`bucket list`, `remove`/`rm`, and hyphenated/non-hyphenated role or realm commands.

Input/output helpers include `read_input()`, two `read_decode_json()` templates, `decode_dump()`, `dump_string()`, `show_result()`, and several formatter wrappers such as `show_user_info()`, `show_perm_policy()`, `show_policy_names()`, `show_policy_arns()`, `show_reshard_status()`, and `show_topics_info_v2()`. They mostly translate RGW structs to `Formatter` output or load JSON from an input file/stdin into Ceph objects.

Quota and rate-limit helpers are shared by raw global config and later user/bucket operations. `set_quota_info()` mutates `RGWQuotaInfo` based on set/enable/disable commands and rounds size through `rgw_rounded_kb()`. `set_ratelimit_info()` mutates `RGWRateLimitInfo`, requires at least one configured value for set commands, and supports read/write/list/delete operation counts plus read/write byte limits. `set_bucket_quota()`, `set_bucket_ratelimit()`, `set_user_ratelimit()`, `show_user_ratelimit()`, `show_bucket_ratelimit()`, `set_user_bucket_quota()`, and `set_user_quota()` persist those structures through bucket info, user info, or SAL attrs such as `RGW_ATTR_RATELIMIT`.

Object and bucket repair helpers in the RADOS-only sections include `check_min_obj_stripe_size()`, `check_obj_locator_underscore()`, `check_obj_tail_locator_underscore()`, and `do_check_object_locator()`. They inspect object attrs/manifests and can call RADOS repair paths for problematic locators on head/tail objects with underscore-prefixed names.

Multisite and remote helpers include `get_remote_conn()` overloads for zonegroups and period maps, `send_to_remote_gateway()`, `send_to_url()`, `send_to_remote_or_url()`, `commit_period()`, `update_period()`, and `do_period_pull()`. These encode periods to JSON, forward admin REST requests to remote zones or explicit URLs, decode responses, and persist returned periods/epochs into the config store.

Sync-status helpers include `get_md_sync_status()`, `get_data_sync_status()`, `sync_status()`, `bucket_source_sync_info`, `bucket_source_sync_status()`, `bucket_sync_info()`, `bucket_sync_status_info`, and `bucket_sync_status()`. They summarize metadata sync markers, data sync markers, recovery shards, source log positions, bucket full/incremental sync states, and remote bilog marker lag. Output can be plaintext or formatter-driven depending on command context.

Sync-policy helpers include `encode_json()` for `RGWBucketSyncFlowManager::pipe_set`, `convert_bucket_set_to_str_vec()`, `get_hint_entities()`, `resolve_zone_id()`, `validate_zone_id()`, `sync_info()`, `init_optional_bucket()`, `SyncPolicyContext`, `resolve_zone_id_opt()`, `resolve_zone_ids_opt()`, `zone_ids_from_str()`, and `JSONFormatter_PrettyZone`. They bridge user-supplied zone/bucket identifiers to real zone ids and bucket keys, initialize bucket-level or zonegroup-level sync policy storage, and serialize policy views with friendlier zone-name rendering.

Validation helpers include `parse_tier_config_param()` for comma-separated tier key/value strings that may contain brace-nested values, `check_pool_support_omap()` for RADOS pool omap capability, `check_reshard_bucket_params()` for bucket reshard preconditions, `scan_totp()` for MFA resync skew scanning, `trim_sync_error_log()`, and small option predicates such as `symmetrical_flow_opt()`, `directional_flow_opt()`, `require_opt()`, and `require_non_empty_opt()`.

## Main Control Flow in This Chunk

`main()` starts by converting argv to a vector, handling `-h/--help`, installing an RGW utility default of `rgw_thread_pool_size=8`, calling `rgw_global_init()`, creating an `io_context_pool`, and preserving the legacy `rgw_region` to `rgw_zonegroup` mapping before `common_init_finish()`.

The next large block declares all command-state variables. These include entity identifiers, realm/zone/zonegroup names and ids, bucket/object parameters, quotas, rate limits, placement parameters, sync-policy operands, pubsub parameters, MFA fields, Lua script fields, fault-injection options, and output formatting state. This block is the shared option state later consumed by the switch dispatch.

Flag parsing uses `ceph_argparse_witharg()`, `ceph_argparse_binary_flag()`, and `ceph_argparse_flag()` in a long `else if` chain. It removes recognized flags from `args`, validates parseable integers/sizes with strict parsers where available, stores optional values in `std::optional`, and updates Ceph config for realm/zone/zonegroup id flags before common initialization is finished. Invalid unrecognized `-` flags return `EINVAL`.

After `common_init_finish()`, the residual command words are parsed by `SimpleCmd`. Optional positional metadata keys are copied for metadata commands. Then the command is classified into `raw_storage_ops_list`, `readonly_ops_list`, and `gc_ops_list`. This classification drives storage initialization: raw topology/config commands use `DriverManager::get_raw_storage()` with a fake site config; ordinary commands load `SiteConfig`, then call `DriverManager::get_storage()` with optional cache and GC enablement.

Once the driver exists, `main()` constructs the target SAL user, normalizes optional buckets from tenant/name/id fragments, applies tenant/user namespace defaults, checks mutually exclusive key-generation inputs, chooses a default pretty JSON formatter if none was requested, initializes HTTP/curl/oath support, and creates `StoreDestructor` for cleanup.

The chunk then enters the first major dispatch, `if (raw_storage_op) switch (opt_cmd)`. Within the requested lines, it handles period delete/get/get-current/list/update/pull, global ratelimit get/set/enable/disable, global quota get/set/enable/disable, realm create/delete/get/get-default/list/list-periods/rename/set/default/default-rm/pull, zonegroup add/create/default/delete/get/list/modify/set/remove/rename/placement list/get/add/modify/rm/default, and zone create/default/delete/get/set/list/modify/rename plus the beginning of zone placement add/modify/rm.

## State and Persistence Behavior

The code persists administrative state through two main abstractions: `rgw::sal::ConfigStore` for realm, period, zonegroup, zone, default ids, and period config; and `rgw::sal::Driver`/SAL objects for users, buckets, bucket attrs, and bucket info. Raw storage commands avoid loading the full site view when they may be repairing or bootstrapping topology.

Realm operations call `rgw::create_realm()`, `rgw::read_realm()`, `RealmWriter::write()`, `RealmWriter::remove()`, `RealmWriter::rename()`, and default realm config-store helpers. `REALM_SET` can create a new realm from JSON and intentionally clears period/epoch for new realms. `REALM_PULL` fetches `/admin/realm` from a URL, optionally pulls its current period, and stores the realm locally with non-exclusive creation.

Period operations read/write period objects and latest epoch markers. `commit_period()` commits locally when the current zone is the period's master zone; otherwise it forwards JSON to the new master via `RGWRESTConn` or a signed explicit URL, stores the returned period, updates latest epoch, reflects local objects, and notifies the realm of the new period. `update_period()` forks the current period to staging, refreshes it from zonegroup state, persists it, and optionally commits it.

Global quota and rate-limit operations read `RGWPeriodConfig` for a realm id or default/empty realm, mutate scoped bucket/user/anonymous fields, write the period config for non-get operations, and print instructions about applying changes through period update/commit when a realm is involved. Empty realm-id changes take effect after gateway restart.

Zonegroup and zone operations persist public topology and placement data. `ZONEGROUP_ADD`, `ZONE_CREATE`, and `ZONE_MODIFY` may update both zone params and zonegroup membership. Feature sets are validated against `rgw::zone_features`, and zonegroup feature requirements are checked against per-zone support in `ZONEGROUP_SET`. Placement operations alter `RGWZoneGroupPlacementTarget` storage classes, tags, tier targets, and defaults, then write the zonegroup.

Bucket/user quota and rate-limit helpers persist per-entity state by writing bucket info, user info, or encoded `RGW_ATTR_RATELIMIT` attrs. Object locator repair helpers call RADOSStore internals and may mutate RADOS object locators when `--fix` is used.

## Dependencies and Integration Points

This chunk depends heavily on Ceph common utilities (`Formatter`, JSON parser/decoder, argparse helpers, bufferlist, safe IO, strict parsers), RGW core models (`RGWRealm`, `RGWPeriod`, `RGWZoneGroup`, `RGWZoneParams`, `RGWBucketInfo`, `RGWUserInfo`, quota/rate-limit structs), SAL (`Driver`, `ConfigStore`, `Bucket`, `User`, writer interfaces), RADOS-only services (`RGWDataSyncStatusManager`, `RGWMetaSyncStatusManager`, bilog/datalog/mdlog helpers, cls services, bucket sync status readers), admin REST forwarding (`RGWRESTConn`, `RGWRESTSimpleRequest`), compression validation, and `liboath` for MFA TOTP verification.

Preprocessor guards are significant. Many commands and helper bodies only exist with `WITH_RADOSGW_RADOS`, while the enum and command table must still remain consistent for non-RADOS builds. The raw/readonly/GC command sets also include guarded entries, so build-configuration coverage matters.

The file integrates with later chunks through the same `OPT` enum, parsed option variables, `driver`, `cfgstore`, `formatter`, `bucket_op`, `user_op`, and switch structure. The requested range ends while handling zone placement, so subsequent chunks complete that case and implement the non-raw command dispatch.

## Risks and Edge Cases

The command surface is centralized but very large. Adding a command requires synchronized edits to `usage()`, `OPT`, `all_cmds`, option parsing, command classification, and switch dispatch. Missing one of those sites can produce misleading help, unreachable functionality, wrong storage initialization, or incorrect cache/GC behavior.

The file-global `driver` and `dpp()` simplify helpers but obscure dependencies and make helper behavior sensitive to initialization order. Many helpers assume `driver` is initialized and, in RADOS-only paths, cast it to `rgw::sal::RadosStore*`.

Return-code sign handling is inconsistent in places. Most Ceph helpers return negative errno, but this chunk contains several `return -ret` patterns after already-negative `ret` values and some diagnostics call `cpp_strerror(ret)` instead of `cpp_strerror(-ret)`. These paths need careful review when changing error propagation.

Raw topology commands can mutate critical multisite state. Some operations write local config immediately but require later `period update`/`period commit` to apply cluster-wide. User-facing output warns for quota/rate-limit changes and realm rename locality, but callers/scripts still need to understand staging versus committed state.

Parsing is mostly strict for numeric values, but some options still use `atoi()` or direct casts. `parse_tier_config_param()` is brace-depth aware but not a full JSON/config parser, so malformed nested input can produce surprising key/value splits.

Feature and sync-module validation happens on selected paths, but topology updates are multi-object sequences. For example, adding/modifying a zone can write zone params and then zonegroup data; failures after the first write can leave partially updated local config that must be repaired by rerunning or manually editing topology.

REST forwarding paths assume small responses capped by `MAX_REST_RESPONSE` and require access/secret keys for explicit URLs. Failed remote period commits can leave the local staging period created but not committed.

## Test Signals

Useful test coverage for this chunk should exercise command parsing aliases and optional positional arguments, especially `metadata get [*]`, hyphenated role/realm aliases, `delete`/`remove`/`rm`, and invalid command expected-token diagnostics.

Initialization tests or integration smoke tests should verify raw storage classification for realm/period/zonegroup/zone/global quota/rate-limit commands, and non-raw initialization for ordinary user/bucket/object commands. Tests should also assert readonly/GC classification where background GC or cache enablement changes side effects.

Config-store integration tests should cover realm create/set/pull/default/list, period update/commit/pull, zonegroup feature validation, zone create/modify with zonegroup membership, and placement add/modify/remove/default. Failure-injection tests are valuable for partial-write scenarios.

Behavioral tests should check quota and rate-limit serialization at global, bucket, and user scopes, including "set with no values" rejection for rate limits and negative quota values disabling limits.

Multisite status tests should cover metadata sync, data sync, and bucket sync outputs for caught-up, full-sync, incremental-lag, recovery, missing source zone, disabled sync, and remote bilog read failure cases. Formatter and plaintext output paths should both be exercised.

RADOS-only tests should cover object locator repair dry-run versus `--fix`, reshard parameter validation, omap pool support checks, and TOTP resync skew scanning. Build tests should compile both with and without `WITH_RADOSGW_RADOS` to catch enum/table/switch drift.

### subset-b-006982: lines 6911-12759

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
