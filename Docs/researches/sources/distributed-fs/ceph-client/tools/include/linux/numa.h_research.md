<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/numa.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/numa.h

## Purpose
This header defines minimal NUMA node constants and validation for tools builds.

## APIs And Flow
It maps `NODES_SHIFT` from `CONFIG_NODES_SHIFT` or zero, defines `MAX_NUMNODES`, `NUMA_NO_NODE`, and `numa_valid_node()`. Flow is a range check that accepts node IDs from zero up to `MAX_NUMNODES - 1`.

## State, Dependencies, Risks, Tests
There is no runtime state. The only dependency is the optional config macro. Integration points include allocators and topology code that need to accept or ignore node IDs. Risks are defaulting to a single node in tools, mismatch with host NUMA topology, and callers treating `NUMA_NO_NODE` as valid. Tests should compile with and without `CONFIG_NODES_SHIFT` and validate boundary node IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/numa.h -->
