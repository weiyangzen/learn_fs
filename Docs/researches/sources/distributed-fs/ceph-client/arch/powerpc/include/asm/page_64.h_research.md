<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_64.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_64.h

## Purpose
This header supplies 64-bit PowerPC hardware page constants, segment-id helpers, page clear/copy primitives, page-table-size state, and VMA default flags.

## Important APIs, Types, And Functions
It defines `HW_PAGE_SHIFT/SIZE/MASK`, `PAGE_FACTOR`, segment masks and `GET_ESID()` helpers for 256M and 1T segments, `pte_basic_t`, `clear_page()`, `copy_page()`, `ppc64_pft_size`, and 32/64-bit task-aware data and stack default VMA flags.

## Control Flow
`clear_page()` computes cache block strides from `ppc64_caches.l1d` and unrolls eight `dcbz` operations per loop iteration in inline assembly. VMA flag macros branch on `is_32bit_task()`.

## State And Persistence Behavior
`ppc64_pft_size` is exported page-hash-table size state. Page clearing mutates the target page only; VMA defaults persist in new mappings as policy.

## Dependencies And Integration Points
It depends on `asm-const`, cache metadata, task bitness helpers, and generic getorder. It integrates with allocator zeroing, copy-on-write, ELF stack/data permissions, and segment management.

## Risks And Edge Cases
Firmware and IOMMU interfaces still use 4K hardware page numbering even when Linux uses larger pages. Cache metadata must be initialized before `clear_page()` use. ABI defaults differ for 32-bit and 64-bit tasks.

## Test Signals
Boot 4K and 64K PPC64 page configs, run page zero/copy tests, 32-bit compat task stack/data permission checks, and segment-id mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page_64.h -->
