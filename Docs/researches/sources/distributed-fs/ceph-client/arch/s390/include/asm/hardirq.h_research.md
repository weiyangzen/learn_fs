# sources/distributed-fs/ceph-client/arch/s390/include/asm/hardirq.h

Purpose: This header adapts generic hardirq/softirq accounting to s390 lowcore storage.

Important APIs/types/functions: `local_softirq_pending()`, `set_softirq_pending()`, and `or_softirq_pending()` access `get_lowcore()->softirq_pending`; `__ARCH_IRQ_STAT` and `__ARCH_IRQ_EXIT_IRQS_DISABLED` advertise architecture behavior; `ack_bad_irq()` logs unexpected IRQ vectors.

Control flow: Softirq raise and processing code reads or updates the current CPU lowcore field directly. Unexpected IRQ handling emits a critical printk from `ack_bad_irq()`.

State and persistence: Softirq pending bits persist per CPU in lowcore. The header does not allocate state, but it defines the canonical accessors for that lowcore field.

Dependencies and integration points: It depends on `asm/lowcore.h` and integrates with generic hardirq, softirq, and IRQ-exit code.

Risks and test signals: Lowcore access must always refer to the current CPU; wrong prefix/lowcore setup would corrupt softirq state. Tests include IRQ/softirq stress, CPU hotplug, lowcore relocation builds, and bad IRQ injection/logging checks.
