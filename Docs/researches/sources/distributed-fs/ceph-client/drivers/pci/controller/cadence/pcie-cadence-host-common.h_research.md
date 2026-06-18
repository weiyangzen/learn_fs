<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.h -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.h

Purpose: declaration header for shared Cadence host helper code. It defines the callback types used to abstract classic versus HPA inbound BAR programming and exports the common link and DMA-range mapping helpers.

Important APIs/types/functions: `extern u64 bar_max_size[]`, typedefs `cdns_pcie_host_bar_ib_cfg` and `cdns_pcie_linkup_func`, plus prototypes for link training/wait/retrain, BAR selection, DMA range sorting, classic BAR config, generic BAR config, and DMA-range mapping.

Control flow: no executable flow is present. The header establishes the contract used by `pcie-cadence-host.c`, `pcie-cadence-host-hpa.c`, and SoC glue that wants shared link setup or DMA inbound mapping.

State/persistence: no state is allocated here. The callback signatures shape state transitions in `struct cdns_pcie_rc`, especially `avail_ib_bar[]`, and hardware inbound translation state in the implementation files.

Dependencies/integration: depends on Linux PCI/resource types and on Cadence types from `pcie-cadence.h` being visible to users. It is an internal driver-family interface, not a firmware or user ABI.

Risks: callback type changes must be synchronized across both classic and HPA host implementations. The header declares `cdns_pcie_host_bar_ib_config()` although HPA users use a private equivalent, so mistaken linkage can pick the wrong register layout. Since `bar_max_size` is global, consumers must treat it as read-only policy.

Test signals: compile coverage for both `CONFIG_PCIE_CADENCE_HOST` and HPA users, callback prototype compatibility, and successful DMA-range mapping through both classic and HPA callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host-common.h -->
