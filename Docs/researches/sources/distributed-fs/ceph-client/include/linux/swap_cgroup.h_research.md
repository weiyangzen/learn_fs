<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swap_cgroup.h -->
# sources/distributed-fs/ceph-client/include/linux/swap_cgroup.h

## Purpose

`swap_cgroup.h` declares the swap-cgroup metadata interface used to associate swap entries with memory cgroup IDs. It provides real declarations when both memory cgroups and swap are enabled and no-op stubs otherwise.

## Important APIs, types, and functions

The active API includes `swap_cgroup_record()`, `swap_cgroup_clear()`, `lookup_swap_cgroup_id()`, `swap_cgroup_swapon()`, and `swap_cgroup_swapoff()`. These functions record cgroup ownership for folio swap entries, clear ownership for ranges, query stored IDs, and allocate/free per-swap-type metadata during swapon/swapoff.

## Control flow

During swapout, VM/memcg code records the cgroup ID for the allocated swap entry. During swapin or swap freeing, the entry can be looked up or cleared. Swapon allocates metadata sized by max pages; swapoff tears it down.

## State and persistence behavior

The state is in-memory metadata keyed by swap type and offset. It does not persist on disk; after reboot or swapoff, ownership records disappear. Stub builds drop all accounting and return zero/success.

## Dependencies and integration points

It depends on `swap.h` and, when enabled, memcg and swap internals. It integrates with memcg charging/uncharging, swap activation/deactivation, and reclaim paths.

## Risks and test signals

Risks include losing accounting when CONFIG combinations disable the implementation, stale IDs after swapoff races, clearing too few or too many entries, and mismatches between folio size and entry count. Tests should cover swapon metadata allocation, record/lookup/clear for multi-page folios, memcg disabled stubs, swapoff cleanup, and concurrent reclaim/swapin paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swap_cgroup.h -->
