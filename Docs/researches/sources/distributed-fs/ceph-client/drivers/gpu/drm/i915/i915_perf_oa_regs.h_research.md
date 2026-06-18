# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_perf_oa_regs.h

## Purpose

`i915_perf_oa_regs.h` defines the OA/OAR/OAM MMIO register addresses and bit fields used by the i915 performance subsystem. It is a hardware-contract header: the macros describe where to program OA buffers, head/tail pointers, control/status registers, trigger registers, context controls, and selected workarounds across Gen7, Gen8, Gen12 OAG/OAR, and Gen12 OAM units.

## Important APIs, types, and functions

The exported API is entirely preprocessor macros. Major groups include Gen7 `GEN7_OACONTROL`, `GEN7_OABUFFER`, `GEN7_OASTATUS1`, `GEN7_OASTATUS2`; Gen8 `GEN8_OACONTROL`, `GEN8_OACTXCONTROL`, `GEN8_OA_DEBUG`, `GEN8_OABUFFER`, `GEN8_OAHEADPTR`, `GEN8_OATAILPTR`, `GEN8_OASTATUS`; Gen12 OAR `GEN12_OAR_OACONTROL` and `GEN12_OACTXCONTROL(base)`; Gen12 OAG `GEN12_OAG_*`; and OAM offset/function macros such as `GEN12_OAM_HEAD_POINTER(base)`, `GEN12_OAM_CONTROL(base)`, `GEN12_OAM_STATUS(base)`, trigger ranges, CEC ranges, and `GEN12_OAM_PERF_COUNTER_B(base, idx)`.

## Control flow

The header has no executable control flow. Consumers select the appropriate macro family by platform and OA unit type. `i915_perf.c` stores these registers in `struct i915_perf_regs`, programs head/tail/buffer/control/status during stream enable/disable, checks overflow/report-lost bits during read, and builds MMIO allowlists for dynamic OA config validation.

## State and persistence behavior

The file owns no mutable state but names stateful hardware locations. OA buffer state persists in hardware head/tail registers and GGTT buffer base registers. Control bits enable counters, select formats, configure periodic timers, include/disable clock ratio or context-switch reports, and invalidate OA TLBs. Status bits report buffer overflow, counter overflow, report loss, and pointer wrap state. Wrong values affect persistent GPU counter collection until reset or reprogramming.

## Dependencies

It depends on `i915_reg_defs.h` for `_MMIO()` and `REG_BIT()` helpers. It is consumed by `i915_perf.c` and GVT scheduler code, and it aligns with context-control and engine register definitions from the GT headers.

## Integration points

The register constants are the bridge between uAPI metric configuration and hardware programming. `i915_perf.c` uses them to derive OAG/OAM register sets, validate userspace-supplied register addresses, enable/disable OA units, initialize circular buffers, and emit context-control updates. GVT scheduling uses the header to understand OA state in virtualized execution.

## Risks

Incorrect offsets or bit definitions can corrupt unrelated MMIO registers, fail to stop OA counters, misreport lost data, or hang the engine. Gen12 has multiple OA units with similar but distinct register layouts; mixing OAG, OAR, and OAM macros is a likely source of platform bugs. Buffer size and pointer masks must stay consistent with `OA_BUFFER_SIZE` and report alignment assumptions in `i915_perf.c`.

## Test signals

Compile coverage of `i915_perf.c` and GVT users validates macro names. Runtime tests should open OA streams on Gen7, Gen8-11, DG2, and MTL, verify status handling on overflow/report loss, and confirm OAG/OAM register programming through register dumps or selftests. Static checks can compare MMIO allowlist ranges in `i915_perf.c` with the trigger/CEC offsets defined here.
