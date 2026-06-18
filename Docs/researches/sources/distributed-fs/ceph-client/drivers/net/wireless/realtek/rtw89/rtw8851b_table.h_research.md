# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_table.h

## Purpose
This header is the table export contract for the RTL8851B RTW89 chip support. It does not define data itself; it exposes board/chip parameter tables produced by companion table sources to the 8851B core and bus-specific modules.

## Important APIs, Types, and Data
- Includes `core.h` for RTW89 table and RFE types.
- Exports `rtw89_8851b_phy_bb_table`, `rtw89_8851b_phy_bb_gain_table`, `rtw89_8851b_phy_radioa_table`, and `rtw89_8851b_phy_nctl_table` as `struct rtw89_phy_table` instances used during PHY/RF initialization.
- Exports `rtw89_8851b_trk_cfg` as `struct rtw89_txpwr_track_cfg` for thermal/TSSI tracking compensation.
- Exports `rtw89_8851b_dflt_parms` and `rtw89_8851b_rfe_parms_conf[]` for radio front-end parameter selection.

## Control Flow and Integration
The header has no runtime control flow. Its declarations are consumed by 8851B chip metadata, most likely in `rtw8851b.c` and bus wrappers such as PCI/USB modules. Initialization code passes these table addresses into generic RTW89 parser helpers, which then write BB, RF, gain, NCTL, power-tracking, and RFE values to hardware.

## State and Persistence
No state is stored here. The declared objects are `const`, so persistence is compile-time data in the kernel module image. Runtime state is created by consumers after parsing tables into hardware registers and `rtw89_dev` fields.

## Dependencies
This file depends on `core.h` for the `rtw89_phy_table`, `rtw89_txpwr_track_cfg`, `rtw89_rfe_parms`, and `rtw89_rfe_parms_conf` type definitions. It also depends on matching definitions in table implementation files; missing or renamed definitions would produce link failures for any 8851B module that references them.

## Risks
- The header is only declarations, so the main risk is drift between declarations and generated/handwritten table definitions.
- RFE and calibration tables are hardware-sensitive; incorrect table definitions behind these declarations can cause bring-up failures, poor RF performance, or regulatory power issues even though this header compiles cleanly.
- Because declarations are shared across bus variants, changing exported names has broad build impact.

## Test Signals
- Build/link coverage for RTL8851B modules verifies symbol availability.
- Device probe logs and RTW89 debug categories for table parsing, RFK, TSSI, and TX power verify that consumers can load and apply the tables.
- Hardware smoke tests should include association, scan, TX power, and thermal tracking on known 8851B RFE variants.
