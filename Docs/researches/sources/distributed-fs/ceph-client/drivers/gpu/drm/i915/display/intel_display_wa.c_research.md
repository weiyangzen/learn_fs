# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_wa.c

## Purpose
This file applies and queries display hardware workarounds. It programs a small set of platform-specific workaround registers during display init and provides a central predicate for workaround IDs used throughout display code.

## Important APIs, Types, and Functions
Static apply helpers include `gen11_display_wa_apply()`, `xe_d_display_wa_apply()`, `adlp_display_wa_apply()`, and `xe3plpd_display_wa_apply()`. The public `intel_display_wa_apply()` dispatches by display version/platform. `intel_display_needs_wa_16025573575()` gates a GPIO bitbashing workaround for Xe3-derived versions. `__intel_display_wa()` maps each `enum intel_display_wa` value to platform, display version, stepping, or PCH predicates and emits a warning for missing cases.

## Control Flow
At init, `intel_display_wa_apply()` applies register writes with `intel_de_rmw()` for display versions 35, 12, 11, and Alder Lake-P. Runtime predicate flow is a switch over sorted workaround lineage IDs. Cases test `DISPLAY_VER`, `DISPLAY_VERx100`, `IS_DISPLAY_VER`, `IS_DISPLAY_STEP`, platform flags, PCH type, and one external helper for WA 16023588340.

## State and Persistence Behavior
Apply helpers mutate display MMIO registers such as `GEN8_CHICKEN_DCPR_1`, `CLKREQ_POLICY`, `GEN9_CLKGATE_DIS_5`, and `GEN9_CLKGATE_DIS_0`. Predicate helpers store no state; they encode static platform policy.

## Dependencies and Integration Points
Dependencies include DRM warnings, `intel_de`, display core/platform data, `intel_display_regs.h`, `intel_display_wa.h`, and stepping helpers. Integration points include init sequences and any code guarded by `intel_display_wa(display, WA_ID)`.

## Risks
The enum and switch must stay in sync. A missing case warns and returns false, which can silently skip a needed workaround. Register writes are platform-specific; applying them too broadly can disable useful clock gating or change power/latency behavior. Stepping bounds must match hardware documentation exactly.

## Test Signals
Signals include boot logs free of missing-WA warnings, register readback for applied workarounds, platform/stepping-specific CI coverage, absence of regressions in GPIO bitbanging, scaler/fatal error masking, clock gating, memory-up policy, DP/MST/FEC/PSR behavior, and power measurements after workaround changes.
