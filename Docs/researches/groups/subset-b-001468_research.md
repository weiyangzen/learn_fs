# subset-b-001468 Research

Grouped research for the listed AMDGPU ATHUB register headers. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_8_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_8_0_sh_mask.h

## Purpose
`athub_1_8_0_sh_mask.h` is a generated-style AMDGPU register field header for ATHUB 1.8.0. It defines C preprocessor constants for bit shifts and masks, letting driver code read, compose, and update individual fields in ATHUB MMIO registers without hard-coded bit arithmetic. The covered address blocks are `aid_athub_atsdec`, `aid_athub_xpbdec`, and `aid_athub_rpbdec`, which together describe address translation services, crossbar/peer routing, and request path buffering/arbiter behavior.

This file has no executable code, functions, structs, or storage of its own. Its API is the macro namespace: `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. It is paired with version-matched offset headers such as `athub_1_8_0_offset.h`; callers combine register addresses from the offset header with masks from this file.

## Important APIs, Types, And Register Families
The ATS decoder section defines masks for `ATC_ATS_CNTL`, `ATC_ATS_CNTL2`, `ATC_ATS_MISC_CNTL`, `ATC_ATS_STATUS`, fault logging/status registers, default page registers, PCIe ATS/PASID/PRI controls, VMID/PASID mapping, and VMID outstanding status. Important field groups include:

- ATS enablement and throttling: `DISABLE_ATC`, `DISABLE_PRI`, `DISABLE_PASID`, `CREDITS_ATS_RPB`, VC5/VC0 translation credits, translation stall, and GC/MM VC5 enable bits.
- Fault reporting: `ATC_ATS_FAULT_CNTL` controls log, interrupt, and crash fault tables; `ATC_ATS_FAULT_STATUS_INFO*` exposes fault type, VMID, VF/VFID, L2 number, invalidating VMIDs, status, and address-high pieces; `ATC_ATS_FAULT_STATUS_ADDR` stores the page address.
- PCIe integration: `ATHUB_PCIE_ATS_CNTL`, `ATHUB_PCIE_PASID_CNTL`, `ATHUB_PCIE_PAGE_REQ_CNTL`, `ATHUB_PCIE_OUTSTAND_PAGE_REQ_ALLOC`, and per-VF `ATHUB_PCIE_ATS_CNTL_VF_0` through `_15`.
- VMID/PASID mapping: `ATC_VMID0_PASID_MAPPING` through `ATC_VMID15_PASID_MAPPING` expose a 16-bit `PASID`, `NO_INVALIDATION`, and `VALID`; `ATC_VMID_PASID_MAPPING_UPDATE_STATUS` has one completion bit per VMID.
- Perf counters: `ATC_PERFCOUNTER{0..3}_CFG`, `ATC_PERFCOUNTER_RSLT_CNTL`, and LO/HI counter fields expose selection, mode, enable, clear, trigger, saturation, and compare bits.

The XPB decoder section covers routing and peer mapping for the ATHUB crossbar path. Repeated macros describe source aperture base registers, destination maps, XDMA destination maps, CLG configuration and match/mask registers, write-combine buffer status, peer system BARs, P2P BAR setup/delta registers, clock gating, interface status, pipe status, sub-block stall/reset controls, sticky status/W1C bits, and GFX/MM unit-id mapping. Fields such as `XPB_RTR_DEST_MAP*__DEST_OFFSET`, `DEST_SEL`, `APRTR_SIZE`, `XPB_P2P_BAR_CFG__ATC_TRANSLATED`, `XPB_P2P_BAR*__VALID`, and `XPB_SUB_CTRL__RESET_*` are the register-level contract for peer routing and isolation-sensitive P2P programming.

The RPB decoder section covers buffering, pass-through behavior, arbitration, BIF/read/write switch settings, write combining, CID queue access, performance counters, VC switching, ATS command encoding, and SDP port throttling. Notable controls include `RPB_PASSPW_CONF`, `RPB_BLOCKLEVEL_CONF`, `RPB_TAG_CONF`, `RPB_ARB_CNTL*`, `RPB_BIF_CNTL*`, `RPB_WR_SWITCH_CNTL`, `RPB_RD_SWITCH_CNTL`, `RPB_PERF_COUNTER_CNTL`, `RPB_ATS_CNTL`, `RPB_ATS_CNTL2`, and `RPB_SDPPORT_CNTL`.

## Control Flow
There is no runtime control flow inside the header. Control flow is imposed by consumers that use these macros in MMIO read-modify-write sequences. A typical path is:

1. Resolve a register offset through `SOC15_REG_OFFSET(ATHUB, instance, reg...)` or related AMDGPU macros.
2. Read a 32-bit register using `RREG32`/`RREG32_SOC15`.
3. Test a `*_MASK`, or clear and set masked bits with values shifted by the corresponding `*_SHIFT`.
4. Write the updated value using `WREG32`/`WREG32_SOC15`.

The VMID/PASID mapping fields are known integration points. `amdgpu_amdkfd_gc_9_4_3.c` includes this header and writes `ATC_VMID0_PASID_MAPPING + vmid` using `ATC_VMID0_PASID_MAPPING__PASID_MASK` and `ATC_VMID0_PASID_MAPPING__VALID_MASK`, then polls `ATC_VMID_PASID_MAPPING_UPDATE_STATUS` until the remap bit for that VMID appears. Similar KFD/GMC code for other generations uses the same field contract.

## State And Persistence Behavior
The header does not persist state. The state it names lives in GPU hardware registers. Some registers represent configuration state that persists until GPU reset or driver reprogramming, such as VMID/PASID mappings, PCIe ATS/PASID enablement, P2P BAR mappings, routing maps, arbitration thresholds, clock/light-sleep settings, and performance-counter configuration. Other registers expose transient status or counters, such as ATS busy/crashed/deadlock indicators, VMID outstanding bits, XPB/RPB buffer fullness, pipe status, performance counter values, and sticky/W1C error bits.

State semantics are hardware-specific and often side-effectful. `*_W1C` registers clear bits when written with ones; update-status registers are used as completion/ack bits; reset and stall controls in `XPB_SUB_CTRL` can disrupt live traffic; and fault-status registers reflect captured errors rather than ordinary software-owned memory.

## Dependencies And Integration Points
The file depends only on the C preprocessor and its include guard. It is meaningful only with the matching ATHUB register offset/base headers and AMDGPU MMIO helpers. Integration points include:

- KFD VMID/PASID programming for process address-space binding on GPU queues.
- GMC and memory-management paths that query PASID mappings or program address-translation behavior.
- ATHUB clock/light-sleep and power-management code through `ATHUB_MISC_CNTL` fields.
- PCIe ATS, PASID, PRI, and per-VF controls used for IOMMU-aware and SR-IOV operation.
- RAS/error handling through ATHUB fault status, interrupt/crash masks, sticky bits, and ATHUB error-event routing in NBIO/NBIF paths.
- Performance/debug tooling that programs ATC or RPB performance counters.

The names are part of a generated register ABI inside the driver tree. Version mismatches matter: consumers using `reg...` names from `athub_1_8_0_offset.h` must use field layouts from this same hardware generation.

## Risks
The largest risk is silent corruption from bitfield drift. A wrong mask or shift can enable ATS/PASID incorrectly, acknowledge or suppress faults, misroute peer traffic, corrupt VMID/PASID ownership, or wedge the ATHUB path through reset/stall fields. Repeated register families are easy to misuse because many entries have identical layouts but distinct hardware addresses. Some fields are security-sensitive in virtualized environments, especially per-VF ATS enable bits, shared virtual reset request fields, active function ID fields, PASID validity, and P2P BAR translation flags.

Because this header is usually generated from hardware register descriptions, hand edits are risky. If hardware docs change, the offset header, mask header, and any default-value header should be regenerated and reviewed as a set. The `L` suffix on 32-bit masks also means callers should avoid assumptions about signedness and should use `u32`-style register values in normal kernel code.

## Test Signals
Build coverage is the first signal: any typo in macro names used by C files fails compilation. Stronger signals come from GPU initialization and KFD tests that exercise VMID/PASID mapping, PASID lookup, process queue creation, and teardown. Runtime signals include successful ATS/PASID enablement on supported platforms, absence of ATHUB RAS/ERREVENT interrupts, no hangs while polling `ATC_VMID_PASID_MAPPING_UPDATE_STATUS`, stable suspend/resume and GPU reset behavior, and expected values in debug register dumps. For performance-counter fields, useful tests are counter programming smoke tests that verify clear, enable, saturation, and LO/HI reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_8_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_0_0_default.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_2_0_0_default.h -->
