# sources/distributed-fs/ceph-client/net/mac80211/rate.h

Purpose: declares the internal mac80211 rate-control interface shared by core TX/station code and rate-control algorithms.

Important APIs and types: `struct rate_control_ref` stores selected `rate_control_ops` and private algorithm data. Function declarations cover rate lookup, TX status, per-link/per-station initialization and updates, rate-mask validation, algorithm initialization/deinitialization, and Minstrel module init/exit. Inline helpers wrap algorithm per-station allocation/free and debugfs setup.

Control flow: users allocate per-station algorithm state through `rate_control_alloc_sta()`, add debugfs through `rate_control_add_sta_debugfs()`, and free via `rate_control_free_sta()`. `rate_control_add_debugfs()` creates the top-level `rc` debugfs directory, `name` file, and algorithm-specific debugfs entries when debugfs and an algorithm hook are present.

State and persistence: the header itself stores no state, but it defines access to `sta->rate_ctrl_lock`, `sta->rate_ctrl_priv`, `local->debugfs.rcdir`, and the selected algorithm reference. Debugfs entries are runtime-only.

Dependencies and integration points: includes mac80211 internals, station info, driver ops, skbuff/netdevice headers, and conditionally exposes `rcname_ops`. It also abstracts `CONFIG_MAC80211_RC_MINSTREL` so callers can invoke Minstrel init/exit regardless of build option.

Risks: inline helpers assume `sta->rate_ctrl` is valid. Debugfs helpers must tolerate missing algorithms or directories. Because this is internal glue, signature changes affect station lifecycle, TX, debugfs, and algorithm modules together.

Test signals: build with and without `CONFIG_MAC80211_DEBUGFS` and `CONFIG_MAC80211_RC_MINSTREL`, station alloc/free lifecycle, debugfs creation/removal, and algorithm-less hardware-RC configurations.
