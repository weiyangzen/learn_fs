# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822bu.c

## Purpose

`rtw8822bu.c` is the USB module binding for RTL8822BU and many rebadged USB adapters using the same RTL8822B hardware. It maintains the USB VID/PID match table, associates every entry with `rtw8822b_hw_spec`, and registers a `usb_driver` that delegates probe/disconnect to the shared rtw88 USB transport.

## Important APIs and Types

- `rtw_8822bu_id_table[]`: `struct usb_device_id` table using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)` for vendor-specific Realtek-style interfaces.
- Each table entry sets `.driver_info = (kernel_ulong_t)&rtw8822b_hw_spec`.
- The table covers Realtek default IDs and adapters from Edimax, ASUS, D-Link, Linksys, TP-Link, Netgear, Hawking, LiteOn, TRENDnet, ELECOM, Mercusys, and Buffalo.
- `rtw8822bu_probe()` is a thin wrapper around `rtw_usb_probe(intf, id)`.
- `rtw_8822bu_driver` registers `.probe = rtw8822bu_probe` and `.disconnect = rtw_usb_disconnect`.
- `MODULE_DEVICE_TABLE(usb, rtw_8822bu_id_table)` and `module_usb_driver()` provide autoload and registration.

## Control Flow and Integration

USB core interface matching selects an ID entry, then `rtw8822bu_probe()` calls `rtw_usb_probe()`. The generic rtw88 USB path uses `id->driver_info` to obtain RTL8822B chip capabilities, creates the device, configures USB aggregation and endpoints, loads firmware/tables, and registers with mac80211. Disconnect calls the shared cleanup path.

## State and Persistence

The file owns a static device-ID allowlist. Runtime state is allocated by the USB transport and chip code. No suspend/resume callbacks are explicitly wired here; USB PM behavior depends on the shared `rtw_usb` layer and driver-core defaults. The static ID table is effectively persistent kernel configuration for which retail adapters bind to this module.

## Dependencies

It depends on Linux USB/module APIs and rtw88 headers `main.h`, `usb.h`, and `rtw8822b.h`. The common USB path contains transport behavior such as endpoint setup, TX/RX aggregation, and chip-specific USB quirks keyed from `rtw8822b_hw_spec`.

## Risks

- The match table is broad and uses vendor-specific interface class masks. Adding IDs without confirming the chipset can bind unrelated devices.
- Missing IDs result in supported adapters not autoloading even though the core chip support exists.
- Probe is only a wrapper, so transport regressions or chip-spec mistakes are surfaced as device bring-up failures in all matched adapters.
- Lack of local PM callbacks means runtime suspend/wake behavior should be verified in the shared USB layer.

## Test Signals

- `modinfo` should expose all intended USB aliases.
- Hotplugging each known VID/PID should call `rtw_usb_probe()` with `rtw8822b_hw_spec`.
- Functional tests should cover association, throughput, disconnect/reconnect, module unload, and autosuspend/runtime PM for representative USB2 and USB3 adapters.
