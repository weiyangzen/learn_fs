# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs.h

## Purpose

This header defines the public debugfs contract for ath11k debug support. It provides constants, enums, small state structures, debug packet/log metadata, inline query helpers, and declarations or no-op stubs depending on `CONFIG_ATH11K_DEBUGFS`.

It is the shared boundary between debugfs implementation files, datapath code that checks debug settings, WMI/HTT stats handling, packet logging, DBR debug tracing, and mac80211 integration hooks.

## Important APIs, Types, and Functions

- `enum ath11k_dbg_htt_ext_stats_type` lists the debugfs-selectable HTT extended stats request types. Values match firmware HTT stats categories such as PDEV TX/RX, HWQ, TQM, peer info, CCA, TWT, REO resources, ring backpressure, TXBF, PHY counters, and peer control path TX/RX.
- `struct debug_htt_stats_req` is the live request object used by `debugfs_htt_stats.c`: it tracks completion, PDEV/type/peer address, formatted buffer length, and an inline flexible buffer for text output.
- `struct ath11k_dbg_dbr_entry`, `struct ath11k_dbg_dbr_data`, and `struct ath11k_debug_dbr` define the direct-buffer-ring debug trace: fixed-size entries containing HP/TP/timestamp/event, protected by a spinlock and associated debugfs dentry/enabled flag.
- `struct ath_pktlog_hdr`, `enum ath11k_pktlog_filter`, `enum ath11k_pktlog_mode`, and `enum ath11k_pktlog_enum` describe pktlog filter bits, lite/full modes, and packet log record types.
- `enum fw_dbglog_wlan_module_id`, `enum fw_dbglog_log_level`, and `struct ath11k_fw_dbglog` describe firmware debug-log module IDs and log-level/config payloads used by `fw_dbglog_config`.
- Public debugfs lifecycle functions include `ath11k_debugfs_soc_create()`, `ath11k_debugfs_pdev_create()`, `ath11k_debugfs_register()`, and matching destroy/unregister functions.
- Inline helpers expose current debug state to other code: `ath11k_debugfs_is_pktlog_lite_mode_enabled()`, `ath11k_debugfs_is_pktlog_rx_stats_enabled()`, `ath11k_debugfs_is_pktlog_peer_valid()`, `ath11k_debugfs_is_extd_tx_stats_enabled()`, `ath11k_debugfs_is_extd_rx_stats_enabled()`, and `ath11k_debugfs_rx_filter()`.

## Control Flow

When debugfs is enabled, this header exposes real function declarations implemented in `debugfs.c` and related stats files. Other driver modules call these during SOC/PDEV/radio lifecycle, VIF creation, firmware stats delivery, and datapath trace points. The inline helper functions read `ar->debug` fields directly, so datapath and monitor logic can cheaply branch on debug settings without a function call.

When debugfs is disabled, the same lifecycle APIs compile to no-op stubs returning success or default false/zero values. This keeps call sites simple while removing runtime debugfs behavior and debug-state side effects from non-debugfs builds.

## State and Persistence

The header itself stores no state, but it defines the layout for debug state held elsewhere. `ATH11K_HTT_STATS_BUF_SIZE` and `ATH11K_FW_STATS_BUF_SIZE` set upper bounds for transient formatted statistics buffers. `ATH11K_DEBUG_DBR_ENTRIES_MAX` fixes the DBR circular trace depth at 512 entries. HTT request state persists only for a live debugfs read, while DBR state and pktlog/debug toggles persist for the life of the corresponding ath11k object.

The inline helper semantics are important: pktlog RX stats are considered enabled when pktlog mode is nonzero and no peer-specific pktlog address is active; peer validity requires both `pktlog_peer_valid` and address equality.

## Dependencies and Integration Points

The header includes `hal_tx.h` and references ath11k core types, WMI direct-buffer module IDs, WMI debug-log parameters, mac80211 `ieee80211_hw`/`ieee80211_vif`, Ethernet addresses, completions, debugfs dentries, spinlocks, and firmware stats structures. It is consumed by `debugfs.c`, `debugfs_htt_stats.c`, datapath logging/statistics code, and mac80211 operation glue.

Its enum values must remain aligned with firmware/HTT expectations and parser support in `debugfs_htt_stats.c`. The `ATH11K_HTT_PEER_STATS_RESET` bit and HTT stats type values are especially sensitive because they are used to form firmware request/config payloads.

## Risks and Edge Cases

- Mismatches between `ath11k_dbg_htt_ext_stats_type` and firmware-supported HTT stats IDs can make debugfs requests fail, time out, or parse unrelated TLVs.
- The no-op stubs make non-debugfs builds silently ignore debug registration and state queries; call sites must not rely on debugfs side effects for required driver behavior.
- Direct reads from `ar->debug` inline helpers do not take locks. They are suitable for diagnostic flags but can observe concurrent debugfs writes.
- Large fixed buffer sizes reduce allocation frequency but can still truncate very large HTT/FW stats dumps, and vmalloc failure must be handled by callers.

## Test Signals

Build coverage should include both `CONFIG_ATH11K_DEBUGFS=y` and disabled builds to verify the declarations and stubs stay type-compatible. Runtime signals include correct helper behavior after writing pktlog and extended stats controls, successful HTT stats request allocation at `ATH11K_HTT_STATS_BUF_SIZE`, DBR entry wrap at 512 records, and expected false/zero helper results in non-debugfs builds.
