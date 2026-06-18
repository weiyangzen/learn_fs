# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bt.h

Purpose: Minimal public RTL8852BT chip header. It publishes path-count constants and the external `rtw8852bt_chip_info` symbol.

Important APIs and types: Defines `RF_PATH_NUM_8852BT` and `BB_PATH_NUM_8852BT` as two, and declares `extern const struct rtw89_chip_info rtw8852bt_chip_info`.

Control flow: No executable logic. Bus modules consume the chip-info declaration; RFK code uses path counts for loops and state-array bounds.

State and persistence: No mutable state. Constants determine RF/BB path iteration and therefore calibration coverage.

Dependencies and integration points: Includes `core.h`; used by `rtw8852bt.c`, `rtw8852bt_rfk.c`, and `rtw8852bte.c`.

Risks: Changing path counts without auditing DPK/TSSI/IQK arrays, DBCC selection, and RF register offset logic risks out-of-bounds access or skipped paths.

Test signals: Build coverage and runtime RFK logs for both RF paths.
