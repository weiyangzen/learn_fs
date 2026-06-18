# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_platform.h

Purpose: public platform glue header for STMMAC wrapper drivers.

Important APIs and functions: declares `devm_stmmac_probe_config_dt()`, `stmmac_pltfr_find_clk()`, `stmmac_get_platform_resources()`, `stmmac_pltfr_probe()`, `devm_stmmac_pltfr_probe()`, `stmmac_pltfr_remove()`, and `stmmac_pltfr_pm_ops`. `get_stmmac_bsp_priv()` retrieves wrapper private data from the common netdev/device path.

Control flow: wrapper drivers include this header, parse DT or prepare platform data, gather resources, then call probe helpers. PM-capable wrappers can point at `stmmac_pltfr_pm_ops`. BSP-private state is stored in `plat->bsp_priv` and recovered by `get_stmmac_bsp_priv()`.

State and persistence: no header-owned state. It encodes assumptions that device driver data is a `struct net_device *` after common probe and that wrapper state is nested under `priv->plat`.

Dependencies and integration: includes `stmmac.h`; implementations are exported by `stmmac_platform.c`.

Risks and test signals: `get_stmmac_bsp_priv()` is unsafe before probe completes or after removal. Validate by building wrapper drivers and exercising probe/remove/PM callback paths.
