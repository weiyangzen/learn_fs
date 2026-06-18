# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hif_usb.c

Purpose: Implements the ath9k_htc USB Host Interface transport: USB device matching, firmware request/download, URB allocation, aggregated TX/RX stream handling, register pipe messaging, suspend/resume, disconnect, and module USB driver registration.

Important APIs and functions: Public module hooks are `ath9k_hif_usb_init()`, `ath9k_hif_usb_exit()`, and `ath9k_hif_usb_dealloc_urbs()`. The `hif_usb` transport callbacks expose `start`, `stop`, `sta_drain`, and `send` to HTC. Key internal paths are `hif_usb_send_tx()`, `__hif_usb_tx()`, TX/mgmt/regout callbacks, `ath9k_hif_usb_rx_stream()`, RX and reg-in callbacks, firmware request/download callbacks, `ath9k_hif_usb_probe()`, disconnect, suspend, and resume.

Control flow: Probe validates endpoint numbers, handles storage-mode eject devices, allocates `hif_device_usb`, and starts async firmware lookup with fallback from development/latest firmware to older 1.3 names. Firmware callback allocates the HTC target, downloads firmware over control messages, allocates URBs, and initializes HTC hardware. TX data SKBs are queued and aggregated into USB stream frames with length/tag headers; management/beacon frames use separate anchored URBs. RX bulk URBs are continuously resubmitted, stream frames are parsed by tag/length/padding, split packets are completed with `remain_skb`, and packets are delivered to HTC. Disconnect waits for firmware completion, deinitializes HTC, optionally reboots the device, and frees state.

State and persistence: Runtime state includes USB anchors, TX free/pending lists, queued SKB counts, flags `HIF_USB_START/READY` and `HIF_USB_TX_STOP/FLUSH`, RX split-packet bookkeeping, firmware name/version index, and HTC handle. Firmware is loaded into device RAM and reloaded after resume; no host-side persistent state is written.

Dependencies and integration points: Depends on Linux USB core, firmware loader, skbuffs, HTC host APIs, WMI callbacks through HTC, debug stat macros, and device IDs for AR9271/AR7010/AR9287 USB devices. It bridges mac80211/HTC traffic to USB endpoints 1-4.

Risks: URB lifetime and anchor cleanup must be exact across stop, disconnect, error callbacks, and suspend. RX stream parsing drops the whole transfer on invalid tags/lengths and has split-packet state protected by `rx_lock`. Firmware fallback is asynchronous, so disconnect waits on `fw_done`. `BUG_ON(!nskb)` assumes queue counts and SKB queue never diverge.

Test signals: Probe supported IDs, storage eject transition, missing firmware fallback sequence, firmware download failure unwind, TX aggregation and management TX completion, RX multi-packet and split-packet transfers, invalid stream tag/length drops, station drain, suspend/resume firmware reload, hot unplug, and soft unbind.
