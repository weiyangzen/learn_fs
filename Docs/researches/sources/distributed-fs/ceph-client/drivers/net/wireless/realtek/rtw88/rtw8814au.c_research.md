# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8814au.c

`rtw8814au.c` is the USB binding for RTL8814AU-family adapters. Its USB ID table lists Realtek and partner VID/PID pairs with vendor-specific interface class wildcards and stores `&rtw8814a_hw_spec` in `driver_info`. The registered `usb_driver` delegates `.probe` and `.disconnect` to `rtw_usb_probe()` and `rtw_usb_disconnect()`.

Control flow is USB match, module autoload, common rtw88 USB probe, endpoint/transport setup, and chip initialization through the RTL8814A spec. The file has no per-device mutable state; URBs, queues, firmware, and registers live below shared rtw88 USB/core and `rtw8814a.c`.

Dependencies are Linux USB/module APIs, `main.h`, `usb.h`, and `rtw8814a.h`. Risks center on ID accuracy and board quirks hidden behind a shared chip profile. Test signals include USB modaliases, probe on listed devices, endpoint aggregation variants, firmware download, traffic, USB suspend/resume, and disconnect under I/O.
