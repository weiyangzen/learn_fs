# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852au.c

Purpose: This file is the USB bus glue module for RTL8852AU adapters. It maps known USB VID/PID/interface matches to the common RTW89 USB driver and supplies the 8852A-specific USB register map, endpoint alignment, and bulk-out DMA queue mapping.

Important APIs, types, and data: `rtw8852a_usb_info` fills `struct rtw89_usb_info` with USB HCI register addresses, endpoint registers, RX aggregation alignment of 8 bytes, and `bulkout_id` assignments for AC queues, management/high queues, and H2C firmware commands. `rtw89_8852au_info` points at `rtw8852a_chip_info` and the USB info. `rtw_8852au_id_table` contains vendor/product matches from Buffalo, Elecom, ASUS, Realtek, D-Link, TP-Link, and others using vendor-specific interface class/subclass/protocol values. `rtw_8852au_driver` registers `rtw89_usb_probe` and `rtw89_usb_disconnect`.

Control flow: Module insertion registers a Linux `usb_driver`. On a matching interface, the USB core calls `rtw89_usb_probe()`, which consumes `driver_info`, creates the RTW89 device, configures USB endpoints/aggregation/HCI registers from `rtw8852a_usb_info`, and then enters common chip initialization using `rtw8852a_chip_info`. Disconnect tears down URBs, queues, and the common RTW89 device through `rtw89_usb_disconnect()`.

State and persistence: The file has static const configuration and no local mutable state. Runtime persistence is in USB core device/interface state, URB/queue state allocated by common RTW89 USB code, firmware state on the adapter, and chip state programmed by common initialization. The endpoint mapping effectively persists for the device lifetime.

Dependencies and integration points: Includes Linux module and USB headers, `rtw8852a.h`, `reg.h`, and `usb.h`. Integrates with USB modalias autoloading through `MODULE_DEVICE_TABLE(usb, ...)`, the common RTW89 USB transport, H2C/C2H firmware paths, and the 8852A chip-info layer shared with PCIe.

Risks: Bulk-out queue mapping is hardware and firmware contract data. Wrong endpoint IDs can route traffic to the wrong pipe or stall TX/H2C commands. Missing or overly broad USB IDs can either fail to bind supported adapters or claim incompatible ones. USB suspend/resume is not wired locally in this snippet, so behavior depends on generic RTW89 USB support and kernel USB PM defaults.

Test signals: Build validates USB helper prototypes and chip-info linkage. Runtime signals include modalias autoload for listed VID/PIDs, successful probe and firmware download, correct endpoint discovery, RX aggregation alignment without malformed frames, H2C command completion, TX on all mapped queues, disconnect cleanup without URB leaks, and association/traffic on 2.4 GHz and 5 GHz.
