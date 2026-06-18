
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192cu/dm.c

Purpose: Provides the CU-specific dynamic transmit power adjustment hook used by the common rtl8192c dynamic-management watchdog. It reduces transmit power for near-field conditions based on smoothed PWDB signal levels and restores normal power when the peer is farther away.

Important APIs/functions: `rtl92cu_dm_dynamic_txpower()` checks `rtlpriv->dm.dynamic_txpower_enable`, `HAL_DM_HIPWR_DISABLE`, link state, AP/STA/adhoc mode, `undec_sm_pwdb` or `entry_min_undec_sm_pwdb`, and updates `dynamic_txhighpower_lvl`. On transitions it calls `rtl92c_phy_set_txpower_level()`, `dm_restorepowerindex()`, or `dm_writepowerindex()` with calibrated index values.

Control flow: Disabled paths return immediately. If unlinked and no minimum undecoded PWDB exists, the function resets to normal. For linked/ad-hoc/AP extension cases it selects a signal source, compares against `TX_POWER_NEAR_FIELD_THRESH_LVL2` and `TX_POWER_NEAR_FIELD_THRESH_LVL1` with hysteresis, then applies a power-level transition only when the level changed from `last_dtp_lvl`.

State and persistence: Mutates `rtlpriv->dm.dynamic_txhighpower_lvl` and `last_dtp_lvl`; indirectly updates BB/RF tx power registers. It relies on shared DM state populated by RX signal processing and common watchdog code.

Dependencies/integration: Called via `.dm_dynamic_txpower` in `rtl8192cu_hal_ops`. Uses shared helpers from `../rtl8192ce/dm.h` and 8192C PHY code. Its result influences RF tx-power writes in `rf.c`, which checks `dynamic_txhighpower_lvl`.

Risks: Threshold hysteresis is hard-coded; bad signal smoothing can cause power oscillation or underpowered links. `TXHIGHPWRLEVEL_LEVEL2` is handled in write logic but this CU function only sets normal or level1 in visible branches. Power changes during active scanning/association need hardware testing.

Test signals: Verify tx-power register changes as RSSI/PWDB crosses near-field thresholds, with no repeated writes when level is unchanged. Test linked STA, adhoc, unlinked, and HIPWR-disable cases. Monitor throughput and regulatory tx-power behavior after transitions.
