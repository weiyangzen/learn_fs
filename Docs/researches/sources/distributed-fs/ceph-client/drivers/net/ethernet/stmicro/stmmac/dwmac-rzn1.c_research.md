<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rzn1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rzn1.c

## Purpose
`dwmac-rzn1.c` is a small Renesas RZ/N1 glue layer that adds optional MIIC PCS support to a standard stmmac platform device.

## Important APIs, Types, and Functions
- `rzn1_dwmac_pcs_init()` parses `pcs-handle`, creates a MIIC PCS with `miic_create()`, and stores it in `priv->hw->phylink_pcs`.
- `rzn1_dwmac_pcs_exit()` destroys the MIIC PCS.
- `rzn1_dwmac_select_pcs()` returns the stored PCS to phylink.
- `rzn1_dwmac_probe()` installs PCS callbacks and calls `stmmac_dvr_probe()`.

## Control Flow
Probe obtains stmmac resources and DT platform data, stores `plat_dat` as `bsp_priv`, assigns PCS init/exit/select callbacks, and registers stmmac. During stmmac MAC setup, the PCS init callback creates the MIIC PCS if the DT phandle exists.

## State and Persistence
The only extra runtime state is the phylink PCS pointer owned through the stmmac hardware structure. There are no persistent syscon settings or file-backed state.

## Dependencies and Integration Points
It depends on OF phandles, `pcs-rzn1-miic`, phylink PCS interfaces, and stmmac platform helpers. Compatible string: `renesas,rzn1-gmac`.

## Risks and Edge Cases
- PCS is optional; missing `pcs-handle` leaves stmmac without a PCS.
- PCS lifetime is tied to stmmac callbacks, so double-destroy or missing exit would affect phylink cleanup.
- Probe uses non-devm `stmmac_dvr_probe()` with `stmmac_pltfr_remove()`.

## Test Signals
Test probe with and without `pcs-handle`, PCS creation failure propagation, phylink mode selection, and traffic over interfaces requiring MIIC PCS. Remove/unbind should verify `miic_destroy()` is called once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-rzn1.c -->
