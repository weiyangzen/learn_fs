<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.c

## Purpose
Provides shared RTL8723 dynamic-management initialization helpers for TX power, EDCA turbo, and dynamic baseband power saving.

## Important APIs, Types, And Functions
- `rtl8723_dm_init_dynamic_txpower` disables dynamic TX power and initializes last/current high-power level to `TXHIGHPWRLEVEL_NORMAL`.
- `rtl8723_dm_init_edca_turbo` resets EDCA turbo state and non-BE/read-load flags.
- `rtl8723_dm_init_dynamic_bb_powersaving` initializes `struct ps_t` CCA/RF states to max and clears minimum RSSI and initialization fields.
- All three functions are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
Each function obtains `struct rtl_priv` from `struct ieee80211_hw` and assigns default fields. There are no branches other than straightforward state initialization.

## State And Persistence
The functions mutate `rtlpriv->dm` and `rtlpriv->dm_pstable`. The values persist as dynamic-management baselines until watchdog or PHY code updates them during runtime.

## Dependencies And Integration Points
Included through `dm_common.h` by RTL8723AE/BE dynamic-management setup. It imports shared rtlwifi state from `../wifi.h` and level constants from the RTL8723AE DM header, reflecting code reuse between chip variants.

## Risks And Edge Cases
Because this common code uses constants from `rtl8723ae/dm.h`, enum or macro divergence between AE and BE can break BE behavior. Defaults shape later watchdog behavior; incorrect initial RF/CCA states can suppress power-saving transitions or TX power limits.

## Test Signals
Signals include successful driver init, dynamic-management watchdog transitions from known initial states, EDCA turbo behavior under traffic, and TX power level staying normal until later logic changes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.c -->
