<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mib.c -->
# sources/distributed-fs/ceph-client/net/mptcp/mib.c

## Purpose
Defines MPTCP SNMP/MIB counter names, allocates per-netns counter storage on demand, and renders counters through seq_file output.

## Important APIs, Types, and Functions
`mptcp_snmp_list` maps human-readable names to `enum linux_mptcp_mib_field` values. `mptcp_mib_alloc()` allocates per-CPU `struct mptcp_mib` storage using `cmpxchg()` so the first MPTCP socket initializes statistics once. `mptcp_seq_show()` emits the `MPTcpExt:` header and values.

## Control Flow
Allocation creates a per-CPU MIB block and installs it only if `net->mib.mptcp_statistics` is still NULL, freeing the loser on races. Rendering writes all names, batches per-CPU sums if stats exist, then writes matching values in the same order.

## State and Persistence
Counter storage is per network namespace in `net->mib.mptcp_statistics` and persists until namespace teardown. Counters are in-memory runtime statistics exposed through proc/net SNMP-style files.

## Dependencies and Integration Points
Depends on SNMP per-CPU helpers, seq_file, net namespace MIB storage, and field definitions from `mib.h`. Integrated throughout MPTCP via `MPTCP_INC_STATS()`, `MPTCP_ADD_STATS()`, and related macros.

## Risks
The list order must match enum fields or user-visible counters become misleading. Allocation is lazy; stat increments before allocation are intentionally ignored by macros. Adding enum values requires updating this string list and tests/monitoring expectations.

## Test Signals
Observe `/proc/net/netstat` MPTCP lines after creating MPTCP connections, MP_JOIN, ADD_ADDR/RM_ADDR, fallback, reset, and stale-subflow scenarios. Race tests should confirm one per-CPU allocation survives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mib.c -->
