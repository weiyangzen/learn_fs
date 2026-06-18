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
