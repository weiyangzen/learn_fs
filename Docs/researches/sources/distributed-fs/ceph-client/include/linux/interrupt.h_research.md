# sources/distributed-fs/ceph-client/include/linux/interrupt.h

Purpose: This header is the kernel IRQ, softirq, and tasklet API surface. It defines IRQ trigger and handling flags, the `irq_handler_t` callback shape, `struct irqaction`, IRQ request/free helpers, affinity descriptors, softirq vectors, and deprecated tasklet scheduling primitives.

Important APIs, types, and functions: Drivers use `request_irq`, `request_threaded_irq`, `request_any_context_irq`, `request_percpu_irq`, `request_nmi`, `free_irq`, `disable_irq*`, `enable_irq*`, `irq_wake_thread`, and wake controls. SMP builds expose `irq_set_affinity`, affinity hints, notifier registration, and generated affinity masks. Softirq users rely on `open_softirq`, `raise_softirq`, `raise_timer_softirq`, `do_softirq`, and per-CPU `ksoftirqd`/`ktimerd`. Tasklets expose `tasklet_setup`, schedule, disable/enable, and kill helpers.

Control flow: Request helpers register action records with hardirq and optional threaded handlers; inline wrappers add `IRQF_COND_ONESHOT`. Disable/enable calls gate delivery and provide lockdep-specific variants. Softirq state is raised per CPU and later drained by interrupt return paths, ksoftirqd, or ktimerd under forced threading. Tasklet scheduling sets state bits and queues execution once until it runs or is rescheduled.

State and persistence: IRQ action chains persist until freed. Affinity notifiers use `kref` and workqueue release. Softirq pending bits live in per-CPU irq stats. Tasklets persist in caller-owned storage with atomic disable counts and state bits.

Dependencies and integration points: Integrates with arch IRQ entry code, procfs interrupt reporting, power suspend/resume, lockdep, PREEMPT_RT forced threading, workqueues, cpumasks, hrtimers, and resource trigger flags from `ioport.h`.

Risks: Mismatched `dev_id` on shared IRQ free, using sleeping operations in hardirq context, incorrect oneshot flags for threaded handlers, affinity assumptions on non-SMP builds, tasklet lifetime races, and PREEMPT_RT behavior differences. Tasklets are explicitly deprecated for new code.

Test signals: IRQ request/free paths should be tested with shared and threaded handlers, suspend/resume wake behavior, CPU affinity changes and notifier release, softirq raising under forced threading, tasklet disable/kill races, and !SMP/!PROC/!GENERIC_IRQ_PROBE compile configurations.
