# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/initvals_phy.h

## Purpose
Provides static RF and BBP temperature/bandwidth tuning tables for MT7601U PHY initialization and runtime calibration.

## Important APIs, Types, And Functions
Defines `RF_REG_PAIR()` and tables `rf_central`, `rf_channel`, `rf_vga`, plus BBP mode tables for normal/high/low temperature and 20/40 MHz operation. `bbp_mode_table[3][3]` maps temperature state and bandwidth/group selection to a register table and count.

## Control Flow
No executable flow. PHY code writes these tables during initialization, channel changes, bandwidth changes, and temperature compensation.

## State And Persistence
Static const tables become persistent RF/BBP register state once written. They configure central RF blocks, channel RX/TX/PA/LOGEN sections, VGA, and temperature-dependent BBP AGC values.

## Dependencies And Integration Points
Consumed by MT7601U PHY code via `struct mt76_reg_pair`. The tables complement EEPROM power/TSSI data and BBP init values from `initvals.h`.

## Risks
The values are hardware-specific and opaque. Comments note a TODO around BBP178/channel 14 behavior, so channel-14 CCK bandwidth handling is a known fragility. Wrong table selection can damage sensitivity or spectral behavior.

## Test Signals
RF bring-up, channel switching across 1-14, 20/40 MHz operation, low/normal/high temperature calibration, RSSI/throughput stability, and spectral compliance around channel 14.
