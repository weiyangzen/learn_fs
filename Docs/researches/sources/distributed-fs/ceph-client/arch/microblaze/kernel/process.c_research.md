# sources/distributed-fs/ceph-client/arch/microblaze/kernel/process.c

Purpose: implements process/thread architecture hooks: register dumps, thread creation, exec-thread setup, idle, and minimal FPU core-dump handling.

Important APIs and state: `show_regs()`, exported `pm_power_off`, `flush_thread()`, `copy_thread()`, `__get_wchan()`, `start_thread()`, `elf_core_copy_task_fpregs()`, and `arch_cpu_idle()`.

Control flow: kernel-thread clone initializes empty regs/context, stores function and argument in r20/r19, and returns through `ret_from_kernel_thread`. User clone copies current regs, sets child stack/TLS, adjusts MSR for return-to-user, and returns through `ret_from_fork`. `start_thread()` installs PC/SP and user-mode MSR state for exec.

State and persistence: mutates child `pt_regs` and `thread_info.cpu_context`; `pm_power_off` is global hook state. No allocation.

Dependencies and integration: context fields are restored in `_switch_to` from `entry.S`. Signal/ptrace code consumes `pt_regs` layout.

Risks and test signals: MSR bit composition is delicate for VM/UMS/IE/EIP. `__get_wchan()` is unimplemented. Test fork, clone with TLS, kernel threads, exec, core dumps, and register dumps after exceptions.
