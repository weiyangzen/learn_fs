<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa-regs.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa-regs.h

Purpose: register-definition header for Cadence HPA PCIe controllers. It describes HPA register-bank base offsets, RP config offsets, BAR control encodings, outbound/inbound translation register layouts, PTM, link status, detect-quiet, tag management, and miscellaneous platform fields.

Important APIs/types/functions: macros for HPA banks (`CDNS_PCIE_HPA_IP_REG_BANK`, `CDNS_PCIE_HPA_AXI_SLAVE`, `CDNS_PCIE_HPA_AXI_MASTER`), BAR config (`CDNS_PCIE_HPA_LM_RC_BAR_CFG`, `HPA_LM_RC_BAR_CFG_*`), outbound regions (`CDNS_PCIE_HPA_AT_OB_REGION_*`), inbound RP/EP BAR addresses, link/debug registers (`CDNS_PCIE_HPA_PHY_DBG_STS_REG0`), and control bits like `CDNS_PCIE_HPA_AT_OB_REGION_CTRL0_SUPPLY_BUS`.

Control flow: no runtime flow. These macros are consumed by HPA common and host code to calculate offsets and bitfields for each register write.

State/persistence: no software state is allocated. The definitions encode hardware state layout; changes alter all compiled HPA register programming.

Dependencies/integration: Linux bitfield helpers, PCI BAR numbering, endpoint framework constants, and `pcie-cadence.h` inline HPA accessors. Used by `pcie-cadence-hpa.c`, `pcie-cadence-host-hpa.c`, `pci-sky1.c`, and any HPA platform glue.

Risks: HPA encodings differ from classic Cadence, especially BAR aperture bases, descriptor type fields, and bus/devfn supply controls. Some macros are long single-line expressions and easy to misuse with side effects. Wrong bank offset selection in platform data combined with these relative offsets will silently target the wrong registers.

Test signals: compile coverage, register trace comparison against HPA documentation, outbound MEM/IO/config/message windows, inbound RP and EP BAR maps, PTM response enable, detect-quiet programming, and link-up status read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-hpa-regs.h -->
