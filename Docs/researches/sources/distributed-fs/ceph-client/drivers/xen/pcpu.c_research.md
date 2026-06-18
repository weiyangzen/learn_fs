# sources/distributed-fs/ceph-client/drivers/xen/pcpu.c

Purpose: exposes Xen physical CPU state to dom0 through the `xen_cpu` bus and sysfs, and handles physical CPU online/offline notifications.

Important APIs/functions: init is `xen_pcpu_init`; VIRQ handling uses `xen_pcpu_interrupt` and `xen_pcpu_work_fn`; CPU synchronization uses `xen_sync_pcpus`, `sync_pcpu`, `create_and_register_pcpu`, and `pcpu_online_status`. ACPI helpers are `xen_processor_present` and `xen_sanitize_proc_cap_bits`.

Control flow: init binds `VIRQ_PCPU_STATE`, registers the `xen_cpu` subsystem, and synchronizes all present physical CPUs by calling `XENPF_get_cpuinfo` from CPU 0 through max-present. New valid CPUs are registered as devices; invalid CPUs are unregistered; online state changes emit KOBJ online/offline uevents. The `online` sysfs attribute calls `XENPF_cpu_online` or `XENPF_cpu_offline` for CAP_SYS_ADMIN writes, but is hidden for CPU0.

State and persistence: a mutex-protected global `xen_pcpus` list stores `struct pcpu` devices with Xen CPU ID, ACPI ID, and flags. Workqueue processing refreshes state after VIRQ delivery. Device release removes list entries and frees memory.

Dependencies and integration: depends on Xen platform ops, event VIRQ binding, Linux device/bus/sysfs, capability checks, and optional ACPI processor integration.

Risks: init failure unwinds the bus and VIRQ binding; registering a device after adding it to the list can leave cleanup dependent on device release; sysfs offlining CPU0 is intentionally blocked; hypervisor state is authoritative and async uevents can race userspace reads.

Test signals: boot dom0, inspect `/sys/bus/xen_cpu/devices`, online/offline nonzero PCPUs through sysfs, trigger `VIRQ_PCPU_STATE`, remove invalid CPUs, test ACPI processor presence filtering, and verify CAP_SYS_ADMIN enforcement.
