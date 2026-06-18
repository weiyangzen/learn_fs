# sources/distributed-fs/ceph-client/arch/sparc/kernel/process_32.c

Purpose: implements 32-bit SPARC process mechanics: idle hook, halt/restart/poweroff, register/stack dumps, FPU cleanup, thread creation, register-window stack cloning, and wait-channel discovery.

Important APIs/functions: architecture entry points include `arch_cpu_idle()`, `machine_halt()`, `machine_restart()`, `machine_power_off()`, `show_regs()`, `show_stack()`, `exit_thread()`, `flush_thread()`, `copy_thread()`, and `__get_wchan()`. Key helpers are `clone_stackframe()`, external `fpsave()`, and assembly return targets `ret_from_fork` and `ret_from_kernel_thread`. Global state includes `sparc_idle`, `pm_power_off`, `scons_pwroff`, `last_task_used_math`, and `current_set`.

Control flow: idle invokes a platform-provided `sparc_idle` callback when installed. Halt/restart/poweroff route through PROM and AUXIO, with a serial-console poweroff policy gate. `copy_thread()` saves the current FPU state when needed, builds a child stack containing a stack frame plus `pt_regs`, initializes kernel-thread frames separately, copies user frames for normal forks, optionally clones a supplied user stack frame, disables child FPU state on SMP, applies either clone3 or SunOS-style fork return values, and installs `%g7` TLS for `CLONE_SETTLS`. `__get_wchan()` walks saved kernel frames until it finds a non-scheduler return PC.

State and persistence: per-task state lives in `thread_info` and `thread_struct`: `ksp`, `kpc`, `kpsr`, `kwim`, `kregs`, saved FPU registers/queue, and register-window counters. Runtime-only globals track the last FPU owner on UP and power/idle hooks. No filesystem persistence is used.

Dependencies and integration points: integrates with PROM, AUXIO, scheduler fork/return assembly, SPARC PSR/WIM window mechanics, SMP FPU flags, generic reboot/poweroff APIs, stack dumping, and `copy_thread()` callers from generic process creation.

Risks: child stack layout must match assembly return paths. User stack cloning copies variable-sized register-window frames and can fault. FPU ownership differs between UP and SMP, so stale `TIF_USEDFPU` or `last_task_used_math` state can corrupt floating-point context. Poweroff behavior depends on console device type and AUXIO availability.

Test signals: boot/reboot/halt/poweroff on sparc32 systems, fork/clone/kernel-thread creation, clone with alternate stack, FPU-using tasks across fork/exit/exec, SMP FPU disable behavior, stack dump readability, and wait-channel output for sleeping tasks.
