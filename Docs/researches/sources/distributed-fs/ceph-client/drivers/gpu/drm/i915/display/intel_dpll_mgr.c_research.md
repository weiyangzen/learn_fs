# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpll_mgr.c

## Purpose

`intel_dpll_mgr.c` implements the shared display PLL abstraction for i915 display platforms. It initializes platform PLL inventories, computes hardware states, reserves compatible PLLs in atomic state, tracks pipe users, enables and disables PLLs under lock, reads and sanitizes hardware state, dumps and compares PLL state, and verifies software tracking against hardware after commits.

The manager covers multiple hardware generations: IBX/CPT PCH PLLs, HSW/BDW WRPLL/SPLL/LCPLL, SKL/KBL DPLLs, BXT/GLK port PLLs, ICL/TGL/DG1/ADL combo and Type-C PLLs, MTL C10/C20/CX0 PLLs, and Xe3 LPD LT PHY PLLs. It hides those differences behind `struct intel_dpll_mgr` and `struct intel_dpll_funcs`.

## Important APIs, Types, And Functions

`struct intel_dpll_funcs` is the per-PLL operation table: `enable`, `disable`, `get_hw_state`, and `get_freq`. `struct intel_dpll_mgr` is the per-platform manager table: PLL inventory plus callbacks for compute, reserve, release, active-DPLL update, refclk update, dump, and compare.

Atomic state helpers include `intel_atomic_duplicate_dpll_state()`, `intel_atomic_get_dpll_state()`, `intel_reference_dpll()`, `intel_unreference_dpll()`, `intel_put_dpll()`, `icl_put_dplls()`, and `intel_dpll_swap_state()`. They stage `struct intel_dpll_state` changes in the atomic state and swap them into `pll->state` during commit.

Core public APIs include `intel_dpll_init()`, `intel_dpll_compute()`, `intel_dpll_reserve()`, `intel_dpll_release()`, `intel_dpll_update_active()`, `intel_dpll_enable()`, `intel_dpll_disable()`, `intel_dpll_get_freq()`, `intel_dpll_get_hw_state()`, `intel_dpll_update_ref_clks()`, `intel_dpll_readout_hw_state()`, `intel_dpll_sanitize_state()`, `intel_dpll_dump_hw_state()`, `intel_dpll_compare_hw_state()`, `intel_dpll_state_verify()`, and `intel_dpll_verify_disabled()`.

PLL selection is centered on `intel_find_dpll()`. It receives a desired hardware state and an allowed DPLL bitmask, prefers an already-referenced PLL with matching state for sharing, otherwise remembers the first unused PLL, and returns `NULL` when no compatible or free PLL exists.

Generation-specific blocks define inventories and operations:

- PCH: `ibx_pch_dpll_*()`, `pch_plls`, `pch_pll_mgr`.
- HSW: WRPLL/SPLL/LCPLL calculation and get/reserve paths, including `hsw_ddi_calculate_wrpll()`.
- SKL: `skl_ddi_calculate_wrpll()`, CFGCR programming, DP link-rate state, and SKL DPLL inventory.
- BXT: `bxt_ddi_pll_enable()`, `bxt_ddi_pll_get_hw_state()`, DP fixed divider table, HDMI divider calculation through `bxt_find_best_dpll()`, and port-to-PLL 1:1 reservation.
- ICL/TGL/ADL: combo PLL and MG/DKL Type-C PLL calculators, TBT PLL state, combo/TC reservation, active-DPLL switching, enable/disable/readback functions, and platform inventories.
- MTL/Xe3: wrappers around `intel_cx0pll_*()` and `intel_lt_phy_*()` helpers, with TBT PLLs marked always-on and alternate-port handling retained.

## Control Flow And State

Initialization starts in `intel_dpll_init()`, which initializes `display->dpll.lock`, chooses a manager based on platform, fills `display->dpll.dplls[]` from the selected `dpll_info` table, stores indexes, and records `display->dpll.mgr` plus `num_dpll`. DG2 explicitly has no shared DPLL manager because port PLLs are part of the PHY.

During atomic check, `intel_dpll_compute()` dispatches to the manager's compute callback. The callback fills `crtc_state->dpll_hw_state` or `crtc_state->icl_port_dplls[]` with the desired state and updates `port_clock` from the get-frequency function when needed. `intel_dpll_reserve()` then dispatches to the manager's get callback, which calls `intel_find_dpll()` with a generation-specific allowed mask. Successful reservation stages a pipe reference in atomic DPLL state and stores the selected `struct intel_dpll *` in `crtc_state->intel_dpll`.

ICL and newer Type-C flows may reserve two PLLs: a default TBT PLL and an MG/TC/CX0/LT PHY PLL. `icl_update_active_dpll()` selects which one is active based on current Type-C mode, and `icl_set_active_port_dpll()` copies the selected port-DPLL state into `crtc_state->intel_dpll` and `crtc_state->dpll_hw_state`.

During commit, `intel_dpll_enable()` marks the CRTC's joined pipe mask active under `display->dpll.lock`. If the PLL has no prior active users, it gets an optional power-domain wakeref and calls the PLL's enable callback. `intel_dpll_disable()` removes the active pipe mask and disables/releases the power domain only when no active users remain.

Readout and sanitize run outside atomic compute. `intel_dpll_readout_hw_state()` reads every PLL's hardware state, records `pll->on`, gets wakerefs for powered PLLs with power domains, reconstructs `pipe_mask` from active CRTC states, and initializes `active_mask`. `intel_dpll_sanitize_state()` disables PLLs that are on but unused, while preserving active or always-on behavior.

Verification uses `verify_single_dpll_state()` to compare software `on`, `active_mask`, `pipe_mask`, and stored hardware state against fresh readback. It has special handling for always-on PLLs and LT PHY comparisons. `intel_dpll_state_verify()` checks new and old PLLs around a CRTC transition, including alternate-port DPLL cases for TC ports.

Persistent state includes `display->dpll.dplls[]`, each `pll->state.hw_state`, `pll->state.pipe_mask`, `pll->active_mask`, `pll->on`, `pll->wakeref`, staged `state->dpll_state[]`, `state->dpll_set`, platform ref clocks in `display->dpll.ref_clks`, and ICL+ per-CRTC port-DPLL selections.

## Dependencies And Integration Points

The manager depends on display register access (`intel_de_*()`), display power domains, atomic CRTC state, encoder type helpers, HTI DPLL masks, PCH refclk setup, DPIO PHY mapping for BXT, DKL PHY access, Type-C mode helpers, CX0 PHY helpers, LT PHY helpers, and platform stepping/workaround helpers.

It integrates upward with `intel_dpll.c`, which calls `intel_dpll_compute()` and `intel_dpll_reserve()` from platform clock hooks. It integrates sideways with encoder/PHY code that calculates port clocks and Type-C mode, and downward with low-level register definitions for every platform generation.

## Risks And Edge Cases

Shared PLL correctness depends on exact hardware-state comparison. A missing field in a compare function can share incompatible PLL states; an extra unstable readback field can prevent sharing or trigger false mismatch warnings. The ICL compare function explicitly notes a FIXME to split combo versus MG state more thoroughly.

Atomic reference tracking is sensitive to ordering. `intel_atomic_get_dpll_state()` requires the connection mutex, staged state must be swapped exactly once, and release paths differ between single-PLL and ICL multi-port-DPLL reservations. Failing to unreference the TBT PLL on MG reservation failure would leak a staged reference, so the error path explicitly unwinds it.

Power and lock sequencing is hardware-sensitive. Many enable paths have short waits for power state and lock bits. Some PLLs require power-domain wakerefs, some are always-on, and some have no-op enable/disable because the clock is fixed or owned elsewhere.

Platform selection and masks are dense. HTI can reserve DPLLs, DG1 splits masks by port group, EHL/JSL/RKL expose DPLL4 quirks, ADL-P has a CMTG clock-gating workaround tied to DPLL0, and MTL/Xe3 map ports to PLL IDs via encoder lookup. Wrong masks can allocate a PLL that cannot physically drive the port.

## Test Signals

High-value test signals include atomic modeset coverage with multiple CRTCs sharing and not sharing PLLs, Type-C DP-alt and legacy-mode transitions, MST using primary-port DPLL decisions, suspend/resume readout and sanitize, hotplug across combo and TC ports, forced HTI-reserved DPLL masks, and fastset checks where old active DPLL selection matters. Kernel logs to watch include DPLL allocation failures, PLL lock/power timeout messages, software/hardware state mismatch dumps, active-mask and pipe-mask verification warnings, and unexpected missing-case warnings for port, refclk, divider, or platform selections.
