# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl8187/dev.c

## Purpose
This is the core RTL8187/RTL8187B USB wireless driver. It registers the USB device table and `ieee80211_ops`, reads EEPROM data, detects chip/RF revisions, initializes hardware, submits TX/RX/status URBs, handles mac80211 interface/configuration callbacks, and wires LED/rfkill support into device probe and disconnect.

## Important APIs, Types, And Functions
The exported module binding is `module_usb_driver(rtl8187_driver)`, with `rtl8187_probe()` and `rtl8187_disconnect()`. mac80211 integration is through the static `rtl8187_ops`, including `tx`, `start`, `stop`, `add_interface`, `remove_interface`, `config`, `bss_info_changed`, multicast/filter callbacks, `conf_tx`, `rfkill_poll`, and `get_tsf`.

Important data and control helpers include `rtl8187_tx()`/`rtl8187_tx_cb()`, `rtl8187_rx_cb()`, `rtl8187_init_urbs()`, `rtl8187b_init_status_urb()`/`rtl8187b_status_cb()`, `rtl8187_init_hw()`, `rtl8187b_init_hw()`, `rtl8187_start()`, `rtl8187_stop()`, `rtl8187_work()` for non-B retry reporting, `rtl8187_beacon_work()`, `rtl8187_conf_erp()`, EEPROM access callbacks, and `rtl8187_set_anaparam()`.

## Control Flow
Probe allocates `ieee80211_hw`, initializes private USB/control mutex state, copies 2.4 GHz channel/rate tables, sets wiphy/mac80211 capabilities, reads EEPROM width/MAC/TX power/base power, detects ASIC/chip revision, handles RTL8187B misidentified as RTL8187, selects the RTL8225 RF ops through `rtl8187_detect_rf()`, sets queue count and TX headroom, registers mac80211 hardware, then initializes LEDs and rfkill polling.

Start takes `conf_mutex`, runs the RTL8187 or RTL8187B hardware init sequence, initializes the USB anchor, sets RX/TX configuration registers, submits RX URBs, and for RTL8187B submits a status URB. RTL8187B uses four data queues and endpoint mapping; non-B uses one TX endpoint and a delayed work item to read cumulative retry count from register `0xFFFA`.

TX allocates a URB, builds a chip-specific TX descriptor in skb headroom, sets rate, no-encryption, fragmentation, RTS/CTS or CTS-to-self duration, optionally assigns software sequence numbers, selects endpoint, anchors and submits the bulk URB. Completion strips the descriptor and reports status immediately, queues RTL8187B frames until a status packet matches sequence bits, or queues non-B frames for delayed retry-count processing.

RX completion unlinks the skb from `rx_queue`, parses a trailing RTL8187 or RTL8187B RX descriptor, derives signal from AGC, fills `ieee80211_rx_status`, trims the skb to descriptor length, reports it to mac80211, then allocates and submits a replacement RX URB. Errors free the skb and do not refill unless allocation/submission succeeds.

BSS/config callbacks update MAC/BSSID/MSR registers, ERP timing, beacon work, RX filter bits, channel changes, TSF reads, and EDCA/CW settings. Stop disables interrupts/TX/RX, stops RF, powers analog blocks down, sets VCO off, kills anchored URBs, flushes queued TX-status skbs, and cancels delayed work for non-B chips.

## State And Persistence
`struct rtl8187_priv` holds persistent driver state: USB device, register map base, RF ops, active vif pointer, channel/rate/band tables, RX config, anchored URBs, delayed work, EEPROM-derived power values, ASIC/hardware revision, RX queue, signal/noise, slot time/AIFSN, rfkill mask/state, TX status queue, DMA-safe control buffer, and software sequence number. Per-vif beacon state lives in `struct rtl8187_vif`.

Hardware state is persisted in RTL818x CSR registers, RF registers, PHY tables, EEPROM-loaded defaults, analog power registers, USB endpoint URBs, and LED/rfkill state. Most hardware state is rebuilt on every `start()` after reset.

## Dependencies And Integration Points
The file depends on Linux USB core, mac80211/cfg80211, `eeprom_93cx6`, `etherdevice`, `rtl8187.h`, `rtl8225.h`, optional `leds.h`, and `rfkill.h`. It integrates with `rtl8225.c` for low-level register I/O and RF tuning, with `leds.c` for LED classdev registration, and with `rfkill.c` through the mac80211 rfkill poll callback.

## Risks
URB lifetime and skb ownership are central risks: TX completion, RTL8187B status matching, RX refill, and stop-time `usb_kill_anchored_urbs()` must not double-free or leak skbs. RTL8187B status matching compares truncated sequence-control bits and can misattribute ACK status under wrap or fragmentation. Non-B retry reporting uses a static cumulative retry variable and averages over queued packets, so rate control receives approximate status. Register sequences contain raw offsets and magic delays; incorrect ordering can hang the device. The driver supports only one active station/adhoc vif, and beaconing is software scheduled rather than hardware timed.

## Test Signals
Signals include successful probe for all USB IDs, correct MAC/TX power/RF revision logging, start/stop without URB leaks, RX delivery with sane dBm signal values, TX ACK/retry status on RTL8187 and RTL8187B, station and adhoc operation, channel changes without device stalls, software beaconing in IBSS, rfkill polling, LED triggers, suspend/disconnect cleanup, and lockdep/KASAN/USB debugging around anchored URBs and queues.
