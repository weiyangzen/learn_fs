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
