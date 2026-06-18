# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/rx.c

## Purpose
`rx.c` implements firmware RX aggregation parsing and delivery into mac80211. It reads RX packet descriptors listed in firmware status, pulls packet data from device memory into the aggregation buffer, creates SKBs, fills `ieee80211_rx_status`, handles firmware logger packets, and maintains active-link information used by RX streaming.

## Important APIs, Types, and Functions
`wlcore_rx()` is the top-level RX drain routine called from the IRQ handler. `wl1271_rx_handle_data()` validates one aggregated packet, handles descriptor class `WL12XX_RX_CLASS_LOGGER`, allocates and fills an SKB, and queues it on `wl->deferred_rx_queue`. `wl1271_rx_status()` converts firmware descriptor metadata to mac80211 status fields: band, rate index via `wlcore_rate_to_idx()`, HT encoding, RSSI/SNR-derived noise, antenna, frequency, encryption/decryption flags, MIC errors, beacon/probe timestamps, and pending regulatory channel updates. Under `CONFIG_PM`, `wl1271_rx_filter_enable()` and `wl1271_rx_filter_clear_all()` control firmware RX filters used for WoWLAN.

## Control Flow
`wlcore_rx()` compares firmware and driver RX counters modulo `wl->num_rx_desc`, batches descriptors until the configured aggregation buffer would overflow, calls chip-specific `wlcore_hw_prepare_read()`, reads `REG_SLV_MEM_DATA`, and splits the aggregate by descriptor-derived aligned lengths. Data frames mark their HLID in a local active bitmap; after all packets are processed, older hardware may receive an end-of-transaction driver counter write. The active bitmap is passed to `wl12xx_rearm_rx_streaming()`.

## State and Persistence Behavior
RX state is in-memory: `wl->rx_counter`, `wl->aggr_buf`, `wl->noise`, per-link `fw_rate_mbps`, `wl->deferred_rx_queue`, and `wl->rx_filter_enabled`. RX SKBs are deferred to `main.c` netstack work rather than submitted directly from the IRQ loop. Firmware logger data is appended to the fwlog buffer through `wl12xx_copy_fwlog()`.

## Dependencies and Integration Points
The file depends on `rx.h`, `wlcore.h`, `acx.h`, `tx.h`, `io.h`, `hw_ops.h`, mac80211 RX status definitions, skb allocation, and the wl12xx register definition for older end-of-transaction hardware. It integrates tightly with `main.c` IRQ handling and sysfs fwlog exposure.

## Risks and Test Signals
Risks include malformed descriptor lengths, aggregation-buffer bounds, alignment handling (`UNALIGNED` vs `PADDED`), dropping frames during PLT mode, and correct counter wrap handling. Tests should observe RX data delivery, beacon/probe timestamping, encrypted packet flags/MIC failure reporting, firmware log extraction, RX filter enable/clear for suspend, and no aggregation buffer overrun under multiple RX descriptors.
