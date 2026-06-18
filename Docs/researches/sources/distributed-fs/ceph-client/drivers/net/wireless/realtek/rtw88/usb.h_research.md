## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/usb.h

Purpose: USB constants, private state structures, and exported lifecycle declarations for rtw88 USB HCI.

Important APIs/types: defines vendor request constants, Realtek USB VID, buffer sizes, RX/TX ring counts, endpoint count, queue-select max, receive buffer alignment/size, and firmware address constants. `struct rx_usb_ctrl_block` ties each RX URB to an skb and device. `struct rtw_usb_tx_data` stores TX report sequence number in skb driver data. `struct rtw_usb` stores USB device, register bounce buffers, endpoint mapping, TX/RX workqueues, TX queues, RX URBs, and RX skb queues. `rtw_get_usb_priv()` and `rtw_usb_get_tx_data()` are inline accessors.

Control flow and state: no complex flow beyond accessors and `BUILD_BUG_ON` validation that USB TX metadata fits mac80211 skb driver data. State layout is consumed by `usb.c` after `ieee80211_alloc_hw()` allocates private memory.

Dependencies and integration: included by chip USB glue modules and `usb.c`. It forms the private HCI ABI for rtw88 USB.

Risks and test signals: buffer constants directly bound URB transfer sizes and aggregation behavior; wrong limits can cause truncation or memory pressure. Test via compile-time metadata fit, stress RX/TX aggregation, and probe devices with different endpoint layouts.
