# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi.c lines 7926-9641

## Scope And Purpose

This chunk is the final large section of the non-TLV ath10k WMI implementation. It covers several late command builders, firmware-statistics text formatting, version-specific WMI operation tables, WMI attach-time dispatch selection, and detach-time cleanup for firmware-owned host resources.

The code is centered on the `struct wmi_ops` backend model used by ath10k. Earlier code and `wmi-ops.h` expose common wrapper functions; this chunk supplies concrete implementations for the main, 10.1, 10.2, 10.2.4, and 10.4 firmware WMI ABIs. `ath10k_wmi_attach()` selects the correct ops table, command map, parameter maps, peer flags, and key-cipher mapping based on `ar->running_fw->fw_file.wmi_op_version`.

The chunk is not filesystem logic despite living under `sources/distributed-fs/ceph-client/`; it is Linux wireless driver code. Its correctness determines how host driver state is serialized into firmware WMI commands and how debugfs firmware-stat snapshots are rendered for ath10k devices.

## Command Builders

The command generator functions allocate a WMI skb with `ath10k_wmi_alloc_skb()`, cast `skb->data` to the ABI-specific command struct, populate little-endian fields, log via `ath10k_dbg()`, and return either the skb or `ERR_PTR(-ENOMEM)`/`ERR_PTR(-EINVAL)`.

Key builders in this range:

- `ath10k_wmi_op_gen_pdev_set_wmm()` serializes BE/BK/VI/VO EDCA/WMM parameters with `ath10k_wmi_set_wmm_param()`. It assumes the caller passes a valid `wmi_wmm_params_all_arg`; there is no null check for `arg`.
- `ath10k_wmi_op_gen_request_stats()` requests firmware stats by writing `stats_mask` into `struct wmi_request_stats_cmd`.
- `ath10k_wmi_op_gen_force_fw_hang()` asks firmware to crash or hang after a requested delay. This is diagnostic/destructive and is exposed through the ops tables for all covered non-TLV versions.
- `ath10k_wmi_op_gen_dbglog_cfg()` and `ath10k_wmi_10_4_op_gen_dbglog_cfg()` program firmware debug logging. The older ABI uses 32-bit module masks even though the API takes `u64`; 10.4 uses 64-bit module masks. Passing `module_enable == 0` restores default WARN-level logging for all modules by setting the valid masks to all ones.
- `ath10k_wmi_op_gen_pktlog_enable()` masks the requested event bitmap with `ATH10K_PKTLOG_ANY` before sending it. `ath10k_wmi_op_gen_pktlog_disable()` emits a zero-length command.
- `ath10k_wmi_op_gen_pdev_set_quiet_mode()` programs quiet-period parameters for coexistence or channel quieting.
- `ath10k_wmi_op_gen_addba_clear_resp()`, `ath10k_wmi_op_gen_addba_send()`, `ath10k_wmi_op_gen_addba_set_resp()`, and `ath10k_wmi_op_gen_delba_send()` build block-ack control commands. They reject null peer MAC pointers, copy the peer address with `ether_addr_copy()`, and encode vdev, TID, status, initiator, reason, or buffer-size fields.
- `ath10k_wmi_10_2_4_op_gen_pdev_get_tpc_config()` requests 10.2.4-style transmit-power-control configuration. 10.4 also reuses this op for `.gen_pdev_get_tpc_config`.
- `ath10k_wmi_op_gen_pdev_enable_adaptive_cca()` builds the 10.2.4 adaptive-CCA command with enable, detection level, and margin.
- `ath10k_wmi_10_4_ext_resource_config()` sends 10.4 extended resource configuration, including host platform type, firmware feature bitmap, coexistence GPIO priority, disabled extra GPIO pins encoded as `-1`, TDLS vdev/table limits, and TDLS sleep/buffer station capacities derived from service bits.
- `ath10k_wmi_10_4_gen_update_fw_tdls_state()` sends 10.4 TDLS state and policy thresholds. If firmware advertises explicit-mode-only TDLS and the caller asks for active enablement, the function downgrades the state to passive. It also enables TDLS buffer-station options when the service bit exists.
- `ath10k_wmi_10_4_gen_tdls_peer_update()` builds a variable-length TDLS peer update command. The command struct contains placeholder space for one channel; the allocation adds `(peer_chan_len - 1) * sizeof(struct wmi_channel)` for additional channels. It copies peer operation classes and writes each channel using `ath10k_wmi_put_wmi_channel()`.
- `ath10k_wmi_10_4_gen_radar_found()` serializes radar pulse range metadata from `struct ath10k_radar_found_info` for firmware DFS confirmation/reporting.
- `ath10k_wmi_10_4_gen_per_peer_per_tid_cfg()` builds a per-peer/per-TID configuration command for ACK policy, aggregation, rate control, retry count, rate-code flags, RTS/CTS control, and extended TID config bitmap. It explicitly zeroes the command before populating fields.
- `ath10k_wmi_op_gen_echo()` emits an echo command used both as a normal firmware echo and as the WMI barrier primitive.
- `ath10k_wmi_10_2_4_op_gen_bb_timing()` serializes baseband TX/XPA timing settings for the 10.2.4 ops table.

Most builders do only local structural validation. Range checks for TIDs, rates, TDLS channel counts, TDLS operating-class lengths, and firmware feature compatibility must happen in callers or firmware. The TDLS peer update path is particularly sensitive because the allocation length and channel loop are driven by `cap->peer_chan_len`.

## Firmware Stats Formatting

The middle of the chunk converts parsed firmware statistics, already stored in `struct ath10k_fw_stats`, into a fixed-size text buffer of `ATH10K_FW_STATS_BUF_SIZE`. These helpers do not parse firmware events themselves; parsing is done earlier by version-specific `pull_fw_stats` functions and debug code accumulates multi-event snapshots before calling the selected `.fw_stats_fill` op.

PDEV formatting helpers:

- `ath10k_wmi_fw_pdev_base_stats_fill()` prints common PDEV channel and frame counters: noise floor, channel TX power, TX/RX frame count, RX clear count, cycle count, and PHY error count.
- `ath10k_wmi_fw_pdev_extra_stats_fill()` adds RTS bad/good, FCS bad, no-beacon, and MIB interrupt counters. It is used by 10.x and 10.4 stats output, not by the main firmware output.
- `ath10k_wmi_fw_pdev_tx_stats_fill()` prints host/firmware TX queueing and error counters such as HTT cookies queued/delivered, MSDU/MPDU queued, WMM drops, local enqueue/free, HW queue/reap, underruns, TX aborts, requeues, excessive retries, rate, self triggers, software retry failures, illegal-rate PHY errors, continuous xretry, TX timeout, PDEV resets, PHY underrun, and TXOP overflow.
- `ath10k_wmi_fw_pdev_rx_stats_fill()` prints route changes, status counts, ring fragment counters, HTT/local delivery counts, oversized A-MSDUs, PHY error counters, and MPDU FCS/MIC/encryption errors.

VDEV and peer helpers:

- `ath10k_wmi_fw_vdev_stats_fill()` prints legacy vdev stats including SNRs, RX/TX counters, RTS success/fail, discard/error counts, four-element TX frame/retry/failure arrays, ten-entry TX-rate history, and ten-entry beacon-RSSI history.
- `ath10k_wmi_fw_peer_stats_fill()` prints peer MAC, RSSI, TX/RX rates, and, unless the stats object is marked extended, RX duration.
- `ath10k_wmi_fw_vdev_stats_extd_fill()` prints 10.4 extended vdev counters, including aggregate/non-aggregate PPDU counts, MPDU queue/retry/failure counters, and optional fine-timing-measurement counts guarded by `WMI_VDEV_STATS_FTM_COUNT_VALID`.
- `ath10k_wmi_fw_extd_peer_stats_fill()` is intended to print extended peer MAC and RX duration entries from `fw_stats->peers_extd`.

Top-level fill functions:

- `ath10k_wmi_main_op_fw_stats_fill()` prints base PDEV, TX, RX, legacy VDEV, and legacy peer sections.
- `ath10k_wmi_10x_op_fw_stats_fill()` adds the extra PDEV stats before TX/RX and is wired into 10.1, 10.2, and 10.2.4.
- `ath10k_wmi_10_4_op_fw_stats_fill()` uses base/extra PDEV, adds 10.4-only TX counters after the common TX block, adds RX overflow after the common RX block, uses extended VDEV stats, prints normal peers, and, if `fw_stats->extended` is true, iterates `fw_stats->peers_extd`.

Each top-level formatter takes `ar->data_lock` while reading the stats lists. If no PDEV stats entry exists, it warns and exits through the common unlock path. After unlocking, it NUL-terminates the buffer at either `buf[len]` or `buf[len - 1]` if the accumulated length reached or exceeded the fixed buffer size.

## VDEV Subtype Mapping

The three subtype helpers translate generic `enum wmi_vdev_subtype` values into firmware-version-specific numeric constants:

- `ath10k_wmi_op_get_vdev_subtype()` maps legacy/main P2P and proxy-STA subtype values but rejects both mesh variants.
- `ath10k_wmi_10_2_4_op_get_vdev_subtype()` adds support for `WMI_VDEV_SUBTYPE_MESH_11S` but still rejects non-11s mesh.
- `ath10k_wmi_10_4_op_get_vdev_subtype()` supports both 11s and non-11s mesh subtypes.

These functions are integration gates between mac80211 virtual-interface types and firmware ABI values. Unsupported subtypes return `-EOPNOTSUPP`, letting higher layers fail interface creation before emitting malformed WMI commands.

## Barrier And Ordering

`ath10k_wmi_barrier()` provides a coarse ordering primitive for command streams that lack explicit acknowledgements. It reinitializes `ar->wmi.barrier` under `ar->data_lock`, sends an echo command with `ATH10K_WMI_BARRIER_ECHO_ID`, then waits up to `ATH10K_WMI_BARRIER_TIMEOUT_HZ` for the echo event path to complete the barrier.

The core start path uses this after a dummy vdev create/delete sequence because WMI and HTT can use separate HIF pipes and most WMI commands have no direct acknowledgements. Receiving the echo reply is treated as evidence that earlier WMI commands have been processed enough to avoid racing HTT RX ring startup against vdev creation/deletion.

Failure modes are explicit: echo submission errors are logged and returned; timeout returns `-ETIMEDOUT`.

## Operation Tables

The five static `struct wmi_ops` tables are the main dispatch surface produced by this chunk:

- `wmi_ops` covers the main non-10.x firmware ABI. It uses main service mapping, main RX/event parsers, main init/scan/peer-assoc builders, main firmware stats fill, legacy subtype mapping, and common command builders for WMM, stats, debug log, pktlog, quiet mode, ADDBA/DELBA, echo, and GPIO. Several optional ops are intentionally left unimplemented in comments, including beacon/probe templates, P2P GO beacon IE, adaptive QCS, adaptive CCA, and temperature.
- `wmi_10_1_ops` uses 10.x service mapping, 10.1 RX and init/start-scan/peer-assoc builders, 10.x service-ready and stats pullers, common event pullers, common command builders, 10.x stats fill, and legacy subtype mapping.
- `wmi_10_2_ops` uses 10.2 RX/stats/init/peer-assoc handling, 10.x service mapping, common builders, and adds `.gen_pdev_set_base_macaddr`, but still lacks temperature and adaptive CCA.
- `wmi_10_2_4_ops` adds 10.2.4 stats pulling, temperature, BSS channel-info request, 10.2.4 SWBA parser, TPC config, adaptive CCA, 10.2.4 subtype mapping, and baseband timing.
- `wmi_10_4_ops` uses 10.4 RX, service mapping, management RX/channel/SWBA/PHY error/DFS parsers, 10.4 init and peer-assoc builders, 64-bit debug-log config, 10.4 stats fill, extended resource config, TDLS state and peer update commands, TPC table command, radar-found command, per-peer/per-TID config, 10.4 subtype mapping, and 10.2-shared temperature/BSS-info/TPC-config/echo/GPIO helpers.

These tables define which driver features are available for a firmware generation. A wrapper in `wmi-ops.h` must check whether an op pointer exists or must only call features known to be present for the selected `wmi_op_version`.

## Attach, Host Memory, And Detach

`ath10k_wmi_attach()` is called during `ath10k_core_start()` after HTC initialization and BMI completion, before HTT initialization. It switches on `ar->running_fw->fw_file.wmi_op_version`:

- 10.4 selects `wmi_10_4_ops`, `wmi_10_4_cmd_map`, 10.4 vdev/pdev maps, common peer params, 10.2 peer flags, and non-TLV cipher suites.
- 10.2.4 selects 10.2.4 ops and command/parameter maps with 10.2 peer flags.
- 10.2 selects 10.2 ops and command map with 10.x vdev/pdev maps and 10.2 peer flags.
- 10.1 selects 10.1 ops, 10.x command/vdev/pdev maps, and 10.x peer flags.
- MAIN selects main ops and maps.
- TLV delegates to `ath10k_wmi_tlv_attach()` and selects TLV key-cipher suites.
- UNSET and MAX are rejected with `-EINVAL`.

After dispatch setup, attach initializes WMI completions for service-ready, unified-ready, barrier, and radar confirmation. It initializes service-ready and radar-confirmation work items. If the running firmware advertises `ATH10K_FW_FEATURE_MGMT_TX_BY_REF`, it initializes `ar->wmi.mgmt_pending_tx` as an IDR for pending management-frame TX descriptors.

`ath10k_wmi_free_host_mem()` frees firmware-requested coherent DMA host-memory chunks from `ar->wmi.mem_chunks[]` using each chunk's length, virtual address, and DMA address, then resets `num_mem_chunks` to zero. The function assumes the chunks were previously allocated coherently and that no firmware path will access them after this cleanup point.

`ath10k_wmi_detach()` handles by-reference management TX cleanup when that feature was enabled. Under `ar->data_lock`, it walks the `mgmt_pending_tx` IDR with `ath10k_wmi_mgmt_tx_clean_up_pending()`, which unmaps each pending skb DMA mapping, frees the tx skb through mac80211 with `ieee80211_free_txskb()`, frees the `ath10k_mgmt_tx_pkt_addr`, and returns zero for continued iteration. Detach then destroys the IDR, unlocks, cancels `svc_rdy_work`, and frees `ar->svc_rdy_skb`.

## Dependencies And Integration Points

This chunk depends on:

- Core ath10k state in `struct ath10k`, especially `ar->wmi`, `ar->running_fw`, `ar->data_lock`, `ar->dev`, `ar->hw`, `ar->coex_gpio_pin`, service bits, firmware feature bits, and work items.
- WMI ABI structs, maps, service bits, command IDs, field macros, and constants from `wmi.h` and related ath10k headers.
- The WMI wrapper layer in `wmi-ops.h`, whose function pointers match the operation tables populated here.
- mac80211 and kernel networking primitives: `struct sk_buff`, `ether_addr_copy()`, `ieee80211_free_txskb()`, and IEEE 802.11 WMM QoS info bits.
- Kernel synchronization and memory APIs: completions, spin locks with bottom halves disabled, workqueues, IDR, `dma_free_coherent()`, `dma_unmap_single()`, list helpers, and `scnprintf()`.
- Earlier event parsing in `wmi.c`, especially echo-event handling for the barrier and firmware-stat pullers that populate `struct ath10k_fw_stats`.
- Debugfs stats code, which accumulates split firmware stats events and ultimately calls the selected `.fw_stats_fill` op to render text.

The code also integrates with firmware capability negotiation. Several builders branch on `ar->wmi.svc_map`, and attach-time selection depends on firmware metadata. A mismatch between firmware version, command map, and ops table would route commands to the wrong ABI layout.

## State And Persistence Behavior

Most command builders are stateless on the host side: they produce one skb representing one firmware command. The state change happens when the wrapper sends the skb to firmware. Those commands may alter persistent or semi-persistent firmware behavior, including WMM parameters, stats collection requests, debug-log module masks and levels, pktlog filters, quiet mode, block-ack sessions, adaptive CCA, TDLS policy/state, TDLS peer capabilities, DFS/radar notifications, per-peer/TID retry and ACK policy, TPC requests, baseband timing, and firmware hang behavior.

Firmware stats formatting reads state already persisted in `struct ath10k_fw_stats` lists. The formatter itself only writes a caller-provided text buffer, but it must hold `ar->data_lock` because debug code updates and frees those lists under the same lock.

`ath10k_wmi_barrier()` mutates the `barrier` completion state and relies on a later echo event to complete it. This is transient synchronization state, not durable firmware configuration.

`ath10k_wmi_attach()` persists driver dispatch state into `ar->wmi` for the lifetime of the running firmware instance. The selected ops and maps determine all later WMI encoding/decoding. It also initializes completions and work items that survive until detach or core shutdown.

Host memory chunks are persistent shared resources while firmware is running. `ath10k_wmi_free_host_mem()` releases them and resets the count, which prevents double-free by count-based cleanup but does not clear stale entries in the array. Correct lifecycle ordering must ensure firmware no longer uses those DMA regions.

The management TX IDR tracks outstanding by-reference management frames. Detach force-cleans any entries not completed by firmware, unmapping DMA and freeing skbs so shutdown does not leak host memory or DMA mappings.

## Risks And Edge Cases

The main risk is firmware ABI mismatch. The command struct selected by each builder must match the command ID and map selected by `ath10k_wmi_attach()`. The 32-bit versus 64-bit debug-log module mask split is a concrete example: using the non-10.4 builder for 10.4 would truncate module masks, while using the 10.4 builder against older firmware would emit the wrong layout.

Several builders trust caller-supplied pointers and lengths. ADDBA/DELBA commands validate `mac`, but WMM, TDLS update, TDLS peer capabilities, channel arrays, radar info, per-peer/TID config, and BB timing do not validate all pointer or range inputs. In particular, `ath10k_wmi_10_4_gen_tdls_peer_update()` calculates skb length from `cap->peer_chan_len` and then indexes `chan_arg[i]`; callers must ensure the channel array is at least that long and that `peer_chan_len` fits the firmware structure limits.

The 10.4 extended-peer stats helper appears incomplete: `ath10k_wmi_fw_extd_peer_stats_fill()` updates a local `len` but never stores it back through `*length` and does not append a separator newline. When `ath10k_wmi_10_4_op_fw_stats_fill()` iterates `fw_stats->peers_extd`, each extended peer can be written at the same offset, and the final top-level terminator may ignore the extended-peer text length. This is a chunk-local output correctness risk for extended peer RX-duration reporting.

All stats formatters use `scnprintf(buf + len, buf_len - len, ...)` while accumulating `len`. If `len` exceeds `buf_len`, unsigned subtraction can produce a large size argument and `buf + len` can point beyond the fixed buffer. The final terminator handles `len >= buf_len`, but the intermediate calls rely on `scnprintf()` not being reached with an already-overfull offset. Large peer/vdev lists therefore depend on upstream limiting in debug stats accumulation.

The top-level stats fill functions warn and output an empty string when no PDEV entry exists. This is appropriate for malformed or incomplete stats snapshots, but consumers expecting partial peer/vdev output will not receive it.

`ath10k_wmi_barrier()` is only an ordering heuristic based on echo completion. The core comments say this means preceding commands have "mostly" been processed; it is not a full transactional acknowledgement for every firmware side effect. Timeout handling must be treated as a real firmware communication failure.

The ops tables intentionally leave some function pointers null. Feature code must test support or rely on version-gated paths before calling optional ops such as beacon template, probe template, P2P GO beacon IE, WoW/PNO features in non-TLV tables, adaptive QCS, adaptive CCA on older versions, or temperature on main/10.1/10.2.

Detach cleanup is feature-gated on `ATH10K_FW_FEATURE_MGMT_TX_BY_REF`. If future code initializes `mgmt_pending_tx` under another condition or shares this IDR with TLV-specific paths, attach/detach gating must stay consistent. Cleanup also assumes each IDR entry contains a valid skb and DMA mapping matching `msdu->len`.

`ath10k_wmi_free_host_mem()` frees based only on `num_mem_chunks`. If allocation partially failed or a chunk entry is corrupt, cleanup can pass bad DMA metadata to the DMA API. The function does not zero each entry after free, so callers must rely on `num_mem_chunks = 0` to prevent reuse.

## Test Signals

Useful tests and review checks for this chunk include:

- Build coverage for all non-TLV WMI versions so every `struct wmi_ops` initializer matches the current `wmi-ops.h` function-pointer layout.
- Attach tests or probes that verify each `ATH10K_FW_WMI_OP_VERSION_*` selects the expected ops table, command map, vdev/pdev/peer maps, peer flags, and key-cipher suite, and that unsupported versions return `-EINVAL`.
- Command encoding tests for WMM, stats request, force firmware hang, debug-log config, pktlog, quiet mode, ADDBA/DELBA, adaptive CCA, TDLS state, TDLS peer update with zero/one/multiple channels, radar-found, per-peer/TID config, echo, TPC config/table, and BB timing.
- ABI-specific debug-log tests confirming older firmware gets 32-bit module masks and 10.4 gets 64-bit masks.
- VDEV subtype tests for legacy, 10.2.4, and 10.4 mappings, especially mesh 11s and non-11s support differences.
- Barrier tests that exercise successful echo completion, echo submission failure, and timeout. The core dummy-vdev flow is a strong integration signal because it relies on the barrier before HTT RX startup.
- Firmware stats rendering tests for main, 10.x, and 10.4 output, including no-PDEV snapshots, many peers/vdevs, extended 10.4 vdev FTM valid/invalid counters, and extended peer RX-duration output. A specific regression test should catch that `ath10k_wmi_fw_extd_peer_stats_fill()` must advance the output length.
- Buffer-boundary tests for `ATH10K_FW_STATS_BUF_SIZE` with enough peers/vdevs to approach or exceed the text buffer.
- Detach tests with pending by-reference management TX entries that verify DMA unmap, skb free, entry free, IDR destroy, service-ready work cancellation, and `svc_rdy_skb` free.
- Host-memory cleanup tests that allocate multiple WMI memory chunks, call `ath10k_wmi_free_host_mem()`, and verify every chunk is freed exactly once and `num_mem_chunks` becomes zero.

For this research pipeline, the expected artifact is this chunk-only document at `Docs/researches/chunks/subset-b-004726_research.md`. The merged per-file report should reconcile this with earlier chunks that define the event parsers, stats pullers, command maps, and helper functions referenced here.
