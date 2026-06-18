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
