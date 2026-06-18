# sources/distributed-fs/ceph-client/lib/dump_stack.c

## Purpose
Provides the generic `dump_stack()` implementation and shared stack-dump header printing for architectures that do not override it.

## APIs, Types, and Functions
Defines `dump_stack_set_arch_desc()`, `dump_stack_print_info()`, `show_regs_print_info()`, internal `__dump_stack()`, exported `dump_stack_lvl()`, and exported `dump_stack()`. Static state is `dump_stack_arch_desc_str[128]`. Build-ID output is controlled by `CONFIG_STACKTRACE_BUILD_ID`.

## Control Flow
Architectures can set a hardware description string during init. `dump_stack_print_info()` prints CPU, UID, PID, task name, kdump state, taint flags, kernel release/version, preemption model, optional build ID, verbose taint info, optional hardware name, worker info, stop-machine info, and sched-ext info. `__dump_stack()` prints that header and calls `show_stack()`. `dump_stack_lvl()` serializes printk output with `printk_cpu_sync_get_irqsave()` unless the current CPU is already in panic, then calls `__dump_stack()` and releases synchronization. `dump_stack()` uses `KERN_DEFAULT`.

## State and Persistence
The only persistent mutable state is the optional architecture description string. The rest is sampled from current task, credentials, UTS state, taint state, kexec state, and scheduler/debug subsystems at dump time.

## Dependencies and Integration Points
Depends on printk, build ID, scheduler/debug helpers, SMP CPU ID, atomics, kexec, UTS namespace, stop-machine diagnostics, and architecture `show_stack()`. It integrates with WARN/OOPS/debug call sites and architecture-specific stack-dump implementations that reuse `dump_stack_print_info()`.

## Risks and Test Signals
Risks include printk serialization deadlocks during panic, unsafe current-task metadata access in unusual contexts, truncated architecture description, and missing architecture stack output if `show_stack()` is weak or unavailable. Test signals include explicit `dump_stack()` calls, WARN/OOPS paths, panic-time stack dumps, build-ID enabled/disabled builds, and architecture override builds.
