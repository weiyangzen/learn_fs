<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_rapl.h -->
# sources/distributed-fs/ceph-client/include/linux/intel_rapl.h

Purpose: Defines common data structures and interfaces for Intel RAPL power/energy limiting across MSR, MMIO, and TPMI backends.

Important APIs/types/functions: Enums model interface type, domain type, domain registers, primitives, and units. `struct rapl_domain_data`, `rapl_power_limit`, `rapl_domain`, `reg_action`, `rapl_defaults`, `rapl_primitive_info`, `rapl_if_priv`, optional `rapl_package_pmu_data`, and `rapl_package` represent domains, registers, constraints, units, primitive metadata, package topology, CPU hotplug, and PMU state. APIs find/add/remove packages, check units, set floor frequency, compute time windows, and add/remove PMUs under `CONFIG_PERF_EVENTS`.

Control flow: Backend drivers register interface callbacks and packages; common RAPL code reads/writes primitives, exposes powercap zones, handles hotplug, and optionally registers PMU energy counters.

State/persistence: Package/domain state persists while CPUs/packages are online; energy counters and power limits reflect hardware registers and powercap constraints.

Dependencies/integration: Integrates powercap, CPU hotplug, perf events, hrtimers, cpumasks, MSR/MMIO/TPMI backends.

Risks: Unit conversion and time-window encoding are platform-specific; package hotplug locking variants must be used in the right context.

Test signals: Powercap zone creation, limit read/write, energy counter updates, CPU hotplug add/remove, perf PMU events, and MSR/MMIO/TPMI backend parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/intel_rapl.h -->
