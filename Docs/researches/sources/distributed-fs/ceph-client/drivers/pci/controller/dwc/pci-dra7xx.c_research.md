<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-dra7xx.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-dra7xx.c

Purpose: TI DRA7xx DesignWare PCIe wrapper supporting root complex and endpoint modes. It handles TI wrapper registers, PHYs, two-lane configuration, interrupt demux, MSI/INTx handling, endpoint interrupt generation, runtime PM, and platform reset/clock sequencing.

Important APIs/types/functions: `struct dra7xx_pcie`, `struct dra7xx_pcie_of_data`, `dra7xx_pcie_probe()`, `dra7xx_add_pcie_port()`, `dra7xx_add_pcie_ep()`, `dra7xx_pcie_irq_handler()`, `dra7xx_pcie_msi_irq_handler()`, `dra7xx_pcie_init_irq_domain()`, `dra7xx_pcie_enable_phy()`, `dra7xx_pcie_unaligned_memaccess()`, and DWC ops `dw_pcie_ops`, `dra7xx_pcie_host_ops`, `pcie_ep_ops`.

Control flow: probe maps `ti_conf`, fetches clocks/PHYs, configures optional two-lane mode, powers PHYs, enables runtime PM, gets optional reset GPIO, disables LTSSM, writes wrapper device type, applies errata i870 unaligned-access workaround, then initializes host or endpoint. Host mode sets up INTx domain, chained MSI/INTx IRQ, DBI base, and `dw_pcie_host_init()`. EP mode maps endpoint DBI regions, initializes EPC and endpoint registers, and notifies EPC init. Main IRQ logs wrapper events and notifies EP link-up.

State/persistence: state includes PHY array/device links, wrapper base, DWC object, IRQ domain, clock, and mode. Hardware state includes TI wrapper interrupt enables/status, device type, LTSSM bit, PHY power, DWC DBI/ATU state, MSI status, and syscon lane/unaligned-access bits.

Dependencies/integration: DWC host/EP core, PHY framework, TI PIPE3, syscon/regmap, GPIO, IRQ domains/chained IRQs, endpoint framework, runtime PM, and DT compatibles for DRA7, DRA746, and DRA726 RC/EP variants.

Risks: MSI IRQ handling loops up to 1000 times to drain status, so interrupt floods can still stress the system. The MSI wrapper switch handles exact status values; simultaneous MSI and INTx bits may not match a single case. Some error paths after PHY/link creation do not delete all device links. Two-lane configuration failure silently falls back to x1.

Test signals: RC enumeration, EP function tests, INTx domain mapping, MSI storm handling, wrapper event logging, two-lane and fallback operation, errata i870 syscon update, suspend/resume PHY cycling and MSE restore, shutdown link stop, and endpoint MSI/INTx raise behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-dra7xx.c -->
