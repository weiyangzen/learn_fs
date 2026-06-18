# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-layerscape-ep.c

Purpose: Provides the NXP/Freescale Layerscape endpoint-mode DWC PCIe glue. It initializes the generic endpoint controller, exposes SoC-specific endpoint capabilities, handles link-up/link-down/hot-reset PME-message interrupts, supports big-endian PF LUT registers, and supplies function-specific DBI offsets for multi-function endpoints.

Important APIs and types: `struct ls_pcie_ep` holds the DWC pointer, mutable `pci_epc_features`, matched `ls_pcie_ep_drvdata`, PME IRQ number, saved link capability register, and endian flag. `struct ls_pcie_ep_drvdata` provides the function DBI stride. Important functions are `ls_pcie_ep_event_handler()`, `ls_pcie_ep_interrupt_init()`, `ls_pcie_ep_init()`, `ls_pcie_ep_raise_irq()`, `ls_pcie_ep_get_dbi_offset()`, and `ls_pcie_ep_probe()`.

Control flow: Probe allocates the Layerscape and DWC objects plus a feature structure, maps the `regs` resource as DBI, records endianness, initializes a 64-bit DMA mask, saves the initial PCIe link capability register, calls `dw_pcie_ep_init()` and `dw_pcie_ep_init_registers()`, notifies the endpoint core, then enables the named `pme` IRQ. The PME handler acknowledges all pending PME message status bits, restores `PCI_EXP_LNKCAP` after link-up/hot reset loss, sets PF0 config ready, and calls `dw_pcie_ep_linkup()` or `dw_pcie_ep_linkdown()`. IRQ raising delegates INTx/MSI/MSI-X to the DWC EP helpers, using the MSI-X doorbell variant.

State and persistence: Driver state includes the saved `lnkcap`, detected MSI/MSI-X capability bits copied into `ls_epc`, and DBI offset rules. Hardware state includes PME interrupt enable/status, PF0 config-ready, restored non-sticky link capability fields, endpoint BARs/iATU programmed by the generic EP core, and link-notifier state in the PCI EPC framework.

Dependencies and integration points: Integrates with `pcie-designware-ep.c`, Linux platform/OF resources, PCI endpoint controller framework, and DT compatibles for LS1028A/LS1046A/LS1088A/LS2088A/LX2160A endpoint controllers. The `get_dbi_offset` callback is important for multi-function EPF support.

Risks: PME events are shared IRQs and depend on correct status clearing. Losing or failing to restore `PCI_EXP_LNKCAP` after link-down/hot reset can make the host see wrong speed/width. Feature capabilities are inferred only from function 0 during EP init. Incorrect `func_offset` values silently direct per-function DBI writes to the wrong function. Big-endian access must match hardware register wiring.

Test signals: Build endpoint support, probe each compatible, verify `pme` IRQ registration, link-up/link-down EPF notifications, hot-reset behavior, restored max speed/width in config space, multi-function DBI access on LS2/LX2 offsets, MSI/MSI-X/INTx raising, and big-endian DT operation.
