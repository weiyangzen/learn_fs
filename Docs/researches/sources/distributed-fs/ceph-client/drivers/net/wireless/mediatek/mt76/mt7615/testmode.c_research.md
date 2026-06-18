# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/testmode.c

Purpose: Implements mt76 nl80211 testmode operations for MT7615, including test TX power control, frequency offset, antenna path control, RX enablement, TX frame state, and RX stat dumping.

Important APIs and functions: `mt7615_tm_set_tx_power()` builds an MCU `SET_TX_POWER_CTRL` message from EEPROM data and optional test TX power overrides. `mt7615_tm_reg_backup_restore()` snapshots/restores selected PHY, antenna-switch, and RF registers. `mt7615_tm_init()` toggles SKU control, refreshes channel/filter state, and handles register backup/restore. `mt7615_tm_set_rx_enable()` toggles ARB RX/RXV bits. `mt7615_tm_set_tx_antenna()` programs PHY/RF/antenna-switch registers for requested chain masks. `mt7615_tm_set_tx_frames()` prepares TX frame mode. `mt7615_tm_update_params()`, `mt7615_tm_set_state()`, `mt7615_tm_set_params()`, and `mt7615_tm_dump_stats()` implement `mt7615_testmode_ops`.

Control flow: mt76 testmode invokes `set_state` and `set_params` with parsed nl80211 attributes. State transitions into/out of idle or TX frames update MCU parameters, channel/filter state, RX enablement, antenna masks, and register backup. Dump stats emits last RX frequency offset, RCPI, IB RSSI, and WB RSSI arrays into nested netlink attributes.

State and persistence: Uses `phy->mt76->test` current state, param bitmaps, tx power, freq offset, tx antenna mask, and tx skb. Stores backup registers in `phy->test.reg_backup` for restoration when testmode exits. No persistent device storage is intentionally modified, though hardware registers are temporarily changed.

Dependencies: mt76 testmode framework, EEPROM power index helpers, MCU test parameter APIs, channel/filter ops, RF read/write helpers, register definitions, and nl80211 netlink attributes.

Risks: Register backup allocation failure silently disables restore protection. Incorrect antenna masks can leave RF paths disabled until reinit. Testmode changes normal RX/TX behavior and must restore SKU, filters, RX, and RF state on exit. TX power index calculations must match EEPROM layout and band/chain rules.

Test signals: nl80211 testmode state transitions, TX frame generation, RX stat dumps, frequency offset and TX power MCU command success, register restoration after OFF, invalid antenna mask rejection, and normal traffic after leaving testmode.
