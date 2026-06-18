# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug_sta.c

Purpose: Adds per-station debugfs files for aggregation state and received rate statistics.

Important APIs/functions: `ath_debug_rate_stats()` updates per-station RX rate counters. `ath9k_sta_add_debugfs()` creates `node_aggr` and `node_recv` files. Static file readers format TID aggregation window state and HT/legacy receive counts.

Control flow: RX data frames call `ath_debug_rate_stats()`, which finds the station by source address under RCU, maps the RX status to HT, CCK, or OFDM buckets, and increments HT20/HT40/SGI/LGI or legacy preamble/rate counters. `node_aggr` verifies HT support, then locks each TID TXQ and prints active BA window fields. `node_recv` prints MCS counters when HT is supported, then legacy CCK/OFDM counters based on current band.

State/persistence: Per-station state lives in `struct ath_node`: `rx_rate_stats`, aggregation TID state, max AMPDU, MPDU density, station pointer, and softc pointer. Debugfs files hold private pointers to `ath_node`.

Dependencies/integration: Requires mac80211 station lookup/debugfs hooks, ath TX aggregation structures, `debug.h` rate stats, and RX status processing from common paths.

Risks: Station lifetime must outlive debugfs private data as managed by mac80211. Rate index assumptions differ for 2 GHz OFDM (`rate_idx - 4`) and 5 GHz. Aggregation readers lock TXQs but stats increments are unsynchronized.

Test signals: Per-station debugfs creation/removal, HT and non-HT station output, RX frames at all MCS/legacy rates, 2 GHz OFDM index adjustment, and aggregation state during active BA sessions.
