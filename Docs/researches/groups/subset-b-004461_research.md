# Research Group: subset-b-004461

This grouped report covers the Intel i40e transmit/receive implementation and hardware type contracts assigned to `subset-b-004461`. Each section preserves the source path and is wrapped with the reconciliation sentinels required for source-tree-aligned split output.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx.c -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx.c

## Purpose

`i40e_txrx.c` is the main packet I/O implementation for the Intel i40e Ethernet driver. It owns Flow Director filter programming, Tx descriptor construction and reclamation, Rx descriptor refill and packet assembly, NAPI polling, adaptive interrupt moderation, XDP transmit/redirect/drop handling, checksum/VLAN/hash metadata processing, Tx timestamp setup, queue selection for software DCB, and recovery hooks for stalled transmit queues.

## Important APIs, Types, and Functions

The exported driver entry points include `i40e_add_del_fdir()`, `i40e_clean_tx_ring()`, `i40e_free_tx_resources()`, `i40e_get_tx_pending()`, `i40e_detect_recover_hung()`, `i40e_force_wb()`, `i40e_setup_tx_descriptors()`, `i40e_clean_rx_ring()`, `i40e_free_rx_resources()`, `i40e_setup_rx_descriptors()`, `i40e_release_rx_desc()`, `i40e_alloc_rx_buffers()`, `i40e_clean_programming_status()`, `i40e_process_skb_fields()`, `i40e_xmit_xdp_tx_ring()`, `i40e_xdp_ring_update_tail()`, `i40e_update_rx_stats()`, `i40e_finalize_xdp_rx()`, `i40e_is_non_eop()`, `i40e_napi_poll()`, `__i40e_maybe_stop_tx()`, `__i40e_chk_linearize()`, `i40e_lan_select_queue()`, `i40e_lan_xmit_frame()`, and `i40e_xdp_xmit()`.

Important internal helpers include the Flow Director path (`i40e_fdir()`, `i40e_program_fdir_filter()`, dummy packet constructors for UDP/TCP/SCTP/IP, and `i40e_fd_handle_status()`), Tx cleanup and mapping helpers (`i40e_unmap_and_free_tx_resource()`, `i40e_clean_tx_irq()`, `i40e_tso()`, `i40e_tsyn()`, `i40e_tx_enable_csum()`, `i40e_create_tx_ctx()`, `i40e_tx_map()`, and `i40e_atr()`), Rx page lifecycle helpers (`i40e_reuse_rx_page()`, `i40e_alloc_mapped_page()`, `i40e_get_rx_buffer()`, `i40e_put_rx_buffer()`, `i40e_can_reuse_rx_page()`, `i40e_rx_buffer_flip()`), skb construction helpers (`i40e_construct_skb()`, `i40e_build_skb()`, `i40e_cleanup_headers()`), and XDP helpers (`i40e_run_xdp()`, `i40e_add_xdp_frag()`, `i40e_consume_xdp_buff()`, `i40e_xmit_xdp_ring()`).

## Control Flow

Flow Director sideband filter programming starts in `i40e_add_del_fdir()`, which switches on ethtool flow type and protocol. Protocol-specific helpers allocate a raw dummy packet, fill Ethernet/IP/L4 fields, optionally place a flexible payload word, assign the correct packet classification type, and call `i40e_program_fdir_filter()`. The programming path finds the FDIR VSI, waits for at least two descriptors, DMA maps the dummy packet, writes a filter programming descriptor plus a dummy data descriptor, sets `next_to_watch`, and rings the Tx tail. Programming completion returns as a special Rx programming status descriptor. `i40e_clean_programming_status()` decodes the status and `i40e_fd_handle_status()` updates PF Flow Director error, invalidation, ATR auto-disable, and sideband auto-disable state when table-full or no-entry errors appear.

Tx queue setup allocates `struct i40e_tx_buffer` entries and a DMA-coherent descriptor ring with an extra head-writeback slot. Normal transmit starts at `i40e_lan_xmit_frame()`, pads very short frames, and calls `i40e_xmit_frame_ring()`. That function computes descriptor demand, linearizes when hardware scatter-gather limits require it, may stop the netdev subqueue when ring space is low, records the first Tx buffer, prepares VLAN/DCB flags, creates TSO and timestamp context bits, enables checksum/tunnel offload, writes an optional context descriptor, samples ATR Flow Director descriptors, and finally maps skb head/frags in `i40e_tx_map()`. `i40e_tx_map()` splits large DMA segments along hardware limits, writes descriptors, sets EOP and periodic RS, publishes `next_to_watch` behind a write barrier, and updates the hardware tail unless xmit-more batching allows deferral. Completion is reclaimed in `i40e_clean_tx_irq()`, which walks from `next_to_clean` until descriptors catch the hardware head or budget expires, unmaps DMA, consumes skb or XDP frames, updates stats, arms writeback-on-ITR when needed, and wakes the subqueue once descriptors recover past the wake threshold.

Rx queue setup allocates a DMA-coherent descriptor ring and a buffer-info array, caches the VSI XDP program, and initializes ring indices. Refill is done by `i40e_alloc_rx_buffers()`, which allocates or reuses pages, maps them with `I40E_RX_DMA_ATTR`, syncs for device access, refreshes packet addresses in descriptors, clears the next status field, and releases the new tail with `i40e_release_rx_desc()`. `i40e_clean_rx_irq()` is the main receive loop. It batches refills, reads descriptor status after `dma_rmb()`, handles programming status descriptors specially, gets the Rx buffer and syncs it for CPU access, tracks multi-buffer packets with `next_to_process`, builds an `xdp_buff`, appends page fragments when needed, runs XDP, and either consumes/transmits/redirects the packet or builds an skb. Stack-bound packets pass through header cleanup, checksum/hash/VLAN/timestamp metadata population, and `napi_gro_receive()`. At the end of the batch, XDP redirects are flushed, XDP Tx tails are written, Rx stats are updated, and allocation failures force another poll pass.

`i40e_napi_poll()` coordinates both sides for one interrupt vector. It cleans every Tx ring, handles zero-budget netpoll calls, divides Rx budget across ring pairs, calls either normal or AF_XDP zero-copy Rx/Tx cleanup, checks interrupt affinity to avoid being pinned on the wrong CPU, optionally arms writeback-on-ITR, completes NAPI, and updates or re-enables interrupts through adaptive ITR logic. `i40e_update_itr()` computes a target interrupt interval from packet count, byte count, link speed, and latency/bulk mode, while `i40e_update_enable_itr()` lazily chooses whether to program Rx or Tx ITR and handles busy-poll software interrupts.

## State and Persistence Behavior

The file manages in-memory driver state tied to ring, VSI, and PF lifetimes. Ring indices (`next_to_use`, `next_to_clean`, `next_to_process`, `next_to_alloc`), descriptor memory, DMA mappings, page reference bias, XDP frame state, Tx `next_to_watch`, queue stats, adaptive ITR counters, Flow Director counters, and PTP Tx state are updated continuously. No on-disk state is written. Hardware-visible persistence occurs through DMA descriptors, tail registers, interrupt control registers, PF state bits, and Flow Director filter programming; teardown paths must unmap and drain all resources because hardware may still have references until queues are stopped.

## Dependencies and Integration Points

The implementation depends on Linux netdev/NAPI/skbuff/GRO/XDP APIs, DMA mapping APIs, BPF/XDP redirect helpers, PTP timestamp support, VLAN/MPLS/SCTP/IP header helpers, libie/libeth packet type parsing, i40e register definitions, AF_XDP helpers from `i40e_xsk.h`, tracepoints from `i40e_trace.h`, and ring/type definitions from `i40e_txrx.h`, `i40e_txrx_common.h`, and `i40e_type.h`. It integrates with ethtool ntuple/Flow Director configuration, ndo_start_xmit, ndo_select_queue, ndo_xdp_xmit, interrupt vector setup, queue resource setup/free, PF reset and hang recovery, and hardware feature flags discovered elsewhere in the driver.

## Risks and Edge Cases

High-risk areas are DMA ordering and ownership transitions: descriptor fields are read only after barriers, descriptor publication uses write barriers before tail writes, and DMA sync/unmap calls must match whether pages are reused or freed. Multi-buffer Rx packets and XDP fragments depend on `next_to_process`, `next_to_clean`, and page bias staying consistent; overflow over `MAX_SKB_FRAGS` drops all buffers. Tx mapping rollback is sensitive to ring wraparound. Flow Director dummy packets are freed by Tx completion on success but must be freed immediately on programming failure. Sideband TCP rules can auto-disable ATR, and table-full status can suppress future sideband rules. Tx timestamping supports only one outstanding timestamped skb and must clear `__I40E_PTP_TX_IN_PROGRESS` on drop paths. Queue-stop/wake logic depends on memory barriers around descriptor availability. Adaptive ITR can misbehave if stats are not reset after programming. The code also has hardware-specific limits such as a maximum of eight DMA buffers per packet, 16K descriptor segment limits, short-frame padding, and link-speed-sensitive ITR scaling.

## Test Signals

Useful validation signals include successful probe and queue setup/free under normal and XDP-enabled configurations, Tx/Rx traffic with checksum, VLAN, TSO, tunneled TSO, SCTP, and MPLS cases, GRO receive without checksum regressions, ethtool ntuple add/delete with Flow Director status descriptors, table-full Flow Director behavior, NAPI completion and interrupt re-enable under low and high traffic, AF_XDP zero-copy cleanup paths, XDP_PASS/XDP_DROP/XDP_TX/XDP_REDIRECT including fragmented frames, Tx queue stop/wake recovery under ring pressure, forced writeback for hung queues, PTP Tx timestamp success and skipped-count behavior, and DMA mapping failure injection for Tx and Rx allocation rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx.h

## Purpose

`i40e_txrx.h` is the main transmit/receive contract for the i40e driver. It defines interrupt moderation constants, RSS defaults, Rx buffer sizing and padding rules, ring data structures, Tx/Rx buffer metadata, queue statistics, ring state flags, descriptor arithmetic helpers, and prototypes for the packet I/O functions implemented in `i40e_txrx.c` and related common/XDP files.

## Important APIs, Types, and Macros

Interrupt moderation definitions include `I40E_ITR_DYNAMIC`, `I40E_ITR_MASK`, `I40E_MIN_ITR`, `I40E_ITR_20K`, `I40E_ITR_8K`, `I40E_MAX_ITR`, `ITR_TO_REG()`, `ITR_REG_ALIGN()`, `ITR_IS_DYNAMIC()`, default Rx/Tx ITR settings, interrupt rate-limit enable bits, and `i40e_intrl_usec_to_reg()`. `enum i40e_dyn_idx` maps hardware ITR indices for Rx, Tx, software, and `I40E_ITR_NONE`.

RSS defaults are captured by `I40E_DEFAULT_RSS_HASHCFG`, `I40E_DEFAULT_RSS_HASHCFG_EXPANDED`, and `i40e_pf_get_default_rss_hashcfg()`, which selects expanded UDP/TCP ptypes when hardware advertises `I40E_HW_CAP_MULTI_TCP_UDP_RSS_PCTYPE`. Rx buffer definitions include `I40E_RXBUFFER_256`, `I40E_RXBUFFER_1536`, `I40E_RXBUFFER_2048`, `I40E_RXBUFFER_3072`, `I40E_MAX_RXBUFFER`, `I40E_RX_HDR_SIZE`, `I40E_PACKET_HDR_PAD`, `I40E_RX_DMA_ATTR`, `i40e_compute_pad()`, `i40e_skb_pad()`, `I40E_SKB_PAD`, and page order helpers. Tx descriptor sizing and flags include `I40E_MAX_BUFFER_TXD`, `I40E_MIN_TX_LEN`, maximum per-descriptor data macros, `i40e_txd_use_count()`, `DESC_NEEDED`, and `I40E_TX_FLAGS_*` bits for VLAN, TSO, IP version, timestamp, Flow Director, and tunnel handling.

The central type is `struct i40e_ring`. It holds descriptor memory, DMA address, device/netdev pointers, XDP program, Tx/Rx buffer arrays or AF_XDP buffer pointers, state bits, queue index, DCB traffic class, tail register, persistent `xdp_buff`, ring cursors, ITR settings, descriptor count, register index, Rx buffer length, XDP Tx activity, ATR sampling state, flags, stats, VSI/q_vector back references, RCU head, channel, Rx offset, XDP Rx queue info, and AF_XDP pool. `struct i40e_tx_buffer` tracks skb/XDP/raw Flow Director packet ownership, DMA mapping, byte count, GSO segments, `next_to_watch`, and flags. `struct i40e_rx_buffer` tracks page, DMA address, page offset, page reference bias, and cached page count. Ring helper APIs include build-skb and XDP flag accessors, `i40e_test_staterr()`, `I40E_RX_NEXT_DESC()`, `i40e_get_head()`, `i40e_xmit_descriptor_count()`, `i40e_maybe_stop_tx()`, `i40e_chk_linearize()`, and `txring_txq()`.

## Control Flow

This header does not implement the full packet path, but its inlines define fast-path decisions used by `i40e_txrx.c`. Tx code uses `i40e_xmit_descriptor_count()` to count descriptor demand across skb head and fragments, `i40e_chk_linearize()` to avoid exceeding hardware buffer limits, `i40e_maybe_stop_tx()` to stop queues only after the cheap descriptor availability check fails, and `txring_txq()` to map an i40e ring back to the netdev queue. Rx code uses `i40e_test_staterr()` for descriptor status/error checks, page order helpers to choose page size, and build-skb flags to select copy versus zero-copy skb construction.

## State and Persistence Behavior

The structures declared here hold the persistent in-memory state of each Tx or Rx queue while the VSI is active. Ring cursors persist across interrupts and NAPI polls. `itr_setting`, `i40e_ring_container` values, and queue stats persist until queue teardown or reset. Buffer arrays persist DMA and page ownership until cleanup. XDP fields persist the current program and partially built multi-buffer packet across poll iterations. No persistent storage is used; persistence is limited to driver memory and hardware descriptor/register state.

## Dependencies and Integration Points

The header includes `i40e_type.h`, Linux XDP definitions, and Intel libie pctype definitions. It is included by Tx/Rx implementation files, queue setup code, interrupt/vector code, ethtool statistics paths, XDP/AF_XDP integration, and common Tx/Rx helpers. Its constants must match hardware descriptor formats from `i40e_type.h` and register programming in other i40e modules.

## Risks and Edge Cases

The descriptor arithmetic macros assume valid ring counts and synchronized cursors. `I40E_DESC_UNUSED()` leaves one descriptor unused to distinguish full from empty rings. ITR values are stored in microseconds with a high dynamic flag, so callers must mask before register writes. Padding logic changes by `PAGE_SIZE`; large page systems use different truesize behavior and small page systems rely on page flipping. `i40e_get_head()` reads the head writeback slot placed after the descriptor ring, so Tx ring allocation must reserve and align that extra `u32`. The union in `i40e_tx_buffer` means cleanup must know whether the payload is an skb, XDP frame, or raw Flow Director packet.

## Test Signals

Compilation coverage should catch descriptor layout and prototype drift. Runtime signals include correct queue stop/wake decisions, no underrun of descriptor counts on fragmented and GSO skbs, proper Rx buffer sizing across page sizes, successful XDP program attach/detach with `xdp_rxq_info`, stable per-ring stats under concurrent readers, correct RSS ptype defaults based on capability bits, and no DMA/page leaks when rings are repeatedly setup and freed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx_common.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx_common.h

## Purpose

`i40e_txrx_common.h` is a small shared contract for Tx/Rx helpers used by the normal path, XDP path, and AF_XDP integration. It exposes common receive processing helpers, XDP result bits, Tx descriptor construction, stat updates, writeback-on-ITR arming, programming-status detection, and AF_XDP cleanup/query functions.

## Important APIs, Types, and Macros

The exported prototypes include `i40e_xmit_xdp_tx_ring()`, `i40e_clean_programming_status()`, `i40e_process_skb_fields()`, `i40e_xdp_ring_update_tail()`, `i40e_update_rx_stats()`, `i40e_finalize_xdp_rx()`, `i40e_release_rx_desc()`, `i40e_xsk_clean_rx_ring()`, `i40e_xsk_clean_tx_ring()`, and `i40e_xsk_any_rx_ring_enabled()`. XDP result masks are `I40E_XDP_PASS`, `I40E_XDP_CONSUMED`, `I40E_XDP_TX`, `I40E_XDP_REDIR`, and `I40E_XDP_EXIT`.

`build_ctob()` assembles the data descriptor qword containing descriptor type, command bits, header offset fields, buffer size, and VLAN tag. `i40e_update_tx_stats()` updates per-ring `u64_stats_sync` counters and q_vector aggregate counters. `i40e_arm_wb()` decides whether a Tx ring should request hardware writeback on interrupt throttling when only a small number of descriptors are pending and the queue is still active. `i40e_rx_is_programming_status()` identifies Flow Director or FCoE programming status descriptors by checking the SPH/length bit location reused when packet split is unsupported.

## Control Flow

Normal Tx descriptor creation calls `build_ctob()` for each data descriptor and `i40e_update_tx_stats()` from the Tx cleanup path after descriptors are reclaimed. `i40e_arm_wb()` is called after Tx cleanup to set `tx_ring->arm_wb`, which `i40e_napi_poll()` later converts into a hardware writeback-on-ITR arm operation. Rx polling calls `i40e_rx_is_programming_status()` before treating a descriptor as a packet; programming status descriptors are routed to `i40e_clean_programming_status()` instead of skb/XDP construction. XDP and AF_XDP paths share the declared finalization, tail update, cleanup, and ring-enabled helpers.

## State and Persistence Behavior

The inline helpers mutate ring and vector counters in memory. `i40e_update_tx_stats()` uses `u64_stats_update_begin/end()` for lockless statistic readers and increments q_vector totals that feed interrupt moderation. `i40e_arm_wb()` sets the transient `arm_wb` flag on the ring. `build_ctob()` and `i40e_rx_is_programming_status()` are pure computations over descriptor fields. No on-disk or firmware-persistent state is created here.

## Dependencies and Integration Points

The header includes `i40e.h`, which provides the broader PF/VSI/ring definitions, register masks, and state bits. It is consumed by `i40e_txrx.c` and AF_XDP support code, and its descriptor field positions come from `i40e_type.h`. It also depends on Linux DMA/netdev stat synchronization and hardware writeback behavior for X722 writeback-on-ITR mode.

## Risks and Edge Cases

`build_ctob()` assumes command, offset, size, and tag fields have already been validated for the hardware bit widths. `i40e_update_tx_stats()` assumes `tx_ring->q_vector` is valid when called. `i40e_arm_wb()` only arms writeback when `I40E_TXR_FLAGS_WB_ON_ITR` is set and descriptors are pending; wrong pending calculations can cause delayed completions or excess interrupts. `i40e_rx_is_programming_status()` relies on the packet-split/header-split assumption; enabling packet split semantics would conflict with using the SPH bit as a programming-status signal.

## Test Signals

Useful signals include descriptor qword correctness for VLAN, checksum, TSO, and XDP Tx; per-ring and per-vector Tx stats matching transmitted packets after cleanup; writeback-on-ITR arming only when pending descriptors are below `WB_STRIDE`; Flow Director programming status descriptors being consumed without being delivered as packets; and AF_XDP cleanup functions being linked and exercised when an XSK pool is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_txrx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_type.h -->
# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_type.h

## Purpose

`i40e_type.h` is the core hardware type and descriptor definition header for the i40e driver. It defines device limits, capability bits, link/PHY/MAC/bus/NVM/DCB structures, the central `struct i40e_hw`, Rx and Tx descriptor layouts, descriptor bit fields, Flow Director programming descriptor fields, switch/VSI/VEB context structures, hardware statistics structures, NVM shadow RAM constants, filter control sizes, reset types, RSS/input-set masks, and Dynamic Device Personalization package structures.

## Important APIs, Types, and Macros

Top-level limits include queue-pair, VF VSI, chained Rx buffer, UDP offload port, NVM timeout, and PHY timeout constants. `I40E_DESC_UNUSED()` is the shared ring-space macro used by Tx/Rx code. Hardware identity and link types include `enum i40e_mac_type`, `enum i40e_media_type`, `enum i40e_fc_mode`, `enum i40e_vsi_type`, and `enum i40e_queue_type`. Link and PHY state is represented by `struct i40e_link_status` and `struct i40e_phy_info`, with PHY capability bit macros for SGMII, BASE-KX/KR/CR/SR/LR/T, AOC/ACC, 25G variants with the documented offset, and 2.5G/5G BASE-T.

`struct i40e_hw_capabilities` records firmware-discovered capabilities such as switch mode, management protocols, SR-IOV, VMDQ, EVB, DCB, FCoE, iSCSI, Flex10, security/update restrictions, PTP, Flow Director counts, RSS table sizes, GPIO LED/SDP capabilities, queue/vector counts, DCB traffic classes, and write-protected CSR bits. `enum i40e_hw_flags` maps driver capability bits used by `hw.caps`. `struct i40e_hw` is the main hardware object: it contains MMIO base, PHY/MAC/bus/NVM/FC substructures, PCI IDs, capabilities, Flow Director shared count, PF/main VSI identifiers, partition data, AdminQ state, NVM update state, HMC state, DCBX configs, capability bitmap, switch tags, and debug state.

Descriptor definitions include `union i40e_16byte_rx_desc`, `union i40e_32byte_rx_desc`, `struct i40e_tx_desc`, `struct i40e_tx_context_desc`, and `struct i40e_filter_program_desc`. Associated enums and masks define Rx status bits, filter-status values, error bits, PTYPE, packet length, programming-status fields, Tx descriptor dtype values, Tx command bits, Tx length offset fields, Tx context command/tunnel fields, and Flow Director filter programming destination/status/command/count fields. Other major groups include `struct i40e_vsi_context`, `struct i40e_veb_context`, `struct i40e_eth_stats`, `struct i40e_veb_tc_stats`, `struct i40e_hw_port_stats`, filter control settings, LLDP variables, alternate RAM offsets, RSS/input-set masks, and DDP package/segment/profile section structures.

## Control Flow

This header is declarative, but it controls runtime behavior by defining the exact memory layouts and bit positions used by fast-path and AdminQ code. Rx polling reads `union i40e_rx_desc::wb.qword1.status_error_len` and extracts status, error, packet type, length, timestamp, VLAN, RSS, and programming status fields using these masks. Tx code writes `struct i40e_tx_desc::buffer_addr` and `cmd_type_offset_bsz` using these command/offset/size/tag shifts, writes context descriptors for TSO/timestamp/tunnel offload, and writes filter programming descriptors for Flow Director sideband and ATR rules. Admin/control-plane code stores firmware-reported capabilities in `struct i40e_hw` and interprets NVM, DCBX, switch, filter-control, and DDP structures with these definitions.

## State and Persistence Behavior

The file defines structures that hold both volatile runtime state and cached firmware/hardware state. `struct i40e_hw` persists for the PCI function lifetime and is refreshed across resets and AdminQ operations. NVM update fields persist during multi-step NVM transactions. Link status, capability bitmaps, DCBX configs, HMC state, and firmware counts are in-memory reflections of hardware or firmware state. Descriptor structures are DMA-visible and persist only while queues are active. NVM/shadow RAM constants refer to nonvolatile device storage, but this header only defines offsets and command shapes; actual persistence is performed by AdminQ/NVM code elsewhere.

## Dependencies and Integration Points

The header includes UAPI Ethernet definitions plus `i40e_adminq.h` and `i40e_hmc.h`, and it is included by most i40e modules. It integrates with firmware AdminQ command handling, queue setup, packet I/O fast paths, Flow Director, RSS, DCB, PTP, NVM update, DDP profile loading, switch/VSI/VEB management, and ethtool statistics. The bit definitions must match the Intel X710/XL710/X722 hardware specification and the firmware ABI.

## Risks and Edge Cases

Descriptor layouts and bit masks are ABI-like contracts with hardware; incorrect shifts, widths, endian conversions, or structure assumptions can cause silent packet corruption, lost checksum offloads, wrong RSS hashes, broken Flow Director programming, or DMA into invalid buffers. `I40E_DESC_UNUSED()` assumes producer/consumer indices are maintained with one empty slot. `I40E_CAP_PHY_TYPE_25GBASE_*` uses an explicit offset because bit 31 is unused while the AdminQ enum has no gap; code that maps PHY enum values to capability bits must preserve this exception. Capability bits in `struct i40e_hw::caps` must be populated before feature decisions such as RSS ptype expansion, writeback-on-ITR, FEC, PTP, or DCB. Flexible-array DDP/package structures require bounds checking by consumers. Several stats fields are hardware counter mirrors and can wrap or require delta accounting elsewhere.

## Test Signals

Validation signals include successful compile of all descriptor and AdminQ users, queue setup with correct descriptor sizes, packet Rx metadata extraction for VLAN/RSS/checksum/timestamp, Tx offload correctness for IPv4/IPv6/UDP/TCP/SCTP/TSO/tunnels, Flow Director add/remove/ATR descriptor programming, firmware capability parsing across X710/XL710/X722 devices, DCBX configuration import/export, NVM update command shape validation, DDP package parsing with malformed size tests, and ethtool statistics matching hardware counters after wrap-aware updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_type.h -->
