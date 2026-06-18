# sources/distributed-fs/ceph-client/kernel/iomem.c

## Purpose
`iomem.c` implements `memremap()` and managed wrappers for mapping physical memory resources as normal kernel pointers when `__iomem` accessors are not appropriate. It chooses direct-map access for suitable system RAM and falls back to cacheable/write-through/write-combine ioremap modes for non-RAM resources.

## Important APIs, types, and functions
Public APIs are `memremap()`, `memunmap()`, `devm_memremap()`, and `devm_memunmap()`. Internal helpers include weak/default `arch_memremap_wb()`, `arch_memremap_can_ram_remap()`, `try_ram_remap()`, `devm_memremap_release()`, and `devm_memremap_match()`.

## Control flow
`memremap()` first rejects empty flags and mixed RAM/non-RAM ranges. For `MEMREMAP_WB`, RAM ranges may return the linear direct-map address if the PFN is valid, not highmem, and the architecture permits it; otherwise it uses the architecture write-back remap. If a mapping is still absent and the target is system RAM with non-WB flags, it warns and fails to avoid cache aliasing. Non-RAM WT and WC requests then use `ioremap_wt()` or `ioremap_wc()`. `memunmap()` only calls `iounmap()` for addresses recognized as ioremap mappings. Devres wrappers allocate a resource record, map, register release, and later release by matching the returned pointer.

## State and persistence
Mappings persist until `memunmap()` or device-managed release. Direct-map WB mappings do not allocate a new virtual mapping and therefore are not unmapped. Device-managed mappings are tied to the `struct device` devres lifecycle. There is no disk persistence.

## Dependencies and integration points
The file depends on the resource tree via `region_intersects()`, architecture overrides for cacheable remap behavior, PFN/page/highmem helpers, ioremap variants, devres, and exported symbols used by drivers and persistent memory subsystems. It bridges resource metadata and virtual address mapping policy.

## Risks and test signals
Risks include aliasing system RAM with non-WB attributes, direct-map assumptions on architecture-specific memory encryption/decryption flags, mixed resource detection failures, highmem handling, and devres double-release warnings. Test signals include mapping RAM with WB, rejecting RAM WT/WC, mapping device memory with WC/WT/WB fallback, `memunmap()` on direct-map versus ioremap addresses, and devm cleanup on probe failure/remove.
