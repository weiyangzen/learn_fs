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
