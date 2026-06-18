<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/physmem_info.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/physmem_info.c

Purpose: Detects s390 physical memory limits and online ranges during decompressor execution, tracks reserved ranges, and provides top-down boot physical memory allocation with collision avoidance.

Important APIs/types/functions: Defines bootdata `struct physmem_info physmem_info`, `physmem_alloc_pos`, and `physmem_alloc_ranges`. Public functions include `add_physmem_online_range()`, `detect_max_physmem_end()`, `detect_physmem_online_ranges()`, `physmem_set_usable_limit()`, `physmem_reserve()`, `physmem_free()`, `physmem_alloc_range()`, `physmem_alloc()`, `physmem_alloc_or_die()`, `get_physmem_alloc_pos()`, and `dump_physmem_reserved()`.

Control flow: Memory limit detection tries DIAG 0x500 storage limit, SCLP read info, then binary search with `tprot()`. Online range detection tries SCLP storage info, SCLP memory size fallback, DIAG 0x260 extents, then a single 0..max range. Allocation walks online ranges from high to low, clamps to `physmem_alloc_pos`, rounds for alignment, skips reserved ranges and IPL certificate intersections, optionally chains repeated allocations of the same reservation type, and panics through `die_oom()` when required.

State and persistence: `physmem_info.online[]`, optional `online_extended`, `range_count`, `info_source`, `usable`, and `reserved[]` become bootdata for later kernel setup. Reserved ranges may form chains for repetitive top-down allocations. `physmem_alloc_pos` is the moving high-water mark for dynamic boot allocations.

Dependencies and integration points: Integrated with `startup.c`, `kaslr.c`, `ipl_report.c`, SCLP early memory queries, DIAG 0x260/0x500, `tprot`, sparsemem section sizing, and boot diagnostics.

Risks: This file is on the critical path for every later placement decision. Off-by-one conversion of inclusive firmware limits, range merging, chain allocation, and collision detection can corrupt kernel image, initrd, IPL report data, vmem tables, or KASAN shadow pages. Extended online range storage is itself allocated using early allocation state.

Test signals: Booting with SCLP, DIAG 500, DIAG 260, and binary-search fallback paths; memory holes; many storage increments requiring `online_extended`; low-memory allocation pressure; KASLR overlap tests; initrd rescue; and OOM diagnostics.

Source read size: 386 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/physmem_info.c -->
