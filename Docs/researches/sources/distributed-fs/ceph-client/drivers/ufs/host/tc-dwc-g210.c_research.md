# sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210.c

## Purpose
Contains the shared Synopsys G210 test-chip PHY setup sequences. It writes local DME attributes required for 20-bit and 40-bit RMMI modes and exports the two configuration functions used by PCI and platform glue.

## Important APIs, types, and functions
`tc_dwc_g210_setup_40bit_rmmi()` and `tc_dwc_g210_setup_20bit_rmmi()` apply static `struct ufshcd_dme_attr_val` tables through `ufshcd_dwc_dme_set_attrs()`. The 20-bit path is split into lane 0 and conditional lane 1 setup; lane 1 is programmed only when `PA_AVAILRXDATALANES` or `PA_AVAILTXDATALANES` report two lanes. Public exports are `tc_dwc_g210_config_40_bit()` and `tc_dwc_g210_config_20_bit()`, which apply the setup, write `VS_MPHYCFGUPDT`, then enable `VS_DEBUGOMC`.

## Control flow and state
No heap state is maintained. The functions program hardware state via DME writes. Errors from attribute programming stop the sequence; update/debug writes are checked enough to propagate failures.

## Dependencies and integration points
Depends on UFS UniPro MIB definitions, DesignWare UFS helper attributes, and UFSHCD DME access. PCI and platform drivers call these functions from their `.phy_initialization` variant op.

## Risks and test signals
The tables are hardware magic values; incorrect values can break link training or marginal signal behavior. Lane discovery errors are not independently logged. Test signals are successful DME write sequences, correct lane count behavior, link startup across 1-lane and 2-lane configurations, and logs showing the expected RMMI width.
