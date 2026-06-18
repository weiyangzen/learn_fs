# sources/distributed-fs/ceph-client/tools/perf/util/cputopo.h

Purpose: declares topology summary structures and lifecycle APIs for CPU, NUMA, and hybrid PMU layouts.

Important APIs/types: `struct cpu_topology`, `struct numa_topology_node`, `struct numa_topology`, `struct hybrid_topology_node`, `struct hybrid_topology`, plus construction/destruction and SMT/core-wide helpers.

Control flow: callers create topology snapshots, inspect unique CPU-list strings or node/PMU arrays, and free with matching delete functions.

State and persistence: structures own strings allocated from sysfs/PMU reads; `online_topology` returns a cached snapshot.

Dependencies and integration: includes Linux types; used by topology display and stat validation paths.

Risks: snapshots are not live-updating after CPU topology changes; implementation delete functions expect valid pointers for NUMA/hybrid.

Test signals: construction/deletion leak checks, SMT/core-wide logic, and hybrid/NUMA absence paths.
