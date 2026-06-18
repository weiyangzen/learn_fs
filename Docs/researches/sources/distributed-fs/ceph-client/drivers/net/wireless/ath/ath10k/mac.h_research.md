# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/mac.h

## Purpose

`mac.h` is the ath10k mac80211-facing API header. It declares the MAC lifecycle, scan/off-channel work, management-frame work, beacon handling, TX scheduling/locking, rate mapping, rfkill, and helper routines used by the rest of the driver. It also defines small shared structures and one inline TX sequence-number helper.

## Important APIs, Types, and Functions

- `struct ath10k_generic_iter` carries an `ath10k` pointer plus return status through mac80211 interface iteration callbacks.
- `struct rfc1042_hdr` is the packed LLC/SNAP header layout.
- `ath10k_mac_create()`, `ath10k_mac_destroy()`, `ath10k_mac_register()`, and `ath10k_mac_unregister()` manage the mac80211 device lifecycle.
- Scan/off-channel APIs include `__ath10k_scan_finish()`, `ath10k_scan_finish()`, `ath10k_scan_timeout_work()`, `ath10k_offchan_tx_*()`, and `ath10k_mgmt_over_wmi_tx_*()`.
- Beacon and firmware-event APIs include `ath10k_mac_vif_beacon_free()`, `ath10k_mac_handle_beacon()`, `ath10k_mac_handle_beacon_miss()`, and `ath10k_mac_handle_tx_pause_vdev()`.
- TX APIs include driver-wide/per-vif TX locks, pending/TXQ push helpers, TXQ lookup, TX-complete wait, and rfkill radio control.
- `ath10k_tx_h_seq_no()` assigns per-vif sequence numbers when mac80211 delegates sequence assignment.

## Control Flow

The header mostly declares functions implemented in the MAC layer. The inline `ath10k_tx_h_seq_no()` reads skb TX metadata, checks `IEEE80211_TX_CTL_ASSIGN_SEQ`, lazily initializes `arvif->tx_seq_no` to `0x1000`, increments on first fragments, preserves the fragment bits in `hdr->seq_ctrl`, and writes the sequence number in little-endian form.

Typical users call these APIs from core registration, WMI event paths, scan timeout work, off-channel TX queues, and firmware TX pause/unpause handling.

## State and Persistence Behavior

No global storage is defined here. Declared APIs mutate long-lived `struct ath10k`, `struct ath10k_vif`, queued skb state, work items, mac80211 TXQs, and firmware-backed vdev state. The inline helper persists and updates `arvif->tx_seq_no` and edits the outgoing 802.11 header in place.

## Dependencies and Integration Points

`mac.h` includes `<net/mac80211.h>` and `core.h`, and forward-declares WMI TLV TX-pause enums. It integrates ath10k core/HIF/WMI code with Linux mac80211 objects such as `ieee80211_hw`, `ieee80211_vif`, `ieee80211_txq`, and `ieee80211_supported_band`.

## Risks and Edge Cases

- `ath10k_tx_h_seq_no()` assumes a valid ath10k vif private area and a writable 802.11 header.
- Sequence assignment is safe only when mac80211 set `IEEE80211_TX_CTL_ASSIGN_SEQ`.
- Many declarations take raw pointers and IDs; implementation-side locking and lifetime rules are critical.
- Forward-declared enum/type drift with WMI headers is caught only at compile time.

## Test Signals

- Build all ath10k bus and WMI variants that include this header.
- TX tests should verify sequence-control assignment and fragment preservation.
- Scan/off-channel cancellation tests should show no stale work after stop or recovery.
- AP/P2P tests should exercise beacon updates, beacon misses, NOA integration, and TX pause events.
