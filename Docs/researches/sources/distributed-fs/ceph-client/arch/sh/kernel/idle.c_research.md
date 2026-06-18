# sources/distributed-fs/ceph-client/arch/sh/kernel/idle.c

Purpose: supplies SH architecture idle, CPU-dead idle, idle routine selection, and CPU stop helpers.

Important APIs and control flow: `default_idle()` sets the BL bit, enables interrupts, executes `cpu_sleep()`, disables interrupts, and clears BL. `arch_cpu_idle_dead()` delegates to `play_dead()`. `arch_cpu_idle()` calls the selected `sh_idle` routine and then `raw_local_irq_enable()`. `select_idle_routine()` chooses `default_idle` unless another implementation has been installed. `stop_this_cpu()` marks the CPU offline and sleeps forever with interrupts disabled.

State, dependencies, and risks: state is the global idle function pointer and per-CPU online state. Dependencies include BL bit helpers, CPU sleep instruction, SMP hotplug `play_dead()`, and scheduler idle loop expectations. Risks include races around interrupt enable during idle, BL bit misuse affecting exception masking, and stop paths that never return. Test signals are idle loop boot stability, CPU hotplug/offline, and interrupt wake from idle.
