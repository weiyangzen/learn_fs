# sources/distributed-fs/ceph-client/arch/sh/kernel/topology.c

Purpose: registers SH CPU topology devices and core-sibling masks.

Important APIs and control flow: per-CPU `cpu_devices` backs sysfs CPU devices. `cpu_coregroup_map()` currently returns all possible CPUs for simple SH-X3-style multicore topology. `cpu_coregroup_mask()` returns `cpu_core_map[cpu]`. `arch_update_cpu_topology()` recomputes core maps. `topology_init()` registers one CPU device per possible CPU, sets core maps, and runs as a `subsys_initcall`.

State, dependencies, and risks: state includes per-CPU `struct cpu` devices and exported `cpu_core_map`. Dependencies include cpu masks, device registration, topology core, and CPU possible map. Risks include oversimplified topology for heterogeneous/non-SH-X3 systems and stale masks after hotplug if updates are incomplete. Test signals are `/sys/devices/system/cpu` topology files, CPU hotplug, and scheduler topology behavior.
