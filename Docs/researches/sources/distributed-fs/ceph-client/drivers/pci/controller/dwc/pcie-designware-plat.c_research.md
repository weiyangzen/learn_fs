# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-designware-plat.c

Purpose: Provides a minimal generic Synopsys DesignWare PCIe platform driver for DT compatibles `snps,dw-pcie` and `snps,dw-pcie-ep`. It wires generic DWC host or endpoint initialization when no SoC-specific glue is needed.

Important APIs and types: `struct dw_plat_pcie` stores the DWC pointer and selected mode. `struct dw_plat_pcie_of_data` stores match mode. Main functions are `dw_plat_add_pcie_port()`, `dw_plat_pcie_ep_raise_irq()`, `dw_plat_pcie_get_features()`, and `dw_plat_pcie_probe()`. Endpoint features use `DWC_EPC_COMMON_FEATURES` with MSI and MSI-X capable.

Control flow: Probe matches RC or EP mode, allocates `dw_plat_pcie` and `dw_pcie`, stores platform driver data, then dispatches. RC mode requires `CONFIG_PCIE_DW_PLAT_HOST`, gets platform IRQ index 1, sets `MAX_MSI_IRQS`, installs empty host ops, and calls `dw_pcie_host_init()`. EP mode requires `CONFIG_PCIE_DW_PLAT_EP`, installs endpoint ops, calls `dw_pcie_ep_init()`, initializes EP registers, and notifies EPC clients.

State and persistence: The file itself has minimal state. Persistent hardware state is entirely established by the generic DWC host/EP core: resources, iATU windows, MSI, BARs, link, endpoint memory, eDMA, and debugfs.

Dependencies and integration points: Directly depends on DWC host/endpoint core, Linux platform/OF APIs, endpoint controller framework, and the IRQ numbering convention for generic host mode. It is a baseline integration point for simple DWC hardware.

Risks: The generic driver has no clocks/resets/PHY sequencing unless the common core `REQ_RES` capability is set by another path, so it is only safe for platforms that need no extra glue. Host IRQ index 1 is a binding contract. EP error handling deinitializes on register-init failure but still calls `pci_epc_init_notify()` after that block in current control flow, which should be validated against the exact return path behavior.

Test signals: Probe both compatibles under matching Kconfig, host enumeration and MSI delivery with IRQ index 1, EP BAR/MSI/MSI-X operations, failed EP register initialization behavior, endpoint start/stop, and absence of platform-specific resource needs.
