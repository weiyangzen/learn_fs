# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/phy.h

## Purpose

`phy.h` is the shared AR9170 PHY register and bitfield map. It names baseband, timing, AGC, CCA, radar, antenna switch, chain, calibration, gain, TX power, spur, channel-mask, heavy-clip, RF bus, mode, CCK/OFDM, and per-chain register fields consumed primarily by `phy.c`.

## Important APIs, Types, and Functions

The file defines `AR9170_PHY_REG_BASE`, `AR9170_PHY_REG(_n)`, hundreds of `AR9170_PHY_REG_*` addresses, and bit masks plus `_S` shift values for use with the generic `SET_VAL`/`GET_VAL` helpers. Important groups include turbo/HT flags, timing/delta-slope fields, ADC/RF control, settling, RX gain, desired size, AGC/CCA/noise fields, radar detection, antenna switch controls, chain masks, power rate registers, spur/filter masks, calibration measurement registers, PHY mode selection, CCK detection/control, 2 GHz gain, TX power control, and chain-specific CCA/ext-CCA fields.

## Control Flow

The header has no executable flow. `phy.c` uses it to build register write batches, extract noise-floor values, apply EEPROM modal fields, program target power tables, configure HT/turbo mode, and enable heavy clipping. Debug and MAC paths indirectly depend on these constants when reporting PHY noise or setting TPC.

## State and Persistence Behavior

Definitions here describe persistent PHY hardware state, not C storage. Writes to these registers affect channel tuning, receive sensitivity, calibration, transmit power, radar detection, spur mitigation, RF/ADC behavior, chain masks, and HT bandwidth behavior until the next channel change or reset.

## Dependencies and Integration Points

It is included by `phy.c` and depends on the broader driver environment for `BIT()` and bitfield helper usage. Its constants must align with `hw.h`, EEPROM calibration fields, firmware RF init expectations, and AR9170/AR5416 hardware documentation.

## Risks and Edge Cases

Because most fields are raw hardware ABI values, incorrect masks or shifts can silently corrupt PHY programming. One macro definition for `AR9170_PHY_REG_CAL_MEAS_1(_i)` contains a line-continuation spacing anomaly in the expression text; it currently compiles in context but should be treated carefully if edited. Per-chain offsets assume the hardware's chain spacing layout.

## Test Signals

Compile all PHY users after any register-map edit. Run channel-change and noise-floor tests across band/bandwidth combinations. Use register traces or hardware diagnostics to verify `SET_VAL`/`GET_VAL` fields for CCA, turbo, RF control, power, heavy clip, and chain masks match expected bit positions.
