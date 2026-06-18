# sources/distributed-fs/ceph-client/include/uapi/linux/mempolicy.h

## Purpose
Defines NUMA memory policy modes and flags for `set_mempolicy(2)`, `get_mempolicy(2)`, `mbind(2)`, and zone reclaim sysctl bit meanings.

## Important APIs, Types, And Functions
Exports policy modes `MPOL_DEFAULT`, `MPOL_PREFERRED`, `MPOL_BIND`, `MPOL_INTERLEAVE`, `MPOL_LOCAL`, `MPOL_PREFERRED_MANY`, `MPOL_WEIGHTED_INTERLEAVE`, mode flags `MPOL_F_STATIC_NODES`, `MPOL_F_RELATIVE_NODES`, `MPOL_F_NUMA_BALANCING`, get flags, mbind move/strict flags, internal flags, and reclaim bits.

## Control Flow
Userspace combines a mode with legal mode flags, supplies nodemasks to policy syscalls, and optionally requests strict validation or page migration through mbind flags. `get_mempolicy` flags choose whether to query by address, node, or allowed memories.

## State, Persistence, And Dependencies
Policies persist in task or VMA memory policy state inside the kernel. Header dependency is `linux/errno.h`.

## Integration Points
Used by NUMA-aware allocators, databases, HPC runtimes, and test tools. Zone reclaim constants map to `/proc/sys/vm/zone_reclaim_mode`.

## Risks
Mode flags share integer space with modes, internal flags are not syscall inputs, and unsupported `MPOL_MF_LAZY` is explicitly invalid. Incorrect nodemask relativity/static semantics can place memory on unintended nodes.

## Test Signals
Exercise each public mode, nodemask validation, get flags, mbind strict/move behavior, NUMA balancing flag acceptance, weighted interleave support, and sysctl bit interpretation.
