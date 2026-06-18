# Research: sources/distributed-fs/ceph-client/drivers/usb/common/common.c

Purpose: provides exported USB helper functions shared by host and gadget stacks. It formats endpoint, OTG, speed, and device states; parses firmware properties for maximum speed, SuperSpeedPlus rate, dual-role mode, and default role-switch mode; decodes endpoint intervals; supplies OF helpers for OTG/PHY relationships; and initializes shared USB debugfs and optional LED triggers.

Important APIs: exported helpers include `usb_ep_type_string`, `usb_otg_state_string`, `usb_speed_string`, `usb_get_maximum_speed`, `usb_get_maximum_ssp_rate`, `usb_state_string`, `usb_get_dr_mode`, `usb_get_role_switch_default_mode`, `usb_decode_interval`, `of_usb_get_dr_mode_by_phy`, `of_usb_host_tpl_support`, `of_usb_update_otg_caps`, and `usb_of_get_companion_dev`. It exports globals `usb_debug_root` and `usb_dynids_lock`.

Control flow: most functions are bounded table lookups or property readers. `usb_decode_interval` converts endpoint `bInterval` to microseconds based on endpoint type and speed. OF helper `of_usb_get_dr_mode_by_phy` scans available controller nodes with `phys`, matches the requested PHY node and argument, then reads that controller's `dr_mode`. `of_usb_update_otg_caps` validates `otg-rev` and applies `hnp-disable`, `srp-disable`, and `adp-disable` properties. `usb_common_init` creates `/sys/kernel/debug/usb` and registers LED triggers; exit reverses this.

State and persistence: no persistent state. Runtime globals are the debugfs root dentry and the dynamic ID mutex. Property-derived values are returned to callers and not cached here.

Dependencies and integration points: depends on generic device properties, OF, platform-device lookup, debugfs, USB chapter 9 definitions, OTG data structures, and optional LED trigger hooks declared in `common.h`. It is foundational for other USB core files such as `devices.c`, tracepoints, host controller drivers, gadget drivers, and DT/ACPI described controllers.

Risks: property string matching is strict, so firmware spelling errors fall back to unknown modes. `of_usb_get_dr_mode_by_phy` assumes it finds a controller before the `finish` path reads properties; changes here need careful null handling. Interval decoding must remain aligned with USB spec rules or user-visible diagnostics and scheduler decisions become misleading. `usb_debug_root` lifetime matters for child debugfs users.

Test signals: unit-style tests can exercise table fallbacks, invalid speeds/states, interval decoding for control/bulk/int/isoc endpoints at low/full/high/super speeds, DT fixtures for `maximum-speed`, SSP rate, `dr_mode`, `role-switch-default-mode`, and OTG capability properties, plus debugfs/LED trigger init-exit smoke tests.
