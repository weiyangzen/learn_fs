# sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht_debugfs.c

Purpose: exposes per-station Minstrel HT/VHT rate-control statistics through debugfs in human-readable and CSV formats.

Important APIs and functions: `minstrel_ht_add_sta_debugfs()` creates `rc_stats` and `rc_stats_csv` files. `minstrel_ht_stats_open()` and `minstrel_ht_stats_csv_open()` allocate a fixed 32 KiB buffer and render a snapshot. `minstrel_stats_read()` serves that buffer; `minstrel_stats_release()` frees it. `minstrel_ht_stats_dump()` and `minstrel_ht_stats_csv_dump()` format each supported rate. `minstrel_ht_is_sample_rate()` marks rates currently queued for sampling.

Control flow: opening a debugfs file snapshots `struct minstrel_ht_sta` into a temporary buffer, iterating CCK first, then HT groups before CCK, then remaining groups. Each row labels mode, guard interval, stream count, best-rate markers A-D, max-prob marker P, sample marker S, MCS/legacy name, encoded index, airtime, max throughput, average throughput, probability, retries, last attempts/successes, historical totals, and packet/sample counters.

State and persistence: debugfs data is generated on open and stored in `struct minstrel_debugfs_info` until release. It does not mutate rate-control state, except that it reads live counters without producing persistent artifacts.

Dependencies and integration points: depends on `rc80211_minstrel_ht.h` structs and helpers, debugfs file operations, module ownership, and simple read helpers. It is installed through Minstrel's `add_sta_debugfs` rate-control op.

Risks: the renderer uses `sprintf()` into a fixed 32 KiB allocation and only warns after rendering if the buffer was exceeded, so future group/rate growth can become a memory corruption risk unless converted to bounded formatting. It reads live stats without explicit locking in this file, so output can be inconsistent during concurrent updates, though it is diagnostic-only.

Test signals: opening both debugfs files for stations with legacy-only, HT, and VHT rates; buffer size with all groups supported; CSV row shape; best/prob/sample markers; and cleanup on open allocation failure or file release.
