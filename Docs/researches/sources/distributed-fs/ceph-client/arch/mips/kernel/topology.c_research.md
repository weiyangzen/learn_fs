## sources/distributed-fs/ceph-client/arch/mips/kernel/topology.c

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/topology.c` registers MIPS CPU devices with the generic CPU topology/sysfs layer during subsystem initialization.

### Important APIs, Types, And Functions
The file defines per-CPU `struct cpu cpu_devices` and the `topology_init()` subsys initcall. It uses `for_each_present_cpu()` and `register_cpu()`.

### Control Flow
At `subsys_initcall`, the code iterates all present CPUs, obtains the per-CPU `struct cpu`, marks all nonzero CPU IDs as hotpluggable, registers each CPU device, and logs a warning if registration fails.

### State, Persistence, And Dependencies
State is the per-CPU `struct cpu` device object and sysfs-visible CPU registration. Dependencies include generic CPU device infrastructure, present CPU masks set by SMP setup, percpu storage, and hotplug conventions.

### Integration Points
This is the bridge from MIPS CPU discovery in SMP/platform setup to generic CPU sysfs and node topology. Hotplug policies rely on `hotpluggable` values.

### Risks
Registration failures only warn, so partial sysfs topology can occur. CPU0 is deliberately not hotpluggable. The correctness of the present CPU mask before this initcall determines which CPU devices appear.

### Test Signals
Boot UP and SMP systems, inspect `/sys/devices/system/cpu`, verify CPU0 hotplug status, hotplug nonzero CPUs where supported, and test behavior when CPU registration fails.
