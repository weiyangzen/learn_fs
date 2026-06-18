# sources/distributed-fs/ceph-client/drivers/ufs/host/cdns-pltfrm.c

## Purpose
Implements Cadence UFSHCI platform variant operations on top of the generic `ufshcd-pltfrm` driver. It programs controller timing, handles a Cadence hibern8 quirk by saving L4 DME attributes, disables host TX LCC before startup, and provides an optional M31 16nm PHY register tweak.

## Important APIs, types, and functions
`struct cdns_ufs_host` stores 12 transport-layer attributes. `cdns_ufs_get_l4_attr()` and `cdns_ufs_set_l4_attr()` snapshot and restore `T_*` MIBs. `cdns_ufs_set_hclkdiv()` locates `core_clk`, derives the HCLK divider in MHz, writes `CDNS_UFS_REG_HCLKDIV`, and reads back to flush the write. `cdns_ufs_hce_enable_notify()`, `cdns_ufs_link_startup_notify()`, and `cdns_ufs_hibern8_notify()` are wired through `ufs_hba_variant_ops`. `cdns_ufs_m31_16nm_phy_initialization()` sets bit 24 in `CDNS_UFS_REG_PHY_XCFGD1`.

## Control flow and state
Probe matches `cdns,ufshc` or `cdns,ufshc-m31-16nm`, selects variant ops from match data, then calls `ufshcd_pltfrm_init()`. Runtime state is only the devm-allocated variant struct and cached L4 attributes. On pre-HCE enable it writes HCLKDIV; on pre-link it disables LCC and AH8; before hibern8 enter it saves L4 attributes and after hibern8 exit it restores them.

## Dependencies and integration points
Depends on UFSHCD core DME helpers, platform probing, Linux clock framework, OF match data, and `ufshcd-pltfrm` PM callbacks. It integrates with UIC notification sequencing supplied by UFSHCD core.

## Risks and test signals
Risk centers on missing `core_clk`, wrong clock rate units, DME get/set failures being ignored in L4 save/restore, and AH8 being forcibly disabled. Test signals are successful link startup, no unexpected interrupts after AH8 disable, HCLKDIV matching `core_clk / 1000000`, and suspend/resume or hibern8 cycles preserving L4 connectivity.
