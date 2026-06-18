<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-cpu.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-cpu.c

Purpose: The CPU trigger exposes per-CPU LED triggers for CPU0-CPU7 and an aggregate `cpu` trigger whose brightness reflects the proportion of active CPUs.

Important APIs and state: `struct led_trigger_cpu` is per-CPU state with active flag, name, and trigger pointer. `ledtrig_cpu(enum cpu_led_event ledevt)` is exported for architecture or idle code to signal CPU activity. `trig_cpu_all` is the aggregate trigger. `num_active_cpus` tracks active CPUs atomically. Syscore and CPU hotplug callbacks translate suspend/resume/shutdown/online/down events to trigger events.

Control flow: Init registers the aggregate trigger, registers up to eight per-CPU triggers, registers syscore callbacks, and installs a dynamic CPU hotplug state. `ledtrig_cpu()` updates current CPU active state, adjusts the active count, fires the per-CPU LED full/off, and updates aggregate brightness.

State and persistence: State lives in per-CPU storage and an atomic global. It persists for the lifetime of the built-in trigger and has no module exit path.

Dependencies and integration: It integrates with the LED core, CPU hotplug, syscore suspend/resume, and kernel CPU event callers. It is disabled on PREEMPT_RT by Kconfig.

Risks and test signals: Only CPU0-CPU7 get individual triggers while aggregate covers all present CPUs. Mismatched START/STOP events can skew `num_active_cpus`. Test hotplug online/down, suspend/resume, aggregate brightness on multi-core systems, and no overrun with high `CONFIG_NR_CPUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-cpu.c -->
