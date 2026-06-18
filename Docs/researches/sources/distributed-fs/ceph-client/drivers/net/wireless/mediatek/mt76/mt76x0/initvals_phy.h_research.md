# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals_phy.h

Purpose: this header contains RF programming tables and frequency plans used by MT76x0 PHY channel setup and RF initialization.

Important data: tables include `mt76x0_rf_central_tab`, `mt76x0_rf_2g_channel_0_tab`, `mt76x0_rf_5g_channel_0_tab`, `mt76x0_rf_vga_channel_0_tab`, `mt76x0_rf_bw_switch_tab`, `mt76x0_rf_band_switch_tab`, `mt76x0_frequency_plan`, `mt76x0_sdm_frequency_plan`, `mt76x0_sdm_channel`, and `mt76x0_rf_ext_pa_tab`. The frequency plans map channels to PLL register fields and band classes including 2 GHz, 5 GHz low/mid/high, and 4.9 GHz/11J-style entries. Switch tables map RF bank/register writes to band and bandwidth combinations.

Control flow and integration: `phy.c` uses these arrays in `mt76x0_phy_rf_init`, `mt76x0_phy_set_band`, and `mt76x0_phy_set_chan_rf_params`. Initial RF setup writes central/2G/5G/VGA defaults with patching for chip/bus variants. Channel changes select a frequency-plan row, program PLL and SDM fields, apply bandwidth and band switch rows, and optionally apply external-PA rows.

State and persistence behavior: constants are not mutated. They configure volatile RF registers every init/channel-change. EEPROM-derived frequency offset and external PA capability combine with these table values at runtime.

Dependencies: it depends on RF macros and struct definitions from `phy.h`; consumers provide register access helpers for either direct RF CSR writes or MCU register-pair writes.

Risks: RF tables are extremely hardware-specific and high impact. Array index coupling between `mt76x0_frequency_plan` and `mt76x0_sdm_frequency_plan` means channel coverage/order changes must be synchronized. Incorrect band classification or external-PA values can cause poor sensitivity, failed channel lock, or regulatory power issues.

Test signals: tune every supported channel family, including channel 14, 4.9 GHz entries if enabled, low/mid/high 5 GHz, 20/40/80 MHz, and devices with external PA. Watch for VCO calibration failures, TX power anomalies, receive sensitivity drops, and firmware/BBP calibration errors.
