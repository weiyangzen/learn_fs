# `sources/distributed-fs/ceph-client/mm/hugetlb_sysfs.c`

## Purpose
`hugetlb_sysfs.c` creates HugeTLB sysfs interfaces under the global `mm/hugepages` kobject and, on NUMA builds, per-node `node*/hugepages` kobjects. It exposes per-hstate pool sizing, free/reserved/surplus counts, overcommit, mempolicy-aware resizing, and demotion controls.

## Important APIs, Types, And Functions
- Global kobjects: `hugepages_kobj` and `hstate_kobjs[HUGE_MAX_HSTATE]`.
- Kobject lookup: `kobj_to_hstate()` and `kobj_to_node_hstate()` map sysfs objects back to an hstate and optional NUMA node.
- Pool attributes: `nr_hugepages_show/store`, `nr_hugepages_mempolicy_show/store`, `nr_overcommit_hugepages_show/store`, `free_hugepages_show`, `resv_hugepages_show`, and `surplus_hugepages_show`.
- Demotion attributes: `demote_store`, `demote_size_show`, and `demote_size_store`.
- Attribute groups: `hstate_attr_group`, `hstate_demote_attr_group`, and `per_node_hstate_attr_group`.
- Registration helpers: `hugetlb_sysfs_add_hstate()`, `hugetlb_sysfs_init()`, `hugetlb_register_node()`, `hugetlb_unregister_node()`, and `hugetlb_register_all_nodes()`.
- NUMA state: `hugetlb_sysfs_initialized` and `node_hstates[MAX_NUMNODES]`.

## Control Flow
`hugetlb_sysfs_init()` creates the global `hugepages` kobject under `mm_kobj`, then registers one child per hstate using `hugetlb_sysfs_add_hstate()`. Each hstate gets the standard attribute group, and hstates with `demote_order` also get demotion attributes. On NUMA builds, initialization marks sysfs ready and registers hugepage kobjects for all online nodes.

Writes to `nr_hugepages` and `nr_hugepages_mempolicy` parse a decimal count, resolve the target hstate and optional node from the kobject, and call `__nr_hugepages_store_common()` with `obey_mempolicy` false or true. Per-node kobjects pass the node id so the core resize path constrains allocation/free to that node.

`nr_overcommit_hugepages_store()` parses a scalar and updates the hstate overcommit limit under `hugetlb_lock`, rejecting gigantic hstates without runtime support. Count show methods read either global hstate counters or per-node arrays depending on the kobject.

`demote_store()` parses the requested number of huge pages to demote, builds a node mask for a node-specific kobject or all memory nodes for a global kobject, then holds the source hstate `resize_lock` and `hugetlb_lock` while repeatedly calling `demote_pool_huge_page()`. It only demotes free pages beyond reservations. `demote_size_store()` validates that the requested target hugepage size exists, is at least `HUGETLB_PAGE_ORDER`, and is smaller than the source hstate before updating `h->demote_order` under the resize lock.

NUMA node registration creates `node->dev.kobj/hugepages` and per-hstate children with a smaller attribute group. Unregistration removes demote and standard groups, drops kobject references, and clears per-node pointers.

## State And Persistence Behavior
The sysfs files expose live `struct hstate` state and per-node hstate counters. Writes mutate `h->max_huge_pages`, per-node pool counts through core resize, `h->nr_overcommit_huge_pages`, and `h->demote_order`. Kobject pointers persist in global and per-node arrays until unregister/init cleanup. No sysfs value is stored independently of HugeTLB core state.

## Dependencies And Integration Points
This file depends on sysfs/kobject infrastructure, NUMA node devices, `mm_kobj`, hstate iteration, `__nr_hugepages_store_common()`, `demote_pool_huge_page()`, `size_to_hstate()`, `hugetlb_lock`, hstate resize locks, and page-isolation/page-owner headers used by demotion dependencies. It is initialized from `hugetlb_init()` and responds to node hotplug registration callbacks.

## Risks
- Kobject-to-hstate lookup must remain correct; failing to find a kobject calls `BUG()` in the node lookup path.
- Demotion changes two hstates and locks source then destination by size-order convention in the core demotion path. Incorrect lock ordering could deadlock with resize.
- `demote_store()` subtracts reserved pages from free pages before demotion; underflow or stale counts would allow demoting pages needed for reservations.
- Per-node registration can partially fail and must unwind with `hugetlb_unregister_node()` to avoid dangling sysfs entries.
- Global and node-specific attributes have different attribute sets; adding a new attribute requires deciding whether it is valid per-node and updating both groups intentionally.

## Test Signals
- Verify `/sys/kernel/mm/hugepages/hugepages-*/` files exist for each hstate and show counts matching `/proc/meminfo` for the default hstate.
- Write global and per-node `nr_hugepages`, including invalid values and interrupted allocations, and verify counts and error returns.
- On NUMA builds, online/offline node devices and verify per-node hugepage sysfs directories register and unregister cleanly.
- Exercise `demote_size` and `demote` with valid smaller hstates, invalid sizes, reserved pages, poisoned/free pages, and node-specific demotion.
- Write `nr_overcommit_hugepages` on gigantic hstates with and without runtime support and verify rejection/acceptance behavior.
