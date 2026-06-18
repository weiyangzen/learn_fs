# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/usb.h

Purpose: private USB HCI definitions for rtw89 USB devices.

Important APIs/types: defines vendor request codes, receive buffer counts/sizes, endpoint limits, RX aggregation registers/masks, TX URB limits, `struct rtw89_usb_info` chip-specific register/endpoint mapping, RX/TX control block structures, and `struct rtw89_usb` private bus state. Declares `rtw89_usb_probe()` and `rtw89_usb_disconnect()`.

Control flow/integration: chip-specific driver modules provide `rtw89_usb_info`; `usb.c` stores it in `rtw89_usb` and uses it for MAC setup, bulk-out mapping, and aggregation alignment. `rtw89_usb_priv()` casts `rtwdev->priv` to the USB backend state.

State and persistence: `struct rtw89_usb` persists for the lifetime of the allocated ieee80211 HW and owns RX queues, free buffers, workqueue, URBs, TX queues, inflight counters, and USB endpoint state.

Dependencies: includes `txrx.h` for channel counts and descriptor symbols, and relies on Linux USB/sk_buff/workqueue types through included core headers.

Risks/test signals: array bounds depend on endpoint and DMA-channel constants. Incorrect `bulkout_id` or aggregation alignment in chip data causes TX routing or RX packet splitting failures. Probe/disconnect and module build tests validate the ABI.
