# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8723du.c

## Purpose
This is the USB module glue for Realtek RTL8723DU devices in rtw88. It matches Realtek and Edimax USB IDs and delegates common USB initialization to rtw88 using `rtw8723d_hw_spec`.

## Important APIs, Types, And Functions
`rtw_8723du_id_table[]` includes a Realtek 0xd723 8723DU 1x1 entry and an Edimax EW-7611ULB V2 entry (`0x7392:0xd611`), both using `rtw8723d_hw_spec` as driver info. `rtw8723du_probe()` is a thin wrapper around `rtw_usb_probe()`. `rtw_8723du_driver` registers USB callbacks for probe and disconnect through `module_usb_driver()`.

## Control Flow
USB core matching invokes `rtw8723du_probe()`, which immediately calls `rtw_usb_probe(intf, id)`. The common USB probe retrieves `rtw8723d_hw_spec` from the device ID and initializes firmware, power, MAC/PHY, TX/RX, and mac80211 integration. Disconnect uses `rtw_usb_disconnect()`.

## State And Persistence
This file owns only static ID and driver structures. Runtime state is created by common USB and rtw88 core code. Hardware programming and firmware persistence are defined by the RTL8723D chip descriptor.

## Dependencies And Integration Points
It depends on Linux USB/module APIs, `main.h`, `usb.h`, and `rtw8723d.h`. It is the USB bus integration point for RTL8723D-family hardware and selected third-party adapters.

## Risks
Wrong USB interface matching could bind non-compatible vendor-specific devices because the table uses class/subclass/protocol `0xff`. The wrapper has no PM callbacks beyond common USB behavior visible through `rtw_usb_probe()`/disconnect, so suspend behavior depends on shared USB code. Device-specific quirks for the Edimax adapter would need to be handled elsewhere.

## Test Signals
Signals include USB modalias autoload for both IDs, successful `rtw_usb_probe()`, firmware load, interface creation, traffic over USB, clean disconnect, and no unintended binding to unrelated vendor-specific Realtek interfaces.
