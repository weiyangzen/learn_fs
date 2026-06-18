# sources/distributed-fs/ceph-client/drivers/pci/endpoint/functions/pci-epf-mhi.c

## Purpose
Implements a PCI endpoint function for MHI endpoint devices, primarily Qualcomm platforms. It presents PCI IDs and BAR/MSI resources to the host, wires endpoint controller address mapping and interrupt callbacks into the MHI EP core, and optionally uses DMAengine for larger transfers.

## Important APIs, Types, And Functions
Key types are `struct pci_epf_mhi`, `struct pci_epf_mhi_ep_info`, and `struct pci_epf_mhi_dma_transfer`. Platform descriptors cover SDX55, SM8450, and SA8775P. Important functions include `pci_epf_mhi_bind()`, `pci_epf_mhi_epc_init()`, `pci_epf_mhi_link_up()`, `pci_epf_mhi_bus_master_enable()`, `pci_epf_mhi_alloc_map()`, `pci_epf_mhi_iatu_read/write()`, DMA sync/async helpers, and `pci_epf_mhi_unbind()`.

## Control Flow
Probe stores platform info and event ops. Bind maps the endpoint controller `mmio` resource and doorbell IRQ. EPC init sets BAR0, MSI count, config header, EPC features, and optional DMA channels. On link up, the driver fills `mhi_ep_cntrl` callbacks and registers the MHI endpoint controller. Bus-master-enable powers up MHI when the host enables bus mastering. Link down, EPC deinit, and unbind power down/unregister MHI and clear resources.

## State And Persistence
State persists in `pci_epf_mhi`: MMIO mapping/physical address, BAR size, endpoint function pointer, MHI controller, DMA channels/workqueue/list, lock, and endpoint feature pointer. MHI runtime state is owned by the MHI EP core after registration.

## Dependencies And Integration Points
Depends on PCI endpoint core/EPC APIs, MHI EP core, platform resources named `mmio` and `doorbell`, DMAengine for DMA-capable variants, and Qualcomm PCI vendor/device identities.

## Risks
DMA init/deinit is called from several failure paths and must not double-release channels. Async DMA stores copied buffer metadata and assumes callback lifetime remains valid. iATU mapping uses alignment offsets from EPC features. MHI power-up depends on host bus mastering events.

## Test Signals
Test configfs creation for each EPF name, host enumeration with expected PCI IDs/MSI count, MHI channel bring-up, doorbell IRQ delivery, small iATU transfers, large DMA transfers and timeouts, async callback cleanup, link down/up cycles, and unbind/rebind.
