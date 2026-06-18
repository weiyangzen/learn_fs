# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851b_rfk.h

## Purpose

`rtw8851b_rfk.h` declares the RTL8851B RF calibration interface used by the chip implementation. It exposes calibration, tracking, scan-notification, TSSI, and RF channel setup entry points while keeping register-sequence details private to `rtw8851b_rfk.c`.

## Important APIs, Types, And Functions

The header declares AACK/LCK/RCK/DACK, IQK, RX-DCK, DPK init/calibration/tracking, TSSI normal and scan setup, Wi-Fi scan notification, and RF channel programming. Signatures use `struct rtw89_dev`, `enum rtw89_phy_idx`, `enum rtw89_chanctx_idx`, and `struct rtw89_chan`.

## Control Flow

There is no executable code. The intended flow is chip initialization calling init routines, channel changes calling RX-DCK/IQK/TSSI/DPK, periodic tracking calling DPK/LCK tracking, scan code calling `rtw8851b_wifi_scan_notify()`, and channel setup calling `rtw8851b_set_channel_rf()`.

## State And Persistence Behavior

The declared functions mutate `rtwdev` calibration state and RF/BB hardware registers. The header itself stores no state but carries the PHY/channel context needed to bind calibration state to the active channel.

## Dependencies And Integration Points

It includes `core.h` for rtw89 types, is consumed by `rtw8851b.c`, and is implemented by `rtw8851b_rfk.c`.

## Risks

Prototype drift breaks chip-op glue. The functions return `void`, so runtime failures are mostly visible through logs and hardware behavior. Callers must use the high-level wrappers when scheduler/BTC protection is required.

## Test Signals

Compile coverage catches prototype mismatch. Runtime signals are RFK logs during init, channel changes, scans, and periodic tracking, plus successful invocation through `rtw8851b_chip_ops`.
