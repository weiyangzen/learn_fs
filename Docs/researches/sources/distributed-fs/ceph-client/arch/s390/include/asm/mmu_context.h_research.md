# sources/distributed-fs/ceph-client/arch/s390/include/asm/mmu_context.h

Purpose: This header implements s390 MM context initialization and switch operations, including ASCE setup, lowcore ASCE fields, CPU attach masks, and delayed TLB flush synchronization.

Important APIs/types/functions: `init_new_context()`, `switch_mm_irqs_off()`, `switch_mm()`, `finish_arch_post_lock_switch()`, and `activate_mm()` are the architecture overrides.

Control flow: New contexts initialize locks, gmap state, flush counters, protected/COW flags, determine 3/4/5-level ASCE type from `asce_limit`, build `mm->context.asce`, and initialize the top table. Switch paths update lowcore user ASCE, attach CPU masks, clear CR1/CR7 to invalid ASCEs, wait for pending flushes, lazily flush TLBs, then reload CR1/CR7 according to thread flags.

State and persistence: Persistent state is in `mm->context`, `mm_cpumask`, lowcore `user_asce`/`kernel_asce`, and control registers. The code carefully transitions CR1/CR7 with interrupts disabled.

Dependencies and integration points: It depends on `pgalloc.h`, uaccess, TLB flush, control-register load helpers, ASCE definitions, lowcore, scheduler MM hooks, and KVM context fields.

Risks and test signals: Races in CPU masks or flush counters can leave stale translations active. Tests should cover fork/exec, 3-to-5-level ASCE upgrades, context-switch stress, TLB shootdowns, `TIF_ASCE_PRIMARY`, KVM protected contexts, and CPU hotplug.
