# sources/distributed-fs/ceph-client/include/drm/drm_module.h

Purpose: declares module registration helpers for DRM PCI and platform drivers that honor the global DRM firmware-driver-only policy and, for older users, a driver-specific modeset parameter.

Important APIs and types: `drm_pci_register_driver()` wraps `pci_register_driver()` and returns `-ENODEV` when `drm_firmware_drivers_only()` is active. `drm_module_pci_driver()` plugs that wrapper into `module_driver()`. `drm_pci_register_driver_if_modeset()` additionally rejects registration when a deprecated `modeset` parameter is disabled or when firmware-only mode and default modeset policy conflict; `drm_module_pci_driver_if_modeset()` exposes that legacy behavior. `drm_platform_driver_register()` and `drm_module_platform_driver()` provide the platform-bus equivalent.

Control flow: at module init, generated `module_driver()` code calls the DRM wrapper instead of raw bus registration. If policy allows, normal PCI/platform driver registration proceeds; otherwise init fails with `-ENODEV`. Module exit unregisters through the standard bus unregister function.

State and persistence behavior: this header does not own runtime state. It reads global DRM policy and optional driver modeset parameter at module initialization time.

Dependencies and integration points: includes Linux PCI and platform driver APIs plus `drm_drv.h` for `drm_firmware_drivers_only()`. It is used directly in DRM driver module source files instead of `module_pci_driver()` or `module_platform_driver()`.

Risks: each macro replaces explicit `module_init()`/`module_exit()` and can only be used once per module. The `_if_modeset` helper is deprecated and preserves legacy parameter semantics that new drivers should avoid. Firmware-only policy can make a driver appear absent even though the module loaded.

Test signals: module init with firmware-driver-only enabled/disabled, modeset parameter values `0`, `-1`, and enabled, PCI and platform unregister paths, and build coverage for drivers using the macros.
