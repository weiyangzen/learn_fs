# sources/distributed-fs/ceph-client/arch/x86/mm/iomap_32.c

## Purpose
This 32-bit-only file supports temporary/local I/O mappings with correct cache attributes, especially write-combining mappings for devices. It bridges generic iomap callers to x86 PAT/memtype tracking and highmem local kmap primitives.

## Important APIs, Types, and Functions
- `iomap_create_wc()` reserves a write-combining memory type for a physical I/O range and returns a filtered `pgprot_t`.
- `iomap_free()` releases the corresponding memtype reservation.
- `__iomap_local_pfn_prot()` maps a PFN locally with a caller-supplied protection, adjusting non-PAT systems to UC-minus for non-WB requests.
- `is_io_mapping_possible()` rejects >4 GiB mappings on non-PAE kernels even when `phys_addr_t` is 64-bit.

## Control Flow and State
`iomap_create_wc()` first validates addressability, calls `memtype_reserve_io()`, and then synthesizes `__PAGE_KERNEL | cachemode2protval(pcm)`, masked by `__default_kernel_pte_mask`. `__iomap_local_pfn_prot()` checks PAT availability, normalizes cache mode when PAT is absent, masks unsupported bits, and delegates to `__kmap_local_pfn_prot()`. Persistent state lives in PAT memtype reservations, not in this file.

## Dependencies and Integration Points
The file depends on `asm/memtype.h`, PAT cache-mode translation, `__default_kernel_pte_mask` from x86 init code, and highmem local mapping. It is used by I/O mapping helpers that need temporary CPU access to device PFNs without a long-lived vmalloc mapping.

## Risks
Skipping the non-PAE addressability check would create impossible mappings above 4 GiB. Cache-mode mismatches can corrupt device interaction or conflict with existing PAT reservations. Callers must pair successful `iomap_create_wc()` with `iomap_free()`.

## Test Signals
Useful signals are successful WC mappings on PAT-enabled 32-bit kernels, UC-minus fallback on non-PAT kernels, rejection of high physical addresses without PAE, and PAT debug output showing reservations released after use.
