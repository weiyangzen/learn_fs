# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4m_smp.c

Purpose: provides sun4m-specific SMP boot, software interrupt IPIs, cross-calls, and per-CPU timer interrupt handling.

Important APIs/types/functions: `sun4m_cpu_pre_online()`, `smp4m_boot_cpus()`, `smp4m_boot_one_cpu()`, `smp4m_smp_done()`, `sun4m_ipi_*()`, `sun4m_cross_call()`, `smp4m_cross_call_irq()`, `smp4m_percpu_timer_interrupt()`, and `sun4m_init_smp()` use `current_set`, `cpu_callin_map`, `smp_penguin_ctable`, `sun4m_irq_percpu`, `ccall_info`, and `cross_call_lock`.

Control flow: boot unblocks profile IRQs, then each CPU is started at a per-CPU trampoline entry and waited on through `cpu_callin_map`. Secondary CPUs swap the call-in bit, flush cache/TLB, load `%g6` from `current_set`, attach `init_mm`, and wait for `smp_commenced_mask`. IPIs are software interrupts at levels 12, 13, and 14 for single, mask, and reschedule; cross-calls use level 15 and a serialized shared call record.

State and persistence: runtime-only cross-call arguments/completion flags and interrupt registers; no persistence.

Dependencies and integration points: integrates with `smp_32.c`, `trampoline_32.S`, PROM `startcpu`, SRMMU context table, sun4m IRQ register mapping, generic SMP call handlers, and per-CPU `sparc32_clockevent`.

Risks: cross-call waits have no timeout and require every targeted CPU to service level-15. `SUN4M_NCPUS` bounds arrays. Secondary startup relies on correct trampoline offset for CPU IDs 1-3.

Test signals: multi-CPU sun4m boot, all IPI classes, cross-call completion, per-CPU periodic/oneshot timers, CPU call-in timeout behavior, and correct active_mm/current thread setup.
