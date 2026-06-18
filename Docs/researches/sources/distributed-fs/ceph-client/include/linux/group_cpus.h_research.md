<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/group_cpus.h -->
# sources/distributed-fs/ceph-client/include/linux/group_cpus.h

Purpose: This header declares a helper for dividing CPUs evenly across groups.

Important APIs/types/functions: `group_cpus_evenly(unsigned int numgrps, unsigned int *nummasks)` returns an array of `struct cpumask` entries and reports the number of masks. It includes CPU and kernel helpers.

Control flow, state, and persistence: The implementation allocates and fills cpumasks so callers can distribute interrupts, queues, or workers across CPU groups. The header itself has no state.

Dependencies/integration: It depends on Linux CPU masks and CPU topology data through `linux/cpu.h`.

Risks and test signals: Callers must handle allocation failure and free returned masks according to implementation contract. Tests should cover zero/one/many groups, more groups than CPUs, offline CPUs, NUMA/topology distribution expectations, and `nummasks` reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/group_cpus.h -->
