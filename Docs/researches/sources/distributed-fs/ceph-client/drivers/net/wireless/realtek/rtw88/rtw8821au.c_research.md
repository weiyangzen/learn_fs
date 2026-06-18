# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8821au.c

`rtw8821au.c` is the USB binding for RTL8821AU/RTL8811AU devices. Its ID table covers Realtek IDs and many vendor-branded adapters, all using vendor-specific interface wildcards and `.driver_info = &rtw8821a_hw_spec`. The `usb_driver` delegates probe and disconnect to the shared rtw88 USB layer.

Control flow is USB enumeration, modalias autoload, `rtw_usb_probe()`, transport/endpoint setup, and chip initialization through `rtw8821a_hw_spec`. Disconnect unwinds through `rtw_usb_disconnect()`. This file stores no mutable runtime state; USB queues, URBs, firmware, and RF/MAC state belong to shared rtw88 code and `rtw8821a.c`.

Dependencies are Linux USB/module APIs, `main.h`, `usb.h`, and `rtw8821a.h`. Risks are inaccurate VID/PID coverage or board-specific RF quirks hidden behind the common 8821A profile. Test signals include `modinfo` aliases, probe for representative vendor IDs, endpoint aggregation, firmware loading, 2.4/5 GHz traffic, Bluetooth coexistence where present, suspend/resume, and removal during active transfers.
