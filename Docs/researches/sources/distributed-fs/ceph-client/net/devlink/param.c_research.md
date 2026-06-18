
# sources/distributed-fs/ceph-client/net/devlink/param.c

## Purpose
This file implements devlink configuration parameters. It lets drivers register typed parameters, exposes them over generic netlink, validates user updates, stores driver-init values that take effect on reload, and sends notifications when parameter definitions or values change.

## Important APIs, Types, And Functions
`devlink_param_generic[]` is the built-in catalog of generic parameter IDs, names, and types, including SR-IOV enablement, region snapshot control, firmware-load policy, enablement toggles for RoCE/RDMA/VNET/iWARP/ETH/PHC, queue sizes, clock ID, VF totals, doorbell counts, and max MACs per VF.

Lookup helpers operate on `struct devlink`'s `params` xarray: `devlink_param_find_by_name()`, `devlink_param_find_by_id()`, and `devlink_param_get_from_info()`. Validation is split between `devlink_param_generic_verify()`, `devlink_param_driver_verify()`, and `devlink_param_verify()`.

Netlink read paths are `devlink_nl_param_get_doit()` and `devlink_nl_param_get_dumpit()`. They use `devlink_nl_param_fill()` to emit the parameter name, generic flag, type, supported cmodes, current values, and optional defaults. `devlink_nl_param_value_put()` handles all supported scalar, string, and bool encodings.

Netlink write flow is handled by `devlink_nl_param_set_doit()` through `__devlink_nl_cmd_param_set_doit()`. It validates the supplied type, parses `DEVLINK_ATTR_PARAM_VALUE_DATA`, calls a driver `validate` callback when provided, checks the requested configuration mode, and either stores a pending driver-init value or calls the driver's runtime `set`/`reset_default` callback.

Exported registration and driver-facing APIs include `devl_params_register()`, `devlink_params_register()`, `devl_params_unregister()`, `devlink_params_unregister()`, `devl_param_driverinit_value_get()`, `devl_param_driverinit_value_set()`, `devlink_params_driverinit_load_new()`, and `devl_param_value_changed()`.

## Control Flow
Drivers register parameters under the devlink lock. Registration verifies IDs/names, checks that driver-init-only parameters do not provide runtime get/set callbacks, inserts a `struct devlink_param_item` into `devlink->params`, and emits a `DEVLINK_CMD_PARAM_NEW` notification. Multi-parameter registration rolls back already inserted items if a later insert fails.

Reads iterate supported cmodes. For `DRIVERINIT`, values are served from cached `driverinit_value_new`, `driverinit_value`, and `driverinit_default` fields. For runtime modes, the driver `get` callback is called and, if available, `get_default` supplies default values.

Writes are deliberately two-path. Runtime cmodes call the driver immediately. Driver-init cmode only updates `driverinit_value_new` and marks it valid; `devlink_params_driverinit_load_new()` later promotes pending values into active driver-init values during reload-oriented flows.

## State And Persistence
State lives in memory in `devlink->params` and per-parameter `struct devlink_param_item`. Driver-init state is cached as current value, default value, pending new value, and validity flags. This is not disk persistence; it survives only for the lifetime of the devlink instance and is intended to influence driver initialization/reload.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, the devlink lock, xarray storage, generic netlink helpers, `devlink_nl_notify_send()`, and driver-provided callbacks in `struct devlink_param`. It integrates with reload support through `devlink_reload_supported()` and with command dispatch through generated `DEVLINK_CMD_PARAM_*` handlers.

Port parameter handlers are stubs that return unsupported, so this tree exposes device-level parameters here but not per-port params.

## Risks And Edge Cases
Driver parameter definitions are checked with `WARN_ON()` but registration can continue after warnings; invalid driver tables should be treated as driver bugs. Runtime multi-attribute writes can partially affect external hardware only through one parameter value, but failures inside driver callbacks must leave driver state coherent.

String values are copied only if NUL-terminated and shorter than `__DEVLINK_PARAM_MAX_STRING_VALUE`. Bool values use flag encoding, with defaults encoded as `u8` so false can be distinguished from absence. Driver-init pending values are visible as the effective value before reload, which can surprise callers expecting hardware state rather than requested next-init state.

## Test Signals
Devlink parameter behavior is exercised indirectly by drivers in this repository that register generic params, such as `zl3073x` using `CLOCK_ID`, and by driver reload paths that call `devl_param_driverinit_value_get()`. Useful tests are netlink get/set/reset-default for every type, driver-init promotion across reload, duplicate name/ID registration, and notification replay on devlink registration/unregistration.
