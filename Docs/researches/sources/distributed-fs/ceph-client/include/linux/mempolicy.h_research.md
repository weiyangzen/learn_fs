<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mempolicy.h -->
# sources/distributed-fs/ceph-client/include/linux/mempolicy.h

## Purpose
This header defines NUMA memory policy structures and APIs for task, VMA, shared-memory, hugepage, migration, and slab allocation policy.

## Important APIs, types, and functions
Under `CONFIG_NUMA`, `struct mempolicy` stores reference count, mode, flags, node masks, home node, rebinding masks, and RCU cleanup. `struct shared_policy` and `struct sp_node` manage rb-tree policy ranges for shared mappings. APIs include policy get/put/dup/equal, shared-policy init/set/free/lookup, VMA policy duplication and lookup, task policy lookup, NUMA default/init, task/mm rebind, hugepage node selection, nodemask initialization, OOM-domain checks, slab node selection, policy zone tracking, page migration, tmpfs policy parse/string formatting, migratability checks, misplaced-page detection, task policy release, preferred-many helper, policy zone applicability, and node performance updates. Non-NUMA builds stub to defaults.

## Control flow
Allocation paths obtain the applicable VMA or task policy, choose nodes according to bind/interleave/preferred modes, and release conditional references. Shared mappings use rb-tree lookups by page offset. Rebinding updates policies after cpuset changes, and NUMA balancing uses `mpol_misplaced()` to decide migrations.

## State and persistence
Policies persist in tasks, mm/VMA structures, or shared-policy trees until replaced or freed. Reference counts and RCU delay object lifetime. No on-disk persistence is defined, although tmpfs can parse policy strings.

## Dependencies and integration points
It depends on scheduler, mm zones, slab, rbtree, spinlocks, nodemasks, pagemap, UAPI mempolicy constants, cpusets, hugepages, tmpfs, and NUMA balancing. It integrates syscalls, VMA management, reclaim/oom, migration, and memory tiers/performance.

## Risks and test signals
Risks include refcount leaks, shared-policy range overlap bugs, stale policies after cpuset rebind, invalid nodemasks, policy-zone mistakes with movable memory, and disabled-NUMA behavior masking policy calls. Test each MPOL mode, shared mappings, fork/VMA duplication, cpuset rebind, hugepage allocation, migration pages syscall, tmpfs parsing, and NUMA=n builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mempolicy.h -->
