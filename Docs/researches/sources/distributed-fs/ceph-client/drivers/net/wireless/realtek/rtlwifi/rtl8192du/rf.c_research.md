# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/rf.c

Purpose: Implements RTL8192DU RF6052 path configuration and temporary peer-PHY enable/powerdown logic for single-PHY and dual-MAC/dual-PHY modes.

Important APIs/functions: `rtl92du_phy_enable_anotherphy()` powers/enables the peer PHY and applies DBI address masks so the current MAC can program it. `rtl92du_phy_powerdown_anotherphy()` powers down the peer PHY if its MAC is still off. `rtl92du_phy_rf6052_config()` chooses RF path count, handles dual-MAC path remapping, prepares RFENV/3-wire access, loads RF tables through `rtl92du_phy_config_rf_with_headerfile()`, restores RFENV, and powers down temporary peer PHYs.

Control flow: RF setup derives path count from `rf_type`. In DUALMAC_DUALPHY mode, MAC0 on 2.4 GHz may initialize radio B through PHY1, while MAC1 on 5 GHz may initialize radio A through PHY0. The path loop saves RFENV, enables RF serial access, configures RF address/data widths, loads radio A/B tables, restores RFENV, and aborts on failure.

State and persistence: Mutates `rtlphy->num_total_rfpath` and `rtlhal->during_mac0init_radiob` / `during_mac1init_radioa`. Checks `MAC0_ON` and `MAC1_ON` before enabling or powering down shared hardware. No disk persistence.

Dependencies/integration: Depends on rtlwifi I/O, rtl8192d registers, common PHY helpers, and `phy.c` RF table loading. Called by `rtl92du_phy_rf_config()`.

Risks: Peer-MAC boolean semantics are easy to misuse. Incorrect `during_*` flag lifetime can corrupt RF writes. Early returns assume peer RF tables are already loaded when peer MAC is on.

Test signals: Dual-interface probe in both orders, DUALMAC_DUALPHY operation with one or both interfaces active, RF path count sanity for 1T1R/2T2R, and successful 2.4/5 GHz association.
