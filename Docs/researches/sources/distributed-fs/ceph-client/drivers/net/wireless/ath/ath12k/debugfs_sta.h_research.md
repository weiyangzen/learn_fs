# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs_sta.h

Purpose: Declares the station-link debugfs hook for ath12k and defines the buffer size used to format per-station RX stats.

Important APIs and definitions: `ATH12K_STA_RX_STATS_BUF_SIZE` is 16 KiB. Under `CONFIG_ATH12K_DEBUGFS`, `ath12k_debugfs_link_sta_op_add()` is declared for mac80211/debugfs integration. The header includes `net/mac80211.h` and `core.h` to expose `struct ieee80211_hw`, `struct ieee80211_vif`, `struct ieee80211_link_sta`, and ath12k core types.

Control flow: The header owns no runtime flow. Its compile-time `CONFIG_ATH12K_DEBUGFS` guard controls whether consumers can call the station debugfs add hook.

State and persistence: No state is stored in the header. The size macro bounds transient formatting buffers allocated by `debugfs_sta.c`.

Dependencies and integration points: Used by `debugfs_sta.c` and by ath12k mac80211/debugfs station setup code. It depends on debugfs-enabled builds providing the implementation; no fallback stub is declared here, so callers must be similarly guarded or only compiled when debugfs support is present.

Risks: Prototype visibility is conditional, which can cause build errors if a caller is not under the same config guard. The buffer-size macro is a silent contract with formatter complexity in `debugfs_sta.c`; increasing displayed stats may require increasing the size or moving to seq_file-style streaming.

Test signals: Build ath12k with `CONFIG_ATH12K_DEBUGFS=y` and disabled; verify station debugfs code only references the function in debugfs builds; and read maximum-populated RX stats to confirm 16 KiB remains sufficient.
