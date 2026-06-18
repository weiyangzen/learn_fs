# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/table.c

## Purpose
Provides static RTL8192DE register programming tables used by PHY, RF, MAC, power-index, and AGC configuration code. The file is data-only and encodes chip-vendor initialization values for 2T operation, internal/external PA variants, 2.4G/5G AGC tables, and MAC register defaults.

## Important APIs, Types, And Functions
The exported arrays are `rtl8192de_phy_reg_2tarray`, `rtl8192de_phy_reg_array_pg`, `rtl8192de_radioa_2tarray`, `rtl8192de_radiob_2tarray`, `rtl8192de_radioa_2t_int_paarray`, `rtl8192de_radiob_2t_int_paarray`, `rtl8192de_mac_2tarray`, `rtl8192de_agctab_array`, `rtl8192de_agctab_5garray`, and `rtl8192de_agctab_2garray`. Each is declared with a matching length macro in `table.h`.

## Control Flow
There is no executable control flow. Consumers iterate these arrays as address/value pairs or, for `rtl8192de_phy_reg_array_pg`, address/mask/data triples. `phy.c` applies PHY and AGC tables via `rtl_set_bbreg()`, applies power-group data via `rtl92d_store_pwrindex_diffrate_offset()`, applies RF arrays via `rtl_rfreg_delay()`, and applies MAC defaults via byte writes.

## State And Persistence
The arrays are persistent module data. They do not change at runtime. Their values become persistent hardware state only after initialization writes them to device registers. Internal-PA efuse flags choose the internal-PA RF arrays for each path.

## Dependencies And Integration Points
Included by `phy.c` through `table.h`. The array layout and length macros must match consumer iteration steps exactly. Register names and semantics come from rtl8192d common headers, but this file stores raw numeric addresses and values.

## Risks
The main risk is data integrity. A wrong length macro, odd number of address/value entries, bad register value, or accidental edit can break hardware initialization without compiler errors. The large raw tables are hard to review and mostly validated only on real hardware. Internal-PA and band-specific table selection must match efuse parsing and current band state.

## Test Signals
Successful BB/RF/MAC initialization is the primary test. Hardware probe, RF register readback, scan sensitivity, 2.4G/5G association, TX power by rate, and AGC behavior validate the tables. Static checks can verify array sizes match length macros and address/value or address/mask/value grouping.
