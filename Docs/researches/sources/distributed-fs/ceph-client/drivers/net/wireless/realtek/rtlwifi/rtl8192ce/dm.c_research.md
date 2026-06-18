# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/dm.c

## Purpose
This CE-specific dynamic-management file implements near-field dynamic TX-power reduction. It complements shared RTL8192C dynamic-management code by deciding when RTL8192CE should lower transmit power based on received signal power.

## Important APIs, Types, And Functions
The only function is `rtl92ce_dm_dynamic_txpower()`, exposed through the HAL ops table as `.dm_dynamic_txpower`. It uses `dynamic_txpower_enable`, `dm_flag`, `dynamic_txhighpower_lvl`, `last_dtp_lvl`, `undec_sm_pwdb`, `entry_min_undec_sm_pwdb`, and thresholds from `dm.h`.

## Control Flow
The function exits if dynamic TX power is disabled or high-power management is masked by `HAL_DM_HIPWR_DISABLE`. It chooses the signal metric from station, adhoc, or extension-port state, maps the value to normal or level-1 high-power reduction with hysteresis, and calls `rtl92c_phy_set_txpower_level()` when the level changes.

## State And Persistence
Runtime state is stored in `rtlpriv->dm` and current channel state in `rtlpriv->phy`. No persistent state is written. The effect is hardware TX AGC programming through subsequent PHY TX-power calls.

## Dependencies And Integration Points
It depends on rtlwifi `rtl_priv`, `rtl_mac`, and common PHY TX-power programming. It is invoked by the shared DM watchdog path through the CE HAL operation.

## Risks And Edge Cases
The code currently sets both near-field threshold branches to `TXHIGHPWRLEVEL_LEVEL1`; level 2 is defined but unused here. Signal thresholds are magic values and depend on correct RSSI/PWDB smoothing from shared DM. Incorrect link-state classification can leave power normal when close to a peer.

## Test Signals
Validate by observing `dynamic_txhighpower_lvl` changes under high RSSI, TX-power register changes after level transitions, no changes when disabled or disconnected, and stable throughput/range during DM watchdog runs.
