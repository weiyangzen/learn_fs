# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/m88ds3103_priv.h

## Purpose
`m88ds3103_priv.h` defines private firmware names, chip IDs/types, runtime state, register-value table format, and chip/system-specific initialization tables for the M88DS3103 driver.

## Important APIs, Types, and Functions
Firmware macros name `dvb-demod-m88ds3103b.fw`, `dvb-demod-m88ds3103c.fw`, `dvb-demod-m88ds3103.fw`, and `dvb-demod-m88rs6000.fw`. Chip macros define IDs for DS3103, RS6000, and DS3103C plus logical chiptypes. `struct m88ds3103_dev` carries I2C clients, regmap, config, frontend, status, firmware warmth, mux, chip identity, MCLK, BER counters, and internal-device address. `struct m88ds3103_reg_val` backs static register tables for DS3103 DVB-S, DS3103 DVB-S2, RS6000 DVB-S, RS6000 DVB-S2, and DS3103C initialization.

## Control Flow
`m88ds3103.c` selects one of these register tables during set-frontend based on delivery system and chip id, then writes it through `m88ds3103_wr_reg_val_tab()`. The firmware name macros are selected in init when the chip is cold. The state structure is allocated at probe and freed at remove.

## State and Persistence
The state structure holds all runtime software state for the driver. Register tables and firmware names are static constants; hardware state remains volatile and is restored by init/tune paths.

## Dependencies and Integration Points
The header includes DVB frontend, public M88DS3103 config, integer log/math, firmware, I2C mux, and regmap headers. It is private to the driver implementation.

## Risks and Edge Cases
Large static tables are hardware magic values; an incorrect chip/table pairing would produce tuning failures that are hard to diagnose. The private state contains both copied config and a config pointer, so code must keep them synchronized through `dev->cfg = &dev->config`.

## Test Signals
Firmware selection should match chip type, register table selection should match DVB-S/DVB-S2 and chip id, state counters should initialize and accumulate correctly, and probe/remove should handle internal dummy clients and mux state for all chip variants.
