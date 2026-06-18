<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acpi.c

## Purpose
`amdgpu_acpi.c` implements amdgpu's ACPI integration. It detects and verifies AMD ATIF and ATCS methods, handles ACPI video and AC power notifications, routes SBIOS requests for brightness and dGPU display events, exposes ATCS calls for PCIe performance, SmartShift, power-shift control, and UMA allocation, enumerates ACPI XCC objects for NUMA/TMR memory information, and provides suspend-mode helpers for GPU reset policy.

The file owns global ACPI capability state for the driver and per-driver XCC topology state. It is not per-device for ATIF/ATCS; the detected handles and function masks live in a singleton `amdgpu_acpi_priv`.

## Important APIs, types, and functions
- ATIF helpers: `amdgpu_atif_call()`, `amdgpu_atif_verify_interface()`, `amdgpu_atif_get_notification_params()`, `amdgpu_atif_query_backlight_caps()`, `amdgpu_atif_get_sbios_requests()`, and `amdgpu_atif_handler()`.
- ATCS helpers: `amdgpu_atcs_call()`, `amdgpu_atcs_verify_interface()`, `amdgpu_acpi_is_pcie_performance_request_supported()`, `amdgpu_acpi_pcie_notify_device_ready()`, `amdgpu_acpi_pcie_performance_request()`, `amdgpu_acpi_power_shift_control()`, `amdgpu_acpi_smart_shift_update()`, and `amdgpu_acpi_set_uma_allocation_size()`.
- XCC/NUMA helpers: `amdgpu_acpi_enumerate_xcc()`, `amdgpu_acpi_get_xcc_info()`, `amdgpu_acpi_dev_init()`, `amdgpu_acpi_get_tmr_info()`, `amdgpu_acpi_get_mem_info()`, and `amdgpu_acpi_release()`.
- Device lifecycle: `amdgpu_acpi_detect()` scans display PCI devices for ATIF/ATCS and enumerates XCC ACPI devices; `amdgpu_acpi_init()` binds a backlight device and registers the ACPI notifier; `amdgpu_acpi_fini()` unregisters it.
- Power/reset helpers: `amdgpu_acpi_should_gpu_reset()`, `amdgpu_acpi_is_s3_active()`, and `amdgpu_acpi_is_s0ix_active()`.
- Optional ISP helper: `amdgpu_acpi_get_isp4_dev()` finds supported ACPI camera sensor devices when ISP support is enabled.

## Control flow
Global ACPI detection scans PCI display-class devices and tries to find `ATIF` and `ATCS` methods under their ACPI handles. Each found handle is verified by calling the interface verification method, parsing version, notification masks, and function masks. Detection then fetches ATIF notification parameters, optionally queries backlight transfer characteristics, and enumerates `AMD3000` through `AMD3023` XCC objects until the first missing HID.

Per-device ACPI init uses detected ATIF state. If brightness-change notification is supported, it selects a DC backlight device or legacy encoder backlight. It then registers `adev->acpi_nb`, whose callback handles AC adapter events through `amdgpu_pm_acpi_event_handler()` and forwards video-class events to `amdgpu_atif_handler()`.

ATIF event handling filters to the configured video notification code, reads pending SBIOS requests, applies brightness changes through the selected backlight device, and for dGPU display events on PX systems wakes runtime PM, emits HPD notification through DRM helper code, and returns `NOTIFY_BAD` to stop ACPI video keypress propagation.

ATCS call paths build method-specific input buffers. PCIe performance request first sends device-ready notification, then retries `ATCS_FUNCTION_PCIE_PERFORMANCE_REQUEST` while firmware reports in-progress. SmartShift maps driver/device lifecycle events to power-shift control states. UMA allocation sends index/type through the ATCS set-UMA method.

XCC enumeration evaluates DSM functions for supported function count, VF-to-XCC mapping, supported/current XCP mode, memory mode, and TMR base/size. It groups XCC entries by physical function SBDF and stores NUMA data from `_PXM` in an xarray keyed by proximity domain.

## State and persistence behavior
`amdgpu_acpi_priv` stores singleton ATIF and ATCS handles, function masks, notification configuration, current backlight device pointer, and backlight capability data. `amdgpu_acpi_dev_list` stores enumerated ACPI GPU device records, each with a list of XCC records. `numa_info_xa` stores allocated NUMA info by PXM.

State persists until global release. `amdgpu_acpi_fini()` only unregisters the per-device notifier; it does not clear global ATIF/ATCS or XCC state. `amdgpu_acpi_release()` frees NUMA and XCC/device lists. Backlight caps are copied out through `amdgpu_acpi_get_backlight_caps()`.

## Dependencies and integration points
The file depends on Linux ACPI, PCI, xarray, power supply, runtime PM, suspend state, ACPI video, ACPI NUMA, DRM backlight/display helpers, AMD ACPI method structure definitions from `amd_acpi.h`, atom display types, and optional AMD PMC/ISP configuration.

It integrates with display hotplug (`drm_helper_hpd_irq_event()`), DC and legacy backlight devices, amdgpu PM AC-event handling, device reset policy, SmartShift support, KFD/partition memory information through TMR/NUMA data consumers, and ACPI-notifier registration.

## Risks and edge cases
ATIF/ATCS state is global, so multi-GPU systems rely on the first detected handles and shared function masks. Error handling around ACPI buffers assumes the first two bytes are a size field before copying into packed output structs; firmware returning malformed buffers can produce `-EINVAL` or disabled notifications.

The PCIe performance request loop returns success after retries are exhausted even if the last return was still in-progress. That may be intentional firmware tolerance, but it is a behavioral edge. `amdgpu_acpi_detect()` initializes XCC lists and xarray each time it runs; repeated detect/release ordering must avoid leaks or stale global state.

Suspend policy is configuration-sensitive. S0ix requires APU, suspend-to-idle, Raven or newer, GFXOFF feature, low-power S0 FADT flag, and `CONFIG_AMD_PMC`; otherwise it logs once and returns false. Reset policy skips GPU reset for IMU-enabled APUs, APU S3, and SR-IOV VFs.

## Test signals
Useful signals include ATIF/ATCS detection in dmesg, correct function masks, working brightness changes from firmware events, HPD events on PX dGPU display events, AC power events updating PM state, successful PCIe performance requests, SmartShift power-shift notifications on load/D0/D3/unload, UMA allocation method success, correct TMR and NUMA info for XCC devices, clean ACPI notifier unregister, and no leaks after `amdgpu_acpi_release()`. Suspend tests should cover S3 and S0ix policy decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_acpi.c -->
