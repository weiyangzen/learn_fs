# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll.h

## Purpose

`intel_dpll.h` declares the display PLL interface implemented primarily by `intel_dpll.c` and used by modeset, encoder, CRTC, and shared-DPLL manager code. It exposes clock computation, hardware-state readback, divider math, VLV/CHV/BXT helpers, per-platform enable/disable calls, assertions, and simple clock comparison.

## Important APIs

Top-level atomic hooks are `intel_dpll_init_clock_hook()`, `intel_dpll_crtc_compute_clock()`, and `intel_dpll_crtc_get_dpll()`. These initialize platform hook selection, compute CRTC PLL state, and reserve shared DPLLs where needed.

Divider and hardware-state helpers are `i9xx_calc_dpll_params()`, `i9xx_dpll_compute_fp()`, `i9xx_dpll_get_hw_state()`, `vlv_compute_dpll()`, `chv_compute_dpll()`, `bxt_find_best_dpll()`, and `chv_calc_dpll_params()`.

PLL force and lifecycle APIs are `vlv_force_pll_on()`, `vlv_force_pll_off()`, `chv_enable_pll()`, `chv_disable_pll()`, `vlv_enable_pll()`, `vlv_disable_pll()`, `i9xx_enable_pll()`, and `i9xx_disable_pll()`.

Clock readback APIs are `i9xx_crtc_clock_get()`, `vlv_crtc_clock_get()`, and `chv_crtc_clock_get()`.

State checking helpers are `assert_pll_enabled()`, `assert_pll_disabled()`, and `intel_dpll_clock_matches()`.

## Control Flow And State

The header does not store state, but its function set defines the order used by the display pipeline: initialize hooks at display setup, compute CRTC PLL state during atomic check, optionally reserve a shared DPLL, enable the relevant PLL during modeset, read back hardware state during get-config/sanitize, and disable or force-off during teardown.

Functions operate on `struct intel_crtc_state`, `struct intel_atomic_state`, `struct intel_display`, `struct intel_crtc`, `struct dpll`, and `struct intel_dpll_hw_state`. Those structures carry all persistent state; this header only connects users to the implementation.

## Dependencies And Integration Points

The header includes `<linux/types.h>` and forward-declares the display types needed by prototypes. It is included by shared DPLL management, display modeset code, and DPIO PHY code. Because it exposes legacy and modern paths together, it is a compatibility boundary between old pipe PLL programming and newer port/shared PLL management.

## Risks And Edge Cases

The declarations mix platform-specific functions with top-level generic hooks. Callers must know which functions are legal for a platform; for example VLV/CHV force PLL helpers are not generic DPLL APIs. Adding or changing hardware-state structs requires matching all prototypes that consume `struct intel_dpll_hw_state`.

## Test Signals

Build coverage is the primary header-level signal. Runtime validation comes from the implementation callers: successful atomic check/commit flows, correct PLL lock/readback, and no unresolved or mismatched function declarations when platform code is compiled.
