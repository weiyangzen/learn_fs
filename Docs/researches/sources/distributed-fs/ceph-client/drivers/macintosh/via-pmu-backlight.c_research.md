# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-backlight.c

Purpose: registers a platform backlight device that controls PowerBook/iBook display brightness through PMU commands.

Important APIs and functions: `pmu_backlight_init_curve()` builds a firmware brightness curve; `pmu_backlight_curve_lookup()` maps autosaved PMU values back to framebuffer levels; `pmu_backlight_get_level_brightness()` converts framebuffer backlight levels to PMU values. `pmu_backlight_update_status()` serializes updates and calls `__pmu_backlight_update_status()` to issue `PMU_BACKLIGHT_BRIGHT` and `PMU_POWER_CTRL` commands. `pmu_backlight_set_sleep()` suppresses updates during suspend. `pmu_backlight_init()` registers the backlight device.

Control flow: init checks supported machine/backlight types, registers `pmubl`, initializes the curve, optionally reads an autosaved brightness on older PowerBooks, sets max brightness as default, marks power on, and updates hardware. Runtime backlight changes call into PMU synchronously unless sleeping.

State and persistence: globals include `sleeping`, `uses_pmu_bl`, the PMU conversion curve, and a spinlock. Hardware brightness/power state persists in the PMU/display hardware; kernel state is rebuilt at boot.

Dependencies and integration: depends on PMU request APIs from `via-pmu.c`, generic backlight framework, PMac backlight globals/helpers, OF machine matching, and suspend hooks.

Risks: PMU requests are sent while holding `pmu_backlight_lock`, so interactions with PMU completion paths must remain non-recursive. Brightness curve constants are hardware-specific. Autosave command `0xd9` is magic and old-model-specific.

Test signals: backlight device registration only on supported machines, brightness level scaling, off/on power commands at zero/nonzero brightness, autosaved level restore on 3400/2400/3500 models, suspend turning backlight off, and resume restoring prior brightness.
