# sources/distributed-fs/ceph-client/drivers/net/wireless/zydas/zd1211rw/zd_mac.h

## Purpose
Defines ZD1211RW MAC-layer packet formats, rate encodings, RX/TX status formats, per-device MAC state, regulatory/channel constants, and public MAC APIs.

## Important APIs, Types, And Functions
Key types are packed `struct zd_ctrlset`, `rx_length_info`, `rx_status`, `tx_retry_rate`, `tx_status`, `housekeeping`, `beacon`, and `zd_mac`. Constants define Zydas CCK/OFDM rates, PLCP header sizes, ctrlset control bits, RX error/decryption bits, regulatory domains, channel bounds, and maximum ACK waiters. Inline helpers expose PLCP rate extraction and conversions between `ieee80211_hw`, `zd_mac`, `zd_chip`, and `zd_usb`.

## Control Flow
The header sets the binary contract used by TX and RX paths. TX prepends `zd_ctrlset`; RX receives a PLCP header plus trailing `rx_status` and sometimes an `rx_length_info` trailer for merged USB frames. Public functions are invoked by USB probe/completion/reset and mac80211 registration.

## State And Persistence
`struct zd_mac` is the long-lived mac80211 private area. It embeds `struct zd_chip`, spinlocks, vif pointer, work items, multicast hash, interrupt buffer, channel/rate arrays, ack queue, and filter/association flags. `beacon.cur_beacon` owns an skb until replaced or disabled.

## Dependencies And Integration Points
Includes Linux kernel and mac80211 headers plus `zd_chip.h`. The declarations are shared between `zd_mac.c`, `zd_usb.c`, and chip code that needs rate/RX status definitions.

## Risks
Packed firmware-facing structs must remain layout-compatible. `info->rate_driver_data` is used by TX/USB code for private pointers and timestamps, so any mac80211 API changes can break assumptions. ACK waiter limit bounds memory but may produce status for old frames without exact hardware confirmation.

## Test Signals
Compile with structure layout warnings enabled, run TX/RX across all supported rates and short preamble settings, receive merged USB frames, pass FCS-failed/control frames, and verify AP beacon/TIM refresh behavior.
