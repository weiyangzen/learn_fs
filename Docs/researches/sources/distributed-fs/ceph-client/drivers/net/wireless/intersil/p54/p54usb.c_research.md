## sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54usb.c

Purpose: this is the USB transport driver for Prism54/p54 devices. It binds a large USB ID table, detects either ISL3887 direct USB hardware or ISL3886 behind a NET2280 bridge, loads firmware, uploads it through the appropriate boot path, wires URB RX/TX callbacks to the common p54 mac80211 core, and registers/unregisters the common wireless device.

Important APIs and functions: module metadata advertises `isl3886usb` and `isl3887usb` firmware. `p54u_probe()` allocates `ieee80211_hw` via `p54_init_common()`, identifies endpoint layout, chooses `p54u_tx_lm87()` or `p54u_tx_net2280()`, and starts async firmware loading with `p54u_load_firmware()`. `p54u_start_ops()` parses firmware, validates firmware interface, uploads firmware, starts URBs, reads EEPROM, stops, then calls `p54_register_common()`. RX is handled by `p54u_rx_cb()`, which adjusts transport headers and calls `p54_rx()`. TX completion uses `p54u_tx_cb()` to call `p54_free_skb()`.

Control flow: probe initializes queues/anchors and schedules firmware. The firmware callback calls `p54u_start_ops()`, and on failure releases the USB interface. Open/stop only manage RX URBs because the code comments say reliable hardware stop is not known. Reset/resume re-upload firmware and restart mac80211 state when needed.

State and persistence: `struct p54u_priv` stores the USB device/interface, firmware pointer, selected hardware type, upload callback, RX skb queue, submitted URB anchor, and completion for async firmware load. Firmware blobs are retained until disconnect. URB lifetime is anchored under `priv->submitted`.

Dependencies and integration: this file depends on USB core, firmware loader, PCI/NET2280 constants, `p54.h`, `lmac.h`, `p54usb.h`, and common p54 functions. Hardware-facing dependencies include bulk endpoints, interrupt endpoint behavior, NET2280 register access, CRC32 framing for ISL3887 X2 upload, and p54 firmware interface IDs.

Risks and tests: firmware upload paths are timing-sensitive and use fixed sleeps, CRC handshakes, DMA status bits, and endpoint heuristics. RX buffer reuse depends on `p54_rx()` returning whether the skb was consumed. Test signals include device probe for both endpoint layouts, firmware load failures, suspend/resume/reset, URB leak checks, EEPROM read success, and packet TX/RX through mac80211.
