## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-generic.c

Purpose: Generic firmware-initialized PCI host controller driver for CAM/ECAM systems and selected DesignWare ECAM-compatible hosts. It supplies OF match data and filtering wrappers, then delegates probe/remove to `pci-host-common`.

Important APIs, types, and functions: `gen_pci_cfg_cam_bus_ops` defines CAM config mapping with `bus_shift = 16`. `pci_dw_valid_device()` filters DesignWare ECAM direct-downstream slots greater than zero to prevent duplicated devices. `pci_dw_ecam_map_bus()` applies that filter before `pci_ecam_map_bus()`. `pci_dw_ecam_bus_ops` wraps generic read/write with the filtered mapper. `gen_pci_of_match` maps compatible strings to CAM, generic ECAM, or filtered DWC ECAM ops. The platform driver uses `pci_host_common_probe` and `pci_host_common_remove`.

Control flow: OF match selects ops; common probe maps ECAM and registers the host bridge. Config access is generic except for DWC-compatible filtering.

State and persistence: no private runtime state in this file; state is ECAM window and host bridge state managed by the common helper.

Dependencies and integration points: PCI ECAM library, `pci-host-common`, OF platform matching, generic PCI config read/write, and compatible strings such as `pci-host-ecam-generic`, `pci-host-cam-generic`, `snps,dw-pcie-ecam`, Armada8k, and SynQuacer.

Risks: DWC filtering assumes only slot 0 below the root bus is valid. Selecting the wrong compatible can expose duplicate devices or hide valid devices. The CAM bus shift is fixed at 16.

Test signals: generic ECAM and CAM enumeration, DWC ECAM duplicate-slot filtering, root bus removal, and OF match data coverage.
