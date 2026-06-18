
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/pci.c

Purpose: mitigates early boot DMA risk by disconnecting non-root, non-VGA PCI devices and disabling bus mastering on PCI bridges before ExitBootServices when requested.

Important APIs/types/functions: exports `efi_pci_disable_bridge_busmaster()`.

Control flow: the function locates all EFI PCI I/O protocol handles, first disconnects drivers for devices behind bus 0 except VGA display controllers, then rescans handles for PCI bridges and clears `PCI_COMMAND_MASTER` in their command registers.

State and persistence behavior: it changes firmware-managed PCI device/bridge state in hardware config space. No software state is retained.

Dependencies and integration points: depends on EFI PCI I/O Protocol, PCI config constants, `disconnect_controller`, and `efi=disable_early_pci_dma` option parsing from helper code.

Risks and test signals: disabling bridges may affect devices firmware still expects, while skipping VGA protects framebuffer but not every display transport. Test signals include systems with PCIe bridges and GOP framebuffer, command register changes, no regression when protocol enumeration fails, and boot with/without the early PCI DMA mitigation option.
