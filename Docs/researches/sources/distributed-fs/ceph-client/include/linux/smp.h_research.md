<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smp.h -->
# sources/distributed-fs/ceph-client/include/linux/smp.h

## Purpose
`smp.h` is the generic symmetric multiprocessing interface. It declares cross-CPU function call primitives, boot/hotplug setup hooks, CPU stop/panic helpers, reschedule IPIs, current CPU accessors, and UP fallbacks.

## Important APIs, Types, and Functions
Key callback types are `smp_call_func_t` and `smp_cond_func_t`. `struct __call_single_data` and `call_single_data_t` wrap `struct __call_single_node`, callback, and info pointer for single-CPU call queues. `CSD_INIT()` and `INIT_CSD()` initialize callback data. Core APIs include `__smp_call_single_queue()`, `smp_call_function_single()`, `smp_call_function_single_async()`, `smp_call_function()`, `smp_call_function_many()`, `smp_call_function_any()`, `on_each_cpu()`, `on_each_cpu_mask()`, `on_each_cpu_cond()`, and `on_each_cpu_cond_mask()`.

Boot and CPU-management APIs include `smp_prepare_boot_cpu()`, `smp_prepare_cpus()`, `__cpu_up()`, `smp_cpus_done()`, `call_function_init()`, `generic_smp_call_function_single_interrupt()`, `setup_nr_cpu_ids()`, `smp_init()`, `get_boot_cpu_id()`, `arch_disable_smp_support()`, thaw hooks, and `smp_setup_processor_id()`. Runtime helpers include `smp_send_stop()`, `smp_send_reschedule()`, `kick_all_cpus_sync()`, `wake_up_all_idle_cpus()`, `cpus_peek_for_pending_ipi()`, `smp_processor_id()`, `get_cpu()`, `put_cpu()`, and CSD debug hooks.

## Control Flow
Cross-CPU call flow packages a callback and argument in call-single data, enqueues it on a target CPU call queue, and uses architecture IPI delivery to make the target flush its queue. `on_each_cpu*()` variants apply this to online CPU masks and optionally wait for completion. Async single calls require caller-managed `call_single_data_t`. Reschedule flow traces the IPI send and delegates to `arch_smp_send_reschedule()`.

Boot flow is split between generic and architecture code: the boot CPU is prepared, secondary CPUs are prepared and brought up through `__cpu_up()`, and finalization runs after all requested CPUs are online. With `CONFIG_SMP` disabled, many operations collapse to local calls or no-ops while retaining API compatibility.

## State and Persistence Behavior
SMP state includes global CPU counts (`total_cpus`, `setup_max_cpus`, `__boot_cpu_id`), CPU online masks from cpumask infrastructure, per-CPU call queues, and call-single data flags defined in `smp_types.h`. `get_cpu()` temporarily disables preemption so the current CPU id remains stable until `put_cpu()`. No disk persistence exists.

## Dependencies and Integration Points
The header depends on errno/types/list/cpumask/init, `smp_types.h`, preemption, compiler annotations, thread info, architecture `asm/smp.h`, and tracing for IPIs. It integrates with scheduler rescheduling, TLB shootdowns, stop-machine/panic paths, CPU hotplug, irq work-compatible call queue nodes, and architecture-specific CPU bringup.

## Risks and Test Signals
Risks include calling waitable cross-CPU functions from interrupt or preemption-invalid contexts, reusing async CSD before completion, deadlocks when target CPUs are offline or stopped, unstable `smp_processor_id()` use without preemption/IRQ protection, and UP/SMP semantic drift. Test signals include lockdep and `CONFIG_DEBUG_PREEMPT` warnings, CSD lock-wait debug reports, CPU hotplug tests, IPI tracing, scheduler selftests, panic/stop path testing, and SMP/UP build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smp.h -->
