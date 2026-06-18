<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.h

## Purpose
This header defines the shared display PLL management contract for the i915 display driver. It names all platform DPLL identifiers, captures generation-specific PLL register state layouts, describes tracked shared-PLL state, and declares the atomic compute/reserve/enable/disable/readout/verification APIs used by encoder and CRTC mode-setting code.

## Important APIs, Types, and Functions
Important identifiers include `enum intel_dpll_id`, `I915_NUM_PLLS`, `enum icl_port_dpll_id`, `struct intel_dpll_hw_state`, `struct intel_dpll_state`, `struct dpll_info`, and `struct intel_dpll`. Hardware-state unions cover i9xx, HSW/BDW, SKL, BXT, ICL/TGL, MPLLB, C10/C20/CX0, and LT PHY PLL formats.

The public API is centered on `intel_dpll_compute()`, `intel_dpll_reserve()`, `intel_dpll_release()`, `intel_dpll_enable()`, `intel_dpll_disable()`, `intel_dpll_swap_state()`, `intel_dpll_init()`, `intel_dpll_readout_hw_state()`, `intel_dpll_sanitize_state()`, `intel_dpll_update_ref_clks()`, `intel_dpll_state_verify()`, and `intel_dpll_verify_disabled()`. Helpers such as `intel_get_dpll_by_id()`, `intel_dpll_get_freq()`, `intel_dpll_get_hw_state()`, `intel_dpll_compare_hw_state()`, `icl_tc_port_to_pll_id()`, `mtl_port_to_pll_id()`, and `intel_dpll_is_combophy()` expose lookup, frequency, and platform mapping services.

## Control Flow
The file itself has no executable flow, but it defines the atomic mode-set lifecycle. Encoders compute the requested PLL hardware state into `intel_crtc_state`, reserve a compatible shared PLL in the atomic state, swap committed state into `display->dpll`, enable PLLs before active scanout, disable/release them after use, and verify readout against expected state. `pipe_mask`, `active_mask`, `on`, and `wakeref` let the implementation distinguish logical users, active pipes, hardware enable state, and runtime power-management requirements.

## State and Persistence Behavior
`struct intel_dpll` is persistent per-display-driver state initialized at probe. `struct intel_dpll_state` exists both in live shared PLLs and in atomic transactions, carrying user pipe masks and exact hardware programming. The hardware-state union must remain stable with platform-specific implementations because equality and sharing decisions depend on byte-level fields such as PLL divider, spread-spectrum, C10/C20 lane, and Thunderbolt mode state.

## Dependencies and Integration Points
This header integrates with atomic CRTC/encoder state, display power domains, platform PLL backends in the DPLL manager implementation, TC/Thunderbolt and combo PHY port code, readout/sanitization paths, and state verification. Consumers depend on `intel_display_power_domain`, `enum port`, `enum tc_port`, `struct ref_tracker`, and MMIO programming hidden behind platform-specific `intel_dpll_funcs`.

## Risks
PLL IDs intentionally alias across platforms, so using an ID without the platform-specific DPLL table can select the wrong PLL. Sharing decisions are only as correct as `intel_dpll_compare_hw_state()` and the populated hardware-state fields. Power-domain and wakeref mistakes can leave PLLs inaccessible or prevent runtime power savings. C10/C20/LT PHY state carries lane-count, SSC, and TBT mode details, so partial initialization can produce link-training failures that look like encoder problems.

## Test Signals
Useful signals include successful i915 builds across display generations, atomic modeset tests covering shared PLL reuse and release, boot/readout without DPLL state mismatch warnings, hotplug and suspend/resume stability, DP/HDMI/eDP link training on combo and TC ports, runtime PM transitions with active/inactive PLLs, and debug dumps showing expected frequency and hardware-state equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.h -->
