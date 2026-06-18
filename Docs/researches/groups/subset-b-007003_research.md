# subset-b-007003 Research

Grouped source research for Ceph RGW multisite zone configuration, zone feature serialization, the `rgwam` command wrapper, bucket metadata services, RADOS bucket-index services, and RADOS bucket-index log services. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_zone.cc -->
# sources/distributed-fs/ceph/src/rgw/rgw_zone.cc

## Purpose

`rgw_zone.cc` implements most of RGW's multisite zone, zonegroup, realm, and period behavior declared in `rgw_zone.h` and `rgw_zone_types.h`. It supplies JSON encode/decode helpers, default object/pool naming, placement/tier parameter handling, zonegroup membership updates, realm/period creation and commit flows, and `rgw::SiteConfig` loading. The file was read as a complete 2329-line implementation.

## Important APIs, Types, and Functions

Key definitions include the `rgw_zone_defaults` object-name and pool-name constants, JSON helpers for `RGWZone`, `RGWZoneParams`, `RGWZoneGroup`, `RGWPeriodMap`, placement targets, storage classes, and tier configs. Operational entry points in namespace `rgw` include `gen_random_uuid()`, `get_zones_pool_set()`, `init_zone_pool_names()`, `get_zonegroup_endpoint()`, `add_zone_to_group()`, `read_realm()`, `create_realm()`, `set_default_realm()`, `realm_set_current_period()`, `reflect_period()`, `get_staging_period_id()`, `fork_period()`, `update_period()`, `commit_period()`, `read_zonegroup()`, `create_zonegroup()`, `set_default_zonegroup()`, `remove_zone_from_group()`, `read_zone()`, `create_zone()`, `set_default_zone()`, `delete_zone()`, `find_zone_placement()`, `all_zonegroups_support()`, and `SiteConfig::{load,make_fake,load_period_zonegroup,load_local_zonegroup}`.

## Control Flow

Zone and placement parsing flow is mostly data transformation: JSON objects are decoded into serialized structs, and dump methods emit the same topology/configuration back to formatters. Zone creation uses `get_zones_pool_set()` to list existing zones, `add_zone_pools()` to collect their pool names, then `init_zone_pool_names()` to choose non-conflicting pools with the zone name as prefix.

Realm flow starts with `read_realm()` selection by id/name/default. `create_realm()` validates/generates a realm id, creates the realm, creates an initial period if needed, updates latest epoch, then calls `realm_set_current_period()`. `realm_set_current_period()` enforces realm epoch monotonicity, writes the realm via `sal::RealmWriter`, and reflects local period config/zonegroup state.

Period update flow in `fork_period()` changes the period into `<realm>:staging`, resets the period map, and increments realm epoch. `update_period()` lists all zonegroups, filters by realm id, validates master-zone references, records master zonegroup/master zone, rebuilds short zone ids, and reads realm-level period config. `commit_period()` requires the local gateway to be in the period's master zone, verifies predecessor and epoch continuity, then either creates a new period id when the master zone changed or writes the next epoch on the current period id; it updates latest epoch and reflects local config.

Site loading starts by clearing previous pointers, attempts configured/default realm loading, loads configured/default zone params, backfills the realm from `zone_params.realm_id` if needed, attempts current-period zonegroup lookup, and falls back to a local zonegroup if allowed.

## State and Persistence Behavior

Persistent topology and configuration are stored through `rgw::sal::ConfigStore` and its writer interfaces. This file does not directly manipulate RADOS objects; it abstracts persistence as realm, period, zonegroup, zone, period-config, and default-id operations. It preserves old serialized formats in `decode()` methods through version checks and fallback defaults, including generated values for legacy pool fields. Period state is versioned by period id, period epoch, realm epoch, predecessor uuid, and latest-epoch records. Zone pool state is persisted in `RGWZoneParams`; short zone ids are deterministically derived from MD5 of zone ids and stored in `RGWPeriodMap`.

## Dependencies and Integration Points

The file depends on `rgw_zone.h`, `rgw_sal.h`, `rgw_sal_config.h`, `driver/rados/rgw_sync.h`, and `services/svc_zone.h`. It integrates with SAL config storage, metadata sync status (`RGWPeriod::update_sync_status()`), Ceph context configuration (`rgw_realm`, `rgw_zone`, `rgw_zonegroup`, root-pool overrides), JSON formatting/decoding, and bucket placement/tiering code. Zone feature handling uses `rgw::zone_features` to gate enabled/supported features across zones and zonegroups.

## Risks and Edge Cases

Period commit is sensitive to epoch/predecessor mismatches and master-zone transitions; incorrect bypasses risk split-brain multisite configuration. `fix_zone_pool_dup()` uses `std::rand()` for conflict suffixes, so pool naming is not deterministic across retries. Short zone id collisions are explicitly checked and return `-EEXIST`, but collisions block period map updates. Some compatibility paths use legacy names such as region/zonegroup defaults, and decode failures may silently default old fields. `reflect_period()` treats setting default zonegroup as best-effort when `-EEXIST` occurs, so defaults can lag topology. Tier parameter parsing converts string booleans and integers manually and resets to defaults on parse errors.

## Test Signals

Useful test signals include dencoder round trips for all serialized classes and versioned decode paths, JSON import/export tests for legacy region fields, unit tests for period commit validation failures, integration tests for realm bootstrap/period update/period commit, pool-name conflict tests across multiple zones, short-zone-id collision injection, and multisite tests covering master-zone promotion and `SiteConfig::load()` fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_zone.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_zone.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_zone.h

## Purpose

`rgw_zone.h` declares the main RGW multisite configuration contracts: local zone parameters, public zonegroup topology, period maps/configuration, realms, periods, and the immutable-at-runtime `rgw::SiteConfig` view. It also declares the administrative helper functions implemented in `rgw_zone.cc`. The file was read as a complete 923-line header.

## Important APIs, Types, and Functions

`RGWZoneParams` stores local zone pool names, system key, placement pools, realm id, tier config, and helpers like `get_pool()`, `get_compression_type()`, `get_placement()`, `get_head_data_pool()`, and `valid_placement()`. `RGWZoneGroup` stores public zonegroup state: id/name/api name, endpoints, master-zone marker, zone map, placement targets, default placement, hostnames, realm id, sync policy, and enabled zone features. `RGWPeriodMap` stores zonegroups, API-name lookup, short zone ids, and helpers to update/find zones. `RGWPeriodConfig` stores quotas and rate limits. `RGWRealm` stores id/name/current period/epoch and can find zones. `RGWPeriod` stores period id, epoch, predecessor, sync status, map/config, master zonegroup/zone, realm id/epoch, and `update_sync_status()`.

Namespace `rgw` declares read/create/default functions for realms, zonegroups, and zones; period reflection/fork/update/commit; placement lookup; feature checks; uuid generation; and `SiteConfig`.

## Control Flow

The header itself has no executable control flow beyond inline accessors and serialization methods. Its inline encoders/decoders define the persistence order and compatibility control flow for versioned records. Higher-level flows are expressed as APIs: callers load or create realms/zones/zonegroups through `ConfigStore`, fork/update/commit periods, then load a `SiteConfig` view for runtime use.

## State and Persistence Behavior

Most types in this header are serialized with `WRITE_CLASS_ENCODER` and explicit `ENCODE_START` versions. `RGWZoneParams` is at version 18 and preserves old defaults for later-added pools such as lifecycle, roles, reshard, otp, oidc, notification, topics/account/group, restore, dedup, and bucket logging. `RGWZoneGroup` persists enabled feature sets and sync policy. `RGWPeriod` persists both realm epoch and period epoch to distinguish topology changes from ordinary epoch advances. `SiteConfig` stores optional realm/period and pointers into either period-owned or local zonegroup-owned objects, so pointer lifetime is tied to the owning optional members.

## Dependencies and Integration Points

Includes connect this header to `rgw_zone_types.h`, `rgw_common.h`, SAL forward declarations, and sync policy definitions. It is consumed by admin tooling, RGW startup/config reload code, bucket placement selection, sync code, and service layers that need local zone/zonegroup params.

## Risks and Edge Cases

Changing field order or version gates in inline serialization can break on-disk compatibility. `SiteConfig` exposes references through internal pointers, so reload coordination must prevent concurrent access to stale pointers. `RGWZoneParams::get_head_data_pool()` must handle explicit bucket placement, placement rules, extra-data pools, and missing rules consistently. Feature checks rely on flat-set contents, so administrative enable/disable flows must keep zonegroup enabled features compatible with per-zone supported features.

## Test Signals

Signals include compile coverage from all RGW services, dencoder compatibility tests for versioned structs, unit tests for placement lookup/data-pool selection, period map zone lookup tests, `SiteConfig::make_fake()` consumers, and integration tests for feature gating via `all_zonegroups_support()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_zone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_zone_features.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_zone_features.h

## Purpose

`rgw_zone_features.h` defines fundamental serialized zone feature names and the feature-set container used by zone and zonegroup configuration. The header is deliberately dependency-light so it can be included by serialized types outside radosgw-only contexts. The file was read as a complete 50-line header.

## Important APIs, Types, and Functions

The namespace `rgw::zone_features` exposes `resharding`, `compress_encrypted`, and `notification_v2` string constants; `supported`, the release-supported feature list; `enabled`, the default-on feature list for new zonegroups; `supports(std::string_view)`; transparent comparator `feature_less`; and `using set = boost::container::flat_set<std::string, feature_less>`.

## Control Flow

The only runtime logic is the constexpr `supports()` loop over the static `supported` list. All other behavior is compile-time declaration or type aliasing.

## State and Persistence Behavior

Feature state is persisted by `rgw::zone_features::set` fields in `RGWZone` and `RGWZoneGroup`. The header itself owns no mutable state. Transparent comparison lets persisted `std::string` entries be queried by `std::string_view` without temporary allocations.

## Dependencies and Integration Points

It depends on `<string>` and `boost::container::flat_set`. `rgw_zone_types.h` includes it for serialized feature sets, and `rgw_zone.cc` uses `enabled` defaults during default zonegroup creation and validates feature enable/disable behavior in `add_zone_to_group()`.

## Risks and Edge Cases

Adding/removing strings changes administrative compatibility across multisite zones. Features enabled in a zonegroup must also be supported by every member zone, so default changes can affect period commits and mixed-version deployments. The feature names are persisted strings, making spelling changes incompatible.

## Test Signals

Tests should cover `supports()` for every supported and unknown feature, serialization round trips of feature sets in `RGWZone` and `RGWZoneGroup`, and mixed-version multisite scenarios where a zone lacks a feature enabled in the zonegroup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_zone_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_zone_types.h -->
# sources/distributed-fs/ceph/src/rgw/rgw_zone_types.h

## Purpose

`rgw_zone_types.h` defines the lower-level serialized data types shared by RGW zone configuration code: name-to-id records, default metadata references, zone placement/storage-class records, public zone records, zonegroup placement/tiering records, and cloud-tier restore settings. It avoids radosgw-only includes because these types are part of serialized contracts. The file was read as a complete 766-line header.

## Important APIs, Types, and Functions

Important types include `RGWNameToId`, `RGWDefaultSystemMetaObjInfo`, `RGWZoneStorageClass`, `RGWZoneStorageClasses`, `RGWZonePlacementInfo`, `RGWZone`, `RGWDefaultZoneGroupInfo`, `RGWTierACLMapping`, `HostStyle`, `RGWZoneGroupPlacementTierS3`, `GlacierRestoreTierType`, `RGWZoneGroupTierS3Glacier`, `RGWTierType`, `RGWZoneGroupPlacementTier`, and `RGWZoneGroupPlacementTarget`.

Key helpers include storage class lookup/mutation (`find()`, `exists()`, `set_storage_class()`, `remove_storage_class()`), placement pool getters (`get_data_pool()`, `get_data_extra_pool()`, `get_compression_type()`), zone sync/feature predicates (`syncs_from()`, `supports()`), target-bucket naming for cloud S3 tiers, and user tag checks on placement targets.

## Control Flow

Most control flow is inline compatibility decoding and simple selection logic. `RGWZonePlacementInfo::decode()` reconstructs legacy standard data/compression fields into `RGWZoneStorageClasses`. `RGWZone::decode()` handles legacy id/name and optional sync/redirect/feature fields. `RGWZoneGroupPlacementTier::decode()` branches by serialized version and tier type to decide whether to decode S3 and glacier substructures. `RGWZoneGroupPlacementTarget::user_permitted()` allows all users when no tags are configured or requires at least one matching user tag.

## State and Persistence Behavior

Every major type has explicit Ceph buffer encoding via `WRITE_CLASS_ENCODER`. `RGWZoneStorageClasses` maintains an in-memory-only `standard_class` pointer into its map and resets it after copy/assignment/decode. `RGWZone` persists public zone behavior such as endpoints, logging flags, read-only flag, tier type, sync sources, redirect zone, bucket index shard default, and supported features. Placement/tier records persist storage-class pools, compression, inline-data preference, cloud endpoint credentials, target path/bucket templates, ACL mappings, multipart thresholds, read-through restore controls, and glacier restore settings.

## Dependencies and Integration Points

The header depends on Ceph types, bucket layout, zone features, pool/ACL/placement types, and formatter declarations. It is included by `rgw_zone.h`, admin tooling, config-store implementations, tiering/sync code, and bucket placement logic. It integrates with object placement via `rgw_placement_rule`, bucket index layout via `rgw::BucketIndexType`, and external cloud-tier sync via S3/glacier tier settings.

## Risks and Edge Cases

Serialized layout changes are high risk because these records live in cluster metadata. `RGWZoneStorageClasses::remove_storage_class()` refuses to remove the default class when passed an empty storage class, which is intentional but easy to miss. Optional pool/compression values can result in empty static fallback values. Cloud tier bucket-name templates are lowercased and token-substituted; missing `${bucket}` in target-by-bucket mode appends the bucket name, which can surprise administrators. The S3 tier stores access keys/secrets in serialized config, so dumps and handling paths must be careful.

## Test Signals

Test signals include dencoder round trips, legacy decode tests for placement and tier versions, storage-class existence/fallback unit tests, user tag permission tests, cloud target-bucket-name template tests, glacier restore config tests, and integration tests for bucket placement selection and cloud tier sync configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgw_zone_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgwam.py -->
# sources/distributed-fs/ceph/src/rgw/rgwam.py

## Purpose

`rgwam.py` is the command-line wrapper for the RGW assist-for-multisite tooling. It parses top-level `realm` and `zone` subcommands, adapts CLI environment options to `RGWAMEnvMgr`, invokes `RGWAM` core operations, and reports command failures. The file was read as a complete 240-line Python script.

## Important APIs, Types, and Functions

`RGWAMCLIMgr` builds a `ceph`/tool argument prefix from `-c`, `-n`, and `-k`, executes external programs via `subprocess.run()`, and stubs orchestrator-style methods `apply_rgw()` and `list_daemons()`. `RealmCommand` dispatches `bootstrap` and `new_zone_creds`. `ZoneCommand` dispatches `run` and `create`. `CommonArgs` stores common Ceph options. `TopLevelCommand._parse()` handles top-level command parsing and help propagation. `main()` sets logging, builds `EnvArgs`, invokes the selected command, and exits based on return code or `RGWAMException`.

## Control Flow

CLI flow starts in `main()`, which calls `TopLevelCommand()._parse()`. The top-level parser separates common options from the remaining subcommand args and preserves subcommand help flags by removing them before top-level parsing and appending them back. The selected top-level method constructs a subcommand class, whose `parse()` maps hyphenated subcommand names to method names, creates a subparser for command-specific arguments, and returns the matching bound method. That method delegates to `RGWAM(self.env)` core methods such as `realm_bootstrap()`, `realm_new_zone_creds()`, `zone_create()`, or `run_radosgw()`.

## State and Persistence Behavior

This script owns no persistent state. Persistence and cluster mutation are delegated to `RGWAM` core and external tools invoked through `RGWAMCLIMgr.tool_exec()`. Runtime state is limited to parsed arguments, command prefixes, stdout/stderr from subprocesses, and process exit status.

## Dependencies and Integration Points

It imports `ceph.rgw.rgwam_core.RGWAM`, `EnvArgs`, `ceph.rgw.types.RGWAMEnvMgr`, and `RGWAMException`. It also imports several standard modules, though some are unused in this wrapper (`random`, `string`, `json`, `socket`, `base64`, `urlparse`). The command is processed by build tooling to substitute the Python shebang/version.

## Risks and Edge Cases

The dynamic dispatch pattern requires method names to match parsed command names after hyphen replacement for realm commands; zone commands currently check the literal subcommand name, which works for `run` and `create` but would need care for future hyphenated zone subcommands. `RGWAMCLIMgr.tool_exec()` decodes stdout/stderr as UTF-8 without error handling. `apply_rgw()` and `list_daemons()` are no-ops in the CLI manager, so any core path requiring orchestrator behavior must handle that. `RGWAMException` handling prints `e.message`, which depends on that attribute being present.

## Test Signals

Tests should cover parser dispatch for each command, subcommand `-h/--help` behavior, propagation of common `-c/-n/-k` arguments into `tool_exec()`, nonzero return logging/exit behavior, `RGWAMException` rendering, and CLI integration with mocked `RGWAM` core methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/rgwam.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bi.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bi.h

## Purpose

`svc_bi.h` declares the abstract RGW bucket-index service interface. It separates bucket metadata services from the backend that initializes, cleans, reads, and reacts to changes in bucket index state. The file was read as a complete 49-line header.

## Important APIs, Types, and Functions

`RGWSI_BucketIndex` derives from `RGWServiceInstance` and declares pure virtual methods: `init_index()`, `clean_index()`, `read_stats()`, and `handle_overwrite()`. Inputs include `RGWBucketInfo`, bucket index layout generations, optional coroutine yield contexts, and a flag to probe log-record support during index initialization.

## Control Flow

The header has no implementation flow. Concrete services such as `RGWSI_BucketIndex_RADOS` implement shard creation/removal, stat reads, and overwrite side effects.

## State and Persistence Behavior

No state is stored here. Implementations own persistence details, typically RADOS bucket index objects and bucket index logs.

## Dependencies and Integration Points

It includes `driver/rados/rgw_service.h` and forward-declares `RGWBucketInfo`/`RGWBucketEnt`. `svc_bucket_sobj.cc` uses this interface for bucket stats and overwrite handling; RADOS-specific code implements it in `svc_bi_rados.{h,cc}`.

## Risks and Edge Cases

The interface assumes all implementations can map high-level bucket layouts to backend index operations. `handle_overwrite()` is part of metadata write flow, so failures can block bucket-info updates. `init_index()`'s `judge_support_logrecord` flag is backend-specific but exposed through the generic interface.

## Test Signals

Compile-time interface coverage, mock implementations for bucket metadata unit tests, and backend integration tests for index lifecycle and overwrite behavior are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bi_rados.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bi_rados.cc

## Purpose

`svc_bi_rados.cc` implements the RADOS-backed bucket-index service. It maps `RGWBucketInfo` and bucket index layout generations to RADOS index objects, performs asynchronous shard fan-out for index lifecycle/read/list/status operations, and coordinates bilog/datalog updates when bucket data-sync flags change. The file was read as a complete 1048-line implementation.

## Important APIs, Types, and Functions

Public methods implemented include `init()`, `open_pool()`, `open_bucket_index_pool()`, `open_bucket_index_base()`, several `open_bucket_index()` overloads, `get_bucket_index_object()`, `open_bucket_index_shard()`, `cls_bucket_head()`, `init_index()`, `clean_index()`, `read_stats()`, `get_reshard_status()`, `set_reshard_status()`, `trim_reshard_log()`, `set_tag_timeout()`, `check_index()`, `rebuild_index()`, `list_objects()`, and `handle_overwrite()`.

Internal helpers include `bucket_obj_with_generation()`, `bucket_obj_without_generation()`, `get_bucket_index_objects()`, `get_bucket_instance_ids()`, and shard_io reader/writer structs such as `IndexHeadReader`, `IndexInitWriter`, `IndexCleanWriter`, `ReshardStatusReader`, `ReshardStatusWriter`, `ReshardTrimWriter`, `TagTimeoutWriter`, `CheckReader`, `RebuildWriter`, and `ListReader`.

## Control Flow

Index object lookup starts by opening an index pool. Explicit bucket placement index pools win; otherwise the service uses the zonegroup default placement when a bucket lacks a placement rule, then looks up that placement in local zone params. Bucket index object names are `.dir.<bucket_id>` for unsharded indexes, `.dir.<bucket_id>.<shard>` for legacy generation 0 sharded indexes, and `.dir.<bucket_id>.<gen>.<shard>` for generated layouts.

Shard fan-out operations build a shard-id-to-oid map, create an appropriate `rgwrados::shard_io` reader/writer, then run either on the caller coroutine executor (`optional_yield`) or on a system executor with `ceph::async::use_blocked`. `init_index()` uses `RadosRevertibleWriter` so partial shard creation is reverted on failure. `list_objects()` handles `RGWBIAdvanceAndRetryError` by retrying with an advanced shard marker. `handle_overwrite()` compares old/new data-sync flags, starts or stops bilog as needed, then writes datalog entries for all log shards.

## State and Persistence Behavior

Persistent state is in RADOS bucket index objects and their omap headers/CLS-managed contents. CLS operations include bucket index initialization, head reads, reshard status get/set, reshard log trim, tag timeout updates, index checks, rebuild, and bucket listing. `read_stats()` aggregates main-category stats from bucket index headers. `handle_overwrite()` persists bilog start/stop state in index objects and writes data changes through `RGWDataChangesLog`.

## Dependencies and Integration Points

The file depends on `svc_bi_rados.h`, `svc_bilog_rados.h`, `svc_zone.h`, `rgw_asio_thread.h`, `rgw_zone.h`, `driver/rados/rgw_datalog.h`, `driver/rados/shard_io.h`, `cls/rgw/cls_rgw_client.h`, and async/error helpers. It integrates with local zone placement state, RADOS IoCtx creation, cls_rgw object-class methods, bilog service, datalog service, bucket layout helpers, and coroutine/blocking execution paths.

## Risks and Edge Cases

Empty bucket ids return `-EIO` because index object names cannot be formed. Placement-rule lookup failures return `-EINVAL` and block index access. Shard id checks use `std::cmp_greater(shard_id, num_shards)` or `shard_id > num_shards`; off-by-one behavior around `num_shards` deserves scrutiny because valid shard ids are zero-based. `cls_bucket_head()` ignores missing index objects but decode failures become `-EIO`. `init_index()` ignores `EEXIST` per shard but still aims for all-or-nothing for other failures. `handle_overwrite()` returns the final datalog result and treats datalog errors as fatal after bilog changes, so partial side effects are possible.

## Test Signals

Signals include unit tests for shard object naming with/without generations, shard selection for normal and multipart object keys, RADOS integration tests for index create/clean/head/list/check/rebuild, reshard status/log tests, coroutine and blocking execution coverage, data-sync flag transition tests that verify bilog and datalog writes, and error-injection tests for placement lookup, empty bucket ids, decode failures, and partial shard failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bi_rados.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bi_rados.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bi_rados.h

## Purpose

`svc_bi_rados.h` declares the RADOS implementation of the bucket-index service. It exposes helpers for opening bucket index pools/objects/shards and high-level methods for stats, resharding, index checking/rebuilding/listing, and overwrite handling. The file was read as a complete 191-line header.

## Important APIs, Types, and Functions

The class `RGWSI_BucketIndex_RADOS` derives from `RGWSI_BucketIndex` and is a friend of `RGWSI_BILog_RADOS`. It stores `librados::Rados* rados` and service dependencies in `Svc` (`RGWSI_Zone`, `RGWSI_BILog_RADOS`, `RGWDataChangesLog`). Static helpers include `shards_max()`, `shard_id()`, and `bucket_shard_index()` overloads. Public methods include index lifecycle overrides, RADOS-specific reshard/status/check/rebuild/listing helpers, bucket index opening helpers, and `cls_bucket_head()`.

## Control Flow

The header defines static shard selection logic: generic keys use `rgw_shard_id()`, while bucket-object keys use Linux string hashing with a bit-mixed value and multipart objects hash on the multipart base key. Implementations use `open_bucket_index_*()` before invoking cls or shard_io operations.

## State and Persistence Behavior

The class itself holds service pointers and the librados cluster handle. Persistent state is external in bucket index RADOS objects, bilog state, reshard logs, and datalog entries manipulated by the `.cc` implementation.

## Dependencies and Integration Points

Includes connect it to RADOS datalog/service/tools, `rgw_bucket.h`, the abstract `svc_bi.h`, and tier RADOS service types. It integrates closely with `RGWSI_BILog_RADOS`, `RGWSI_Zone`, bucket layout types, and cls_rgw return structures.

## Risks and Edge Cases

The shard hash functions are part of object placement compatibility; changing them would move object index entries. Public `open_bucket_index()` helpers are used by bilog and other services, so naming/layout bugs have broad impact. Service pointer initialization order must ensure `init()` runs before operations.

## Test Signals

Compile coverage, shard hash golden tests, multipart key shard tests, service initialization tests, and RADOS integration tests for every public method are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bi_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bilog_rados.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bilog_rados.cc

## Purpose

`svc_bilog_rados.cc` implements bucket-index log operations on top of the RADOS bucket-index service. It starts/stops bilog recording, trims bilog ranges, lists log entries across shards, and reads bilog status markers. The file was read as a complete 382-line implementation.

## Important APIs, Types, and Functions

Implemented methods are `RGWSI_BILog_RADOS::init()`, `log_trim()`, `log_start()`, `log_stop()`, `log_list()`, and `get_log_status()`. Internal pieces include `TrimWriter`, `StartWriter`, `StopWriter`, `build_bucket_index_marker()`, `LogReader`, and helper `bilog_list()`.

## Control Flow

Every operation converts a bucket log layout to its backing index layout with `rgw::log_to_index_layout()`, asks `RGWSI_BucketIndex_RADOS::open_bucket_index()` for shard oids, then fans out RADOS cls operations through `rgwrados::shard_io`. Start and stop are simple writes of `cls_rgw_bilog_start()`/`cls_rgw_bilog_stop()`. Trim parses start/end marker strings with `BucketIndexShardsManager`, calls `cls_rgw_bilog_trim()`, and retries until cls reports no more data. Listing parses the input marker, reads per-shard log lists, round-robins entries up to `max`, rewrites entry ids with shard prefixes for sharded indexes, updates per-shard markers, and reports truncation if cls or local merge state has remaining entries.

## State and Persistence Behavior

Bilog state is persisted inside bucket index RADOS objects through cls_rgw bilog methods. Markers are string state owned by callers and encoded/decoded by `BucketIndexShardsManager`. `get_log_status()` reads bucket index headers and returns each shard's `max_marker` keyed by shard.

## Dependencies and Integration Points

The file depends on `svc_bilog_rados.h`, `svc_bi_rados.h`, `rgw_asio_thread.h`, `driver/rados/shard_io.h`, `cls/rgw/cls_rgw_client.h`, and blocked async completion support. It is called by bucket index overwrite handling and by sync/admin paths that consume or trim bucket index logs.

## Risks and Edge Cases

Marker parsing errors abort list/trim. Multi-shard list merging is round-robin rather than globally timestamp-sorted, so consumers must rely on marker semantics rather than a total order. `log_trim()` retries until `ENODATA`; unexpected cls behavior could loop through shard_io retry handling. `get_log_status()` asserts header and instance-id counts match, so malformed results can abort in debug/asserting builds.

## Test Signals

Signals include RADOS cls integration tests for start/stop/trim/list/status, marker round-trip tests for sharded and unsharded logs, pagination/truncation tests, trim-to-ENODATA behavior, and bucket data-sync transition tests through `RGWSI_BucketIndex_RADOS::handle_overwrite()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bilog_rados.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bilog_rados.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bilog_rados.h

## Purpose

`svc_bilog_rados.h` declares the RADOS bucket-index log service interface used by bucket index and sync code. The file was read as a complete 62-line header.

## Important APIs, Types, and Functions

`RGWSI_BILog_RADOS` derives from `RGWServiceInstance`, stores a dependency on `RGWSI_BucketIndex_RADOS`, and declares `init()`, `log_start()`, `log_stop()`, `log_trim()`, `log_list()`, and `get_log_status()`.

## Control Flow

The header itself has no executable flow. The declared methods operate on `RGWBucketInfo`, bucket log layout generations, optional shard ids, markers, and coroutine yield contexts.

## State and Persistence Behavior

The class stores only a bucket-index service pointer. Persistent log state is in RADOS bucket index objects via the implementation.

## Dependencies and Integration Points

It includes `driver/rados/rgw_service.h` and depends on bucket/log layout and bilog entry types from broader RGW headers. It is initialized by service wiring and used by `RGWSI_BucketIndex_RADOS` when bucket sync logging changes.

## Risks and Edge Cases

Consumers must pass a log layout compatible with in-index bilog operations. Marker strings and shard ids must match the target layout or list/trim operations fail. Initialization order matters because methods dereference `svc.bi`.

## Test Signals

Compile coverage, service initialization tests, and integration tests through bilog list/trim/start/stop/status paths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bilog_rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bucket.cc

## Purpose

`svc_bucket.cc` implements small common helpers for the abstract bucket metadata service. The file was read as a complete 25-line implementation.

## Important APIs, Types, and Functions

`RGWSI_Bucket::get_entrypoint_meta_key()` returns the metadata key for a bucket entrypoint, clearing `bucket_id` first when present so the entrypoint key addresses the logical bucket rather than a specific instance. `RGWSI_Bucket::get_bi_meta_key()` returns the bucket instance metadata key directly.

## Control Flow

`get_entrypoint_meta_key()` branches on whether `bucket.bucket_id` is empty. If empty, it returns `bucket.get_key()`. Otherwise, it copies the bucket, clears the instance id, and returns the logical key. `get_bi_meta_key()` is direct.

## State and Persistence Behavior

No state is stored. The returned keys are used by concrete services to locate bucket entrypoint and bucket instance metadata objects.

## Dependencies and Integration Points

It includes `svc_bucket.h` and relies on `rgw_bucket::get_key()`. `svc_bucket_sobj.cc` uses these helpers to map high-level bucket references to system object keys.

## Risks and Edge Cases

Incorrect key normalization would make reads/writes target a bucket instance when the entrypoint is intended, or vice versa. Tenant and bucket-id encoding depends on `rgw_bucket::get_key()` behavior.

## Test Signals

Unit tests should cover buckets with/without bucket ids and with tenants, and integration tests should verify entrypoint reads resolve to current bucket instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bucket.h

## Purpose

`svc_bucket.h` declares the abstract bucket metadata service. It is the interface for listing, reading, storing, removing, and statting bucket entrypoint and bucket instance metadata. The file was read as a complete 107-line header.

## Important APIs, Types, and Functions

`RGWSI_Bucket` derives from `RGWServiceInstance`. Static helpers are `get_entrypoint_meta_key()` and `get_bi_meta_key()`. Pure virtual methods create entrypoint/instance listers, read/store/remove `RGWBucketEntryPoint`, read/store/remove `RGWBucketInfo`, read bucket info by `rgw_bucket`, and read stats for one or many buckets.

## Control Flow

The header has no implementation flow. It defines the contract that concrete services must follow, including optional cache refresh versions, object version trackers, attrs, mtimes, coroutine yields, and debug prefix providers.

## State and Persistence Behavior

The interface itself stores no state. Implementations persist bucket entrypoints and bucket instance records and may maintain caches. Version trackers and refresh versions are part of optimistic consistency and cache validation semantics.

## Dependencies and Integration Points

It includes `driver/rados/rgw_service.h` and uses RGW bucket metadata types, version trackers, cache entry info, bufferlist attrs, and metadata listers. `RGWSI_Bucket_SObj` is the system-object implementation in this subset.

## Risks and Edge Cases

Implementations must distinguish entrypoint metadata from instance metadata and preserve versioning behavior. `store_bucket_instance_info()` has nuanced `orig_info` semantics: `nullopt` means not fetched, `nullptr` means known absent/new instance, and non-null points to previous info.

## Test Signals

Signals include mock-based users of the interface, concrete backend tests for read/store/remove/list/stat behavior, cache refresh tests, and bucket overwrite tests that verify `orig_info` handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sobj.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sobj.cc

## Purpose

`svc_bucket_sobj.cc` implements bucket metadata storage on top of RGW system objects. It reads and writes bucket entrypoints and bucket instance records in the local zone's domain root, maintains a chained bucket-info cache, completes metadata-log entries after writes, updates bucket sync hints, and delegates stats to the bucket-index service. The file was read as a complete 579-line implementation.

## Important APIs, Types, and Functions

Important helpers include `instance_meta_key_to_oid()` and `instance_oid_to_meta_key()` for `.bucket.meta.` object-name translation, `BucketEntrypointLister`, and `BucketInstanceLister`. Implemented service methods include `init()`, `do_start()`, lister creation, `read_bucket_entrypoint_info()`, `store_bucket_entrypoint_info()`, `remove_bucket_entrypoint_info()`, `read_bucket_instance_info()`, `do_read_bucket_instance_info()`, `read_bucket_info()`, `store_bucket_instance_info()`, `remove_bucket_instance_info()`, `read_bucket_stats()` overloads, and `read_buckets_stats()`.

## Control Flow

Startup initializes a `RGWChainedCacheImpl` for bucket info using the system object cache. Entrypoint listing scans the zone domain root with an empty prefix and filters out object names that start with `.`, while instance listing scans `.bucket.meta.` and converts oids back to metadata keys. Reads first consult the cache, validate refresh versions when supplied, and fall back to system-object reads plus decode. Logical bucket reads first load the entrypoint; if it contains embedded old bucket info, that is returned, otherwise the referenced bucket instance is read.

Writes encode metadata into bufferlists and store through `rgw_put_system_obj()`. Entrypoint writes/removes complete an mdlog entry with section `bucket`. Instance writes may fetch prior info, call `svc.bi->handle_overwrite()` when overwriting, write the instance object, complete mdlog section `bucket.instance`, and call `svc.bucket_sync->handle_bi_update()`. Instance removal deletes the system object and calls `handle_bi_removal()`, treating sync hint cleanup failures as nonfatal. Stats load bucket info then call the bucket-index service.

## State and Persistence Behavior

Bucket entrypoints are persisted as system objects in `zone_params.domain_root` under logical bucket keys. Bucket instances are persisted in the same pool under `.bucket.meta.<key>` oids, with tenant separator conversion between metadata key `tenant/bucket:instance` and object oid `tenant:bucket:instance`. The service caches bucket info and attrs/mtime with chained invalidation tied to system object cache entries. Object version trackers are stored in decoded `RGWBucketInfo` after instance reads and passed to write/delete operations.

## Dependencies and Integration Points

The implementation depends on zone, sysobj, sysobj cache, bucket index, mdlog, sync modules, bucket sync, bucket types, metadata listers, string utilities, RADOS tools, and zone config. It is a central integration point among bucket metadata persistence, mdlog replication, bucket sync policy indexes, bucket index logging, and cache coherency.

## Risks and Edge Cases

Cache inconsistency warnings trigger invalidation and recovery reads, but stale cache behavior remains high risk. The tenant separator conversion assumes bucket instance oids cannot contain optional shard suffixes and only rewrites the first colon when another colon exists. `store_bucket_instance_info()` must correctly distinguish exclusive creates, absent prior info, and fetched prior info; mistakes can skip `handle_overwrite()` or incorrectly reject races. `-EEXIST` on exclusive instance store is treated as success for multisite race tolerance. Metadata log completion happens after system object writes, so mdlog failures can make writes return errors after persistence has happened.

## Test Signals

Signals include unit tests for key/oid translation, lister filtering and marker behavior, cache hit/refresh/invalidation paths, read paths for embedded old bucket info versus instance objects, write paths with all `orig_info` variants, mdlog failure injection, bucket sync hint update/removal tests, multisite exclusive-create race tests, and stats delegation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sobj.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sobj.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sobj.h

## Purpose

`svc_bucket_sobj.h` declares the system-object-backed implementation of the bucket metadata service. The file was read as a complete 160-line header.

## Important APIs, Types, and Functions

`RGWSI_Bucket_SObj` derives from `RGWSI_Bucket`. It defines a private `bucket_info_cache_entry`, a `RGWChainedCacheImpl` pointer, private `do_start()`, `do_read_bucket_instance_info()`, and a `RGWBucketInfo`-based stats helper. Its `Svc` bundle stores dependencies on bucket service, bucket index, zone, sysobj, sysobj cache, mdlog, sync modules, and bucket sync. It overrides every abstract bucket metadata method from `RGWSI_Bucket`.

## Control Flow

The header defines service wiring and method contracts. Runtime flow is implemented in `svc_bucket_sobj.cc`: initialize dependencies, start cache, list/read/store/remove metadata objects, and delegate stats/sync/index side effects.

## State and Persistence Behavior

The class owns only cache state and service pointers. Persistent bucket metadata lives in zone domain-root system objects, while mdlog, bucket sync, and bucket index state are updated through dependent services.

## Dependencies and Integration Points

It includes `driver/rados/rgw_service.h`, `svc_bucket.h`, and `svc_bucket_sync.h`, and forward-declares zone/sysobj/cache/mdlog/sync-module classes. It integrates bucket metadata with cache, metadata log, bucket index, and sync policy handling.

## Risks and Edge Cases

Dependency initialization order matters because operations dereference several service pointers. Cache entry contents must stay aligned with `RGWBucketInfo` serialization and object attrs. The private read helper and public read methods need consistent version-refresh semantics.

## Test Signals

Compile coverage, service wiring tests, cache initialization tests, and concrete behavior tests through `svc_bucket_sobj.cc` are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sobj.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync.h

## Purpose

`svc_bucket_sync.h` declares the abstract bucket-sync service interface used by bucket metadata storage to maintain bucket-level sync policy handlers and bucket index sync hints. The file was read as a complete 52-line header.

## Important APIs, Types, and Functions

`RGWSI_Bucket_Sync` derives from `RGWServiceInstance`. It defines `RGWBucketSyncPolicyHandlerRef` as `std::shared_ptr<RGWBucketSyncPolicyHandler>` and declares pure virtual methods `get_policy_handler()`, `handle_bi_update()`, `handle_bi_removal()`, and `get_bucket_sync_hints()`.

## Control Flow

The header has no implementation flow. Concrete services provide policy handler lookup for optional zone/bucket scope, react to bucket-info updates/removals, and return source/destination sync hint buckets.

## State and Persistence Behavior

No state is stored in this interface. Implementations may persist sync hints or policies in system objects or indexes; `svc_bucket_sobj.cc` calls update/removal hooks after bucket instance mutations.

## Dependencies and Integration Points

It includes `driver/rados/rgw_service.h` and forward-declares `RGWBucketSyncPolicyHandler`. It integrates bucket metadata writes with multisite bucket sync policy evaluation and sync hint maintenance.

## Risks and Edge Cases

Bucket metadata writes depend on `handle_bi_update()` success, while removal treats `handle_bi_removal()` failures as nonfatal in the system-object implementation. Optional zone/bucket arguments require implementations to handle global, zone, and bucket-specific policies consistently.

## Test Signals

Signals include mock policy-handler tests, bucket instance update/removal integration tests, hint source/destination tests, and error-path tests for update failure versus removal failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_bucket_sync.h -->
