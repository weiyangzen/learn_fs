# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_phy.c

Purpose: USB-specific channel programming and periodic PHY calibration for MT76x2U, layered on shared MT76x2 PHY helpers.

Important APIs: `mt76x2u_phy_set_channel` and delayed-work callback `mt76x2u_phy_calibrate`. Internal `mt76x2u_phy_channel_calibrate` runs once per channel unless the channel is silent.

Control flow: channel set resets calibration state, derives hardware channel, bandwidth, bandwidth index, and extension CCA mapping from chandef, reads RX gain, configures txpower registers, tx delay, txpower, band, bandwidth, CCA fields, and MCU channel. It then initializes gain, enables LDPC on newer revisions, performs R/RC/RXDCOC and channel calibrations when appropriate, sets AGC/TXOP/RXO registers, initializes TSSI default compensation, optionally runs TSSI calibration, queues periodic calibration, and returns. The periodic worker locks the device, completes channel calibration if needed, runs TSSI compensation and gain update, then reschedules itself.

State and persistence: runtime calibration state includes `channel_cal_done`, `init_cal_done`, `tssi_cal_done`, `cal_work`, scan state, current chandef, and AGC gain values.

Dependencies and integration: depends on shared `phy.c`, `usb_mac.c` stop/resume, mt76x02 MCU calibration commands, EEPROM flags, EDCCA, AGC helpers, and mac80211 workqueue scheduling.

Risks: channel/bandwidth index math is central to regulatory and RF correctness. Calibration is skipped during scanning/silent channels, so stale calibration state can matter. Worker rescheduling must be cancelled during stop/cleanup to avoid register access after removal.

Test signals: 20/40/80 MHz channel switches, upper/lower 40 MHz extension mapping, scanning path, TSSI-enabled and disabled EEPROMs, silent-channel behavior, calibration work cancellation, and LDPC enable on E3+ revisions.
