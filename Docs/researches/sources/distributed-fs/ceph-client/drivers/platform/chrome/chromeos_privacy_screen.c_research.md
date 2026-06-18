# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_privacy_screen.c

Purpose: ACPI DRM privacy-screen provider for ChromeOS devices exposing electronic privacy screens via GOOG0010 and a firmware `_DSM` interface.

Important APIs, types, and functions: `chromeos_privacy_screen_get_hw_state()` calls `_DSM` function 1 to read status. `chromeos_privacy_screen_set_sw_state()` calls `_DSM` functions 2 or 3 to enable or disable. `chromeos_privacy_screen_ops` registers those callbacks with `drm_privacy_screen_register()`.

Control flow: probe registers a DRM privacy screen tied to the platform device and stores the returned object as driver data. DRM consumers call the ops to read or set state; set validates requested state and updates both `hw_state` and `sw_state` after firmware accepts. Remove unregisters the privacy screen.

State and persistence: authoritative state is in firmware/privacy-screen hardware. The DRM privacy-screen object caches software and hardware state after reads/writes. No module-level state.

Dependencies and integration points: depends on ACPI and DRM privacy-screen framework. i915 and other DRM drivers may defer until this provider registers. ACPI match ID is `GOOG0010`; DSM GUID and function numbers are contract with ChromeOS firmware.

Risks and edge cases: get failure logs but leaves cached state unchanged. set treats any non-NULL `_DSM` result as success without validating object type or return value. Unsupported status values other than integer 1 are treated as disabled. Build help recommends built-in use to avoid DRM probe deferral latency.

Test signals: verify provider registration before display driver privacy-screen lookup, successful get/set over ACPI DSM, bad DSM object handling, and DRM userspace privacy-screen state transitions.
