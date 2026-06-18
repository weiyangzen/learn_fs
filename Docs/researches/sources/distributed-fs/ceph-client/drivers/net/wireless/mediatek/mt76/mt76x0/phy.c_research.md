# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/phy.c

Purpose: this file implements MT76x0 PHY/RF initialization, channel programming, transmit-power programming, calibration, temperature/TSSI compensation, and periodic gain adjustment.

Important functions: RF access is abstracted by `mt76x0_rf_wr`, `mt76x0_rf_rr`, `mt76x0_rf_rmw`, `mt76x0_rf_set`, and `mt76x0_rf_clear`, using direct RF CSR on MMIO and MCU register-pair access on USB. Public/common APIs are `mt76x0_phy_wait_bbp_ready`, `mt76x0_phy_init`, `mt76x0_phy_set_channel`, `mt76x0_phy_set_txpower`, and `mt76x0_phy_calibrate`. Internal helpers program band/frequency tables, antenna selection, BBP bandwidth, TSSI DC/ADC calibration, target/delta power, temperature sensor, gain, and RF init patching.

Control flow: PHY init initializes delayed calibration work, selects antenna/coexistence wiring from EEPROM, writes RF defaults, and sets RX/TX paths. Channel setup computes RF band/bandwidth and center-channel group, programs BBP bandwidth, mt76x02 bandwidth/band, EXT_CCA mapping, RF band tables, PLL/frequency plan fields, channel 14 filter, RX gain, BBP params, and VCO enable. If not scanning, it initializes AGC, calibrates, applies txpower, and queues calibration work. Calibration runs full/VCO/LC/RXDCOC sequences through MCU commands and handles TSSI-specific DC calibration on power-on.

State and persistence behavior: it mutates RF/BBP/MAC registers, `dev->cal` fields such as TSSI DC/target/temp/gain, `dev->rate_power`, `dev->target_power`, `dev->mphy.txpower_cur`, delayed `cal_work`, and gain/RSSI tracking fields. It relies on EEPROM-derived offsets and does not write EEPROM.

Dependencies and integration: it depends on `mcu.h`, `eeprom.h`, `phy.h`, `initvals.h`, `initvals_phy.h`, and mt76x02 PHY helpers. It is invoked from init, channel config, start calibration, and periodic delayed work. USB behavior depends on `MT76_STATE_MCU_RUNNING` because RF writes are routed through the MCU.

Risks: this is timing- and hardware-sensitive code. RF CSR access is mutex-protected, but register programming and delayed calibration interact with channel changes and device removal. Unsupported widths 5/80+80/160 are silently returned from BBP bandwidth helper. Frequency-plan arrays and SDM channels must stay aligned. TSSI math uses fixed-point saturation and signed EEPROM fields; mistakes affect regulatory power and link quality. `is_mt7630` skips calibration entirely.

Test signals: BBP ready logs, channel changes across 2/5 GHz and 20/40/80 MHz, scanning path without recalibration, periodic calibration under traffic, TSSI enabled/disabled devices, MT7630 special behavior, USB and PCI RF writes, external PA devices, temperature-triggered VCO/full recalibration, and txpower/current-power reporting.
