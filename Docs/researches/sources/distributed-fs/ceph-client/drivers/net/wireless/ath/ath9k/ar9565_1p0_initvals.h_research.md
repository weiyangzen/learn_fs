# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar9565_1p0_initvals.h

Purpose: Defines AR9565 1.0 PCIe WLAN init tables for MAC, baseband, radio, SOC, RX gain, PCIe SERDES power-save, fast clock, and multiple TX gain modes. These are used by ath9k when `AR_SREV_9565()` hardware is older than 1.1.

Important APIs and data: Exports `ar9565_1p0_mac_core`, `ar9565_1p0_baseband_core`, `ar9565_1p0_baseband_postamble`, `ar9565_1p0_radio_core`, `ar9565_1p0_radio_postamble`, `ar9565_1p0_soc_preamble`, `ar9565_1p0_soc_postamble`, `ar9565_1p0_Common_rx_gain_table`, `ar9565_1p0_pciephy_clkreq_disable_L1`, `ar9565_1p0_modes_fast_clock`, `ar9565_1p0_common_wo_xlna_rx_gain_table`, and low/high/high-power TX gain tables. Aliases map the default lowest-OB/DB TX gain table and the Japan 2484 MHz CCK FIR coefficients.

Control flow: `ar9003_hw.c` installs these arrays in the AR9565 1.0 branch. PCIe SERDES arrays are assigned only when `ah->config.pll_pwrsave` requests D3 or D0 PLL power-save handling. TX and RX gain helper functions can later swap `ah->iniModesTxGain` and `ah->iniModesRxGain` among low, high, high-power, and no-XLNA variants based on EEPROM/configuration gain indices.

State and persistence: The file holds immutable register tables. Active runtime state is stored in `struct ath_hw` INI descriptors and in the programmed PCIe/radio/baseband registers. PCIe power-save behavior persists in the device until the next SERDES reprogramming or reset.

Dependencies and integration points: Consumed by AR9003 hardware attach/reset code and PCIe power-management paths. It depends on AR9331 MAC postamble and AR9300 2.2 CCK FIR data through aliases. It interacts with EEPROM calibration, PLL power-save config, mac80211 suspend/resume, and ath9k reset/recovery paths.

Risks: PCIe SERDES values can cause link instability or resume failures if applied to the wrong revision or power state. AR9565 has PCIe-specific behavior unlike SoC-only QCA95xx parts, so table mixups can show as device disappearance rather than only RF degradation. The 1.1 header aliases most 1.0 tables, so changes here affect later revisions unless overridden. TX power and receive sensitivity depend on EEPROM gain-mode selection matching these arrays.

Test signals: Probe AR9565 1.0 PCIe devices, suspend/resume with D0 and D3 PLL power-save flags, verify scan/association and throughput, exercise TX gain modes 0/1/2/3, test no-XLNA RX mode, monitor PCIe link errors, and run reset recovery after beacon miss or hardware check failures.
