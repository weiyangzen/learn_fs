# sources/distributed-fs/ceph-client/arch/mips/cobalt/pci.c

Purpose: registers the Cobalt GT64120-backed PCI controller when PCI is enabled.

Important APIs and data: `cobalt_pci_controller` references external `gt64xxx_pci0_ops`, defines PCI memory and I/O resource windows, sets `io_offset`, and maps I/O via `CKSEG1ADDR(GT_DEF_PCI0_IO_BASE)`. `cobalt_pci_init()` registers the controller at `arch_initcall`.

State and integration: controller registration persists in the PCI core. It depends on GT64120 constants and PCI ops supplied elsewhere.

Risks and test signals: I/O offset and resource window mistakes break PCI config/resource assignment. Build with `CONFIG_PCI`; boot should enumerate PCI devices and assign resources inside the configured windows.
