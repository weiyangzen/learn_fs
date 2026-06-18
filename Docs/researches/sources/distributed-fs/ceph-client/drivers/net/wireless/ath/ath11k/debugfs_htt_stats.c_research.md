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
