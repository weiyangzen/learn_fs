# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt_rfk_table.h

Purpose: Declares all RFK TSSI table symbols provided by `rtw8852bt_rfk_table.c` for use by RTL8852BT RFK code.

Important APIs and types: Exports `const struct rtw89_rfk_tbl` declarations for common TSSI defaults, path A/B 2G/5G system defaults, init TX power, HE TB TX power, DCK, DAC gain, 2G/5G slope, per-path alignment defaults, and slope finalization tables.

Control flow: No executable logic. It enables conditional parser calls in `rtw8852bt_rfk.c`.

State and persistence: No mutable state. The declared tables are immutable; parser side effects become hardware state.

Dependencies and integration points: Includes `phy.h`; used by the RFK table definition and RFK calibration implementation.

Risks: Must stay synchronized with the `.c` file and TSSI helpers. Swapping path or band semantics may build but misprogram RF power tracking.

Test signals: Compile/link coverage, table parser coverage during TSSI, and channel sweeps that hit every alignment table.
