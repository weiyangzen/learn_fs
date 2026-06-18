# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/types.h

Purpose: Provides brcmsmac-wide board flags, supported PHY/core revision masks, feature-test macros, logging helpers, write-flush behavior, multibool helpers, math helpers, and common forward declarations.

Important APIs/macros: Board flags describe PA/LNA/FEM/regulator/PLL/spur workarounds. `D11CONF`, `NCONF`, `LCNCONF`, and `SSLPNCONF` encode supported core/PHY revisions. `CONF_*`, `NREV_*`, `LCNREV_*`, `D11REV_*`, and `PHYTYPE_IS()` gate code by compile-time support and runtime revision. `BRCMS_ISNPHY`, `BRCMS_ISLCNPHY`, `BRCMS_ISSSLPNPHY`, and `BRCMS_PHY_11N_CAP` classify band PHYs. Also defines `BCMMSG`, `bcma_wflush16`, multibool helpers, `CEIL`, and forward declarations.

Control flow and state: Header-only behavior is macro expansion. It shapes build-time and runtime branch behavior across the driver, but stores no data. `bcma_wflush16` conditionally performs read-after-write on BCM47XX to handle ordering.

Dependencies and integration: Includes Linux types and MMIO helpers; references `brcm_msg_level` from `defs.h` logging flags and BCMA accessors. Risks include macro bugs (`CONF_RANGE` references `high` rather than `hi`), shifts beyond type width if revision constants grow, duplicated definitions, and hidden build-time pruning. Test signals include allmodconfig/build coverage, revision-gated paths for N/LCN/SSN PHYs, BCM47XX write flushing, and boardflag-dependent PHY/radio behavior.
