<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-sky1.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-sky1.c

Purpose: CIX Sky1 PCIe host glue for the Cadence HPA controller. It supplies Sky1 register-bank offsets, ECAM config-space setup, link-training control through strap registers, link-up detection through the HPA debug-status register, and host setup quirks.

Important APIs/types/functions: `struct sky1_pcie`, `sky1_pcie_resource_get()`, `sky1_pcie_start_link()`, `sky1_pcie_stop_link()`, `sky1_pcie_link_up()`, `sky1_pcie_probe()`, and `sky1_pcie_remove()`. `sky1_pcie_ops` implements Cadence link operations. Probe fills `struct cdns_plat_pcie_of_data` offsets and calls `cdns_pcie_hpa_host_setup()`.

Control flow: probe allocates `struct sky1_pcie` and a PCI host bridge, maps `reg`, `cfg`, `rcsu_strap`, `rcsu_status`, and `msg`, creates a generic ECAM window from the bridge bus range, installs ECAM pci_ops, sets HPA ECAM mode and root-port IDs, marks inbound mapping disabled, records register-bank offsets, and starts HPA host setup. Link start/stop toggles `LINK_TRAINING_ENABLE` in `STRAP_REG(1)`; link-up checks bit 0 in `IP_REG_I_DBG_STS_0`.

State/persistence: the driver stores ECAM resources and Cadence RC state in `struct sky1_pcie` and `struct cdns_pcie_rc`. Persistent hardware effects are HPA outbound windows, optional message region, strap link-training bit, root-port vendor/device IDs, and ECAM mapping. Remove only frees the ECAM window, relying on devm for mappings.

Dependencies/integration: platform resources, `pci_ecam_create()`, generic ECAM ops, Cadence HPA host/common code, and DT compatible `cix,sky1-pcie-host`. It uses the HPA register-bank abstraction from `pcie-cadence.h`.

Risks: `sky1_pcie_remove()` does not call `cdns_pcie_host_disable()`, so teardown coverage depends on platform lifetime expectations. The `struct cdns_plat_pcie_of_data` is allocated and filled manually despite only offsets being used. `rcsu_status` is mapped but not read. Inbound map is disabled, so DMA translation assumptions must be validated by platform/IOMMU design. Wrong bank offsets would misprogram HPA translation registers.

Test signals: ECAM root and child config access, link train/stop register toggles, HPA link-up polling, message region setup, enumeration under generic ECAM ops, removal/unbind behavior, and DMA/IOMMU behavior with `no_inbound_map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pci-sky1.c -->
