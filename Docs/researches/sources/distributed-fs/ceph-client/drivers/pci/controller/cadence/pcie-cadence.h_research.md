<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.h

Purpose: central internal interface for the Cadence PCIe driver family. It defines common RC/EP/platform structures, register bank abstractions, read/write helpers, config-space access helpers, link operation wrappers, and prototypes for classic and HPA host/endpoint/common helpers.

Important APIs/types/functions: `enum cdns_pcie_rp_bar`, `struct cdns_pcie_rp_ib_bar`, `enum cdns_pcie_reg_bank`, `struct cdns_pcie_ops`, `struct cdns_plat_pcie_of_data`, `struct cdns_pcie`, `struct cdns_pcie_rc`, `struct cdns_pcie_epf`, `struct cdns_pcie_ep`, inline accessors `cdns_pcie_*`, `cdns_pcie_hpa_*`, RP/EP config access helpers, and public prototypes for host, EP, PHY, translation, and link operations.

Control flow: inline wrappers map generic operations onto platform callbacks when available (`start_link`, `stop_link`, `link_up`) or default classic helpers. Register-bank helpers translate HPA logical banks into offsets before MMIO. Config read/write helpers handle byte/word/dword accesses through aligned dword accesses where needed.

State/persistence: structures declared here own most Cadence runtime state: MMIO bases, resources, PHYs, links, mode, ops, register offsets, RC IDs/quirks/BAR availability, EP outbound region state, IRQ cache, and EPF BAR pointers. The header does not allocate state by itself.

Dependencies/integration: Linux PCI host and endpoint APIs, PHY framework, module/kernel helpers, classic and HPA register headers. It is included by every Cadence source in this work item.

Risks: the header mixes classic and HPA accessors; using the wrong helper on a controller can target different addresses. `cdns_reg_bank_to_off()` depends on non-null `cdns_pcie_reg_offsets` for HPA users. Inline config-size helpers read aligned dwords and mask fields, so callers must pass valid sizes and offsets. Build-time inline stubs return `-ENODEV` when host/EP configs are disabled, which can hide mode support issues until runtime.

Test signals: build matrix for host-only, EP-only, HPA, and platform glue; sparse/compile checks for prototypes; root and endpoint config access sizes; HPA bank offsets; callback fallback behavior; and structure initialization in all glue drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.h -->
