# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk.c

## Purpose

`rtw8851b_rfk.c` implements RTL8851B RF calibration and RF channel programming. It covers DACK, RX-DCK, IQK, DPK, RCK, AACK/LCK, TSSI setup/tracking, scan-time TSSI handling, LCK thermal tracking, and RF channel/bandwidth writes.

## Important APIs, Types, And Functions

Public wrappers are `rtw8851b_aack()`, `rtw8851b_lck_init()`, `rtw8851b_lck_track()`, `rtw8851b_rck()`, `rtw8851b_dack()`, `rtw8851b_iqk()`, `rtw8851b_rx_dck()`, `rtw8851b_dpk_init()`, `rtw8851b_dpk()`, `rtw8851b_dpk_track()`, `rtw8851b_tssi()`, `rtw8851b_tssi_scan()`, `rtw8851b_wifi_scan_notify()`, and `rtw8851b_set_channel_rf()`. Calibration command IDs live in `enum dpk_id`, `enum dpk_agc_step`, and `enum rtw8851b_iqk_type`. Static arrays encode one-path TSSI DE registers, IQK/DPK gain groups, and BB/RF/KIP backup registers.

## Control Flow

DACK runs DRCK, ADDCK, DACK S0, DADCK, backup/reload, and stores completion state. RX-DCK stops scheduler TX, waits for RX mode, triggers RX DCK, swaps RXBB offsets into RF LUT, and restores RF state. IQK backs up BB/RF, forces calibration clocks, runs LOK/TXK/RXK by band and wideband/narrowband mode, stores fail bits, restores hardware, and wraps the operation in BTC notifications. DPK backs up KIP/RF, records channel metadata, disables conflicting loops, runs KIP preset/TXAGC/TPG/AGC/IDL/MPA/gain normalization, enables DPD on success, and restores normal state. TSSI programs system, TX power, DCK, thermal meter, DAC gain, slope/alignment, tracking, and efuse-derived DE values. RF channel setup writes RF channel, bandwidth, and RXBB bandwidth and performs LCK recovery if the synthesizer is not locked.

## State And Persistence Behavior

Runtime state is in `rtwdev->dack`, `rtwdev->iqk`, `rtwdev->dpk`, `rtwdev->tssi`, `rtwdev->lck`, and `rtwdev->is_tssi_mode[]`. Hardware state is written directly to RF/BB/KIP registers and remains until reset, retune, or recalibration. The implementation saves/restores selected registers to avoid leaving calibration modes active.

## Dependencies And Integration Points

The file depends on common rtw89 RF/PHY/MAC helpers, RFK parser tables, tracking tables, BTC notifications, channel-context lookup, scheduler stop/resume, and atomic poll helpers. `rtw8851b.c` calls these wrappers from chip initialization, per-channel RFK, scan notification, periodic tracking, and RF channel setup.

## Risks

Timeouts often log and continue, so calibration quality can degrade without a hard failure. Backup/restore lists must be complete. The code heavily assumes one RF path. DPK AGC thresholds and TSSI group mappings are hardware/regulatory sensitive. Scan-end TSSI offset handling can affect post-scan transmit power if ordered incorrectly.

## Test Signals

Use `RTW89_DBG_RFK`, `RTW89_DBG_RFK_TRACK`, and `RTW89_DBG_TSSI` logs. Validate successful one-shots, no SYN lock failures after channel changes, sane TSSI DE writes from efuse, DPK path-ok/tracking updates, restored traffic after scheduler stop/resume, and stable RSSI/TX EVM across 2G/5G and 20/40/80 MHz channels.
