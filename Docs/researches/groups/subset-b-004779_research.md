# Research: subset-b-004779

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx.c

## Purpose
This file implements the legacy DMA transmit and receive data path for the wil6210 60 GHz wireless driver, plus data-path routines shared by both legacy and enhanced DMA through `wil->txrx_ops`. It owns legacy vring allocation, RX buffer posting/reaping, TX descriptor construction, TSO/checksum offload programming, netdev queue stop/wake decisions, AP forwarding/multicast replication, EAPOL split-rekey handling, and TX completion accounting.

## Important APIs, Types, and Functions
- Module parameters and globals: `rx_align_2`, `rx_large_buf`, and `drop_if_ring_full` alter RX buffer layout/size and TX backpressure behavior.
- Ring helpers: `wil_ring_wmark_low()`, `wil_ring_wmark_high()`, `wil_ring_avail_low()`, and `wil_ring_avail_high()` drive queue throttling; `wil_is_tx_idle()` waits for TX rings to drain during power transitions.
- Legacy ring lifecycle: `wil_vring_alloc()`, `wil_vring_free()`, `wil_rx_init()`, `wil_rx_fini()`, `wil_vring_init_tx()`, `wil_tx_vring_modify()`, and `wil_vring_init_bcast()` allocate coherent descriptors, map WMI ring configuration, and clean pending DMA/SKB state.
- RX path: `wil_vring_alloc_skb()` posts a DMA-mapped SKB, `wil_vring_reap_rx()` consumes completed descriptors into `skb->cb`, `wil_rx_handle()` feeds monitor packets directly or sends data through reorder, and `wil_netif_rx_any()` performs crypto/error checks before local delivery.
- TX path: `wil_start_xmit()` chooses a unicast, station, broadcast, or multicast-to-unicast ring; `wil_tx_ring()` serializes against suspend/resume and calls `__wil_tx_ring()` or `__wil_tx_vring_tso()`; `wil_tx_complete()` reaps descriptors, unmaps DMA, updates statistics, handles EAPOL completion, and wakes queues.
- Offload support: `wil_tx_desc_map()`, `wil_tx_desc_offload_setup()`, `wil_tx_desc_offload_setup_tso()`, `wil_tx_last_desc()`, and `wil_tx_desc_set_nr_frags()` encode descriptor fields for checksum and TSO.
- Security helpers: `reverse_memcmp()`, `wil_rx_crypto_check()`, `wil_rx_error_check()`, `wil_skb_is_eap_3()`, `wil_skb_is_eap_4()`, `wil_enable_tx_key_worker()`, and `wil_tx_complete_handle_eapol()` implement PN replay protection and station split-rekey sequencing.
- Dispatch registration: `wil_init_txrx_ops_legacy_dma()` fills `struct wil_txrx_ops` so the rest of the driver can call legacy DMA through a common interface.

## Control Flow
RX initialization sizes the buffer with `wil_rx_buf_len_init()`, allocates `wil->ring_rx`, registers it with firmware through `wmi_rx_chain_add()`, and posts descriptors via `wil_rx_refill()`. NAPI calls `wil_rx_handle()`, which repeatedly calls `wil_vring_reap_rx()`. Reaping checks descriptor ownership, unmaps DMA, copies descriptor metadata into `skb->cb`, validates MID/CID/length, accounts MCS, handles radiotap monitor mode, consumes BAR/non-data frames, adjusts checksum state, strips optional SNAP alignment bytes, and returns an SKB. Normal data packets are passed to `wil_rx_reorder()`, while monitor packets go directly through `wil_netif_rx_any()`.

TX starts at `wil_start_xmit()`. It rejects packets when firmware or VIF connectivity is not ready, then selects a ring based on interface mode and destination: station mode uses the first active peer ring, AP unicast uses CID lookup, AP broadcast may use a dedicated broadcast ring, and PBSS or multicast-to-unicast duplicates frames across peer rings after rewriting the destination address. `wil_tx_ring()` protects per-ring state and rejects suspend/resume races. Non-GSO frames map the linear head and fragments, write descriptors only after DMA mappings succeed, advance `swhead`, and ring the hardware tail register. GSO frames build a header descriptor and per-segment data descriptors with TSO metadata. Completion walks from `swtail`, waits for the last fragment's DU bit, unmaps each descriptor, accounts one SKB at the context slot carrying the SKB pointer, zeroes context before advancing the tail, and updates net queues.

## State and Persistence Behavior
All persistent state is in `struct wil6210_priv`, `struct wil_ring`, per-descriptor `struct wil_ctx`, `struct wil_ring_tx_data`, VIF status, and station statistics/crypto arrays. There is no disk persistence. Critical state includes coherent descriptor memory (`vring->va`/`pa`), software head/tail cursors, `ring2cid_tid`, per-peer PN replay windows, `ptk_rekey_state`, `dot1x_open`, and net queue stopped flags. Memory barriers before head advancement and hardware tail writes are essential because the device and completion path share descriptors.

## Dependencies and Integration Points
The file depends on Linux networking and DMA APIs, NAPI, cfg80211/nl80211 interface types, WMI commands/events, tracepoints, and register access through `wil_w()`. It integrates with RX reorder/BAR logic, WMI ADDBA, firmware ring configuration, debugfs/dynamic debug traces, PM suspend status bits, and netdev queue APIs. Enhanced DMA reuses shared functions such as `wil_start_xmit()`, `wil_netif_rx_any()`, `wil_tx_latency_calc()`, EAPOL helpers, and `reverse_memcmp()` through the operation table.

## Risks
Descriptor ownership and cursor races are the main risk; missing `wmb()` ordering can let completion consume stale descriptors. DMA mapping error unwinding must exactly unmap descriptors already mapped, especially across fragments and TSO. Legacy RX CID is only 3 bits, so AP/P2P_GO lookup by transmitter address is required for more than eight peers. `skb->cb` is heavily overloaded for RX descriptors, TX latency timestamps, and eDMA status in shared code. Queue stop/wake behavior changes if `drop_if_ring_full` is enabled. EAPOL split-rekey state is sensitive to message classification and completion ordering. Broadcast duplication rewrites destination addresses and can accidentally loop traffic if source filtering or ring eligibility changes.

## Test Signals
Useful validation includes TX/RX traffic in station, AP, PBSS, monitor, privacy, and non-privacy modes; multi-peer AP tests above eight CIDs; RX reorder with BAR frames; multicast-to-unicast and broadcast ring paths; checksum offload and GSO/TSO traffic; suspend/resume drain via `wil_is_tx_idle()`; ring-full behavior with both busy and drop modes; PN replay/key-missing negative tests; EAPOL rekey message 3/4 and 4/4 sequencing; and counters in `wil_net_stats`, netdev stats, dynamic debug dumps, tracepoints, and queue stop/wake behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx.h

## Purpose
This header defines the legacy TX/RX descriptor ABI, shared ring helper routines, EAPOL key structures, skb control-buffer layouts, and exported TX/RX data-path entry points for wil6210. It is the common contract between legacy DMA code, enhanced DMA code, interrupt/reorder logic, WMI setup, and the netdev transmit path.

## Important APIs, Types, and Functions
- Descriptor address helpers: `wil_desc_addr()` and `wil_desc_addr_set()` encode/decode 48-bit DMA addresses used by legacy descriptors.
- Legacy descriptor structures: `struct vring_tx_mac`, `struct vring_tx_dma`, `struct vring_rx_mac`, `struct vring_rx_dma`, `struct vring_tx_desc`, `struct vring_rx_desc`, `union wil_tx_desc`, `union wil_rx_desc`, and `union wil_ring_desc`.
- Bit definitions: MAC/DMA TX fields, RX error/status bits, TSO descriptor type constants, and EAPOL key constants define the hardware-facing wire format.
- SKB metadata: `struct skb_rx_info`, `wil_skb_rxdesc()`, `wil_skb_get_cid()`, and `wil_skb_set_cid()` store descriptor and CID state inside `skb->cb`.
- Ring helpers: `wil_ring_is_empty()`, `wil_ring_next_tail()`, `wil_ring_advance_head()`, `wil_ring_is_full()`, `wil_ring_used_tx()`, `wil_ring_avail_tx()`, and `wil_get_min_tx_ring_id()` abstract cursor math for both DMA modes.
- Packet helpers: `wil_skb_get_da()`, `wil_skb_get_sa()`, `wil_need_txstat()`, `wil_consume_skb()`, `wil_is_back_req()`, and `wil_val_in_range()`.
- Public prototypes: RX delivery/reorder/BAR, TX data init, legacy ops initialization, and TX latency accounting.

## Control Flow
The header has no runtime control flow of its own, but its inline helpers are on hot paths. RX code decodes descriptor bitfields through `wil_rxdesc_*()` helpers, stores the descriptor in `skb->cb`, and later recovers CID/security/reorder parameters. TX code computes used/available slots with ring helpers before writing descriptors and advancing `swhead`. Completion code uses `wil_consume_skb()` to optionally report Wi-Fi ACK status to sockets that requested it.

## State and Persistence Behavior
The header defines in-memory hardware/shared-memory layouts. State is transient and includes descriptor ownership bits, ring cursor fields in `struct wil_ring`, per-descriptor mapping state in `struct wil_ctx`, and `skb->cb` metadata. The layouts are packed and must remain aligned with firmware/hardware expectations; changing them changes the device ABI.

## Dependencies and Integration Points
It includes `wil6210.h` and `txrx_edma.h`, so it bridges shared private driver state with both descriptor formats. It depends on Linux SKB, Ethernet, IEEE 802.11, DMA, checksum, and socket ACK APIs. `wil_get_min_tx_ring_id()` integrates with eDMA by reserving ring 0 for RX when enhanced DMA is active.

## Risks
The descriptor structs and masks are hardware ABI; wrong bit positions or packing cause silent data corruption. `skb->cb` space is limited and shared with eDMA status storage, so additions can overflow or alias metadata. Ring cursor helpers assume power-of-two-sized circular rings and one empty slot. `wil_rxdesc_retry()` reads bit 31 of `d0`, which overlaps the documented extended subtype field, so users must understand legacy hardware semantics before relying on retry. Include ordering is tight because this file references enhanced descriptor types through `union wil_tx_desc`.

## Test Signals
Compile-time signals include `BUILD_BUG_ON()` checks in users of descriptor sizes and structure packing warnings. Runtime signals include descriptor hex dumps, correct CID/TID/MID extraction, ACK status delivery for sockets requesting Wi-Fi status, correct ring availability under wraparound, and successful operation in both legacy and eDMA builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx_edma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx_edma.c

## Purpose
This file implements the enhanced DMA data path for wil6210. Compared with legacy vrings, eDMA uses separate TX/RX descriptor rings and TX/RX status rings, buffer IDs for RX, optional compressed RX status, optional hardware RX reordering, and enhanced descriptors with 64-bit DMA address support. It supplies the eDMA implementation of `wil->txrx_ops` while reusing common netdev TX/RX delivery logic from `txrx.c`.

## Important APIs, Types, and Functions
- Status ring lifecycle: `wil_find_free_sring()`, `wil_sring_alloc()`, `wil_sring_free()`, `wil_tx_init_edma()`, and `wil_tx_fini_edma()` allocate coherent completion queues and configure them through WMI.
- Descriptor ring lifecycle: `wil_ring_alloc_desc_ring()`, `wil_ring_free_edma()`, `wil_init_rx_desc_ring()`, `wil_ring_init_tx_edma()`, `wil_ring_init_bcast_edma()`, and `wil_tx_ring_modify_edma()`.
- RX buffer ID management: `wil_init_rx_buff_arr()`, `wil_free_rx_buff_arr()`, `wil_move_all_rx_buff_to_free_list()`, `wil_ring_alloc_skb_edma()`, and `wil_rx_refill_edma()` move buffers between free and active lists and post descriptors.
- RX status processing: `wil_get_next_rx_status_msg()`, `wil_sring_advance_swhead()`, `wil_sring_reap_rx_edma()`, `wil_rx_handle_edma()`, `wil_check_bar()`, `wil_rx_error_check_edma()`, and `wil_rx_crypto_check_edma()`.
- TX status processing: `wil_get_next_tx_status_msg()` and `wil_tx_sring_handler()` reap status messages, unmap completed descriptors, account SKBs, and update queue state.
- eDMA TX descriptor programming: `wil_tx_desc_map_edma()`, `wil_tx_desc_unmap_edma()`, `wil_tx_desc_offload_setup_tso_edma()`, `wil_tx_tso_gen_desc()`, and `__wil_tx_ring_tso_edma()`.
- Dispatch registration: `wil_init_txrx_ops_edma()` installs eDMA callbacks in the common operation table.

## Control Flow
TX initialization allocates a TX status ring, sends `wil_wmi_tx_sring_cfg()`, sets descriptor-ready polarity, and records `tx_sring_idx`. TX descriptor rings are created on connect/broadcast setup with WMI add commands. Common `wil_start_xmit()` eventually calls common non-GSO TX or eDMA TSO through `txrx_ops`. TX completions arrive as status messages: `wil_tx_sring_handler()` reads messages while the descriptor-ready bit matches expected polarity, validates ring IDs and descriptor counts, walks the corresponding descriptor ring from `swtail`, unmaps each DMA segment, consumes the SKB on the context carrying it, advances tails, periodically updates hardware status-ring tail, and wakes queues.

RX initialization validates status compression versus software reorder, sizes the status ring larger than the descriptor ring, configures default RX offload, allocates one or more RX status rings, allocates the RX descriptor ring and a coherent SW-tail pointer, builds a buffer-ID array, and posts initial RX buffers. `wil_rx_handle_edma()` scans all RX status rings under NAPI quota. `wil_sring_reap_rx_edma()` reads a status message, validates/retries buffer ID visibility, extracts and unmaps the active SKB, returns the buffer ID to the free list, validates length/CID, coalesces chained buffers until EOP, handles BAR frames for software reorder, applies data offset compensation, stores status in `skb->cb`, and returns a full packet. Packets go straight to `wil_netif_rx_any()` when hardware reorder is used or to `wil_rx_reorder()` otherwise. At the end of a pass, status-ring tails and RX descriptor credits are returned to hardware.

## State and Persistence Behavior
The file maintains only volatile driver/device state: `wil->srings[]`, `wil->ring_rx`, `wil->ring_tx[]`, `wil->rx_buff_mgmt`, status-ring ready polarity, RX chaining state in `sring->rx_data`, invalid-buffer counters, per-descriptor DMA mapping context, and TX/RX statistics. The buffer array uses ID 0 as invalid, so valid IDs run from 1 through configured count. DMA physical addresses for RX buffers are temporarily stored in `skb->cb` until completion, then `skb->cb` is reused for the RX status message.

## Dependencies and Integration Points
This file depends on enhanced descriptor/status definitions from `txrx_edma.h`, common ring/netdev helpers from `txrx.h`, WMI eDMA commands declared in `wil6210.h`, Linux DMA/SKB/list APIs, NAPI, and tracepoints. It integrates with firmware capability/configuration paths through `use_compressed_rx_status`, `use_rx_hw_reordering`, `num_rx_status_rings`, `rx_status_ring_order`, `tx_status_ring_order`, `rx_buff_id_count`, and aggregation settings.

## Risks
RX buffer-ID handling is delicate: missing IDs, stale IDs, or invalid IDs can leak buffers or drop frames, so the reset and free-list paths are important. `skb->cb` reuse across DMA address storage and status storage makes ordering constraints strict. Compressed RX status cannot support software reorder, and the code rejects that combination. Status-ring ready polarity must flip exactly on wraparound. TX completion trusts firmware-provided `num_descriptors`; invalid values can desynchronize descriptor tails. eDMA ring modify is unsupported, so roaming or peer retargeting must use a different lifecycle than legacy. Error unwinding in TSO must unmap all descriptors generated before failure.

## Test Signals
Validate eDMA with station/AP/broadcast traffic, multiple RX status rings, hardware and software RX reordering, compressed and extended status modes, chained RX packets, invalid/corrupt buffer ID injection, checksum offload status, L2 MIC/KEY/REPLAY/A-MSDU errors, TSO over IPv4 and IPv6, TX status ring wrap and polarity flip, ring-full behavior, and cleanup under disconnect/reset. Counters to watch include `invalid_buff_id_cnt`, `free_list_empty_cnt`, per-station RX/TX/error stats, tracepoints, and status-ring hardware tail updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx_edma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx_edma.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx_edma.h

## Purpose
This header defines enhanced DMA descriptor and status-ring formats, eDMA constants, status accessors, 64-bit DMA address helpers, and public eDMA TX/RX entry points for wil6210. It is the hardware ABI companion to `txrx_edma.c`.

## Important APIs, Types, and Functions
- Ring sizing and IDs: `WIL_SRING_SIZE_ORDER_*`, default RX/TX status-ring orders, default RX buffer ID count, `WIL_DEFAULT_RX_STATUS_RING_ID`, `WIL_RX_DESC_RING_ID`, and interrupt index constants.
- Descriptor types: `struct wil_ring_rx_enhanced_mac`, `struct wil_ring_rx_enhanced_dma`, `struct wil_rx_enhanced_desc`, `struct wil_ring_tx_enhanced_dma`, `struct wil_ring_tx_enhanced_mac`, and `struct wil_tx_enhanced_desc`.
- Status types: `struct wil_ring_tx_status`, `struct wil_rx_status_compressed`, `struct wil_rx_status_extension`, and `struct wil_rx_status_extended`.
- RX status accessors: helpers extract length, MCS, CB mode, flow ID, CID/TID, EOP, buffer ID, data offset, frame type, FC, sequence, MID, error bits, L2/L3/L4 status, checksum state, security, and key ID.
- TX status/address helpers: `wil_tx_status_get_mcs()`, `wil_desc_set_addr_edma()`, `wil_tx_desc_get_addr_edma()`, and `wil_rx_desc_get_addr_edma()`.
- Public prototypes: `wil_configure_interrupt_moderation_edma()`, `wil_tx_sring_handler()`, `wil_rx_handle_edma()`, and `wil_init_txrx_ops_edma()`.

## Control Flow
The header provides inline logic used while processing status messages. RX code first checks descriptor-ready polarity, then uses helpers to interpret compressed fields or extended fields depending on driver mode. CID/TID decoding handles DLPF lookup hit and miss layouts. Checksum helper maps hardware L3/L4 status into Linux `CHECKSUM_UNNECESSARY` or `CHECKSUM_NONE`. Address helpers split or reconstruct 64-bit DMA addresses across enhanced descriptor fields.

## State and Persistence Behavior
All structures represent transient coherent-memory records shared with hardware. The ready bit polarity and buffer ID fields are stateful protocol fields; `wil_rx_status_reset_buff_id()` writes back to the coherent status slot to clear a consumed ID. Packed structure layout and bit positions are persistent ABI contracts with firmware/hardware but not persisted to storage.

## Dependencies and Integration Points
The header includes `wil6210.h` for common state, bit extraction, statistics, and ring types. It integrates with `txrx.h` through the shared `union wil_tx_desc`/`union wil_rx_desc` model and with IRQ code through the exported status handlers. It depends on Linux SKB and checksum semantics indirectly via inline helpers.

## Risks
Bitfield extraction must match hardware status exactly. A wrong DLPF hit/miss interpretation can deliver traffic to the wrong station/TID. `wil_rx_status_get_retry()` returns a conservative constant because eDMA lacks a retry bit, which can affect reorder duplicate handling. Compressed status masks management/control frame details and is only safe with hardware reorder. `wil_rx_status_get_data_offset()` accepts only encoded offsets 0 and 3, treating other values as invalid. Address helpers must preserve bits 48-63 or high-memory DMA will fail.

## Test Signals
Build tests should catch packed layout size changes where users assert descriptor sizes. Runtime tests should verify status parsing for DLPF hit/miss, compressed versus extended status, checksum states, MID defaulting, buffer ID reset, 64-bit DMA addressing, TSO descriptor fields, and MCS/CB-mode accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/txrx_edma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil6210.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil6210.h

## Purpose
This is the central private header for the wil6210 driver. It declares module-wide tunables, firmware names, hardware register addresses, firmware memory mappings, ring/status-ring data structures, station/VIF/private driver state, operation tables, logging/register helpers, and cross-file function prototypes. The TX/RX and crash-dump files in this work item depend on it for almost all shared state and integration contracts.

## Important APIs, Types, and Functions
- Global tunables: firmware recovery, MTU, aggregation, RX buffer sizing/alignment, AP SME, FTM, ring-full behavior, and max associated stations.
- Hardware constants: firmware/board names, ring sizes, max CIDs/rings/status rings, interrupt moderation defaults, register addresses, interrupt bits, eDMA registers, firmware assertion registers, and hardware version IDs.
- Mapping and mailbox types: `struct fw_map`, WMI mailbox ring/header/control structures, and pending WMI event records.
- DMA/ring types: `struct wil_ring_dma_addr`, `struct wil_ctx`, `struct wil_ring`, `struct wil_status_ring`, `struct wil_ring_rx_data`, `struct wil_ring_tx_data`, and `struct wil_txrx_ops`.
- Statistics/security/reorder types: `struct wil_net_stats`, `struct wil_tid_ampdu_rx`, `struct wil_tid_crypto_rx_single`, `struct wil_tid_crypto_rx`, and `struct wil_sta_info`.
- Interface/device state: `struct wil6210_vif`, `struct wil_rx_buff_mgmt`, `struct wil_fw_stats_global`, and the large `struct wil6210_priv`.
- Helpers: `WIL_GET_BITS()`, `wil_mtu2macbuf()`, CID/TID encode/decode, `wil_to_dev()`/VIF/netdev conversions, logging macros, register accessors `wil_r()`/`wil_w()`/`wil_s()`/`wil_c()`, and `wil_cid_valid()`.
- Prototypes: lifecycle, WMI, cfg80211, IRQ, TX/RX, PM, firmware loading, crash dump, eDMA WMI, P2P, HALP, debugfs, and platform calls.

## Control Flow
The header does not implement a top-level flow, but it defines the call graph contracts. Probe/configuration code initializes `struct wil6210_priv`, selects legacy or enhanced DMA by installing `wil_txrx_ops`, configures WMI/IRQ/NAPI, then TX/RX code uses the shared rings and VIF/station arrays. WMI helpers configure firmware rings and peer state. PM code uses status bits and idle checks. Crash-dump code uses `fw_mapping`, `mem_lock`, `csr`, and register mapping helpers to copy firmware memory.

## State and Persistence Behavior
`struct wil6210_priv` is the persistent in-memory driver object for a device lifetime. It holds PCI/cfg80211/netdev handles, firmware/hardware identity, capabilities, recovery state, VIFs, WMI mailbox state, workqueues, NAPI instances, DMA rings, status rings, station state, platform hooks, PM state, crash/assert addresses, and eDMA feature flags. Per-VIF and per-station state persists across data-path calls until disconnect/reset. Nothing here persists to disk, but many fields mirror firmware/device state and must be reset consistently during recovery.

## Dependencies and Integration Points
This header integrates Linux PCI, netdev, wireless/cfg80211, IRQ, DMA, workqueue, NAPI, debugfs, firmware, WMI, and platform abstractions. It is included by nearly every driver source file. The platform API comes from `wil_platform.h`; firmware records come from `fw.h`; WMI commands and capabilities come from `wmi.h`.

## Risks
Because this is a central header, changes have high blast radius and can alter ABI with firmware/hardware. Packed hardware structures, register addresses, and constants must remain exact. `struct wil6210_priv` mixes many concurrency domains: mutexes, spinlocks, completions, workqueues, NAPI, and memory access semaphores. Incorrect locking around rings, VIFs, WMI, or platform callbacks can cause races during reset/suspend. Function prototypes for both legacy and eDMA paths must stay consistent with operation-table initialization.

## Test Signals
Important signals include full driver build across debugfs and non-debugfs configs, probe/remove, firmware boot and WMI echo, legacy and eDMA data traffic, multiple VIFs, AP/STA/P2P modes, suspend/resume, firmware recovery, crash dump capture, IRQ moderation, DMA over 32-bit and wider address masks, and consistency of stats/debugfs outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil6210.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_crash_dump.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_crash_dump.c

## Purpose
This file implements firmware crash dump extraction for wil6210. It computes the host-address span covering all firmware mapping sections marked for crash dump, copies those regions from device memory into a contiguous buffer, and publishes the result through Linux `dev_coredumpv()`.

## Important APIs, Types, and Functions
- `wil_fw_get_crash_dump_bounds()` scans `fw_mapping[]` for `crash_dump` sections and returns total dump size plus optional minimum host address.
- `wil_fw_copy_crash_dump()` validates destination size, locks device memory access, rejects suspend/suspended state, copies each crash-dump mapping with `wil_memcpy_fromio_32()`, and unlocks.
- `wil_fw_core_dump()` allocates a vmalloc-backed dump buffer, copies the dump, and transfers ownership to the devcoredump subsystem.

## Control Flow
On firmware crash or recovery, callers invoke `wil_fw_core_dump()` or the lower-level copy API. Bounds are calculated first. Core dump allocation uses `vzalloc()`. Copying takes `wil->mem_lock` for write, checks suspend state, iterates over every `fw_mapping` entry with `crash_dump` set, computes its destination offset relative to the minimum host address, copies from `wil->csr + HOSTADDR(map->host)`, then releases the lock. `dev_coredumpv()` owns and later frees the buffer after successful publication.

## State and Persistence Behavior
The generated dump is transient kernel memory handed to devcoredump; it is not written directly by this file. Source state is the global `fw_mapping[]` table and the device memory window `wil->csr`. The function preserves holes between mapped sections by using a contiguous host-address span, so unmapped gaps remain zero from `vzalloc()` in the core-dump path.

## Dependencies and Integration Points
The file depends on `wil6210.h`, firmware mapping metadata populated elsewhere, `wil_memcpy_fromio_32()`, `HOSTADDR()`, `wil->mem_lock`, status bits for suspend state, and Linux `devcoredump`. Platform recovery code may call the exported copy function through platform callbacks.

## Risks
The first mapping seeds bounds even if it is not marked `crash_dump`, so mapping table ordering and flags matter. Size arithmetic assumes mapping ranges are valid and non-overflowing. Copying during suspend is explicitly blocked, but callers must handle `-EBUSY`. Because destination layout is based on host addresses, consumers need mapping knowledge to interpret sections. Failure to keep `fw_mapping[]` synchronized with hardware versions can omit important crash regions or read invalid memory.

## Test Signals
Trigger firmware crash recovery and verify a devcoredump appears with expected size and non-zero mapped sections. Test low-memory allocation failure, too-small destination buffers via `wil_fw_copy_crash_dump()`, suspend-in-progress rejection, and hardware variants with different `fw_mapping[]` tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_crash_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_platform.c

## Purpose
This file provides the default no-op platform integration implementation for wil6210. It allows the core driver to build and run when no platform-specific module supplies power, bus, suspend, recovery, or capability hooks.

## Important APIs, Types, and Functions
- `wil_platform_modinit()` returns success without doing work.
- `wil_platform_modexit()` is empty.
- `wil_platform_init()` validates the caller-provided `struct wil_platform_ops *`, logs an error on NULL, and returns a non-NULL placeholder handle based on the ops pointer.

## Control Flow
Module initialization succeeds unconditionally. During device initialization, the core driver calls `wil_platform_init()` with a device, operations table, optional reverse callbacks, and a wil handle. The default implementation only checks that `ops` is non-NULL and otherwise returns it as an opaque handle. No callbacks are filled and no platform-specific setup occurs.

## State and Persistence Behavior
There is no persistent private state. The returned handle is only a placeholder to satisfy callers that expect a non-NULL platform handle. The provided ops table is not modified by this implementation.

## Dependencies and Integration Points
The file depends on Linux `struct device` logging and declarations from `wil_platform.h`. It is a weak/default integration point for platform-specific code that may be replaced or extended in other builds.

## Risks
Callers must treat platform operations as optional and check function pointers before use, because this implementation does not populate them. Returning the ops pointer as a handle is safe only while callers understand it is not an owned allocation. Missing platform features such as bus bandwidth voting or external clock control may affect power/performance on systems that require them.

## Test Signals
Build and probe on a system without platform hooks should succeed. Passing NULL ops should fail with a device error. Suspend/resume, bus request, and crash recovery flows should verify they correctly handle absent platform callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_platform.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_platform.h

## Purpose
This header defines the wil6210 platform abstraction. It lets the driver notify or request services from board/platform code and lets platform code call back into the driver for ramdump and firmware recovery.

## Important APIs, Types, and Functions
- `enum wil_platform_event` enumerates lifecycle notifications: firmware crash, pre-reset, firmware ready, pre-suspend, and post-suspend.
- `enum wil_platform_features` identifies platform-controlled features such as external firmware clock control and triple MSI.
- `enum wil_platform_capa` defines platform capabilities stored in `wil->platform_capa`, including radio-on suspend, T power-on 0, and external clock capability.
- `struct wil_platform_ops` contains platform callbacks for bus bandwidth requests, suspend/resume, uninitialization, event notification, capability retrieval, and feature setting.
- `struct wil_platform_rops` contains reverse callbacks from platform code into wil6210 for ramdump and firmware recovery.
- `wil_platform_init()`, `wil_platform_modinit()`, and `wil_platform_modexit()` are the public lifecycle APIs.

## Control Flow
The core driver initializes platform support by passing an ops table and optional reverse ops to `wil_platform_init()`. Platform code can fill ops and store reverse callbacks. Later driver lifecycle points can call `notify()`, `suspend()`, `resume()`, `bus_request()`, or feature/capability functions if present. Platform code can invoke `ramdump()` or `fw_recovery()` through the reverse ops when coordinating broader subsystem recovery.

## State and Persistence Behavior
The header defines callback contracts only. Runtime state lives in the platform implementation and in `wil6210_priv.platform_handle`, `platform_ops`, `platform_capa`, and `keep_radio_on_during_sleep`. Capabilities and features are in-memory policy state for the device lifetime.

## Dependencies and Integration Points
It forward-declares `struct device` and uses fixed-width integer and boolean types supplied by kernel includes in users. It integrates with PM, firmware recovery, crash dump, bus scaling, MSI setup, and clock/power policy in the main driver.

## Risks
Callback ownership and lifetime must be clear: the platform may copy reverse ops, and the returned handle must remain valid until uninit. Callers must check optional function pointers. Capability/feature enum ordering is part of the in-driver contract, so mismatches between platform code and driver can enable wrong power or interrupt behavior.

## Test Signals
Test with no platform implementation and with a populated platform implementation. Validate event ordering around firmware ready, crash, reset, suspend, and resume; bus bandwidth votes under traffic; capability bits reflected in driver policy; and ramdump/recovery callbacks during firmware crash handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wil_platform.h -->
