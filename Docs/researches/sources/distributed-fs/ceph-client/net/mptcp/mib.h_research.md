<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mib.h -->
# sources/distributed-fs/ceph-client/net/mptcp/mib.h

## Purpose
Declares all MPTCP MIB counter fields and inline helpers for updating per-netns MPTCP statistics.

## Important APIs, Types, and Functions
`enum linux_mptcp_mib_field` contains counters for MP_CAPABLE, MP_JOIN, DSS, ADD_ADDR/RM_ADDR, priority/fail/fastclose/reset, stale subflows, shared windows, fallback, blackhole detection, and probes. `struct mptcp_mib` stores the per-CPU counter array. `MPTCP_ADD_STATS()`, `MPTCP_INC_STATS()`, `__MPTCP_INC_STATS()`, and `MPTCP_DEC_STATS()` wrap SNMP helpers with null-storage checks. `mptcp_mib_alloc()` is declared for allocation.

## Control Flow
The inline helpers perform a likely check that MPTCP stats storage exists before updating the selected field. They do not allocate or sleep.

## State and Persistence
The header defines the shape of per-CPU MPTCP statistics; actual storage lives in `net->mib.mptcp_statistics`. Counter values persist for the netns lifetime.

## Dependencies and Integration Points
Depends on inet/SNMP common helpers and is included across MPTCP implementation files that need accounting. It must stay synchronized with `mib.c` string names.

## Risks
Enum reordering breaks user-visible counter interpretation. Callers using `__MPTCP_INC_STATS()` must already be in a context suitable for the non-preempt-safe SNMP update variant. Missing allocation means increments are dropped silently.

## Test Signals
Compile coverage across all MPTCP files, counter-name alignment with `mib.c`, and runtime increases for each feature path in netstat/proc output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mib.h -->
