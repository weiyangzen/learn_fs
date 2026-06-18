# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852cu.c

## Purpose
This file is the USB bus binding for RTL8852CU devices. It supplies USB register addresses, endpoint/channel mapping, USB IDs from several vendors, and a `usb_driver` that delegates probe/disconnect to the common rtw89 USB layer while reusing `rtw8852c_chip_info`.

## Important APIs, Types, and Data
- `rtw8852c_usb_info` provides USB HCI register addresses, `rx_agg_alignment = 8`, and `bulkout_id` mappings from rtw89 DMA queues to USB bulk endpoints.
- `rtw89_8852cu_info` selects `rtw8852c_chip_info` with `.bus.usb = &rtw8852c_usb_info`.
- `rtw_8852cu_id_table` matches multiple USB vendor/product IDs, including Realtek `0x0bda:c832`, `0x0bda:c85a`, and `0x0bda:c85d`.
- `rtw_8852cu_driver` uses `rtw89_usb_probe` and `rtw89_usb_disconnect`.

## Control Flow
The USB core matches an interface using `USB_DEVICE_AND_INTERFACE_INFO(..., 0xff, 0xff, 0xff)`. The `driver_info` pointer supplies the rtw89 driver info to the common USB probe path. That path configures endpoints, aggregation, HCI registers, and chip-level operations from `rtw8852c_chip_info`. Disconnect is fully delegated to common USB teardown.

## State and Persistence
The file owns only static immutable registration tables. Runtime URB, endpoint, firmware, and device state is allocated by the rtw89 USB/core layers. The ID table persists in module metadata through `MODULE_DEVICE_TABLE(usb, ...)`.

## Dependencies and Integration Points
Depends on Linux USB/module APIs and rtw89 `usb.h`, `reg.h`, and `rtw8852c.h`. Integration hinges on correct DMA queue to endpoint mapping for data, management, high-priority, and H2C command traffic.

## Risks
- Incorrect `bulkout_id` mapping can silently route traffic to the wrong endpoint or break queue QoS.
- Vendor-specific IDs with class `0xff` rely on devices exposing the expected Realtek vendor interface.
- USB aggregation alignment must match firmware/device expectations or RX parsing can fail.

## Test Signals
- `modinfo` contains the USB aliases and devices bind on insertion.
- Probe should enumerate endpoints, download firmware, and pass TX/RX traffic on all mapped queues.
- Hot unplug/replug, suspend/resume, high-throughput RX aggregation, and H2C command delivery are key runtime checks.
