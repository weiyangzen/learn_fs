# sources/distributed-fs/ceph-client/drivers/platform/arm64/acer-aspire1-ec.c

Purpose: I2C embedded-controller driver for Snapdragon-based Acer Aspire 1. It reconstructs platform services not exposed through standard firmware interfaces: battery and AC power supplies, lid switch input, Fn-lock sysfs control, and USB-C DisplayPort HPD via a DRM bridge.

Important APIs, types, and functions: `struct aspire_ec` holds the I2C client, two power supplies, input device, DRM bridge, and HPD work. `aspire_ec_ram_read()`/`aspire_ec_ram_write()` access EC RAM commands. `aspire_ec_irq_handler()` dispatches EC event IDs. `aspire_ec_bat_psy_get_property()` and `aspire_ec_adp_psy_get_property()` expose `power_supply` properties. `aspire_ec_bridge_hpd_enable()` schedules initial HPD readback, and `fn_lock_show()`/`fn_lock_store()` expose keyboard mode state.

Control flow: probe allocates the DRM bridge-embedded private struct, registers battery and mains power supplies, registers an input device for `SW_LID`, programs keyboard Fn/media notification bits in EC RAM, optionally registers a child-node-backed USB connector bridge, then requests a threaded IRQ. IRQ handling waits briefly after resume-prone interrupts, reads `ASPIRE_EC_EVENT`, and handles watchdog clear, lid events, fuel-gauge changes, HPD connect/disconnect, and ignored keyboard/backlight events. Resume reads the lid status RAM byte and reports switch state.

State and persistence: persistent state lives in EC RAM, including watchdog, keyboard mode, HPD status, lid status, and adapter status registers. Kernel state tracks whether the DRM bridge is configured. Fn-lock writes persist at least until EC state changes or reset. Power-supply properties are read live from static/dynamic EC fuel-gauge blocks and converted from milli-units to micro-units.

Dependencies and integration points: uses I2C SMBus, input, power_supply, DRM bridge/HPD, OF child node `connector`, threaded IRQ, and simple PM ops. Device IDs are `aspire1-ec` and OF compatible `acer,aspire1-ec`.

Risks and edge cases: low-level RAM read/write helpers ignore SMBus return values and always report success, so read failures can propagate as stale stack data. Capacity computation divides by `capacity_full` without explicit zero guard. HPD work is scheduled but no explicit cancellation is visible on remove, relying on devm lifetime and short work. Lid resume reports `!!(tmp & ASPIRE_EC_LID_OPEN)` directly as `SW_LID`, while IRQ close/open reports `1` for closed and `0` for open; this polarity merits hardware validation. Event handling contains several no-op known events.

Test signals: hardware tests should verify battery status/capacity/current, AC online changes, Fn-lock sysfs read/write, lid switch polarity across IRQ and resume, DP HPD notifications with a Type-C display, and watchdog event clearing. Fault tests should simulate SMBus errors if possible.
