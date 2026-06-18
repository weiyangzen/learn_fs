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
