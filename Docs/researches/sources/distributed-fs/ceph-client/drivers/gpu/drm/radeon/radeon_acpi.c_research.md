# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_acpi.c

## Purpose

`radeon_acpi.c` implements the Radeon driver's ACPI integration for AMD ATIF and ATCS methods. It verifies firmware-provided ACPI interfaces, records supported ATIF/ATCS features in `struct radeon_device`, registers an ACPI notifier, handles selected ACPI power/display events, forwards AC power changes into Radeon power management, handles SBIOS brightness and dGPU display events, and exposes helpers for PCIe performance requests through ATCS.

## Important APIs, types, and functions

Local packed ACPI buffer structures mirror firmware layouts: `atif_verify_interface`, `atif_system_params`, `atif_sbios_requests`, `atcs_verify_interface`, `atcs_pref_req_input`, and `atcs_pref_req_output`.

Important internal functions include `radeon_atif_call()`, `radeon_atcs_call()`, ATIF/ATCS parser and verifier helpers, `radeon_atif_get_notification_params()`, `radeon_atif_get_sbios_requests()`, `radeon_atif_handler()`, and `radeon_acpi_event()`.

Exported functions are `radeon_acpi_init()`, `radeon_acpi_fini()`, `radeon_acpi_is_pcie_performance_request_supported()`, `radeon_acpi_pcie_notify_device_ready()`, and `radeon_acpi_pcie_performance_request()`.

## Control flow and lifecycle

`radeon_acpi_init()` obtains the ACPI handle, exits harmlessly if the device is not AVIVO-class or lacks BIOS/ACPI support, verifies ATCS, verifies ATIF, finds a backlight-capable LCD encoder when brightness notifications are supported, reads notification configuration, and registers an ACPI notifier.

`radeon_acpi_event()` receives ACPI bus events. AC adapter events call `radeon_pm_acpi_event_handler(rdev)`. Video events are filtered by `radeon_atif_handler()` against the configured ATIF command code, then pending SBIOS requests are read. Brightness requests update the Radeon encoder backlight and force a backlight hotkey update. dGPU display events on PX systems runtime-resume the GPU, emit a DRM HPD event, and autosuspend again. Consumed ATIF events return `NOTIFY_BAD` to stop generic video propagation.

The ATCS PCIe performance request helper validates support, fills a packed request using the PCI client ID and requested link speed, retries while firmware reports in-progress, and returns success, `-EINVAL`, or `-EIO` depending on firmware status.

## State and persistence behavior

Persistent state is stored on `struct radeon_device`: `rdev->atif.notifications`, `rdev->atif.functions`, `rdev->atif.notification_cfg`, `rdev->atif.encoder_for_bl`, `rdev->atcs.functions`, and `rdev->acpi_nb`. ACPI method return buffers are allocated through `ACPI_ALLOCATE_BUFFER` and freed with `kfree()`. Runtime PM references around dGPU display events are transient and balanced with autosuspend.

## Dependencies and integration points

Kernel dependencies include ACPI core, ACPI video/bus events, PCI helpers, runtime PM, power supply, backlight, slab allocation, and DRM probe helper HPD notification. Radeon dependencies include `atom.h`, `radeon.h`, `radeon_acpi.h`, `radeon_pm.h`, display encoder private structs, `radeon_set_backlight_level`, `rdev_to_drm`, `ASIC_IS_AVIVO`, `RADEON_IS_PX`, and `radeon_pm_acpi_event_handler`. VGA switcheroo integration is through `radeon_atpx_dgpu_req_power_for_displays()` when configured.

## Risks and edge cases

Firmware buffers are dereferenced for their size fields and then copied into packed structs, so malformed ACPI objects are a robustness risk. `radeon_acpi_init()` registers the notifier even after ATIF verification failure; current zeroed state should filter events, but the lifecycle is notable. PCIe performance requests return success after all retries report `IN_PROGRESS`, which may mask an incomplete link-speed change. Backlight handling depends on cached encoder private data remaining valid until notifier unregister. Returning `NOTIFY_BAD` suppresses generic video notification propagation and depends on correct command-code configuration.

## Test signals

Useful tests include booting systems with and without ATIF/ATCS, AC adapter plug/unplug PM transitions, brightness hotkeys on ATIF laptops, PX dGPU display notifications and runtime PM balance, PCIe DPM/device-ready requests, suspend/resume and module unload notifier teardown, plus fault injection for missing methods, short buffers, refused ATCS requests, and repeated in-progress responses.
