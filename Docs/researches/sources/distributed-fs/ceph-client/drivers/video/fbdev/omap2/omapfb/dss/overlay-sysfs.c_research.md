# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/overlay-sysfs.c

## Purpose
`overlay-sysfs.c` exposes OMAP DSS overlay controls in sysfs. It allows users to inspect and mutate overlay manager assignment, position, output size, enable state, global alpha, pre-multiplied alpha, and z-order.

## Important APIs, types, and functions
The public lifecycle APIs are `dss_overlay_kobj_init` and `dss_overlay_kobj_uninit`. Attribute handlers cover `name`, `manager`, `input_size`, `screen_width`, `position`, `output_size`, `enabled`, `global_alpha`, `pre_mult_alpha`, and `zorder`. `struct overlay_attribute`, `OVERLAY_ATTR`, `overlay_sysfs_ops`, and `overlay_ktype` provide sysfs dispatch.

## Control Flow
Kobject init creates `overlay%d`. Show/store dispatch maps the kobject back to `struct omap_overlay`. Manager store resolves a manager name, gets DISPC runtime PM, unsets the old manager and applies it, sets the new manager and applies it, then releases runtime PM. Geometry/alpha/zorder stores parse input, update the overlay info through `ovl->set_overlay_info`, and apply the attached manager if present. Enable store calls `ovl->enable` or `ovl->disable`.

## State and Persistence
State changes live in overlay info, manager attachment, hardware shadow registers, and DISPC state through `apply`. The sysfs object lifetime follows the overlay object. There is no persistence beyond runtime.

## Dependencies and Integration Points
It depends on OMAP overlay callbacks, manager apply paths, DISPC runtime PM, DSS feature/capability flags, kobject/sysfs APIs, and `dss_features.h`.

## Risks
Position and output-size parsing uses `simple_strtoul` and minimal separator validation. Manager reassignment error handling can leave an overlay detached or partially applied after old manager removal. Stores are mostly not serialized by a local lock. Unsupported capability attributes remain visible but return `-ENODEV`.

## Test Signals
Exercise all attributes, invalid geometry strings, capability-gated alpha/zorder on different overlays, manager attach/detach success and failure, enabled toggles, runtime PM failure paths, concurrent sysfs changes, and apply failures after geometry mutation.
