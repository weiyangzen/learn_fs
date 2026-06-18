<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.h

## Purpose
`gen8_ppgtt.h` is the public header for Gen8+ PPGTT creation and GGTT PTE encoding.

## Important APIs, Types, and Functions
It declares `gen8_ppgtt_create(struct intel_gt *gt, unsigned long lmem_pt_obj_flags)` and `gen8_ggtt_pte_encode(dma_addr_t addr, unsigned int pat_index, u32 flags)`. The source file in this subset implements PPGTT creation; GGTT PTE encoding is declared here for users outside this file.

## Control Flow
The header contains declarations only. Callers request a new `i915_ppgtt` from GT setup or GEM context/VM code and use the GGTT encoder when producing platform-compatible GGTT PTE values.

## State and Persistence
No state is owned by the header. `gen8_ppgtt_create()` returns an address-space object with persistent page-table and scratch state managed by the VM lifecycle.

## Dependencies and Integration Points
The header forward-declares `i915_address_space` and `intel_gt` and depends on Linux kernel integer/DMA types. It is the integration point between GT initialization, VM binding code, and the Gen8+ page-table implementation.

## Risks and Edge Cases
Prototype drift would break VM setup across the driver. Callers must pass the correct GT and LMEM page-table allocation flags for the target platform because those choices shape later page-table allocation behavior.

## Test Signals
Build coverage catches declaration mismatches. Runtime coverage comes from PPGTT VM creation, context creation, page-table binding, and GGTT PTE encoding tests on Gen8+ and LMEM-capable platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/gen8_ppgtt.h -->
