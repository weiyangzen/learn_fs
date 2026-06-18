## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/usb.c

Purpose: USB HCI implementation for rtw88. It provides vendor control register access, firmware page download, endpoint parsing, TX/RX URB management, TX aggregation, RX aggregation parsing, USB2/USB3 mode switching, PHY interface tuning, lifecycle probe/disconnect, and `rtw_hci_ops`.

Important APIs/functions: exported `rtw_usb_probe()` and `rtw_usb_disconnect()`. Core helpers include `rtw_usb_read/write*`, `rtw_usb_write_firmware_page`, `rtw_usb_parse`, `rtw_usb_tx_agg_skb`, `rtw_usb_tx_handler`, `rtw_usb_rx_handler`, `rtw_usb_rx_resubmit`, dynamic RX aggregation functions, USB mode switching helpers, `rtw_usb_phy_cfg`, and HCI ops `rtw_usb_ops`.

Control flow: probe allocates `ieee80211_hw` plus `rtw_usb`, preallocates RX URBs, initializes core/interface/TX/RX workqueues, sets chip info, applies USB PHY parameters, optionally triggers USB3 mode switching by disconnecting/re-enumerating, registers hardware, then submits RX URBs. TX pushes descriptors onto endpoint queues, workqueue aggregates SKBs up to chip limits and submits bulk URBs, then reports status or waits for firmware TX report. RX completion queues filled SKBs, resubmits URBs, and workqueue splits aggregated descriptors into C2H or mac80211 RX frames.

State and persistence: owns `rtw_usb` state: device pointer, register bounce buffer ring protected by spinlock, endpoint maps, TX/RX workqueues, TX endpoint queues, RX control blocks, RX queue/free queue. Module parameter `switch_usb_mode` persists policy for USB3 switching.

Dependencies and integration: depends on Linux USB core, rtw88 TX/RX/FW/MAC/PS helpers, chip RQPN/intf tables, and mac80211.

Risks and test signals: high-risk areas are URB lifetime on disconnect, queue index validation, TX aggregation skb ownership, RX length bounds, control-transfer errors, USB3 re-enumeration, and reset during disconnect. Test USB2/USB3 probe, unplug under traffic, suspend/resume, large RX aggregation, TX status requests, and endpoint variants with one to four bulk-out pipes.
