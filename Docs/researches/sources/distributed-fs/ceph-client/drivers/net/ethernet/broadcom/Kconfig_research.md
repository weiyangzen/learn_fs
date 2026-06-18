# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/Kconfig

Purpose: this Kconfig file defines the Broadcom Ethernet driver menu and all selectable Broadcom network driver symbols in this subtree. It controls whether the configurator exposes Broadcom devices and which individual drivers can be built in or as modules.

Important APIs/types/functions: the top-level symbol is `NET_VENDOR_BROADCOM`, gating the menu. Individual symbols include legacy and modern Broadcom drivers such as `B44`, `BCM4908_ENET`, `BCM63XX_ENET`, `BCMGENET`, `BNX2`, `CNIC`, `SB1250_MAC`, `TIGON3`, `BNX2X`, `BGMAC`, `SYSTEMPORT`, `BNXT`, `BNGE`, and `BCMASP`. `BCMASP` is the relevant symbol for the ASP2 files: it is tristate, depends on `ARCH_BRCMSTB || COMPILE_TEST`, defaults on for `ARCH_BRCMSTB`, depends on `OF`, and selects `PHYLIB`, `MDIO_BCM_UNIMAC`, and `PAGE_POOL`.

Control flow: Kconfig has no runtime flow; its build-time flow determines which object files are reachable by Makefiles. Enabling `NET_VENDOR_BROADCOM` allows selection of the driver symbols. Enabling `BCMASP` causes the Broadcom ASP2 module to be built by the Makefiles and brings in PHY, MDIO, and page-pool dependencies.

State and persistence: selected values persist in the kernel `.config`. These choices affect compile-time inclusion, module availability, and dependency closure, not runtime driver state.

Dependencies and integration points: this file integrates with the Linux kernel Kconfig system and with `drivers/net/ethernet/broadcom/Makefile`. It also encodes architecture, bus, optional PTP, HWMON, DCB, devlink, page-pool, and auxiliary bus dependencies used by drivers in the directory.

Risks: dependency mistakes produce build failures or silently hide drivers from expected platforms. For `BCMASP`, OF and page-pool support are mandatory; missing `ARCH_BRCMSTB` requires `COMPILE_TEST`. Test signals include `olddefconfig`, allmodconfig/allyesconfig builds, COMPILE_TEST coverage for `BCMASP`, and checking that selected helper subsystems are included when the driver is modular.
