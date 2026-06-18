# Group Research: group_898_linux_sources_os_linux_linux_mm_memory_hotplug_c_sources_os_linux_li_e1776d8f8c58

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memory_hotplug.c -->
# File Research: sources/os/linux/linux/mm/memory_hotplug.c

## Purpose

Implements Linux memory hotplug and hotremove plumbing for adding physical memory ranges, creating memory block devices, onlining/offlining pages, updating zones/nodes, and removing memory again. It coordinates architecture memory map operations, sparsemem section management, sysfs memory blocks, firmware maps, node state transitions, and allocator-visible page state.

## Core State and Policy

Key global state includes:

- `mem_hotplug_lock`, a percpu rwsem protecting memory online/offline transitions.
- `online_page_callback`, normally `generic_online_page()`, allowing special page onlining behavior.
- `memmap_mode`, controlled by `memory_hotplug.memmap_on_memory`.
- `online_policy`, controlled by `memory_hotplug.online_policy`.
- `auto_movable_ratio` and `auto_movable_numa_aware`, used by automatic ZONE_MOVABLE placement.
- `movable_node_enabled`, set by the `movable_node` boot parameter.
- `mhp_default_online_type`, set by Kconfig defaults or `memhp_default_state=`.

The file enforces memory-block alignment for public hotplug paths and subsection alignment for lower-level add/remove page paths.

## Add and Online Flow

The primary external add paths are:

- `add_memory()`
- `__add_memory()`
- `add_memory_driver_managed()`
- `add_memory_resource()`

`register_memory_resource()` reserves the physical address range under `iomem_resource`, rejects ranges outside `mhp_get_pluggable_range()`, and marks driver-managed System RAM specially.

`add_memory_resource()` performs the main sequence:

1. Validate block alignment and resolve memory groups.
2. Acquire `mem_hotplug_lock` through `mem_hotplug_begin()`.
3. Optionally update retained memblock metadata.
4. Initialize/register a previously offline NUMA node if needed.
5. Add memory through `arch_add_memory()` or per-block altmaps for memmap-on-memory.
6. Create memory block devices.
7. Register memory blocks under the node and firmware hotplug map.
8. Release the hotplug lock.
9. Merge resources if requested.
10. Auto-online memory blocks if the default online type is not offline.

`__add_pages()` is the lower-level sparsemem section population helper used by architectures and device memory paths.

## Zone Selection

`zone_for_pfn_range()` chooses where memory should be onlined:

- `MMOP_ONLINE_KERNEL` chooses a kernel zone, preferring an intersecting low/normal zone and otherwise ZONE_NORMAL.
- `MMOP_ONLINE_MOVABLE` chooses ZONE_MOVABLE.
- `MMOP_ONLINE` follows `online_policy`.
- `contig-zones` inherits an existing non-overlapping zone when possible.
- `auto-movable` uses MOVABLE:KERNEL_EARLY ratios and memory group state to decide whether the range can safely become ZONE_MOVABLE.

The auto-movable logic treats CMA pages as movable, tracks dynamic memory groups separately, and optionally applies NUMA-local ratio checks.

## Page and Zone State Mutation

Important helpers:

- `move_pfn_range_to_zone()` associates a PFN range with a zone, resizes zone/pgdat spans, initializes memmap entries, sets migratetypes, and handles ZONE_DEVICE subsection taint.
- `remove_pfn_range_from_zone()` poisons struct pages, shrinks zone spans when possible, updates pgdat span, and restores zone contiguity metadata.
- `adjust_present_page_count()` updates zone, node, early-present, and memory-group counters.
- `online_pages_range()` frees hotplugged pages via `online_page_callback` and marks sections online.

`online_pages()` performs notifier calls, zone setup, isolated pageblock accounting, section onlining, present-page accounting, zonelist rebuilds, pageblock un-isolation, page shuffling, watermark recalculation, kswapd/kcompactd startup, and final `MEM_ONLINE` notification.

## Memmap-on-Memory

When `CONFIG_MHP_MEMMAP_ON_MEMORY` is enabled, vmemmap pages can be allocated from the hotplugged memory itself.

Relevant functions:

- `mhp_supports_memmap_on_memory()`
- `mhp_init_memmap_on_memory()`
- `mhp_deinit_memmap_on_memory()`
- `create_altmaps_and_memory_blocks()`
- `remove_memory_blocks_and_altmaps()`

The feature requires pageblock-compatible vmemmap sizing and architecture support. Forced mode can pad vmemmap pages to pageblock alignment, wasting pages in each memory block.

## Hotremove and Offline Flow

Under `CONFIG_MEMORY_HOTREMOVE`, `offline_pages()` is the central offlining operation. It:

1. Verifies alignment and absence of memory holes.
2. Disables PCP lists and LRU cache.
3. Isolates the page range.
4. Sends node and memory notifiers.
5. Repeatedly scans for movable pages with `scan_movable_pages()`.
6. Migrates movable folios with `do_migrate_range()`.
7. Dissolves free hugetlb folios.
8. Confirms isolation.
9. Removes isolated free pages from the buddy allocator.
10. Updates managed/present counters and node states.
11. Rebuilds zonelists and stops per-node daemons if the node becomes memoryless.
12. Sends `MEM_OFFLINE` and removes the PFN range from the zone.

Removal APIs include:

- `remove_memory()`
- `__remove_memory()`
- `offline_and_remove_memory()`
- `try_offline_node()`

`try_remove_memory()` requires all memory blocks offline, removes firmware map entries, removes memory block devices, calls `arch_remove_memory()`, updates retained memblock metadata, releases the resource, and may unregister the NUMA node.

`offline_and_remove_memory()` records per-block online types, attempts to offline all blocks, removes memory, and re-onlines previously offlined blocks on failure.

## Locking and Notifications

- `device_hotplug_lock` serializes external hotplug and sysfs online/offline operations.
- `mem_hotplug_lock` protects core memory topology changes.
- CPU hotplug read locking is acquired while holding the hotplug write side.
- `online_page_callback_lock` protects callback replacement.
- Zone locks protect isolated pageblock counters.
- Node and memory notifier chains gate transitions such as first memory added and last memory removed.

## Integration Points

This file integrates with sparsemem, memblock, `/proc/iomem`, firmware memory maps, sysfs memory blocks, NUMA node registration, page migration, hugetlb, compaction, writeback ratelimits, KASAN shadow setup, memory groups, ZONE_DEVICE, and architecture-specific add/remove memory hooks.

## Risks and Invariants

The key invariants are alignment, section/block granularity, single-zone offlining ranges, all-blocks-offline removal, consistent zone/node span accounting, and correct notifier rollback. Offlining is sensitive to unmovable pages, migration races, hugetlb state, memory holes, and concurrent sysfs operations. Memmap-on-memory adds extra risk because altmap accounting must fully unwind and vmemmap self-hosted pages must be marked online/offline consistently.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memory_hotplug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mempolicy.c -->
# File Research: sources/os/linux/linux/mm/mempolicy.c

## Purpose

Implements Linux NUMA memory policy: process policies, VMA policies, shared tmpfs/shmem policies, policy-aware allocation, policy-driven migration, NUMA balancing placement checks, weighted interleave, and the user-facing `set_mempolicy`, `get_mempolicy`, `mbind`, `migrate_pages`, and `set_mempolicy_home_node` syscalls.

## Policy Model

Supported policy modes include:

- `MPOL_DEFAULT`
- `MPOL_LOCAL`
- `MPOL_PREFERRED`
- `MPOL_PREFERRED_MANY`
- `MPOL_BIND`
- `MPOL_INTERLEAVE`
- `MPOL_WEIGHTED_INTERLEAVE`

The system default policy is local allocation. Per-task policy applies to most process-context allocations. VMA policy overrides task policy for faults. Shared policies persist on backing objects such as tmpfs files.

Policy objects are slab-allocated, refcounted, and freed through RCU because some speculative mmap users can observe policies outside normal mmap lock boundaries.

## Policy Construction and Rebinding

`mpol_new()` validates mode, flags, and nodemask shape. `mpol_set_nodemask()` contextualizes nodemasks against cpuset and online memory nodes, preserving user nodemasks for static/relative modes where needed.

Rebinding paths include:

- `mpol_rebind_task()`
- `mpol_rebind_mm()`
- `mpol_rebind_policy()`

They preserve static, relative, or cpuset-remapped semantics when cpusets change. VMA rebinding is protected by `mmap_write_lock()` and VMA write locking.

## Syscall Paths

`set_mempolicy()` uses `do_set_mempolicy()` to install a task policy under `task_lock()`.

`get_mempolicy()` can report the current policy, allowed mems, next interleave node, weighted interleave node, or the actual node of a page at an address.

`mbind()` uses `do_mbind()` to:

1. Validate range, flags, and nodemask.
2. Build a new policy.
3. Queue misplaced folios when strict or migration flags are requested.
4. Split/merge VMAs and replace VMA policies.
5. Migrate queued folios using policy-aware target allocation.
6. Return strict placement errors when requested.

`migrate_pages()` validates permissions and cpuset access, then moves pages between source and destination node masks while preserving relative node layout when possible.

`set_mempolicy_home_node()` sets `home_node` for existing `MPOL_BIND` or `MPOL_PREFERRED_MANY` VMA policies.

## Page Scanning and Migration

`queue_pages_range()` walks page tables with `mm_walk_ops`, checking whether present folios are on required nodes and optionally isolating them for migration.

It handles:

- PTE mappings.
- THP/PMD mappings.
- hugetlb mappings.
- migration entries.
- strict non-migration checks.
- VMA holes unless `MPOL_MF_DISCONTIG_OK` is set.
- shared folio avoidance unless `MPOL_MF_MOVE_ALL` is set.

Migration target allocation is policy-aware via `alloc_migration_target_by_mpol()`, including hugetlb and large folio cases.

## Allocation-Time Policy

Central allocation helpers include:

- `policy_nodemask()`
- `alloc_pages_mpol()`
- `folio_alloc_mpol_noprof()`
- `vma_alloc_folio_noprof()`
- `alloc_frozen_pages_noprof()`
- `alloc_pages_noprof()`
- `folio_alloc_noprof()`
- `alloc_pages_bulk_mempolicy_noprof()`
- `mempolicy_slab_node()`

`policy_nodemask()` translates policy into a preferred node and optional allocation nodemask. Bind policy applies only for suitable zones, preferred-many uses a two-pass preferred-then-fallback allocation, and interleave policies select nodes by current task counters or address-derived interleave index.

THP allocation avoids broad fallback for non-interleave policies when the current or preferred node is allowed, because remote THP can be worse than smaller local pages.

## Interleave and Weighted Interleave

Classic interleave chooses nodes round-robin by task state or page offset. Weighted interleave uses per-node weights from `wi_state`.

Weighted interleave state is RCU-protected and updated under `wi_state_lock`. It supports:

- Manual per-node weights through sysfs.
- Automatic weights derived from memory-tier performance coordinates via `mempolicy_set_node_perf()`.
- GCD reduction of bandwidth-derived weights.
- Bulk allocation batching by full weighted rounds.

Sysfs creates `/sys/kernel/mm/mempolicy/weighted_interleave`, an `auto` knob, and per-node weight files. Node hotplug adds/removes per-node files.

## Shared Policy Storage

Shared policies are stored in a red-black tree of `struct sp_node` ranges protected by `shared_policy.lock`.

Important functions:

- `mpol_shared_policy_init()`
- `mpol_shared_policy_lookup()`
- `mpol_set_shared_policy()`
- `mpol_free_shared_policy()`
- `shared_policy_replace()`

Range replacement deletes, trims, splits, or inserts policy nodes while preserving non-overlapping file page ranges.

## NUMA Balancing

Under `CONFIG_NUMA_BALANCING`, this file implements:

- `folio_can_map_prot_numa()`
- `change_prot_numa()`
- boot parsing for `numa_balancing=`
- `mpol_misplaced()`

`mpol_misplaced()` decides whether a faulted folio should migrate toward a policy target or the accessing CPU, honoring `MPOL_F_MOF`, `MPOL_F_MORON`, interleave placement, bind/preferred-many masks, and node distance/zonelist choices.

## Tmpfs Policy Parsing

Under `CONFIG_TMPFS`, `mpol_parse_str()` parses mount option policies in the form `<mode>[=<flags>][:<nodelist>]`, and `mpol_to_str()` formats policies for display. It supports static and relative flags and preserves user nodemasks for contextualization.

## Initialization

`numa_policy_init()` creates policy caches, initializes per-node preferred policies, sets an interleave policy for init across memory nodes of sufficient size, and enables or disables automatic NUMA balancing according to config and boot parameters.

## Locking and Lifetime

- Task policies are protected by `task_lock()`.
- VMA policy changes require mmap write locking and VMA write locks.
- Shared policy trees use rwlocks.
- Weighted interleave updates use `wi_state_lock` plus RCU.
- `mpol_put_task_policy()` clears a task pointer before dropping the final ref to avoid allocator instrumentation touching freed policy state.

## Risks and Invariants

Important invariants include valid nodemask/cpuset intersections, correct refcount ownership for shared policies, VMA range continuity checks for `mbind`, avoiding migration of shared/pinned/dirty unsuitable folios, and preserving policy semantics across cpuset rebinding. Weighted interleave must keep RCU readers safe while sysfs and performance updates replace state.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mempolicy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/mempool.c -->
# File Research: sources/os/linux/linux/mm/mempool.c

## Purpose

Implements Linux mempools: small preallocated reserve pools used to guarantee forward progress for memory allocations under heavy VM pressure. Callers provide allocation and free callbacks, and the pool maintains a minimum reserve of reusable elements.

## Core Data Model

A `struct mempool` contains:

- `min_nr`: target reserve size.
- `curr_nr`: current number of reserved elements.
- `elements`: array of reserved element pointers.
- `alloc` / `free`: caller-provided callbacks.
- `pool_data`: callback-private data.
- `lock`: spinlock protecting reserve state.
- `wait`: waitqueue for sleepers waiting for reserve replenishment.

The implementation also supports zero-minimum pools by keeping storage for at least one element and special wakeup handling.

## Creation and Destruction

Main APIs:

- `mempool_init_node()`
- `mempool_init_noprof()`
- `mempool_create_node_noprof()`
- `mempool_exit()`
- `mempool_destroy()`

Initialization allocates the element array and preallocates `max(1, min_nr)` elements. Destruction drains reserved elements through the configured free callback and releases metadata.

## Allocation Flow

`mempool_alloc_noprof()` first tries the normal allocation callback using adjusted GFP flags that avoid emergency reserves, long retries, and noisy warnings. The first pass also suppresses direct reclaim and IO. If that fails, it attempts to remove an element from the reserve.

If direct reclaim is allowed and the reserve is empty, allocation waits on the pool waitqueue with periodic timeout so the normal allocator can be retried as pressure changes. Without direct reclaim, allocation can fail.

`mempool_alloc_bulk_noprof()` applies the same model across an array of element slots, first filling through the callback and then dipping into the reserve for missing entries.

`mempool_alloc_preallocated()` only removes an already-reserved element and never sleeps.

## Free and Refill Flow

`mempool_free_bulk()` returns elements to the reserve while `curr_nr < min_nr`, nulling transferred slots from the caller’s array. Elements beyond the needed reserve remain for the caller to free normally.

`mempool_free()` returns one element to the reserve if needed, otherwise calls the configured free callback.

Memory barriers pair allocation and free paths so a free racing through externally published pointers observes reserve state from after the corresponding allocation. Waiters are woken when elements are added.

## Resizing

`mempool_resize()` can shrink or grow a pool while concurrent allocation/free operations continue. Shrinking frees extra reserved elements. Growing replaces the element pointer array, updates `min_nr`, and opportunistically allocates additional reserve elements; if allocation fails, future frees can refill the pool.

The caller must prevent concurrent destruction.

## Debugging and Sanitizers

The file integrates with:

- fault injection debugfs entries `fail_mempool_alloc` and `fail_mempool_alloc_bulk`;
- SLUB debug poisoning for free/in-use element validation;
- KASAN mempool poison/unpoison helpers;
- kmemleak trace updates when elements are pulled from the reserve.

Debug poisoning supports kmalloc-backed, slab-backed, and page-backed pools, including highmem page mapping where needed.

## Common Callback Helpers

Exported helper alloc/free pairs include:

- `mempool_alloc_slab()` / `mempool_free_slab()`
- `mempool_kmalloc()` / `mempool_kfree()`
- `mempool_alloc_pages()` / `mempool_free_pages()`

These cover slab cache objects, fixed-size kmalloc objects, and page allocations of a configured order.

## Locking and Invariants

`pool->lock` protects `curr_nr` and `elements`. Allocation callbacks are invoked outside the spinlock. The reserve must never exceed `min_nr` except the zero-minimum compatibility slot case. `__GFP_ZERO` is explicitly unsupported for `mempool_alloc_noprof()` because reserve elements are reused and not guaranteed zeroed.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/mempool.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memremap.c -->
# File Research: sources/os/linux/linux/mm/memremap.c

## Purpose

Implements `memremap_pages()` and related helpers for mapping device-managed physical address ranges into the kernel memory model with `struct page` backing, primarily for ZONE_DEVICE users such as device-private memory, coherent device memory, fs-dax, generic device memory, and PCI peer-to-peer DMA memory.

## Core State

The file maintains a global `pgmap_array` xarray mapping PFNs to `struct dev_pagemap` objects. Lookup is RCU-protected and references are taken through the pagemap percpu ref.

`dev_pagemap` ranges may include altmap-backed vmemmap storage. `pfn_first()`, `pfn_end()`, `pfn_len()`, and `pgmap_pfn_valid()` compute usable PFN coverage while accounting for altmap-reserved vmemmap pages.

## Mapping Flow

`memremap_pages()` validates the pagemap, initializes its completion and percpu ref, then maps each range through `pagemap_range()`.

`pagemap_range()` performs the main work:

1. Reject conflicting dev_pagemap mappings at range boundaries.
2. Reject ranges that intersect System RAM.
3. Store the pagemap in `pgmap_array`.
4. Track the PFN map with `pfnmap_track()`.
5. Validate hotplug addressability with `mhp_range_allowed()`.
6. Acquire `mem_hotplug_lock`.
7. Add struct page backing with `add_pages()` for private memory or `arch_add_memory()` for CPU-accessible memory.
8. Add KASAN zero shadow for CPU-accessible memory.
9. Move the range into ZONE_DEVICE.
10. Release the hotplug lock.
11. Initialize ZONE_DEVICE memmap entries with `memmap_init_zone_device()`.
12. Preload pagemap references for relevant device-memory types.

Device-private memory intentionally avoids a linear mapping. Other device memory types use architecture memory-add paths.

## Unmapping Flow

`memunmap_pages()` kills the pagemap percpu ref, drops preloaded references for applicable types, waits for completion, unmaps each range with `pageunmap_range()`, exits the percpu ref, and warns if altmap pages remain allocated.

`pageunmap_range()` removes the PFN range from its zone, removes sparse pages or architecture linear mappings depending on memory type, removes KASAN shadow, untracks the PFN map, and deletes `pgmap_array` entries after RCU synchronization.

Device-managed wrappers:

- `devm_memremap_pages()`
- `devm_memunmap_pages()`

bind unmapping to device resource lifetime.

## Pagemap Lookup and Page Freeing

`get_dev_pagemap()` looks up a pagemap by PFN and attempts to acquire a live percpu reference.

`free_zone_device_folio()` handles release of ZONE_DEVICE folios:

- uncharges memory cgroups;
- clears anonymous exclusive state;
- clears stale mappings for non-fsdax/non-generic types;
- invokes driver `folio_free()` for private, coherent, and P2PDMA pages;
- resets generic page refcount for reuse;
- wakes fs-dax waiters;
- drops pagemap references where required.

`zone_device_page_init()` prepares a ZONE_DEVICE page or compound folio for driver allocation, clears stale compound metadata, assigns `pgmap`, resets fs-dax share state, takes pagemap references, sets refcount, locks the page, and prepares compound page metadata for higher orders.

## Device Type Handling

`memremap_pages()` validates type-specific requirements:

- `MEMORY_DEVICE_PRIVATE` requires `CONFIG_DEVICE_PRIVATE`, `migrate_to_ram`, `folio_free`, and `owner`.
- `MEMORY_DEVICE_COHERENT` requires `folio_free` and `owner`.
- `MEMORY_DEVICE_FS_DAX` uses decrypted page protections.
- `MEMORY_DEVICE_GENERIC` uses default protections.
- `MEMORY_DEVICE_PCI_P2PDMA` uses noncached protections.

## Integration Points

This file integrates with memory hotplug, sparsemem, ZONE_DEVICE, devres, KASAN, pfnmap tracking, percpu refs, xarray lookup, memory cgroups, swap/migration semantics, and architecture add/remove memory hooks.

## Risks and Invariants

Ranges must not overlap System RAM or existing dev_pagemap sections. Altmap support is limited to a single range. The pagemap xarray must be unwound on all failures. Refcount shutdown must wait for all outstanding device page users before tearing down memmap and mappings. ZONE_DEVICE page reinitialization must clear stale compound and mapping state before reuse.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memremap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memtest.c -->
# File Research: sources/os/linux/linux/mm/memtest.c

## Purpose

Implements the early boot `memtest=` facility. It writes a sequence of test patterns over free memblock memory ranges, verifies the values, reserves detected bad physical memory ranges, and reports the total bad memory through proc meminfo.

## State and Patterns

State consists of:

- `early_memtest_done`, indicating at least one test pass ran.
- `early_memtest_bad_size`, accumulated bytes reserved due to failures.
- `memtest_pattern`, the boot-selected number of test passes.

The pattern table starts with zero so tested memory is left zeroed after a full cycle, then includes all-ones, alternating bit patterns, nibble patterns, and a final fixed signature.

## Boot Parameter

`early_param("memtest", parse_memtest)` parses:

- `memtest` without an argument as all available patterns.
- `memtest=<n>` as `n` passes.
- default `0`, meaning disabled.

## Test Flow

`early_memtest(start, end)` exits if disabled. Otherwise it runs `memtest_pattern` passes in reverse index order, wrapping through the pattern array.

`do_one_pass()` iterates all free memblock ranges via `for_each_free_mem_range()`, clamps each range to the requested physical interval, logs the tested range and pattern, and calls `memtest()`.

`memtest()` aligns the physical start to `sizeof(u64)`, writes the pattern to each word through the direct map, then rereads each word. Consecutive failing words are coalesced into bad ranges. Each bad range is passed to `reserve_bad_mem()`.

`reserve_bad_mem()` logs the bad range, reserves it with `memblock_reserve()`, and increments the bad-size counter.

## Reporting

`memtest_report_meminfo()` emits `EarlyMemtestBad` when procfs is enabled and a test ran. A nonzero bad size smaller than 1 KiB is rounded up to 1 KiB; zero means the test completed without detected bad memory.

## Invariants and Risks

The test only covers memblock free ranges, so already reserved memory is skipped. It relies on early direct-map access through `__va()` and runs before normal allocation. Detected failures are quarantined by memblock reservation, but this is a destructive write test over free memory and must run early enough that no live allocations occupy the tested ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memtest.c -->