# subset-b-004152 Research

This grouped report covers Qualcomm Iris/Venus video driver files under `sources/distributed-fs/ceph-client/drivers/media/platform/qcom/`. Each file section is delimited for reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_buffer.h

## Purpose
`iris_vpu_buffer.h` centralizes Iris VPU buffer sizing constants and inline size calculators used by the Iris decoder/encoder resource code. It does not allocate memory itself; it encodes hardware alignment, codec-specific auxiliary buffer dimensions, maximum picture/tile counts, and line-buffer/QP sizing formulas so platform-specific buffer-size implementations can compute firmware-visible buffer requirements consistently.

## Important APIs, Types, And Constants
- Declares `struct iris_inst` and exports `iris_vpu_buf_size()`, `iris_vpu33_buf_size()`, `iris_vpu4x_buf_size()`, and `iris_vpu_buf_count()`.
- Defines broad alignment and count constants such as `MIN_BUFFERS`, `DMA_ALIGNMENT`, `HFI_ALIGNMENT_4096`, `NUM_HW_PIC_BUF`, `MAX_TILE_COLUMNS`, `MAX_WIDTH`, `MAX_HEIGHT`, `NUM_MBS_4K`, and `NUM_MBS_720P`.
- Provides codec families of constants for H.264, H.265/HEVC, VP9, AV1, and encoder command/slice metadata buffers, including slice-list sizes, CABAC ratios, hardware picture table sizes, Dolby/HDR metadata sizes, ARP sizes, and tile/probability table sizes.
- Inline helpers compute line-buffer and metadata sizes for H.264 and AV1: `size_h264d_lb_fe_top_data()`, `size_h264d_lb_*()`, `size_h264d_qp()`, `size_av1d_lb_fe_*()`, `size_av1d_lb_se_*()`, `size_av1d_lb_pe_top_data()`, `size_av1d_lb_vsp_top()`, `size_av1d_lb_recon_dma_metadata_wr()`, and `size_av1d_qp()`.

## Control Flow And Behavior
The header is purely declarative plus inline arithmetic. Callers pass frame dimensions and buffer type/session context into platform buffer-size routines; these routines compose the constants and helpers to choose sizes for hardware picture buffers, line buffers, slice command buffers, metadata, QP maps, and codec-specific scratch areas. The inline functions mostly align width/height to codec LCU or macroblock boundaries, multiply by per-line or per-control-pack constants, and return byte sizes.

## State And Persistence
There is no state, locking, allocation, or persistence. The only implicit state is compile-time configuration: formulas depend on kernel macros such as `ALIGN`, `DIV_ROUND_UP`, `BIT`, `max`, and fixed hardware limits.

## Dependencies And Integration Points
- Depends on Iris buffer type definitions from headers included by users of this file, especially `enum iris_buffer_type`.
- Used by Iris VPU buffer-size implementations and session setup paths that must program HFI/Iris firmware with correct buffer sizes.
- Hardware-facing constants must match firmware and VPU architecture expectations; the exported function declarations split generic, VPU33, and VPU4x sizing.

## Risks And Edge Cases
- Several formulas use `u32`; extremely large dimensions or future hardware limits could overflow unless callers clamp to supported caps first.
- Duplicate macro definitions exist for some AV1 and PE line-buffer constants, increasing the risk of accidental divergent edits.
- Integer arithmetic such as `VPX_DECODER_FRAME_BIN_RES_BUDGET_RATIO (3 / 2)` truncates to `1`, so callers must not assume fractional precision from that macro.
- The constants are hardware contract values; incorrect alignment or per-codec table sizes can cause firmware rejection, decode corruption, or DMA overruns.

## Test Signals
- Build coverage catches missing type/macro dependencies and duplicate/invalid declarations.
- Runtime test signals are successful stream-on and buffer negotiation for H.264, HEVC, VP9, AV1, and encoder paths across VPU33/VPU4x platforms.
- Stress useful boundaries: 720p threshold, 4K max dimensions, AV1 large tile counts, 10-bit/UBWC formats, and dynamic resolution changes that recompute line buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_common.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_common.c

## Purpose
`iris_vpu_common.c` implements shared Iris VPU controller and hardware power, firmware boot, interrupt, watchdog, power-collapse, and clock-frequency helper logic. It is the common hardware-control layer behind per-platform `vpu_ops`, abstracting register programming differences while coordinating clocks, power domains, interconnect bandwidth, IRQ state, and firmware boot memory maps.

## Important APIs And Functions
- Boot and interrupt control: `iris_vpu_boot_firmware()`, `iris_vpu_raise_interrupt()`, `iris_vpu_clear_interrupt()`, `iris_vpu_watchdog()`.
- Power collapse and power sequencing: `iris_vpu_prepare_pc()`, `iris_vpu_power_on_controller()`, `iris_vpu_power_on_hw()`, `iris_vpu_power_on()`, `iris_vpu_power_off_controller()`, `iris_vpu_power_off_hw()`, `iris_vpu_power_off()`, `iris_vpu_set_hwmode()`, `iris_vpu_switch_to_hwmode()`.
- VPU35/VPU4x-specific controller operations: `iris_vpu35_vpu4x_power_on_controller()`, `iris_vpu35_vpu4x_power_off_controller()`, `iris_vpu35_vpu4x_program_bootup_registers()`.
- Performance model: `iris_vpu3x_vpu4x_calculate_frequency()` computes required VPU frequency from frame size, FPS, firmware cycles, VPP/VSP cycles, pipe count, and stage.
- Internal helpers include `iris_vpu_interrupt_init()` and `iris_vpu_setup_ucregion_memory_map()`.

## Control Flow
Firmware boot first programs the UC region and queue table addresses in `iris_vpu_setup_ucregion_memory_map()`, including 4 KiB queue-table alignment and 1 MiB UC region size alignment, then writes `CTRL_INIT` and polls `CTRL_STATUS` until firmware reports boot progress or an invalid UC-region setting. On success it enables host-to-Xtensa interrupts and clears X2RPMH state.

Power-on flows vote maximum interconnect bandwidth, enable controller power and clocks through platform ops, enable hardware power/clocks, set OPP frequency, apply preset registers, unmask VPU interrupts, clear `core->intr_status`, and enable IRQ delivery. Error unwinding disables controller resources and interconnect votes in reverse order.

Power-off clears OPP rate, powers off hardware then controller through platform ops, drops interconnect votes, and disables IRQ when the last interrupt status was not a watchdog. Controller power-off sequences write X2RPMH and NOC low-power requests, poll LPI status registers, halt/debug bridge clocks, toggle resets, and then disable clocks/power domains. VPU35/VPU4x uses a retry loop for AON video-control NOC LPI handshake and resets controller clocks after power down.

Power-collapse preparation checks `CTRL_STATUS` PC-ready and idle bits plus TZ CPU WFI status, asks firmware via `sys_pc_prep`, then polls for PC-ready and WFI status. If any condition fails it logs current state and returns `-EAGAIN`.

## State And Persistence
- Mutates hardware registers through `core->reg_base` and offsets from `iris_vpu_register_defines.h`.
- Uses `core->iface_q_table_daddr`, `core->sfr_daddr`, `core->intr_status`, `core->irq`, `core->power.clk_freq`, and platform data including power domains, clocks, resets, core architecture, and `vpu_ops`.
- No persistent storage is written; state lives in device registers, runtime PM resources, and `iris_core`.

## Dependencies And Integration Points
- Linux APIs: `readl/writel`, `readl_poll_timeout`, reset bulk reset, PM domains, OPP, IRQ, sleeps.
- Iris subsystems: `iris_core`, instance state, HFI queue table definitions, clock/power-domain helpers, interconnect helpers, and platform data callbacks.
- Integrates with HFI through `core->hfi_ops->sys_pc_prep()` and interrupt signaling registers.

## Risks And Edge Cases
- Firmware boot timeout is fixed at 1000 polls with 50-100 us sleeps; slow firmware or bad register programming yields `-ETIME`.
- Power-off controller functions often continue to disable resources after LPI poll failures and return `0`, so failures are logged or implied rather than propagated.
- `core->sfr_daddr + core_arch` is written to SFR address; incorrect architecture offset or DMA address truncation to `u32` can break firmware debug/boot on address layouts beyond the expected mask.
- IRQ disable is skipped on watchdog status, which is intentional for fault handling but must be considered in recovery races.
- Frequency calculation assumes default FPS and valid firmware caps; pipe count of zero would be invalid for `mult_frac` divisor.

## Test Signals
- Probe/boot should complete with firmware queues initialized and interrupts unmasked.
- Suspend/resume and idle power-collapse should show successful `sys_pc_prep` and no "skip power collapse" logs under idle workloads.
- Watchdog/fault tests should trigger `-ETIME` and preserve recovery path behavior.
- Clock/power-domain traces should show balanced enable/disable on probe failure, runtime suspend, stream start, and stream stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_common.h

## Purpose
`iris_vpu_common.h` is the public interface for Iris VPU hardware operations. It declares the per-generation `vpu_ops` tables and the shared controller, firmware, interrupt, power, and frequency functions implemented by `iris_vpu_common.c`.

## Important APIs And Types
- `struct vpu_ops` defines platform operation slots: `power_off_hw`, `power_on_hw`, `power_off_controller`, `power_on_controller`, optional `program_bootup_registers`, `calc_freq`, and `set_hwmode`.
- Extern operation tables: `iris_vpu2_ops`, `iris_vpu3_ops`, `iris_vpu33_ops`, `iris_vpu35_ops`, and `iris_vpu4x_ops`.
- Public functions cover firmware boot, interrupt raise/clear, watchdog check, PC preparation, power on/off split by controller/hardware, hardware mode switching, VPU35/VPU4x controller functions, boot-register programming, and frequency calculation.

## Control Flow And Integration
Platform data embeds a `const struct vpu_ops *`; higher-level Iris core and PM code call through this table to execute generation-specific sequences while sharing common helpers. Optional hooks such as `program_bootup_registers` allow VPU35/VPU4x to write extra registers during queue/SFR setup.

## State And Persistence
No state is stored in the header. It forward-declares `struct iris_core`; several declarations also use `struct iris_inst` through the `calc_freq` callback and exported frequency helper, relying on other includes to provide that type in compilation units.

## Dependencies
Requires kernel integer types and `struct iris_core`/`struct iris_inst` definitions in users. It is tightly coupled to Iris platform data and clock/power/reset helpers.

## Risks
- Any mismatch between an operation table and hardware generation can produce incorrect power sequencing.
- Function declarations expose split controller/hardware stages; callers must maintain the correct ordering and unwind paths.
- Header forward declarations are minimal; include-order mistakes can surface where `struct iris_inst` is not visible.

## Test Signals
Build coverage validates operation table signatures. Runtime validation comes from platform probe, firmware boot, suspend/resume, power collapse, watchdog recovery, and frequency scaling on all declared VPU generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_register_defines.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_register_defines.h

## Purpose
`iris_vpu_register_defines.h` defines register offsets and bit masks for Iris VPU controller, CPU, wrapper, trust-zone wrapper, AON, interrupt, reset, clock, and NOC low-power control blocks. It is the hardware address contract consumed by `iris_vpu_common.c` and related platform code.

## Important Constants
- Base offsets: `VCODEC_BASE_OFFS`, `CPU_BASE_OFFS`, `WRAPPER_BASE_OFFS`, `WRAPPER_TZ_BASE_OFFS`, `AON_BASE_OFFS`, and `AON_MVP_NOC_RESET`.
- Interrupt registers and masks: `CPU_CS_A2HSOFTINTCLR`, `CPU_CS_H2XSOFTINTEN`, `CPU_IC_SOFTINT`, `WRAPPER_INTR_STATUS`, `WRAPPER_INTR_MASK`, and bit masks for A2H/A2H watchdog.
- Power/clock/reset controls: `CPU_CS_X2RPMH`, `WRAPPER_DEBUG_BRIDGE_LPI_CONTROL/STATUS`, `WRAPPER_IRIS_CPU_NOC_LPI_CONTROL/STATUS`, `WRAPPER_TZ_CTL_AXI_CLOCK_CONFIG`, `WRAPPER_TZ_QNS4PDXFIFO_RESET`, `WRAPPER_CORE_CLOCK_CONFIG`.
- AON/NOC low-power and reset controls: `AON_WRAPPER_MVP_NOC_LPI_CONTROL`, `AON_WRAPPER_MVP_NOC_LPI_STATUS`, `AON_WRAPPER_MVP_NOC_RESET_REQ/ACK`, and status bits `NOC_LPI_STATUS_DONE`, `DENY`, `ACTIVE`.

## Control Flow And Integration
The file has no executable control flow. Callers add these offsets to an MMIO base and use `readl/writel` to drive firmware boot, interrupt clearing, low-power handshakes, debug-bridge control, CPU reset, and clock halt sequences.

## State And Persistence
No software state is stored. The constants identify device register state that persists only as hardware register values across power/reset transitions.

## Dependencies
Depends on `BIT()` and kernel integer macro context. It is included by Iris VPU common code and must match the register map of supported Iris VPU generations.

## Risks
- Incorrect offsets or bit masks can wedge the VPU, fail boot, mask interrupts, or break power-collapse handshakes.
- Register naming mixes wrapper and trust-zone wrapper spaces; callers must choose the proper base for their generation.
- Some status bits are reused in polling conditions; bad polarity assumptions can cause false success or timeout.

## Test Signals
Useful signals include successful firmware boot, host-to-firmware interrupt delivery, watchdog interrupt detection, suspend/resume low-power entry, and no timeout logs from NOC/debug-bridge polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_register_defines.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/Kconfig

## Purpose
`Kconfig` exposes `CONFIG_VIDEO_QCOM_VENUS`, the build-time option for the Qualcomm Venus V4L2 mem2mem encoder/decoder driver.

## Important Configuration
- `config VIDEO_QCOM_VENUS` is a tristate option labeled "Qualcomm Venus V4L2 encoder/decoder driver".
- Depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, `QCOM_SMEM`, and either Qualcomm ARM64 with `IOMMU_API` or `COMPILE_TEST`.
- Selects `OF_DYNAMIC` on Qualcomm architectures, `QCOM_MDT_LOADER`, `QCOM_SCM`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_MEM2MEM_DEV`.

## Control Flow And Integration
The option controls compilation of the Venus core, decoder, and encoder objects listed in the Makefile. The selected dependencies are directly reflected in source code: firmware MDT loading, SCM secure calls, SMEM firmware version publication, dynamic OF child nodes, DMA-contiguous vb2 queues, and V4L2 mem2mem devices.

## State And Persistence
No runtime state. The tristate determines whether the driver is built in, modular, or absent.

## Risks
- Missing `IOMMU_API`, `QCOM_SCM`, or `QCOM_MDT_LOADER` support prevents firmware boot on real hardware.
- `OF_DYNAMIC` is selected only under `ARCH_QCOM`; dynamic child node behavior may differ under compile-test configurations.

## Test Signals
Build matrix should include built-in, module, and `COMPILE_TEST` coverage. Runtime probe requires matching device tree nodes, firmware files, reserved memory, SCM availability when secure boot is used, and V4L2 mem2mem device registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/Makefile

## Purpose
The Venus `Makefile` defines how the driver is split into core, decoder, and encoder kernel objects under `CONFIG_VIDEO_QCOM_VENUS`.

## Important Build Targets
- `venus-core-objs` includes shared driver infrastructure: `core.o`, `helpers.o`, `firmware.o`, `hfi_venus.o`, `hfi_msgs.o`, `hfi_cmds.o`, `hfi.o`, parser/platform/PM/debugfs code, and v6 buffer helpers.
- `venus-dec-objs` builds decoder-specific `vdec.o` and `vdec_ctrls.o`.
- `venus-enc-objs` builds encoder-specific `venc.o` and `venc_ctrls.o`.
- The config adds `venus-core.o`, `venus-dec.o`, and `venus-enc.o` to `obj-*`.

## Control Flow And Integration
The build split matches runtime architecture: `venus-core` owns platform probing, firmware/HFI/PM infrastructure, while decoder and encoder child drivers bind to populated platform devices. `core.c` may create dynamic OF nodes for decoder/encoder, which correspond to the separate object modules.

## State And Persistence
No runtime state. Build inclusion is controlled by Kconfig.

## Risks
- Missing an object from `venus-core-objs` can create unresolved symbols for HFI, PM, parser, debugfs, or platform buffer logic.
- Decoder and encoder objects depend on exported symbols from `venus-core`; build and module load order must keep all three under the same config.

## Test Signals
Kernel build should produce `venus-core`, `venus-dec`, and `venus-enc` objects/modules when the config is enabled. Link-time checks validate symbol availability across the split.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/core.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/core.h

## Purpose
`core.h` defines the shared Venus driver data model: platform resource descriptors, V4L2/HFI format descriptors, per-core runtime state, per-instance session state, controls, buffers, and helper macros used throughout the core, encoder, decoder, PM, firmware, and HFI layers.

## Important Types And APIs
- Platform descriptors: `struct freq_tbl`, `struct reg_val`, `struct bw_tbl`, `enum vpu_version`, `struct firmware_version`, `struct venus_resources`.
- Format model: `enum venus_fmt`, `struct venus_format`.
- Core state: `struct venus_core`, with MMIO base pointers, IRQ, clocks, interconnects, PM domains, resets, V4L2 devices, firmware metadata, locks, instance list/count, HFI state, capabilities, debugfs root, firmware version, dynamic OF changeset, and hardware mode flag.
- Controls: `struct vdec_controls` and `struct venc_controls` capture V4L2 control values for decoder and encoder sessions.
- Buffer/session state: `struct venus_buffer`, `struct clock_data`, decoder/encoder state enums, `struct venus_ts_metadata`, `enum venus_inst_modes`, and `struct venus_inst`.
- Inline helpers/macros: HFI version checks (`IS_V1`, `IS_V3`, `IS_V4`, `IS_V6`), VPU version checks, `is_lite()`, `ctrl_to_inst()`, `to_inst()`, `to_hfi_priv()`, `venus_caps_by_codec()`, firmware revision comparisons.
- Declares exported `venus_close_common()`.

## Control Flow And Integration
This header drives how the rest of the driver shares state. `core.c` initializes `venus_core`; decoder/encoder open paths allocate and initialize `venus_inst`; `helpers.c` manipulates lists and buffer metadata; `hfi.c` uses `state`, completions, errors, and instance lists; firmware and PM code use core resource fields. The version macros select code paths across HFI packet formats, buffer requirements, power sequencing, and register layouts.

## State And Persistence
`venus_core` is the driver-wide state object for a physical VPU. `venus_inst` is per-file/session state and persists from open through close. It includes V4L2 queue state, stream-on flags, format sizes, DPB/output buffer types, firmware minimum counts, timestamps, payload cache, codec state, completion/error fields, HFI callbacks, core acquisition, bit depth, picture structure, drain flags, low-power flags, and DPB ID allocator.

## Dependencies
Includes V4L2, vb2, list/bitops, debugfs, HFI platform/helper headers, and HFI interface definitions. Struct members require PM helper definitions in implementation files.

## Risks And Edge Cases
- Many fields are shared across IRQ, workqueue, ioctl, and runtime PM contexts; lock discipline around `core->lock`, `inst->lock`, `ctx_q_lock`, and waitqueues is critical.
- Bitfields and flags such as `core_acquired`, `session_error`, `next_buf_last`, and `drain_active` encode lifecycle assumptions that must remain synchronized with HFI callbacks.
- Static limits such as clock/reset array sizes and `VIDEO_MAX_FRAME`-sized timestamp/payload arrays constrain supported hardware/session layouts.
- Firmware version comparisons only compare exact major/minor with rev thresholds, not arbitrary semantic ordering.

## Test Signals
Build coverage across all translation units validates shared type compatibility. Runtime signals include correct per-instance state transitions, no stale list entries on close, correct capability lookup by codec/domain, and stable behavior under concurrent decoder/encoder sessions and system-error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/dbgfs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/dbgfs.c

## Purpose
`dbgfs.c` creates and removes Venus debugfs controls. It exposes firmware debug verbosity and, when fault injection is enabled, a software path to force SSR/system-error recovery testing.

## Important APIs
- `venus_dbgfs_init(struct venus_core *core)` creates `/sys/kernel/debug/venus`, adds `fw_level`, and conditionally adds `fail_ssr`.
- `venus_dbgfs_deinit(struct venus_core *core)` removes the debugfs tree.
- Declares `venus_ssr_attr` through `DECLARE_FAULT_ATTR()` when `CONFIG_FAULT_INJECTION` is set.

## Control Flow
Probe calls `venus_dbgfs_init()` after successful driver initialization. Remove calls `venus_dbgfs_deinit()` after tearing down HFI/V4L2 state. The IRQ thread consults `venus_fault_inject_ssr()` from `dbgfs.h`; if the fault attribute fires, it triggers HFI SSR.

## State And Persistence
Stores the debugfs root dentry in `core->root`. The `fw_level` file directly exposes global `venus_fw_debug`. Fault-injection state is kernel debugfs state and not persistent across module unload/reboot.

## Dependencies
Uses Linux debugfs and fault-injection APIs plus `core.h`.

## Risks
- Debugfs creation failures are not checked; this is conventional but means controls may be absent without failing probe.
- Writable `fw_level` and fault injection are debugging interfaces and should not be relied on for production control.

## Test Signals
With debugfs mounted, `venus/fw_level` should exist after probe and disappear after remove. With `CONFIG_FAULT_INJECTION`, writing to `venus/fail_ssr` should allow IRQ-thread-triggered SSR recovery paths to be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/dbgfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/dbgfs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/dbgfs.h

## Purpose
`dbgfs.h` declares the Venus debugfs lifecycle and provides a compile-time conditional fault-injection helper.

## Important APIs
- `venus_dbgfs_init()` and `venus_dbgfs_deinit()` declarations.
- Under `CONFIG_FAULT_INJECTION`, exports `venus_ssr_attr` and defines `venus_fault_inject_ssr()` as `should_fail(&venus_ssr_attr, 1)`.
- Without fault injection, `venus_fault_inject_ssr()` is a constant false inline.

## Control Flow And Integration
`core.c` calls the debugfs init/deinit functions and uses `venus_fault_inject_ssr()` in the threaded ISR to optionally call `hfi_core_trigger_ssr()`. The header hides the configuration difference from core code.

## State And Persistence
No state is owned by the header. Fault-injection state lives in the `fault_attr` object declared in `dbgfs.c`.

## Dependencies
Includes `linux/fault-inject.h` and forward-declares `struct venus_core`.

## Risks
- Fault injection is only compiled when configured; tests that expect SSR injection must account for the inline false stub.
- Header consumers must not access `venus_ssr_attr` unless `CONFIG_FAULT_INJECTION` is enabled.

## Test Signals
Build coverage with and without `CONFIG_FAULT_INJECTION` should compile. Runtime with fault injection should expose and honor the `fail_ssr` debugfs attribute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/dbgfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/firmware.c

## Purpose
`firmware.c` manages Venus firmware loading, secure/non-secure boot, firmware memory mapping, CPU reset control, content-protection memory programming, firmware-version validation, and firmware device/IOMMU setup.

## Important APIs And Functions
- Hardware state/reset: `venus_reset_cpu()`, `venus_set_hw_state()`.
- Firmware image handling: `venus_load_fw()`, `venus_boot()`, `venus_shutdown()`.
- Non-TrustZone boot path: `venus_boot_no_tz()`, `venus_shutdown_no_tz()`.
- Platform quirks and validation: `venus_firmware_cfg()`, `venus_firmware_check()`.
- Firmware child device lifecycle: `venus_firmware_init()`, `venus_firmware_deinit()`.

## Control Flow
`venus_firmware_init()` looks for a `video-firmware` child node. If absent, the driver uses the TrustZone/PAS path. If present, it registers a child platform device, configures DMA, allocates an IOMMU paging domain, attaches the device, and stores the firmware device/domain in `core->fw`.

`venus_boot()` verifies MDT loader availability and SCM availability for secure boot, chooses firmware name from `firmware-name` DT property or SoC resource data, loads the MDT into reserved memory via `venus_load_fw()`, records physical address and size, then either authenticates/resets the PAS image through SCM or maps the firmware memory at IOVA 0 and releases the local CPU reset. Secure boot may also program video content-protection address ranges via `qcom_scm_mem_protect_video_var()`.

Shutdown mirrors the boot mode: secure boot uses `qcom_scm_pas_shutdown()`, while non-secure boot asserts CPU reset and unmaps the IOMMU firmware region. Firmware check compares `core->venus_ver` against an optional resource minimum.

## State And Persistence
- Mutates `core->use_tz` and `core->fw` fields: child device, IOMMU domain, mapped memory size, physical firmware memory, and memory size.
- Writes wrapper registers for firmware start/end, CPA/non-pixel ranges, CPU clock/reset, and XTSS/A9SS reset.
- No persistent files are written; firmware version is parsed elsewhere and checked here.

## Dependencies And Integration Points
- Linux firmware, reserved-memory, platform-device, DMA, IOMMU, and MMIO APIs.
- Qualcomm SCM and MDT loader APIs.
- Register definitions from `hfi_venus_io.h` and version macros from `core.h`.
- `core.c` calls init, boot, cfg, check, shutdown, and deinit in probe/remove/recovery.

## Risks And Edge Cases
- Reserved memory must exist and be large enough for the MDT image but not exceed `VENUS_FW_MEM_SIZE`; otherwise boot fails.
- Non-secure boot depends on a correctly described `video-firmware` child and IOMMU attachment; failures cause probe deferral or error.
- Secure boot requires SCM availability; otherwise boot defers.
- `venus_shutdown_no_tz()` reports unmap-size mismatch but still returns `0`, so partial cleanup relies on logs.
- Firmware version check requires `core->venus_ver` to have been populated by HFI image-version handling before validation.

## Test Signals
- Probe should request and load the expected firmware path for each compatible SoC.
- Secure devices should authenticate/reset via PAS and program CP ranges when configured.
- Non-secure devices should attach IOMMU, map IOVA 0, release reset, and unmap on shutdown.
- Firmware minimum-version tests should reject old qcm2290 images with the logged version comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/firmware.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/firmware.h

## Purpose
`firmware.h` declares the Venus firmware lifecycle and hardware-state APIs used by core and PM code.

## Important APIs
- `venus_firmware_init()` / `venus_firmware_deinit()` for firmware child device and IOMMU setup.
- `venus_firmware_check()` and `venus_firmware_cfg()` for version validation and platform-specific firmware register configuration.
- `venus_boot()` / `venus_shutdown()` for loading/authenticating/resetting and stopping firmware.
- `venus_set_hw_state()` plus inline `venus_set_hw_state_suspend()` and `venus_set_hw_state_resume()` wrappers.

## Control Flow And Integration
`core.c` uses the lifecycle sequence during probe, recovery, remove, and shutdown. PM helpers can use the suspend/resume wrappers to put firmware CPU state into reset or release it depending on secure/non-secure mode.

## State And Persistence
The header owns no state. Functions mutate `struct venus_core` firmware fields and hardware registers in `firmware.c`.

## Dependencies
Forward use of `struct venus_core` is expected through including translation units. The header also references `bool`.

## Risks
- The parameter name in `venus_set_hw_state(struct venus_core *core, bool suspend)` is semantically opposite the implementation name `resume`; callers should use the inline wrappers to avoid confusion.
- Calling boot/shutdown outside the expected runtime PM and HFI ordering can leave firmware state inconsistent.

## Test Signals
Build coverage validates exported signatures. Runtime tests should cover secure boot, non-secure child firmware node boot, suspend/resume wrappers, and probe unwind after boot failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/helpers.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/helpers.c

## Purpose
`helpers.c` is the main bridge between V4L2/vb2 mem2mem queues and HFI session operations. It handles codec/format validation, buffer-size calculations, DPB and internal DMA buffer allocation, buffer registration, timestamp metadata, profile/level translation, dynamic buffer mode, stream start/stop sequencing, and queued buffer processing.

## Important APIs And Functions
- Codec/format and sizing: `venus_helper_check_codec()`, `venus_helper_check_format()`, `venus_helper_get_out_fmts()`, `venus_helper_get_framesz_raw()`, `venus_helper_get_framesz()`, `venus_helper_get_opb_size()`.
- Buffer requirements and allocations: `venus_helper_get_bufreq()`, `venus_helper_alloc_dpb_bufs()`, `venus_helper_queue_dpb_bufs()`, `venus_helper_free_dpb_bufs()`, `venus_helper_intbufs_alloc()`, `venus_helper_intbufs_free()`, `venus_helper_intbufs_realloc()`, `venus_helper_unregister_bufs()`.
- V4L2/vb2 callbacks: `venus_helper_vb2_buf_init()`, `venus_helper_vb2_buf_prepare()`, `venus_helper_vb2_buf_queue()`, `venus_helper_vb2_start_streaming()`, `venus_helper_vb2_stop_streaming()`, `venus_helper_buffers_done()`, `venus_helper_vb2_queue_error()`.
- Mem2mem callbacks: `venus_helper_m2m_device_run()`, `venus_helper_m2m_job_abort()`.
- HFI property setup: resolution, work mode, format constraints, buffer counts, raw/color format, multistream, dynamic buffer mode, buffer size, stride, profile/level.
- Session utilities: `venus_helper_session_init()`, `venus_helper_init_instance()`, `venus_helper_process_initial_cap_bufs()`, `venus_helper_process_initial_out_bufs()`, timestamp metadata get/put, buffer reference acquire/release, DPB owner changes.

## Control Flow
Stream setup allocates internal buffers based on HFI/platform buffer requirements, registers capture buffers when static buffer mode is required, updates load scaling, loads HFI resources, and starts the session. Queued buffers are put into the V4L2 mem2mem queues, payloads are cached for clock/BW scaling, and if streaming is active they are converted into `hfi_frame_data` and sent through `hfi_session_process_buf()`. Output queues become HFI input buffers; capture queues become HFI output/secondary-output buffers depending on encoder/decoder and OPB type.

DPB handling allocates DMA buffers for decoder picture buffers, assigns tags from `ida`, queues only driver-owned buffers to firmware, and changes ownership back when HFI releases buffer references. Internal scratch/persist buffers are allocated from version-specific type lists and sent to firmware through `set_buffers`; realloc skips persistent buffers and refreshes scratch buffers after format changes.

Stop streaming runs HFI stop, unload resources, unregisters static buffers, frees internal buffers, deinitializes the session, aborts on errors, frees DPBs, rescales PM load, returns all queued V4L2 buffers with error, clears stream flags, releases the PM core, and clears session error state.

## State And Persistence
- Uses `inst->dpbbufs`, `internalbufs`, `registeredbufs`, and `delayed_process` lists.
- Stores timestamp metadata in `inst->tss[]`, payload sizes in `inst->payloads[]`, firmware minimum counts in `inst->fw_min_cnt`, output/input sizes, DPB/OPB formats and buffer types, bit depth, picture structure, and clock data.
- DMA allocations are transient and tied to stream/session lifetime.
- No persistent storage is written.

## Dependencies And Integration Points
- Linux DMA attrs, IDA, lists, mutexes, vb2-dma-contig, V4L2 mem2mem.
- HFI session APIs from `hfi.c`, HFI constants/types from `hfi_helper.h`, platform buffer/frequency data from `hfi_platform*`, PM scaling from `pm_helpers`.
- Called heavily by decoder/encoder queue ops and control setup code outside this subset.

## Risks And Edge Cases
- Buffer lifecycle is intricate: static versus dynamic buffer mode, DPB ownership, readonly buffer references, delayed work, and error returns must not double-free or leave firmware with stale DMA addresses.
- `delayed_process_buf_func()` returns immediately on `session_process_buf()` error without unlocking in that path, which is a subtle control-flow risk if reached.
- Timestamp metadata has a fixed `VIDEO_MAX_FRAME` slot array; slot exhaustion only logs and loses metadata association.
- Platform buffer requirements are preferred, with firmware query fallback; mismatches can cause under-allocation or stream-on failure.
- Frame-size formulas are alignment-heavy and must remain consistent with firmware for UBWC, P010, TP10, and compressed sizes.
- Stop streaming combines multiple return values with bitwise OR and may abort sessions after partial cleanup.

## Test Signals
- V4L2 compliance for queue setup, reqbufs, streamon/off, flush/drain, and buffer error paths.
- Decode tests with dynamic resolution change, secondary output, DPB-only paths, 10-bit UBWC, and delayed buffer-reference release.
- Encoder tests for profile/level mapping, bitrate/QP controls, stride/format programming, and EOS handling.
- DMA leak checks and lockdep under repeated stream start/stop, error injection, and system-error recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/helpers.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/helpers.h

## Purpose
`helpers.h` declares the V4L2/HFI helper surface used by Venus decoder and encoder implementation files. It is the public header for buffer lifecycle, stream control, format validation, HFI property setup, and session utility functions implemented in `helpers.c`.

## Important APIs
The header groups declarations for codec checking, V4L2 buffer init/prepare/queue/stop/start, queue error and buffer completion, mem2mem run/abort, HFI buffer requirements, frame-size calculations, resolution/color/format/work-mode/buffer-count/dynamic-buffer/multistream/stride properties, DPB/internal buffer allocation, buffer registration, initial queued buffer processing, timestamp recovery, profile/level get/set, and output-format negotiation.

## Control Flow And Integration
Decoder and encoder queue operations call these helpers to validate vb2 buffers, start HFI streaming, process initial buffers, and stop/cleanup. Control and format setup code calls the property helpers before starting sessions. HFI callbacks call buffer-reference and timestamp helpers to complete buffers correctly.

## State And Persistence
No state is stored in the header. All functions operate on `struct venus_inst`, `struct venus_core`, `vb2_buffer`, and `vb2_v4l2_buffer` state owned elsewhere.

## Dependencies
Includes `media/videobuf2-v4l2.h` and relies on HFI types such as `struct hfi_buffer_requirements` being visible through the including context.

## Risks
- A wide helper API means ordering is caller-sensitive; for example buffer counts, formats, work mode, and internal buffers must be configured before `hfi_session_start()`.
- Several functions return HFI errors directly and callers need consistent cleanup/error propagation.

## Test Signals
Compile tests validate cross-file declarations. Runtime tests should exercise each queue op path in decoder and encoder, plus property programming for supported codecs and formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi.c

## Purpose
`hfi.c` provides the high-level Host Firmware Interface state machine wrapper. It translates V4L2 pixel formats to HFI codecs, creates/destroys sessions, serializes core/session lifecycle transitions, waits for asynchronous firmware completions, gates operations during system errors, and delegates packet transport to lower-level `venus_hfi` operations.

## Important APIs And Functions
- Core lifecycle: `hfi_create()`, `hfi_destroy()`, `hfi_reinit()`, `hfi_core_init()`, `hfi_core_deinit()`, `hfi_core_suspend()`, `hfi_core_resume()`, `hfi_core_trigger_ssr()`.
- Session lifecycle: `hfi_session_create()`, `hfi_session_destroy()`, `hfi_session_init()`, `hfi_session_deinit()`, `hfi_session_load_res()`, `hfi_session_start()`, `hfi_session_stop()`, `hfi_session_unload_res()`, `hfi_session_abort()`, `hfi_session_continue()`.
- Session operations: `hfi_session_flush()`, `hfi_session_set_buffers()`, `hfi_session_unset_buffers()`, `hfi_session_get_property()`, `hfi_session_set_property()`, `hfi_session_process_buf()`.
- IRQ wrappers: `hfi_isr()` and `hfi_isr_thread()`.

## Control Flow
`hfi_create()` initializes core state, completion, instance count, core callbacks, and packet version, then creates the Venus HFI transport. Core init sends firmware init, waits up to one second for `core->done`, checks `core->error`, and marks `CORE_INIT`. Core deinit can block until all instances are destroyed if requested, then calls transport deinit and marks `CORE_UNINIT`.

Session create adds an instance to `core->instances` under `core->lock` if `sys_error` is clear and `max_sessions_supported` is not exceeded. Session init maps pixel format to HFI codec, sends session init, waits for completion, and moves to `INST_INIT`. Load/start/stop/unload/deinit enforce expected state transitions and wait for firmware responses. Get-property waits and copies `inst->hprop`; set-property and process buffers are asynchronous fire-and-forget at this wrapper level.

## State And Persistence
- Mutates `core->state`, `core->done`, `core->error`, `core->insts_count`, `core->instances`, `core->core_ops`, and `core->ops`.
- Mutates `inst->state`, `inst->done`, `inst->error`, `inst->ops`, and `inst->hfi_codec`.
- No persistent storage; state is runtime only and synchronized with firmware messages parsed by `hfi_msgs.c`.

## Dependencies And Integration Points
- Lower transport implementation in `hfi_venus.c` through `venus_hfi_create()`, `venus_hfi_destroy()`, and queue reinit.
- Packet versioning in `hfi_cmds.c`.
- Completion callbacks in `hfi_msgs.c` set errors and complete waits.
- Called by core probe/recovery/PM and by helper/decoder/encoder stream paths.

## Risks And Edge Cases
- One-second timeout is fixed; slow firmware or lost interrupts cause `-ETIMEDOUT`.
- State checks are strict, so caller cleanup paths must call lifecycle methods in the expected order.
- `hfi_session_destroy()` assumes the instance was successfully added; misuse can corrupt counts/lists.
- `hfi_session_continue()` is a no-op on HFI 1xx, version-specific behavior callers must tolerate.
- Operations during `sys_error` return `-EIO`, which must be handled by queue and cleanup paths without deadlock.

## Test Signals
- HFI init/deinit should complete during probe/remove and SSR recovery.
- Session lifecycle tests should cover init/load/start/stop/unload/deinit, abort on errors, max-session exhaustion, and property get/set timeouts.
- Lost IRQ or firmware fault injection should produce timeout or system-error paths without list/count leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi.h

## Purpose
`hfi.h` defines the high-level HFI interface shared between Venus core/helpers and the lower-level transport. It declares session/domain constants, buffer/frame descriptors, callback structures, core/session state values, operation tables, and wrapper APIs.

## Important Types And Constants
- Session domains: `VIDC_SESSION_TYPE_VPE`, `VIDC_SESSION_TYPE_ENC`, `VIDC_SESSION_TYPE_DEC`.
- Resource IDs: `VIDC_RESOURCE_NONE`, `OCMEM`, `VMEM`.
- Data descriptors: `struct hfi_buffer_desc`, `struct hfi_frame_data`, and `union hfi_get_property`.
- Events and event payload: `EVT_SYS_EVENT_CHANGE`, watchdog/system/session errors, `struct hfi_event_data`.
- Core/session states: `CORE_UNINIT`, `CORE_INIT`, `INST_UNINIT`, `INST_INIT`, `INST_LOAD_RESOURCES`, `INST_START`, `INST_STOP`, `INST_RELEASE_RESOURCES`.
- Callback/ops tables: `struct hfi_core_ops`, `struct hfi_inst_ops`, and `struct hfi_ops`.
- Public HFI wrapper declarations corresponding to `hfi.c`.

## Control Flow And Integration
`struct hfi_ops` is filled by the lower transport and used by `hfi.c` to send commands. `struct hfi_inst_ops` is supplied by decoder/encoder sessions so HFI message processing can report buffer completion, events, and flush completion. `hfi_frame_data` carries vb2 buffer metadata into ETB/FTB commands.

## State And Persistence
The header defines state numbers and data structures but stores no state. Runtime state lives in `venus_core` and `venus_inst`.

## Dependencies
Includes interrupt declarations and `hfi_helper.h` for HFI constants and property structs.

## Risks
- State constants begin at mixed numeric ranges (`CORE_*` and `INST_*`), so callers must compare only within the proper domain.
- `device_addr` fields are `u32`; hardware and DMA masks must keep addresses within representable ranges.
- Callback pointers are required for normal session operation; missing `buf_done` or `event_notify` would crash on firmware events.

## Test Signals
Compile coverage across core, helpers, transport, and decoder/encoder validates ABI shape. Runtime tests should confirm callback delivery for buffer done, event notify, and flush done across encoder and decoder sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_cmds.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_cmds.c

## Purpose
`hfi_cmds.c` constructs firmware command packets for system and session operations. It hides HFI version differences for property packetization, validates many enum-like values, computes packet sizes for flexible-array payloads, and converts driver descriptors into wire-format HFI packets.

## Important APIs And Functions
- Versioning: `pkt_set_version()`.
- System packets: `pkt_sys_init()`, `pkt_sys_pc_prep()`, `pkt_sys_idle_indicator()`, `pkt_sys_debug_config()`, `pkt_sys_coverage_config()`, `pkt_sys_ubwc_config()`, `pkt_sys_set_resource()`, `pkt_sys_unset_resource()`, `pkt_sys_ping()`, `pkt_sys_power_control()`, `pkt_sys_ssr_cmd()`, `pkt_sys_image_version()`.
- Session lifecycle and buffer packets: `pkt_session_init()`, `pkt_session_cmd()`, `pkt_session_set_buffers()`, `pkt_session_unset_buffers()`, `pkt_session_etb_decoder()`, `pkt_session_etb_encoder()`, `pkt_session_ftb()`, sequence-header, flush, get-property, and set-property helpers.
- Version-specific property builders: `pkt_session_get_property_1x/3xx()` and `pkt_session_set_property_1x/3xx/4xx/6xx()`.

## Control Flow
Callers allocate packet storage, then call a packet helper to fill headers, session IDs, sizes, and property payloads. Session IDs and resource handles are generated with `hash32_ptr(cookie)`. ETB/FTB helpers map `hfi_frame_data` fields into compressed or uncompressed packet layouts. Buffer set/unset uses different payload shapes for output/output2 buffers, which carry `hfi_buffer_info`, versus other buffer types, which carry address arrays.

Property setting dispatches by global `hfi_ver`: 1xx handles the base set, 3xx overrides changed packet layouts, 4xx adds work mode/video-core/HDR10/QP-range differences and rejects unsupported properties, and 6xx adds constraints, HEIC quality, and work-route properties before falling back. Many properties validate allowed modes and return `-EINVAL`, `-ERANGE`, or `-ENOTSUPP`.

## State And Persistence
The only module state is static `hfi_ver`, set at HFI creation from SoC resource data. Packet helpers otherwise write caller-provided packet memory and do not persist data.

## Dependencies And Integration Points
- Uses HFI packet structs from `hfi_cmds.h`, property structs/constants from `hfi_helper.h`, and version enum from `hfi.h`.
- Lower transport code sends these packets to firmware queues.
- Helpers, controls, PM, and core code indirectly rely on these builders through `hfi_ops`.

## Risks And Edge Cases
- Packet size calculations must exactly match flexible payload content; mistakes can cause firmware parser failures or memory corruption.
- `hash32_ptr()` session IDs can theoretically collide, though low probability; message demux relies on the same hash.
- Global `hfi_ver` assumes one active HFI packet version process-wide; multiple Venus devices with different HFI versions would be risky.
- Some unsupported properties intentionally return `-ENOTSUPP`; callers must tolerate version differences.
- QP range packing validates only 8-bit values before duplicating into I/P/B fields.

## Test Signals
- Firmware command/response success for core init, session init/start/stop, ETB/FTB, flush, buffer set/unset, and property programming.
- Version matrix tests on HFI 1xx/3xx/4xx/6xx hardware or emulation.
- Negative tests for invalid flush modes, SSR types, rate-control modes, intra-refresh modes, QP ranges, and unsupported properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_cmds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_cmds.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_cmds.h

## Purpose
`hfi_cmds.h` defines the HFI command IDs, command packet structures, SFR/SSR payload structs, and packet-construction API exported by `hfi_cmds.c`.

## Important Types And Constants
- Command IDs for system init/PC prep/resource/property/session commands, ping, SSR test, session load/start/stop/ETB/FTB/suspend/resume/flush/get-property/parse-sequence/release/continue/sync.
- Packet structs for system commands, session lifecycle, buffer set/release, compressed and uncompressed ETB, FTB, flush, get/set property, sequence header, SFR data, and SSR test.
- Function declarations for all system/session packet builders and `pkt_set_version()`.

## Control Flow And Integration
The lower HFI transport includes this header to allocate correctly typed packet buffers and call builders before writing to firmware queues. Struct layouts encode the firmware ABI, while helper functions in `hfi_cmds.c` fill version-specific details.

## State And Persistence
No state in the header. Packet structures are transient queue payloads.

## Dependencies
Includes `hfi.h`, which brings in HFI helper constants and version definitions.

## Risks
- ABI struct layout is firmware-facing; field order, width, and flexible array shape must not drift from firmware expectations.
- Some flexible arrays use `__counted_by`; callers must allocate enough storage for variable payloads.
- Several command IDs occupy different numeric ranges; wrong ID selection causes firmware to route packets incorrectly.

## Test Signals
Build coverage validates struct declarations and prototypes. Runtime success of packet builders is visible through matching HFI response messages and absence of firmware bad-packet errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_helper.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_helper.h

## Purpose
`hfi_helper.h` is the shared HFI ABI vocabulary for Venus: error codes, events, buffer flags, flush modes, extradata IDs, property IDs, codec/profile/level constants, buffer types/modes, HFI versions, and payload structures for properties, capabilities, formats, resources, and packet headers.

## Important Constants And Types
- HFI domains, architecture offsets, command/message offsets, and `enum hfi_version`.
- Error codes for system and session failures, plus special stream errors.
- Event IDs for system/session error, sequence changed, property changed, LTR failure, and buffer-reference release.
- Buffer flags such as EOS, sync frame, codec config, readonly, EOSEQ, corruption/drop/discontinuity flags.
- Flush constants, extradata constants, interlace constants, property IDs for common/VDEC/VENC/VPE system, param, and config spaces.
- Codec/profile/level maps for H.264, H.263, MPEG2/4, VC1, VP8/VP9, HEVC, DivX.
- Buffer types and version-sensitive macros for scratch/extradata buffer IDs.
- Property structs for debug, UBWC, enable, frame size/rate, profile/level, bitrate, QP, HDR10, work mode/route, raw plane constraints, codec capabilities, buffer requirements, resources, image version, sequence header, color conversion, and packet headers.
- Inline accessors for `struct hfi_buffer_requirements` compensate for HFI 4xx member swaps.

## Control Flow And Integration
This header contains no executable flow beyond inline accessors. It is included by HFI packet builders, message parsers, helpers, platform capability code, and core state definitions. It provides the constants that map V4L2 controls and formats to firmware properties and the structs that are copied into or out of HFI packets.

## State And Persistence
No runtime state. All definitions are compile-time ABI descriptions. The firmware image version string may be carried in `struct hfi_property_sys_image_version_info_type` and later stored in `venus_core`.

## Dependencies
Relies on kernel integer types, flexible arrays, and `__counted_by` annotations. It is tightly coupled to Qualcomm Venus firmware ABI versions.

## Risks And Edge Cases
- Numeric constants are firmware ABI; a single wrong value can make controls, buffers, or events silently misbehave.
- Some property IDs alias by HFI generation, such as QP range and MPEG4 time resolution, so version-specific packet code must choose carefully.
- HFI 4xx buffer-requirement member swaps require using inline accessors; direct field access can be wrong on that generation.
- Many DMA/device addresses in HFI structs are `u32`, requiring SoC DMA masks and firmware memory maps to stay below limits.

## Test Signals
- Compile tests across all HFI versions and platform files.
- Runtime parsing and property setup across generations, especially HFI 4xx buffer requirements and HFI 6xx constraints.
- V4L2 control tests for every mapped profile/level/rate-control/QP/HDR/format property.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_msgs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_msgs.c

## Purpose
`hfi_msgs.c` parses firmware-to-host HFI messages, demultiplexes them to core or session handlers, converts firmware events into driver callbacks, completes synchronous waits, extracts firmware capabilities/properties, and maps buffer-done messages back to V4L2-visible metadata.

## Important APIs And Functions
- Public message entry points: `hfi_process_msg_packet()` and `hfi_process_watchdog_timeout()`.
- Event handlers: `event_seq_changed()`, `event_release_buffer_ref()`, `event_sys_error()`, `event_session_error()`, `hfi_event_notify()`.
- System response handlers: init done, property info/image version, release resource, ping ack, idle, PC prepare done.
- Session response handlers: property info, init/load/start/stop/flush/release/end/abort/sequence-header done, ETB done, FTB done.
- `to_instance()` maps firmware session IDs back to `venus_inst` using `hash32_ptr()`.
- Static `handlers[]` maps HFI message packet IDs to minimum sizes, optional alternate size, callback, and system/session classification.

## Control Flow
`hfi_process_msg_packet()` looks up the packet type in `handlers[]`, validates packet size against the expected structure(s), resolves a session for non-system messages, and calls the handler. System packets operate with `inst == NULL`; session packets require a valid hashed session ID except system-error events.

Sequence-change events parse a variable list of changed properties from `ext_event_data`, handling frame size, profile/level, bit depth, picture structure, color space, entropy, buffer requirements, input crop, and DPB counts. It validates remaining bytes before each read and reports `EVT_SYS_EVENT_CHANGE`.

Sync response handlers set `core->error` or `inst->error` and complete the matching completion used by `hfi.c`. Buffer-done handlers call session `buf_done()` with HFI buffer type, output/input tag, bytes used, offsets, V4L2 keyframe/P/B/LAST flags, raw HFI flags, and timestamps. Firmware image-version messages parse known string formats into `core->venus_ver`, copy the version string into Qualcomm SMEM when available, and complete core init when a minimum firmware check is required.

## State And Persistence
- Mutates `core->error`, `core->venus_ver`, `inst->error`, and `inst->hprop`.
- Completes `core->done` and `inst->done`.
- Writes the firmware version string into SMEM image version table when available, which is externally visible platform state.
- Delivers events and buffer completions through callbacks, which update higher-level V4L2/session state outside this file.

## Dependencies And Integration Points
- HFI message struct definitions from `hfi_msgs.h`, constants from `hfi_helper.h`, parser from `hfi_parser.h`, core/instance state from `core.h`, SMEM API, and V4L2 buffer flags.
- Complements command builders in `hfi_cmds.c` and state waits in `hfi.c`.
- Integrates with system-error recovery in `core.c` through core event callbacks.

## Risks And Edge Cases
- Packet-size validation is minimal-size based; variable payload parsing must remain careful to avoid out-of-bounds reads.
- `to_instance()` uses hashed pointer IDs, so rare collisions or stale session IDs could misroute messages.
- System-error events may have no valid session; other invalid session IDs are logged and ignored, which can leave waiters timing out.
- Firmware version parsing accepts only known string formats; unrecognized formats log and can leave version fields zero.
- Sequence-change parsing sets `size_read = 0` for unknown property IDs, which risks not advancing over unknown payloads if firmware includes them.

## Test Signals
- HFI init should complete and populate codec capabilities through `hfi_parser()`.
- Firmware image-version responses should populate `core->venus_ver` and allow minimum-version checks.
- Buffer done should produce correct V4L2 LAST/keyframe/P/B flags and timestamps for encoder and decoder.
- Dynamic resolution change should deliver complete event data, including size, crop, bit depth, picture structure, and buffer count.
- Fault injection/watchdog should call core event recovery paths without stuck completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/hfi_msgs.c -->
