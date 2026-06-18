# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/malidp_crtc.c

## Purpose

`malidp_crtc.c` implements CRTC behavior for the ARM Mali-DP500/DP550/DP650 DRM driver. It validates pixel clocks, manages runtime PM and CRTC enable/disable, performs CRTC-level atomic validation for gamma, CTM, scaling, and rotation-memory budgets, owns custom CRTC state, and wires vblank interrupt enablement.

## Important APIs, Types, And Functions

The exported function is `malidp_crtc_init()`. Important helpers include `malidp_crtc_mode_valid()`, `malidp_crtc_atomic_enable()`, `malidp_crtc_atomic_disable()`, `malidp_crtc_atomic_check()`, `malidp_crtc_atomic_check_gamma()`, `malidp_crtc_atomic_check_ctm()`, `malidp_crtc_atomic_check_scaling()`, and CRTC state reset/duplicate/destroy functions. `struct malidp_crtc_state` carries generated gamma coefficients, color-adjust coefficients, scaling-engine config, and a scaled-plane bitmask.

## Control Flow

Initialization creates display-engine planes, finds the primary plane, initializes the CRTC, enables DRM color management, and programs scaling enhancer coefficients. Atomic mode validation checks exact pixel-clock support. Atomic enable gets runtime PM, converts the adjusted mode to `struct videomode`, enables and sets the pixel clock, calls variant `modeset()`, leaves config mode, and turns vblank on. Atomic disable disables planes, turns vblank off, enters config mode, disables pixel clock, and drops runtime PM. Atomic check first budgets rotation memory across rotated or compressed planes, suppresses modesets for writeback-only connector-mask changes, then validates gamma, CTM, and scaling in sequence.

## State And Persistence Behavior

CRTC state persists in DRM atomic state and is duplicated between commits. Gamma is converted from a 4096-entry monochrome LUT into 64 hardware coefficient-table entries. CTM is converted from S31.32 DRM values to Q3.12-like two's-complement hardware coefficients. Scaling state records source/destination sizes, phase values, selected coefficient sets, source plane ID, and enhancer enable. Hardware config-mode and vblank state are controlled through variant callbacks and IRQ helpers.

## Dependencies And Integration Points

The file depends on DRM atomic helpers, runtime PM, clocks, videomode conversion, Mali-DP private structures, hardware callbacks from `malidp_hw.h`, and writeback connector indexing from `malidp_drv.h`. It integrates with plane checks via `scaled_planes_mask` and `rotmem_size`, and with `malidp_drv.c` commit-tail code that later writes gamma/color/scaling state.

## Risks And Edge Cases

The rotation-memory algorithm depends on DRM plane iteration order placing `DE_VIDEO1` first when needed. Gamma rejects non-monochrome curves and requires exactly `MALIDP_GAMMA_LUT_SIZE`; CTM rejects values outside representable hardware range. Only one plane can use the scaling engine. Pixel clock validation requires exact `clk_round_rate()` equality. `pm_runtime_get_sync()` failure in enable returns without cleanup beyond debug logging.

## Test Signals

Test signals include mode-clock rejection, enable/disable suspend-resume paths, 4096-entry gamma LUT acceptance and invalid-size/color rejection, CTM overflow rejection, single-plane scaling and multi-plane scaling rejection, rotated/compressed plane memory budget failures, writeback-only connector changes avoiding modesets, and vblank enable/disable IRQ behavior.
