<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.c

## Purpose
`omap_device.c` bridges Linux platform devices to OMAP hwmod power/clock/reset metadata. It builds `struct omap_device` wrappers from DT `ti,hwmods`, creates clkdev aliases, attaches PM domains, handles runtime/system PM, exposes reset helpers, and idles unbound devices late in boot.

## Important APIs, Types, and Functions
Public APIs are `omap_device_enable()`, `omap_device_idle()`, `omap_device_assert_hardreset()`, and `omap_device_deassert_hardreset()`. Important internals include `omap_device_build_from_dt()`, `_omap_device_notifier_call()`, `_omap_device_enable_hwmods()`, `_omap_device_idle_hwmods()`, `omap_device_alloc()`, `omap_device_delete()`, `_od_runtime_suspend()`, `_od_runtime_resume()`, `_od_suspend_noirq()`, `_od_resume_noirq()`, `omap_device_pm_domain`, `omap_device_fail_pm_domain`, and late idle initcalls.

## Control Flow
A postcore initcall registers a platform-bus notifier. On device add, DT nodes with `ti,hwmods` are converted into `omap_device` wrappers unless the node is handled by `ti-sysc` or is special SDMA. The builder looks up hwmods, allocates wrapper state, fixes resource names, creates clock aliases, and attaches a PM domain. Runtime resume enables all hwmods before generic resume; runtime suspend runs generic suspend then idles hwmods. Noirq suspend idles still-active bound devices and marks them suspended for resume. On driver unbind or late init, enabled devices without drivers are idled unless marked `HWMOD_INIT_NO_IDLE`.

## State and Persistence Behavior
State is stored in `pdev->archdata.od`, hwmod back-pointers, `_state`, `_driver_status`, and `OMAP_DEVICE_SUSPENDED` flags. It mutates hwmod clock/reset/power state but writes no persistent data.

## Dependencies and Integration Points
It depends on platform bus notifiers, PM domains/runtime PM, OF `ti,hwmods`, clock/clkdev APIs, OMAP hwmod, `omap_device.h`, and SoC/sysc integration. Drivers interact indirectly through runtime PM and direct hardreset helper calls.

## Risks
Notifier ordering and PM state transitions are fragile. Missing `ti,hwmods` attaches a fail PM domain that makes runtime PM return `-ENODEV`. Incorrect skip logic can conflict with `ti-sysc`. State validation returns `-EINVAL` on double enable/idle, which can expose driver runtime PM misuse. Clock alias creation has mixed legacy and OF paths.

## Test Signals
Boot DT OMAP systems and inspect platform devices for attached `archdata.od`. Exercise runtime PM get/put on hwmod-backed drivers, driver unbind/rebind, noirq suspend/resume, hardreset helpers, and late-idle warnings. Verify SDMA and ti-sysc-managed nodes are not incorrectly wrapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_device.c -->
