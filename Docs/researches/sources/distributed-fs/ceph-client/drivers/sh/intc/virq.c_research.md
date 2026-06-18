# sources/distributed-fs/ceph-client/drivers/sh/intc/virq.c

Purpose: virtual IRQ subgroup support for SH INTC. It lets one physical parent IRQ fan out to multiple virtual IRQs based on subgroup status bits.

Important APIs and functions: `intc_irq_xlate_set/get` maintain global IRQ-to-enum translation. `intc_irq_lookup` finds an IRQ by chip name and enum id, deferring subgroup VIRQs until allocated. `intc_subgroup_init` inserts pending subgroup entries into the controller radix tree. `intc_finalize` allocates IRQ descriptors for tagged subgroup entries through `intc_subgroup_map`. `intc_virq_handler` masks/acks the parent, tests each virtual bit, dispatches matching virtual IRQs, then unmasks the parent.

Control flow: controller registration inserts normal mappings and subgroup placeholders. Finalization allocates virtual IRQs, configures them with simple handlers and parent chip data, chains the parent handler, and replaces radix entries with real translation entries. Runtime parent interrupts dispatch to active subgroup virtual descriptors.

State and dependencies: global `intc_irq_xlate[INTC_NR_IRQS]`, per-parent linked lists of virtual IRQs in handler data, controller radix tree tags, and subgroup entries. Dependencies include IRQ allocation, radix trees, raw locks, and access dispatch. Risks include memory allocation under init locks, no duplicate virtual entry leak cleanup, parent handler data ownership, non-threadable VIRQs, and failure when no IRQ descriptors remain. Test signals are subgroup setup logs, successful `intc_irq_lookup` before and after finalize, parent-to-virtual interrupt dispatch, and debugfs mapping rows.
