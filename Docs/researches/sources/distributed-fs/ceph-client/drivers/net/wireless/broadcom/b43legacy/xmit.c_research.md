# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/xmit.c

## Purpose
Implements b43legacy TX header generation, PLCP rate encoding, RX frame conversion to mac80211 status, hardware TX-status decoding, and generic TX suspend/resume dispatch between PIO and DMA.

## Important APIs, Types, and Functions
Public functions are `b43legacy_plcp_get_ratecode_cck()`, `b43legacy_plcp_get_ratecode_ofdm()`, `b43legacy_generate_plcp_hdr()`, `b43legacy_generate_txhdr()`, `b43legacy_rx()`, `b43legacy_handle_txstatus()`, `b43legacy_handle_hwtxstatus()`, `b43legacy_tx_suspend()`, `b43legacy_tx_resume()`, and `b43legacy_qos_init()`. Internal helpers extract bitrate indexes, calculate fallback rates, generate firmware v3 TX headers, and postprocess RSSI.

## Control Flow, State, and Persistence
TX header generation chooses the mac80211 primary and fallback rates, copies frame-control and receiver fields, calculates fallback duration, embeds encryption IV/key metadata only if the key is still enabled, builds data and RTS/CTS PLCP headers, sets MAC/PHY control bits, and stores a caller-provided cookie. It may return `-ENOKEY` to prevent plaintext leakage during resume races. RX strips PLCP and optional padding, validates minimum lengths, accounts FCS errors, removes IV/ICV for hardware-decrypted frames, computes signal/rate/antenna/timestamp/channel fields, stores `ieee80211_rx_status`, and reports the skb through `ieee80211_rx_irqsafe()`. TX status ignores intermediate/AMPDU status, updates IEEE counters, then dispatches to PIO or DMA status handling.

## Dependencies and Integration Points
Depends on mac80211 rate, duration, RTS/CTS, TX/RX status, and skb APIs; b43legacy security key indexing; DMA/PIO backends; PHY RSSI/radio metadata; TSF reading; debugfs TX-status logging.

## Risks and Test Signals
Risks include invalid rate-code BUG paths, wrong retry-count accounting, encryption key races, skb underruns, timestamp wrap assumptions, and mismatched channel frequency reporting. Test encrypted traffic across suspend/resume, RTS/CTS and CTS-to-self, fallback/retry statistics, monitor/beacon timestamps, FCS/decrypt error handling, and both DMA and PIO TX-status paths.
