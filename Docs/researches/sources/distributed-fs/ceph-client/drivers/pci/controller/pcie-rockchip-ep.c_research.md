# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip-ep.c

Purpose: Implements the Rockchip AXI PCIe endpoint-controller driver for RK3399 endpoint mode. It exposes a `pci_epc` to endpoint-function drivers, manages BAR programming, outbound address translation, MSI/INTx generation, PERST# handling, and link training notification.

Important APIs/types/functions: `struct rockchip_pcie_ep` wraps shared `struct rockchip_pcie`, EPC object, outbound region state, IRQ trigger window, PERST state, and delayed link-training work. It implements `pci_epc_ops`: `write_header`, `set_bar`, `clear_bar`, `align_addr`, `map_addr`, `unmap_addr`, `set_msi`, `get_msi`, `raise_irq`, `start`, `stop`, and `get_features`. Key local helpers include `rockchip_pcie_prog_ep_ob_atu()`, `rockchip_pcie_ep_send_msi_irq()`, `rockchip_pcie_ep_link_training()`, and `rockchip_pcie_ep_hide_broken_msix_cap()`.

Control flow: Probe creates the EPC, parses shared Rockchip DT resources, initializes outbound memory windows, enables clocks, initializes the controller in endpoint mode through common helpers, hides the unsupported MSI-X capability, enables function 0, notifies endpoint core initialization, and optionally requests a PERST# GPIO IRQ. `start()` enables selected functions and begins link training. Link training polls Gen1/link-up state, optionally retrains to Gen2, then calls `pci_epc_linkup()`. PERST assertion cancels training and reports linkdown; deassertion retrains.

State and persistence: Driver state includes the outbound-region bitmap and addresses, reserved IRQ outbound window, current MSI PCI address/function, pending INTx state, PERST/link booleans, and hardware BAR/ATU/config registers. EPC memory windows are allocated through `pci_epc_multi_mem_init()` and persist until endpoint memory exit.

Dependencies/integration: Depends on Linux PCI endpoint core, endpoint-function framework, GPIO IRQs, delayed work, and shared Rockchip helpers/register macros from `pcie-rockchip.c`/`.h`.

Risks: Outbound regions are derived from 1 MiB windows and `rockchip_ob_region(addr)`; misaligned or duplicate mappings return busy or target the wrong region. MSI generation dynamically reprograms a dedicated outbound window and must track function/address changes. Unsupported MSI-X is hidden by editing the capability list; errors can expose unusable MSI-X to the host. PERST and polling paths must avoid reporting linkup after reset.

Test signals: EPC configfs operation, endpoint-function bind/unbind, BAR sizing and host enumeration, MSI and INTx delivery, PERST assert/deassert, Gen1/Gen2 training logs, outbound DMA mapping/unmapping, and RK3399 endpoint DT compatibility.
