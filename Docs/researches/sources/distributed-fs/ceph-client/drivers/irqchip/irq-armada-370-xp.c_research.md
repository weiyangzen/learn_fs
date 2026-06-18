# sources/distributed-fs/ceph-client/drivers/irqchip/irq-armada-370-xp.c

Purpose: Implements the Marvell Armada 370/XP MPIC, including wired IRQs, per-CPU interrupts, optional IPI doorbells, PCI MSI domains, CPU hotplug reinitialization, cascaded mode, and syscore suspend/resume.

Important APIs/types/functions: `struct mpic`, `mpic_irq_mask()/unmask()`, `mpic_irq_map()`, `mpic_handle_irq()`, `mpic_handle_cascade_irq()`, MSI helpers (`mpic_msi_alloc()`, `mpic_compose_msi_msg()`, `mpic_msi_init()`), IPI helpers (`mpic_ipi_send_mask()`, `mpic_ipi_init()`), CPU hotplug callbacks, `mpic_suspend()/resume()`, and `mpic_of_init()`.

Control flow: Init maps global and per-CPU regions, disables all interrupts, detects parent IRQ presence to choose top-level or cascaded mode, creates a wired IRQ domain, initializes boot CPU masks/perf IRQs, creates an MSI domain when PCI MSI is enabled, and either installs `set_handle_irq()` plus IPI domain or chains to a parent IRQ. Runtime top-level handling reads CPU INTACK repeatedly and dispatches normal, MSI, or IPI sources; cascaded mode scans per-CPU cause bits and source CPU masks.

State and persistence: `mpic_data` stores mapped bases, parent IRQ, wired/IPI/MSI domains, MSI bitmap and doorbell metadata, and saved doorbell mask. Per-CPU mask registers must be restored on CPU hotplug and resume.

Dependencies/integration: Uses OF, ARM exception hooks, irqdomain, MSI library, PCI MSI, SMP IPI APIs, CPU hotplug, syscore PM, and architecture CPU logical maps.

Risks and test signals: Test top-level versus cascaded platforms, per-CPU/global mask split, MSI allocation/free and message CPU encoding, IPI ordering barriers, suspend/resume doorbell restore, CPU hotplug, and IRQs 0/1 special handling.
