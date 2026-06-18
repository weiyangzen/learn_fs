# sources/distributed-fs/ceph-client/drivers/base/topology.c

Purpose: this file exposes CPU topology information through sysfs and adds a per-CPU capacity attribute.

Important APIs, types, and functions: macro-generated show/read functions expose IDs and cpumasks for package, die, cluster, core, thread siblings, core siblings, package CPUs, and optional book/drawer topology. `topology_add_dev`, `topology_remove_dev`, and `topology_sysfs_init` register the `topology` sysfs group through CPU hotplug. `DEFINE_PER_CPU(cpu_scale)` stores CPU capacity; `topology_set_cpu_scale`, `cpu_capacity_show`, and `register_cpu_capacity_sysctl` expose capacity.

Control flow: at `device_initcall`, `cpuhp_setup_state` installs callbacks that create/remove the `topology` attribute group on CPU devices. Text attributes use `sysfs_emit` with `topology_*` accessors. Binary cpumask attributes allocate a temporary cpumask, copy the topology mask, and print either bitmask or list format for partial reads. The `ppin` attribute is hidden when `topology_ppin()` returns zero. Capacity sysfs setup uses a dynamic CPU hotplug state to create/remove `cpu_capacity`.

State and persistence: CPU topology values come from architecture topology providers. `cpu_scale` is per-CPU state initialized to `SCHED_CAPACITY_SCALE` and mutated by `topology_set_cpu_scale`.

Dependencies and integration points: it depends on CPU device registration, CPU hotplug state management, cpumask printing helpers, architecture `topology_*` macros/functions, and scheduler capacity definitions.

Risks: sysfs callbacks assume `get_cpu_device(cpu)` succeeds in topology add/remove; the capacity path explicitly handles missing devices. Binary attributes allocate cpumasks per read, so memory allocation failure returns `-ENOMEM`. Optional topology macros change the visible ABI across architectures. Capacity hotplug setup ignores the return value from `cpuhp_setup_state`, always returning zero.

Test signals: sysfs entries under `/sys/devices/system/cpu/cpu*/topology/` and `cpu_capacity` are the main signals. CPU hotplug tests should verify group creation/removal and partial reads of cpumask/list binary attributes.
