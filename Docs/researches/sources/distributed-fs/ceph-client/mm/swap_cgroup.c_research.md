# sources/distributed-fs/ceph-client/mm/swap_cgroup.c

Purpose: records and looks up memory cgroup IDs for swap entries, primarily for swap accounting. It stores compact per-swap-slot cgroup IDs in arrays allocated at swapon and freed at swapoff.

Important APIs and functions: `swap_cgroup_record()` records one folio’s cgroup ID across all swap entries it occupies. `swap_cgroup_clear()` clears a contiguous entry range and returns the prior ID. `lookup_swap_cgroup_id()` reads an entry’s ID. `swap_cgroup_swapon()` allocates the per-type map, and `swap_cgroup_swapoff()` unpublishes and frees it. Internals `__swap_cgroup_id_lookup()` and `__swap_cgroup_id_xchg()` pack two `unsigned short` IDs into one atomic word and update one field with `atomic_try_cmpxchg()`.

Control flow: swapon allocates a zeroed map sized by `max_pages`, then publishes it under `swap_cgroup_mutex`. Swapout records an ID for a folio’s slots and asserts that the old IDs were zero. Swapin or slot freeing clears IDs and asserts all entries in the range had the same previous ID. Lookups skip all work when memcg is disabled.

State and persistence: state lives in `swap_cgroup_ctrl[MAX_SWAPFILES]`, where each swap type holds a vmalloc-backed packed ID array. IDs are in-memory accounting metadata and are not persisted in the swap device; they are discarded on swapoff. Atomic packing prevents torn updates when adjacent slots in the same word are modified.

Dependencies and integration points: depends on `linux/swap_cgroup.h`, memcg enablement, swap entry type/offset helpers, vmalloc, and the swapon/swapoff lifecycle in `swapfile.c`. It is consumed by memcg swap accounting and by swap table shadow encoding paths that need cgroup attribution.

Risks and test signals: risks include ID overflow beyond `unsigned short`, publishing or clearing maps while swap entries are still visible, inconsistent old IDs across a folio range, and atomic packing mistakes corrupting the neighboring slot. Test with memcg swap accounting enabled/disabled, folios larger than one page, repeated swapon/swapoff, concurrent swapout/swapin under cgroups, and debug assertions for nonzero old IDs.
