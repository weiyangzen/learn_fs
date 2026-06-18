# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_0_0_default.h

## Purpose
`athub_2_0_0_default.h` defines reset/default values for ATHUB 2.0.0 registers. Unlike a shift/mask header, it does not describe individual fields; it records the expected 32-bit baseline value for each register as `mm<REGISTER>_DEFAULT`. Driver code can use these constants to compare hardware state, restore defaults, seed golden settings, or document the hardware reset contract for ATHUB 2.0.0.

The file is declarative C preprocessor data. It contains no functions, structs, enums, or executable control flow. It is included by `amdgpu/athub_v2_0.c` together with `athub_2_0_0_offset.h` and `athub_2_0_0_sh_mask.h`, so the default values are version-aligned with the register addresses and field masks used by ATHUB v2.0 code.

## Important APIs, Types, And Register Families
The API surface is the `mm..._DEFAULT` macro namespace. The defaults are grouped by address block:

- `athub_atsdec`: ATS control/status, fault controls, VMID/PASID mappings, ATC performance counters, PCIe ATS/PASID/PRI/page-request controls, per-VF ATS controls for VF 0 through VF 30, ATHUB memory-power/light-sleep and interrupt-handler credits, VMID 16 through 31 mappings, shared virtualization registers, SDP port control, and GFX/MMHUB VMID snapshot status.
- `athub_xpbdec`: XPB routing source apertures, XDMA apertures, destination maps, CLG configuration, P2P BAR configuration and peer system BAR defaults, clock gating/interface/pipe/sub-control defaults, sticky registers, CLG match/mask values, and GFX/MM/GUS unit-id mappings.
- `athub_rpbdec`: RPB pass-through, block-level, tag, efficiency, arbitration, BIF, read/write switch and combine controls, CID queue defaults, performance counter configuration, queue controls, ATS controls, and SDP port controls.

Many defaults are zero, reflecting disabled or idle hardware state. Non-zero defaults are operationally important: `mmATC_ATS_CNTL_DEFAULT` is `0x009a0c00`, `mmATC_ATS_FAULT_CNTL_DEFAULT` enables a low fault-register-log mask as `0x000001ff`, `mmATC_TRANS_FAULT_RSPCNTRL_DEFAULT` is all ones, `mmATHUB_MISC_CNTL_DEFAULT` is `0x001c0200`, ATC/RPB result controls default to `0x04000000`, XPB P2P BAR config defaults to `0x0000000f`, XPB clock/interface/match settings have non-zero fabric defaults, and RPB arbitration/ATS/SDP controls are preloaded with non-zero tuning values.

## Control Flow
There is no internal control flow. Runtime flow appears in consumers:

1. ATHUB v2.0 code includes this header beside the matching offset and mask headers.
2. Initialization or power-management code reads live registers through `RREG32_SOC15(ATHUB, 0, mm...)`.
3. It may compare or restore against `mm..._DEFAULT`, or use defaults as reference values when applying clock-gating/light-sleep changes.
4. Writes are performed through AMDGPU MMIO helpers only when live data differs from the desired value.

In the current tree, `athub_v2_0.c` includes this header but primarily manipulates `mmATHUB_MISC_CNTL` through mask constants for medium-grain clock gating and memory light sleep. That inclusion still makes the reset defaults available to any v2.0 ATHUB implementation file that needs a known baseline.

## State And Persistence Behavior
The header itself stores no state. It describes hardware reset/default state for GPU registers. These defaults are persistent only as source constants in the driver; actual register contents live in the GPU and can change during boot, runtime power management, SR-IOV setup, KFD process binding, ATS/PASID enablement, RAS handling, or debug/performance-counter programming.

Defaults are especially relevant after GPU reset, resume, or IP block reinitialization. Zero defaults for VMID/PASID mappings and per-VF ATS controls imply mappings and VF ATS enablement must be explicitly established. Non-zero queue, arbiter, SDP, and credit defaults imply hardware is not simply blank at reset; preserving or restoring those values may be necessary for stable traffic flow.

## Dependencies And Integration Points
The file depends only on the preprocessor include guard, but it is semantically tied to:

- `athub_2_0_0_offset.h`, which defines `mm...` register addresses matching these `mm..._DEFAULT` names.
- `athub_2_0_0_sh_mask.h`, which defines fields used to interpret or modify the same registers.
- `athub_v2_0.c`, which includes the default header in the ATHUB v2.0 power-management implementation.
- `gmc_v10_0.c` and `amdgpu_amdkfd_gfx_v10.c`, which include v2.0 ATHUB offset/mask headers for PASID and VMID integration.
- SOC15 register-access helpers and the `ATHUB_HWIP` register base mapping established during ASIC initialization.

The header also integrates conceptually with PCIe/IOMMU ATS and PASID support, KFD process address spaces, SR-IOV VF handling, AMDGPU clock-gating flags, and RAS/error reporting paths that distinguish ATHUB as a hardware block.

## Risks
Incorrect defaults can produce subtle regressions even if compilation succeeds. A wrong non-zero value can change arbitration, credits, low-power timing, or ATS command behavior after reset. A wrong zero can leave required hardware tuning unapplied. Defaults for `mmATC_TRANS_FAULT_RSPCNTRL_DEFAULT`, `mmATC_ATS_FAULT_CNTL_DEFAULT`, per-VF ATS controls, `mmATHUB_SHARED_*`, and RPB ATS controls are security and reliability sensitive because they influence fault handling, translation behavior, and virtualization-facing state.

Because the header is a hardware contract, the main maintenance risk is version skew: using ATHUB 2.0.0 defaults with 2.1/3.x/4.x offsets or masks can write plausible-looking but incorrect values. Another risk is assuming defaults are safe runtime values; some registers are status, W1C, queue, or counter registers and should not necessarily be restored blindly during live operation.

## Test Signals
Compilation verifies macro availability when included by `athub_v2_0.c`. Runtime signals include clean ATHUB v2.0 initialization, stable clock-gating/light-sleep toggles, no unexpected ATHUB RAS events, successful KFD VMID/PASID mapping on v10-class hardware, and correct resume/reset behavior. Register-dump comparison after reset can validate that live hardware matches the documented defaults for immutable reset fields. Stress tests that exercise PCIe ATS/PASID, SR-IOV VFs, P2P BAR routing, and RPB/XPB traffic are the most useful behavioral checks for default-value drift.
