# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/eeprom.h

Purpose: this header exposes MT76x0 EEPROM constants and helpers to common init and PHY code.

Important APIs: it defines `MT76X0U_EE_MAX_VER` as `0x0c`, `MT76X0_EEPROM_SIZE` as 512 bytes, and prototypes for `mt76x0_eeprom_init`, `mt76x0_read_rx_gain`, `mt76x0_get_tx_power_per_rate`, and `mt76x0_get_power_info`. Inline `s6_to_s8` converts signed 6-bit EEPROM rate values to `s8`; inline `mt76x0_tssi_enabled` reads `MT_EE_NIC_CONF_1_TX_ALC_EN`.

Control flow and state: callers use this header to gate PHY behavior. `mt76x0_tssi_enabled` controls whether txpower uses closed-loop TSSI calibration or static EEPROM deltas. `s6_to_s8` is used while populating `mt76x02_rate_power`.

Dependencies and integration: it includes `../mt76x02_eeprom.h` for EEPROM offsets and shared helpers and forward-declares `struct mt76x02_dev`. It is included by `mt76x0.h`, `eeprom.c`, `init.c`, and `phy.c`.

Risks: signed conversion and TSSI flag interpretation affect transmit-power limits and calibration. Changing the max version or EEPROM size can break compatibility with firmware/hardware data layout.

Test signals: compile users with no duplicate definitions, validate txpower decoding on known EEPROM dumps, and test TSSI-enabled and non-TSSI devices.
