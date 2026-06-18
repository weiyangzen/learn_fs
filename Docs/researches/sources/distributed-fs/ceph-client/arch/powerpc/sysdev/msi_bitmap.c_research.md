<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/msi_bitmap.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/msi_bitmap.c

Purpose: Implements a generic bitmap allocator for PowerPC MSI hardware interrupt numbers, including device-tree available-range reservation and optional selftests.

Important APIs/types/functions: Exports `msi_bitmap_alloc_hwirqs()`, `msi_bitmap_free_hwirqs()`, `msi_bitmap_reserve_hwirq()`, `msi_bitmap_reserve_dt_hwirqs()`, `msi_bitmap_alloc()`, and `msi_bitmap_free()`.

Control flow: Allocation finds a naturally aligned zero area matching the requested vector count, marks it allocated under a spinlock, and returns the offset. Free clears a range. DT reservation defaults all bits reserved, then releases only ranges listed in `msi-available-ranges`. Allocator setup uses slab allocation after slab init or memblock before slab is available; free releases only slab-backed bitmaps.

State and persistence: `struct msi_bitmap` persists bitmap pointer, IRQ count, OF node reference, spinlock, and allocation origin flag. Bitmap bits represent allocated/reserved hwirqs.

Dependencies and integration points: Used by MPIC MSI and other PowerPC MSI controllers. Depends on bitmap APIs, OF property parsing, memblock early allocation, kmemleak annotation, and optional `CONFIG_MSI_BITMAP_SELFTEST`.

Risks: `msi_bitmap_reserve_hwirq()` uses `bitmap_allocate_region()` without checking failure; invalid hwirqs can warn or misbehave. `msi_bitmap_free_hwirqs()` trusts caller ranges. DT available ranges are interpreted as exact free hwirq ranges, so malformed or incomplete bindings can starve MSI allocation.

Test signals: Built-in selftests cover allocation, exhaustion, alignment, free/reuse, null OF node, and fake `msi-available-ranges`. Additional runtime signals are multi-vector MSI allocation and early-boot allocator use before slab.

Source read size: 273 lines, 7447 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/msi_bitmap.c -->
