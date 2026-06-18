<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.c

## Purpose
This file implements the mac80211 integration for the pureLiFi plfxlc USB device. It advertises channels/rates, allocates and registers `ieee80211_hw`, handles TX/RX frame adaptation, filters ACKs, tracks station MACs for USB FIFO scheduling, manages minimal station/adhoc interface state, configures receive filters, handles beacon interval changes, and exposes ethtool statistics.

## Important APIs, Types, And Functions
Public helpers include `plfxlc_mac_alloc_hw()`, `plfxlc_mac_release_hw()`, `plfxlc_mac_preinit_hw()`, `plfxlc_mac_init_hw()`, `plfxlc_mac_rx()`, `plfxlc_mac_tx_to_dev()`, `plfxlc_op_start()`, `plfxlc_op_stop()`, and `plfxlc_restore_settings()`. The `ieee80211_ops` table `plfxlc_ops` supplies TX, start/stop, interface add/remove, config, filter, BSS change, stats, and ethtool callbacks while using mac80211 emulation for channel-context operations.

Key internal functions are `plfxlc_fill_ctrlset()` for USB TX headers and alignment, `plfxlc_op_tx()` for data versus management TX dispatch, `plfxlc_mac_tx_status()` for mac80211 completion, `plfxlc_filter_ack()` for ACK matching, `plfxlc_op_configure_filter()`, and `plfxlc_op_bss_info_changed()`.

## Control Flow
Allocation creates an `ieee80211_hw`, initializes private `struct plfxlc_mac`, copies static 2.4 GHz/LC channels and 802.11b/g-like rates, sets `NL80211_BAND_LC`, enables RX-includes-FCS, dBm signal reporting, host broadcast buffering, and MFP capability, restricts interface modes to station and adhoc, reserves extra TX headroom, initializes ACK queues, and initializes the embedded chip/USB state.

TX prepends `struct plfxlc_ctrlset`, pads packets to 4-byte alignment and away from exact 512-byte multiples, stores `hw` in `rate_driver_data[0]`, and for data frames maps the destination MAC to a tracked station queue or broadcast queue. It stops mac80211 queues when a station queue exceeds 60 SKBs, drops above 256, enqueues the SKB, and asks USB to send the next queued packet round-robin. Non-data frames are sent immediately with `plfxlc_usb_wreq_async()`.

RX parses the device `rx_status`, synthesizes `ieee80211_rx_status` with fixed 2412 MHz LC band and RSSI conversion, updates CRC/rssi counters, optionally consumes ACK frames, reads a big-endian payload length, validates MTU, applies padding for QoS/A4 alignment, updates the station table and heartbeat flags from source address, allocates an SKB, copies the 802.11 payload, and delivers it with `ieee80211_rx_irqsafe()`.

Interface add accepts only one station or adhoc VIF. BSS info changes update association state and, for adhoc beacon changes, fetch/free the beacon and program beacon interval. Filter configuration records FCS/control pass-through and multicast hash state.

## State And Persistence
`struct plfxlc_mac` persists the active `ieee80211_vif`, interface type, beacon cache, multicast hash, ACK wait queue, channels/rates/band, embedded chip, serial/MAC buffers, pass flags, ACK state, association flag, channel/regdomain fields, CRC error counter, and RSSI. USB TX station queues and flags are embedded under the chip's USB object. Firmware owns actual radio, rate, beacon, and data FIFO state.

## Dependencies And Integration Points
Depends on mac80211/cfg80211 APIs, USB transport helpers from `usb.c`, chip control from `chip.c`, request/status structures from `mac.h`/`intf.h`, and firmware behavior around ACKs/FIFO messages. Probe in `usb.c` calls allocation/preinit/register/init paths and RX URBs call `plfxlc_mac_rx()`.

## Risks
`struct plfxlc_header` overlays frame data with a pointer field for destination MAC, which is unusual for a wire header and depends on local layout assumptions. ACK handling comments admit it may need fixing; queued SKBs can be completed optimistically. TX queue thresholds and per-station mapping are driver-local and can stop/wake all mac80211 queues based on one station's backlog. RX assumes fixed frequency and LC band and has limited CRC/error filtering. Interface support is deliberately minimal and rejects AP mode despite station table naming. Some flags such as `PURELIFI_DEVICE_RUNNING` are cleared but not set in this file.

## Test Signals
Validate station and adhoc interface creation, TX data and management frames, queue stop/wake thresholds, ACK/no-ACK completion, RX data/control/filter behavior, station heartbeat table cleanup through USB timers, beacon interval programming in adhoc mode, ethtool RSSI/CRC stats, and probe/disconnect/reset races. mac80211 debug, skb leak checks, and USB error injection are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/mac.c -->
