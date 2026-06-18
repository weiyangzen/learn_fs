# sources/distributed-fs/ceph-client/drivers/video/backlight/qcom-wled.c

Purpose: Qualcomm PMIC WLED backlight driver for WLED3, WLED4, and WLED5 blocks. It configures boost/current/OVP parameters, LED string sinks, brightness modulators, CABC, short detection, and OVP-triggered string auto-detection.

Important APIs/types/functions: `struct wled` is the central device state; `struct wled_config` holds parsed DT configuration. Version hooks include `wled3/4/5_set_brightness()`, `wled3_sync_toggle()`, `wled5_mod_sync_toggle()`, `wled4/5_cabc_config()`, `wled4/5_ovp_delay()`, and `wled4/5_auto_detection_required()`. Probe uses parent `regmap`, OF match data, `wled_configure()`, version setup, IRQ setup, delayed work, and `devm_backlight_device_register()`.

Control flow: `wled_configure()` selects defaults and option tables by hardware version, reads register base addresses from OF resources, validates enumerated properties, and parses enabled strings. Version setup writes OVP, boost/current limits, switching frequency, sink enables, modulator source, CABC, and brightness width. Backlight `update_status` sets brightness, toggles sync, enables/disables the module on zero/nonzero transitions, and stores current brightness under a mutex. Short IRQ temporarily disables and retries the module, permanently disabling after repeated faults. OVP IRQ can run auto string detection, which tests each sink at low brightness and rewrites valid sink configuration.

State and persistence: volatile state includes brightness, fault counters, `disabled_by_short`, delayed OVP work, CABC disable latch, and parsed config. PMIC registers retain programmed settings.

Dependencies and integration: platform child of a Qualcomm PMIC with regmap, OF resource addresses, optional `short`/`ovp` IRQs, Linux backlight core, delayed work, and mutex serialization.

Risks: probe never calls `platform_set_drvdata()`, but remove dereferences `platform_get_drvdata()`, so unbind can crash. `wled5_ovp_delay()` appears inverted: successful `regmap_read()` leaves `val` used only in the failure branch and otherwise returns the fallback delay. Some setup errors inside loops are not checked immediately after every update. Test signals include all compatible versions, invalid DT enum values, string bounds, IRQ storm handling, auto-detection under OVP faults, unbind, and zero-brightness transitions.
