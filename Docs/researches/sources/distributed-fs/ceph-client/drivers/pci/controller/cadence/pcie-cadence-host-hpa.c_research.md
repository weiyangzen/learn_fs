<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-hpa.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-hpa.c

Purpose: host-mode support for Cadence High Performance Architecture PCIe controllers. It provides HPA config-space mapping, root-port setup, PTM response enablement, inbound/outbound address translation, ECAM/non-ECAM config-region handling, and host probing.

Important APIs/types/functions: `cdns_pci_hpa_map_bus()`, `cdns_pcie_hpa_host_bar_ib_config()`, `cdns_pcie_hpa_host_init_root_port()`, `cdns_pcie_hpa_create_region_for_cfg()`, `cdns_pcie_hpa_host_init_address_translation()`, `cdns_pcie_hpa_host_link_setup()`, and public `cdns_pcie_hpa_host_setup()`.

Control flow: setup marks RC mode, maps `reg` and `cfg` unless the glue already did, clears EROM aperture, starts link through platform ops and HPA link polling, resets BAR availability, initializes root-port class/IDs/command bits, programs config region 0 when ECAM is not provided, optionally maps a message region, maps bridge IO/MEM windows to HPA outbound regions, maps DMA ranges unless disabled, installs HPA pci_ops if needed, then calls `pci_host_probe()`.

State/persistence: RC state includes `ecam_supported`, `no_inbound_map`, `cfg_base`, `cfg_res`, `msg_res`, and BAR availability. Hardware state is distributed across HPA register banks: RP config, IP config control, AXI slave outbound regions, AXI master inbound BARs, tag management, and PTM controls.

Dependencies/integration: shared host-common DMA mapping, HPA register definitions, `cdns_pcie_hpa_*` common functions, PCI host bridge resources, optional ECAM setup from glue drivers such as Sky1, and platform link ops.

Risks: register-bank offsets must be correct for every platform. `cdns_pci_hpa_map_bus()` does not explicitly reject config cycles when link is down, unlike the classic path. RP_NO_BAR is remapped to BAR0 control fields in HPA inbound setup, which is subtle. ECAM and non-ECAM paths program different config access machinery, so glue must set `ecam_supported` and `cfg_base` accurately.

Test signals: ECAM and non-ECAM enumeration, config type0/type1 cycles, message outbound region, DMA inbound ranges, `no_inbound_map`, root command bits, PTM enable, link timeout propagation, and register traces in all HPA banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-hpa.c -->
