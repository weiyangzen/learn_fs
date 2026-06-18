# Research: subset-b-004729

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs.c

## Purpose

This file implements the ath11k debugfs control and inspection surface for a device/SOC and each PDEV. It creates debugfs directories, exposes firmware and datapath statistics, lets privileged users toggle diagnostic modes such as extended TX/RX statistics and packet logging, provides test hooks for firmware crash/radar/TWT behavior, and maintains an optional direct-buffer-ring debug trace.

The code is compiled only through the debugfs-enabled ath11k build path declared in `debugfs.h`. It is not datapath-critical in the normal packet path, but several controls reconfigure monitor status filters, send WMI/HTT commands, or queue reset work, so writes can affect live device behavior.

## Important APIs, Types, and Functions

- `ath11k_debugfs_soc_create()` and `ath11k_debugfs_soc_destroy()` create/remove `/sys/kernel/debug/ath11k/<bus-dev>` SOC roots. The parent `ath11k` directory is intentionally left behind.
- `ath11k_debugfs_pdev_create()` and `ath11k_debugfs_pdev_destroy()` add SOC-level files: `simulate_fw_crash`, `soc_dp_stats`, and optional `sram`.
- `ath11k_debugfs_register()` creates per-radio `macN` debugfs directories, a symlink under the mac80211 wiphy debugfs tree, HTT and firmware stats files, packet logging and extended stats controls, DFS controls, DBR debug enablement, and power-save tracking toggles.
- `ath11k_debugfs_unregister()` frees any direct-buffer debug allocations associated with a radio.
- `ath11k_debugfs_fw_stats_init()` creates `fw_stats/{pdev_stats,vdev_stats,beacon_stats}`. The corresponding open handlers allocate `ATH11K_FW_STATS_BUF_SIZE`, request WMI firmware stats, fill text with `ath11k_wmi_fw_stats_fill()`, and serve it through `simple_read_from_buffer()`.
- `ath11k_debugfs_fw_stats_process()` consumes beacon stats replies and completes `ar->fw_stats_done` when all started VDEVs have supplied beacon stats.
- `ath11k_write_extd_rx_stats()` and `ath11k_write_pktlog_filter()` reconfigure monitor status-ring TLV filters through `ath11k_dp_tx_htt_rx_filter_setup()`.
- `ath11k_write_fw_dbglog()` parses debug-log configuration and sends it through `ath11k_wmi_fw_dbglog_cfg()`.
- `ath11k_debugfs_add_dbring_entry()` appends RX/replenish snapshots into a circular DBR debug buffer under a spinlock.
- TWT debugfs file operations (`ath11k_write_twt_add_dialog()`, `ath11k_write_twt_del_dialog()`, `ath11k_write_twt_pause_dialog()`, `ath11k_write_twt_resume_dialog()`) parse user commands and invoke WMI TWT commands for AP or supported STA interfaces.

## Control Flow

Device setup flows from SOC creation to PDEV creation and then per-radio registration. `ath11k_debugfs_soc_create()` finds or creates the global `ath11k` debugfs directory, creates a bus/device-named child, and stores it in `ab->debugfs_soc`. `ath11k_debugfs_pdev_create()` adds SOC-wide files unless the device has already been registered. `ath11k_debugfs_register()` creates the `macN` child and populates all per-radio controls, including calls into `ath11k_debugfs_htt_stats_init()` and `ath11k_debugfs_fw_stats_init()`.

Read-only stats files commonly use an open/read/release pattern: on open they lock `ar->conf_mutex`, verify `ATH11K_STATE_ON`, allocate a vmalloc buffer, request or snapshot data, attach the buffer to `file->private_data`, and release the mutex. Reads then copy the prepared text or binary SRAM dump. Release frees the buffer.

Write controls parse a bounded user buffer or use `kstrto*_from_user()`, validate state and input, then update `ar->debug` fields or call WMI/HTT/DP helpers. Packet logging first toggles firmware pktlog, clears any previous monitor filter, chooses lite/full/default TLV masks, updates all RXDMA monitor status rings, and persists `pktlog_filter`/`pktlog_mode`. Extended RX stats similarly applies either a diagnostic TLV mask or the default monitor status filter unless monitor mode is already active.

DBR debug control creates a per-module child directory (`spectral` or `CFR`) and allocates a fixed 512-entry circular buffer. Runtime producers call `ath11k_debugfs_add_dbring_entry()` only if the module debug state exists and is enabled; readers dump the table while holding the DBR spinlock.

Power-save tracking controls use WMI pdev parameters to enable peer PS state change events. Disabling resets per-station cached PS state and duration through `ieee80211_iterate_stations_atomic()`. TWT per-vif controls are installed by `ath11k_debugfs_op_vif_add()` for AP VIFs and STA VIFs with STA_TWT firmware service support.

## State and Persistence

Most state is in-memory and lifetime-bound to `struct ath11k`, `struct ath11k_base`, debugfs dentries, or open file handles. Persistent knobs include `ar->debug.extd_tx_stats`, `ar->debug.extd_rx_stats`, `ar->debug.rx_filter`, `ar->debug.pktlog_filter`, `ar->debug.pktlog_mode`, `ar->debug.module_id_bitmap`, `ar->ps_state_enable`, and `ar->ps_timekeeper_enable`; these survive across debugfs reads/writes while the driver instance is alive, but not across device removal.

Per-open statistics buffers are transient and freed by release handlers. Firmware stats lists are maintained under `ar->fw_stats`; beacon stats are explicitly freed after a multi-VDEV beacon stats request is formatted. DBR debug buffers persist until disabled or unregister, and behave as ring buffers indexed by `dbr_debug_idx`.

Concurrency is managed with `ar->conf_mutex` around live state/configuration changes, `ab->base_lock` for SOC backpressure stats reads, `ar->data_lock` for station PS state/duration updates and beacon-list cleanup, and per-DBR spinlocks for debug ring snapshots.

## Dependencies and Integration Points

The file integrates with Linux debugfs, vmalloc/kzalloc, simple read/write helpers, mac80211 VIF/station iteration, WMI firmware commands, HTT/DP monitor-ring configuration, HIF memory reads, and ath11k core state. Important local dependencies include `debugfs_htt_stats.h`, `wmi.h`, `dp_tx.h`, `hal_rx.h`, `peer.h`, `hif.h`, and structures rooted at `struct ath11k`, `struct ath11k_base`, `struct ath11k_vif`, and `struct ath11k_sta`.

The debugfs controls are privileged operational hooks. They cross into firmware via `ath11k_mac_fw_stats_request()`, `ath11k_wmi_force_fw_hang_cmd()`, `ath11k_wmi_fw_dbglog_cfg()`, `ath11k_wmi_pdev_pktlog_enable()/disable()`, `ath11k_wmi_simulate_radar()`, TWT WMI commands, and `ath11k_wmi_pdev_set_param()`. They also directly affect datapath monitor filter setup through `ath11k_dp_tx_htt_rx_filter_setup()`.

## Risks and Edge Cases

- Debugfs writes can intentionally crash firmware, queue hardware restart, simulate radar, or reconfigure monitor filters, so misuse can disrupt active traffic.
- Several formatter paths rely on fixed-size buffers and repeated `scnprintf()` accounting. Most guard length, but truncation is expected when firmware emits more data than the buffer can hold.
- DBR initialization has partial-allocation failure paths where a debugfs directory or parent object can exist before later allocation fails; unregister/disable cleanup is important for leak avoidance.
- Some write paths parse with `sscanf()` after bounded copies. Input validation is strict for field count but does not deeply validate semantic ranges beyond selected IDs and booleans.
- Packet logging and extended RX stats both manipulate monitor status filter state; interactions with monitor mode are guarded in the extended RX path but still require careful sequencing in tests.
- `simulate_fw_crash` chooses the first radio in ON state; multi-radio behavior depends on that scan.

## Test Signals

Useful test signals include debugfs file presence under both `/sys/kernel/debug/ath11k/<soc>/macN` and the wiphy symlink, successful open/read/release of firmware stats while `ATH11K_STATE_ON`, `-ENETDOWN` while down, correct `-EINVAL`/`-EPERM` responses for malformed writes, observable WMI/HTT command calls for toggles, monitor filter changes for pktlog/extended RX stats, DBR circular-buffer wrap behavior, and cleanup after debugfs unregister. Runtime integration tests should verify that toggling pktlog and extended RX stats restores defaults and does not leave monitor status rings with stale filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_htt_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_htt_stats.c

## Purpose

This file implements ath11k debugfs support for HTT extended statistics. It provides a large set of TLV-specific text formatters, a TLV parser dispatch function, the asynchronous firmware event handler that fills a pending debugfs request, and debugfs files for selecting stats type, reading a stats dump, and resetting firmware-side counters.

The file is primarily diagnostic glue between userspace debugfs reads and firmware HTT stats replies. It does not own the firmware counters themselves; it formats snapshots received from HTT into a bounded in-memory text buffer.

## Important APIs, Types, and Functions

- `PRINT_ARRAY_TO_BUF()` is the common helper macro for appending indexed counter arrays to the request buffer.
- `htt_print_*_tlv()` functions each cast a TLV payload to a matching `struct htt_*` type and append human-readable fields to `struct debug_htt_stats_req::buf`.
- `ath11k_dbg_htt_ext_stats_parse()` is the central dispatch table. It receives TLV tag/length/payload from `ath11k_dp_htt_tlv_iter()` and invokes the matching formatter.
- `ath11k_debugfs_htt_ext_stats_handler()` handles firmware HTT extended stats events. It validates the stats cookie magic, maps the PDEV ID back to `struct ath11k`, marks completion when the firmware DONE bit is set, parses TLVs into the live request, and completes the waiting debugfs reader.
- `ath11k_write_htt_stats_type()` validates and stores the selected request type in `ar->debug.htt_stats.type`; reset and out-of-range types are rejected.
- `ath11k_prep_htt_stats_cfg_params()` builds per-type HTT config words for requests needing extra selection, such as all HWQs/TXQs/cmdqs/rings, peer MAC address requests, active peers, CCA cumulative stats, active VDEVs, and peer control path TX/RX stats.
- `ath11k_debugfs_htt_stats_req()` initializes completion state, builds a cookie from `HTT_STATS_MAGIC_VALUE` plus PDEV ID, sends `ath11k_dp_tx_htt_h2t_ext_stats_req()`, and waits up to three seconds for the DONE event.
- `ath11k_open_htt_stats()`, `ath11k_read_htt_stats()`, and `ath11k_release_htt_stats()` implement the `htt_stats` debugfs read path.
- `ath11k_write_htt_stats_reset()` sends a reset request for a selected HTT stats type and records `ar->debug.htt_stats.reset`.
- `ath11k_debugfs_htt_stats_init()` initializes the stats lock and creates `htt_stats_type`, `htt_stats`, and `htt_stats_reset`.

The formatter surface spans PDEV TX/RX common counters, underrun/flush/SIFS/PHY errors, HWQ and scheduler state, TQM, TX DE classification/enqueue/completion, ring interfaces, SRNG/SFM, peer common/details/rate/TID/flow stats, RX firmware/refill/REO resources, PDEV rate stats, CCA, TWT sessions, OBSS PD, ring backpressure, TXBF/OFDMA, PHY counters/stats/reset diagnostics, and peer control path TX/RX management frame counters.

## Control Flow

Users first write a numeric type to `htt_stats_type`. Opening `htt_stats` rejects reset, peer-info, and peer-control-path types because those need extra peer-specific parameters not supplied by the simple read path. The open handler locks `ar->conf_mutex`, verifies the radio is ON, ensures there is no concurrent stats request, allocates `sizeof(*stats_req) + ATH11K_HTT_STATS_BUF_SIZE` with `vzalloc()`, stores it in `ar->debug.htt_stats.stats_req`, copies the selected type, and calls `ath11k_debugfs_htt_stats_req()`.

The request function initializes a completion, records PDEV ID, creates a cookie containing a magic value and PDEV ID, prepares type-specific config words, and sends the HTT H2T request. It waits in a loop for completion with a three-second timeout. If the wait times out and `stats_req->done` is still false, it marks the request done and returns `-ETIMEDOUT`.

Firmware replies arrive through `ath11k_debugfs_htt_ext_stats_handler()`. The handler validates the cookie, finds the matching radio with `ath11k_mac_get_ar_by_pdev_id()` under RCU, fetches the live `stats_req`, updates its `done` flag under `ar->debug.htt_stats.lock`, runs `ath11k_dp_htt_tlv_iter()` over the event data, and completes the waiting request if the DONE bit was set. The parser then dispatches each TLV by tag and appends text into the shared request buffer.

Reads from `htt_stats` copy the final request buffer up to `min(buf_len, ATH11K_HTT_STATS_BUF_SIZE)`. Release frees the request and clears the singleton pointer, allowing another stats read. Reset writes bypass the read path and send a stats-reset HTT request with a bit derived from the selected type.

## State and Persistence

The active request is a singleton per `struct ath11k` at `ar->debug.htt_stats.stats_req`, guarded by `conf_mutex` for allocation/lifetime and a spinlock for the DONE flag. The formatted output accumulates in the request object and is valid until the debugfs file is released. The selected stats type and last reset type persist in `ar->debug.htt_stats.type` and `ar->debug.htt_stats.reset` while the driver instance lives.

Buffer length is tracked by `stats_req->buf_len`. Most formatter functions explicitly null-terminate and clamp at `ATH11K_HTT_STATS_BUF_SIZE`; a few later formatters update the length directly and rely on the common fixed-size buffer and `scnprintf()` accounting. Array-length formatters usually derive element counts from TLV length and clamp with HTT maximums, though not every array print path has identical bounds handling.

## Dependencies and Integration Points

This file depends on HTT TLV structure definitions and tag constants from `debugfs_htt_stats.h`, ath11k core/debug logging, DP TX request helpers, DP RX/HTT TLV iteration, Linux debugfs file operations, vmalloc, completions, spinlocks, bitfield helpers, RCU lookup, and `struct ath11k` debug state defined via `debugfs.h`.

The firmware-facing integration is `ath11k_dp_tx_htt_h2t_ext_stats_req()` for requests/reset and `ath11k_dp_htt_tlv_iter()` for parsing target replies. Cookie encoding ties events back to a PDEV, and `ath11k_mac_get_ar_by_pdev_id()` maps that PDEV to the live radio. The debugfs file creation is called from `ath11k_debugfs_register()` in `debugfs.c`.

## Risks and Edge Cases

- The parser trusts that the TLV tag payload layout matches the struct cast. If firmware changes a TLV layout without matching driver updates, output can be wrong or unsafe.
- Fixed 512 KiB output can truncate large dumps. Truncation is mostly graceful, but formatter consistency varies and some functions do less explicit null-termination.
- Singleton request state rejects concurrent `htt_stats` opens with `-EAGAIN`; tooling must serialize reads per radio.
- Timeout handling sets `done` under the spinlock, but a late firmware event can still parse into the request before release if it arrives while `stats_req` remains installed.
- Peer-info and peer-control-path stats have config code but the simple debugfs read path forbids those types; adding peer-specific debugfs input would need careful lifetime and validation.
- Some formatter loops use firmware-provided or tag-length-derived counts. Most are capped with `min_t()`, but audit is needed when adding new TLVs to avoid reading past variable-length payloads.
- Reset writes compute `1 << (offset + type)` in `cfg1`; type/range changes need validation against bit width and firmware reset bitmap semantics.

## Test Signals

Unit-style validation should exercise `ath11k_dbg_htt_ext_stats_parse()` with representative TLVs for each tag family and verify expected headings/counter names without buffer overflow. Integration signals include `htt_stats_type` rejecting reset/out-of-range values, `htt_stats` returning `-EPERM` for peer-only types, `-ENETDOWN` when radio is down, `-EAGAIN` on concurrent opens, successful completion on DONE events with valid cookies, timeout behavior when no completion arrives, and reset writes sending an HTT reset request. Fuzzing TLV lengths around variable-array tags is valuable because this file is dominated by struct casts and length-derived loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_htt_stats.c -->
