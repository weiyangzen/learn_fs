<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu.h

## Purpose

`cpu.h` is the generic CPU device, topology, hotplug, idle, suspend, and CPU mitigation interface. It exposes the `devices/system/cpu` model, architecture hooks, sysfs vulnerability reporting hooks, and common wrappers around CPU bringup/offline and idle entry. The source was read as a complete 236-line file.

## Important APIs, Types, and Functions

`struct cpu` stores `node_id`, `hotpluggable`, and an embedded `struct device`. Registration and lookup APIs include `register_cpu()`, `unregister_cpu()`, `get_cpu_device()`, `cpu_device_create()`, `arch_register_cpu()`, `arch_unregister_cpu()`, `arch_cpu_is_hotpluggable()`, and OF physical-ID matching helpers. Sysfs integration uses `cpu_add_dev_attr()`, `cpu_remove_dev_attr()`, group variants, and many `cpu_show_*()` vulnerability reporters. Hotplug and suspend APIs include `add_cpu()`, `remove_cpu()` through `cpuhplock.h`, `cpu_device_up()`, `notify_cpu_starting()`, `cpu_maps_update_begin()`, `cpu_maps_update_done()`, `freeze_secondary_cpus()`, `thaw_secondary_cpus()`, and `suspend_disable_secondary_cpus()`. Idle and mitigation APIs include `cpu_startup_entry()`, `cpu_idle_poll_ctrl()`, `arch_cpu_idle*()`, `play_idle_precise()`, `cpuhp_report_idle_dead()`, `enum cpu_attack_vectors`, and `enum smt_mitigations`.

## Control Flow

CPU boot starts through boot/init hooks, then CPU devices are registered and exported. Online/offline paths pass through CPU hotplug states and map-update locks. Suspend paths freeze secondary CPUs and thaw them later. Idle flow enters `cpu_startup_entry()`, calls architecture idle hooks, and may report dead idle for hotplug teardown.

## State and Persistence Behavior

Persistent kernel state is external: per-CPU `cpu_devices`, CPU bus objects, CPU masks, hotplug task-freeze state, and mitigation mode. This header declares and gates access; it does not allocate storage.

## Dependencies and Integration Points

It includes `node.h`, `compiler.h`, `cpuhotplug.h`, `cpuhplock.h`, and `cpu_smt.h`. It integrates with driver core sysfs, architecture CPU discovery, SMP/hotplug, PM sleep, scheduler idle, tick broadcast, security mitigation reporting, and architecture `prctl` controls for branch landing pad state.

## Risks and Edge Cases

Misusing hotplug locks can race CPU masks and device registration. Sysfs vulnerability reporters must remain aligned with mitigation state. Non-SMP and !HOTPLUG builds intentionally compile many APIs to no-ops, so callers must tolerate success without real CPU changes. Suspend code must respect the optional nonzero primary CPU configuration.

## Test Signals

Signals include CPU online/offline stress, sysfs CPU device and vulnerability attribute checks, suspend/resume with secondary CPU freeze, non-SMP and !HOTPLUG builds, architecture CPU ID matching tests, and idle/dead CPU hotplug teardown coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu.h -->
