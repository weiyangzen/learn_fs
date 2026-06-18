<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/topology.c -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/topology.c

### Purpose
`topology.c` registers CPU devices and constructs PA-RISC package/core topology records.

### Important APIs, Types, And Functions
It defines per-cpu `cpu_devices`, `store_cpu_topology()`, and `init_cpu_topology()`.

### Control Flow
On first topology storage for a CPU, it marks the CPU hotpluggable when supported, registers the CPU device, initializes thread/core IDs, compares firmware `cpu_loc` values with online CPUs, assigns package IDs, updates sibling masks, and logs the resulting core/socket pair. Init resets all CPU topology state.

### State, Persistence, And Dependencies
Persistent state is `cpu_topology[]`, registered CPU devices, and sibling masks. Dependencies include per-cpu `cpu_data`, CPU hotplug locking assumptions, generic topology helpers, and firmware location values.

### Integration Points
Called from CPU probing and early boot topology initialization; `show_cpuinfo()` later reads generic topology values.

### Risks
Package/core inference is heuristic around `cpu_loc`, especially when firmware reports zero. Registration failures are warnings rather than fatal.

### Test Signals
SMP boot with multiple sockets/cores, CPU hotplug device registration, sibling masks, and `/proc/cpuinfo` physical/core IDs should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/topology.c -->
