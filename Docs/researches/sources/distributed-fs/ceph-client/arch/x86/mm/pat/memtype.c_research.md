# sources/distributed-fs/ceph-client/arch/x86/mm/pat/memtype.c

## Purpose
This file implements x86 PAT cache-type policy: PAT MSR initialization, cache-mode translation, reservation/freeing of memory types for RAM and I/O ranges, direct-map cache synchronization, `/dev/mem` protections, PFN map tracking, and debugfs reporting.

## Important APIs, Types, and Functions
- `pat_bp_init()` selects the boot CPU PAT MSR value and initializes cache-mode translation; `pat_cpu_init()` programs secondary CPUs.
- `pat_enabled()`, `nopat`, and `debugpat` control feature availability and diagnostics.
- `memtype_reserve()`, `memtype_free()`, `memtype_reserve_io()`, and `memtype_free_io()` manage cache-type reservations.
- `reserve_ram_pages_type()` stores RAM cache type in page flags; non-RAM ranges use the interval tree through `memtype_check_insert()`.
- `memtype_kernel_map_sync()` updates direct-map attributes to avoid cache alias conflicts.
- `pfnmap_track()`, `pfnmap_untrack()`, `pfnmap_setup_cachemode()`, `phys_mem_access_prot_allowed()`, `phys_mem_access_prot()`, `pgprot_writecombine()`, and `pgprot_writethrough()` provide external policy hooks.

## Control Flow and State
PAT boot initialization disables PAT for missing CPU/firmware support, emulates legacy PWT/PCD modes when needed, handles old Intel errata by using only lower entries, or programs the full PAT layout with WC/WP/WT support. Reservations sanitize physical addresses, skip platform-untracked ranges, intersect WB requests with MTRR state, classify RAM vs non-RAM, and either update page flags or insert an interval-tree entry under `memtype_lock`. Freeing reverses page flags or exact interval entries. Direct-map synchronization changes kernel identity mapping cache attributes for RAM aliases.

## Dependencies and Integration Points
The file depends on MTRR lookup, page flags, memblock/system RAM walking, `x86_platform.is_untracked_pat_range`, set-memory CPA, ioremap, `/dev/mem`, KVM export for UC-MTRR immunity, debugfs, and `memtype_interval.c`. It is a core dependency of `ioremap.c` and 32-bit iomap.

## Risks
Conflicting cache aliases can corrupt memory, so reservation correctness is critical. RAM supports only WB/WC/UC-/WT in page flags; WP fails and UC redirects. MTRR can force WB requests to UC-minus. Non-RAM reservations require exact freeing; invalid frees are logged. Direct-map sync failures must unwind reservations.

## Test Signals
Boot logs print `x86/PAT: Configuration [0-7]`. `debugpat` logs reservations and frees. Debugfs `pat_memtype_list` exposes non-RAM reservations. Tests should cover PAT disabled, legacy CPUs, old Intel errata paths, ioremap WC/UC/WT, `/dev/mem` O_DSYNC, PFNMAP VMAs, RAM page-flag conflicts, and KVM `pat_pfn_immune_to_uc_mtrr()`.
