# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bgmac-platform.c

Purpose: Implements the platform/OF front-end for the shared `bgmac` Ethernet core, targeting Broadcom AMAC/NSP/NS2 style devices with memory resources rather than BCMA devices.

Important APIs/functions: Platform callbacks perform raw MMIO and optional IDM access: `platform_bgmac_read/write()`, `platform_bgmac_idm_read/write()`, `platform_bgmac_clk_enabled()`, and `platform_bgmac_clk_enable()`. `bgmac_nicpm_speed_set()` programs NICPM pad/IOMUX speed for RGMII and then calls shared link adjustment. `platform_phy_connect()` selects either NICPM-aware link callback or normal `bgmac_adjust_link()`. `bgmac_probe()` maps `amac_base`, optional `idm_base`, optional `nicpm_base`, sets platform feature flags and callbacks, chooses PHY/fixed-link policy, and calls `bgmac_enet_probe()`.

Control flow: Platform probe allocates shared bgmac state, loads MAC address if present, gets IRQ and resources, configures feature flags initially as 4707-like, clears IDM-mask feature if an IDM resource exists, installs callback table, selects OF PHY or fixed 2.5G mode, and delegates to the shared core. Remove calls only `bgmac_enet_remove()` because resources are devm-managed. PM hooks delegate suspend/resume to shared bgmac.

State/persistence: The front-end populates `bgmac->plat.base`, `idm_base`, `nicpm_base`, `dma_dev`, IRQ, feature flags, and callback pointers. NICPM speed writes persist in platform registers and are refreshed by link callback.

Dependencies/integration: Uses platform driver/OF resources, phylib, optional NICPM registers, BCMA constants for IDM register definitions, and shared `bgmac` APIs.

Risks/test signals: Optional resource handling changes behavior substantially, especially `BGMAC_FEAT_IDM_MASK`. NICPM speed programming must match PHY speed and RGMII board wiring. Test compatible strings, resource-name failures, fixed-link fallback, PHY handle path, 10/100/1000 speed changes with NICPM, suspend/resume, and module unload.
