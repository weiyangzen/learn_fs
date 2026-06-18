# Research: subset-b-004730

Grouped source research for the ath11k datapath/debugfs subset. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_htt_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_htt_stats.h

Purpose: Defines the firmware-facing HTT extended-statistics TLV schema used by ath11k debugfs. It is a contract header, not a parser: it assigns TLV tag IDs, bit masks, fixed and variable-length packed structs, counter-array dimensions, peer-stat request modes, and the debugfs HTT stats entry points.

Important APIs and types: `enum htt_tlv_tag_t` maps numeric firmware tags for TX pdev, TX HWQ, TQM, scheduler, ring interface, SRNG, peer, RX pdev/SOC, CCA, TWT, REO resource, sounding, OBSS PD, backpressure, PHY, and peer control-path stats. Key layouts include `htt_tx_pdev_stats_cmn_tlv`, `htt_tx_hwq_stats_cmn_tlv`, `htt_tx_tqm_*`, `htt_tx_de_*`, `htt_ring_if_stats_tlv`, `htt_sring_stats_tlv`, `htt_peer_*`, `htt_tx_peer_rate_stats_tlv`, `htt_rx_peer_rate_stats_tlv`, `htt_rx_pdev_rate_stats_tlv`, `htt_rx_pdev_fw_stats_tlv`, `htt_phy_*`, and `htt_peer_ctrl_path_txrx_stats_tlv`. The only exported routines are `ath11k_debugfs_htt_stats_init()`, `ath11k_debugfs_htt_ext_stats_handler()`, and `ath11k_debugfs_htt_stats_req()`, compiled to no-op stubs when `CONFIG_ATH11K_DEBUGFS` is disabled.

Control flow: No executable control flow lives here beyond debugfs stubs. Runtime flow is driven by `debugfs_htt_stats.c`: users request a stats type, the driver sends an HTT ext-stats command, target-to-host `EXT_STATS_CONF` messages are decoded by tag/length, and the matching struct definitions here determine how bytes are interpreted and printed.

State and persistence: The header owns no state. It defines transient firmware report formats and request constants such as `HTT_STATS_MAGIC_VALUE`, cookie bit masks, peer request selectors, and array bounds. Persistence is firmware-side counter accumulation and the debugfs request buffer maintained elsewhere.

Dependencies and integration points: Depends on Linux bit helpers, packed/flexible array conventions, `ETH_ALEN`, and the HTT ext-stats message definitions in `dp.h`. It integrates with `debugfs_htt_stats.c`, per-peer debugfs in `debugfs_sta.c`, RX HTT message dispatch in `dp_rx.c`, and HTT request generation in `dp_tx.c`.

Risks: Struct layout and tag IDs are firmware ABI. Incorrect array dimensions, missing `__packed`, or wrong masks corrupt parsing. Many TLVs are variable length and must be bounded by the incoming TLV length, not by assumed maximums. Duplicated names such as `HTT_TX_PDEV_STATS_NUM_SPATIAL_STREAMS` appear in multiple contexts and can hide incompatible firmware evolution. Endianness comments on string/name fields matter for display code.

Test signals: Build with and without `CONFIG_ATH11K_DEBUGFS`; request every supported HTT stat type through debugfs; validate peer-info and peer control-path stats; exercise multi-segment `EXT_STATS_CONF` with done-bit handling; fuzz TLV lengths around flexible arrays; compare printed counters against firmware logs for TX/RX rate, TQM, ring backpressure, PHY, TWT, and CCA reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_htt_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_sta.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_sta.c

Purpose: Implements per-station ath11k debugfs files for TX/RX peer statistics, HTT peer statistics, peer packet logging, manual aggregation controls, HTT peer stats reset, peer power-save state/duration, and optional CFR capture control.

Important APIs and functions: `ath11k_debugfs_sta_op_add()` creates station debugfs files. `ath11k_debugfs_sta_add_tx_stats()` folds per-peer TX completion counters into `arsta->tx_stats` by HE/VHT/HT/legacy rate, bandwidth, NSS, GI, success/fail/retry, AMPDU, BA failures, ACK failures, and duration. `ath11k_debugfs_sta_update_txcompl()` delegates completion accounting to `ath11k_dp_tx_update_txcompl()`. File operations cover `tx_stats`, `rx_stats`, `htt_peer_stats`, `peer_pktlog`, `aggr_mode`, `addba`, `addba_resp`, `delba`, `htt_peer_stats_reset`, `peer_ps_state`, `current_ps_duration`, `total_ps_duration`, and optional `cfr_capture`.

Control flow: Station creation calls `ath11k_debugfs_sta_op_add()`, conditionally exposing files based on extended stat settings and WMI service bits. Reads allocate or use small buffers, lock driver state, format counters, and return via `simple_read_from_buffer()`. Writes parse user input, validate range and device state, then send WMI or HTT commands: packet-log filters, ADD/DELBA controls, aggregation mode changes, CFR capture config, and HTT peer stats reset. Opening `htt_peer_stats` allocates a request buffer, records the target peer address, sends `ath11k_debugfs_htt_stats_req()`, and releases the buffer on close.

State and persistence: Mutates runtime-only station and debug state: `arsta->tx_stats`, `arsta->rx_stats`, `arsta->aggr_mode`, `arsta->cfr_capture`, peer power-save timing fields, `ar->debug.htt_stats.stats_req`, and `ar->debug.pktlog_peer_*`. Locks split by ownership: `ar->conf_mutex` protects configuration/debugfs operations, `ar->data_lock` protects TX and power-save station fields, `ab->base_lock` protects RX peer stats, and `ar->cfr.lock` protects CFR peer count.

Dependencies and integration points: Depends on mac80211 station debugfs hooks, ath11k peer and core state, WMI peer commands, DP TX completion accounting, HTT stats request/response plumbing, service-bit discovery, and optional `CONFIG_ATH11K_CFR`. It exposes datapath and firmware behavior to userspace under debugfs.

Risks: The TX stats updater trusts rate-derived indexes (`mcs`, `bw`, `nss`, `gi`, legacy index) and requires upstream bounds correctness. Debugfs writes can change live aggregation and CFR behavior, so state checks and mutex coverage are important. `htt_peer_stats` uses a single `ar->debug.htt_stats.stats_req` pointer, so concurrent opens can race semantically even with mutex-protected assignment. Counter formatting uses fixed-size buffers and relies on `scnprintf()` truncation. CFR enable-count decrement must match previous enable state to avoid underflow-like accounting errors.

Test signals: Enable extended TX/RX stats and verify per-rate buckets after successful, failed, retried, AMPDU, and legacy transmissions; read RX peer stats under traffic; request HTT peer stats and reset them; toggle peer pktlog; switch aggregation auto/manual and send addba/addba_resp/delba; read power-save duration while a station enters/leaves PS; validate CFR capture parsing, range checks, max-peer threshold, disable path, and WMI error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_sta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_sta.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_sta.h

Purpose: Declares the station debugfs integration points and provides no-op fallbacks when ath11k debugfs support is not compiled.

Important APIs and types: Exposes `ath11k_debugfs_sta_op_add()` for mac80211 station debugfs file creation, `ath11k_debugfs_sta_add_tx_stats()` for per-station TX counter accumulation, and `ath11k_debugfs_sta_update_txcompl()` for TX completion stat updates. It includes `core.h` and `hal_tx.h` for `struct ath11k`, `struct ath11k_sta`, `struct ath11k_per_peer_tx_stats`, and `struct hal_tx_status`.

Control flow: With `CONFIG_ATH11K_DEBUGFS`, callers bind to implementations in `debugfs_sta.c`. Without it, `ath11k_debugfs_sta_op_add` is `NULL` and the stat update helpers inline to empty functions, letting datapath code call them without preprocessor noise.

State and persistence: Owns no state. Its compile-time configuration changes whether station debugfs state is reachable and whether TX completion paths update debug-only counters.

Dependencies and integration points: Used by mac80211 ops registration and TX completion paths. It bridges debugfs-specific accounting to normal ath11k datapath code while keeping non-debug builds lean.

Risks: Prototype drift would break callers in TX and station setup. The `NULL` station op must remain acceptable to the mac80211 registration path. Non-debug builds intentionally lose these counters, so no functional behavior should depend on the helpers doing work.

Test signals: Compile both `CONFIG_ATH11K_DEBUGFS=y` and disabled builds; create/destroy stations and ensure debugfs entries appear only in debug builds; run TX completion paths in non-debug builds to confirm no unresolved symbols or behavior dependency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debugfs_sta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp.c

Purpose: Provides ath11k datapath core setup/teardown and servicing: peer datapath setup, SRNG allocation and MSI wiring, common TX/RX/REO ring setup, link descriptor bank/scatter setup, pdev RX/monitor allocation, HTT HTC connection, vdev TCL metadata setup, pending TX cleanup, and shadow-register timer maintenance.

Important APIs and functions: Public entry points include `ath11k_dp_alloc()`, `ath11k_dp_free()`, `ath11k_dp_pdev_pre_alloc()`, `ath11k_dp_pdev_alloc()`, `ath11k_dp_pdev_free()`, `ath11k_dp_htt_connect()`, `ath11k_dp_vdev_tx_attach()`, `ath11k_dp_peer_setup()`, `ath11k_dp_peer_cleanup()`, `ath11k_dp_srng_setup()`, `ath11k_dp_srng_cleanup()`, `ath11k_dp_link_desc_setup()`, `ath11k_dp_link_desc_cleanup()`, `ath11k_dp_service_srng()`, and shadow timer helpers. Static helpers calculate MSI groups, initialize common rings, allocate link descriptor banks, build idle scatter lists, set up the WBM idle ring, and free pending TX skbs.

Control flow: Device allocation initializes DP lists/locks, computes link descriptor count, sets up the WBM idle ring, seeds idle link descriptors, creates common SRNGs, allocates per-TCL TX status arrays, and programs DSCP/TID mapping. Common SRNG setup creates WBM release, TCL command/status/data/completion, REO reinject, RX release, REO exception/command/status rings, initializes HAL ring contents, starts shadow timer metadata, and calls hardware `reo_setup()`. Interrupt/NAPI servicing checks the current external IRQ group masks, processes TX completions, RX errors, WBM RX releases, REO destination RX, monitor rings, REO status, RXDMA errors, and refill rings until budget is exhausted. Cleanup unwinds rings, timers, REO command lists, link descriptors, IDRs, and mapped pending TX buffers.

State and persistence: Mutates `ab->dp`, `ar->dp`, HAL SRNG state, DMA-coherent/noncoherent ring allocations, IDRs for TX/RX buffers, pending TX waitqueues, monitor lists, timer fields, peer `dp_setup_done`, vdev `tcl_metadata`, and address-search flags. Nothing is durable, but DMA addresses and ring IDs are hardware-visible and must remain valid until teardown.

Dependencies and integration points: Depends on HAL SRNG APIs, HIF/MSI helpers, WMI peer routing, HTC HTT service connection, DP TX/RX modules, peer RX TID/fragment helpers, mac80211 vdev/peer lifecycle, AHB/PCI interrupt paths, and hardware params (`ring_mask`, `hal_params`, `alloc_cacheable_memory`, `supports_shadow_regs`, `htt_peer_map_v2`).

Risks: Error paths in ring and descriptor setup must free partially allocated DMA memory; `ath11k_dp_srng_setup()` currently returns after HAL setup failure without freeing its just-allocated ring memory, so callers rely on later cleanup. Ring number plus `mac_id` affects MSI grouping and can misroute interrupts. Cached ring allocation uses noncoherent DMA and must match HAL cache handling. Link descriptor counts and bank limits can reject large configs. `ath11k_dp_service_srng()` consumes a shared budget across heterogeneous rings, so starvation and budget accounting matter. Shadow timer callbacks require SRNG lock discipline and safe timer deletion during teardown.

Test signals: Probe/remove and reset loops with failure injection at every SRNG/DMA allocation; MSI vector grouping across PCI/AHB variants; TX completion and RX traffic under NAPI budget pressure; peer setup failure after partial TID setup; monitor mode attach/detach; WBM idle link descriptor bank/scatter paths above and below threshold; noncoherent cached-ring platforms; shadow-register timer start/stop during TX and teardown; vdev attach for STA/AP/IBSS/monitor with and without peer-map-v2 support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp.h

Purpose: Defines ath11k datapath state, ring sizing, HTT host/target message formats, PPDU stats formats, RX filter masks, peer map events, ext-stats messages, and public DP function prototypes.

Important APIs and types: Core state structs include `dp_rx_tid`, `dp_reo_cmd`, `dp_srng`, `dp_rxdma_ring`, `dp_tx_ring`, `ath11k_mon_data`, `ath11k_pdev_dp`, `ath11k_hp_update_timer`, and `ath11k_dp`. Constants define TX/RX/REO/RXDMA ring sizes, buffer sizes, descriptor-bank limits, cookie masks, TCL metadata fields, PPDU stats tags, monitor filter masks, and shadow timer intervals. Packed HTT layouts include version, SRING setup, PPDU stats config/indication, RX ring selection, full monitor config, peer map/unmap, packet log, ext-stats request/response, and PPDU user/rate/completion structs. `ath11k_dp_get_mac_addr()` handles endian-aware MAC extraction.

Control flow: The header encodes control messages consumed by `dp_tx.c` and response/event formats consumed by `dp_rx.c`. It also declares the lifecycle and service functions implemented in `dp.c`, allowing core probe, bus interrupt handlers, mac80211 vdev/peer setup, RX monitor code, and ring users to share DP primitives.

State and persistence: Defines in-memory runtime state for SOC-level DP and per-pdev DP. Lists track REO commands and full monitor MPDUs; IDRs map software buffer IDs to skbs; DMA ring descriptors expose host memory to firmware/hardware; timers defer shadow head/tail pointer updates. The state is rebuilt on probe/reset and is not persistent beyond device lifetime.

Dependencies and integration points: Includes `hal_rx.h` and references `ath11k_base`, `ath11k_peer`, `ath11k_vif`, `hal_srng`, `hal_tcl_status_ring`, `ath11k_ext_irq_grp`, `sk_buff`, `timer_list`, IDR, locks, and mac80211 constants. It is a high-fanout header for `dp.c`, `dp_tx.c`, `dp_rx.c`, `peer.c`, `mac.c`, bus interrupt code, copy engines, and debugfs HTT stats.

Risks: This file is firmware/hardware ABI dense: bit masks, packed layouts, enum numeric values, and ring sizes must match target firmware and HAL expectations. A duplicate `HTT_TX_WBM_COMP_INFO0_REINJECT_REASON` define and typo-like `FLASG` names are harmless only because users already match them. Changing ring sizes affects memory use, interrupt load, and firmware capacity. Flexible array and payload-size users must validate lengths before reading. Endian-sensitive MAC unpacking is isolated in `ath11k_dp_get_mac_addr()` and should be reused.

Test signals: Compile all users after HTT/HAL schema changes; run HTT version, SRING setup, PPDU stats, RX ring selection, full monitor, peer map/unmap, pktlog, and ext-stats flows; verify RX monitor filters produce expected TLVs; stress TX IDR and RX refill cookie bounds; validate ring sizes on each supported hardware family; run big-endian build or static checks for MAC extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/dp.h -->
