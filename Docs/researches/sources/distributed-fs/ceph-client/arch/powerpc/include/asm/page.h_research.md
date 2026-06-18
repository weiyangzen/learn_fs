<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page.h

## Purpose
This central PowerPC page header defines page/hugepage policy, kernel physical/virtual address relationships, `__va()`/`__pa()` translations, PFN helpers, and data/stack VMA defaults.

## Important APIs, Types, And Functions
It includes VDSO page definitions, defines `HPAGE_SHIFT/SIZE/MASK`, `HUGETLB_PAGE_ORDER`, `HUGE_MAX_HSTATE`, `KERNELBASE`, `PAGE_OFFSET`, `LOAD_OFFSET`, `PHYSICAL_START`, `MEMORY_START`, optional `memstart_addr`, `kernstart_addr`, `virt_phys_offset`, `VIRT_PHYS_OFFSET`, `ARCH_PFN_OFFSET`, `__va()`, `__pa()`, `virt_to_pfn()`, `pfn_to_kaddr()`, `virt_to_page()`, `virt_addr_valid()`, VMA data defaults, and architecture `is_kernel_addr()` policy.

## Control Flow
The important runtime logic is inline address translation. BookE relocatable 32-bit kernels use `virt_phys_offset`; PPC64 uses bitwise mappings to avoid compiler codegen issues; other 32-bit builds use `PAGE_OFFSET - MEMORY_START`.

## State And Persistence Behavior
Non-static kernels expose runtime physical and virtual base variables. The translation macros define persistent assumptions for the linear map, kdump, relocation, and memory model.

## Dependencies And Integration Points
It depends on Kconfig address constants, VDSO page definitions, memory model, hugeTLB, BookE relocation, and includes `page_32.h` or `page_64.h`.

## Risks And Edge Cases
Confusing `KERNELBASE` with `PAGE_OFFSET` breaks kdump and relocatable kernels. Debug virtual checks can warn on invalid PPC64 translation. 32-bit ELF default executable data is intentional ABI behavior.

## Test Signals
Boot static, relocatable, kdump, BookE, and PPC64 configs; run virt/phys translation selftests, hugeTLB tests, `virt_addr_valid()` checks, and memory hotplug where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/page.h -->
