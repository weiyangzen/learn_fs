# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8812au.c

## Purpose
`rtw8812au.c` is the USB bus binding for RTL8812AU-class devices. It declares USB vendor/product IDs that should bind to the rtw88 8812A chip implementation, registers a `usb_driver`, and points all matching devices at `rtw8812a_hw_spec` through `driver_info`.

## Important APIs and data
- `rtw_8812au_id_table[]`: `struct usb_device_id` array using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)` for Realtek and many OEM product IDs. Each entry stores `(kernel_ulong_t)&rtw8812a_hw_spec`.
- `MODULE_DEVICE_TABLE(usb, rtw_8812au_id_table)`: exports modalias information for module autoloading.
- `rtw_8812au_driver`: `struct usb_driver` with `.name = KBUILD_MODNAME`, `.id_table`, `.probe = rtw_usb_probe`, and `.disconnect = rtw_usb_disconnect`.
- `module_usb_driver(rtw_8812au_driver)`: creates module init/exit registration boilerplate.

## Control flow and state behavior
There is no device-control logic in this file. The kernel USB core matches a connected interface against `rtw_8812au_id_table`, module autoloading can occur via the generated device table, and the generic rtw88 USB probe receives the matched ID. Probe then uses the `driver_info` pointer to initialize the device with `rtw8812a_hw_spec`. Disconnect is delegated to the generic rtw88 USB disconnect path. Runtime state is owned by the USB core and rtw88 core, not this file.

## Dependencies and integration points
The file includes Linux USB/module headers, rtw88 `main.h`, `usb.h`, and `rtw8812a.h`. It integrates the bus-neutral chip implementation in `rtw8812a.c` with USB transport helpers `rtw_usb_probe()` and `rtw_usb_disconnect()`. The ID table includes Realtek product IDs (`0x8812`, `0x881a`, `0x881b`, `0x881c`) and OEM IDs from NEC, Buffalo, I-O DATA, Belkin, ZyXEL, Logitec, Abocom, Netgear, ASUS, Sitecom, Hawking, WD, Linksys, Amped Wireless, EnGenius, D-Link, Planex, TRENDnet, TP-Link, Tenda, and Edimax.

## Risks and edge cases
- The broad vendor-specific interface match (`0xff/0xff/0xff`) is appropriate for Realtek USB Wi-Fi devices but can bind incorrectly if an OEM product ID is reused for a non-8812A interface.
- A missing product ID prevents autoload/probe for that adapter even though the chip support exists.
- All entries point to the same `rtw8812a_hw_spec`; devices with board-specific quirks must be handled through EFUSE/RFE data or additional matching logic elsewhere.
- Probe/disconnect behavior depends entirely on generic USB code and the chip spec being linked into the module.

## Test signals
Test signals include `modinfo` showing the listed USB aliases, hotplug autoload for supported adapters, `rtw_usb_probe()` receiving `rtw8812a_hw_spec`, firmware request for `rtw88/rtw8812a_fw.bin`, successful disconnect without leaks or crashes, and no unintended binding reports for adjacent Realtek USB devices.
