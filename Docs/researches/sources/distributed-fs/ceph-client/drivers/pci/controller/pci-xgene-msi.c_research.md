# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-xgene-msi.c

## Purpose
`pci-xgene-msi.c` implements the APM X-Gene v1 PCIe MSI controller. It exposes a PCI MSI parent domain backed by 16 MSI termination frames, statically partitions frame targeting across CPUs, composes endpoint MSI messages, and chains per-frame GIC interrupts into Linux MSI IRQs.

## Important APIs, Types, And Functions
`struct xgene_msi` stores the MSI IRQ domain, physical MSI register base, mapped registers, allocation bitmap, bitmap mutex, and 16 GIC IRQs. `xgene_allocate_domains()` creates the MSI parent irq domain using `xgene_msi_domain_ops` and `xgene_msi_parent_ops`. `xgene_irq_domain_alloc()` allocates one vector from `NR_MSI_VEC`, installs `xgene_msi_bottom_irq_chip`, and enables resend behavior. `xgene_compose_msi_msg()` selects a target frame from effective CPU affinity. `xgene_msi_isr()` reads `MSIINTn`, then read-to-clear `MSInIRx`, computes hwirqs, and dispatches `generic_handle_domain_irq()`.

## Control Flow, State, And Persistence
Probe allocates a single global `xgene_msi_ctrl`, maps the MSI register region, records its physical start as the endpoint doorbell base, initializes the bitmap, creates the domain, clears stale read-to-clear state, obtains 16 platform IRQs, pins each GIC IRQ to a CPU modulo `num_possible_cpus()`, and installs chained handlers. Runtime state is the allocation bitmap and GIC IRQ table. There is no persistent state and no PM restoration path in this file.

## Dependencies, Integration Points, Risks, And Test Signals
The MSI host matches `"apm,xgene1-msi"` and is checked by `pci-xgene.c` before root complex probing. It depends on IRQ domains, generic MSI library, chained IRQ helpers, CPU affinity APIs, OF PCI, and platform IRQ resources. Risks include reduced vector capacity from congruent CPU reservation, CPU-count assumptions in frame composition, single global instance state, and read-to-clear ordering. Test MSI domain discovery, stale IRQ clearing, MSI/MSI-X delivery on multiple CPUs, affinity changes causing regenerated MSI messages, and no unexpected MSI/WARN reports under load.
