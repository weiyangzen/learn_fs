# sources/distributed-fs/ceph-client/drivers/xen/cpu_hotplug.c

## Purpose
`cpu_hotplug.c` watches Xenstore CPU availability and mirrors Xen vCPU online/offline state into Linux CPU present/hotplug state.

## Important APIs, types, and functions
Important functions are `enable_hotplug_cpu`, `disable_hotplug_cpu`, `vcpu_online`, `vcpu_hotplug`, `handle_vcpu_hotplug_event`, `setup_cpu_watcher`, and `setup_vcpu_hotplug_event`.

## Control flow
A late initcall registers a Xenstore notifier for PV/PVH-capable Xen domains. When Xenstore is available, it registers a watch on `cpu`, then scans possible CPUs. For each `cpu/N/availability`, `"online"` registers/presents the CPU if needed, while `"offline"` offlines the device under the hotplug lock, unregisters Xen arch CPU state, and clears present. Watch callbacks parse the CPU number from the changed path and reapply the state.

## State and persistence
State is Linux CPU present/online state plus Xen arch CPU registration. The watch object is static. Xenstore availability is external persistent configuration for the domain.

## Dependencies and integration points
It depends on Xenstore watches/notifiers, CPU hotplug/device APIs, `xen_arch_register_cpu`, `xen_arch_unregister_cpu`, and Xen domain type checks.

## Risks and test signals
Risks include parsing unexpected Xenstore paths, ignored registration errors, races with normal CPU hotplug, initial-domain read failures, and policy differences between x86 PV/PVH and other Xen domains. Test signals include Xenstore CPU online/offline changes, CPUs outside `nr_cpu_ids`, non-hotpluggable CPUs, device_offline failures, Xenstore unavailable at init, and domain-type matrix builds.
