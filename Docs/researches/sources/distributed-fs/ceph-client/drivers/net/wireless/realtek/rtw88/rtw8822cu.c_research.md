## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822cu.c

Purpose: USB module glue for RTL8822CU-compatible devices. It lists Realtek and OEM USB IDs and binds them to the shared 8822C hardware spec through the rtw88 USB transport.

Important APIs/types: `rtw_8822cu_id_table`, `MODULE_DEVICE_TABLE(usb, ...)`, `rtw8822cu_probe()`, and `struct usb_driver rtw_8822cu_driver`. The table covers Realtek IDs `0xc82c`, `0xc812`, `0xc82e`, `0xd820`, `0xd82b`, plus Alpha and D-Link aliases.

Control flow and state: USB core matching invokes `rtw8822cu_probe()`, which simply delegates to `rtw_usb_probe()`. Disconnect delegates to `rtw_usb_disconnect()`. No local state persists beyond the static ID table and module registration.

Dependencies and integration: depends on Linux USB core, `main.h`, `rtw8822c.h`, and `usb.h`. Integration with mac80211, firmware, endpoint parsing, URB lifecycle, and power sequencing is in `usb.c`.

Risks and test signals: risks are ID table omissions, interface-class matching too broad/narrow, and incorrect `driver_info`. Test by checking USB modaliases, probing each listed VID/PID where available, and verifying firmware load and TX/RX over USB2/USB3.
