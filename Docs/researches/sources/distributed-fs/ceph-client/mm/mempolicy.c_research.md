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
