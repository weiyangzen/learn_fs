# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8851bu.c

## Purpose
This file is the USB bus glue for RTL8851BU-family Realtek 802.11ax adapters. It binds the generic RTW89 USB transport to the 8851B chip descriptor and declares USB IDs for Realtek and several retail adapters.

## Important APIs, Types, and Data
- `rtw8851b_usb_info` is a `struct rtw89_usb_info` containing register addresses for USB host request, WLAN, HCI enable, USB3 NPI config, and endpoint registers.
- The same structure sets `rx_agg_alignment = 8` and maps RTW89 DMA queues to bulk-out endpoint IDs: ACH0/1/2/3 to endpoints 3/4/5/6, management/high/H2C queues to endpoints 0/1/2.
- `rtw89_8851bu_info` points `.chip` to `rtw8851b_chip_info` and attaches the USB info under `.bus.usb`.
- `rtw_8851bu_id_table` matches Realtek IDs `0x0bda:0xb831` and `0x0bda:0xb851`, plus D-Link AX9U rev. A1, TP-Link Archer TX10UB Nano, and Edimax EW-7611UXB IDs using vendor-specific interface class/subclass/protocol `0xff`.
- `rtw_8851bu_driver` delegates `.probe` and `.disconnect` to `rtw89_usb_probe` and `rtw89_usb_disconnect`.

## Control Flow
`module_usb_driver()` registers the USB driver. When a matching interface appears, the USB core calls `rtw89_usb_probe`; that generic routine receives `rtw89_8851bu_info` through `driver_info`, then initializes RTW89 core state with 8851B chip operations and the USB endpoint/register map. Disconnect is handled by the common USB teardown routine.

## State and Persistence
This file has no mutable driver state. Persistent binding comes from `MODULE_DEVICE_TABLE(usb, ...)`, which enables modalias-based auto-loading. Runtime transport queues, URBs, firmware state, and hardware state are maintained by RTW89 USB/core layers.

## Dependencies and Integration Points
- Linux USB and module subsystems: `<linux/usb.h>`, `<linux/module.h>`.
- RTL8851B chip metadata in `rtw8851b.h`, register definitions in `reg.h`, and generic RTW89 USB helpers in `usb.h`.
- The endpoint map is an integration contract with USB descriptors and firmware/HCI queue routing.

## Risks
- Bulk endpoint mapping is hardware-contract data; a wrong queue-to-endpoint ID can break TX, management frames, or H2C commands.
- Device IDs use vendor-specific interface matching. Composite devices with unexpected interface descriptors could fail to bind.
- USB-specific power management is not declared here; behavior depends on generic RTW89 USB support.

## Test Signals
- Kernel build confirms `struct rtw89_usb_info` and generic USB callbacks match this wrapper.
- `modinfo` should list USB aliases for the declared adapters.
- Runtime tests should verify firmware download, scan, association, data TX/RX, disconnect cleanup, and operation through USB2/USB3 ports where applicable.
- Queue-specific traffic, especially management/H2C and multiple AC queues, is a useful endpoint-map validation signal.
