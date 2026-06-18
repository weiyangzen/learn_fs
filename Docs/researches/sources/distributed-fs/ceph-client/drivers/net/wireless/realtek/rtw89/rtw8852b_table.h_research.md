# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852b_table.h

Purpose: Declares the externally defined RTL8852B PHY, RF, NCTL, transmit-power tracking, and default RFE parameter tables used by the common 8852B chip implementation. It is a small contract header between `rtw8852b_table.c` and chip setup code in `rtw8852b.c`.

Important APIs and types: The exports are `rtw89_8852b_phy_bb_table`, `rtw89_8852b_phy_bb_gain_table`, `rtw89_8852b_phy_radioa_table`, `rtw89_8852b_phy_radiob_table`, `rtw89_8852b_phy_nctl_table`, `rtw89_8852b_trk_cfg`, and `rtw89_8852b_dflt_parms`. All are `const` table objects using RTW89 core types.

Control flow: No executable logic. Chip registration points table pointers at these symbols, then RTW89 parser code writes the referenced data during initialization and calibration.

State and persistence: Immutable declarations only. Hardware state persists only after the tables are parsed into BB/RF/NCTL registers or power-tracking configuration.

Dependencies and integration points: Includes `core.h`; consumed by `rtw8852b.c`; definitions live in `rtw8852b_table.c`.

Risks: Declaration/definition mismatches break link. Incorrect table wiring can silently program the wrong register group.

Test signals: Build/link coverage for 8852B, successful probe table parsing, and RF/BB bring-up on PCI/USB 8852B devices.
