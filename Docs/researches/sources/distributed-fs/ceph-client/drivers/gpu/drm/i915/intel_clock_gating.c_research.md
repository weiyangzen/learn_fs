# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_clock_gating.c

Purpose: selects and applies platform-specific clock-gating and display/GT workaround register programming during i915 initialization.

Important APIs/functions: exports `intel_clock_gating_hooks_init()` and `intel_clock_gating_init()`. Internal init functions cover DG2, CFL/CML, SKL, KBL, BXT, GLK, BDW, CHV, HSW, IVB, VLV, gen6, ILK, G4X, i965, gen3, i85x, i830, and a no-op fallback. Helpers include `gen9_init_clock_gating`, `g4x_disable_trickle_feed`, `gen6_check_mch_setup`, and `gen8_set_l3sqc_credits`.

Control flow: hook initialization picks a static function table based on platform/version macros. Later `intel_clock_gating_init()` calls the selected function, which writes or read-modify-writes uncore/display/GT registers for known workarounds, often calling PCH clock-gating setup or shared gen helpers.

State and persistence: persistent driver state is the `i915->clock_gating_funcs` pointer. Hardware-visible state is MMIO register programming that lasts until reset/suspend or reinitialization.

Dependencies and integration: depends on uncore MMIO helpers, display register headers, PCH setup, GT MCR access, platform stepping macros, and MCHBAR definitions. It is part of hardware init rather than runtime policy.

Risks: workarounds are platform and stepping sensitive; writing the wrong register or missing a posting read can cause hangs, underruns, flicker, or power issues. Some comments identify historical hardware errata whose requirements are not obvious from code.

Test signals: platform boot on affected hardware, display underrun/flicker checks, runtime PM and suspend/resume, debug messages from no-op or MCH setup validation, and regression coverage for hardware workaround tables.
