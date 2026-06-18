# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/display-sysfs.c

## Purpose

`display-sysfs.c` creates legacy per-display sysfs attributes for OMAP DSS devices. The complete 347-line source was read. It exposes display identity, enabled state, TE, timings, rotation, mirror, and WSS controls by routing sysfs operations to `omap_dss_driver` callbacks.

## Important APIs, Types, and Functions

Show/store helpers include `display_name_show()`, `display_enabled_show/store()`, `display_tear_show/store()`, `display_timings_show/store()`, `display_rotate_show/store()`, `display_mirror_show/store()`, and `display_wss_show/store()`. `struct display_attribute` wraps a sysfs attribute with DSS show/store callbacks. `display_init_sysfs()` creates a kobject per registered display, and `display_uninit_sysfs()` removes them.

## Control Flow

Compatibility init calls `display_init_sysfs()`, which iterates all displays with `for_each_dss_dev()` and creates kobjects under the DSS platform device kobject using display aliases. Sysfs read/write dispatch uses `container_of()` to recover the DSS device and selected display attribute. Enabling writes call driver `enable()` or `disable()` after parsing booleans. Timing writes parse PAL/NTSC aliases when VENC is enabled or numeric timing strings, check timings, disable the display, set timings, then re-enable it.

## State and Persistence Behavior

The sysfs layer owns only the kobject lifecycle. Actual display state remains in each `omap_dss_device` and panel/output driver. Timings, rotate, mirror, and WSS writes persist only in those driver states or hardware until changed/unbound.

## Dependencies and Integration Points

It depends on display registration from `display.c`, driver callback completeness, sysfs/kobject APIs, `kstrtox`, and optional VENC timing constants. It is initialized and removed by `omapdss_compat_init()` / `uninit()` in `apply.c`.

## Risks and Edge Cases

The timing store path disables before setting timings and attempts to re-enable; if enable fails, the display remains off. Attribute availability is dynamic: unsupported callbacks return `-ENOENT`. There is no central display mutex here, so serialization relies on lower drivers. Kobject cleanup zeroes the embedded kobject after put, which assumes no outstanding sysfs references beyond normal kobject lifetime rules.

## Test Signals

Signals include sysfs read/write for every attribute, unsupported callback paths returning `-ENOENT`, invalid timing parsing, timing change failure recovery, enable writes on disconnected displays, PAL/NTSC parsing under VENC builds, and init/uninit with multiple registered displays.
