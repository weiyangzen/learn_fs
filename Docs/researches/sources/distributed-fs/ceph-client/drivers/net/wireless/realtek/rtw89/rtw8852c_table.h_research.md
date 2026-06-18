# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_table.h

## Purpose
This header is the external table contract for the RTL8852C rtw89 chip support. It does not define data; it declares the BB, gain, radio, NCTL, TSSI, tracking, and default RFE parameter objects consumed by the 8852C chip descriptor and PHY initialization paths elsewhere in the driver.

## Important APIs, Types, and Data
- Includes `core.h` for `struct rtw89_phy_table`, `struct rtw89_phy_tssi_dbw_table`, `struct rtw89_txpwr_track_cfg`, and `struct rtw89_rfe_parms`.
- Declares `rtw89_8852c_phy_bb_table`, `rtw89_8852c_phy_bb_gain_table`, `rtw89_8852c_phy_radioa_table`, `rtw89_8852c_phy_radiob_table`, and `rtw89_8852c_phy_nctl_table`.
- Declares `rtw89_8852c_tssi_dbw_table`, `rtw89_8852c_trk_cfg`, and `rtw89_8852c_dflt_parms`.

## Control Flow and Integration
There is no executable control flow. The header is included by 8852C implementation files to bind generated/static register programming tables into the chip-info initialization pipeline. Consumers use the declared objects to load PHY/RF tables, configure TSSI behavior, and select default RFE parameters during probe or hardware setup.

## State and Persistence
The file owns no mutable state. The declared objects are expected to be immutable `const` definitions in matching table source files and become part of the module image.

## Dependencies
The declarations depend on rtw89 core table structures and on matching definitions being linked into the same driver build. The source path indicates Linux kernel driver code under Realtek rtw89, not Ceph-specific logic despite the repository prefix.

## Risks
- Missing or mismatched table definitions will fail link or cause chip descriptor setup to reference unavailable data.
- Table content errors in the defining C files can cause hardware misprogramming, but this header has no validation layer.
- Because these are extern declarations, build configuration must keep producer and consumer files in sync.

## Test Signals
- Compile/link coverage is the primary signal: all externs must resolve.
- Runtime bring-up should show successful 8852C PHY/RF table load, no register-table parse warnings, valid TSSI tracking, and normal association/throughput on both RF paths.
