# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852a_table.h

Purpose: This header is the table declaration boundary for the RTL8852A variant of the RTW89 driver. It exposes immutable PHY/RF/NCTL configuration tables, transmit-power tracking configuration, and default RFE parameters to the 8852A chip implementation while keeping the table definitions in separate generated or vendor-derived table translation units.

Important APIs, types, and data: The exported symbols are `rtw89_8852a_phy_bb_table`, `rtw89_8852a_phy_radioa_table`, `rtw89_8852a_phy_radiob_table`, `rtw89_8852a_phy_nctl_table`, `rtw89_8852a_trk_cfg`, and `rtw89_8852a_dflt_parms`. The types come from `core.h`: `struct rtw89_phy_table` for baseband/radio/NCTL register sequences, `struct rtw89_txpwr_track_cfg` for thermal power tracking swing tables, and `struct rtw89_rfe_parms` for front-end parameter defaults.

Control flow: There is no executable flow in this file. Runtime behavior is indirect: the 8852A chip info points at these symbols, and common PHY setup code later parses the `rtw89_phy_table` descriptors to program BB, RF path A/B, and NCTL registers. The tracking and RFE structures are read by TX power and RF front-end logic when selecting temperature compensation and regulatory/front-end limits.

State and persistence: The declarations refer to const data. The header creates no driver state, but parsing the declared tables persists hardware register state until reset, power transition, channel reconfiguration, or a later table overrides it. Any consumer assumes the table objects have static lifetime.

Dependencies and integration points: Depends only on `core.h` and the matching 8852A table C files. It is normally consumed by `rtw8852a.c` and bus glue such as `rtw8852ae.c`/`rtw8852au.c` through the 8852A chip info. It also sits in the broader RTW89 table-parser contract shared with `phy.c`.

Risks: This is a small ABI header, so the main risk is declaration/definition drift. A missing or renamed table breaks the module link; a semantically wrong table with the same type compiles but can misprogram RF paths, baseband, NCTL, or TX power tracking. The dual-radio declarations must remain path-specific because later chip info distinguishes radio A and radio B tables.

Test signals: Build and module link validate symbol names and types. Runtime validation comes from successful RTL8852A probe on PCIe and USB variants, firmware load, PHY table parsing without register-write errors, 2.4 GHz and 5 GHz association, channel changes, thermal/TX power tracking debug output, and absence of RF/BB initialization failures.
