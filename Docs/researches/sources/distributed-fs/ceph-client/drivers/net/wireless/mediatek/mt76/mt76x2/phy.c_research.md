# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/phy.c

Purpose: Shared MT76x2 PHY calibration and transmit-power code used by the PCI/USB variants. It programs AGC, PA mode, tx delay, TSSI/DPD compensation, and channel gain behavior through mt76 register helpers and MCU calibration commands.

Important APIs: exported entry points include `mt76x2_apply_gain_adj`, `mt76x2_phy_set_txpower_regs`, `mt76x2_phy_set_txpower`, `mt76x2_configure_tx_delay`, `mt76x2_phy_tssi_compensate`, and `mt76x2_phy_update_channel_gain`. Internal helpers adjust high LNA gain, AGC gain, and compute the minimum non-zero rate power.

Control flow: channel setup callers first read EEPROM-derived power info, apply bandwidth deltas, clamp rate power to configured/SAR limits, derive per-chain target offsets, and program hardware with `mt76x02_phy_set_txpower`. Periodic calibration alternates between triggering TSSI measurement and consuming completion state from `MT_BBP(CORE, 34)`, optionally running DPD once.

State and persistence: all persistent inputs come from EEPROM-parsed calibration fields in `dev->cal` and current chandef/txpower configuration. Runtime state includes `tssi_comp_pending`, `tssi_cal_done`, `dpd_cal_done`, `agc_gain_cur`, `low_gain`, RSSI averages, and cached `rate_power`/target deltas.

Dependencies and integration: depends on mt76x02 PHY/EEPROM helpers, mac80211 band/channel definitions, MCU calibration functions, external PA/LNA capability detection, DFS AGC adjustments, and raw register access.

Risks: register constants are hardware-sensitive; incorrect per-chain delta math or EEPROM interpretation can violate regulatory power limits or degrade RF performance. The assignment of `target_power_delta[1]` subtracts chain 0 target power, which is worth regression attention. Calibration paths must avoid running on silent/radar-sensitive channels incorrectly.

Test signals: validate per-band txpower using regulatory/SAR scenarios, channel switches across 20/40/80 MHz, external PA/LNA boards, TSSI/DPD completion, DFS channels, and RSSI-driven gain transitions under weak and strong signal conditions.
