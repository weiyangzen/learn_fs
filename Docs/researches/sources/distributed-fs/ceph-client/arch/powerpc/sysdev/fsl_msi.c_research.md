<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.c

Purpose: Freescale MSI controller driver for MPIC, IPIC, and virtual MPIC MSI blocks, wiring PCI MSI/MSI-X allocation to hardware MSI status registers and cascaded interrupts.

Important APIs/types/functions: platform driver `fsl_of_msi_driver`, probe/remove `fsl_of_msi_probe()`/`fsl_of_msi_remove()`, PCI ops `fsl_setup_msi_irqs()` and `fsl_teardown_msi_irqs()`, message composer `fsl_compose_msi_msg()`, cascade handler `fsl_msi_cascade()`, allocator `fsl_msi_init_allocator()`, hwirq setup `fsl_msi_setup_hwirq()`, irqdomain map `fsl_msi_host_map()`, and feature descriptors for MPIC/IPIC/VMPIC.

Control flow: probe creates a linear MSI irqdomain, maps hardware registers unless using VMPIC hypercalls, computes the MSIIR offset, marks MPIC v2.0 endian erratum, initializes a bitmap with all hwirqs reserved, parses available ranges or v4.3 implicit registers, maps each cascade IRQ, requests cascade handlers, and frees corresponding hwirqs into the bitmap. It then installs MSI setup/teardown ops on all PCI host bridges unless another MSI driver is present. PCI setup rejects plain MSI on PIC1 erratum hardware, honors an `fsl,msi` phandle on the PCI controller, allocates one hwirq per MSI desc, creates a virq, attaches the MSI desc, composes the MSI address/data, and writes it to PCI config. Cascades read MSIR bits from MPIC/IPIC registers or VMPIC hypercall and dispatch each set bit through the MSI irqdomain.

State and persistence: global `msi_head` tracks all MSI banks. Each `fsl_msi` stores irqdomain, register mapping, feature bits, MSIIR shifts/offset, cascade data per MSIR, bitmap allocator, and phandle. PCI devices persist assigned virqs/hwirqs until teardown.

Dependencies and integration points: depends on PCI MSI core, PowerPC PCI controller ops, irqdomain, OF address/IRQ/phandle properties, `msi_bitmap`, MPIC version queries, Freescale hypervisor calls for VMPIC, and `fsl_pci_immrbar_base()` for MSIIR address composition.

Risks: allocator starts fully reserved and only releases ranges with valid cascade IRQs; malformed `msi-available-ranges` disables probe. Error unwind calls remove on partially initialized structures. The MPIC v2.0 endian erratum blocks MSI but allows MSI-X with data byte swapping. Installing ops across all host bridges can conflict with another MSI backend.

Test signals: MSI/MSI-X enablement on FSL PCI devices, `/proc/interrupts` chip names including cascade virqs, range parsing, `fsl,msi` phandle restriction, teardown freeing hwirqs, cascade dispatch from MSIR bits, VMPIC hypercall paths, and erratum behavior validate the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_msi.c -->
