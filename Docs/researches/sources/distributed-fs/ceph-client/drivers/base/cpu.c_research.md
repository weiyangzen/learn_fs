# sources/distributed-fs/ceph-client/drivers/base/cpu.c

## Purpose
`cpu.c` implements the driver-core CPU subsystem and the `/sys/devices/system/cpu` surface. It registers per-CPU devices, exposes CPU masks and CPU vulnerability attributes, supports hotplug online/offline operations, and provides helper device creation under CPU devices.

## Important APIs, Types, And Functions
Important state includes per-CPU `cpu_sys_devices`, `cpu_subsys`, `total_cpus`, and optional per-CPU `cpu_devices`. Key APIs are `register_cpu()`, `unregister_cpu()`, `get_cpu_device()`, `cpu_device_create()`, `cpu_is_hotpluggable()`, weak `arch_register_cpu()` and `arch_unregister_cpu()`, and `cpu_dev_init()`. Sysfs helpers print online, possible, present, offline, enabled, isolated, housekeeping, nohz_full, crash, modalias, and vulnerability data.

## Control Flow, State, And Persistence
`cpu_dev_init()` registers the CPU bus with root attributes, registers present CPUs when generic CPU devices are enabled, then installs vulnerability attributes. `register_cpu()` initializes a `struct cpu` device, binds it to `cpu_subsys`, registers it in sysfs, records it in the per-CPU pointer array, links it under its NUMA node, exposes resume latency QoS, and marks it enabled. Hotplug online retries transient `-EBUSY`, then adjusts NUMA node links if CPU-to-node mapping changed.

## Dependencies, Integration Points, Risks, And Test Signals
The file depends on ACPI matching, OF CPU nodes, NUMA node devices, CPU hotplug, cpumasks, scheduler isolation, tick/nohz, crash dump notes, PM QoS, and architecture hooks. Risks center on hotplug races, static CPU device lifetime, sysfs output staying within page buffers, weak fallback vulnerability text hiding architecture omissions, and NUMA relinking. Test signals include CPU online/offline sysfs operations, node relink after memoryless-node hot add, cpumask output, crash note addresses, modalias generation, and vulnerability group registration.
