# subset-b-006137 Research

Grouped source research for Linux memory-management files under the ceph-client source mirror. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memory_hotplug.c -->
# sources/distributed-fs/ceph-client/mm/memory_hotplug.c

## Purpose

`memory_hotplug.c` implements the core Linux memory hotplug and hotremove paths for adding, onlining, offlining, and removing physical memory ranges. It coordinates resource reservation, sparsemem section creation/removal, node and zone span updates, memory block device registration, page onlining callbacks, memmap-on-memory altmaps, automatic `ZONE_MOVABLE` policy, and memory removal migration/isolation. The complete 2432-line file was read.

## Important APIs, Types, and Functions

Exported and externally consumed APIs include `get_online_mems()`, `put_online_mems()`, `mem_hotplug_begin()`, `mem_hotplug_done()`, `mhp_get_default_online_type()`, `mhp_set_default_online_type()`, `pfn_to_online_page()`, `__add_pages()`, `__remove_pages()`, `set_online_page_callback()`, `restore_online_page_callback()`, `generic_online_page()`, `move_pfn_range_to_zone()`, `adjust_present_page_count()`, `mhp_supports_memmap_on_memory()`, `add_memory_resource()`, `__add_memory()`, `add_memory()`, `add_memory_driver_managed()`, `mhp_get_pluggable_range()`, `mhp_range_allowed()`, `try_online_node()`, `try_offline_node()`, `remove_memory()`, and `offline_and_remove_memory()`. Internal state and helper types include `memmap_mode`, `online_policy`, `auto_movable_ratio`, `auto_movable_numa_aware`, `online_page_callback`, the static percpu `mem_hotplug_lock`, `movable_node_enabled`, `mhp_default_online_type`, `auto_movable_stats`, and `auto_movable_group_stats`.

## Control Flow

Adding normal memory starts by reserving an `iomem_resource` child in `register_memory_resource()`, then `add_memory_resource()` validates memory-block alignment, resolves memory-group IDs, serializes with `mem_hotplug_begin()`, optionally updates memblock metadata, initializes/registers a previously offline node, calls either `arch_add_memory()` or per-memory-block `create_altmaps_and_memory_blocks()` for memmap-on-memory, creates memory block devices, links them under the node, adds firmware-map entries for ordinary `System RAM`, releases the hotplug write lock, optionally merges the resource, and auto-onlines memory blocks according to `mhp_get_default_online_type()`.

Onlining a memory block calls `online_pages()` under the hotplug write lock. It moves the PFN range into the selected zone with `move_pfn_range_to_zone()`, notifies node and memory hotplug listeners, adjusts isolated pageblock accounting, initializes zone pagesets if this is the first population of a zone, frees pages through `online_pages_range()` and the registered `online_page_callback`, updates present-page accounting and node states, rebuilds zonelists when needed, undoes page isolation, shuffles the zone, recalculates watermarks, starts `kswapd`/`kcompactd`, updates writeback limits, and emits `MEM_ONLINE`.

Offlining under `CONFIG_MEMORY_HOTREMOVE` is the inverse but more complex. `offline_pages()` rejects holes and multizone ranges, disables per-cpu page lists and LRU cache draining, isolates the range, sends last-memory and going-offline notifications, repeatedly scans for movable pages with `scan_movable_pages()`, migrates them with `do_migrate_range()`, dissolves free hugetlb folios, verifies isolation, removes isolated free pages from the buddy with `__offline_isolated_pages()`, updates managed/present counts and node states, stops reclaim/compaction threads for memoryless nodes, sends `MEM_OFFLINE`, and shrinks zone/node spans with `remove_pfn_range_from_zone()`. Removing memory requires all memory block devices to be offline, removes firmware-map entries, tears down memory block devices, removes arch memory or per-block altmaps, removes memblock and resource state, and may unregister an empty node.

## State and Persistence Behavior

Persistent runtime state spans kernel parameters, node/zone metadata, memory block devices, `/proc/iomem` resources, firmware-map entries, memblock metadata on architectures that keep it, and memory-group present-page counters. `memmap_on_memory`, `online_policy`, `auto_movable_ratio`, and `auto_movable_numa_aware` are module parameters. The hotplug lock serializes structural changes against users that call `get_online_mems()`. Zone and pgdat spans persist after onlining and are shrunk during removal when possible. Memmap-on-memory stores altmap pointers in each `memory_block` and must free all altmap allocations during remove.

## Dependencies and Integration Points

This file integrates with sparsemem (`sparse_add_section()`, `sparse_remove_section()`), architecture hotplug hooks (`arch_add_memory()`, `arch_remove_memory()`, `arch_get_mappable_range()`), memory block sysfs devices, node registration, memblock, firmware maps, resource management, page allocator zones, page isolation and migration, hugetlb, KASAN zero shadow setup, kswapd/kcompactd, writeback throttling, memory notifiers, node notifiers, device hotplug locking, memory groups such as virtio-mem style dynamic groups, and `memremap.c` through `ZONE_DEVICE` and `get_dev_pagemap()`.

## Risks and Edge Cases

Alignment is critical: hotplug operations generally require memory-block or section granularity, while memmap-on-memory introduces pageblock-aligned exceptions. Incorrect zone selection can break kernel/movable memory ratios or create overlapping zone spans. Offlining can fail because of signals, holes, pages with unmovable references, migration failures, hugetlb dissolution failure, notifier vetoes, CPUs still associated with a node, or racing sysfs online attempts. Altmap accounting is fragile because every per-block vmemmap allocation must be undone. `pfn_to_online_page()` has a special slow path for sections tainted by `ZONE_DEVICE` subsection collisions. Resource names control whether memory is considered driver-managed, so malformed names or wrong flags affect kexec and firmware-map behavior.

## Test Signals

Useful tests include memory hotplug selftests for add/online/offline/remove, sysfs memory block onlining across `online_kernel`, `online_movable`, and automatic policies, NUMA node first/last memory notifier coverage, failure-injection of memory and node notifiers, hotremove with busy/unmovable/hugetlb/DMA-pinned pages, altmap and memmap-on-memory add/remove with leak checks, dynamic memory group ratio tests, resource conflict and out-of-mappable-range tests, `movable_node` boot-parameter behavior, and stress tests racing onlining/offlining with allocation, migration, and cpuset changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memory_hotplug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mempolicy.c -->
# sources/distributed-fs/ceph-client/mm/mempolicy.c

## Purpose

`mempolicy.c` implements NUMA memory policy for Linux tasks, VMAs, shared mappings, syscalls, page allocation, page migration, NUMA balancing placement decisions, tmpfs policy parsing, and weighted interleave sysfs controls. It supports default/local, preferred, preferred-many, bind, interleave, and weighted-interleave policies. The complete 3948-line file was read.

## Important APIs, Types, and Functions

Important global objects are `policy_cache`, `sn_cache`, `policy_zone`, `default_policy`, `preferred_node_policy[]`, RCU-protected `wi_state`, `node_bw_table`, and `wi_state_lock`. Key types include `struct weighted_interleave_state`, `struct mempolicy_operations`, `struct migration_mpol`, `struct queue_pages`, `struct sp_node`, `struct shared_policy`, `struct iw_node_attr`, and `struct sysfs_wi_group`.

Important functions include `mempolicy_set_node_perf()`, `numa_nearest_node()`, `nearest_node_nodemask()`, `get_task_policy()`, `mpol_new()`, `mpol_set_nodemask()`, `__mpol_put()`, `mpol_rebind_task()`, `mpol_rebind_mm()`, `queue_pages_range()`, `do_set_mempolicy()`, `do_get_mempolicy()`, `do_mbind()`, `do_migrate_pages()`, `alloc_migration_target_by_mpol()`, syscall handlers for `mbind`, `set_mempolicy`, `get_mempolicy`, `migrate_pages`, and `set_mempolicy_home_node`, `get_vma_policy()`, `vma_policy_mof()`, `policy_nodemask()`, `huge_node()`, `init_nodemask_of_mempolicy()`, `mempolicy_in_oom_domain()`, `vma_alloc_folio_noprof()`, `alloc_pages_noprof()`, `folio_alloc_noprof()`, `alloc_pages_bulk_mempolicy_noprof()`, `vma_dup_policy()`, `__mpol_dup()`, `__mpol_equal()`, shared-policy helpers, `mpol_misplaced()`, `numa_policy_init()`, `numa_default_policy()`, `mpol_parse_str()`, and `mpol_to_str()`.

## Control Flow

User policy installation begins in syscall wrappers, which sanitize encoded mode flags, copy variable-sized user nodemasks, and call `do_set_mempolicy()` or `do_mbind()`. `do_set_mempolicy()` creates a policy with `mpol_new()`, contextualizes its nodes against cpuset and `N_MEMORY` via `mpol_set_nodemask()`, installs it under `task_lock()`, and resets interleave counters when needed. `do_mbind()` validates the range and move flags, creates the new policy, write-locks the mm, locks VMAs during page-table walking, queues misplaced folios if strict/move flags require it, updates VMA policy ranges through `mbind_range()` and `vma_replace_policy()`, then migrates queued folios using policy-aware target allocation.

Page scanning uses `walk_page_range()` with PTE, PMD, and hugetlb callbacks. It skips holes only when allowed, rejects strict misplaced folios with `-EIO`, and isolates migratable folios when `MPOL_MF_MOVE` or `MPOL_MF_MOVE_ALL` is set. `migrate_pages()` uses either simple node-remap targets for `migrate_pages(2)` or `alloc_migration_target_by_mpol()` for `mbind(2)`.

Allocation flow obtains the effective policy from a VMA or task, translates it with `policy_nodemask()` into a preferred nid plus optional nodemask, and calls the page allocator. Interleave policies choose either a process counter (`interleave_nodes()`, `weighted_interleave_nodes()`) or a page-offset index (`interleave_nid()`, `weighted_interleave_nid()`). Preferred-many first tries preferred nodes without direct reclaim, then falls back globally. THP allocation under non-interleave policy may first attempt the selected node with `__GFP_THISNODE | __GFP_NORETRY` to avoid remote THP cost.

Shared mappings keep persistent policy ranges in a red-black tree under `shared_policy.lock`. Init, lookup, replace, and free paths duplicate policies, mark them shared, split overlapping intervals, and preserve policy after mappings disappear. Weighted interleave has both automatic bandwidth-derived updates from memory-tier performance data and manual sysfs updates under `/sys/kernel/mm/mempolicy/weighted_interleave`.

## State and Persistence Behavior

Task policies live in `task_struct->mempolicy` and are reference counted. VMA policies live in `vma->vm_policy`; shared policies persist in inode-associated `shared_policy` trees. Policies are re-bound when cpusets change, preserving static, relative, or remapped node semantics. `default_policy` is never freed, and per-node preferred policies provide NUMA-balancing-friendly defaults. Weighted interleave state is RCU-published, while writers serialize with `wi_state_lock`; manual mode persists until sysfs switches back to auto. Tmpfs mount policies are parsed into stored user nodemasks so they can be contextualized later in the caller's cpuset.

## Dependencies and Integration Points

This file integrates with cpusets and `mems_allowed_seq`, page-table walking, folio migration, hugetlb, THP, KSM, DAX exclusion, memory tiers and access coordinates, scheduler NUMA balancing, security hooks, ptrace permission checks, syscalls, compat bitmap handling, slab allocation, tmpfs mount option parsing, proc/sysfs formatting, mmu notifiers through protection changes, zonelists, OOM domain filtering, and KVM-visible exported mempolicy helpers.

## Risks and Edge Cases

Nodemask validation is subtle because user masks can exceed `MAX_NUMNODES`, cpusets can rebind concurrently, and static/relative flags change remapping semantics. Strict `mbind()` can return `-EIO` without migrating if any misplaced page is detected. Migration can miss or fail pages due to shared mappings, hugetlb sharing, migration entries, non-migratable VMAs, dirty file folios, pins, or allocation failures. Weighted interleave depends on RCU lifetime and nonzero weights; manual sysfs writes can diverge from auto bandwidth state. `set_mempolicy_home_node()` intentionally does not roll back already-updated VMAs on later errors. Policy application is limited by `policy_zone`, movable-only node masks, and `__GFP_THISNODE` warnings under bind policy.

## Test Signals

Useful signals include syscall selftests for all policy modes and flags, compat `maxnode` bitmap tests, cpuset rebind and relative/static node tests, `mbind()` strict/move/move-all migration tests, permission checks for moving another process, THP and hugetlb policy allocation tests, tmpfs mount policy parse/format round trips, shared-policy interval replacement tests, NUMA balancing misplaced-folio tests, sysfs weighted-interleave manual and auto tests with node hotplug, and allocator tests verifying bind/preferred/interleave behavior under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mempolicy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mempool.c -->
# sources/distributed-fs/ceph-client/mm/mempool.c

## Purpose

`mempool.c` implements Linux generic memory pools: preallocated emergency reserves used by subsystems that must make bounded, deadlock-resistant allocations under memory pressure. It provides lifecycle, resize, single and bulk allocation, refill/free logic, debug poisoning, KASAN support, fault-injection hooks, and common slab/kmalloc/page backends. The complete 766-line file was read.

## Important APIs, Types, and Functions

Public APIs include `mempool_init_node()`, `mempool_init_noprof()`, `mempool_create_node_noprof()`, `mempool_exit()`, `mempool_destroy()`, `mempool_resize()`, `mempool_alloc_bulk_noprof()`, `mempool_alloc_noprof()`, `mempool_alloc_preallocated()`, `mempool_free_bulk()`, `mempool_free()`, `mempool_alloc_slab()`, `mempool_free_slab()`, `mempool_kmalloc()`, `mempool_kfree()`, `mempool_alloc_pages()`, and `mempool_free_pages()`. Important internal helpers include `add_element()`, `remove_element()`, `mempool_alloc_from_pool()`, `mempool_adjust_gfp()`, `poison_element()`, `check_element()`, and KASAN poison/unpoison helpers. Fault attributes `fail_mempool_alloc` and `fail_mempool_alloc_bulk` are created at late init.

## Control Flow

Initialization sets the spinlock, minimum reserve, callback pointers, waitqueue, and element array, then preallocates `max(1, min_nr)` elements. Allocation first adjusts GFP flags to avoid global emergency reserves and page allocator retries, then tries the caller-supplied allocator with a non-reclaiming first pass. If allocation fails or fault injection forces reserve use, `mempool_alloc_from_pool()` removes an element under the pool lock. Sleepable callers wait on the pool waitqueue with periodic timeouts when the reserve is empty; non-sleeping callers can return `NULL`.

Bulk allocation repeats the same pattern across an array, using normal allocation first and dipping into reserves for missing slots. Freeing uses a barrier-paired fast check of `curr_nr`; if the pool is below `min_nr`, it returns elements to the reserve under lock and wakes waiters. If the pool is already full, `mempool_free()` calls the backend free function. Resize can shrink by freeing extra reserve elements or grow by reallocating the element pointer array and filling new reserve slots opportunistically.

## State and Persistence Behavior

The durable pool state is `struct mempool`: `min_nr`, `curr_nr`, backend callbacks, `pool_data`, reserve `elements[]`, spinlock, and waitqueue. Reserved elements stay poisoned and KASAN-poisoned while in the pool and are unpoisoned when removed. Zero-minimum pools still allocate storage for one reserve slot and have explicit free-side wake/refill handling to avoid sleeping waiters being stranded.

## Dependencies and Integration Points

The file depends on slab and page allocators, KASAN mempool hooks, SLUB debug poisoning constants, kmemleak trace updates, waitqueues, `io_schedule_timeout()`, fault-injection debugfs, writeback-related scheduling context, and exported mempool APIs used by block, filesystem, networking, and storage paths that cannot tolerate allocation recursion deadlocks.

## Risks and Edge Cases

Callers must not use `__GFP_ZERO` with `mempool_alloc()`, must size bulk requests no larger than `min_nr`, and must ensure `mempool_destroy()` does not race with `mempool_resize()`. Backend callbacks may sleep, so context rules depend on both GFP flags and callback behavior. Barrier pairing between allocation and free protects rare lockless handoff cases; weakening it can lose reserve refills or wakeups. Debug poisoning is skipped under KASAN because KASAN may store metadata in freed objects. Zero-minimum pools have special behavior and should not be assumed to guarantee progress beyond one returned preallocated slot.

## Test Signals

Useful tests include fault-injection forcing reserve use, bulk allocation with partially prefilled arrays, allocation under `GFP_NOWAIT` and `GFP_KERNEL`, wait/wakeup behavior with empty pools, resize grow/shrink while allocations occur, zero-minimum pool allocation/free cycles, KASAN and SLUB poisoning mismatch detection, slab/kmalloc/page backend coverage, and kmemleak trace update checks for reserve-sourced elements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/mempool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memremap.c -->
# sources/distributed-fs/ceph-client/mm/memremap.c

## Purpose

`memremap.c` implements `memremap_pages()` and related helpers that map device or persistent memory ranges into the kernel page model as `ZONE_DEVICE` pages. It tracks PFN-to-`dev_pagemap` ownership, adds/removes device memory through memory-hotplug infrastructure, initializes device folios, and handles teardown once all page references drain. The complete 528-line file was read.

## Important APIs, Types, and Functions

Important APIs include `memremap_compat_align()`, `pgmap_pfn_valid()`, `memunmap_pages()`, `memremap_pages()`, `devm_memremap_pages()`, `devm_memunmap_pages()`, `get_dev_pagemap()`, `free_zone_device_folio()`, and `zone_device_page_init()`. Internal helpers include `pgmap_array_delete()`, `pfn_first()`, `pfn_end()`, `pfn_len()`, `pageunmap_range()`, `devm_memremap_pages_release()`, `dev_pagemap_percpu_release()`, and `pagemap_range()`. The central state is the global XArray `pgmap_array`, indexed by PFN and read under RCU.

## Control Flow

`memremap_pages()` validates the `dev_pagemap` range count, vmemmap shift, type-specific operations, owner fields, and page protections. It initializes a percpu reference, temporarily clears `pgmap->nr_range`, and maps each range through `pagemap_range()`. That helper rejects conflicting pgmaps at range boundaries, rejects System RAM overlaps, stores the pgmap over the PFN range in `pgmap_array`, tracks the PFN map, checks the hotplug mappable range, takes the memory hotplug lock, adds struct pages via `add_pages()` for private device memory or `arch_add_memory()` plus KASAN zero shadow for CPU-accessible memory, moves the range into `ZONE_DEVICE`, drops the hotplug lock, initializes the zone-device memmap, and pins the pgmap reference for non-private/non-coherent pages.

Teardown through `memunmap_pages()` kills the percpu ref, drops range-sized references for ordinary device memory, waits for completion, unmaps each range with `pageunmap_range()`, exits the percpu ref, and warns if altmap allocations remain. `pageunmap_range()` removes the PFN range from the zone, calls either `__remove_pages()` or `arch_remove_memory()`, removes KASAN shadow for CPU-accessible memory, untracks the PFN map, and clears the XArray entry after an RCU grace period.

## State and Persistence Behavior

`pgmap_array` persists the live PFN ownership map until unmap. `dev_pagemap->ref` gates removal against live pages, with `dev_pagemap_percpu_release()` completing teardown when the ref drains. `pgmap->altmap` tracks vmemmap allocations for devices that self-host struct pages. Zone-device pages carry `folio->pgmap` and type-specific fields such as DAX share counts. Device-managed mappings registered with `devm_memremap_pages()` persist until the owning device releases the devres action or `devm_memunmap_pages()` is called.

## Dependencies and Integration Points

This file integrates with memory hotplug, `ZONE_DEVICE`, sparsemem, KASAN zero shadow, pfnmap tracking, XArray/RCU lookup, percpu references and completions, devres, DAX, HMM/device-private and coherent memory, generic device memory, PCI peer-to-peer DMA, folio migration/free callbacks, memcg uncharge, swapops, page locking, and architecture direct-map creation/removal.

## Risks and Edge Cases

Device memory must not overlap System RAM or an existing `dev_pagemap`, and altmaps are unsupported for multiple ranges. Private memory is inaccessible to the CPU and intentionally skips direct-map creation; CPU-accessible types need KASAN zero shadow and arch mappings. Reference draining is central: removing mappings while pages are still live would corrupt `ZONE_DEVICE` users. `free_zone_device_folio()` has type-specific semantics; clearing stale mapping state is required for private/coherent pages but not for FS DAX or generic pages. `zone_device_page_init()` clears stale compound metadata and warns if drivers allocate after `memunmap_pages()`.

## Test Signals

Useful tests include DAX namespace map/unmap cycles, HMM private/coherent migration tests, PCI P2PDMA mapping tests, overlap/conflict rejection, invalid type/missing-ops validation, altmap allocation accounting, devres automatic cleanup, `get_dev_pagemap()` lookup under concurrent teardown, KASAN shadow add/remove coverage, and folio free paths for each `MEMORY_DEVICE_*` type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memtest.c -->
# sources/distributed-fs/ceph-client/mm/memtest.c

## Purpose

`memtest.c` implements the early boot `memtest=` physical memory test. It writes a sequence of 64-bit patterns over free memblock ranges, verifies the pattern, reserves any bad physical ranges so the rest of the kernel will not allocate them, and reports the reserved bad-memory total through proc meminfo. The complete 139-line file was read.

## Important APIs, Types, and Functions

The file keeps `early_memtest_done`, `early_memtest_bad_size`, and the `patterns[]` table, whose first entry is zero so the final pass can leave memory zeroed. Important functions are `parse_memtest()`, registered by `early_param("memtest", ...)`, `early_memtest()`, `do_one_pass()`, `memtest()`, `reserve_bad_mem()`, and `memtest_report_meminfo()`.

## Control Flow

Boot parameter parsing sets `memtest_pattern` to the user-supplied count or to the number of built-in patterns when `memtest` is passed without an argument. `early_memtest(start, end)` returns immediately when disabled. Otherwise it iterates backward for the requested number of tests, maps each pass to `patterns[i % ARRAY_SIZE(patterns)]`, and calls `do_one_pass()`. `do_one_pass()` walks free memblock ranges, clamps them to the requested physical bounds, logs the range and pattern, and calls `memtest()`. `memtest()` aligns the start address to an eight-byte pattern boundary, writes the pattern with `WRITE_ONCE()`, reads it back with `READ_ONCE()`, coalesces adjacent bad words into physical ranges, and calls `reserve_bad_mem()` for each bad span.

## State and Persistence Behavior

Bad regions are persisted by `memblock_reserve()`, making them unavailable for later boot allocation. `early_memtest_bad_size` accumulates the reserved byte total, and `early_memtest_done` controls whether `memtest_report_meminfo()` emits `EarlyMemtestBad`. A reported value of zero after a completed test means the test ran successfully without detected bad memory.

## Dependencies and Integration Points

The implementation depends on early memblock free-range iteration, direct physical-to-virtual mapping via `__va()`, boot parameter parsing, kernel logging, and procfs meminfo emission through `seq_file`. It must run early enough that tested free ranges are safe to overwrite and before normal allocators consume bad regions.

## Risks and Edge Cases

The test is destructive by design and must only touch free memblock ranges. Start alignment can skip leading unaligned bytes. `VM_WARN_ON_ONCE()` guards against impossible underflow when the aligned start exceeds the range. The loop in `early_memtest()` uses unsigned decrement from `memtest_pattern - 1` to zero, so disabled state must be filtered before entering it. Very small bad totals report as 1 kB to avoid hiding nonzero failures after shifting to KiB.

## Test Signals

Useful signals include boot tests with `memtest=0`, `memtest=1`, and bare `memtest`, log verification for tested ranges and patterns, injected memory corruption in an early test environment, checks that bad spans are reserved in memblock and reflected in `EarlyMemtestBad`, and confirmation that no proc output appears when the early test did not run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memtest.c -->
