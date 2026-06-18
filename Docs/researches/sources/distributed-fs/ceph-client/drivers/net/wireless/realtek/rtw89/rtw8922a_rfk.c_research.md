# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8922a_rfk.c

## Purpose
This file implements RTL8922A RF calibration support outside the main chip file. It handles TSSI continuous tracking gating, RF channel register programming, synthesizer power selection for DBCC/MLO modes, calibration table reload selection, and RFK hardware/channel pre/post hooks.

## Important APIs, Types, and Functions
- `rtw8922a_tssi_cont_en_phyidx()` enables/disables continuous TSSI per PHY, mapping PHY0/PHY1 to RF A/B in `MLO_1_PLUS_1_1RF` and both paths otherwise.
- `rtw8922a_set_channel_rf()` wraps `rtw8922a_ctl_band_ch_bw()` to update RF `RR_CFGCH`/`RR_CFGCH_V1` for active kpaths and apply CAV-specific LUT writes.
- `_rf_syn_pow` encodes `RF_SYN_ON_OFF`, `RF_SYN_OFF_ON`, `RF_SYN_ALLON`, and `RF_SYN_ALLOFF`.
- `rtw8922a_set_syn01_cav()` and `_cbv()` program cut-specific synthesizer power bits.
- `rtw8922a_chlk_reload_sel_tbl_v0/v1()` maintain RFK MCC channel descriptors, with v1 selected when firmware advertises `RFK_PRE_NOTIFY_MCC_V1`.
- `rtw8922a_rfk_hw_init()`, `rtw8922a_pre_set_channel_rf()`, and `rtw8922a_post_set_channel_rf()` are called by chip ops around RFK and channel changes.

## Control Flow
Channel changes call pre-set RF logic when DBCC is active, temporarily selecting the appropriate synthesizer power state for the PHY being changed. RF channel programming reads current RF18 values, validates against `INV_RF_DATA`, merges channel/band/bandwidth bits from `rtw89_chip_chan_to_rf18_val()`, writes both RF channel registers, and delays for hardware settling. Post-set calls `rtw8922a_rfk_mlo_ctrl()`, which chooses synthesizer state from `mlo_dbcc_mode` and reloads calibration table selections for the management channels.

## State and Persistence
The file updates RF hardware registers and persistent driver RFK state in `rtwdev->rfk_mcc`. Table indices, channel, band, bandwidth, and RF18 values are retained for reuse across MCC/MLO channel reloads.

## Dependencies and Integration Points
It depends on `chan.h`, `mac.h`, `phy.h`, `reg.h`, `rtw8922a.h`, and rtw89 RFK helpers such as `rtw89_phy_get_kpath()`, `rtw89_phy_get_syn_sel()`, `rtw89_rfk_chan_lookup()`, and `rtw89_mgnt_chan_get()`. The main chip file wires these functions through `rtw8922a_chip_ops`.

## Risks
- Invalid RF reads abort programming; repeated `INV_RF_DATA` indicates lower-level RF access or power sequencing failure.
- Calibration table selection is limited to index <= 2; mode or firmware changes that need more entries require code changes.
- CAV/CBV synthesizer programming differs; wrong cut detection can power the wrong RF synthesizer.
- Shared-table v1 logic stores common channel arrays with per-path `table_idx`, so indexing mistakes can cross-contaminate paths.

## Test Signals
- RFK debug logs should show expected SYN config and no invalid RF18 warnings.
- DBCC/MLO channel switch tests should verify both PHYs retain calibrated RF state.
- Firmware feature toggling for `RFK_PRE_NOTIFY_MCC_V1` should be covered if both firmware generations are supported.
