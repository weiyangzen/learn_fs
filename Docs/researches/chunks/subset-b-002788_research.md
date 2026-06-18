# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_2_0_0_sh_mask.h lines 4837-7297

## Scope

This chunk is part of a generated AMDGPU MMHUB 2.0.0 shift/mask header. It contains C preprocessor constants for hardware register bit fields, not executable driver logic. Each field is represented by the generated AMD convention:

- `<REGISTER>__<FIELD>__SHIFT` for the field's low bit.
- `<REGISTER>__<FIELD>_MASK` for the raw 32-bit field mask.

The covered range starts mid-register in `MM_ATC_L2_CNTL2`, continues through MMHUB ATC L2, MMVM L2, VM context, invalidation, performance, SR-IOV framebuffer, MARC, IOMMU, and PCIe ATS field definitions, and ends after the first `MMVM_PCIE_ATS_CNTL_VF_0` field. The repository path is under `distributed-fs/ceph-client`, but this file is AMD GPU driver hardware metadata, not Ceph filesystem logic.

## Purpose

The purpose of this chunk is to keep MMHUB 2.0.0 driver code synchronized with the ASIC register specification for MMHUB address translation and IOMMU control. The macros let AMDGPU code compose and decode 32-bit MMIO register values with helper macros such as `REG_SET_FIELD` and `REG_GET_FIELD` while using companion offset headers for actual register addresses.

The main hardware surfaces described here are:

- ATC L2 translation-cache controls and status.
- MMVM L2 cache, page-walk, invalidation, protection-fault, identity-aperture, and parity/error controls.
- Sixteen VM contexts with repeated page-table control, base, start, and end registers.
- Eighteen invalidation engines with semaphore, request, acknowledgement, and address-range fields.
- MMVM L2 performance counters.
- SR-IOV virtual-function framebuffer size/offset windows.
- MARC base, relocation, length, enable, and read-only fields.
- IOMMU enable/performance-optimization and PCIe ATS enable fields.

## Important Macro Families

ATC L2 definitions:

- `MM_ATC_L2_CNTL2` defines bank selection, cache update mode, LRU update by write, tag-index swapping, VMID mode, and wildcard reference value fields.
- `MM_ATC_L2_CACHE_DATA0/1/2` define cache-entry readback/write data: register validity, cache-entry validity, cached attributes, virtual page address high/low, and physical page address.
- `MM_ATC_L2_CNTL3`, `MM_ATC_L2_STATUS`, and `MM_ATC_L2_STATUS2` expose invalidation delay, ATS request credits, clock-request hysteresis, busy state, and parity-error information.
- `MM_ATC_L2_MISC_CG`, `MM_ATC_L2_MEM_POWER_LS`, `MM_ATC_L2_CGTT_CLK_CTRL`, and `MM_ATC_L2_SDPPORT_CTRL` describe clock gating, memory light-sleep timing, soft override/stall controls, and SDP port clock-enable handshakes.

MMVM L2 and protection fault definitions:

- `MMVM_L2_CNTL`, `MMVM_L2_CNTL2`, `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` control L2 cache enablement, fragment processing, endian swap modes, PDE/PTE cache behavior, default-page routing, invalidation controls, cache sizing/associativity/force-miss knobs, physical tap requests, IFIFO transaction limits, clock-gating overrides, and walker priority/small-fragment size.
- `MMVM_L2_STATUS` reports L2 busy, per-context/domain busy, and parity-error discovery for 4K PTE, bigK PTE, and PDE caches.
- `MMVM_DUMMY_PAGE_FAULT_*` and `MMVM_L2_PROTECTION_FAULT_DEFAULT_ADDR_*` define dummy/default page fault controls and fallback physical page addresses.
- `MMVM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, `MM_CNTL3`, and `MM_CNTL4` define clear/update behavior, default fault enables, retry/no-retry interrupt routing, active page migration behavior, crash-on-fault bits, and per-client no-retry masks.
- `MMVM_L2_PROTECTION_FAULT_STATUS` and `ADDR_LO32/HI32` decode latched fault details: more faults, walker error, permission faults, mapping error, client ID, read/write, atomic, VMID, VF flag, VFID, and faulting logical page.
- `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_*` and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*` define identity-mapped logical aperture bounds and physical offsets for identity-access mode.
- `MMVM_L2_CACHE_PARITY_CNTL`, `MMVM_L2_IH_LOG_CNTL`, `MMVM_L2_IH_LOG_BUSY`, `MMVM_L2_GCR_CNTL`, and `MMVML2_WALKER_*_THROTTLE_*` cover parity checking/injection, interrupt-handler translation logging, per-VMID translation/invalidation busy state, GCR client selection, and page-walker macro/micro throttle windows.

VM context and invalidation definitions:

- `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL` share the same layout: context enable, page-table depth, page-table block size, retry policy for permission/invalid/other faults, and interrupt/default handling for range, dummy-page, PDE0, valid, read, write, and execute protection faults.
- `MMVM_CONTEXTS_DISABLE` packs disable bits for contexts 0-15.
- `MMVM_INVALIDATE_ENG0_SEM` through `MMVM_INVALIDATE_ENG17_SEM` provide one semaphore bit per invalidation engine.
- `MMVM_INVALIDATE_ENG0_REQ` through `MMVM_INVALIDATE_ENG17_REQ` share the same request layout: 16-bit per-VMID invalidate request bitmap, flush type, invalidate L2 PTE/PDE0/PDE1/PDE2, invalidate L1 PTEs, clear protection fault status address, log request, and 4K-pages-only selection.
- `MMVM_INVALIDATE_ENG0_ACK` through `MMVM_INVALIDATE_ENG17_ACK` report per-VMID invalidate acknowledgements and semaphore state.
- `MMVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` through `ENG17_ADDR_RANGE_LO32/HI32` define optional address-range invalidation state, including the low `S_BIT`, low logical page address bits, and high logical page address bits.
- `MMVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_*` through `CONTEXT15_PAGE_TABLE_BASE_ADDR_*` hold page-directory-entry base addresses.
- `MMVM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `END_ADDR_*` through context 15 define logical page-number aperture start/end bounds.

Performance, virtualization, MARC, and ATS definitions:

- `MMMC_VM_L2_PERFCOUNTER0_CFG` through `PERFCOUNTER7_CFG` define selector start/end, mode, enable, and clear fields. `MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MMMC_VM_L2_PERFCOUNTER_LO`, and `HI` provide selected counter readout, compare value, trigger selection, clear-all, enable-any, and stop-on-saturate behavior.
- `MMMC_VM_FB_SIZE_OFFSET_VF0` through `VF31` define 16-bit virtual-function framebuffer size and 16-bit offset fields for SR-IOV partitioning.
- `MMVM_IOMMU_MMIO_CNTRL_1` exposes `MARC_EN`.
- `MMMC_VM_MARC_BASE_LO/HI_0..3`, `MARC_RELOC_LO/HI_0..3`, and `MARC_LEN_LO/HI_0..3` define four MARC ranges with page-aligned base, relocation, length, enable, and read-only fields.
- `MMVM_IOMMU_CONTROL_REGISTER` exposes `IOMMUEN`; `MMVM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER` exposes `PERFOPTEN`.
- `MMVM_PCIE_ATS_CNTL` exposes ATS `STU` and `ATC_ENABLE`; the chunk ends after `MMVM_PCIE_ATS_CNTL_VF_0__ATC_ENABLE`.

## Control Flow and Data Flow

This header has no runtime control flow. Its behavior is compile-time preprocessing. The implied consumer flow is:

1. Include the MMHUB 2.0.0 register offset header and this shift/mask header.
2. Select the appropriate `reg...` MMIO offset for an MMHUB register.
3. Use `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or offset variants to compose, update, read, poll, or decode a 32-bit register.
4. Apply ordering, quiesce, reset, interrupt, and firmware coordination rules in the consumer driver code.

The field layout supports several regular data flows: MMHUB initialization programs L2 cache controls and context registers; VM update paths write page-table base/start/end registers; TLB invalidation paths write `MMVM_INVALIDATE_ENG*_REQ`, poll `ACK`, and coordinate with `SEM`; fault paths decode `MMVM_L2_PROTECTION_FAULT_STATUS` and address registers; SR-IOV setup writes VF framebuffer windows and VF ATS state; diagnostics configure performance counters, logging, parity injection, and read status registers.

Repository usage searches show these macro names are consumed by AMDGPU MMHUB generation files such as `amdgpu/mmhub_v3_*.c` and `amdgpu/mmhub_v4_*.c` with the same generated-header naming scheme. Those consumers initialize cache controls, context controls, invalidation requests, register spacing, and VM fault masks through AMD register helpers. This chunk itself only supplies the bit positions for the MMHUB 2.0.0 variant.

## State and Persistence Behavior

The macros persist no software state. The described state lives in hardware MMIO registers.

Durable configuration state includes L2 cache enablement and sizing, endian modes, identity aperture bounds, page-table bases and apertures for contexts 0-15, invalidation-engine address ranges, protection-fault policy, clock-gating/light-sleep settings, walker throttle limits, performance-counter configuration, VF framebuffer sizing, MARC mappings, IOMMU enablement, and ATS enablement.

Volatile or latched status includes ATC/MMVM busy bits, parity error information, per-domain busy state, protection-fault status/address, invalidation acknowledgements, per-VMID translation/invalidation logging busy bits, performance counter values, and fault/error discovery bits. Clear, latch, read-only, write-one-to-clear, and reset semantics are hardware-defined; the header exposes names and bit positions but not access rules.

Action-like fields include invalidation requests, protection-fault status clearing, performance-counter clear/clear-all, parity mismatch forcing, logging enable, crash-on-fault policy, and IOMMU/ATS enable bits. These fields can alter live memory-translation behavior and normally need strict sequencing around active GPU traffic.

## Dependencies and Integration Points

Key dependencies:

- The matching MMHUB 2.0.0 offset header must provide the corresponding register addresses for every `MM_ATC_*`, `MMVM_*`, and `MMMC_VM_*` register named here.
- AMDGPU register helpers depend on the exact generated suffixes `__SHIFT` and `_MASK`.
- MMHUB initialization, VM context setup, invalidation, reset recovery, suspend/resume, fault handling, SR-IOV, and diagnostics depend on these bit layouts matching the ASIC specification.
- Adjacent chunks are required for the complete file view. This chunk starts after earlier `MM_ATC_L2_CNTL2` fields and ends before the remaining `MMVM_PCIE_ATS_CNTL_VF_*` definitions.

Primary integration points:

- GPU virtual memory setup: context control, page-table base, start, and end registers define how MMHUB translates GPU virtual addresses.
- TLB and L2 invalidation: invalidation engines provide request/ack/semaphore flow and optional address-range invalidation for VMID-scoped cache maintenance.
- Fault handling and interrupts: protection-fault policy/status macros feed VM fault interrupt routing, retry behavior, page migration handling, and fault address decode.
- Power management: clock-gating, light-sleep, hysteresis, and soft override fields interact with power-gating and clock-gating sequences.
- SR-IOV and isolation: VF framebuffer size/offset fields, VF/VFID fault status, MARC ranges, and per-VF ATS controls are used to partition or identify virtualized traffic.
- Performance and diagnostics: L2 performance counters, parity controls, IH logging, busy status, and cache data registers support profiling and hardware debug.
- PCIe/IOMMU integration: IOMMU enable, performance optimization, ATC/ATS controls, and ATC L2 request/cache fields connect the MMHUB translation path to system IOMMU and PCIe address translation services.

## Risks and Edge Cases

- Header/offset generation mismatch is the highest risk. These masks can compile cleanly with the wrong register offsets but program the wrong hardware bits.
- The chunk boundary is artificial. A final per-file report must reconcile the preceding `MM_ATC_L2_CNTL2` fields and the following VF ATS fields to avoid incomplete register descriptions.
- Repeated register families invite off-by-one or wrong-distance errors. Contexts 0-15, invalidation engines 0-17, VFs 0-31, counters 0-7, and MARC ranges 0-3 have similar layouts but distinct offsets.
- VM context and aperture fields are safety-critical. Incorrect page-table depth, base, start, end, retry, or default fault policy can cause GPU VM faults, silent memory aliasing, or access outside intended apertures.
- Invalidation programming has liveness risk. Bad VMID masks, flush type, semaphore handling, or polling of `ACK` can leave stale translations, hang invalidation, or race active page-table updates.
- Fault controls can hide or over-escalate errors. Disabling interrupts/default routing may mask faults; enabling crash-on-fault bits can convert recoverable faults into GPU resets.
- Parity injection, force-miss, logging, and performance controls are diagnostic surfaces. Leaving them enabled outside tests can degrade performance, create artificial errors, or perturb timing-sensitive paths.
- SR-IOV framebuffer and MARC fields must preserve isolation. Misprogrammed VF size/offset, relocation, read-only, or enable fields can overlap guest apertures or expose host memory.
- Clock-gating and light-sleep fields may require idle-state sequencing not visible in the header. Read-modify-write should preserve reserved bits unless generation-specific code intentionally writes full defaults.
- ATS/IOMMU enablement depends on platform and PCIe/IOMMU state. Enabling ATC/ATS without matching system support or invalidation discipline can produce stale or unauthorized translations.

## Test and Verification Signals

Useful signals are mostly build, static audit, and hardware integration tests:

- Compile coverage for MMHUB 2.0.0 code paths that include the matching offset and shift/mask headers.
- Generated-header audits that every `__SHIFT` has a matching `_MASK`, masks align with shifts, repeated context/invalidation/VF/MARC families are complete, and companion offsets exist.
- Register readback tests after MMHUB initialization to confirm L2 cache controls, context controls, page-table bases, apertures, and invalidation engine spacing decode to expected values.
- GPU VM stress tests that exercise page-table updates, VMID switching, TLB invalidation, address-range invalidation, retry/no-retry faults, and suspend/resume or reset recovery.
- Fault-injection or negative-access tests that validate `MMVM_L2_PROTECTION_FAULT_STATUS`, fault address registers, interrupt routing, and clear behavior.
- SR-IOV tests with multiple VFs checking framebuffer partitioning, VF/VFID fault attribution, MARC isolation, and VF ATS enable/disable behavior.
- PCIe ATS/IOMMU tests on platforms with ATS enabled and disabled, verifying translation correctness and invalidation ordering.
- Performance/debug tests that configure L2 counters, parity controls, IH logging, cache data registers, and busy/status registers without causing hangs or persistent side effects.

## Cross-Chunk Notes

This chunk begins at line 4837, after earlier `MM_ATC_L2_CNTL2` fields have already been defined in the previous chunk. It ends at line 7297 immediately after `MMVM_PCIE_ATS_CNTL_VF_0__ATC_ENABLE_MASK`; definitions for additional ATS VF registers continue in the next chunk. The later merge/reconciliation lane should combine adjacent chunks before drawing whole-file conclusions for `mmhub_2_0_0_sh_mask.h`.
