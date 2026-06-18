<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.h

## Purpose
Declares shared RTL8723 dynamic-management initialization helpers.

## Important APIs, Types, And Functions
- `rtl8723_dm_init_dynamic_txpower(struct ieee80211_hw *hw)`.
- `rtl8723_dm_init_edca_turbo(struct ieee80211_hw *hw)`.
- `rtl8723_dm_init_dynamic_bb_powersaving(struct ieee80211_hw *hw)`.

## Control Flow
The header has no control flow; it provides prototypes for `dm_common.c`.

## State And Persistence
The declared functions initialize persistent runtime DM fields in `rtl_priv`.

## Dependencies And Integration Points
Included by chip-specific DM code for RTL8723AE and RTL8723BE. It assumes `struct ieee80211_hw` is available from the including rtlwifi headers.

## Risks And Edge Cases
Prototype changes break shared chip-specific callers and exported symbol users. Missing declarations can hide type mismatches in common DM setup.

## Test Signals
Compile coverage for AE/BE DM code and successful symbol resolution for the three common initialization functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723com/dm_common.h -->
