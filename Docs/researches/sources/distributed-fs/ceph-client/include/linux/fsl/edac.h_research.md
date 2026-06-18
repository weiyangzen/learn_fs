# sources/distributed-fs/ceph-client/include/linux/fsl/edac.h

Purpose: provides a minimal platform-data structure for Freescale/NXP EDAC memory-controller integration.

Important APIs and types: `struct mpc85xx_edac_pci_plat_data` contains an OF node pointer identifying the PCI/controller node associated with EDAC setup.

Control flow and state: platform glue supplies this struct to EDAC probe code, which uses the node to locate registers and report errors. The header itself has no control flow and owns no persistent state.

Dependencies and integration points: integrates with Freescale EDAC drivers and Open Firmware device discovery.

Risks and test signals: risks are limited to stale or missing node pointers and platform-data ABI drift. Tests should cover EDAC probe on MPC85xx/Layerscape platforms, missing OF node handling, and controller remove/unbind.
