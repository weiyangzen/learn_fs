# sources/distributed-fs/ceph-client/include/linux/soc/ti/ti_sci_inta_msi.h

Purpose: This TI header exposes helpers for configuring MSI through TI SCI-managed Interrupt Aggregator resources.

Important APIs/types/functions: It declares `ti_sci_inta_msi_create_irq_domain(struct fwnode_handle *fwnode, struct msi_domain_info *info, struct irq_domain *parent)` and `ti_sci_inta_msi_domain_alloc_irqs(struct device *dev, struct ti_sci_resource *res)`.

Control flow: IRQ setup creates an MSI domain backed by a parent IRQ domain, then device probe code allocates IRQs using a TI SCI resource range.

State and persistence: MSI event routing and interrupt aggregator resources are managed through TI SCI firmware and hardware aggregator state.

Dependencies and integration: Integrates with TI SCI protocol, IRQ domains, MSI infrastructure, K3 interrupt aggregator, and platform devices.

Risks and test signals: Resource allocation or event mapping errors can lose interrupts. Test MSI allocation/free, IRQ delivery, firmware denial paths, and teardown on probe failure.
