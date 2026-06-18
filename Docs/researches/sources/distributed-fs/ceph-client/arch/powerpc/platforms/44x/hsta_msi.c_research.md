<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/hsta_msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/hsta_msi.c

Purpose: provides PCI MSI support for PPC4xx SoCs where High Speed Transfer Assist generates interrupts from writes to 128-bit aligned MMIO addresses.

Important APIs/types/functions: `struct ppc4xx_hsta_msi` stores HSTA MMIO, physical base, MSI bitmap, IRQ map, and count; `hsta_setup_msi_irqs()` allocates bitmap entries, maps each MSI descriptor to a hardware IRQ, and writes MSI messages; `hsta_teardown_msi_irqs()` frees mappings; `hsta_msi_probe()` discovers resources and installs MSI controller ops on all PCI host bridges.

Control flow: subsys init registers a platform driver matching `ibm,hsta-msi`. Probe maps the HSTA memory resource, counts OF IRQs, allocates the MSI bitmap and IRQ map, parses each IRQ, then patches every `pci_controller` in `hose_list` with setup/teardown callbacks. Setup rejects MSI-X, allocates one hwirq per MSI descriptor, computes `address + index * 0x10`, associates the descriptor with the mapped IRQ, and writes an MSI message with zero data.

State and persistence: global singleton `ppc4xx_hsta_msi` persists HSTA state and bitmap allocations. Each MSI descriptor holds its associated Linux IRQ until teardown. HSTA MMIO mapping persists for the platform lifetime.

Dependencies and integration: depends on OF resources/IRQs, `asm/msi_bitmap.h`, PCI host bridge `controller_ops`, Linux MSI descriptors, and platform PCI bridge enumeration occurring before or alongside HSTA probe.

Risks and test signals: partial setup failure after bitmap allocation can leak entries; singleton design assumes one HSTA block; callbacks are assigned only to currently existing hoses; missing IRQ map entries break MSI setup. Test MSI-capable PCI devices on Akebono/compatible hardware, allocation exhaustion, device removal/teardown, MSI-X rejection, and boot ordering with multiple host bridges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/platforms/44x/hsta_msi.c -->
