# sources/distributed-fs/ceph-client/net/devlink/dev.c

## Purpose

`dev.c` implements top-level devlink device netlink operations and helper APIs: instance dumps, reload, nested devlink reporting, eswitch configuration, device info/version reporting, firmware flash update, compatibility helpers, and selftests.

## Important APIs, Types, and Functions

Key handlers include `devlink_nl_get_doit()`, `devlink_nl_get_dumpit()`, `devlink_nl_reload_doit()`, `devlink_nl_eswitch_get_doit()`, `devlink_nl_eswitch_set_doit()`, `devlink_nl_info_get_doit()`, `devlink_nl_info_get_dumpit()`, `devlink_nl_flash_update_doit()`, `devlink_nl_selftests_get_doit()`, `devlink_nl_selftests_get_dumpit()`, and `devlink_nl_selftests_run_doit()`. Exported helpers include `devl_nested_devlink_set()`, `devlink_is_reload_failed()`, `devlink_remote_reload_actions_performed()`, `devlink_info_*_put()`, `devlink_flash_update_status_notify()`, `devlink_flash_update_timeout_notify()`, `devlink_compat_running_version()`, and `devlink_compat_flash_update()`.

## Control Flow

Device GET fills the devlink handle, reload failure bit, local and remote reload stats, and nested devlink handles. Register/unregister notification fans out to linecards, ports, traps, rates, regions, and params in a defined order. Reload validates resources, requested action, limit, and optional target namespace, then calls driver `reload_down()`, changes namespace if requested, reloads driverinit params and sanity-checks empty reinit-only object lists for driver reinit, calls `reload_up()`, updates failure state, verifies actions performed, and increments stats. Flash update validates optional component support by probing `info_get()` versions, requests firmware, emits begin/end/status notifications, and calls driver `flash_update()`. Selftests advertise supported test IDs and run selected tests with per-test result attributes.

## State and Persistence Behavior

Persistent devlink state touched here includes `reload_failed`, local and remote reload stat arrays, nested relationship xarray entries, net namespace pointer, and driverinit parameter state. Firmware pointers are transient and released after flash update. Info reporting is callback driven and stateless except for optional version callback collection used for component validation and compatibility running-version strings.

## Dependencies and Integration Points

The file depends on `struct devlink_ops` callbacks for reload, eswitch, info, flash, and selftests. It integrates with net namespace lookup/capability checks, firmware loader, generic netlink replies and multicast notifications, devlink resources, params, rates, and nested relationship support from `core.c`.

## Risks

Reload is sensitive because it may change namespaces and expects device lock ownership. Drivers must report performed actions consistently and must not update remote stats during local reload. Flash update component validation depends on version names and types reported by `info_get()`. Selftest run previously parsed nested requested flags; missing attribute checks can lead to unexpected skips. Notification order matters for userspace object tracking.

## Test Signals

Test reload with default and explicit action/limit, invalid action-limit combinations, namespace moves, reload failure state toggling, remote reload stat updates, eswitch get/set with absent callbacks, info version nesting, flash firmware lookup and unsupported component errors, overwrite mask support, compatibility flash path, and selftest get/run skip/pass/fail statuses.
