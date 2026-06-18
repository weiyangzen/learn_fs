# sources/distributed-fs/ceph-client/arch/sparc/kernel/irq_64.c

## Purpose
`irq_64.c` implements sparc64 IRQ initialization, allocation, interrupt-vector routing, sun4u register-backed IRQ chips, sun4v hypervisor IRQ/VIRQ chips, hard/soft IRQ stacks, PROM timer shutdown, and sun4v mondo queue setup.

## Important APIs, Types, and Functions
Global state includes `ivector_table`, `ivector_table_pa`, `hardirq_stack`, and `softirq_stack`. Public functions include `irq_alloc()`, `irq_free()`, `build_irq()`, `sun4v_build_irq()`, `sun4v_build_virq()`, `handler_irq()`, `do_softirq_own_stack()`, `fixup_irqs()`, `init_irqwork_curcpu()`, `sun4v_register_mondo_queues()`, and `init_IRQ()`. Key types are `struct irq_handler_data`, `struct ino_bucket`, and `struct sun5_timer`.

## Control Flow and State
Boot calls `irq_init_hv()` to negotiate `HV_GRP_INTR`, initializes the ivector table unless using cookie-only VIRQs, maps and disables PROM timers, allocates sun4v mondo/error queues, initializes send-mondo info, registers boot CPU queues, clears pending softints, enables interrupts, and installs a timer action on IRQ0. sun4u `build_irq()` derives INO from IMAP, stores the virtual IRQ in the ivector bucket, and uses `sun4u_irq` callbacks to program IMAP/ICLR. sun4v can either use sysino buckets or cookie-only VIRQ delivery; cookie mode stores an inverted physical pointer to a per-IRQ bucket via the hypervisor. `handler_irq()` atomically grabs and clears the per-CPU irq worklist, switches to hardirq stack, walks bucket chains using bypass ASIs, clears chain pointers, and dispatches generic IRQs.

## Persistence and Dependencies
Persistent state includes IRQ descriptors, handler data, ivector buckets, hypervisor IRQ API version, mondo queue real addresses, PROM timer saved limits, trap-block irq worklists, and stack arrays. Dependencies include hypervisor wrappers, generic IRQ core, Open Firmware, UPA/IMAP registers, Starfire CPU translation, cpumap, trap block, and softirq stack support.

## Integration Points, Risks, and Test Signals
Integration points include PCI/UPA device IRQ construction, LDC/VIO virtual interrupts, SMP IPIs/mondos, CPU hotplug affinity fixups, timer initialization, and trap-vector assembly. Risks include HV IRQ API version ambiguity, cookie/sysino duplicate detection, ivector table sizing for large devhandle/devino systems, bypass/non-bypass coherency, lost bucket chains if `handler_irq()` races, PROM timer side effects, and queue allocation alignment requirements. Test signals are successful IRQ API log, device IRQ delivery and affinity changes, VIRQ cookie interrupts, hotplug `fixup_irqs()`, mondo queue registration on all CPUs, hardirq/softirq stack operation, and no BAD IRQ acknowledgements.
