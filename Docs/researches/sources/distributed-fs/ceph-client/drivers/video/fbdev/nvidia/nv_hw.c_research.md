# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_hw.c

## Purpose

`nv_hw.c` contains low-level NVIDIA hardware state calculation and register programming for `nvidiafb`. It handles VGA unlock/cursor visibility, clock discovery, FIFO arbitration heuristics, pixel-clock PLL calculation, extended CRTC/RAMDAC state generation, full graphics/FIFO object initialization, state save/restore, and CRTC start-address updates. The source was read as a complete 1688-line file.

## Important APIs, Types, and Functions

Exported functions are `NVLockUnlock()`, `NVShowHideCursor()`, `NVCalcStateExt()`, `NVLoadStateExt()`, `NVUnloadStateExt()`, and `NVSetStartAddress()`. Internal arbitration types include `nv4_fifo_info`, `nv4_sim_state`, `nv10_fifo_info`, and `nv10_sim_state`. Clock and FIFO helpers include `nvGetClocks()`, `nv4CalcArbitration()`, `nv4UpdateArbitrationSettings()`, `nv10CalcArbitration()`, `nv10UpdateArbitrationSettings()`, `nv30UpdateArbitrationSettings()`, `nForceUpdateArbitrationSettings()`, `CalcVClock()`, and `CalcVClock2Stage()`.

## Control Flow

Mode setup starts in `nvidia_calc_regs()` in `nvidia.c`, which calls `NVCalcStateExt()` to compute extended state from bpp, virtual width, visible dimensions, dot clock, and vmode flags. That routine chooses PLL calculation, architecture-specific FIFO arbitration, cursor register values, config/general bits, repaint and pixel-depth fields. `nvidia_write_regs()` later calls `NVLoadStateExt()`, which resets PMC/PTIMER/PFB/PGRAPH/PFIFO/PRAMIN objects, applies architecture- and chipset-specific graphics engine setup, then writes extended CRTC/RAMDAC fields from `RIVA_HW_STATE`. `NVUnloadStateExt()` reads the current extended state for saving. `NVSetStartAddress()` writes the display start register for panning.

## State and Persistence Behavior

State is represented by `RIVA_HW_STATE` instances in `struct nvidia_par`: `SavedReg`, `ModeReg`, `initial_state`, and `CurrentState`. Hardware-visible persistence includes programmed PLLs, CRTC registers, FIFO/object RAM entries, PGRAPH state, PRAMDAC flat-panel settings, cursor configuration, and framebuffer start address. The file also updates `CurrentState` so cursor show/hide can mutate the live state image.

## Dependencies and Integration Points

The file depends on register-bank pointers initialized by `NVCommonSetup()` in `nv_setup.c`, bitfield macros and architecture constants from `nv_type.h`, raw MMIO helpers from `nv_local.h`, and PCI config access for nForce arbitration. It is central to `nvidia.c` mode set, cursor, panning, suspend/resume, and acceleration setup; `nv_accel.c` assumes the graphics/FIFO objects initialized here are present.

## Risks and Edge Cases

Most register values are chipset-specific magic constants. Unsupported or misidentified architectures can program the wrong PRAMIN/PGRAPH/PFIFO layout. PLL calculation uses integer heuristics and must respect crystal frequency and two-stage PLL variants. Several PCI helper calls assume host bridge functions are present. Arbitration failures or overly optimistic FIFO watermarks can cause display snow or underruns. The broad register reset in `NVLoadStateExt()` can disrupt firmware/console state if save/restore ordering is wrong.

## Test Signals

Strong signals include successful mode-set on NV04/NV10/NV20/NV30/NV40 families, cursor visibility toggles, panning start address changes, suspend/resume save-load round trips, acceleration immediately after mode set, flat-panel and CRT paths, endian build coverage, and stress tests at high dot clocks where FIFO arbitration margins matter.
