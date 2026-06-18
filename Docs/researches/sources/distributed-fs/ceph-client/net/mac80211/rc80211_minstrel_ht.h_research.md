# sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht.h

Purpose: defines Minstrel HT/VHT constants, encoded rate helpers, data structures, and cross-file declarations used by the algorithm and debugfs renderer.

Important APIs and types: macros include `MINSTREL_SCALE`, `MINSTREL_FRAC()`, `MINSTREL_TRUNC()`, EWMA/noise-filter coefficients, group counts, `MI_RATE()`, `MI_RATE_IDX()`, `MI_RATE_GROUP()`, sample counts, and sample interval. Main structs are `minstrel_priv`, `mcs_group`, `minstrel_rate_stats`, `minstrel_mcs_group_data`, `minstrel_sample_category`, and `minstrel_ht_sta`. Exports include bitrate arrays, `minstrel_mcs_groups[]`, `minstrel_ht_add_sta_debugfs()`, and `minstrel_ht_get_tp_avg()`.

Control flow: the header shapes how `.c` encodes rates into a 16-bit group/index value, stores per-rate probability and retry state, organizes sample queues by type, and shares the station data with debugfs.

State and persistence: all structs describe runtime in-memory state. `minstrel_rate_stats` keeps current-period, last-period, and historical attempts/success counters plus filtered probabilities. `minstrel_ht_sta` keeps per-station selected rates and supported groups until the station is freed or capabilities are rebuilt.

Dependencies and integration points: relies on Linux bitfield helpers and mac80211/cfg80211 constants supplied by including C files. It is included by both the algorithm and debugfs implementation, so layout changes affect debugfs output and rate-selection state.

Risks: group-count constants and array dimensions must stay synchronized with `minstrel_mcs_groups[]`. Encoded rate bitfield widths constrain maximum group/rate indexes. Debugfs accesses these structs directly, so concurrent/statistical fields should remain readable without needing extra ownership assumptions beyond mac80211 rate-control locking conventions.

Test signals: compile-time array/group count checks, encoded rate round trips, fixed-point probability math, struct layout users in debugfs, and builds with/without debugfs enabled.
