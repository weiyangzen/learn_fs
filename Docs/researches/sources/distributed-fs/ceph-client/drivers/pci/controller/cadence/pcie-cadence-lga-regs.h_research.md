<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-lga-regs.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-lga-regs.h

Purpose: register-definition header for the classic Cadence PCIe local/global architecture. It defines local-management registers, endpoint/root BAR controls, root-port config base, address-translation registers, inbound/outbound window layouts, PTM, link timing, and normal-message encodings.

Important APIs/types/functions: macros for `CDNS_PCIE_LM_*`, root and endpoint BAR config fields, `CDNS_PCIE_RP_BASE`, `CDNS_PCIE_AT_OB_REGION_*`, `CDNS_PCIE_AT_IB_RP_BAR_*`, `CDNS_PCIE_AT_IB_EP_FUNC_BAR_*`, `CDNS_PCIE_LTSSM_CONTROL_CAP`, `CDNS_PCIE_RP_MAX_IB`, `CDNS_PCIE_MAX_OB`, and normal-message routing/code bits.

Control flow: no executable flow. Host, endpoint, and common code use these macros to compose register writes for config cycles, BAR setup, DMA inbound maps, outbound windows, link tuning, and interrupt messages.

State/persistence: no state is stored here. The macros encode persistent hardware register ABI for classic Cadence controllers.

Dependencies/integration: Linux bitfield helpers and PCI BAR numbering. Included by `pcie-cadence.h`, which exposes typed accessors and structures used throughout the Cadence driver family.

Risks: field encodings differ from HPA, including outbound descriptor bits, BAR aperture base, and function BAR grouping. Many macros shift caller arguments directly, so invalid BAR/function/region numbers can generate plausible but wrong offsets. Constants such as `CDNS_PCIE_MAX_OB` and `CDNS_PCIE_RP_MAX_IB` shape allocation and loop bounds in other files.

Test signals: compile coverage, classic Cadence root/endpoint enumeration, register traces for outbound config/MEM/IO/message windows, inbound RP/EP BAR maps, PTM response, detect-quiet programming, and MSI/INTx normal-message offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-lga-regs.h -->
