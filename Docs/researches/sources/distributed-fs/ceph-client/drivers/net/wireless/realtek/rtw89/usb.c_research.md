# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/usb.c

Purpose: USB HCI backend for rtw89. It supplies register access, TX/RX URB handling, MAC initialization hooks, L1 recovery operations, and USB probe/disconnect integration with the shared rtw89 core.

Important APIs/functions: exported `rtw89_usb_probe()` and `rtw89_usb_disconnect()` bind/unbind a USB interface. `rtw89_usb_ops` implements `struct rtw89_hci_ops`: TX write/kickoff, register reads/writes, MAC pre/post init, resource checks, reset, and L1 recovery. Internal helpers handle vendor control requests, TX descriptor insertion, RX aggregation parsing, URB resubmission, endpoint discovery, and RX/TX queue lifecycle.

Control flow: probe allocates ieee80211 HW with USB private data, parses endpoints, initializes queues and RX URBs, initializes core/chip, registers mac80211, starts RX URBs, then marks probe done. TX pushes an rtw89 descriptor, queues the skb per channel, and `tx_kick_off` submits one bulk URB per skb. Completion strips descriptors, reports TX status or TX reports, decrements per-channel inflight counters, and frees control blocks. RX completion queues aggregate buffers to a workqueue, which splits packets by RX descriptor offsets and alignment before calling `rtw89_core_rx()`.

State and persistence: `struct rtw89_usb` holds USB device, endpoint pipes, vendor request buffer, IO error counter, RX workqueue/free queues/control blocks, anchored TX URBs, per-channel TX queues, and inflight counters. State is device-lifetime and cleared on disconnect.

Dependencies/integration: Linux USB core, mac80211 TX status/RX delivery, rtw89 chip descriptor callbacks, register definitions, HCI recovery, firmware command channel CH12.

Risks: repeated vendor/URB errors set `RTW89_FLAG_UNPLUGGED`. RX aggregation bounds and queue overflow handling are critical. CH12 firmware command mismatch is rejected. USB 512-byte multiple padding prevents transfer edge cases.

Test signals: USB2/USB3 probe, endpoint parsing, register IO, sustained aggregate RX, TX status/report delivery, disconnect while URBs are live, and SER L1 recovery toggling USB reset bits.
