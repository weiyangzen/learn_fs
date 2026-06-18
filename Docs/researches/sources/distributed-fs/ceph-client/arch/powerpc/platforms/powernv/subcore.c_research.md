## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/subcore.c

### Purpose
`subcore.c` controls POWER8 dynamic subcore split mode and exposes `/sys/devices/system/cpu/subcores_per_core`.

### Important APIs, Types, And Functions
It maintains `subcores_per_core`, `new_split_mode`, `cpu_offline_mask`, and per-CPU `struct split_state`. Important functions are `unsplit_core()`, `split_core()`, `cpu_do_split()`, `cpu_core_split_required()`, `update_subcore_sibling_mask()`, `cpu_update_split_mode()`, `set_subcores_per_core()`, sysfs show/store handlers, and `subcore_init()`.

### Control Flow
Mode changes run under `stop_machine_cpuslocked()`. The master CPU publishes `new_split_mode`, wakes offline CPUs, and all CPUs first unsplit if needed. Nonzero threads nap for unsplit or enter the real-mode assembly loop for split; thread 0 updates HID0 and SLW state, waits for hardware mode bits, then the master updates global topology and PACA sibling masks.

### State, Persistence, And Dependencies
State persists in global split mode variables, per-CPU sync bytes, `threads_per_subcore`, and PACA sibling masks. SLW HID0 patches persist for idle/winkle wakeups. Dependencies include OPAL SLW calls, cpuidle supported-state queries, KVM HV mode checks, CPU topology helpers, and stop-machine.

### Integration Points
SMP offline loops call `cpu_core_split_required()` so offline CPUs can participate. Sysfs provides runtime control, and `subcore_init()` installs the attribute only on supported POWER8-family PVRs.

### Risks
All threads in a core must be present; partial CPU limits disable the feature. Split changes are rejected while KVM HV mode is active. Missing barriers or failed offline wakeups can deadlock stop-machine.

### Test Signals
Sysfs writes of `1`, `2`, and `4`, unsupported PVR no-op behavior, KVM-active rejection, CPU hotplug during split, and sibling-mask/topology validation are useful signals.
