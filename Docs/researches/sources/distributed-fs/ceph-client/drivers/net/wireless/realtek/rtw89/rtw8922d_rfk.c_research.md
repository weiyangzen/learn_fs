# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922d_rfk.c

## Purpose
This file implements RTL8922D RFK helper logic. It handles a small NCTL post table, TSSI continuous tracking control, RF channel programming, synthesizer/MLO RF state, calibration table reload, RFK hardware setup, pre/post channel RF hooks, and LCK thermal tracking.

## Important APIs, Types, and Functions
- `rtw8922d_nctl_post_defs` plus `RTW89_DECLARE_RFK_TBL()` exports `rtw8922d_nctl_post_defs_tbl`.
- `rtw8922d_tssi_cont_en_phyidx()` gates continuous TSSI tracking per PHY/path using BE4 indexed PHY writes.
- `rtw8922d_set_channel_rf()` writes RF `RR_CFGCH` and `RR_CFGCH_V1` with RSV/MOD sequencing and a 400 us settling delay.
- `_rf_syn_pow`, `rtw8922d_get_syn_pow()`, and `rtw8922d_set_syn01()` select RF synthesizer power based on `mlo_dbcc_mode`.
- `rtw8922d_chlk_reload_sel_tbl()` and `rtw8922d_chlk_reload()` update RFK MCC descriptors and RF/BB table selection for both paths.
- `rtw8922d_rfk_hw_init()` applies X4K settings.
- `rtw8922d_pre_set_channel_rf()` and `rtw8922d_post_set_channel_rf()` coordinate RF state around channel changes.
- `_get_thermal()`, `_lck_keep_thermal()`, `_lck()`, and `rtw8922d_lck_track()` implement thermal-threshold-triggered LCK.

## Control Flow
Hardware init applies X4K RF settings. Channel changes call pre-set when DBCC is enabled to select SYN power for the changing PHY, then the main chip code writes channel state, then post-set calls `rtw8922d_rfk_mlo_ctrl()` to restore mode-appropriate SYN power and reload calibration table selection. LCK tracking periodically reads thermal per RF path; when the delta from stored `lck->thermal[]` reaches `RTW8922D_LCK_TH` (16), `_lck()` triggers calibration on active paths and refreshes the baseline.

## State and Persistence
The file mutates RF/BB registers, `rtwdev->rfk_mcc.data`, and `rtwdev->lck.thermal[]`. These values persist across channel changes and tracking cycles until reset or RFK reinitialization.

## Dependencies and Integration Points
Depends on `chan.h`, `debug.h`, `phy.h`, `reg.h`, `rtw8922d.h`, and rtw89 RFK channel lookup, management-channel, RF read/write, and indexed PHY write helpers. `rtw8922d.c` wires the exported functions into chip ops and RFK tracking.

## Risks
- `mlo_linking` in `rtw8922d_chlk_ktbl_sel()` is hardcoded false, so any future linking-specific behavior is currently inactive.
- LCK relies on thermal reads being stable; noisy thermal values can cause excessive LCK or missed recalibration.
- RF channel writes use the selected synthesizer path only; wrong `rtw89_phy_get_syn_sel()` results can tune the wrong path.
- Table selection supports only indices <= 2; more RFK channel slots require updates.

## Test Signals
- RFK debug logs should show expected SYN config, LCK thermal readings, and no out-of-limit table warnings.
- DBCC/MLO channel switch tests should validate correct RF path tuning and calibration reuse.
- Thermal-stress tests should verify LCK fires when expected and does not destabilize RX/TX.
