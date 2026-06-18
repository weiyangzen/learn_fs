# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_sh_mask.h lines 4761-7204

## Scope And Purpose

This chunk is a generated-style AMDGPU MMHUB 3.0.0 register field header. It contains C preprocessor constants only: every hardware field is represented as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` macros. There are no C functions, structs, enums, storage objects, or executable branches in this range.

The range starts inside the `MMVM_L2_CNTL3` register definition and then covers most of the MMHUB MMUTCL2/MMVML2 virtual-memory control surface: L2 status and fault handling, identity aperture fields, L2 cache/cache-parity controls, VM context controls for contexts 0-15, invalidation engines 0-17, page-table base/start/end address registers for contexts 0-15, PTE cache fragment-size controls, MMHUB and UTCL2 performance counters, per-VF framebuffer size/offset registers, and the beginning of PF/shared aperture controls. The chunk ends at line 7204 in the middle of `MMMC_VM_FB_NOALLOC_CNTL`; the remaining masks for that register are outside this work item.

The companion offset header is `mmhub_3_0_0_offset.h`. That file maps register names such as `regMMVM_CONTEXT0_CNTL`, `regMMVM_INVALIDATE_ENG0_REQ`, and `regMMMC_VM_FB_SIZE_OFFSET_VF0` to MMIO offsets; this `_sh_mask.h` chunk defines the bit layout used to compose or decode the 32-bit values at those offsets.

## Important APIs, Types, And Constants

There are no callable APIs or declared C types. The public interface is the macro namespace consumed by AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15*`, `RREG32_SOC15*`, and `SOC15_REG_OFFSET`.

The main macro families in this chunk are:

- `MMVM_L2_CNTL3` tail fields: cache bank selection, update mode, wildcard reference value, big-page and 4K effective-size/associativity controls, and force-miss bits for 4K PTE, big-page PTE, and PDE caches. The register begins before this chunk.
- `MMVM_L2_STATUS`: L2 busy state, per-context/domain busy bitmap, and parity-error indicators for 4K PTE, big-page PTE, and PDE cache levels.
- Dummy-page and protection-fault registers: `MMVM_DUMMY_PAGE_FAULT_CNTL`, dummy-page fault address low/high, `MMVM_L2_PROTECTION_FAULT_CNTL`, `CNTL2`, `MM_CNTL3`, `MM_CNTL4`, `STATUS`, fault logical address low/high, and default physical page address low/high.
- Identity aperture registers: `MMVM_L2_CONTEXT1_IDENTITY_APERTURE_LOW_ADDR_*`, `HIGH_ADDR_*`, and `MMVM_L2_CONTEXT_IDENTITY_PHYSICAL_OFFSET_*`, which describe logical identity aperture bounds and physical offsets.
- L2 cache and routing controls: `MMVM_L2_CNTL4`, `MMVM_L2_MM_GROUP_RT_CLASSES`, `MMVM_L2_BANK_SELECT_RESERVED_CID`, `MMVM_L2_BANK_SELECT_RESERVED_CID2`, `MMVM_L2_CACHE_PARITY_CNTL`, `MMVM_L2_CGTT_CLK_CTRL`, `MMVM_L2_CNTL5`, `MMVM_L2_GCR_CNTL`, `MMVM_L2_CGTT_BUSY_CTRL`, `MMVM_L2_PTE_CACHE_DUMP_CNTL`, `MMVM_L2_PTE_CACHE_DUMP_READ`, and `MMVM_L2_BANK_SELECT_MASKS`.
- Credit-safety registers: `MMUTCL2_CREDIT_SAFETY_GROUP_RET_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_CDC`, `MMUTCL2_CREDIT_SAFETY_GROUP_CLIENTS_INVREQ_NOCDC`, `MMVML2_CREDIT_SAFETY_IH_FAULT_INTERRUPT`, and `MMVML2_WALKER_CREDIT_SAFETY_FETCH_RDREQ`. Each exposes a credit count plus an update bit.
- Address block `mmhub_mmutcl2_mmvml2vcdec`: `MMVM_CONTEXT0_CNTL` through `MMVM_CONTEXT15_CNTL`, all sharing the same field layout for `ENABLE_CONTEXT`, `PAGE_TABLE_DEPTH`, `PAGE_TABLE_BLOCK_SIZE`, retry behavior, and default/interrupt enables for range, dummy-page, PDE0, valid, read, write, and execute protection faults.
- `MMVM_CONTEXTS_DISABLE`: a packed disable bitmap for contexts 0-15.
- Invalidation engines 0-17: `MMVM_INVALIDATE_ENGn_SEM`, `REQ`, `ACK`, `ADDR_RANGE_LO32`, and `ADDR_RANGE_HI32`. Request fields include per-VMID invalidation bitmap, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, protection-fault address clearing, request logging, and 4K-only invalidation. Acknowledgements expose per-VMID ack plus semaphore state.
- Per-context page-table address registers: for contexts 0-15, `PAGE_TABLE_BASE_ADDR_LO32/HI32` expose full 64-bit page-directory-entry fields, while `PAGE_TABLE_START_ADDR_LO32/HI32` and `PAGE_TABLE_END_ADDR_LO32/HI32` expose logical page-number bounds with 32 low bits and 4 high bits.
- PTE fragment-size controls: `MMVM_L2_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` plus context-specific `MMVM_L2_CONTEXT0_PER_PFVF_PTE_CACHE_FRAGMENT_SIZES` through `CONTEXT15`, containing PF/VF and context fragment sizes for PTE cache behavior.
- Address block `mmhub_mmutcl2_mmvml2pldec`: `MMMC_VM_L2_PERFCOUNTER0_CFG` through `7_CFG`, `MMMC_VM_L2_PERFCOUNTER_RSLT_CNTL`, `MMUTCL2_PERFCOUNTER0_CFG` through `3_CFG`, and `MMUTCL2_PERFCOUNTER_RSLT_CNTL`. These cover performance event selection ranges, modes, enable/clear bits, start/stop triggers, global enable/clear, and stop-on-saturate.
- Address block `mmhub_mmutcl2_mmvml2prdec`: `MMMC_VM_L2_PERFCOUNTER_LO/HI` and `MMUTCL2_PERFCOUNTER_LO/HI`, with low 32-bit counter values and high 16-bit counter/compare-value packing.
- Address block `mmhub_mmutcl2_mmvmsharedhvdec`: `MMMC_VM_FB_SIZE_OFFSET_VF0` through `VF15`, each packing a 16-bit VF framebuffer size and 16-bit VF framebuffer offset.
- Address block `mmhub_mmutcl2_mmvmsharedpfdec`: `MMMC_VM_FB_OFFSET`, system aperture default physical page-number low/high, default steering, memory power light-sleep setup/hold, cacheable DRAM range, local sysmem range, APT controls, local FB range, local FB address lock, `MMUTCL2_CGTT_CLK_CTRL`, `MMUTCL2_CGTT_BUSY_CTRL`, and the first part of `MMMC_VM_FB_NOALLOC_CNTL`.

## Control Flow And State Behavior

The header has no runtime control flow. The C preprocessor substitutes constants into driver code that performs MMIO reads, writes, and read-modify-write operations against MMHUB registers.

Runtime state lives in the GPU. The context-control fields program how VMIDs translate memory: whether a context is enabled, page-table depth and block size, and whether different fault classes interrupt, retry, or fall back to default behavior. The page-table base/start/end registers define the active translation roots and logical aperture ranges for each context. The invalidation engine registers implement a hardware protocol: software writes semaphore/request/address-range registers, hardware updates acknowledgement bits, and callers poll or otherwise synchronize with the ack state.

Fault state is also hardware-resident. `MMVM_L2_PROTECTION_FAULT_STATUS` encodes whether more faults are queued, walker error class, permission bits, mapping error, client ID, read/write direction, atomic access, VMID, VF/VFID, and PRT status. Fault address and default-address registers expose the logical faulting page and fallback physical page location. Control bits such as `CLEAR_PROTECTION_FAULT_STATUS_ADDR`, retry fault interrupt enablement, and crash-on-fault settings influence how the hardware records and escalates faults.

Cache, clock-gating, credit, and performance-counter registers are stateful knobs around the translation cache. Cache fields configure fragment sizes, associativity, partitioning, force-miss behavior, parity checking, PTE dump selection/readback, and group real-time classes. Performance-counter config registers select events and modes, then enable or clear accumulation; result-control registers select counters, start/stop triggers, global clear, and stop-on-saturate behavior.

Persistence is hardware-local. Values generally persist only until reset, power-gating, firmware reinitialization, or driver reprogramming. This header does not store state, serialize access, distinguish read-only from write-only fields, or restore values across suspend/resume.

## Dependencies And Integration Points

The immediate register-offset dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_3_0_0_offset.h`. In that file, representative offsets are `regMMVM_L2_STATUS` at `0x0703`, `regMMVM_CONTEXT0_CNTL` at `0x0740`, `regMMVM_INVALIDATE_ENG0_REQ` at `0x0763`, `regMMMC_VM_L2_PERFCOUNTER0_CFG` at `0x0824`, `regMMMC_VM_FB_SIZE_OFFSET_VF0` at `0x084c`, and `regMMMC_VM_FB_OFFSET` at `0x08d7`.

The direct in-tree consumer for this exact header is `drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, which includes `mmhub/mmhub_3_0_0_offset.h`, `mmhub/mmhub_3_0_0_sh_mask.h`, and default-value headers. Important uses include:

- `mmhub_v3_0_get_invalidate_req()`: builds an invalidation request with `MMVM_INVALIDATE_ENG0_REQ` fields for per-VMID invalidation, flush type, L2 PTE/PDE invalidation, L1 PTE invalidation, and protection-fault-address clearing.
- `mmhub_v3_0_print_l2_protection_fault_status()`: decodes `MMVM_L2_PROTECTION_FAULT_STATUS` with `REG_GET_FIELD` to report client ID, read/write direction, walker errors, permission faults, VMID, VF/VFID, and PRT state.
- MMHUB cache/TLB initialization paths: program `MMVM_L2_CNTL3`, `MMVM_L2_CNTL4`, and `MMVM_L2_CNTL5` fields, including cache fragment-size and physical-request controls.
- `mmhub_v3_0_enable_system_domain()` and `mmhub_v3_0_setup_vmid_config()`: use `MMVM_CONTEXT0_CNTL` and `MMVM_CONTEXT1_CNTL` field macros to enable contexts, set page-table depth/block size, and configure protection-fault behavior for contexts 1-15 through offset strides.
- `mmhub_v3_0_disable_identity_aperture()`: writes the identity aperture and physical offset registers covered here, skipping VF-SRIOV where the PF is responsible.
- `mmhub_v3_0_program_invalidation()`: initializes all 18 invalidation engine address-range registers to the full supported range using the engine address stride.
- MMHUB register base setup: stores SOC15 offsets for context base address, invalidation semaphore/request/ack, context-control, L2 protection fault status/control, and bank-select reserved CID2; it derives `ctx_distance`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance` from adjacent register offsets.

Similar macro families appear in `mmhub_3_0_1_sh_mask.h`, `mmhub_4_1_0_sh_mask.h`, and `mmhub_4_2_0_sh_mask.h`, but exact field widths and high-address masks differ by IP version. Call sites must include the matching generation header rather than assuming a common MMHUB layout.

## Risks And Edge Cases

- This file is a hardware ABI. A wrong mask or shift can still compile while programming the wrong bit in VM translation, fault, invalidation, or cache-control hardware.
- The chunk starts inside `MMVM_L2_CNTL3`; whole-file research should combine it with the prior chunk before describing the full register.
- The chunk ends inside `MMMC_VM_FB_NOALLOC_CNTL`; line 7204 includes `ROUTER_ATCL2_NOALLOC_MASK`, while `ROUTER_GPA_MODE2_NOALLOC_MASK` and `ROUTER_GPA_MODE3_NOALLOC_MASK` continue after the boundary.
- Repeated register groups are easy to misuse. Context 0 is the system/domain context, while contexts 1-15 are often programmed by stride from `MMVM_CONTEXT1_*`; invalidation engines 0-17 similarly rely on offset arithmetic. A correct-looking macro from the wrong context or engine can target the wrong register.
- Invalidation request, ack, and semaphore bits form a synchronization protocol with hardware. If callers set a flush type or per-VMID bitmap incorrectly, stale translations can remain visible or software can wait on the wrong acknowledgement bit.
- Fault-control bits can change system behavior sharply. Defaulting, interrupting, retrying, or crashing on retry/no-retry faults affects both diagnostics and user-visible GPU recovery behavior.
- Full-width masks such as `0xFFFFFFFFL` should be treated as unsigned 32-bit fields. Signed promotion can confuse diagnostics or static comparisons.
- Status, fault, counter, and cache-dump registers can be read-only, sticky, write-one-to-clear, or have other side effects depending on the hardware guide. The macro header does not encode access type.
- Per-VF framebuffer size/offset registers are virtualization-sensitive. Misprogramming VF size or offset can expose an incorrect framebuffer aperture or break SR-IOV isolation assumptions.
- Power and clock-gating controls such as `CGTT_CLK_CTRL`, light-sleep setup/hold, and busy overrides are low-level hardware knobs; invalid values can cause hangs, excessive power, or missed idle/busy transitions.

## Test And Validation Signals

There are no direct unit tests for this macro-only header chunk. Useful validation is compile-time, static, and hardware-oriented:

- Build AMDGPU configurations that include `mmhub_v3_0.c` and `mmhub_3_0_0_sh_mask.h`.
- Run static mask/shift checks: single-bit masks should match their shift, multi-bit masks should be contiguous, packed repeated fields should not overlap, and full-width masks should have shift zero.
- Cross-check every register-comment group in this chunk against `mmhub_3_0_0_offset.h` to verify that each register has a matching `reg*` offset and base index.
- Exercise MMHUB GART/VM bring-up on MMHUB 3.0 hardware and confirm that context enablement, page-table start/end bounds, identity aperture disablement, and invalidation address ranges match the values programmed by `mmhub_v3_0.c`.
- Trigger or inspect MMHUB VM fault reporting and verify that `MMVM_L2_PROTECTION_FAULT_STATUS` decodes client ID, RW, VMID, VF/VFID, permission, mapping, and PRT fields consistently with register dumps.
- Exercise GPUVM invalidation paths and verify request/ack progression for all active VMIDs; stale translation symptoms after mapping changes are a strong signal of bad invalidation masks.
- If performance counters are used by diagnostics, verify enable, clear, event select, result select, high/low readback, compare value, and stop-on-saturate behavior against hardware documentation.
- For SR-IOV, validate that PF-owned identity aperture and VF framebuffer size/offset programming are not touched by VF-only code paths and that VF register dumps reflect the expected aperture partitioning.

## Chunk Notes For Merge Lane

This chunk covers the central MMVM/MMUTCL2 field definitions for `mmhub_3_0_0_sh_mask.h`, especially VM contexts, invalidation engines, L2 fault/cache controls, performance counters, and PF/VF aperture fields. Merge with adjacent chunks before making whole-file claims about `MMVM_L2_CNTL3` or `MMMC_VM_FB_NOALLOC_CNTL`, because both register groups are split by this chunk's boundaries.
