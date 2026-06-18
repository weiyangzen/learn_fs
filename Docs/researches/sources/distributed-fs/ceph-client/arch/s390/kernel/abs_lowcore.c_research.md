# sources/distributed-fs/ceph-client/arch/s390/kernel/abs_lowcore.c

## Purpose
Maps and unmaps per-CPU lowcore pages into the absolute lowcore virtual area used by s390 control-register save and low-address access paths.

## Important APIs, Types, And Functions
`abs_lowcore_map(int cpu, struct lowcore *lc, bool alloc)` maps `LC_PAGES` of a CPU lowcore to `__abs_lowcore + cpu * sizeof(struct lowcore)`. `abs_lowcore_unmap(int cpu)` removes those mappings. The preserved boot datum `__abs_lowcore` provides the virtual base.

## Control Flow
Mapping iterates page by page, converting `lc` to physical addresses and calling `__vmem_map_4k_page`. If a map fails and allocation was allowed, already mapped pages are unwound. Unmap mirrors the same page loop with `vmem_unmap_4k_page`.

## State And Persistence
The persistent state is page-table mapping state for absolute lowcore aliases. The source lowcore memory belongs to per-CPU setup; this file only creates and removes virtual mappings.

## Dependencies And Integration Points
Depends on pgtable helpers, `struct lowcore`, `LC_PAGES`, `__pa`, and boot-preserved section data. It is used by control-register and lowcore access code that needs an absolute lowcore view.

## Risks And Edge Cases
The unwind path intentionally avoids unmapping when `alloc` is false because the caller may be in atomic context and unmap could sleep. CPU index arithmetic and lowcore size alignment must stay consistent with architecture layout.

## Test Signals
Signals include CPU hotplug tests, boot with multiple CPUs, failure injection for page-table allocation, lockdep sleep checks around atomic callers, and lowcore alias access validation.
