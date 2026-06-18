# sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210-pltfrm.c

## Purpose
Provides OF/platform glue for the Synopsys G210 test chip. Unlike the PCI version, chip width is selected by device-tree compatible string rather than a module parameter.

## Important APIs, types, and functions
Two `ufs_hba_variant_ops` instances select `tc_dwc_g210_config_20_bit()` or `tc_dwc_g210_config_40_bit()` while sharing `ufshcd_dwc_link_startup_notify()`. `tc_dwc_g210_pltfm_match` maps `snps,g210-tc-6.00-20bit` and `snps,g210-tc-6.00-40bit`. Probe retrieves match data with `of_match_node()` and calls `ufshcd_pltfrm_init()`. Remove delegates to `ufshcd_pltfrm_remove()`.

## Control flow and state
The generic platform UFSHCD driver owns the host lifetime. This file contributes variant ops at probe time and uses standard UFS system/runtime PM callbacks. There is no private persistent state.

## Dependencies and integration points
Depends on OF matching, `ufshcd-pltfrm`, `ufshcd-dwc`, and the shared G210 DME setup functions. It integrates at the UFSHCD variant-op boundary.

## Risks and test signals
Risks are mostly device-tree binding accuracy and correct use of match data; a missing or wrong compatible string selects no PHY setup. Test signals are correct compatible matching, link startup notification reaching DesignWare glue, successful G210 PHY configuration, and platform suspend/resume through UFSHCD PM callbacks.
