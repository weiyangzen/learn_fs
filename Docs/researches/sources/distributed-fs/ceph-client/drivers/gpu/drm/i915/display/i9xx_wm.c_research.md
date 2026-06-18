# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_wm.c

## Purpose

`i9xx_wm.c` implements FIFO watermark and memory self-refresh control for pre-SKL Intel display hardware: i845/i830/i9xx/i965/Pineview, G4x, Valleyview/Cherryview, and Ironlake through Broadwell PCH-split platforms. It computes safe plane, cursor, sprite, FBC, self-refresh, HPLL, PM5, and DDR DVFS watermark settings from display mode, pixel format, plane visibility, FIFO partitioning, memory latency, and platform quirks, then programs the relevant MMIO/Punit registers during atomic commit phases and hardware state sanitization.

## Important APIs, Types, And Functions

The exported entry points are `intel_set_memory_cxsr()`, `ilk_disable_cxsr()`, `ilk_wm_sanitize()`, and `i9xx_wm_init()`. `i9xx_wm_init()` selects a `struct intel_wm_funcs` implementation for the platform. The main helper data types are `struct intel_watermark_params`, `struct intel_wm_config`, `struct cxsr_latency`, `struct g4x_wm_state`, `struct vlv_wm_state`, `struct intel_pipe_wm`, `struct ilk_wm_values`, `struct g4x_wm_values`, and `struct vlv_wm_values` as carried inside `intel_display` and `intel_crtc_state`.

The legacy path uses `i9xx_compute_watermarks()` to mark pre/post watermark updates and `i845_update_wm()`, `i9xx_update_wm()`, `i965_update_wm()`, or `pnv_update_wm()` to program registers. The G4x path centers on `g4x_raw_plane_wm_compute()`, `_g4x_compute_pipe_wm()`, `g4x_compute_intermediate_wm()`, `g4x_program_watermarks()`, `g4x_wm_get_hw_state()`, and `g4x_wm_sanitize()`. The VLV/CHV path uses `vlv_compute_fifo()`, `vlv_raw_plane_wm_compute()`, `_vlv_compute_pipe_wm()`, `vlv_atomic_update_fifo()`, `vlv_program_watermarks()`, `vlv_wm_get_hw_state()`, and `vlv_wm_sanitize()`. The ILK/SNB/IVB/HSW/BDW path uses `ilk_setup_wm_latency()`, `ilk_compute_pipe_wm()`, `ilk_compute_intermediate_wm()`, `ilk_wm_merge()`, `ilk_compute_wm_results()`, `ilk_write_wm_values()`, and `ilk_wm_get_hw_state()`.

## Control Flow

Initialization chooses the platform function table and reads or seeds memory latency values. PCH-split platforms read MCH/SSKPD/MLTR latency registers and apply SNB underrun and LP3 interrupt quirks. G4x and VLV seed fixed latency levels. Pineview validates its FSB/memory latency table before enabling the Pineview update path.

Atomic check computes per-CRTC watermark state. For G4x, VLV, and ILK-style atomic paths, plane states are converted into raw watermark levels, invalid levels are marked with `USHRT_MAX`, and an optimal pipe state is derived. An intermediate state is then created by combining old and new values so the hardware can be programmed before vblank without risking underrun; if the intermediate differs from the optimal state, `wm.need_postvbl_update` triggers a second programming pass. For non-atomic legacy GMCH paths, plane changes only set `update_wm_pre` and `update_wm_post`, and the old global update functions recompute directly from current CRTC and primary-plane state.

Programming merges per-pipe active watermark state into global register values. G4x enables CxSR/HPLL only for one active pipe with compatible state and temporarily disables CxSR before unsafe transitions. VLV/CHV additionally handles PM5 and DDR DVFS transitions through Punit sideband registers and updates DSPARB FIFO partitions under `uncore->lock`. ILK-style code merges LP1+ watermarks across active pipes, evaluates 1/2 versus 5/6 DDB partitioning when possible, disables affected LP watermarks before touching LP0, FBC, partitioning, or LP registers, and avoids unnecessary writes because the hardware reevaluates watermarks on each write.

## State And Persistence Behavior

Persistent software state lives in `display->wm`, per-CRTC `crtc->wm.active`, and per-commit `intel_crtc_state->wm`. Hardware state persists in DSPARB/DSPFW/FW_BLC, WM0/WM_LP/WM_MISC/DISP_ARB registers, VLV DDL registers, and Cherryview Punit PM/DVFS registers. CxSR is both hardware policy and tracked state for VLV and G4x. FIFO partition state is explicit in VLV `fifo_state` and can be reset by display power wells, so modesets force recomputation. Hardware readout reconstructs only what is trustworthy; sanitize paths recompute from current DRM state and rewrite hardware to match driver expectations.

## Dependencies And Integration Points

This file integrates DRM atomic state, i915 display register access (`intel_de_*`), platform descriptors, CRTC/plane state, framebuffer format/modifier state, FBC watermark support, Punit sideband access on VLV/CHV, memory/DRAM information for Pineview, tracepoints, and the common watermark hooks in `intel_wm.h`. It is selected by display init and then called by the generic Intel atomic modeset pipeline for check, initial programming, post-vblank optimization, atomic FIFO updates, hardware readout, and sanitize.

## Risks And Edge Cases

The primary risk is underrun or lost vblank interrupt from too-aggressive watermarks, incorrect latency readout, or unsafe transition ordering. Legacy code assumes reconstructed primary framebuffer and adjusted mode state are valid before using `intel_crtc_active()`. VLV FIFO repartitioning has pipe-specific high-bit registers and a sprite0 workaround when sprite1 is active alone. CHV DDR DVFS may not acknowledge requests if BIOS disabled DVFS, and readout adapts by reducing available levels. ILK/SNB/IVB restrictions around sprites, scaling, multiple pipes, and FBC watermarks can silently reduce usable LP levels. Sanitization intentionally leaves BIOS watermarks untouched if the recomputed state is invalid.

## Test Signals

Useful validation includes boot fastboot/readout on every supported platform family, modesets with one and multiple active pipes, plane enable/disable/resize/rotation/tiling changes, cursor and sprite-only transitions, FBC enabled and disabled, VLV/CHV sprite FIFO repartition and power-well reset recovery, CxSR disable around plane updates, SNB high-resolution modes, LP3 interrupt quirk systems, suspend/resume, and underrun/vblank interrupt monitoring under IGT KMS plane, cursor, flip, FBC, PSR-disabled, and modeset stress tests.
