# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/rtw8852bu.c

Purpose: Registers the USB RTL8852BU driver and supplies USB HCI register and endpoint parameters for the common RTW89 USB probe path. It binds multiple Realtek and OEM USB ids to `rtw8852b_chip_info`.

Important APIs and types: `rtw8852b_usb_info` defines USB HCI registers, RX aggregation alignment, and bulk-out ids for AC queues, management/high queues, and H2C. `rtw89_8852bu_info` packages chip and bus data. The USB id table and `usb_driver` delegate probe/disconnect to shared RTW89 USB code.

Control flow: USB core matches an id, calls `rtw89_usb_probe`, and passes `rtw89_8852bu_info`. Shared USB code configures transport, H2C, RX aggregation, and queues using the descriptor.

State and persistence: Immutable descriptors here. URBs, endpoints, aggregation state, and core device state live in shared USB/core code. Hardware register writes persist until reset/disconnect.

Dependencies and integration points: Linux USB/module APIs plus `rtw8852b.h`, `reg.h`, and `usb.h`. Uses the 8852B chip profile, not 8852BT.

Risks: Wrong bulkout ids route traffic to wrong queues. Broad vendor-specific interface matches require careful device-id additions. RX aggregation alignment affects receive parsing.

Test signals: Build, modalias/autoload for all ids, USB2/USB3 probe, H2C delivery, queue traffic, 8-byte RX aggregation parsing, disconnect under traffic, and shared USB PM paths.
