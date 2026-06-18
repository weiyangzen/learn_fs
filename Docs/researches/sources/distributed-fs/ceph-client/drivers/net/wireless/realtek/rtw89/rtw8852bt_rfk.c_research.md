# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk.c

Purpose: Implements RTL8852BT RF calibration and RF channel programming: RCK, RX DCK, DACK/ADDCK, IQK, DPK, TSSI setup/alignment/tracking, scan handling, MCC bookkeeping, and RF channel/bandwidth writes.

Important APIs and functions: Public entry points are `rtw8852bt_rck()`, `rtw8852bt_dack()`, `rtw8852bt_iqk()`, `rtw8852bt_rx_dck()`, `rtw8852bt_dpk_init()`, `rtw8852bt_dpk()`, `rtw8852bt_dpk_track()`, `rtw8852bt_tssi()`, `rtw8852bt_tssi_scan()`, `rtw8852bt_wifi_scan_notify()`, `rtw8852bt_set_channel_rf()`, `rtw8852bt_mcc_get_ch_info()`, and `rtw8852bt_rfk_chanctx_cb()`.

Control flow: Calibration entries notify BTC, stop scheduler TX when necessary, wait for RX mode, back up BB/RF/KIP registers, force calibration clocks/AFE state, trigger NCTL one-shot commands, poll completion registers, store results, restore state, and resume traffic. IQK runs LOK/TX/RX per active DBCC path. DPK reloads existing backups or runs KIP preset, TXAGC/RXAGC, sync/gain-loss AGC, MDPK, result fill, and DPD enable. TSSI parses RFK tables, loads thermal/efuse values, optionally performs hardware-TX alignment, and enables tracking.

State and persistence: Mutates `rtwdev->dack`, `iqk`, `dpk`, `tssi`, `rfk_mcc`, `is_tssi_mode`, thermal EWMA-derived tracking, and many hardware registers. Calibration backups persist across channel contexts until reset or recalibration.

Dependencies and integration points: Depends on RTW89 channel, BTC, debug, firmware, MAC scheduler, PHY/RF accessors, `rtw8852b_common`, and `rtw8852bt_rfk_table.c`. Called by chip ops in `rtw8852bt.c`.

Risks: Very high hardware risk: register ordering, delays, and backup/restore balance matter. Several timeout paths log and continue. DPK/TSSI path coverage can differ from DBCC path selection. Signed DPK/TSSI arithmetic needs careful review.

Test signals: RFK debug logs, channel sweeps, DBCC/MCC, scan start/end, external PA bypass, thermal drift with DPK tracking, BT coexistence during RFK, and timeout-path register dumps.
