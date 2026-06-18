# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/hdp/hdp_5_0_0_sh_mask.h

## Purpose

`hdp_5_0_0_sh_mask.h` defines the HDP 5.0.0 register field shifts and masks used by AMDGPU read-modify-write helpers. It is the field-level contract for the offsets in `hdp_5_0_0_offset.h` and is directly included by `hdp_v5_0.c`.

## Important APIs, types, and macros

The file defines no functions or structs. Important macro groups include:

- `HDP_MMHUB_TLVL__*` and `HDP_MMHUB_UNITID__*` fields, with 3-bit traffic-level masks as in HDP 4.0.
- Surface and non-surface read/write flag fields and clear fields.
- `HDP_HOST_PATH_CNTL` fields, including write-combine controls, `RD_CPL_BUF_EN`, `ALL_SURFACES_DIS`, `WRITE_THROUGH_CACHE_DIS`, and `LIN_RD_CACHE_DIS`.
- `HDP_READ_CACHE_INVALIDATE__READ_CACHE_INVALIDATE`, used by the invalidation path.
- `HDP_MISC_CNTL` fields for flush invalidate, idle hysteresis, multiple reads, raw address CAM, early write ack, FED/atomic FED, syshub priority, MMHUB burst, pending-write tag checks, and cacheline behavior.
- `HDP_MEM_POWER_CTRL` fields for IPH and RC memory power control, LS, DS, SD, idle hysteresis, power-up recovery, and power-down enter delays.
- `HDP_EDC_CNT` fields for four memory SED counters (`MEM0` through `MEM3`).
- `HDP_CLK_CNTL` fields for IPH/RC memory clock soft overrides plus DBUS, dynamic, XDP, and HDP register clock overrides.
- XDP/P2P and diagnostics fields, including 24-bit busy bits, IOV VFID mask `0x01F00000`, `GPU_IOV_VIOLATION_LOG2__INITIATOR_ID`, and MMHUB error response/NACK bits.

## Control flow

The file has no runtime branching. It enables call-site control flow in `hdp_v5_0.c`: `REG_SET_FIELD()` toggles `HDP_MEM_POWER_CTRL` fields in a defined order; clock-gating code masks `HDP_CLK_CNTL__*SOFT_OVERRIDE_MASK` values; init sets `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE_MASK`; invalidation uses the read-cache invalidate field with the offset header.

## State and persistence behavior

The fields represent hardware state in HDP registers. Memory power gating and clock override fields persist until rewritten and control whether HDP SRAMs/clocks can enter LS/DS/SD or medium-grain clock gating. Cache and invalidation fields affect coherency state. Diagnostic fields capture sticky or status information for busy conditions, IOV violations, and MMHUB response errors.

## Dependencies and integration points

This header depends on `hdp_5_0_0_offset.h` for register addresses and on AMDGPU token-pasting register helper conventions. `hdp_v5_0.c` uses these masks with `REG_SET_FIELD()` and direct bitwise checks. The power-gating fields integrate with runtime `adev->cg_flags` and AMD power-management reporting, while the invalidate field integrates with KIQ/no-KIQ and ring write-register paths.

## Risks

Field layout errors can produce subtle runtime failures. The power-gating sequence must not enable multiple mutually exclusive LS/DS/SD modes at once, and wrong masks could do so. Clock override masks must match the bits cleared for MGCG; otherwise `get_clockgating_state()` can report false positives. `HDP_MISC_CNTL__FLUSH_INVALIDATE_CACHE_MASK` is a coherency-critical field. The VFID width differs from 4.4.2 (`0x01F00000` here versus `0x00F00000` there), so diagnostics must use the correct generation.

## Test signals

Compile-time validation should cover all `REG_SET_FIELD()` and bitwise mask users in `hdp_v5_0.c`. Runtime validation should toggle LS/DS/SD and MGCG, confirm clock-gating state reads back correctly, exercise HDP cache invalidation in direct and ring paths, and monitor IOV/MMHUB error decoding under SR-IOV and P2P workloads. Static generation-diff tests should compare masks against the HDP 5.0.0 register source.
