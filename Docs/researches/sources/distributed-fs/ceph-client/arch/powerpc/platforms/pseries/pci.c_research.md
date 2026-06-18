# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pci.c

Purpose: Provides pSeries-specific PCI fixups, SR-IOV PE association, legacy I/O region reservation, and host bridge preparation.

Important APIs/types/functions: Implements SR-IOV helpers `pseries_send_map_pe()`, `pseries_associate_pes()`, enable/disable hooks, `pSeries_final_fixup()`, Winbond IDE fixup, `prop_to_pci_speed()`, and `pseries_root_bridge_prepare()`.

Control flow: Final fixup reserves legacy ISA I/O regions, reports EEH state, and installs SR-IOV hooks when enabled. SR-IOV enable creates VF pci_dn data, builds an RTAS PE map from VF BAR/RID values, calls `ibm,open-sriov-map-pe-number`, and records firmware-assigned PE numbers. Root bridge preparation sets deferred controller release and reads `ibm,pcie-link-speed-stats` up the OF parent chain to set bus speeds.

State and persistence: Per-device SR-IOV state is stored in `pci_dn->pe_num_map`; host bridge release data ties `pci_host_bridge` lifetime to `pci_controller`. No persistent storage is maintained by this file.

Dependencies and integration points: Depends on RTAS PCI calls, EEH, pci_dn, pseries MSI domains, Open Firmware PCI properties, and generic PCI SR-IOV resource handling.

Risks: RTAS data buffer usage must be serialized, PE map size must fit `RTAS_DATA_BUF_SIZE`, and VF limit validation combines firmware configurable VFs with a hard cap. Resource fixups for old Winbond hardware can affect legacy systems. Parent OF node reference handling in bridge speed discovery is subtle.

Test signals: SR-IOV enable/disable on pseries, PE number assignment validation, absent RTAS token, VF count boundary tests, PCIe link speed sysfs values, hotplugged root bridges, EEH recovery, and Winbond fixup regression on legacy machines.

Source read size: 293 lines, 8204 bytes.
