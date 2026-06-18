# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/rf.c

## Purpose
Implements RTL8192DE RF6052 radio setup and helper routines for temporarily enabling or powering down the other PHY/radio in dual-MAC dual-PHY configurations. It is the RF table-loading bridge between `phy.c`, static RF arrays in `table.c`, and the dual-MAC DBI access model.

## Important APIs, Types, And Functions
`rtl92d_phy_enable_anotherphy()` checks whether the peer MAC is powered and, if needed, enables BB/RF power through DBI writes. `rtl92d_phy_powerdown_anotherphy()` powers the peer radio path down when the peer MAC is not active. `rtl92d_phy_rf6052_config()` selects one or two RF paths, handles single-PHY versus dual-MAC dual-PHY startup, configures RF environment bits, loads `radioa_txt` or `radiob_txt` through `rtl92d_phy_config_rf_with_headerfile()`, restores RF environment state, and powers down temporarily enabled radios.

## Control Flow
RF configuration first derives `num_total_rfpath` from `rtlphy->rf_type`. In dual-MAC dual-PHY mode it may require MAC0 on 2.4G to pre-load Radio B via PHY1, or MAC1 on 5G to pre-load Radio A via PHY0. If the peer MAC is already on, it assumes both radio tables are loaded and returns success. For each selected RF path, it saves RFENV bits, enables RF serial interface environment, sets address/data length fields, loads the appropriate RF table, then restores RFENV. Temporary peer PHY access is unwound by `rtl92d_phy_powerdown_anotherphy()`.

## State And Persistence
The file mutates `rtlhal->during_mac0init_radiob`, `rtlhal->during_mac1init_radioa`, and `rtlphy->num_total_rfpath`. Those flags alter BB register access in `phy.c` so reads/writes go through DBI to the peer PHY while RF tables are loaded. Actual persistent radio state lives in hardware RF registers populated from table arrays.

## Dependencies And Integration Points
Depends on rtlwifi register I/O, DBI helpers from 8192DE hardware code, common PHY/RF definitions, RF content identifiers from `phy.h`, DM and hardware headers, and the RF register tables in `table.c`. It is called through `rtl92d_phy_rf_config()` in `phy.c` during hardware initialization.

## Risks
The dual-MAC path is fragile because control flags redirect later BB register operations. A failure before flags are cleared could make subsequent register access target the wrong PHY. The "peer MAC already on" shortcut assumes the radio tables have already been loaded, which depends on startup ordering. Error handling returns the current status but does not perform elaborate restoration beyond the normal environment restore/powerdown paths.

## Test Signals
Test single-MAC single-PHY, dual-MAC dual-PHY MAC0-first, and MAC1-first initialization. Hardware logs should show successful Radio A/B table loading, no "Radio[%d] Fail!!" messages, correct RF path count, and valid RF register readback after initialization. Dual-MAC tests should verify one interface does not break the other's radio state.
