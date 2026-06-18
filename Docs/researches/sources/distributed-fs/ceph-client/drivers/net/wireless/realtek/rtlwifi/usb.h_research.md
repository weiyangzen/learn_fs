# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/usb.h

## Purpose
Defines the shared rtlwifi USB transport interface, endpoint/queue constants, USB private state structures, skb transport metadata helper, start/stop state macros, and exported probe/disconnect declarations.

## Important APIs, Types, And Functions
Important constants are `RTL_RX_DESC_SIZE`, `USB_HIGH_SPEED_BULK_SIZE`, `USB_FULL_SPEED_BULK_SIZE`, `RTL_USB_MAX_TXQ_NUM`, `RTL_USB_MAX_EP_NUM`, `RTL_USB_MAX_BULKOUT_NUM`, and `RTL_USB_MAX_TX_URBS_NUM`. `RTL_USB_DEVICE` helps chip drivers build USB ID table entries that point to an `rtl_hal_cfg`. `enum rtl_txq` defines BK/BE/VI/VO/BCN/MGT/HI queues. `struct rtl_ep_map`, `struct rtl_usb`, and `struct rtl_usb_priv` hold endpoint maps, anchors, queues, tasklet, callbacks, and Bluetooth coexistence state. `_rtl_install_trx_info` stores the `rtl_usb` pointer and endpoint number in skb driver data for completion callbacks.

## Control Flow
The header has inline metadata installation and macros to set/test USB transport state. Runtime control flow is implemented in `usb.c` and chip USB drivers.

## State And Persistence
`struct rtl_usb` captures all live transport state: USB device/interface, start/stop state, beacon and interrupt masks, queue-to-endpoint mapping, TX/RX anchors, skb queues, tasklet, and chip-specific callback hooks. This is in-memory state attached to `ieee80211_hw` and released at disconnect.

## Dependencies And Integration Points
Depends on Linux skbuff and USB/mac80211 types supplied by surrounding includes. Integrated with chip USB modules via `RTL_USB_DEVICE`, with shared rtlwifi core through `rtl_usbpriv`/`rtl_usbdev`, and with `usb.c` through `rtl_usb_probe` and `rtl_usb_disconnect`.

## Risks And Edge Cases
The queue enum must stay consistent with `skb_get_queue_mapping`, as noted in the file, or TX traffic will go to the wrong endpoint. `rate_driver_data` slots are reused for transport metadata, so chip TX/report code must not assume those slots are free while USB owns them. Maximum endpoint constants constrain devices with unusual endpoint layouts.

## Test Signals
Build USB rtlwifi chip drivers, verify USB ID table matching through `RTL_USB_DEVICE`, exercise queue mapping for BK/BE/VI/VO/beacon/management/high queues, and test unplug/stop paths to ensure state macros and anchors coordinate with `usb.c` cleanup.
