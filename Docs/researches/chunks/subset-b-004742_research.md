# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs_htt_stats.c lines 1-5976

## Scope and Purpose

This chunk is the main HTT extended-statistics formatter body for ath12k debugfs. It defines helpers and a large set of TLV-specific printer callbacks that convert firmware HTT stats payloads into human-readable text in `struct debug_htt_stats_req::buf`. The covered range starts with generic formatting helpers and ends inside `ath12k_dbg_htt_ext_stats_parse()` at the `HTT_STATS_LATENCY_CNT_TAG` case label, so the dispatch function is only partially covered by the assigned lines.

The code is diagnostic-only: it does not update datapath counters itself. It formats firmware-provided tx/rx, scheduler, TQM, self-generated frame, sounding, OFDMA/MU-MIMO, PHY, RTT, MLO, FSE, ring, and reset statistics for later readout through the debugfs HTT stats file operations defined after this chunk.

## Important APIs, Types, and Helpers

- `struct debug_htt_stats_req` is the per-open aggregation object passed through all printers. In this chunk its important fields are `buf`, `buf_len`, and later `type`, `cfg_param`, `done`, and completion fields referenced outside the covered range.
- `print_array_to_buf_index()`, `print_array_to_buf()`, and `print_array_to_buf_s8()` are shared emitters for indexed `__le32` and signed-byte arrays. They append into the fixed `ATH12K_HTT_STATS_BUF_SIZE` buffer and return the number of bytes appended.
- `ath12k_htt_ax_tx_rx_ru_size_to_str()`, `ath12k_htt_be_tx_rx_ru_size_to_str()`, and `ath12k_tx_ru_size_to_str()` translate AX/BE RU enum values into strings used by TX/RX PER, OFDMA, and rate stats.
- `ath12k_htt_get_punct_dir_type_str()`, `ath12k_htt_get_punct_ppdu_type_str()`, and `ath12k_htt_get_punct_pream_type_str()` map puncturing direction, PPDU type, and preamble enums into label fragments.
- Nearly every formatter receives `(const void *tag_buf, u16 tag_len, struct debug_htt_stats_req *stats_req)`, casts `tag_buf` to the corresponding `struct ath12k_htt_*_tlv`, checks `tag_len` for fixed-size TLVs, decodes little-endian fields with `le32_to_cpu()` or `__le32_to_cpu()`, and appends text with `scnprintf()`.
- Important structure families referenced here include `ath12k_htt_tx_pdev_*`, `ath12k_htt_tx_tqm_*`, `ath12k_htt_tx_de_*`, `ath12k_htt_tx_selfgen_*`, `ath12k_htt_rx_pdev_*`, `ath12k_htt_phy_*`, `ath12k_htt_stats_pdev_rtt_*`, `ath12k_htt_pdev_mlo_ipc_stats_tlv`, `ath12k_htt_sring_stats_tlv`, and `htt_rx_pdev_fw_stats_tlv`.

## Functional Areas Covered

- TX PDEV common and scheduler stats: common PDEV counters, underrun/flush/SIFS arrays, MU PPDU distribution, scheduler common fields, per-TXQ scheduling, command-posted/reaped arrays, scheduling order, ineligibility, and supercycle triggers.
- Hardware and reset diagnostics: HW PDEV error/reset reasons, interrupt misc counters, WHAL TX, hardware workaround arrays, DMAC reset timing, PHY reset details, PHY reset counters, and channel switch timing history.
- TX queue manager and descriptor engine: TQM common/error/gen/list/PDEV stats, DE common/classification/EAPOL/enqueue/discard/completion stats, and TX HWQ common stats.
- Self-generated and sounding stats: AC/AX/BE selfgen, error, schedule-status counters, NDPA/NDP/BRP/trigger counters, beamforming/sounding stats, channel-vector upload/query stats, and TXBF OFDMA AX NDPA/NDP/BRP/steering stats.
- MU-MIMO/OFDMA and rate/PER stats: PDEV MU-MIMO scheduler/group/MPDU stats, UL OFDMA and UL MU-MIMO trigger/user stats, TX rate stats, BE OFDMA rate stats, RX rate stats, RX extended rate stats, PER per bandwidth/NSS/MCS/RU, TXBF rate stats, and histogram stats.
- RX/datapath support: RX PDEV firmware ring/refill/suspend/resume counters, RX FSE software/hardware cache counters, SFM memory/client/user stats, SRING stats, AST entries, and SOC drop count.
- PHY/channel/regulatory diagnostics: noise floor and runtime NF, CCA history/counters, OBSS PD/spatial reuse, PHY TPC/regulatory power fields, puncture stats, TDMA stats, MLO scheduler, and MLO IPC ring-full counters.
- RTT/ranging: responder, initiator, hardware, TBR self-generated queued, and TBR command-result stats.
- Dispatch integration begins at `ath12k_dbg_htt_ext_stats_parse()`, which maps each HTT stats tag to its printer. The covered part reaches through `HTT_STATS_LATENCY_CTX_TAG` and stops at the `HTT_STATS_LATENCY_CNT_TAG` case label.

## Control Flow

The printers are intentionally flat. A firmware HTT extended-stats response is parsed elsewhere by a TLV iterator, and each TLV tag is routed to one of these callbacks. The callback validates enough length for fixed-layout TLVs, formats a section header, prints scalar fields or arrays, and updates `stats_req->buf_len`.

Several callbacks add mode-specific branches:

- `htt_print_tx_pdev_mu_ppdu_dist_stats_tlv()` selects AC/AX/BE labels from `hw_mode`, then iterates NR bins, PPDU-per-burst arrays, and termination-status arrays.
- `ath12k_htt_print_tx_pdev_mu_mimo_mpdu_stats_tlv()` uses `tx_sched_mode` and `user_index` to select AC MU-MIMO, AX MU-MIMO, or AX MU-OFDMA user counter labels.
- `ath12k_htt_print_tx_sounding_stats_tlv()` switches on sounding mode to print AC, AX, BE, or common channel-vector upload/query stats. BE adds 320 MHz handling.
- `ath12k_htt_print_tx_per_rate_stats_tlv()` switches on rate-control mode to choose SU/DL MU-MIMO/DL OFDMA/UL MU-MIMO/UL OFDMA prefixes, then prints PER by bandwidth, NSS, MCS, and optionally RU size.
- `ath12k_htt_print_chan_switch_stats_tlv()` prints channel switch records in reverse chronological order, using bitfields for bandwidth, center frequency, phy mode, chainmasks, and switch profile.
- `ath12k_dbg_htt_ext_stats_parse()` is the central dispatch switch. Its covered cases map tags from TX PDEV common through latency context to their formatter functions; later cases continue outside this chunk.

## State and Persistence Behavior

This range does not persist state to disk or firmware. Its state is a transient in-memory text buffer:

- Each printer appends to `stats_req->buf` at `stats_req->buf_len`.
- `stats_req->buf_len` is monotonically increased by callback-local `len` and written back before return.
- The buffer capacity is treated as `ATH12K_HTT_STATS_BUF_SIZE`; all normal appends use `scnprintf()` with `buf_len - len`.
- The source stats values are firmware snapshots. The code does not cache them beyond the debugfs read buffer.
- Some callbacks conditionally print a header only for first user index or firmware-supplied `print_header`, so multi-TLV sequences rely on firmware ordering and repeated calls into the same `stats_req`.

The request/completion lifecycle is outside the requested line range, but the post-boundary code shows that this buffer is allocated per debugfs open, filled by HTT event parsing, read with `simple_read_from_buffer()`, and freed on file release.

## Dependencies and Integration Points

- Depends on Linux kernel facilities: `scnprintf()`, `snprintf()`, `min_t()`, `min()`, endian helpers, bitfield helpers such as `u32_get_bits()` and `le32_get_bits()`, debugfs file operations after the chunk, and RCU/spinlock/completion machinery after the chunk.
- Depends on ath12k core headers included at the top: `core.h`, `debug.h`, `debugfs_htt_stats.h`, `dp_tx.h`, and `dp_rx.h`.
- Depends heavily on firmware ABI constants and packed TLV structures declared in `debugfs_htt_stats.h` and related HTT headers. Field order, array lengths, tag numbers, and enum values must match the firmware payload exactly.
- The parser callback integrates with `ath12k_dp_htt_tlv_iter()` after this chunk. Each switch case must match a `HTT_STATS_*_TAG` value emitted by firmware.
- The HTT request path after this chunk uses `ath12k_dp_tx_htt_h2t_ext_stats_req()` to request selected stats, and the response handler passes returned TLVs into `ath12k_dbg_htt_ext_stats_parse()`.
- Debugfs integration after this chunk creates `htt_stats_type`, `htt_stats`, and `htt_stats_reset` under each PDEV debugfs directory.

## Risks and Edge Cases

- The formatter layer trusts many firmware-supplied array counts. Some functions cap counts with `min_t()`, but others use counts such as `num_elems_ax_ndpa_arr`, `num_elems_ax_ndp_arr`, `num_elems_ax_brp_arr`, `num_elems_ax_steer_arr`, or `tbr_num_sch_cmd_result_buckets` directly against fixed struct arrays. If firmware sends an out-of-range value, the printer can read beyond the TLV structure despite the initial fixed-size check.
- Several helpers and printers decrement an index or `len` to remove a trailing comma. This assumes at least one element was emitted. Zero-length arrays can underflow in `print_array_to_buf_s8()` and in local loops that do `len--` after iterating a firmware-provided count.
- Some fixed-size checks are inconsistent. For example, `htt_print_pdev_ctrl_path_tx_stats_tlv()` checks `if (len < sizeof(*htt_stats_buf))` where `len` is the current output buffer length, not `tag_len`; this can skip valid input when output is short or accept invalid input later.
- `ath12k_htt_print_sring_stats_tlv()` prints `producer_full` from `head_tail_ptr` instead of the decoded `sring_stat`, which looks suspicious because `consumer_empty` uses `sring_stat` from `consumer_empty__producer_full`.
- `ath12k_htt_print_pdev_sched_algo_ofdma_stats_tlv()` prints `rate_based_dlofdma_probing_count` from `rate_based_dlofdma_disabled_cnt`, likely a copy/paste bug if a distinct probing counter exists in the ABI.
- Large debug output can silently truncate because appends are bounded by `ATH12K_HTT_STATS_BUF_SIZE`; there is no explicit truncation marker in these printers.
- The parser silently ignores unknown tags in the default case, which is useful for forward compatibility but can hide firmware/driver ABI drift unless users compare expected tag coverage.
- Boundary note: line 5976 contains only the `HTT_STATS_LATENCY_CNT_TAG` label. The call to `ath12k_htt_print_latency_prof_cnt()` and all following dispatch cases are outside this chunk and must be covered by the next chunk.

## Test Signals

- Build coverage should catch missing struct fields, tag constants, and enum constants when firmware ABI headers change.
- Runtime smoke tests can read debugfs `htt_stats_type`, write representative stats type IDs and cfg params, then read `htt_stats`; expected signals are non-empty section headers such as `HTT_TX_PDEV_STATS_CMN_TLV`, `HTT_TX_TQM_CMN_STATS_TLV`, `HTT_RX_PDEV_RATE_STATS_TLV`, or PHY/RTT headers depending on requested type.
- Reset behavior is tested outside this chunk through `htt_stats_reset`, but this chunk supplies many of the tags whose counters should drop or change after reset.
- Robustness tests should inject or simulate malformed TLVs: short `tag_len`, zero-length variable arrays, oversized firmware element counts, unknown tags, and mixed multi-part responses. Expected behavior should be no out-of-bounds read and no kernel warning beyond intended validation warnings.
- Output correctness tests should compare known synthetic TLV values against exact formatted field labels, especially bitfield extraction for `mac_id`, PDEV IDs, AST MAC addresses, puncture labels, channel switch rows, RU size labels, and BE 320 MHz counters.
- Concurrency/lifecycle test signals are handled after this chunk: only one stats request per `ar->debug.htt_stats.stats_req` should be active, completion should arrive before timeout, and the buffer should be freed on release.

## Cross-Chunk Notes

Lines after 5976 complete `ath12k_dbg_htt_ext_stats_parse()`, define `ath12k_debugfs_htt_ext_stats_handler()`, implement debugfs read/write/open/release paths, issue HTT requests, handle request timeout, and register debugfs files. The final per-file research should merge this chunk with the next chunk to describe the complete request-to-response lifecycle.
