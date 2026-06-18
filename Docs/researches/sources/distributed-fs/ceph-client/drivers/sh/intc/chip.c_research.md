# sources/distributed-fs/ceph-client/drivers/sh/intc/chip.c

Purpose: Linux `irq_chip` implementation for SH INTC interrupts. It translates generic IRQ mask/unmask/type/affinity calls into encoded INTC register operations.

Important APIs and functions: `_intc_enable` iterates per-CPU enable registers and applies `intc_enable_fns`, then enables balancing. `intc_disable` disables balancing and writes disable handles. `intc_mask_ack` masks then clears an ack bit for controllers with ack registers. `intc_set_priority` updates per-IRQ priority and optional secondary priority handles. `intc_set_type` writes sense register fields using `intc_irq_sense_table`. `intc_irq_chip` exports mask, unmask, enable, disable, mask_ack, set_type, and optional set_affinity.

Control flow: controller registration installs `intc_irq_chip` on each IRQ with a primary handle in chip data. Generic IRQ core later invokes these callbacks for interrupt lifecycle operations. Secondary handles are enabled during registration for combined mask/priority controllers.

State and dependencies: uses descriptor lookup through chip container, per-IRQ priority array in core, prio/sense handle lists, affinity masks, and optional balancing. Risks include invalid sense type for narrow fields, priority range validation, cpumask interactions with SMP register banks, raw ack mask inversion width, and `BUG()` on unexpected handle function. Test signals are IRQ delivery after unmask, masking and ack clearing, trigger-type programming, priority syscalls/platform code, and SMP affinity behavior.
