# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/core.c

## Purpose
`core.c` is the platform driver entry point and central lifecycle manager for Qualcomm Venus video hardware. It probes resources, configures runtime PM and HFI, boots firmware, registers V4L2 devices, populates decoder/encoder child devices, handles fatal system errors and coredumps, and defines SoC-specific resource tables.

## Important APIs And Functions
- Driver lifecycle: `venus_probe()`, `venus_remove()`, `venus_core_shutdown()`, `module_platform_driver(qcom_venus_driver)`.
- Runtime PM: `venus_runtime_suspend()`, `venus_runtime_resume()`, `venus_pm_ops`.
- Error recovery: `venus_event_notify()`, `venus_sys_error_handler()`, `venus_coredump()`.
- HFI/core support: `venus_core_ops`, `venus_enumerate_codecs()`, `to_v4l2_codec_type()`, `venus_assign_register_offsets()`, `venus_isr_thread()`.
- Dynamic OF support under `CONFIG_OF_DYNAMIC`: `venus_add_video_core()`, `venus_add_dynamic_nodes()`, `venus_remove_dynamic_nodes()`.
- Shared close helper: `venus_close_common()` is exported for encoder/decoder file release paths.
- SoC data: multiple `venus_resources` instances for msm8916, msm8996, msm8998, sdm660, sdm845 variants, sc7180, sm8250, sc7280, qcm2290, with frequency, bandwidth, clock, reset, power-domain, firmware, secure memory, HFI version, VPU version, and compatible data.

## Control Flow
Probe allocates `venus_core`, maps MMIO, gets interconnect paths and IRQ, reads match data, initializes PM helpers, DMA mask, list/locks/workqueue/waitqueue, creates HFI, requests threaded IRQ, assigns version-specific register bases, registers V4L2, enables runtime PM, boots firmware, configures firmware, resumes/initializes HFI, checks firmware version, optionally creates dynamic decoder/encoder OF nodes, populates child devices, enumerates codecs for old HFI 1xx firmware, drops runtime PM, and initializes debugfs. Error labels unwind HFI, firmware, runtime PM, V4L2, dynamic nodes, and PM resources.

Fatal HFI events set `core->sys_error` and `core->dump_core`, notify all live instances of `EVT_SESSION_ERROR`, disable IRQ, and schedule delayed recovery. Recovery deinitializes HFI, waits for decoder/encoder runtime PM to idle, shuts firmware down, optionally captures firmware memory via devcoredump, reinitializes HFI queues, reboots firmware, resumes and initializes HFI, reenables IRQ, and clears `sys_error` on success. Failure schedules another recovery attempt after logging the failed phase.

Runtime suspend asks HFI to suspend, powers the core off via PM ops, then drops interconnect bandwidth. Runtime resume restores interconnect votes, powers the core on, and resumes HFI.

## State And Persistence
- `venus_core` holds MMIO bases, clocks, power domains, interconnect paths, reset controls, V4L2 device, firmware state, instance list/count, HFI state, codec capabilities, debugfs root, firmware version, and dynamic OF changeset pointer.
- `core->sys_error` and `core->dump_core` are bit flags shared across IRQ/recovery/session paths.
- Coredump copies firmware reserved memory into a devcoredump; otherwise no persistent user data is stored.
- Static resource tables persist for the driver lifetime and define SoC behavior.

## Dependencies And Integration Points
- Linux platform, device tree, runtime PM, interconnect, power-domain, reset, IRQ, V4L2, vb2, devcoredump, and OF dynamic APIs.
- Internal modules: firmware boot/shutdown, PM helpers, HFI queue implementation, debugfs, decoder/encoder child drivers.
- Device tree compatible strings map directly to `venus_resources` and firmware names.

## Risks And Edge Cases
- Probe error unwind is complex; wrong ordering can leak firmware mappings, runtime PM refs, HFI state, or dynamic OF changesets.
- Recovery waits for child runtime PM idle with bounded attempts; active sessions can delay or race recovery.
- `venus_coredump()` remaps the entire firmware memory region and vmallocs the same size, so large or invalid reserved memory can fail silently.
- `pm_runtime_get_sync()` failures are handled, but some recovery paths continue through multiple phases and may reschedule indefinitely.
- Codec enumeration creates a dummy session for HFI 1xx only; unsupported codec mappings produce init failures and abort probe.

## Test Signals
- Probe logs and `/dev/video*` creation for decoder and encoder on each compatible SoC.
- Runtime suspend/resume cycles with no HFI timeout and balanced interconnect bandwidth votes.
- Fault injection through debugfs `fail_ssr` should trigger SSR recovery and restore operation.
- Firmware version check should reject qcm2290 firmware older than the minimum version.
- Remove/shutdown should deinit HFI and firmware without IRQ-after-free or PM reference leaks.
