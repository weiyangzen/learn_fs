# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_devids.h

Purpose: this header defines PCI device IDs recognized by the iavf VF driver.

Important APIs/types: it declares constants for `IAVF_DEV_ID_VF` (`0x154C`), `IAVF_DEV_ID_VF_HV` (`0x1571`), `IAVF_DEV_ID_ADAPTIVE_VF` (`0x1889`), and `IAVF_DEV_ID_X722_VF` (`0x37CD`).

Control flow and integration: PCI id tables in the driver use these constants to bind the iavf module to supported virtual-function devices. The IDs distinguish common Intel Ethernet VF variants, Hyper-V-facing VF, adaptive VF, and X722 VF.

State and persistence: no runtime state exists here; these are compile-time hardware binding constants.

Risks and test signals: wrong IDs can prevent probe or bind the driver to unsupported devices. Tests should cover modalias generation, PCI id table compile references, module autoloading, and probe on supported VF hardware or emulated PCI IDs.
