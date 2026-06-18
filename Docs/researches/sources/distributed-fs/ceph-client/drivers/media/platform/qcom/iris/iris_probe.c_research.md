# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_probe.c

## Purpose
Implements the platform driver lifecycle for Qualcomm Iris. It binds DT compatibles to platform data, maps registers/IRQ, initializes HFI and hardware resources, registers V4L2 decoder/encoder video devices, sets DMA constraints, and wires runtime/system PM.

## Important APIs And Functions
- `iris_init_icc()` allocates `icc_bulk_data` from platform ICC table and obtains interconnect paths.
- `iris_init_power_domains()` attaches normal and OPP PM domains, configures OPP clocks, and loads the OPP table.
- `iris_init_clocks()` obtains all clocks from DT.
- `iris_init_reset_table()` and `iris_init_resets()` resolve bulk reset controls, including optional controller resets.
- `iris_register_video_device()` creates decoder or encoder `video_device` objects with selected ioctl ops.
- `iris_probe()` allocates `iris_core`, maps MMIO, obtains IRQ, initializes ops, resources, caps, V4L2 devices, DMA mask/segments, and runtime PM autosuspend.
- `iris_remove()` unregisters devices and deinitializes core state.
- `iris_sys_error_handler()` deinitializes and reinitializes the core after system error.
- `iris_pm_suspend()` and `iris_pm_resume()` call HFI PM hooks only when the core is initialized.

## Control Flow And Integration Points
`module_platform_driver()` registers `qcom_iris_driver`. DT matching selects one `iris_platform_data` entry. Probe initializes generic V4L2/vb2 ops through `iris_init_ops()`, then platform-specific HFI ops through callbacks in the matched platform data. Decoder and encoder devices share the same core but expose different names and ioctl tables. Runtime PM is enabled after successful device registration and DMA setup.

## State And Persistence Behavior
Creates the long-lived `iris_core` devm allocation with lock, instance list, response packet, completion, delayed system-error work, resource handles, and video-device pointers. Core state starts at `IRIS_CORE_DEINIT`; actual firmware/core initialization occurs later on open. Devm-managed resources are released by device core; V4L2 devices are explicitly unregistered on remove/error.

## Dependencies
Uses Linux platform, IRQ, clk, ICC, PM-domain, OPP, reset, PM runtime, DMA, and V4L2 subsystems. Integrates with `iris_core`, `iris_ctrls`, `iris_vidc`, HFI ISR/handlers, and all exported platform data.

## Risks
- Error unwinding must unregister video devices and V4L2 device in the right order; probe registers decoder before encoder.
- `of_device_get_match_data()` must return valid platform data; missing match data would crash later.
- Optional controller resets are only initialized when size is nonzero; platform size/table consistency is critical.
- The driver disables IRQ after request; firmware/core init must later enable it correctly.
- `iris_remove()` unregisters both `vdev_dec` and `vdev_enc`; partial probe failures must avoid later remove paths with unset pointers.

## Test Signals
- Probe/unbind tests for each compatible string.
- Failure injection around ICC/PM-domain/clock/reset/video registration validates unwind.
- Runtime PM suspend/resume while streaming and idle.
- System-error work path triggers deinit/init recovery without leaking devices.
