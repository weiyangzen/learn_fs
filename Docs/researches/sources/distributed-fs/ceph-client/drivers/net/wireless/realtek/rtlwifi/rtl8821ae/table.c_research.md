# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/table.c

## Purpose
Stores the generated hardware programming tables for RTL8812AE and RTL8821AE. These arrays provide PHY register initialization, per-rate power group values, RF radio path programming, MAC register setup, AGC tables, and regulatory TX power limit records consumed by `rtl8821ae/phy.c`.

## Important APIs, Types, And Functions
There are no functions. Exported data symbols include `RTL8812AE_PHY_REG_ARRAY`, `RTL8821AE_PHY_REG_ARRAY`, `RTL8812AE_PHY_REG_ARRAY_PG`, `RTL8821AE_PHY_REG_ARRAY_PG`, `RTL8812AE_RADIOA_ARRAY`, `RTL8812AE_RADIOB_ARRAY`, `RTL8821AE_RADIOA_ARRAY`, `RTL8812AE_MAC_REG_ARRAY`, `RTL8821AE_MAC_REG_ARRAY`, `RTL8812AE_AGC_TAB_ARRAY`, `RTL8821AE_AGC_TAB_ARRAY`, `RTL8812AE_TXPWR_LMT`, `RTL8821AE_TXPWR_LMT`, and their `ARRAY_SIZE` length variables.

## Control Flow
The file contributes static initialization data only. At runtime, `phy.c` selects arrays by hardware type and walks their register/value tuples. Several arrays contain conditional marker words such as `0x80000000`, `0x90000000`, `0xA0000000`, and `0xB0000000`; the PHY table parser interprets these as board/interface/platform conditions rather than direct register addresses. TX power limit string arrays are parsed as repeated regulation, band, bandwidth, rate section, RF path count, channel, and limit fields.

## State And Persistence
The arrays are compiled into the module image and are read-only by convention, although the `u32` arrays are not declared `const`. They represent persistent vendor calibration defaults until the module is rebuilt. Applying the tables mutates device registers but this file does not store runtime state.

## Dependencies And Integration Points
Depends on `<linux/kernel.h>` for `ARRAY_SIZE` and on `table.h` for declarations. The main consumer is `rtl8821ae/phy.c`, which loads MAC, BB, AGC, RF, power-group, and TX power limit tables during hardware initialization and regulatory setup. `rf.c` depends on the calibration results produced after these tables are applied.

## Risks And Edge Cases
The data is dense and hardware-specific; a single wrong tuple can break RF bring-up, calibration, receive sensitivity, or regulatory compliance. Length symbols are element counts, not tuple counts, so consumers must step with the correct stride for each table. Because the arrays are mutable globals, accidental writes from parser bugs would corrupt future reinitialization. TX power limit strings are untyped, so parser assumptions about seven-field records and channel names must remain aligned with this file.

## Test Signals
Primary signals are successful hardware initialization on both RTL8812AE and RTL8821AE, PHY/RF table load logs, channel scans on 2.4 GHz and 5 GHz, AGC sensitivity, RF path A/B operation for RTL8812AE, and regulatory TX power limit behavior across FCC/ETSI/MKK/WW. Static checks should verify length symbols match `ARRAY_SIZE` and consumers never step past array bounds.
