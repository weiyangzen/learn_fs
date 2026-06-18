<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swap.h -->
# sources/distributed-fs/ceph-client/include/linux/swap.h

## Purpose

`swap.h` is the central VM header for swap space, reclaim, LRU handling, swapcache accounting, and memory-cgroup swap charging. It defines swap flags, special swap entry type allocation, swap area metadata, reclaim helpers, and configuration stubs.

## Important APIs, types, and functions

The header defines user-visible swap flags, `MAX_SWAPFILES` layout with reserved pseudo-types for hwpoison, migration, device-private memory, and PTE markers, `union swap_header`, `struct reclaim_state`, `struct swap_extent`, `struct swap_sequential_cluster`, and `struct swap_info_struct`. APIs include reclaimed-page accounting, workingset hooks, LRU add/drain and access helpers, reclaim entry points, swap extent activation, swapcache freeing, swap device lookup/refcounting, swap counts, hibernation swap slots, memcg swappiness/charging/uncharge helpers, swap throttling, and managed-zone iteration.

## Control flow

Swap activation parses headers and extents into `swap_info_struct`, then allocation uses cluster lists, sequential cluster hints, and per-device locks. Reclaim paths isolate folios, may allocate swap entries, add to swapcache, write pages, free swapcache later, and account reclaimed pages through `current->reclaim_state`. Memcg paths charge and uncharge swap entries when swap is enabled and memory cgroups are active.

## State and persistence behavior

Persistent disk state is the swap header and swap area contents. In-memory state lives in `swap_info_struct`: flags, priority, extent tree, cluster lists, zeromap, total/free page counters, locks, discard/reclaim work, and percpu user references. Global counters include `nr_swap_pages`, `total_swap_pages`, `nr_rotate_swap`, and `lru_disable_count`.

## Dependencies and integration points

It depends on spinlocks, MM zones, memcg, scheduler, filesystem/pagemap, page flags, mempolicy UAPI, and architecture page definitions. It integrates with vmscan, swapfile, shmem, hibernation, HMM/device-private memory, memory failure, cgroups, block discard, LRU generation, and sysinfo reporting.

## Risks and test signals

Risks include special swap type overlap, lock ordering between `swap_lock` and per-device locks, races during swapoff, bad cluster accounting, THP swap order handling, memcg disabled stubs masking behavior, and accidental I/O under no-IO reclaim contexts. Tests should cover swapon/swapoff, full-swap behavior, discard modes, swapcache counts, migration/device-private/hwpoison entries, memcg charging, hibernation slots, CONFIG_SWAP disabled builds, and stress with concurrent reclaim and swapoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swap.h -->
