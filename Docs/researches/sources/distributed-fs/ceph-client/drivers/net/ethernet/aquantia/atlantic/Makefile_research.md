## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/Makefile

Purpose: kbuild object list for the Atlantic AQtion driver.

Important APIs/types: builds `atlantic.o` from core NIC, PCI, vector, ring, hardware utility, ethtool, drvinfo, filter, PHY, hardware generation, and MACsec API objects. Conditionally adds `aq_macsec.o` under `CONFIG_MACSEC` and `aq_ptp.o` under `CONFIG_PTP_1588_CLOCK`. Adds `-I$(src)` include path.

Control flow: build-time only. It determines which optional feature objects are linked into the module/built-in driver.

State and persistence: none beyond build artifacts.

Dependencies/integration: integrates this subset with other Atlantic files not included here, including `aq_nic`, `aq_pci_func`, hardware-generation implementations, and MACsec register API.

Risks: optional feature source lists must match preprocessor guards in C files. Missing object entries can compile headers but fail link for feature paths.

Test signals: allmodconfig/allyesconfig builds, `CONFIG_MACSEC` and `CONFIG_PTP_1588_CLOCK` matrix builds, and module link symbol checks.
