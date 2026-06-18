# sources/distributed-fs/ceph/src/rgw/driver/immutable_config/store.h

## Purpose

This header declares `rgw::sal::ImmutableConfigStore`, a read-only implementation of the RGW `ConfigStore` abstraction. It exposes a full override surface for realm, period, zonegroup, zone, and period-config operations while documenting that the store serves a given default zonegroup and zone.

## Important APIs, Types, and Functions

- `ImmutableConfigStore` derives from `ConfigStore`.
- The constructor accepts `const RGWZoneGroup&`, `const RGWZoneParams&`, and `const RGWPeriodConfig&`.
- Realm API overrides cover default realm id read/write/delete, realm create/read by id/read by name/read default/read id, period notification, watcher creation, and realm-name listing.
- Period API overrides cover create/read/delete/list/update latest epoch.
- ZoneGroup API overrides cover default zonegroup id read/write/delete, create/read by id/read by name/read default, and list names.
- Zone API overrides cover default zone id read/write/delete, create/read by id/read by name/read default, and list names.
- PeriodConfig API overrides cover read and write.
- Private state is three const value members: `zonegroup`, `zone`, and `period_config`.
- `create_immutable_config_store()` is the public factory returning `std::unique_ptr<ConfigStore>`.

## Control Flow

The header describes the contract implemented in the `.cc`: callers interact through the generic `ConfigStore` interface, while construction fixes the only zonegroup, zone, and period config available. Optional writer out-parameters are supported by the signatures, allowing immutable writer wrappers to be returned where reads succeed.

## State and Persistence Behavior

The declared state is immutable after construction and has no persistent backing store. Because the members are const value copies, callers cannot observe later changes to the original objects passed into the constructor.

## Dependencies and Integration Points

The header depends on `rgw_sal_config.h` for `ConfigStore`, writer interfaces, `ListResult`, and `optional_yield`; and `rgw_zone.h` for `RGWZoneGroup`, `RGWZoneParams`, `RGWPeriod`, `RGWRealm`, and `RGWPeriodConfig`. It is consumed by the implementation and by `json_config/store.h` as the factory target for parsed JSON config.

## Risks and Edge Cases

- The class advertises the entire `ConfigStore` surface, but the implementation intentionally supports only a narrow single-zone subset. Callers must be prepared for `-EROFS`, `-ENOENT`, or `-ENOTSUP`.
- Value-copying potentially makes large config structures more expensive but keeps lifetime simple.
- Because private members are const, runtime reconfiguration requires constructing a new store.

## Test Signals

The header has no standalone tests. Its testability hinges on interface-conformance builds and behavioral tests against the factory and read-only methods.
