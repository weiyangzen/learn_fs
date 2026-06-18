<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.c

## Purpose
Stores vendor-supplied RTL8723BE initialization tables for baseband, power-by-rate, RF radio path A, MAC registers, and AGC. These arrays are consumed during hardware/PHY/RF initialization instead of being generated algorithmically.

## Important APIs, Types, And Functions
- Baseband table: `RTL8723BEPHY_REG_1TARRAY` and `RTL8723BEPHY_REG_1TARRAYLEN`.
- Power-group table: `RTL8723BEPHY_REG_ARRAY_PG` and `RTL8723BEPHY_REG_ARRAY_PGLEN`.
- RF path table: `RTL8723BE_RADIOA_1TARRAY` and `RTL8723BE_RADIOA_1TARRAYLEN`.
- MAC table: `RTL8723BEMAC_1T_ARRAY` and `RTL8723BEMAC_1T_ARRAYLEN`.
- AGC table: `RTL8723BEAGCTAB_1TARRAY` and `RTL8723BEAGCTAB_1TARRAYLEN`.
- Uses `ARRAY_SIZE` to bind exported length symbols to the table contents.

## Control Flow
There is no executable control flow. Initialization code iterates these arrays as register/value pairs or vendor table commands. Some RF entries contain condition markers such as high-bit command words that the header-file parser interprets for chip cuts or modes before applying following register writes.

## State And Persistence
The arrays are static module data. When consumed, they program persistent MAC, baseband, AGC, RF, TX power, channel, gain, and calibration-related hardware registers. The arrays themselves are read-only in normal operation, although they are declared as mutable `u32`.

## Dependencies And Integration Points
Declared by `table.h` and used by chip PHY/RF helpers such as `rtl8723be_phy_config_rf_with_headerfile` and related MAC/BB table loading paths. Register offsets and values correspond to `reg.h` constants and the RTL8723BE vendor programming guide.

## Risks And Edge Cases
These opaque values are hardware-sensitive. Reordering, truncating, or editing values can break radio bring-up, calibration, AGC, channel operation, or regulatory power behavior. Length symbols must stay correct. Conditional RF table markers must remain in parser-compatible order. Because the values are magic register data, normal review cannot infer correctness without hardware testing or vendor reference comparison.

## Test Signals
Signals include successful BB/MAC/RF table load, stable association, expected RSSI and throughput, no RF calibration failures, no invalid register access warnings, correct TX power levels, and comparison against known-good register dumps after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/table.c -->
