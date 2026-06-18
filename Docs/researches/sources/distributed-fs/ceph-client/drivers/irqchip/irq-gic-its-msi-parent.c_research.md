# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-its-msi-parent.c

## Purpose
Provides MSI parent operations for GIC ITS domains, covering GICv3 and GICv5 PCI/platform MSI preparation and teardown.

## Important APIs, Types, and Functions
Exports `gic_v3_its_msi_parent_ops` and `gic_v5_its_msi_parent_ops`. Important helpers include `its_translate_frame_address()`, PCI prepare functions, platform MSI info lookup, `its_pmsi_prepare()`, `its_v5_pmsi_prepare()`, `its_msi_teardown()`, and device MSI info initializers.

## Control Flow
MSI domain creation uses parent ops to initialize per-device MSI info. The initializer delegates to `msi_lib_init_dev_msi_info()`, then overrides `msi_prepare` by bus token. Prepare paths compute the ITS DeviceID from PCI RID, DMA alias, OF `msi-parent`, OF `msi-map`, or ACPI IORT; GICv5 paths also obtain a translate-frame physical address. They round vector counts to powers of two, impose minimums where required, then call the real ITS parent prepare op. Teardown delegates to the parent ITS op.

## State and Persistence
The file has no mutable global state. Per-allocation state is passed through `msi_alloc_info_t` scratchpad fields: DeviceID in slot 0 and GICv5 translate-frame PA in slot 1.

## Dependencies and Integration Points
Depends on PCI MSI, OF, ACPI IORT, `irq-msi-lib`, and ITS parent domain ops. It is selected by GIC ITS irqdomains to expose PCI and platform MSI bus domains.

## Risks and Test Signals
Risks include incorrect alias sizing, DevID 0 workaround over-allocation, missing GICv5 `ns-translate` resources, and failure to match OF/ACPI controller nodes. Test signals include PCI MSI/MSI-X allocation on aliased buses, platform MSI DeviceID mapping, GICv5 translate PA propagation, and successful teardown delegation.
