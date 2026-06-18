# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hvs.c

## Purpose

`vc4_hvs.c` manages the Hardware Video Scaler shared by VC4 display pipelines. The HVS composites/scales/converts framebuffer pixels into output FIFOs consumed by pixel valves or the transposer. This file owns HVS resource allocation, display-list and line-buffer memory managers, channel enable/disable, atomic display-list upload, gamma/LUT handling for older generations, underrun reporting, debugfs, generation-specific hardware initialization, COB allocation, component binding, and platform driver registration.

## Important APIs, Types, and Functions

- Debug and state helpers: `vc4_hvs_dump_state()`, `vc4_hvs_debugfs_underrun()`, `vc4_hvs_debugfs_dlist()`, `vc6_hvs_debugfs_dlist()`, `vc6_hvs_debugfs_upm_allocs()`, and `vc4_hvs_debugfs_init()`.
- Kernel/filter setup: `vc4_hvs_upload_linear_kernel()` installs the Mitchell/Netravali filter into display-list memory.
- Gamma helpers: `vc4_hvs_lut_load()` and `vc4_hvs_update_gamma_lut()` update VC4 gamma SRAM from DRM LUTs.
- FIFO/output helpers: `vc4_hvs_get_fifo_frame_count()` and `vc4_hvs_get_fifo_from_output()` report frame counters and map HVS outputs to FIFOs by generation.
- Channel lifecycle: `vc4_hvs_init_channel()`, `vc6_hvs_init_channel()`, `__vc4_hvs_stop_channel()`, `__vc6_hvs_stop_channel()`, and exported `vc4_hvs_stop_channel()`.
- Atomic hooks used by CRTC/TXP code: `vc4_hvs_atomic_check()`, `vc4_hvs_atomic_begin()`, `vc4_hvs_atomic_enable()`, `vc4_hvs_atomic_disable()`, and `vc4_hvs_atomic_flush()`.
- Underrun handling: `vc4_hvs_mask_underrun()`, `vc4_hvs_unmask_underrun()`, `vc4_hvs_report_underrun()`, and `vc4_hvs_irq_handler()`.
- Allocation/init: `__vc4_hvs_alloc()`, `vc4_hvs_hw_init()`, `vc6_hvs_hw_init()`, `vc4_hvs_cob_init()`, `vc4_hvs_bind()`, `vc4_hvs_unbind()`, and `vc4_hvs_driver`.

## Control Flow

Component bind maps registers, allocates `struct vc4_hvs`, initializes `drm_mm` allocators for display-list memory and LBM, initializes UPM tracking for VC6, selects debugfs regsets based on generation and hardware version, gets firmware/core/disp clocks on VC5+, determines HDMI 2.0/4096x2160 core-clock capability, enables clocks, locates the display-list memory base, initializes the HVS hardware, uploads the scaler kernel, programs COB partitions, and registers the underrun IRQ on pre-VC6 hardware.

Atomic check computes each CRTC's display-list word requirement from active planes, allocates a dlist block in `hvs->dlist_mm`, and stores it in `vc4_crtc_state->mm`. Atomic enable installs the dlist pointer, updates current dlist/event state, and starts the generation-specific HVS channel. Atomic flush writes plane display-list entries in normalized z-order, appends `SCALER_CTL0_END`, updates background-fill policy, updates the active dlist pointer for already-running CRTCs, and reloads gamma when color management changes. Atomic disable stops the assigned channel.

Underrun IRQs read status and control, honor software masking because hardware masks are not always honored, mask the offending channel, increment the underrun counter, log an error, and clear per-channel interrupt status. Debugfs paths expose register state, dlist contents, underrun count, load-tracker toggle, and VC6 UPM allocations.

## State and Persistence

`struct vc4_hvs` owns MMIO base, regset, platform device, core/disp clocks, `drm_mm` allocators for dlist/LBM/UPM, UPM handle/refcount state, display-list memory pointer, maximum core rate, HDMI capability flags, and uploaded filter allocation. `struct vc4_crtc_state` carries per-commit dlist allocation and assigned channel. State is live kernel/hardware state; display-list memory persists in HVS SRAM/MMIO until reallocated or reset, and bootloader display-list entries are intentionally preserved by starting allocation after `HVS_BOOTLOADER_DLIST_END`.

## Dependencies and Integration Points

This file depends on DRM atomic/vblank/debug helpers, Linux component/platform/clock APIs, Raspberry Pi firmware clock queries, `drm_mm`, local plane/CRTC helpers, HVS register macros in `vc4_regs.h`, and VC4 device structures in `vc4_drv.h`. It integrates with `vc4_kms.c` through HVS global state and channel assignment, with `vc4_crtc.c`/`vc4_txp.c` through atomic hooks, and with HDMI mode validation indirectly through HVS core clock capability flags.

## Risks and Edge Cases

- Display-list allocation must exactly match the words written during flush; mismatches trip `WARN_ON_ONCE` and can corrupt following dlist entries.
- Existing bootloader dlist memory is intentionally not overwritten to avoid boot display glitches; changing allocation start risks transition artifacts.
- VC6 uses mock sizes under KUnit because register access is unavailable; production register-size reads must remain outside tests.
- FIFO/output routing is generation-specific and returns `-EPIPE` for disabled/unroutable outputs; callers must handle it.
- Underrun interrupts may fire despite hardware masking, so software control checks are required.
- COB/LBM/UPM sizes are fixed or inferred and can limit high-resolution/multi-plane composition.
- VC6 D0 hardware is detected in bind and mutates `vc4->gen` from GEN_6_C to GEN_6_D, which affects later register paths.

## Test Signals

Signals include KUnit mock allocation paths, PV muxing tests in the VC4 test directory, atomic modesets with multiple planes/z-order/gamma, debugfs dlist/reg dumps, underrun counter behavior, HDMI 2.0 mode availability based on firmware core clock, repeated enable/disable preserving channel state, and real hardware coverage across GEN_4, GEN_5, GEN_6_C, and GEN_6_D.
