# sources/distributed-fs/ceph-client/arch/x86/include/asm/page_32_types.h

Purpose: defines 32-bit x86 page and virtual-address layout constants used before the rest of the paging headers can derive generic limits. It fixes `__PAGE_OFFSET`, `TASK_SIZE`, stack limits, thread/IRQ stack sizing, exception-stack count, kernel-image virtual limit, and physical/virtual mask widths for PAE and non-PAE builds.

Important APIs, types, and functions: the public surface is macro-based: `__PAGE_OFFSET_BASE`, `__PAGE_OFFSET`, `__START_KERNEL_map`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `IRQ_STACK_SIZE`, `N_EXCEPTION_STACKS`, `__PHYSICAL_MASK_SHIFT`, `__VIRTUAL_MASK_SHIFT`, `TASK_SIZE*`, `DEFAULT_MAP_WINDOW`, `STACK_TOP*`, and `KERNEL_IMAGE_SIZE`. Non-assembler users also see `__VMALLOC_RESERVE`, `sysctl_legacy_va_layout`, and `find_low_pfn_range()`.

Control flow: no executable flow is implemented here. Compile-time configuration selects PAE versus non-PAE physical mask definitions and exports constants consumed by page-table setup, memory layout, KASLR, vmalloc/highmem, and user address-space limit code.

State and persistence: runtime state is limited to extern declarations for vmalloc reserve, legacy VA layout sysctl, and low PFN discovery implemented elsewhere. There is no persistence.

Dependencies and integration points: depends on `CONFIG_PAGE_OFFSET`, `CONFIG_X86_PAE`, `CONFIG_VMSPLIT_*`, and highmem/vmalloc users. It feeds `page_types.h`, `pgtable_32_types.h`, boot memory initialization, user-stack placement, and module/vmalloc area calculation.

Risks: changing `__PAGE_OFFSET` or mask shifts changes the 32-bit kernel/user split and can break highmem, KASLR placement, and PAE PROT_NONE inversion assumptions. The PAE physical mask is intentionally wider than the real 44-bit PFN limit to preserve guest inverted PROT_NONE behavior.

Test signals: build both PAE and non-PAE i386 configurations, boot with different VMSPLIT/HIGHMEM options, verify `/proc/meminfo` lowmem/highmem sizing, vmalloc range, stack top, and KASLR placement, and exercise mappings near `TASK_SIZE` and `PAGE_OFFSET`.
