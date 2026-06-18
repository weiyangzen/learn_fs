# sources/distributed-fs/ceph/src/rgw/driver/rados/config/store.h

Purpose: Declares `RadosConfigStore`, the RADOS-backed implementation of `sal::ConfigStore` for RGW multisite realms, periods, zonegroups, zones, period config, and realm watchers.

Important APIs/types/functions: The class overrides default-id read/write/delete for realms, zonegroups, and zones; create/read/list operations for realms, periods, zonegroups, and zones; writer factory returns through SAL writer pointers; `realm_notify_new_period()` and `create_realm_watcher()` handle dynamic reconfiguration; `read_period_config()` and `write_period_config()` handle period config. `create_config_store()` is the factory.

Control flow: The header defines the high-level SAL contract; implementation is split across entity-specific `.cc` files that share one private `ConfigImpl`.

State/persistence: All persistent state is behind `ConfigImpl` and stored in configured RADOS root pools. The class owns exactly one `unique_ptr<ConfigImpl>`.

Dependencies/integration: Includes `rgw_common.h` and `rgw_sal_config.h`, tying this implementation to SAL config abstractions and RGW metadata types such as `RGWRealm`, `RGWPeriod`, `RGWZoneGroup`, `RGWZoneParams`, and `RGWPeriodConfig`.

Risks: Because implementation is distributed across many files, interface changes in `sal::ConfigStore` require synchronized updates. The class exposes multi-object entity operations that are only partially transactional in implementations.

Test signals: Compile all overrides against SAL, exercise each factory/writer path through the interface, and verify persistence layout with integration tests against a RADOS cluster or mock.
