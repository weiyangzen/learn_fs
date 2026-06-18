## sources/distributed-fs/ceph-client/arch/s390/kernel/topology.c

Purpose: Converts s390 hardware topology and polarization information into scheduler topology masks, CPU sysfs attributes, hiperdispatch state, and sysctl/sysfs controls.

Important APIs and functions: `topology_init_early()`, `arch_update_cpu_topology()`, `update_cpu_masks()`, `store_topology()`, `topology_schedule_update()`, `topology_expect_change()`, `topology_cpu_init()`, `cpu_coregroup_mask()`, `topology_set_cpu_management()`, and sysctl handlers for `s390/topology` and `s390/polarization`.

Control flow: Early init chooses hardware, package, or single topology mode, allocates mask linked lists based on STSI magnitudes, stores STSI 15.1.x data, detects polarization, seeds CPU 0 setup, and updates scheduler masks. Updates parse topology entries into drawer/book/socket masks, set per-CPU IDs, polarization, capacity, thread/core/book/drawer masks, booted-core counts, and hiperdispatch core state. A timer polls PTF change indications, schedules rebuilds, and uses a faster polling window after expected configuration changes.

State and persistence: Owns `topology_mode`, `cpu_management`, `tl_info`, linked lists of socket/book/drawer `mask_info`, exported `cpu_topology[]`, a deferrable timer, work item, and polling counter. State changes are protected by `smp_cpu_state_mutex` and scheduler-domain synchronization.

Dependencies and integration: Uses STSI topology blocks, PTF horizontal/vertical/check operations, s390 SMP CPU address lookup, CPU hotplug setup mask, scheduler topology levels, sysfs CPU devices, sysctl, and hiperdispatch helpers.

Risks and test signals: Risks include malformed topology entries, stale masks after CPU hotplug/configure, mismatch between hardware topology and scheduler domains, and polarization changes racing with CPU state changes. Test signals include `/sys/devices/system/cpu/dispatching`, per-CPU `polarization` and `dedicated`, sysctl toggles, scheduler-domain rebuilds, STSI topology debug output, and hotplug/configure events triggering `topology_expect_change()`.
