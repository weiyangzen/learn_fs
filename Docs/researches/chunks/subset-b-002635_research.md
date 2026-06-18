# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_sh_mask.h lines 7194-9653

## Scope

This chunk is a generated AMD GC 9.1 shift/mask register-header segment. It contains C preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for composing or decoding 32-bit GPU register values. There are no functions, structs, enums, variables, allocations, locks, callbacks, includes, or executable branches in this range.

The selected lines begin in the tail of the `VM_CONTEXT9_CNTL` mask list, then cover VM context control for contexts 10-15, global VM-context disable bits, VM invalidation engines 0-17, per-context page table base/start/end addresses for contexts 0-15, VM shared memory-controller aperture/TLB controls, and a large `gc_ea_gceadec` block for GCEA DRAM and IO request grouping, priority, address normalization, and address decode. Although this path sits under a `ceph-client` mirror, this file is AMDGPU DRM hardware metadata, not Ceph filesystem logic.

## Purpose

`gc_9_1_sh_mask.h` supplies bit layouts for the GC 9.1 graphics IP. Driver code pairs these masks with register addresses from the matching `gc_9_1_offset.h` header and uses AMDGPU register helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` to pack fields for MMIO writes, command-stream setup, firmware initialization, or diagnostic reads.

This chunk describes three main hardware surfaces:

- GPU virtual memory context programming: context enable, page-table depth/block size, retry behavior, fault interrupt/default controls, global context disable bits, invalidation engine request/ack/semaphore fields, invalidation address ranges, and per-context page table base/start/end logical page numbers.
- VM shared memory-controller policy: NB MMIO and PCI aperture controls, top-of-DRAM and framebuffer/system/AGP aperture ranges, default physical aperture address, direct-system/cacheable/local-HBM aperture configuration, reset request bits for PF/VF virtualization, memory light-sleep timing, and L1 TLB/ATC controls.
- GCEA/effective-address memory scheduling and decode: DRAM and IO client-to-group maps, group-to-virtual-channel maps, lazy delays, CAM depth/reorder limits, page burst limits, priority aging/queue/fixed/urgency/quantum thresholds, address normalization, DRAM/GMI bank/channel/chip-select/rank-mask selection, hashing, harvesting, and duplicated address decoder 0/1 mappings for primary and secondary chip selects.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit index of a field.
- `<REGISTER>__<FIELD>_MASK` gives the 32-bit field mask.
- Register-address symbols are supplied by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h`.
- AMDGPU consumers typically combine these definitions with `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, and ASIC-specific initialization or golden-register tables.

Notable macro families in this slice are:

- `VM_CONTEXT10_CNTL` through `VM_CONTEXT15_CNTL`: per-VMID context enable, page table depth, page table block size, retry-on-fault controls, and individual fault interrupt/default behavior for range, dummy-page, PDE0, valid, read, write, and execute protection faults. The chunk also includes the last eight mask macros for `VM_CONTEXT9_CNTL`.
- `VM_CONTEXTS_DISABLE`: one disable bit for each VM context 0-15.
- `VM_INVALIDATE_ENG*_SEM`, `VM_INVALIDATE_ENG*_REQ`, `VM_INVALIDATE_ENG*_ACK`, and `VM_INVALIDATE_ENG*_ADDR_RANGE_{LO32,HI32}`: semaphore, request, acknowledgement, and optional logical-page-number range fields for invalidation engines 0-17. Request fields include invalidate-start, invalidate-end, PASID, flush type, and invalidation type.
- `VM_CONTEXT*_PAGE_TABLE_BASE_ADDR_{LO32,HI32}`, `VM_CONTEXT*_PAGE_TABLE_START_ADDR_{LO32,HI32}`, and `VM_CONTEXT*_PAGE_TABLE_END_ADDR_{LO32,HI32}`: split low/high logical page number fields for contexts 0-15.
- `MC_VM_NB_*`, `MC_VM_FB_OFFSET`, `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_*`, `MC_VM_STEERING`, `MC_SHARED_VIRT_RESET_REQ`, `MC_MEM_POWER_LS`, `MC_VM_CACHEABLE_DRAM_ADDRESS_*`, `MC_VM_APT_CNTL`, and `MC_VM_LOCAL_HBM_ADDRESS_*`: memory-controller aperture, PCI/MMIO, virtualization reset, cacheability, local memory, and power timing fields.
- `MC_VM_FB_LOCATION_*`, `MC_VM_AGP_*`, `MC_VM_SYSTEM_APERTURE_*`, and `MC_VM_MX_L1_TLB_CNTL`: framebuffer/AGP/system aperture limits and L1 TLB/system-access/advanced-driver-model/memory-type/ATC controls.
- `GCEA_DRAM_{RD,WR}_CLI2GRP_MAP{0,1}` and `GCEA_IO_{RD,WR}_CLI2GRP_MAP{0,1}`: 2-bit group assignment fields for client IDs 0-31, separately for DRAM read/write and IO read/write traffic.
- `GCEA_DRAM_{RD,WR}_GRP2VC_MAP`, `GCEA_DRAM_{RD,WR}_LAZY`, `GCEA_DRAM_{RD,WR}_CAM_CNTL`, and `GCEA_DRAM_PAGE_BURST`: GCEA DRAM group-to-VC mapping, delay, CAM sizing/reorder, and read/write burst limit fields.
- `GCEA_DRAM_{RD,WR}_PRI_AGE`, `GCEA_DRAM_{RD,WR}_PRI_QUEUING`, `GCEA_DRAM_{RD,WR}_PRI_FIXED`, `GCEA_DRAM_{RD,WR}_PRI_URGENCY`, and `GCEA_DRAM_{RD,WR}_PRI_QUANT_PRI{1,2,3}`: per-group priority aging, queuing, fixed priority, urgency, and threshold controls.
- `GCEA_ADDRNORM_*`, `GCEA_ADDRDEC_BANK_CFG`, `GCEA_ADDRDEC_MISC_CFG`, `GCEA_ADDRDECDRAM_ADDR_HASH_*`, and `GCEA_ADDRDECDRAM_HARVEST_ENABLE`: address range validity, interleave selection, socket/die/fabric target, high-address offset, DRAM hole, bank/GMI selection, VCM/channel/chip-select/rank-mask masks, address hashing, and harvest forcing.
- `GCEA_ADDRDEC{0,1}_*`: two parallel decoder instances with chip-select enable/base, address masks, address geometry, bank/row/column selectors, rank-mask selectors, channel-bit choice, and row-MSB inversion for CS01, CS23, SECCS01, and SECCS23.
- `GCEA_IO_RD_COMBINE_FLUSH`, `GCEA_IO_WR_COMBINE_FLUSH`, `GCEA_IO_GROUP_BURST`, `GCEA_IO_{RD,WR}_PRI_AGE`, and `GCEA_IO_{RD,WR}_PRI_QUEUING`: IO traffic flush timers, read/write burst limits, and per-group priority controls. The chunk ends at the first two shift macros of `GCEA_IO_RD_PRI_FIXED`, so the rest of that register is outside this work item.

## Control Flow

This header has no runtime control flow. Its direct behavior is compile-time macro substitution.

The implied runtime flow in AMDGPU consumers is:

1. Select GC 9.1 register definitions for the detected ASIC.
2. Choose a register address from `gc_9_1_offset.h`.
3. Read a current register value or construct a new register payload.
4. Use the `__SHIFT` and `__MASK` constants, usually through common field helpers, to extract or insert field values.
5. Write the value through MMIO, include it in a command stream where supported, or decode it for debugging, reset, fault handling, or telemetry.

For VM context programming, initialization code sets page table depth/block size and enables contexts, then programs page table base/start/end addresses. Fault policy fields decide whether protection faults interrupt, use a default behavior, or retry for specific classes. `VM_CONTEXTS_DISABLE` can globally prevent selected contexts from being used, so it must be coordinated with VMID allocation, queue setup, and reset flows.

For invalidation, software or firmware sequences an invalidation engine by coordinating its semaphore, address range, request, and acknowledgement fields. The `REQ` fields encode the start/end trigger, PASID, flush type, and invalidate type; the `ACK` fields report completion for the engine. The header does not encode ordering rules, poll timeouts, fences, or cache/TLB dependencies around those writes.

For MC and GCEA programming, boot, resume, reset, virtualization, and golden-register paths establish aperture limits, TLB behavior, cacheable/local-memory windows, client grouping, virtual-channel routing, DRAM address mapping, priority controls, and IO throttling. Diagnostic paths may also read these registers to explain memory routing, aperture, or translation behavior.

## State And Persistence Behavior

The macros themselves are stateless and persist nothing. They describe stateful GPU registers whose values are owned by hardware, firmware, the kernel driver, and command submission.

VM context control and page-table address registers are persistent VMID state. They define whether a context is enabled, how page tables are walked, which virtual range is valid, where page tables start, and how faults are surfaced. Incorrect field packing can disable a context, point a VMID at the wrong page table, select the wrong page-table depth, hide important faults, or generate interrupt storms.

Invalidation engine registers are stateful synchronization interfaces. Request bits can trigger TLB/cache invalidation work, acknowledgement bits can be polled or latched, and range registers scope the invalidation. Races or stale fields can produce missed translations, overbroad flushes, hangs while waiting for ACK, or incorrectly attributed PASID invalidations.

MC aperture and TLB registers persist platform memory policy. Framebuffer, AGP, system aperture, local HBM, TOM, MMIO, default physical page, steering, direct-system, memory type, ATC, and L1 TLB fields must match firmware discovery and platform topology. Wrong values can route accesses outside intended memory, produce GPU page faults, break PCI/MMIO visibility, or corrupt coherency.

GCEA registers persist low-level memory scheduling and address decode policy. Client grouping, VC mapping, priority coefficients, burst limits, address normalization, hashing, bank/channel/chip-select selection, and harvesting settings can affect correctness and performance. A decode mismatch against real DRAM/GMI topology can create silent data corruption or hard hangs; priority and CAM mistakes can also show up as starvation or severe bandwidth loss rather than immediate failures.

## Dependencies And Integration Points

This chunk depends on the generated GC 9.1 register set remaining internally synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/gc/gc_9_1_offset.h` provides the matching register addresses.
- Common AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32*`, `WREG32*`, `SOC15_REG_OFFSET`, and golden-register programming helpers consume these shift and mask definitions.
- GC/GMC/GFXHUB/MMHUB code is the likely consumer of the VM context, invalidation, aperture, and TLB fields.
- Reset, suspend/resume, SR-IOV, KFD queue management, PASID handling, VM fault handling, and GPU hang recovery paths depend on these registers being programmed and decoded consistently.
- Platform discovery and firmware tables provide the topology values that must be packed into framebuffer/system/AGP/local-memory ranges and GCEA address decode fields.

Integration points include VMID setup, page table base programming, per-process PASID invalidation, GPUVM fault handling, global VM context masking during reset or virtualization, memory aperture setup, local HBM/cacheable DRAM region programming, ATC/system-access policy, memory-power light sleep timing, DRAM/IO QoS tuning, and board/ASIC-specific address decode and harvest configuration.

## Risks And Edge Cases

- Generated-header drift is the dominant risk. A wrong mask or shift compiles cleanly but writes the wrong hardware bits or decodes misleading diagnostics.
- The chunk starts and ends mid-family. It begins with the tail of `VM_CONTEXT9_CNTL` and ends after only `GCEA_IO_RD_PRI_FIXED__GROUP0_FIXED_COEFFICIENT__SHIFT` and `GROUP1_FIXED_COEFFICIENT__SHIFT`; adjacent chunks are required for complete context 9 and IO fixed-priority coverage.
- VM context controls are repetitive but not harmless. Copy/paste mistakes across contexts 10-15 can make one VMID use another context's policy or leave a context unexpectedly disabled.
- Split address registers require correct low/high composition and address-unit interpretation. The masks expose logical or physical page number bits, not necessarily byte addresses.
- Invalidation engines 0-17 are structurally similar. Software must target the correct engine, preserve unrelated fields, and pair request/ack/semaphore handling with the hardware-required ordering outside this header.
- PASID, invalidate type, and flush type fields are side-effectful. Incorrect values can flush the wrong address space, miss stale translations, or stall command processing.
- Fault interrupt/default fields can change reliability symptoms. Masking fault interrupts or selecting default handling may turn a visible protection fault into data corruption, retry loops, or delayed recovery.
- MC aperture and TLB settings are platform-sensitive. System aperture, framebuffer location, AGP windows, TOM, local HBM ranges, ATC, and memory type fields must agree with firmware, IOMMU, SR-IOV, and memory topology.
- GCEA address decode and hashing fields are correctness-critical. Bad base/mask/selector/hash/harvest values can alias chip-selects, select the wrong bank/channel/rank mapping, or access harvested resources.
- Priority, lazy, CAM, VC, and burst controls affect fairness and latency. Incorrect values may only appear as workload-specific bandwidth collapse, queue starvation, or intermittent timeouts.
- Full-width masks such as `0xFFFFFFFFL` do not imply arbitrary legal values; alignment, reserved encodings, topology constraints, and hardware sequencing are documented outside this generated header.

## Test Signals

Useful validation is mostly generated-data consistency, build coverage, and hardware runtime behavior:

- Kernel build coverage for AMDGPU files that include `gc_9_1_sh_mask.h`, especially GC/GMC/GFXHUB/MMHUB, VM fault, reset, SR-IOV, KFD, and suspend/resume paths.
- Mechanical comparison against AMD's authoritative GC 9.1 register database to confirm every `__SHIFT` and `__MASK` value in this slice.
- Cross-checks that registers in this chunk have matching address macros in `gc_9_1_offset.h`.
- Static mask/shift sanity checks: masks align with shifts, repeated VM context and invalidation-engine families remain consistent, 2-bit CID group fields tile 32-bit registers without overlap, and full-width/address fields use the expected masks.
- GPUVM tests that create multiple VMIDs, program page tables, exercise read/write/execute permissions, trigger valid/range/dummy/PDE0 faults, and verify interrupt/default/retry behavior.
- TLB invalidation tests that issue PASID and range invalidations through multiple engines, poll acknowledgements, and verify stale translations are removed without hangs.
- SR-IOV or virtualization tests that exercise `MC_SHARED_VIRT_RESET_REQ`, PF/VF reset paths, and VM context disable behavior.
- Aperture tests covering framebuffer, AGP, system aperture, cacheable DRAM, local HBM, default system aperture address, ATC, and L1 TLB configuration across boot, suspend/resume, and GPU reset.
- Memory stress tests checking DRAM/IO routing, GCEA client grouping, VC mapping, burst limits, priority aging/urgency/quantum settings, CAM reorder behavior, and starvation under mixed graphics/compute/DMA workloads.
- Platform/topology validation that verifies GCEA address normalization, bank/channel/chip-select/rank-mask selection, hashing, harvesting, and DRAM hole programming against discovered memory geometry.
- Runtime warning signals include VM fault storms, missed fault interrupts, invalidate ACK timeouts, stale GPU translations, incorrect PASID attribution, aperture out-of-range faults, unexplained memory corruption, DRAM bandwidth collapse, queue starvation, or repeated GPU resets.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002635`. It covers lines 7194-9653 of `gc_9_1_sh_mask.h`. The final per-file research should merge this with adjacent chunks to restore the beginning of `VM_CONTEXT9_CNTL` before line 7194 and the remainder of `GCEA_IO_RD_PRI_FIXED` plus later GC 9.1 register families after line 9653.
