# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals_init.h

Purpose: this header provides static register tables for common MAC initialization, MT76x0-specific MAC initialization, BBP initialization, and DCOC calibration setup.

Important data: `common_mac_reg_table` programs beacon offsets, legacy/HT rates, RX filter, backoff, TX link/timeout/max length, LED, PBF, retry, protection, WPDMA, and timing registers. `mt76x0_mac_reg_table` programs IO/PBF/FCE, AMPDU length, TX software and power registers, LDO, HT control, PN padding, VHT fallback, and related MAC/PHY glue. `mt76x0_bbp_init_tab` initializes core, IBI, AGC, TXC/RXC, TXBE, RXFE, and RXO BBP blocks. `mt76x0_dcoc_tab` sets CAL registers 47-55.

Control flow and integration: `mt76x0_init_mac_registers` writes the common and MT76x0 MAC tables during common hardware init. `mt76x0_init_bbp` writes the BBP init table, selected switch-table rows, and DCOC table after BBP readiness is confirmed.

State and persistence behavior: all arrays are read-only constants. Runtime writes configure volatile hardware registers and are re-applied on probe/resume/reinit.

Dependencies: it includes `phy.h` for RF-related type context and is consumed by `init.c`. It relies on register macros from mt76/mt76x02 headers in the includer.

Risks: this file is register-programming data with little self-description. Wrong values can break DMA, aggregation, protection, power, or receive behavior. Some raw registers use numeric addresses, which are harder to audit than named macros.

Test signals: successful probe, DMA start, beaconing, TX/RX traffic, HT/VHT aggregation, key/WCID setup, and resume are practical tests. Hardware register dumps before/after init help diagnose regressions.
