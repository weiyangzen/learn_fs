<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-44x.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-44x.h

## Purpose
This header defines the PPC44x nohash PTE bit layout, mapping Linux permission/cache flags into 44x TLB fields that support 36-bit addressing.

## Important APIs, Types, And Functions
It defines `_PAGE_PRESENT`, `_PAGE_WRITE`, `_PAGE_EXEC`, `_PAGE_READ`, `_PAGE_DIRTY`, `_PAGE_SPECIAL`, `_PAGE_ACCESSED`, endian/guarded/coherent/cache/write-through bits, `_PMD_*` masks, `_PTE_NONE_MASK`, `_PAGE_BASE_NC`, and `_PAGE_BASE`, then includes `pgtable-masks.h` for standard Linux protections.

## Control Flow
No executable flow is present. TLB miss handlers and page-table operations interpret these bits when loading TLB words and when generic MM helpers test permissions.

## State And Persistence Behavior
The persistent state is the encoded PTE value stored in page tables and later reflected into hardware TLB entries. `_PTE_NONE_MASK` preserves ERPN bits while testing for none entries.

## Dependencies And Integration Points
It is selected by `CONFIG_44x` from the 32-bit nohash pgtable header. It integrates with 44x TLB refill assembly, I-cache flushing policy through executable PTE changes, and SMP coherency policy via `_PAGE_COHERENT`.

## Risks And Edge Cases
Low PTE bits overlap swap-entry discrimination, so bit changes can break swap. Large-page PMD support is explicitly not implemented. Coherency bits differ across original 440 and later 460-class parts.

## Test Signals
Build 44x kernels with and without SMP, run swap and executable mmap tests, validate no stale instruction-cache behavior after modifying executable user mappings, and exercise DMA mappings on coherent variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/pte-44x.h -->
