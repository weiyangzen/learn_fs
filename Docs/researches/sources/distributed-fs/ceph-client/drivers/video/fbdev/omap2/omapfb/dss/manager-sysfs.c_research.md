# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/manager-sysfs.c

## Purpose
`manager-sysfs.c` exposes OMAP DSS overlay manager attributes under sysfs. It lets users inspect manager names and attached displays and mutate manager-level display attachment, default color, transparency keying, alpha blending, and color phase rotation coefficients.

## Important APIs, types, and functions
The public lifecycle functions are `dss_manager_kobj_init` and `dss_manager_kobj_uninit`. Attribute handlers include `manager_display_store`, default color, transparency type/value/enabled, alpha blending, CPR enable, and CPR coefficient show/store functions. `struct manager_attribute`, `MANAGER_ATTR`, `manager_sysfs_ops`, and `manager_ktype` implement the kobject dispatch.

## Control Flow
Kobject init creates `manager%d` under the DSS platform device. Show/store dispatch converts from kobject to `struct omap_overlay_manager`. Most stores fetch current manager info, parse sysfs input with `kstrto*`, `sysfs_match_string`, or `sscanf`, update one field, call `mgr->set_manager_info`, then `mgr->apply`. Display store finds the named display, verifies new and old displays are disabled, disconnects the old display, connects the new one, verifies it landed on this manager, and applies the config.

## State and Persistence
State is stored in manager objects and lower DISPC shadow/hardware state through `set_manager_info` and `apply`. Sysfs kobject lifetime is tied to overlay manager lifetime. No settings persist across driver unload or reboot except through whatever userspace reapplies.

## Dependencies and Integration Points
The file depends on `omapfb_dss.h` manager/display APIs, DSS feature flags for alpha/CPR support, sysfs/kobject APIs, and display driver connect/disconnect callbacks.

## Risks
Most stores are not protected by a file-local lock, relying on lower layers. `manager_display_store` may leave the old display disconnected if new connect or apply fails. CPR parsing uses `sscanf` and enforces coefficient range after parsing. Feature-gated attributes still exist but return `-ENODEV` on unsupported hardware.

## Test Signals
Exercise all sysfs attributes, invalid strings/ranges, unsupported feature returns, display reassignment while enabled versus disabled, failure injection around connect/apply, CPR coefficient boundary values, and concurrent sysfs/ioctl display configuration.
