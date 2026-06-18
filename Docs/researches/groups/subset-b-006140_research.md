# Research: subset-b-006140

Grouped research for the requested `sources/distributed-fs/ceph-client/mm/` files. Each section preserves its source path for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/nommu.c -->
# sources/distributed-fs/ceph-client/mm/nommu.c

## Purpose

`nommu.c` supplies the memory-management implementation used on Linux targets without an MMU. Since there is no page-table-backed virtual address space, it replaces VM facilities with directly allocated memory, tracks process mappings as real address ranges, and rejects or stubs operations that require arbitrary virtual remapping. It is a compatibility layer for syscalls and MM APIs expected by filesystems, drivers, BPF/proc accessors, and generic kernel code while enforcing NOMMU constraints.

For the Ceph-client source tree, this is not Ceph-specific code, but it defines the kernel behavior a Ceph-enabled build inherits on NOMMU systems: mmap semantics are restricted, vmalloc is physically/logically contiguous allocation, page-fault helpers are unavailable, and remote process memory reads/writes operate directly over VMA address ranges.

## Important APIs, Types, And Functions

- Global state: `highest_memmap_pfn`, `heap_stack_gap`, `mmap_pages_allocated`, `nommu_region_tree`, `nommu_region_sem`, and the `vm_region_jar` slab cache hold NOMMU memory-region accounting.
- Exported allocation shims: `vfree()`, `__vmalloc_noprof()`, `vmalloc_noprof()`, `vzalloc_noprof()`, `vmalloc_user_noprof()`, `vmalloc_node_noprof()`, `vmalloc_32_noprof()`, `vmalloc_to_page()`, and `vmalloc_to_pfn()` map vmalloc-style callers onto `kmalloc`, `krealloc`, or direct address translation.
- Unsupported remapping APIs: `vmap()`, `vunmap()`, `vm_map_ram()`, `vm_unmap_ram()`, `free_vm_area()`, `filemap_fault()`, and `filemap_map_pages()` deliberately `BUG()` or fail because NOMMU cannot synthesize arbitrary virtual mappings or normal page faults.
- User mapping syscalls: `brk`, `mmap_pgoff`, optional `old_mmap`, `munmap`, and `mremap` are implemented with NOMMU-specific validation and region accounting.
- Mapping helpers: `validate_mmap_request()`, `determine_vm_flags()`, `do_mmap_shared_file()`, `do_mmap_private()`, `do_mmap()`, `do_munmap()`, `split_vma()`, and `vmi_shrink_vma()` form the core mmap/munmap path.
- VMA/region helpers: `add_nommu_region()`, `delete_nommu_region()`, `put_nommu_region()`, `setup_vma_to_mm()`, `cleanup_vma_from_mm()`, `delete_vma_from_mm()`, `delete_vma()`, `find_vma()`, and `find_vma_intersection()`.
- Device/file mapping adapters: `remap_pfn_range()`, `vm_iomap_memory()`, `remap_vmalloc_range()`, and `nommu_shrink_inode_mappings()`.
- Remote memory helpers: `access_remote_vm()`, `access_process_vm()`, and, under `CONFIG_BPF_SYSCALL`, `copy_remote_vm_str()`.

## Control Flow

Initialization starts in `mmap_init()`, which initializes `vm_committed_as`, creates the `vm_region` slab cache, registers `vm.nr_trim_pages`, and initializes VMA state. `init_user_reserve()` and `init_admin_reserve()` later seed overcommit reserve sysctls from free memory.

The vmalloc path is intentionally simple. Calls such as `vmalloc()` and `vzalloc()` eventually use `__vmalloc_noprof()`, which allocates with `kmalloc_noprof()` plus `__GFP_COMP` and strips `__GFP_HIGHMEM`. `vmalloc_user_noprof()` additionally searches the caller's mm for the allocated VMA and sets `VM_USERMAP`, allowing `remap_vmalloc_range()` to expose that region later. APIs requiring a virtual remap table are either no-ops, return `-EINVAL`, or crash via `BUG()` to catch impossible use on NOMMU.

`do_mmap()` first delegates policy checks to `validate_mmap_request()`. That function rejects `MAP_FIXED`, invalid `MAP_TYPE`, zero length, overflow, missing file mmap support, incompatible file permissions, noexec violations, and unsupported shared/private combinations. It computes NOMMU capabilities from file operations, file type, read/write mode, and direct-map support. `determine_vm_flags()` converts the request and capability set into `vm_flags`, including `VM_SHARED`, `VM_MAYOVERLAY`, and direct-map flags.

After validation, `do_mmap()` allocates one `vm_region` and one `vm_area_struct`, records file references, and takes `nommu_region_sem`. If a shared mapping is possible, it searches `nommu_region_tree` for an already compatible mapping of the same inode and pgoff range. Exact or superset matches share the existing `vm_region` and bump `vm_usage`; mismatched sharing is rejected unless the backing file handles direct mapping itself. If no existing region is reusable, direct maps ask the file's `get_unmapped_area()` for a real address; otherwise `do_mmap_private()` allocates pages with `alloc_pages_exact()`, optionally reads file contents into the copy, records `VM_MAPPED_COPY`, and updates `mmap_pages_allocated`.

Successful mappings are inserted into the global `nommu_region_tree` and the process `mm->mm_mt` maple tree. File-backed VMAs are also inserted into the inode mapping interval tree under `i_mmap_lock_write()`. Executable regions are flushed once with `flush_icache_user_range()`.

`do_munmap()` is stricter than MMU Linux. File-backed mappings must be unmapped as whole VMAs. Anonymous mappings may be unmapped wholly, shrunk from one end, or split once then shrunk; arbitrary middle removal is only handled through `split_vma()` plus `vmi_shrink_vma()`. Shrinking adjusts both the VMA and its private `vm_region`, removes and reinserts region rb-tree entries, and releases the abandoned pages through `free_page_series()`.

`exit_mmap()` walks all VMAs, unlinks file interval-tree state, drops file refs and region refs, destroys the maple tree, and resets `total_vm`. `do_mremap()` can only resize an exact anonymous/private mapping in place within its originally allocated region; moving and fixed remap are rejected.

`nommu_shrink_inode_mappings()` protects truncate. It rejects truncation if any shared VMA overlaps the removed range, then trims shared region tops that extend past the new file size.

## State And Persistence Behavior

State is in-memory kernel state only. Persistent backing file contents are copied into private mappings with `kernel_read()` during mmap and are not automatically written back by this file. Region lifetime is reference-counted by `vm_region->vm_usage`; when usage hits zero, file refs are dropped, copied page ranges are released, and the `vm_region` object returns to the slab.

The global rb-tree serializes shareable real-address regions across processes through `nommu_region_sem`. Per-process VMAs live in `mm->mm_mt`; file mappings also persist in `mapping->i_mmap` interval trees for truncate coordination. `mmap_pages_allocated` accounts exact page-series allocations for copied mappings.

## Dependencies And Integration Points

This file integrates with the syscall layer, Linux VMA maple-tree iteration, inode address-space interval trees, LSM `security_mmap_addr()`, audit, sysctl, file operation hooks (`mmap`, `mmap_capabilities`, `get_unmapped_area`), memblock/page allocation via normal allocators, and architecture hooks for cache flushing and I/O remapping.

Ceph and other filesystems interact indirectly through generic mmap, writeback, truncate, and remote-access paths. Any Ceph file mapping on a NOMMU target must satisfy these direct/copy mapping constraints; normal page-fault-based cache population is unavailable because `filemap_fault()` is a `BUG()` stub here.

## Risks And Edge Cases

- `MAP_FIXED`, most VMA movement, arbitrary virtual remapping, and page-fault-driven file mappings are unavailable; callers assuming MMU behavior can fail or hit `BUG()`.
- Shared mapping correctness depends on file capability reporting and overlap checks. Incorrect `mmap_capabilities()` or `get_unmapped_area()` behavior in a driver/filesystem can expose invalid direct mappings.
- Private file mappings read file contents once; subsequent file changes do not behave like normal page-cache-backed private mmap.
- Unmap restrictions are stricter for file-backed mappings. Partial unmaps that are common on MMU systems may return `-EINVAL`.
- Region rb-tree invariants are critical; debug validation catches overlap/order bugs only under `CONFIG_DEBUG_NOMMU_REGIONS`.
- `__access_remote_vm()` copies directly from target virtual addresses after VMA permission checks; VMA bounds and overflow handling are essential because there is no GUP/page-table walk.

## Test Signals

- NOMMU boot smoke tests should verify `mmap_init()` sysctl registration and absence of region-tree validation failures.
- Syscall tests should cover anonymous/private mmap, shared direct mmap through a capable chardev or memory filesystem, invalid `MAP_FIXED`, permission failures, partial anonymous munmap, rejected partial file munmap, and in-place `mremap`.
- Truncate tests should exercise `nommu_shrink_inode_mappings()` with shared and private file mappings.
- BPF/proc-style tests should cover `access_process_vm()` and `copy_remote_vm_str()` permission and boundary behavior.
- Filesystem tests for Ceph on NOMMU, if supported, should avoid assuming page-fault mmap behavior and should validate expected `mmap` failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/nommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/numa.c -->
# sources/distributed-fs/ceph-client/mm/numa.c

## Purpose

`numa.c` provides small generic NUMA helpers for allocating per-node `pg_data_t` structures and fallback physical-address-to-node lookups. It is early-boot infrastructure used before normal allocators are available. In this source tree, it underpins the memory topology that later page allocation, reclaim, writeback throttling, and filesystem cache behavior rely on.

## Important APIs, Types, And Functions

- `struct pglist_data *node_data[MAX_NUMNODES]`: exported global array behind `NODE_DATA(nid)`.
- `alloc_node_data(int nid)`: allocates and zeros one node's `pg_data_t` from memblock, preferring memory local to `nid`.
- `alloc_offline_node_data(int nid)`: allocates `pg_data_t` for an offline node with `memblock_alloc_or_panic()`.
- `memory_add_physaddr_to_nid(u64 start)`: weak fallback for memory hotplug node selection, returning node 0 when architecture/meminfo code does not provide a real mapping.
- `phys_to_target_node(u64 start)`: weak fallback for target-node lookup, also returning node 0.

## Control Flow

During NUMA initialization, platform code calls `alloc_node_data()` for each parsed node. The function rounds `sizeof(pg_data_t)` to a cache-line boundary, tries to allocate from the target node with `memblock_phys_alloc_try_nid()`, panics on failure, reports the physical range, checks where the allocation actually landed via `early_pfn_to_nid()`, stores the virtual address in `node_data[nid]`, and zeros the structure.

`alloc_offline_node_data()` handles node structures that must exist even when a node has no online memory. It uses a generic memblock allocation and stores it in `node_data[nid]`.

The two fallback lookup functions are compiled only when no macro or architecture implementation overrides them. They log once and return node 0, preserving functionality on platforms without retained NUMA memblock metadata.

## State And Persistence Behavior

`node_data[]` is long-lived kernel memory initialized during boot and used for the lifetime of the system. Allocations come from memblock early memory and are not freed. The fallback lookup functions have no state except `pr_info_once()` rate state.

## Dependencies And Integration Points

The file depends on `memblock`, `numa.h`, and `numa_memblks.h`. Its output is consumed by the buddy allocator, page reclaim, writeback code such as `node_dirty_ok()`, memory hotplug, per-node statistics, and any subsystem that resolves `NODE_DATA()`. Ceph-client behavior is indirect: page-cache allocation, dirty throttling, and reclaim decisions depend on correct node data.

## Risks And Edge Cases

- `alloc_node_data()` panics if memblock cannot allocate per-node metadata, which is appropriate during boot but makes malformed topology fatal.
- Node-local allocation is best effort. If metadata lands on another node, the function logs it but continues.
- Fallback `memory_add_physaddr_to_nid()` and `phys_to_target_node()` always return 0; on systems needing accurate hotplug placement, relying on these stubs can misplace memory.

## Test Signals

- Boot logs should show `NODE_DATA(nid)` allocations for expected nodes and no panic.
- NUMA topology tests should confirm `NODE_DATA()` exists for memoryless/offline nodes when relevant.
- Memory hotplug tests should verify whether architecture-specific lookup functions override the stubs; if not, added memory will target node 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/numa_emulation.c -->
# sources/distributed-fs/ceph-client/mm/numa_emulation.c

## Purpose

`numa_emulation.c` implements `numa=fake` boot-time NUMA emulation. It splits physical NUMA memory blocks into synthetic nodes, remaps CPU-to-node and APIC-to-node relationships, and rebuilds NUMA distance tables so the rest of the kernel can exercise NUMA policy on hardware with fewer or differently shaped physical nodes.

For Ceph-client development and validation, this is useful because page cache, writeback throttling, reclaim, and memory allocation behavior can be tested across synthetic NUMA nodes without requiring matching hardware.

## Important APIs, Types, And Functions

- `int emu_nid_to_phys[MAX_NUMNODES]`: maps emulated node IDs to the physical node they are carved from.
- `numa_emu_cmdline(char *str)`: stores the `numa=fake` command-line payload for later boot parsing.
- Split helpers: `split_nodes_interleave()`, `split_nodes_size_interleave_uniform()`, `split_nodes_size_interleave()`, `find_end_of_node()`, `uniform_size()`, and `mem_hole_size()`.
- Block helpers: `emu_find_memblk_by_nid()` and `emu_setup_memblk()`.
- `numa_emulation(struct numa_meminfo *numa_meminfo, int numa_dist_cnt)`: main transformation function.
- CPU mask hooks: `numa_add_cpu()` and `numa_remove_cpu()`, with debug and non-debug implementations.

## Control Flow

Early parameter parsing calls `numa_emu_cmdline()` and preserves the raw fake-NUMA string. Later `numa_emulation()` receives the physical `numa_meminfo` and current distance count. If no command line was provided, it builds identity `emu_nid_to_phys[]` and exits.

When emulation is requested, the function copies physical meminfo into `pi`, clears the emulated meminfo `ei`, initializes all emulated node mappings to `NUMA_NO_NODE`, and parses the command:

- A string containing `U` requests uniform splitting within each physical node into a specified number of nodes.
- A string containing `M` or `G` requests fake nodes with a fixed size.
- A plain number requests that total available memory be split into that many interleaved fake nodes.

The splitting helpers walk physical blocks, account for absent pages through `mem_hole_size()`, preserve at least `FAKE_NODE_MIN_SIZE` non-reserved memory per node where possible, avoid leaving unusably small fragments below DMA32 boundaries, and call `emu_setup_memblk()` to append each emulated block. `emu_setup_memblk()` records the fake range, sets the fake-to-physical mapping on first use, advances the physical block start, removes exhausted physical blocks, and logs the fake node range.

After splitting, `numa_emulation()` sanitizes `ei` with `numa_cleanup_meminfo()`. If a physical distance table exists, it copies the current `node_distance()` matrix into memblock memory. It then computes the highest emulated node and default physical node, rebuilds `numa_nodes_parsed` from emulated blocks, calls `fix_pxm_node_maps()` to avoid ACPI PXM collisions, commits `ei` back to `*numa_meminfo`, and updates CPU-to-node data through `numa_emu_update_cpu_to_node()`.

Distance handling is rebuilt in two phases. First, `numa_reset_distance()` clears the old table. Then each emulated pair receives either explicit distances parsed after `:` from the command line, a local/remote default if the physical node is outside the copied table, or the physical distance between the backing nodes. A second pass fills entries involving non-emulated physical nodes using the copied physical table. Finally the copied table is freed.

CPU hotplug hooks map a CPU to every online emulated node backed by the CPU's physical node. Non-debug mode updates `node_to_cpumask_map` directly; debug mode uses `debug_cpumask_set_cpu()`.

## State And Persistence Behavior

All major transformations happen during boot with `__init` data. The persistent result is the rewritten `numa_meminfo`, updated global `numa_nodes_parsed`, rebuilt NUMA distance table, modified CPU-to-node mappings, and `emu_nid_to_phys[]`, which remains needed by CPU add/remove callbacks.

If emulation fails at any validation step, control goes to `no_emu`, restores the physical parsed-node mask, and fills `emu_nid_to_phys[i] = i` so later CPU hooks still have a defined identity mapping.

## Dependencies And Integration Points

The file depends on generic memblock, topology, `numa_memblks` helpers, x86/architecture NUMA hooks in `asm/numa.h`, and ACPI NUMA PXM maps. It calls `numa_cleanup_meminfo()`, `numa_reset_distance()`, `numa_set_distance()`, `fix_pxm_node_maps()`, `numa_emu_update_cpu_to_node()`, `numa_emu_dma_end()`, and node-distance APIs.

Its integration point with memory management is early topology mutation before page allocator node registration. Filesystems such as Ceph see the effects indirectly through allocation locality, reclaim, dirty limits, and CPU/node masks.

## Risks And Edge Cases

- Bad command-line sizes or excessive fake node counts can fail emulation or force size adjustments.
- Memory holes and DMA32 boundary preservation make the final fake-node layout non-obvious; tests should inspect boot logs.
- The code assumes fixed-size arrays bounded by `MAX_NUMNODES` and `NR_NODE_MEMBLKS`; overproduction of fake blocks fails emulation.
- Distance override parsing is stateful over `emu_cmdline` after `:`; malformed or incomplete overrides fall back to physical/default distances.
- `phys_dist` allocation failure disables emulation when a distance table must be preserved.
- CPU masks intentionally associate one physical CPU with all emulated nodes backed by the same physical node; scheduler and locality behavior is synthetic rather than hardware-real.

## Test Signals

- Boot with `numa=fake=N`, fixed-size `numa=fake=SIZE`, and uniform `U` forms; verify `Faking node` logs and `/sys/devices/system/node/`.
- Validate `numa_nodes_parsed`, CPU masks, and `node_distance()` matrices after emulation.
- Exercise memory pressure and writeback workloads on fake nodes to confirm per-node accounting behaves consistently.
- Test malformed command lines and too-small sizes to ensure graceful fallback to identity mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/numa_emulation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/numa_memblks.c -->
# sources/distributed-fs/ceph-client/mm/numa_memblks.c

## Purpose

`numa_memblks.c` manages early NUMA memory block metadata. It records parsed memory ranges, validates and merges them against memblock DRAM, registers node ownership in `memblock.memory`, handles reserved ranges, manages the NUMA distance table, supports fake NUMA emulation, and optionally retains enough metadata for memory hotplug address-to-node decisions.

This file is core topology infrastructure. Ceph-client effects are indirect but important: page-cache allocation locality, writeback dirty limits, reclaim accounting, and hotplug behavior all depend on correct physical-memory-to-node registration.

## Important APIs, Types, And Functions

- Global topology state: `nodemask_t numa_nodes_parsed`, `int numa_distance_cnt`, and static `u8 *numa_distance`.
- Static meminfo stores: `numa_meminfo` and `numa_reserved_meminfo`.
- Distance APIs: `numa_reset_distance()`, `numa_set_distance()`, and exported `__node_distance()`.
- Memblock registration APIs: `numa_add_memblk()`, `numa_add_reserved_memblk()`, `numa_cleanup_meminfo()`, `numa_memblks_init()`, and `numa_fill_memblks()`.
- Internal helpers: `numa_nodemask_from_meminfo()`, `numa_add_memblk_to()`, `numa_remove_memblk_from()`, `numa_move_tail_memblk()`, `numa_clear_kernel_node_hotplug()`, `numa_register_meminfo()`, and `cmp_memblk()`.
- Optional retained-info APIs under `CONFIG_NUMA_KEEP_MEMINFO`: exported `phys_to_target_node()` and `memory_add_physaddr_to_nid()`.

## Control Flow

Topology setup typically enters through `numa_memblks_init(init_func, memblock_force_top_down)`. It clears parsed/possible/online node masks, zeroes `numa_meminfo`, resets all `memblock.memory` and `memblock.reserved` node IDs to `NUMA_NO_NODE`, clears hotplug flags, and resets the distance table. It then calls the architecture/platform `init_func()` to populate `numa_meminfo` and distance data.

After platform parsing, it optionally restores memblock allocation direction to top-down, sanitizes parsed ranges with `numa_cleanup_meminfo()`, invokes `numa_emulation()` to mutate topology if requested, and finally registers the resulting memory info through `numa_register_meminfo()`.

`numa_cleanup_meminfo()` is the central validator. It trims all ranges to DRAM boundaries, moves non-DRAM/reserved-only ranges into `numa_reserved_meminfo`, preserves non-RAM tails above current DRAM limits as reserved ranges, removes empty ranges, rejects overlaps across different nodes, warns and merges overlaps within the same node, and merges same-node neighboring ranges if no other node owns the intervening span. Unused array entries are cleared to `NUMA_NO_NODE`.

`numa_register_meminfo()` builds `node_possible_map` from CPU-parsed nodes plus memory-bearing nodes, rejects an empty possible map, calls `memblock_set_node()` for each memory range, clears hotplug eligibility for any node containing kernel-reserved memory through `numa_clear_kernel_node_hotplug()`, and validates pfn-to-node alignment if node IDs are not stored in page flags.

Distance handling is lazy. `numa_set_distance()` allocates a square table sized to the highest currently parsed node if needed, initializes local/remote defaults, validates bounds and local-distance invariants, and writes one byte per pair. `numa_reset_distance()` frees the old memblock table and allows recreation. `__node_distance()` returns defaults for out-of-range queries.

`numa_fill_memblks()` repairs gaps across a requested physical span by collecting overlapping blocks, sorting them by start, extending first/last to cover the requested bounds, and backfilling gaps by moving later block starts to the previous end. It returns `NUMA_NO_MEMBLK` when no parsed block overlaps the range.

When `CONFIG_NUMA_KEEP_MEMINFO` is enabled, hotplug lookup helpers search retained `numa_meminfo` and `numa_reserved_meminfo`. `phys_to_target_node()` prefers online memory info unless the address is also in reserved info, while `memory_add_physaddr_to_nid()` returns the matching memory node or falls back to the first parsed block's node.

## State And Persistence Behavior

Most data is early boot `__initdata` unless `CONFIG_NUMA_KEEP_MEMINFO` preserves it. The persistent effects are node IDs written into memblock regions, node masks, hotplug flags, and the allocated NUMA distance table. Distance memory is allocated and freed through memblock, not normal slab.

Reserved meminfo records ranges outside usable memory or explicitly registered reserved ranges so later hotplug/target-node logic can avoid losing firmware/kernel placement knowledge.

## Dependencies And Integration Points

This file depends on `memblock`, `sort`, generic NUMA masks, architecture NUMA definitions, and the fake-NUMA emulation code. It is called by architecture NUMA initialization. Downstream users include page allocator initialization, node data allocation, memory hotplug, pfn-to-node mapping, reclaim, writeback, scheduler locality, and sysfs node exposure.

Ceph-client integration is through these downstream VM behaviors. Misregistered nodes can skew page-cache placement and dirty throttling for Ceph file data or metadata.

## Risks And Edge Cases

- Cross-node overlapping memory ranges are fatal to NUMA setup.
- Same-node overlaps are tolerated but can hide firmware quirks; warnings should be investigated.
- `numa_distance` uses a sentinel `(void *)1LU` on allocation failure; callers must reset before retrying.
- Distance table sizing depends on nodes known at allocation time; late higher node IDs are rejected until reset.
- Hotplug decisions are weak without `CONFIG_NUMA_KEEP_MEMINFO` or architecture overrides.
- `numa_fill_memblks()` mutates block starts/ends in place; incorrect caller ranges can broaden node ownership.
- Clearing hotplug for any node with reserved kernel memory can make entire nodes un-hotpluggable.

## Test Signals

- Boot with firmware NUMA tables and verify no overlap errors, expected merge logs, and correct `/sys/devices/system/node/` memory ranges.
- Unit or boot tests should cover distance setup, invalid distance rejection, reset/recreate behavior, and out-of-range defaults.
- Memory hotplug tests should validate `memory_add_physaddr_to_nid()` and `phys_to_target_node()` with retained meminfo.
- Fake NUMA tests should confirm `numa_memblks_init()` sanitizes emulated meminfo and registers memblock node IDs correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/numa_memblks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/oom_kill.c -->
# sources/distributed-fs/ceph-client/mm/oom_kill.c

## Purpose

`oom_kill.c` implements Linux out-of-memory victim selection, diagnostics, kill signaling, OOM reaping, OOM killer disable/enable coordination, memory-cgroup OOM handling, and the `process_mrelease` syscall. It is invoked when reclaim and allocation fallback cannot satisfy memory demand.

For Ceph-client workloads, this code matters under heavy page-cache, writeback, metadata, or network-buffer pressure. It decides whether a Ceph process, helper, or unrelated task is killed when system or memcg memory is exhausted.

## Important APIs, Types, And Functions

- Sysctl state: `panic_on_oom`, `oom_kill_allocating_task`, and `oom_dump_tasks`.
- Locks and counters: exported `oom_lock`, `oom_adj_mutex`, `oom_victims`, `oom_victims_wait`, and `oom_killer_disabled`.
- Victim scoring and selection: `oom_badness()`, `constrained_alloc()`, `oom_evaluate_task()`, and `select_bad_process()`.
- Eligibility helpers: `oom_cpuset_eligible()`, `find_lock_task_mm()`, `oom_unkillable_task()`, `task_will_free_mem()`, and `process_shares_mm()`.
- Diagnostic helpers: `dump_header()`, `dump_tasks()`, `dump_task()`, `dump_oom_victim()`, and `should_dump_unreclaim_slab()`.
- OOM reaper under `CONFIG_MMU`: `__oom_reap_task_mm()`, `oom_reap_task_mm()`, `oom_reap_task()`, `oom_reaper()`, `wake_oom_reaper()`, and `queue_oom_reaper()`.
- Kill path: `mark_oom_victim()`, `__oom_kill_process()`, `oom_kill_process()`, and `oom_kill_memcg_member()`.
- Public controls: `exit_oom_victim()`, `oom_killer_enable()`, `oom_killer_disable()`, `register_oom_notifier()`, `unregister_oom_notifier()`, `out_of_memory()`, `pagefault_out_of_memory()`, and `process_mrelease()`.

## Control Flow

`oom_init()` starts the `oom_reaper` kernel thread on MMU builds and registers VM sysctls. Runtime OOM handling enters `out_of_memory()` with an `oom_control` describing allocation context, gfp mask, order, zonelist, nodemask, and optional memcg.

The first stage handles bypasses. If the OOM killer is disabled, it returns false. For global OOM, notifier callbacks get a chance to free memory; if they report freed pages, the OOM path succeeds without killing. If current is already exiting or has a fatal path that will free memory, it is marked as an OOM victim and queued for reaping. GFP contexts without `__GFP_FS` avoid global OOM killing because I/O-less reclaim is not compensated here.

`constrained_alloc()` classifies the allocation as global, cpuset-constrained, mempolicy-constrained, or memcg-constrained and sets `oc->totalpages` to the appropriate scoring universe. `check_panic_on_oom()` enforces `panic_on_oom` policy, with special handling for constrained OOM and sysrq OOM.

If `oom_kill_allocating_task` is enabled and current is eligible, current is selected. Otherwise `select_bad_process()` scans either memcg tasks or all processes. `oom_evaluate_task()` filters unkillable tasks, tasks outside the OOM domain, existing OOM victims that may still free memory, and tasks with unusable scores. It chooses `oom_task_origin()` tasks immediately or the highest `oom_badness()` score. `oom_badness()` scores RSS, swapents, and page-table memory, adjusted by `oom_score_adj`, while excluding init, kthreads, `OOM_SCORE_ADJ_MIN`, already reaped `MMF_OOM_SKIP`, and vfork-in-progress tasks.

`oom_kill_process()` first checks whether the selected task is already exiting and likely to free memory. If so, it marks and reaps without logging a full kill. Otherwise it rate-limits diagnostics, prints memory/task context, resolves an optional memcg OOM group, and calls `__oom_kill_process()`. The kill function locks a thread with a live `mm`, grabs the mm, sends `SIGKILL`, marks the victim with `TIF_MEMDIE`, records events, kills other user processes sharing the same mm across thread groups, and queues the mm for reaping unless init pins it.

The OOM reaper waits for queued victims, sleeps briefly after kill through a timer, then tries to take `mmap_read_trylock()` and walks VMAs in reverse. It skips hugetlb and PFNMAP, reaps anonymous or private mappings with `zap_vma_for_reaping()`, sets `MMF_UNSTABLE`, retries a bounded number of times, then sets `MMF_OOM_SKIP` and drops the queued task reference. This hides the mm from later OOM selection.

`process_mrelease(pidfd, flags)` lets userspace reclaim an exiting process's anonymous/private memory proactively. It validates flags, resolves a pidfd, locks a task with an mm, requires `task_will_free_mem()` or already completed reaping, and invokes `__oom_reap_task_mm()` under `mmap_read_lock_killable()`.

## State And Persistence Behavior

OOM decisions are transient, but they mutate task and mm state. Victims get `TIF_MEMDIE`, `signal->oom_mm`, `MMF_OOM_REAP_QUEUED`, `MMF_UNSTABLE`, and eventually `MMF_OOM_SKIP`. `oom_victims` tracks victims in flight so `oom_killer_disable()` can wait. The reaper list is protected by a spinlock and uses task references until reaping completes.

Sysctls persist runtime policy until changed. The notifier chain persists registered subsystems that can respond to global OOM before killing.

## Dependencies And Integration Points

This file depends on task lists and locking, memcg, cpuset, mempolicy, reclaim, slab diagnostics, tracepoints, sysctl, pidfd, freezer, credentials, mmu notifiers, and VMA zapping. It integrates with page allocation, page fault handling, memory cgroups, suspend/freezer behavior, and userspace OOM tooling.

Ceph-client integration is indirect through memory use. Ceph workloads in cgroups can trigger memcg OOM, and Ceph page-cache pressure can contribute to global OOM. `oom_score_adj`, cgroup OOM grouping, and dirty/writeback behavior all affect whether Ceph-related processes are selected.

## Risks And Edge Cases

- Victim scoring is heuristic and can be skewed by `oom_score_adj`, memcg limits, cpuset/mempolicy constraints, and shared mm users.
- Existing OOM victims can abort further selection to avoid over-killing, potentially prolonging stalls if the victim cannot exit.
- Reaper races with exit paths and mmap locks; it uses trylock/retry to avoid deadlocks but may fail and mark skip after diagnostics.
- Killing processes sharing an mm must avoid init and kthreads; pinned init mm disables reaping for that mm.
- `panic_on_oom=2` is fatal except sysrq OOM; `panic_on_oom=1` only panics for unconstrained OOM.
- GFP_NOFS global allocation failures can return without killing, relying on caller/reclaim behavior.
- `process_mrelease()` only works for tasks already exiting or already reaped; otherwise it returns `-EINVAL`.

## Test Signals

- Kernel selftests and stress workloads should cover global OOM, memcg OOM, cpuset/mempolicy-constrained OOM, sysrq OOM, and `oom_score_adj` exclusion.
- Verify sysctl behavior for panic, allocating-task kill, and task dump output.
- Exercise OOM reaper tracepoints, `MMF_OOM_SKIP`, and `process_mrelease()` with exiting processes.
- Cgroup tests should validate OOM group kill and protected memory reporting.
- Ceph-oriented stress tests should run metadata and writeback-heavy clients under memcg limits to observe expected victim selection and absence of kernel deadlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/oom_kill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page-writeback.c -->
# sources/distributed-fs/ceph-client/mm/page-writeback.c

## Purpose

`page-writeback.c` manages dirty page accounting, dirty throttling, background writeback thresholds, backing-device writeback proportions, folio dirty/writeback state transitions, and helper iteration for filesystem `writepages` implementations. It is the core policy layer that prevents dirty file cache from overrunning memory while keeping storage devices busy.

For Ceph-client code, this is a major integration point. Ceph file data dirtied through the page cache uses these helpers for dirty accounting and throttling, while Ceph writeback behavior interacts with `address_space_operations`, `writeback_control`, backing-device limits, cgroup writeback domains, and folio writeback state.

## Important APIs, Types, And Functions

- Sysctl-backed policy variables: `dirty_background_ratio`, `dirty_background_bytes`, `vm_dirty_ratio`, `vm_dirty_bytes`, `dirty_writeback_interval`, `dirty_expire_interval`, `vm_highmem_is_dirtyable`, and deprecated `laptop_mode`.
- Global writeback domain: `struct wb_domain global_wb_domain`.
- Dirty limit calculators: `global_dirty_limits()`, `node_dirty_ok()`, `domain_dirty_limits()`, `node_dirty_limit()`, `global_dirtyable_memory()`, and `node_dirtyable_memory()`.
- Writeback-domain accounting: `wb_domain_init()`, `wb_domain_exit()`, `wb_writeout_inc()`, `wb_domain_writeout_add()`, `writeout_period()`, and `__wb_writeout_add()`.
- BDI limit controls: `bdi_set_min_ratio()`, `bdi_set_max_ratio()`, `bdi_set_min_bytes()`, `bdi_set_max_bytes()`, `bdi_set_strict_limit()`, and byte getters.
- Dirty throttle engine: `balance_dirty_pages_ratelimited_flags()`, `balance_dirty_pages_ratelimited()`, `balance_dirty_pages()`, `wb_position_ratio()`, `wb_update_dirty_ratelimit()`, `wb_update_bandwidth()`, and `wb_over_bg_thresh()`.
- Writeback iteration: `tag_pages_for_writeback()`, `writeback_iter()`, `do_writepages()`, and helper `writeback_get_folio()`.
- Folio dirty/writeback state APIs: `noop_dirty_folio()`, `filemap_dirty_folio()`, `folio_mark_dirty()`, `folio_mark_dirty_lock()`, `folio_redirty_for_writepage()`, `__folio_cancel_dirty()`, `folio_clear_dirty_for_io()`, `__folio_start_writeback()`, `__folio_end_writeback()`, `folio_wait_writeback()`, `folio_wait_writeback_killable()`, and `folio_wait_stable()`.

## Control Flow

Initialization enters `page_writeback_init()`. It initializes `global_wb_domain`, registers CPU hotplug callbacks that recompute `ratelimit_pages`, and registers VM writeback sysctls. `writeback_set_ratelimit()` computes the global dirty threshold and sets a per-CPU/task polling interval intended to limit overshoot when all CPUs dirty concurrently.

Dirty limit calculation starts from dirtyable memory. `global_dirtyable_memory()` sums free pages and active/inactive file pages, subtracts reserves and optionally highmem. `domain_dirty_limits()` converts ratio or byte sysctls into dirty and background thresholds for either the global domain or a memcg domain, including real-time/deadline task boosts and 32-bit cap enforcement. `global_dirty_limits()` exposes global thresholds, and `node_dirty_ok()` checks per-node dirty/writeback pages against node-scaled limits.

Writeback bandwidth accounting uses `wb_domain` completions with fprop. `__wb_writeout_add()` increments per-wb `WB_WRITTEN`, global completions, and memcg-domain completions when enabled. `writeout_period()` ages proportions on a deferrable timer and stops the timer when all fractions decay to zero.

Backing-device threshold sharing is handled by `__wb_calc_thresh()`, which assigns each `bdi_writeback` a fraction of a dirty threshold based on recent completion proportions, BDI min/max ratios, inactive-device grace, and strict-limit behavior. BDI setter functions validate ratio/byte limits under `bdi_lock` and maintain the global `bdi_min_ratio` sum.

Dirty throttling begins when `balance_dirty_pages_ratelimited_flags()` is called after newly dirtying pages. It skips non-writeback BDIs, resolves the current cgroup writeback object if needed, handles per-CPU ratelimit and leaked dirty counts from exiting tasks, and calls `balance_dirty_pages()` once the current task reaches its dirty pause threshold.

`balance_dirty_pages()` repeatedly computes global and optional memcg dirty domains, starts background writeback when above background thresholds, checks freerun ceilings, computes per-wb dirty limits, chooses the stricter global or memcg throttle control, updates bandwidth and dirty ratelimit every `BANDWIDTH_INTERVAL`, and sleeps the task with `io_schedule_timeout()` unless `BDP_ASYNC` asks for `-EAGAIN`. The core control loop uses `wb_position_ratio()` and `wb_update_dirty_ratelimit()` to scale each task's dirtying rate based on dirty position relative to freerun, setpoint, hard limit, write bandwidth, strict BDI limits, and observed dirty rate.

Background writeback decisions use `wb_over_bg_thresh()`, which checks global and memcg domains without counting writeback pages for the background decision, then checks per-wb background thresholds.

Filesystem writeback uses the second half of the file. `tag_pages_for_writeback()` marks currently dirty xarray entries with `PAGECACHE_TAG_TOWRITE` to avoid livelock against new dirtying. `writeback_iter()` is the expected helper loop for filesystem `->writepages`: it initializes range state, tags pages for integrity or tagged writeback, fetches and locks folios by tag, waits for existing writeback in sync mode, clears dirty for I/O, decrements `nr_to_write`, preserves the first error for `WB_SYNC_ALL`, and updates cyclic writeback index without wrapping in a way that would invert folio lock ordering. `do_writepages()` invokes the filesystem's `writepages` op, throttles on repeated `-ENOMEM` in sync mode, and updates bandwidth periodically.

Dirty-state transitions are carefully accounted. `filemap_dirty_folio()` sets the folio dirty bit, calls `__folio_mark_dirty()` to set xarray dirty tags and account `NR_FILE_DIRTY`, `NR_DIRTIED`, `WB_RECLAIMABLE`, `WB_DIRTIED`, task I/O, and cgroup foreign dirty tracking, then marks the inode `I_DIRTY_PAGES`. `folio_clear_dirty_for_io()` serializes against dirty PTEs with the locked folio, performs `folio_mkclean()`, invokes `folio_mark_dirty()` for side effects if needed, clears the dirty bit, and subtracts dirty accounting while leaving xarray tags temporarily coherent for writeback discovery. `__folio_start_writeback()` sets `PG_writeback`, xarray writeback tags, writeback stats, superblock inode-writeback state, clears dirty/TOWRITE tags as appropriate, and updates LRU/zone pending stats. `__folio_end_writeback()` clears writeback state, removes writeback xarray tags, subtracts `WB_WRITEBACK`, increments writeout completions and `NR_WRITTEN`, and wakes waiters through the folio flag transition.

## State And Persistence Behavior

The file maintains runtime-only kernel policy state: dirty thresholds, BDI ratios, writeback-domain fprop completions, timers, per-wb bandwidth/ratelimit stamps, per-CPU dirty ratelimit counters, and per-task `nr_dirtied`, `nr_dirtied_pause`, and `dirty_paused_when`. These states persist across writeback cycles until sysctl changes, CPU hotplug, BDI teardown, or domain exit.

Persistent file data is not written here directly. Instead, this code selects and prepares dirty folios, updates accounting, and calls filesystem `writepages`; the filesystem and lower layers perform actual I/O. Correct xarray tags and folio flags persist in the page cache until writeback or truncation changes them.

## Dependencies And Integration Points

This file depends on the page cache xarray, folios, inode/address-space operations, backing-dev info, cgroup writeback, memcg dirty stats, per-node VM stats, task I/O accounting, CPU hotplug, timers, fprop, sysctl, tracepoints, reclaim throttling, and architecture stable-page hooks.

Ceph integrates through its mapping and inode writeback operations. When Ceph marks folios dirty or implements `writepages`, these helpers control when dirtying tasks throttle, when background writeback starts, how errors propagate in writeback iteration, how cgroup writeback domains apply, and when folios are considered under writeback or clean.

## Risks And Edge Cases

- Dirty throttling is feedback-control code; small changes can destabilize throughput, fairness, or latency.
- Strict-limit BDIs throttle on per-wb counters even when global dirty pages are low; this is important for untrusted or slow filesystems but can surprise callers.
- Memcg writeback adds a second dirty domain; the effective throttle is the lower position ratio of global and memcg domains.
- Per-cpu stat error forces expensive exact stats at low thresholds; missing this can deadlock stacked BDIs by undercounting dirty pages.
- `writeback_iter()` callers must not break out early; they must call until it returns `NULL` so batches, errors, and cyclic index state are finalized.
- Dirty flag and xarray dirty tag are intentionally inconsistent while a folio is locked for writeback preparation; filesystem code must follow the expected folio lifecycle.
- `folio_clear_dirty_for_io()` relies on lock-based exclusion against dirty faults and on filesystem dirty_folio side effects.
- Stable writes can force waits in `folio_wait_stable()`, affecting direct I/O or network filesystem latency.
- `do_writepages()` retries sync writeback on `-ENOMEM` with reclaim throttling, which can stall under severe memory pressure.

## Test Signals

- VM tests should cover sysctl ratio/byte exclusivity, dirty threshold computation, highmem handling, CPU hotplug ratelimit recalculation, and BDI min/max/strict-limit validation.
- Writeback stress should validate `balance_dirty_pages()` under single fast device, slow device, mixed devices, strict-limit BDI, and memcg writeback.
- Filesystem tests should verify `writeback_iter()` usage, `WB_SYNC_ALL` error preservation, cyclic range progression, and no livelock while pages are being dirtied concurrently.
- Folio state tests should exercise dirty, redirty, cancel dirty, clear-for-IO, start/end writeback, wait-writeback, and stable-write behavior with correct VM and wb stats.
- Ceph-client tests should include buffered writes under cgroup limits, dirty throttling during slow OSD/network conditions, writeback error propagation, and page-cache accounting under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/page-writeback.c -->
