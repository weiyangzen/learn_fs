
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/mem.c

Purpose: provides EFI stub memory-map retrieval and page allocation/free helpers with Linux-specific slack, alignment, soft-reserve, and low-address allocation policies.

Important APIs/types/functions: exports `efi_get_memory_map()`, `efi_allocate_pages()`, `efi_free()`, and `efi_low_alloc_above()`.

Control flow: memory-map retrieval first probes descriptor size, allocates a buffer with `EFI_MMAP_NR_SLACK_SLOTS`, optionally installs it as the Linux boot memmap configuration table before the final GetMemoryMap, and returns ownership to the caller. Page allocation honors `EFI_ALLOC_LIMIT`, `EFI_ALLOC_ALIGN`, and maximum-address allocation semantics. Low allocation scans conventional memory descriptors, skips hot-pluggable and soft-reserved memory, rounds to requested alignment, and allocates at exact addresses.

State and persistence behavior: allocations are EFI page or pool allocations owned by callers. Installing the boot memmap table makes the map visible to the kernel. No local static state exists.

Dependencies and integration points: depends on EFI boot services, Linux EFI memory descriptor helpers, soft-reserve policy, and aligned allocation fallback supplied elsewhere. It is used by almost every stub subsystem.

Risks and test signals: off-by-one maximum-address math, descriptor slack sufficiency, soft-reserve skipping, and freeing with the same alignment granularity are key risks. Test signals include memory-map installation, ExitBootServices retry using slack, low allocations above a minimum, high-limit allocations, hotplug/SP memory exclusion, and allocation/free leak checks.
