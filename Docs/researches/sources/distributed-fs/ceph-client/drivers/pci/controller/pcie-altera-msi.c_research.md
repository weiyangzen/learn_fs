# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-altera-msi.c

## Purpose
`pcie-altera-msi.c` is the companion MSI controller for Altera PCIe. It maps the MSI CSR and vector slave regions, creates a PCI MSI parent domain, allocates up to the DT-provided vector count, composes per-vector MSI doorbell addresses, and dispatches chained controller interrupts.

## Important APIs, Types, And Functions
`struct altera_msi` stores the vector allocation bitmap, mutex, platform device, inner MSI domain, CSR/vector MMIO bases, vector physical base, vector count, and parent IRQ. `altera_msi_isr()` loops over `MSI_STATUS`, clears each pending vector by dummy-reading the vector slave address, and invokes `generic_handle_domain_irq()`. `altera_irq_domain_alloc()` allocates one vector, installs `altera_msi_bottom_irq_chip`, and sets `MSI_INTMASK`. `altera_compose_msi_msg()` points endpoints at `vector_phy + hwirq * 4`.

## Control Flow, State, And Persistence
Probe maps `"csr"` and `"vector_slave"`, reads `num-vectors`, creates the MSI parent domain, obtains the platform IRQ, and installs a chained handler. Allocation/free updates the `used` bitmap and the hardware interrupt mask. Removal masks all vectors, removes the chained handler, removes the IRQ domain, and clears drvdata. There is no persistent storage or suspend/resume restoration; state is volatile controller registers plus the in-memory bitmap.

## Dependencies, Integration Points, Risks, And Test Signals
The driver binds `"altr,msi-1.0"` and registers at `subsys_initcall`, early enough for host bridge probing. It depends on IRQ domains, `irq-msi-lib`, generic MSI flags, OF resource mapping, and platform IRQs. Risks include trusting `num-vectors` against a fixed 32-bit bitmap and only expecting single-vector allocations. Test MSI/MSI-X endpoints for vector-specific doorbell writes, `MSI_INTMASK` updates on allocation/free, status clearing via vector reads, clean removal, and no unexpected MSI messages.
