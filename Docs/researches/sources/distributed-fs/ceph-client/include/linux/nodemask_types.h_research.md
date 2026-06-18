# sources/distributed-fs/ceph-client/include/linux/nodemask_types.h

Purpose: Defines the fundamental NUMA nodemask storage type and node-count constants.

Important APIs, types, and functions: Exports `NODES_SHIFT`, `MAX_NUMNODES`, `NUMA_NO_NODE`, and `nodemask_t` as a bitmap of `MAX_NUMNODES` bits. Detected source surface: 19 lines; includes `linux/bitops.h`; macros `MAX_NUMNODES`, `NODES_SHIFT`, `NUMA_NO_NODE`, `__LINUX_NODEMASK_TYPES_H`; structs none; enums none; typedefs `DECLARE_BITMAP`; function-like declarations/helpers none.

Control flow: No runtime flow; other headers inline bitmap operations over this storage type.

State and persistence behavior: `nodemask_t` instances store caller-owned node sets. The header owns no global state.

Dependencies and integration points: Depends on bitops and `CONFIG_NODES_SHIFT` for NUMA sizing.

Risks and test signals: Risks are insufficient node bit width for platform topology and stack pressure from large nodemask allocations. Test NUMA and non-NUMA builds plus large-node configurations.
