# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_core.c

Purpose: Main PCI lifecycle and firmware registration module for the Broadcom ThorUltra `bng_en` driver. It identifies BCM57708 devices, enables PCI, maps BARs, allocates devlink/HWRM resources, registers with firmware, configures defaults, initializes netdev/RDMA aux/IRQs, and tears everything down.

Important APIs/functions: `bnge_probe_one()` is the central probe path. It validates non-bridge/MSI-X device, handles kdump FLR, enables PCI, allocates devlink-backed `bnge_dev`, maps BAR0, initializes HWRM, registers with firmware, registers devlink, sets IRQ resource maximum, initializes default aux/net config, maps doorbell BAR, initializes RDMA aux, allocates IRQs, allocates netdev, adds aux device, and saves PCI state. `bnge_remove_one()` reverses this. Firmware setup is split into `bnge_fw_register_dev()`, `bnge_func_qcaps()`, `bnge_func_qrcaps_qcfg()`, and `bnge_fw_unregister_dev()`. PCI helpers handle enable/disable, BAR unmap, doorbell BAR map, and MSI-X table size.

Control flow: Probe uses linear staged initialization with labeled unwinds. Firmware registration gets version/NVM, resets function, sets FW time, queries function and queue capabilities, allocates context memory, registers driver with firmware, then queries resources/config/VNIC caps and sets default RSS hash. Remove deletes aux, frees netdev/IRQs, uninitializes defaults, unregisters devlink and firmware, cleans HWRM, unmaps BARs, frees devlink, and disables PCI.

State/persistence: `bnge_dev` is allocated as devlink private data and stored in PCI drvdata. Persistent state includes BAR mappings, firmware version/capability/resource data, doorbell mapping, IRQ table, default RSS, netdev, aux device, and HWRM resources. Shutdown disables the PCI device and optionally enters D3hot for poweroff.

Dependencies/integration: Uses PCI, devlink, HWRM/resource/netdev/link/aux helpers from sibling files, crash dump handling, MSI-X config, DMA mask, and module PCI driver registration.

Risks/test signals: Probe unwind order is critical because firmware, devlink, netdev, IRQs, aux, BARs, and PCI resources overlap. `dma_set_mask_and_coherent()` return is not checked. Test probe failure injection at each stage, kdump path, MSI-X absent, BAR mapping failure, firmware registration failure, doorbell BAR sizing, remove after partial client registration, shutdown poweroff, and module reload.
