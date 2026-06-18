# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_sta.h

Purpose: Declares the station debugfs integration points and provides no-op fallbacks when ath11k debugfs support is not compiled.

Important APIs and types: Exposes `ath11k_debugfs_sta_op_add()` for mac80211 station debugfs file creation, `ath11k_debugfs_sta_add_tx_stats()` for per-station TX counter accumulation, and `ath11k_debugfs_sta_update_txcompl()` for TX completion stat updates. It includes `core.h` and `hal_tx.h` for `struct ath11k`, `struct ath11k_sta`, `struct ath11k_per_peer_tx_stats`, and `struct hal_tx_status`.

Control flow: With `CONFIG_ATH11K_DEBUGFS`, callers bind to implementations in `debugfs_sta.c`. Without it, `ath11k_debugfs_sta_op_add` is `NULL` and the stat update helpers inline to empty functions, letting datapath code call them without preprocessor noise.

State and persistence: Owns no state. Its compile-time configuration changes whether station debugfs state is reachable and whether TX completion paths update debug-only counters.

Dependencies and integration points: Used by mac80211 ops registration and TX completion paths. It bridges debugfs-specific accounting to normal ath11k datapath code while keeping non-debug builds lean.

Risks: Prototype drift would break callers in TX and station setup. The `NULL` station op must remain acceptable to the mac80211 registration path. Non-debug builds intentionally lose these counters, so no functional behavior should depend on the helpers doing work.

Test signals: Compile both `CONFIG_ATH11K_DEBUGFS=y` and disabled builds; create/destroy stations and ensure debugfs entries appear only in debug builds; run TX completion paths in non-debug builds to confirm no unresolved symbols or behavior dependency.
