# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/table.c

Purpose: `table.c` contains the static register-programming tables for RTL8723AE MAC, PHY, PHY power-group offsets, RF path A, and AGC setup.

Important APIs/data: exported arrays are `RTL8723EPHY_REG_1TARRAY`, `RTL8723EPHY_REG_ARRAY_PG`, `RTL8723E_RADIOA_1TARRAY`, `RTL8723EMAC_ARRAY`, and `RTL8723EAGCTAB_1TARRAY`. The arrays are sized by constants in `table.h` and consumed by `phy.c`.

Control flow: no functions execute here. `phy.c` iterates arrays as address/value pairs for MAC, PHY, AGC, and RF tables; the PG array is interpreted as address/mask/data triples used to populate tx-power offset state. Special sentinel addresses such as `0xfe` through `0xf9` in PHY/RF arrays encode millisecond or microsecond delays in the loader.

State and persistence: data is static and read-only by convention, though not declared `const`. Loading these tables persists values into MAC, BB, RF, AGC, and power-index state. PG table data persists in `rtlphy->mcs_txpwrlevel_origoffset`.

Dependencies/integration: included through `table.h`; used by `rtl8723e_phy_mac_config`, `_rtl8723e_phy_config_bb_with_headerfile`, `_rtl8723e_phy_config_bb_with_pgheaderfile`, and `rtl8723e_phy_config_rf_with_headerfile`.

Risks: table corruption or length mismatch can misprogram hardware with little diagnostic context. Arrays are writable globals, which increases accidental mutation risk. Values are magic vendor calibration data and are hard to review semantically. Delay sentinels depend on loader logic skipping normal register writes for those entries.

Test signals: successful BB/RF/MAC initialization, no table overrun under KASAN/UBSAN, expected delay handling, register dumps matching vendor baseline, association stability, RX sensitivity, tx power, and calibration behavior after table load.
