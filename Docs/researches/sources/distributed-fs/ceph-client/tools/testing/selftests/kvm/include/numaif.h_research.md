# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/numaif.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/numaif.h

Purpose: local NUMA policy syscall declarations/constants for selftests that cannot rely on a system `numaif.h` being available.

Important APIs/types/functions: provides NUMA policy constants, mode/flag definitions, and prototypes or syscall wrappers for operations such as `mbind`, `get_mempolicy`, `set_mempolicy`, and page-node queries.

Control flow and state: tests use these wrappers to bind guest memory or host helper allocations to NUMA nodes, then observe placement or migration behavior. Persistent state is host process memory policy until changed or process exit.

Dependencies and integration: relies on Linux NUMA syscalls and `test_util.h` style assertions in users. It integrates with memory backing, memstress, demand paging, and NUMA balancing tests.

Risks: NUMA availability is host-specific. Tests must skip if the system has one node, lacks permissions, or disables NUMA policy support. Incorrect nodemask sizing can make syscalls fail with `EINVAL`.

Test signals: NUMA-aware KVM memory tests validate that policy calls succeed, memory placement is observable, and skip paths work on non-NUMA hosts.
