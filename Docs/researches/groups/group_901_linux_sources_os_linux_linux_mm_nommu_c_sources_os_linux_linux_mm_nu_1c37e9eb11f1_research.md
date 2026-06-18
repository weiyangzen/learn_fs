# Group Research: group_901_linux_sources_os_linux_linux_mm_nommu_c_sources_os_linux_linux_mm_nu_1c37e9eb11f1

Scope: `Docs/research_subset_a.md` / Linux memory-management sources under `sources/os/linux/linux/mm`. All six listed source files were read completely.

Read evidence: `nommu.c` 1903 lines (`89afa7fce5ff64e2d66bb828d5adf66ee2e8862fd455d22f02f888d8aa9153fe`), `numa.c` 61 lines (`ec43d4edee52dcb84eb885c421ee731c7a26517121be5b40090dd616b2d5eb9c`), `numa_emulation.c` 602 lines (`334b87e7146076cc800bfec073373237a0eacfd26ce20dd47e3d456ee26fe36f`), `numa_memblks.c` 596 lines (`961ce28d10519530943fef5345d8f4c9712ac6e96c49a65c12c789ea38f061ad`), `oom_kill.c` 1257 lines (`452f1348e79c252ee89215d55fb104591412bbcea4a3ee965e873a401f756b4e`), `page-writeback.c` 3116 lines (`8211487be95e6b2319028afc9b147a33a0f568d98d34f25116d512c2a47ebbc0`).

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/nommu.c -->
# File Research: sources/os/linux/linux/mm/nommu.c

## Role

NOMMU implementation of core Linux virtual-memory interfaces for systems without page-table based virtual memory. It replaces many MMU-only facilities with direct kernel allocations, tracks executable/user mappings with `vm_region` records, implements `brk`, `mmap`, `munmap`, limited `mremap`, remote-memory access, and NOMMU inode mapping shrink behavior.

## Key Behavior

- Provides NOMMU versions of vmalloc APIs. Most allocation entry points are backed by `kmalloc`/`krealloc` with `__GFP_COMP` and no highmem.
- Maintains global shareable mapping state in `nommu_region_tree`, protected by `nommu_region_sem`.
- `do_mmap()` validates capabilities, shares compatible direct file/device mappings, or allocates private copies with `alloc_pages_exact()` and `kernel_read()`.
- `do_munmap()` requires whole-file-backed VMA removal but can split or shrink anonymous private mappings at page-aligned edges.
- `mremap` only resizes exact non-shared mappings in place and within the already allocated region.
- Remote memory access copies directly from real mapped addresses after VMA and permission checks.
- `nommu_shrink_inode_mappings()` protects shared mappings during truncate and trims region bounds past the new file size.

## Dependencies

Depends on Linux VMA/maple-tree helpers, address-space interval trees, file mmap callbacks, security mmap hooks, exact page allocation, cache/TLB/icache helpers, uaccess, sysctl, and NOMMU capability flags.

## Research Notes

The key invariant is that user-visible mapping addresses are real allocated or device/file-supplied addresses. Sharing is tracked through `vm_region` records rather than page tables, so reference ownership and exact overlap rules are the main risk areas.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/numa.c -->
# File Research: sources/os/linux/linux/mm/numa.c

## Role

Generic NUMA initialization support. It owns exported `node_data[]`, allocates early per-node `pg_data_t`, and provides fallback physical-address-to-node stubs.

## Key Behavior

- Defines and exports `struct pglist_data *node_data[MAX_NUMNODES]`.
- `alloc_node_data()` allocates cacheline-aligned node-local `pg_data_t` via memblock, panicking if allocation fails.
- Reports the allocation physical range and whether it landed on a different node.
- `alloc_offline_node_data()` allocates node data for offline nodes.
- Fallback `memory_add_physaddr_to_nid()` and `phys_to_target_node()` warn once and return node 0.

## Dependencies

Uses early boot `memblock`, NUMA node APIs, physical-to-virtual conversion, printk, `linux/numa.h`, and `linux/numa_memblks.h`.

## Research Notes

This file provides generic storage/allocation primitives; topology parsing is delegated to architecture and memblock NUMA code.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/numa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/numa_emulation.c -->
# File Research: sources/os/linux/linux/mm/numa_emulation.c

## Role

Boot-time NUMA emulation. It rewrites parsed physical NUMA memory into fake nodes from `numa=fake`, rebuilds CPU-to-node and distance mappings, and updates CPU masks for emulated nodes.

## Key Behavior

- Stores the fake NUMA command line and maintains `emu_nid_to_phys[]`.
- Splits memory by requested fake node count, fixed size, or uniform per-physical-node mode.
- Accounts for holes, minimum fake-node size, DMA32 boundary concerns, and end-of-node fragments.
- `numa_emulation()` validates constructed meminfo, copies physical distances, fixes PXM/node maps, commits fake meminfo, and rebuilds distances.
- Falls back to physical topology and identity mappings if emulation is absent or fails.
- `numa_add_cpu()` and `numa_remove_cpu()` map CPUs to all online fake nodes backed by the CPU’s physical node.

## Dependencies

Uses `numa_meminfo`, memblock, absent-page accounting, max PFN, ACPI NUMA PXM fixups, architecture NUMA hooks, node masks, CPU masks, and NUMA distance APIs.

## Research Notes

This is an early-boot topology transformer. The subtle logic is range splitting around holes/DMA boundaries and preserving emulated-to-physical mapping for CPU hotplug and distance lookup.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/numa_emulation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/numa_memblks.c -->
# File Research: sources/os/linux/linux/mm/numa_memblks.c

## Role

Generic early-boot NUMA memory-block parser and registrar. It collects memory ranges per node, sanitizes and merges them, registers node ownership in memblock, handles NUMA distances, and supplies address-to-node helpers.

## Key Behavior

- Maintains `numa_nodes_parsed`, regular/reserved meminfo, and the dynamic NUMA distance table.
- `numa_set_distance()` lazily allocates and validates a directional distance table.
- `numa_cleanup_meminfo()` trims to DRAM, moves reserved/non-DRAM ranges, removes empty blocks, rejects cross-node overlaps, and merges compatible same-node blocks.
- `numa_register_meminfo()` builds `node_possible_map`, writes node ids into `memblock.memory`, clears hotplug for kernel-reserved nodes, and validates PFN-node granularity.
- `numa_memblks_init()` resets topology, runs an architecture parser, cleans meminfo, applies NUMA emulation, and registers final meminfo.
- `numa_fill_memblks()` extends overlapping memblocks to fill gaps across a requested range.
- With `CONFIG_NUMA_KEEP_MEMINFO`, physical-address lookup helpers use retained regular and reserved meminfo.

## Dependencies

Uses memblock memory/reserved APIs, node masks, sort, printk, architecture NUMA definitions, optional NUMA emulation, hotplug flags, PFN section alignment helpers, and exported distance consumers.

## Research Notes

This file bridges firmware topology parsing into generic Linux memory topology. Cross-node overlap rejection is critical because it protects PFN-to-node ownership.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/numa_memblks.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/oom_kill.c -->
# File Research: sources/os/linux/linux/mm/oom_kill.c

## Role

Linux out-of-memory killer. It selects OOM victims, coordinates global and memcg OOMs, marks victims for memory reserves, logs diagnostics, optionally panics, runs the MMU OOM reaper, and implements `process_mrelease`.

## Key Behavior

- Registers sysctls for `panic_on_oom`, `oom_kill_allocating_task`, and `oom_dump_tasks`.
- `oom_badness()` scores candidates by RSS, swap, page-table memory, and `oom_score_adj`.
- `constrained_alloc()` classifies OOMs as global, cpuset, mempolicy, or memcg constrained.
- `select_bad_process()` scans eligible tasks and chooses the highest-scoring victim.
- `mark_oom_victim()` sets `TIF_MEMDIE`, records `oom_mm`, thaws frozen victims, and increments victim accounting.
- On MMU builds, the OOM reaper asynchronously zaps anonymous/private VMAs from killed tasks.
- `oom_kill_process()` handles already-dying tasks, logs diagnostics, kills the selected victim, and optionally kills a memcg OOM group.
- `out_of_memory()` is the top-level entry: invokes notifiers, handles panic policy, selects/kills a task, or panics if global OOM has no killable process.
- `process_mrelease()` uses pidfd lookup and the OOM reaper primitive to reclaim memory from exiting/reapable tasks.

## Dependencies

Uses scheduler/task iteration, memcg, cpusets, NUMA mempolicy, notifier chains, sysctl, freezer, credentials, tracepoints, VMA internals, pidfd lookup, signal delivery, VM counters, and page allocator OOM control structures.

## Research Notes

The central invariant is serialized OOM decisions plus fast victim marking so selected tasks can access reserves and exit. Shared-`mm` handling and candidate eligibility are the highest-risk parts.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/oom_kill.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/page-writeback.c -->
# File Research: sources/os/linux/linux/mm/page-writeback.c

## Role

Core dirty-page accounting, dirty throttling, writeback iteration, and folio writeback state management. It computes dirty limits, throttles page-cache writers, starts background writeback, exposes VM writeback sysctls, and supplies folio helpers used by filesystems.

## Key Behavior

- Defines dirty VM sysctls for ratio/byte thresholds, highmem dirtyability, writeback interval, expiry interval, and deprecated laptop mode.
- Maintains `global_wb_domain`, completion fractions, dirty limits, dirty ratelimits, per-CPU throttle leak accounting, and BDI min/max ratios.
- Computes dirtyable memory from free/file pages minus reserves, with optional highmem exclusion.
- Supports cgroup writeback by evaluating both global and memcg dirty-throttle contexts.
- `__wb_calc_thresh()` assigns each writeback instance a threshold share from completion fractions and BDI min/max limits.
- `wb_position_ratio()` computes feedback control for dirty throttling from global and per-writeback dirty state.
- Bandwidth and ratelimit update helpers estimate writeout capacity and adapt each WB’s dirty ratelimit.
- `balance_dirty_pages()` starts background writeback, chooses the stricter global/memcg domain, and sleeps or returns `-EAGAIN` for async callers.
- `balance_dirty_pages_ratelimited_flags()` is the exported dirtier-side accounting and throttling entry.
- `writeback_iter()` returns locked dirty folios for filesystem writeback and requires callers to drain to `NULL`.
- Dirty and writeback folio helpers synchronize folio flags, xarray tags, inode state, WB/global/memcg stats, and writeback completion accounting.

## Dependencies

Uses address_space xarrays, pagecache tags, folio APIs, backing-dev writeback structures, memcg writeback domains, fprop accounting, sysctl, CPU hotplug, scheduler IO sleep, inode writeback attachment, superblock markers, tracepoints, filesystem `address_space_operations`, reclaim throttling, and architecture stable-page hooks.

## Research Notes

This file combines accounting with feedback control. Correctness depends on keeping folio dirty flags, xarray tags, writeback flags, inode state, and WB/global/memcg counters synchronized across filesystem writeback, faults, reclaim, and truncation.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/page-writeback.c -->