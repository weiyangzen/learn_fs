# sources/distributed-fs/ceph-client/arch/alpha/kernel/irq.c

**Purpose:** Contains Alpha generic IRQ accounting, affinity selection, `/proc/interrupts` architecture rows, bad-IRQ reporting, and the common `handle_irq()` bridge into the generic IRQ subsystem.

**Important APIs/types/functions:** Exposes `irq_err_count`, per-CPU `irq_pmi_count`, `ack_bad_irq()`, SMP-only `irq_select_affinity()`, `arch_show_interrupts()`, and `handle_irq()`. It consumes `irq_to_desc()`, `generic_handle_irq_desc()`, `irq_enter()`, and `irq_exit()`.

**Control flow:** Controller-specific device interrupt handlers call `handle_irq(irq)`. It validates the descriptor and range, rate-limits invalid IRQ messages by `MAX_ILLEGAL_IRQS`, enters IRQ context, invokes the generic descriptor handler, and exits IRQ context. `arch_show_interrupts()` prints IPI counts on SMP, performance monitoring interrupt counts, and error count. SMP affinity selection round-robins over possible CPUs allowed by `irq_default_affinity`, unless the chip lacks `irq_set_affinity` or user affinity was recorded.

**State and persistence behavior:** Maintains runtime counters and optional per-IRQ user-affinity flags. No persistent storage. Invalid IRQs increment `irq_err_count`.

**Dependencies and integration points:** Called by `irq_alpha.c` and controller files (`irq_i8259.c`, `irq_pyxis.c`, `irq_srm.c`, platform system files). Integrates with Linux generic IRQ descriptors and procfs interrupt display.

**Risks:** The invalid IRQ condition combines descriptor/range checks in a way that only logs up to a cap; out-of-range values after the cap silently return. Affinity code assumes valid IRQ index for `irq_user_affinity[]`. `generic_handle_irq_desc()` expects the descriptor to be initialized by platform init.

**Test signals:** Trigger valid and invalid IRQs, inspect `/proc/interrupts`, verify `irq_err_count`, exercise SMP affinity-capable chips, and confirm nested IRQ enter/exit accounting under device interrupt load.
