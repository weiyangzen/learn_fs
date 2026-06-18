# sources/distributed-fs/ceph-client/arch/sparc/kernel/process_64.c

Purpose: implements 64-bit SPARC process mechanics: sun4u/sun4v idle behavior, CPU hotplug death, register diagnostics, sysrq global CPU/PMU snapshots, thread exit/flush, user register-window synchronization, thread cloning, ADI task duplication, and wait-channel walking.

Important APIs/functions: key exported hooks are `arch_cpu_idle()`, `arch_cpu_idle_dead()`, `show_regs()`, `arch_trigger_cpumask_backtrace()`, `exit_thread()`, `flush_thread()`, `synchronize_user_stack()`, `fault_in_user_windows()`, `copy_thread()`, `arch_dup_task_struct()`, and `__get_wchan()`. Diagnostic helpers include `__global_reg_self()`, `pmu_snapshot_all_cpus()`, and sysrq registrations for global registers and PMU counters.

Control flow: idle either touches the NMI watchdog on non-hypervisor systems or enters a sun4v yield with interrupts carefully toggled and scheduler-poke handling. Register dumps flush windows and print native or compat windows. `synchronize_user_stack()` flushes user windows and copies buffered windows to user stacks, compacting the buffer after successful writes; `fault_in_user_windows()` performs the stricter return-to-user path and signals `SIGBUS` or `SIGSEGV` on bad windows. `copy_thread()` constructs the child trap frame, handles kernel threads, adjusts 32-bit stack values, clones alternate stack frames for user clone, bumps shared user trap table references, applies clone3 versus SunOS return conventions, and sets `%g7` TLS. `arch_dup_task_struct()` samples ADI `%mcdper` so lazy per-task MCDPER state is inherited correctly.

State and persistence: owns runtime per-thread state in `thread_info`: saved windows, window stack pointers, FPU saved flags/registers, utrap reference table, child trap frame, CWP byte, and ADI-related flags. Global diagnostics use `global_cpu_snapshot` and a spinlock only while dumping. No durable storage is written.

Dependencies and integration points: depends on sun4v hypervisor calls, scheduler and CPU hotplug, SPARC V9 register-window ABI, `kstack_valid()`, FPU/VIS helpers, ADI capability checks, PMU PCR operations, SMP cross-calls, sysrq, context tracking, and generic fork/clone entry points.

Risks: return-to-user correctness hinges on flushing register windows without racing signal/reschedule work. Stack-bias and 32-bit stack detection are easy to break. Utrap reference counts must not leak or be freed too early. Sysrq snapshots intentionally avoid hard synchronization, so consumers must tolerate missing or stale CPU entries. ADI MCDPER lazy state must be updated before copying a task.

Test signals: native and compat clone/fork/TLS tests, register-window fault injection, signal delivery with pending windows, sun4v idle/poke behavior, CPU hotplug offline, sysrq `y` and `x` dumps on SMP, ADI-enabled task duplication, and wait-channel reporting under deep kernel stacks.
