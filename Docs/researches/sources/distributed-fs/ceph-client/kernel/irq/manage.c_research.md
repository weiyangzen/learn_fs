# sources/distributed-fs/ceph-client/kernel/irq/manage.c

## Purpose
`manage.c` is the main driver-facing genirq management layer. It implements interrupt request/free APIs, enable/disable nesting, synchronization, trigger configuration, SMP affinity and affinity notifications, forced threaded interrupt handling, per-CPU IRQs, NMI setup, wakeup control, vCPU affinity hooks, and irqchip state access.

## Important APIs, types, and functions
Important public APIs include `request_threaded_irq()`, `request_any_context_irq()`, `request_nmi()`, `free_irq()`, `free_nmi()`, `enable_irq()`, `disable_irq()`, `disable_irq_nosync()`, `disable_hardirq()`, `synchronize_irq()`, `synchronize_hardirq()`, `irq_set_irq_wake()`, `irq_set_affinity()`, `irq_force_affinity()`, `irq_set_affinity_notifier()`, `irq_set_vcpu_affinity()`, `request_percpu_irq_affinity()`, `free_percpu_irq()`, `request_percpu_nmi()`, `prepare_percpu_nmi()`, `teardown_percpu_nmi()`, `irq_get_irqchip_state()`, and `irq_set_irqchip_state()`. Core internals are `__setup_irq()`, `__free_irq()`, `irq_thread()`, `irq_finalize_oneshot()`, `irq_do_set_affinity()`, `irq_set_affinity_locked()`, and `__irq_set_trigger()`.

## Control flow
Requesting an IRQ validates flags, allocates an `irqaction`, powers the irqchip, optionally rewrites the handler for forced threading, creates kthreads for threaded actions, serializes setup through `request_mutex`, bus lock, and `desc->lock`, requests chip resources, checks sharing and trigger compatibility, activates the IRQ domain, starts the interrupt unless `NO_AUTOEN`, installs PM accounting, registers proc entries, and waits for threads to become ready. Freeing removes the matching action, updates PM counters, shuts down the line if it was the last action, unregisters proc entries, synchronizes hard and threaded handlers, stops kthreads, deactivates the domain, releases chip resources, and drops module/PM references.

## State and persistence
State is descriptor-local and runtime-only: `desc->action`, depth counters, `istate` bits such as `IRQS_ONESHOT` and `IRQS_NMI`, `threads_active`, `threads_oneshot`, wake depth, affinity masks, pending affinity masks, affinity notifier refs, per-CPU enabled masks, PM suspend counters, and irqchip activation state. Forced threading is controlled by the early `threadirqs` parameter static key.

## Dependencies and integration points
This file depends on irq descriptors, irq domains, irq chips, kthreads, task work, cpumasks, CPU isolation/housekeeping, PM-runtime irqchip hooks, proc registration helpers, `irq_work` redirect synchronization, and architecture/chip callbacks for affinity, wake, NMI setup, resource management, and irqchip state. It is the bridge between device drivers and lower-level interrupt-controller implementations.

## Risks and test signals
Risks include deadlocks from synchronization while holding driver locks, sharing mismatches, unbalanced enable/disable or wake depth, stale oneshot masks, kthread teardown races, affinity updates during CPU hotplug, managed IRQ behavior on isolated/offline CPUs, NMI misuse, irqchip PM/resource leaks on setup failure, and pending move handling. Test signals include shared threaded IRQs, `handler=NULL` oneshot validation, forced `threadirqs`, setup failure rollback at each stage, free while interrupt threads are active, wake enable nesting, trigger mismatch warnings, affinity notifier lifetime, per-CPU IRQ enable/disable on each CPU, NMI request/free, and irqchip state get/set through parent data.
