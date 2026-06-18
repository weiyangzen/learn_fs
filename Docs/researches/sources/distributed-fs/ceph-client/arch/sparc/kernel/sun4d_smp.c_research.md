# sources/distributed-fs/ceph-client/arch/sparc/kernel/sun4d_smp.c

Purpose: supplies sun4d-specific SMP boot, IPI, cross-call, and per-CPU timer handling for the generic sparc32 SMP layer.

Important APIs/types/functions: `sun4d_cpu_pre_starting()`, `sun4d_cpu_pre_online()`, `smp4d_boot_cpus()`, `smp4d_boot_one_cpu()`, `smp4d_smp_done()`, `sun4d_ipi_interrupt()`, `smp4d_cross_call_irq()`, `smp4d_percpu_timer_interrupt()`, and `sun4d_init_smp()` use `cpu_callin_map`, `current_set`, `smp_penguin_ctable`, `sun4d_ipi_work`, `ccall_info`, `cross_call_lock`, LED state, and `sun4d_imsk_lock`.

Control flow: secondary startup lights LEDs, enables level-15 and blocks level-14, swaps its call-in bit, waits for `current_set` and CPU assignment, installs `%g6`, attaches `init_mm`, waits for `smp_commenced_mask`, then enables PIL14. Boot starts PROM CPUs at `sun4d_cpu_startup` and waits for call-in. IPI senders set per-CPU work flags and generate controller messages; the interrupt drains single-call, mask-call, and reschedule work. Cross-calls serialize through `ccall_info`, fire level-15 IPIs, and spin until all targets enter/exit.

State and persistence: runtime-only per-CPU IPI flags, cross-call arguments, LED values, CPU list rotation, and readiness flags.

Dependencies and integration points: uses sun4d bootbus/controller registers, PROM startcpu, SRMMU context table, generic SMP call functions, clockevents, timer profile IRQs, and IRQ trap table patching.

Risks: cross-call spin waits have no timeout. Shared `ccall_info` requires strict serialization. Secondary boot depends on cache/TLB flushes and correct `current_set` visibility. IRQ levels 14/15 are overloaded for timers/IPIs.

Test signals: secondary CPU boot, LED/progress changes, call-function/reschedule IPIs, cross-call completion on all CPUs, per-CPU timer events, and IRQ distribution after `smp4d_smp_done()`.
