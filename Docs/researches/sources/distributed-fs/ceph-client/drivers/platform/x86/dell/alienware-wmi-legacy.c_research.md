# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/alienware-wmi-legacy.c

Purpose: Legacy Alienware WMI backend for `LEGACY_CONTROL_GUID` AlienFX systems.

Important APIs/types/functions: `struct legacy_led_args`, `legacy_wmi_update_led()`, `legacy_wmi_update_brightness()`, `legacy_wmi_probe()`, and the WMI driver registration functions.

Control flow/state/persistence: Probe passes legacy LED operations to the base AlienFX setup. Zone writes call WMI method `location + 1`; brightness refreshes zone 0. The shared `alienfx_priv` holds requested color/brightness/control state, while firmware applies actual LED state.

Dependencies/integration: ACPI WMI and the base Alienware module, including `LEGACY_CONTROL_GUID` and `LEGACY_POWER_CONTROL_GUID`.

Risks/test signals: The state/power-control path is subtle and model-specific. Test per-zone color, global brightness, booting/running/suspend state, multi-device probing with `no_singleton=true`, and unregister.
