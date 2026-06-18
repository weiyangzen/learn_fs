# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/Kconfig

Purpose: This Kconfig file exposes the legacy Radeon DRM/KMS driver and optional userptr support.

Important APIs, types, and functions: `DRM_RADEON` is a tristate depending on `DRM`, `PCI`, and `AGP || !AGP`. It selects firmware loading, DRM/KMS/display helpers, TTM/DRM_EXEC, framebuffer I/O helpers, sound HDA component integration, power supply, hwmon, backlight, interval trees, I2C/algobit, and ACPI video/WMI dependencies when applicable. `DRM_RADEON_USERPTR` selects `MMU_NOTIFIER`.

Control flow: Build-time only. Enabling `DRM_RADEON` includes the Radeon driver object list; enabling userptr forces full user pointer invalidation support through MMU notifier.

State and persistence: No runtime state. The selected dependencies determine compiled-in feature support for firmware, memory management, display, audio, power, and ACPI integration.

Dependencies and integration points: Integrates the Radeon driver with PCI/AGP, DRM KMS, TTM, display helpers, fbdev emulation, HDA audio, power/hwmon/backlight, I2C, and ACPI subsystems.

Risks: Select chains are broad; changing them can produce missing symbols or feature regressions on ACPI/x86, audio, backlight, or userptr configurations. The userptr option changes MMU notifier dependency and memory invalidation behavior.

Test signals: Build matrix for built-in/module, AGP enabled/disabled, ACPI x86/non-x86, fbdev emulation, HDA, and userptr; boot on representative Radeon ASICs and verify firmware loading/display/audio/power hooks.
