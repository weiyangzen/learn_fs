<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cu.c

## Purpose

This file is the USB bus binding module for RTW8821CU-family USB adapters. It declares the supported USB vendor/product/interface matches, forwards matching interfaces to the shared `rtw88` USB probe path, and registers disconnect handling.

## Important APIs, Types, and Functions

- `rtw_8821cu_id_table[]`: USB match table using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)` for vendor-specific interfaces. Most entries use `RTW_USB_VENDOR_ID_REALTEK`; additional third-party entries include D-Link (`0x2001:0x331d`), Edimax (`0x7392:0xc811`, `0x7392:0xd811`), and Mercusys (`0x2c4e:0x0105`). All entries set `.driver_info = (kernel_ulong_t)&rtw8821c_hw_spec`.
- `MODULE_DEVICE_TABLE(usb, rtw_8821cu_id_table)`: exports USB aliases for autoload.
- `rtw_8821cu_probe()`: thin wrapper that calls `rtw_usb_probe(intf, id)`.
- `rtw_8821cu_driver`: `struct usb_driver` with `.probe = rtw_8821cu_probe`, `.disconnect = rtw_usb_disconnect`, and `.id_table = rtw_8821cu_id_table`.
- `module_usb_driver(rtw_8821cu_driver)`: standard USB driver registration wrapper.

## Control Flow

When the module loads, it registers with the USB core. A matching vendor-specific USB interface triggers `rtw_8821cu_probe`, which delegates directly to `rtw_usb_probe`. The common USB probe reads `id->driver_info`, selects `rtw8821c_hw_spec`, creates the `rtw_dev`, configures USB transport resources, loads firmware, parses efuse, applies tables, and registers mac80211 state. Disconnect events go to `rtw_usb_disconnect`.

The local probe wrapper exists mostly to satisfy the expected USB probe signature and keep the ID table associated with the shared USB implementation.

## State and Persistence Behavior

The file contains static USB ID and driver metadata. It does not maintain runtime state or persistent configuration. Per-device state is owned by USB core structures and the common `rtw88` USB layer after probe. The module's persistent user-visible effect is the USB modalias list, which controls autoloading for many branded adapters.

## Dependencies and Integration Points

- Linux USB and module frameworks: `<linux/usb.h>`, `<linux/module.h>`.
- `usb.h`: shared `rtw88` USB probe/disconnect implementation and `RTW_USB_VENDOR_ID_REALTEK`.
- `main.h` and `rtw8821c.h`: common driver types and the 8821C chip spec.
- `rtw8821c.c` and `rtw8821c_table.c`: executable chip behavior and hardware table payloads used after probe.

## Risks

- USB ID coverage is product-facing. Missing IDs mean otherwise compatible adapters do not bind; incorrect IDs could bind an incompatible Realtek part to the 8821C chip spec.
- Vendor-specific interface matching (`0xff/0xff/0xff`) is broad at the interface class level, so product/vendor IDs must be precise.
- No local suspend/resume hooks are provided in this `struct usb_driver`; any runtime or system PM support depends on shared USB-layer registration and kernel USB defaults.
- The wrapper does not inspect interface altsettings or endpoints; endpoint validation must be done by `rtw_usb_probe`.

## Test Signals

- `modinfo` should list all USB aliases in the table, including branded D-Link, Edimax, and Mercusys IDs.
- Hotplug tests for representative Realtek and third-party IDs should trigger `rtw_usb_probe` and load `rtw88/rtw8821c_fw.bin`.
- Disconnect/replug stress should validate `rtw_usb_disconnect` cleanup.
- Traffic tests over USB 2 and USB 3 hosts should confirm endpoint setup, aggregation, and firmware operation through the shared USB transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821cu.c -->
