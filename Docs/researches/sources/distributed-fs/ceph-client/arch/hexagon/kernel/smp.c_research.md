# sources/distributed-fs/ceph-client/arch/hexagon/kernel/smp.c

## Purpose

`smp.c` implements Hexagon SMP bring-up and IPI delivery. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs include `send_ipi`, `handle_ipi`, `start_secondary`, `__cpu_up`, `smp_prepare_cpus`, `arch_smp_send_reschedule`, and call-function IPI helpers. Concrete declarations observed in the file: Includes: `linux/err.h`, `linux/errno.h`, `linux/kernel.h`, `linux/init.h`, `linux/interrupt.h`, `linux/module.h`, `linux/percpu.h`, `linux/sched/mm.h`, `linux/smp.h`, `linux/spinlock.h`, `linux/cpu.h`, `linux/mm_types.h`, `asm/time.h`, `asm/hexagon_vm.h`. Macros: `BASE_IPI_IRQ`. Types referenced or declared: `ipi_data`, `cpumask`, `ipi_message_type`, `task_struct`, `thread_info`. Functions/syscalls: `__handle_ipi`, `smp_vm_unmask_irq`, `handle_ipi`, `send_ipi`, `start_secondary`, `__cpu_up`, `smp_cpus_done`, `arch_smp_send_reschedule`, `smp_send_stop`, `arch_send_call_function_single_ipi`, `arch_send_call_function_ipi_mask`, `smp_start_cpus`.

## Control Flow, State, And Persistence

Boot CPU marks possible/present CPUs, starts secondary CPUs with `__vmstart`, installs per-CPU IPI IRQs, and runtime IPI handling drains per-CPU bitmaps for timer, call-function, stop, and reschedule messages.

## Dependencies And Integration Points

It depends on generic SMP/cpumask APIs, scheduler IPIs, timer broadcast, and HVM interrupt posting.

## Risks And Test Signals

Risks are IPI races, wrong BASE_IPI_IRQ mapping, secondary stack/thread-info corruption, and CPU stop hangs. Test signals are SMP boot, CPU hotplug, reschedule/call-function stress, and timer IPI behavior.
 A local static signal for this file is that it has 246 lines and 4983 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
