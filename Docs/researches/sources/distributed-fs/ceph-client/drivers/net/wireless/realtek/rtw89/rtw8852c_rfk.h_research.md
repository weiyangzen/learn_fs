# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852c_rfk.h

## Purpose

`rtw8852c_rfk.h` declares the RTL8852C RF calibration and RF channel-control interface implemented by `rtw8852c_rfk.c`. It is the narrow boundary used by `rtw8852c.c` to register RFK callbacks in `rtw8852c_chip_ops` and to coordinate scan, channel-context, and channel-change behavior.

## Important APIs, types, and data

The header declares:

- `rtw8852c_mcc_get_ch_info()` for MCC/channel-context RFK table selection.
- One-shot calibration entry points: `rtw8852c_rck()`, `rtw8852c_dack()`, `rtw8852c_iqk()`, `rtw8852c_rx_dck()`, `rtw8852c_dpk()`, and `rtw8852c_tssi()`.
- Tracking and initialization entry points: `rtw8852c_rx_dck_track()`, `rtw8852c_dpk_init()`, `rtw8852c_dpk_track()`, `rtw8852c_lck_init()`, and `rtw8852c_lck_track()`.
- Scan/channel support: `rtw8852c_tssi_scan()`, `rtw8852c_tssi_cont_en_phyidx()`, `rtw8852c_wifi_scan_notify()`, `rtw8852c_set_channel_rf()`, and `rtw8852c_rfk_chanctx_cb()`.

All functions operate on `struct rtw89_dev *` plus PHY, channel, channel-context, or scan-state parameters. There are no exported types or mutable globals in the header.

## Control flow

The header itself has no executable logic. It defines the callable RFK flow surface:

- Initialization code in `rtw8852c.c` calls LCK/DPK init and initial RCK/DACK/RX-DCK through these declarations.
- Channel RFK code calls MCC info capture, RX DCK, IQK, TSSI, and DPK.
- Channel switching calls `rtw8852c_set_channel_rf()` after MAC and BB channel programming, and gates continuous TSSI with `rtw8852c_tssi_cont_en_phyidx()`.
- Periodic tracking calls DPK, LCK, and RX DCK trackers.
- Scan and channel-context code calls scan notification and RFK channel-context callback hooks.

## State and persistence behavior

The API is stateful through `struct rtw89_dev`. Callers do not pass calibration result buffers; implementations store and reuse calibration state inside `rtwdev->dack`, `rtwdev->iqk`, `rtwdev->rx_dck`, `rtwdev->dpk`, `rtwdev->tssi`, `rtwdev->lck`, and `rtwdev->rfk_mcc`. This means call order matters: init routines establish baselines and flags used by later channel and tracking routines.

## Dependencies and integration points

The header includes `core.h` for `struct rtw89_dev`, `struct rtw89_chan`, `enum rtw89_phy_idx`, and `enum rtw89_chanctx_idx`. It is included by `rtw8852c.c` and implemented by `rtw8852c_rfk.c`.

Its functions are integrated into the chip ops and channel-context listener rather than exported as standalone kernel symbols. The dependency direction is intentionally one-way: the main chip file knows the RFK public API, while the RFK implementation can use chip constants from `rtw8852c.h` and generated RFK tables.

## Risks and edge cases

- Prototype drift between this header and `rtw8852c_rfk.c` would break chip ops wiring at compile time.
- Callers must pass the correct PHY and channel-context index under DBCC/MCC. Incorrect inputs can select the wrong RF path or calibration cache.
- Several functions assume RFK state has been initialized. Calling trackers before `rtw8852c_lck_init()` or `rtw8852c_dpk_init()` can produce weak baselines or disabled calibration behavior.
- `rtw8852c_tssi_cont_en_phyidx()` requires a valid current channel pointer because enabling continuous TSSI rewrites efuse-derived DE values for that channel.

## Test signals

- A normal build should validate every declaration against its implementation and the `rtw8852c_chip_ops` assignments.
- Runtime RFK debug should show the declared entry points being reached in the expected order: init RFK, channel RFK, scan notifications, and track callbacks.
- DBCC/MCC tests should explicitly cover non-default PHY/channel-context parameters because most APIs carry those selectors.
- Channel-change tests should confirm `rtw8852c_set_channel_rf()` is paired with MAC/BB programming and that TSSI continuous enable/disable is restored around the change.
