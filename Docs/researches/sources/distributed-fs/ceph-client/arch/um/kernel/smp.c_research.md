# sources/distributed-fs/ceph-client/arch/um/kernel/smp.c

## Purpose
Provides UML's kernel-side SMP support: virtual CPU startup, IPI delivery semantics, CPU possible map setup, and cross-CPU call/reschedule operations.

## Important APIs, Types, and Functions
`arch_smp_send_reschedule()`, `arch_send_call_function_single_ipi()`, `arch_send_call_function_ipi_mask()`, and `smp_send_stop()` issue host IPIs. `ipi_handler()` maps UML IPI vectors to scheduler, call-function, and stop handling. `uml_start_secondary()`, `smp_prepare_cpus()`, and `__cpu_up()` coordinate AP boot. `prefill_possible_map()` and `uml_ncpus_setup()` configure CPU counts.

## Control Flow, State, and Persistence
Persistent state includes `uml_ncpus`, `cpu_states[]`, and `cpu_tasks[]`. AP threads wait on a futex until `__cpu_up()` publishes the idle task and marks the CPU runnable, then install stacks/timers and enter idle.

## Dependencies and Integration Points
Pairs with host pthread/signal IPI code in `os-Linux/smp.c`, timer setup in `time.c`, signal stacks, generic SMP call-function code, and scheduler CPU hotplug startup.

## Risks and Test Signals
Risks are AP boot races, missed IPIs, invalid stop behavior, and lack of ptrace-userspace SMP support unless seccomp is used. Test `ncpus=`, SMP boot, call_function stress, scheduler reschedules, CPU stop, and time-travel/SMP interactions.
