# subset-b-004401 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sge.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sge.c

## Purpose
Implements the Chelsio T4/T5/T6 Scatter Gather Engine data path for the `cxgb4` Ethernet driver. It owns Tx/Rx descriptor rings, free-list refill, NAPI response processing, firmware work request construction, DMA mapping and reclamation, interrupt handling, queue allocation/free, PTP timestamp paths, Ethernet offload queues, control queues, and upper-layer offload Tx queues.

## Important APIs, Types, and Functions
The public/exported entry points include `t4_start_xmit`, `t4_sge_init`, `t4_sge_start`, `t4_sge_stop`, `t4_sge_alloc_rxq`, `t4_sge_alloc_eth_txq`, `t4_sge_alloc_ctrl_txq`, `t4_sge_mod_ctrl_txq`, `t4_sge_alloc_uld_txq`, `t4_sge_alloc_ethofld_txq`, `t4_sge_free_ethofld_txq`, `t4_free_sge_resources`, `free_rspq_fl`, `free_txq`, `t4_intr_handler`, `t4_sge_intr_msix`, `t4_sge_eth_txq_egress_update`, `t4_ofld_send`, `cxgb4_ofld_send`, `cxgb4_immdata_send`, `cxgb4_crypto_send`, `t4_mgmt_tx`, `cxgb4_ethofld_send_flowc`, `cxgb4_ethofld_rx_handler`, `cxgb4_pktgl_to_skb`, `cxgb4_map_skb`, `cxgb4_write_sgl`, `cxgb4_write_partial_sgl`, `cxgb4_inline_tx_skb`, `cxgb4_ring_tx_db`, and `cxgb4_selftest_lb_pkt`.

The main state types are declared in `cxgb4.h`: `struct sge`, `sge_txq`, `sge_eth_txq`, `sge_ctrl_txq`, `sge_uld_txq`, `sge_rspq`, `sge_fl`, `sge_eth_rxq`, `sge_eohw_txq`, and `sge_eosw_txq`. This file also defines `struct rx_sw_desc` for per-FL software state, constants for Rx buffer layout, Tx/Rx reclaim and refill limits, immediate-data thresholds, and timer periods.

## Control Flow
Tx starts at `t4_start_xmit`, which routes packets to VF-style Ethernet Tx, Ethernet offload Tx, PTP-protected Tx, or normal Ethernet Tx. `cxgb4_eth_xmit` validates packet length, handles IPsec/TLS ULD detours, selects the queue, reclaims completed descriptors, computes WR flits/descriptors, maps skb data when not immediate, builds FW/CPL headers for normal packets, TCP TSO, UDP GSO, tunneled LSO, VLAN insertion, checksumming, FCoE, and PTP, advances producer state, and rings the doorbell. `cxgb4_vf_eth_xmit` follows the same descriptor accounting model but emits `FW_ETH_TX_PKT_VM_WR`. Offload and crypto sends are queued through `uld_send`, `ofld_xmit`, and `service_ofldq`; control WRs go through `ctrl_xmit` and `restart_ctrlq`. Ethernet offload queues use a software queue (`sge_eosw_txq`) plus hardware queue (`sge_eohw_txq`) with FLOWC open/close state transitions and completion-driven credit return.

Rx starts when an interrupt schedules NAPI. `napi_rx_handler` calls `process_responses`, which checks response generation bits, distinguishes free-list packet buffers, direct CPLs, and async messages, builds a `pkt_gl` over current FL pages, synchronizes the last DMA buffer for CPU access, dispatches to the response handler, advances the response queue, and refills FL entries. Ethernet packets are handled by `t4_ethrx_handler`, which also recognizes TX egress updates, trace packets, compressed T6 error vectors, loopback self-test frames, GRO-eligible packets, PTP Rx/Tx loopback timestamp packets, VLAN tags, hash values, and checksum state before handing skbs to GRO or `netif_receive_skb`.

Queue lifecycle flows through allocation helpers which allocate coherent descriptor rings and software descriptors, issue firmware IQ/EQ allocation mailbox commands, populate reverse ingress/egress maps, initialize BAR2 doorbell/GTS addresses, add NAPI, and refill free lists. Free paths stop/free firmware queues, purge pending skbs, unmap/free DMA buffers, delete NAPI, kill tasklets, clear reverse maps, and release MSI-X bitmap slots.

## State and Persistence Behavior
Persistent driver state lives in `adapter->sge`, queue descriptors, software descriptor arrays, firmware/hardware queue contexts, status pages, reverse `ingr_map`/`egr_map`, bitmaps such as `starving_fl` and `txq_maperr`, and queue counters. Descriptor rings and status pages are DMA-coherent memory; skb payload pages are mapped/unmapped explicitly. Doorbell state includes producer/consumer indexes, BAR2 queue IDs, T4 doorbell recovery fields, and pending FL credits. Timers persist across device start until `t4_sge_stop`; tasklets persist per suspended queue. No filesystem persistence exists.

## Dependencies and Integration Points
Depends on Linux networking (`sk_buff`, `net_device`, NAPI, GRO, VLAN, XFRM, TLS hooks, PTP, busy poll), DMA mapping APIs, timers/tasklets/spinlocks, Chelsio firmware commands (`t4fw_api.h`), CPL formats (`t4_msg.h`), registers (`t4_regs.h`), chip helpers (`t4_chip_type.h` via `cxgb4.h`), PTP helpers, ULD glue, traffic-class/mqprio support, and scheduler/offload headers. It is wired into `cxgb4_main.c` via netdev `ndo_start_xmit`, firmware event/control queues, queue allocation during adapter bring-up, interrupt handler selection, and adapter teardown. It integrates with `t4_hw.c` for mailbox/register/BAR2/context operations and with ULD modules for TOE/RDMA/iSCSI/crypto/TLS/IPsec data paths.

## Risks
High-risk areas are descriptor accounting around ring wrap, DMA mapping unwind, skb lifetime ownership, queue stop/wake thresholds, firmware WR length calculations, endian conversions in CPL/FW fields, BAR2 vs legacy doorbells, T4/T5/T6 chip-version branches, NAPI budget/rearm logic, FL starvation recovery, PTP single-skb serialization, and ETHOFLD state/credit transitions. Memory pressure paths are subtle because packet buffers can be restored unmapped, FLs can starve, and Tx map errors rely on timers/tasklets to retry. Queue allocation error unwind must match firmware and DMA resources precisely.

## Test Signals
Useful signals include successful probe/remove/reset with all queue types, `ndo_start_xmit` traffic for normal, VLAN, checksum, TSO, UDP GSO, VXLAN/Geneve tunnel offload, VF Tx, PTP timestamp, and FCoE builds; NAPI Rx with GRO and non-GRO packets; checksum and RXHASH validation; loopback self-test completion; ethtool interrupt coalescing and queue stats; forced DMA mapping failures; low-memory FL refill recovery; Tx queue stop/wake under saturation; MSI-X/MSI/INTx interrupt modes; ULD send paths; ETHOFLD FLOWC open/close completion; and teardown under in-flight traffic without leaks or use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/sge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/smt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/smt.c

## Purpose
Implements Source MAC Table allocation, reference counting, firmware programming, and reply handling for Chelsio switch/filter source-MAC entries.

## Important APIs, Types, and Functions
Exports `t4_init_smt`, `cxgb4_smt_alloc_switching`, `cxgb4_smt_release`, and `do_smt_write_rpl`. Internal helpers are `find_or_alloc_smte`, `t4_smte_free`, `write_smt_entry`, and `t4_smt_alloc_switching`. The runtime data model is `struct smt_data` plus per-entry `struct smt_entry` from `smt.h`.

## Control Flow
`t4_init_smt` allocates a flex-array SMT table with `SMT_SIZE` entries, initializes the table rwlock, per-entry spinlocks, indexes, states, source MACs, and refcounts. Allocation takes the table write lock, scans for an existing switching entry with the same source MAC or the first free entry, locks the selected entry, initializes it if the refcount was zero, copies the MAC, records `pfvf`, writes the entry to firmware, or increments the refcount for reuse. Release decrements the refcount under the entry lock and returns the entry to `SMT_STATE_UNUSED` when it reaches zero.

`write_smt_entry` builds a CPL SMT write request and sends it through `t4_mgmt_tx`. T4/T5 hardware programs pairs of source MACs per row, so the request carries both the target entry and its neighbor. T6 uses a distinct request shape and one entry per row. `do_smt_write_rpl` handles firmware replies and marks an entry `SMT_STATE_ERROR` on unexpected status.

## State and Persistence Behavior
State is in memory under `adapter->smt` and in the adapter firmware/hardware SMT after successful management Tx. The driver keeps refcounts and entry states locally; firmware reply errors only mark local state as error and log. Table memory is freed by the adapter teardown path, not in this file.

## Dependencies and Integration Points
Depends on `cxgb4.h` for adapter/netdev conversion and management Tx, `smt.h` for table types, `t4_msg.h` CPL formats, `t4fw_api.h`, `t4_regs.h`, and `t4_values.h`. `cxgb4_filter.c` allocates/releases SMT entries for filters with source-MAC rewriting, `cxgb4_main.c` initializes/frees `adapter->smt` and dispatches `CPL_SMT_WRITE_RPL` to `do_smt_write_rpl`, and `t4_hw.c` has related VI MAC/SMT index handling.

## Risks
Risks include table exhaustion returning `NULL`, failed `alloc_skb` leaving caller with no programmed entry, no immediate propagation of `write_smt_entry` failure to allocation state, refcount imbalance from filter error paths, pair-row programming on T4/T5 accidentally using stale neighbor MACs, and races if callers use entry fields without holding locks.

## Test Signals
Exercise filters requiring source-MAC rewrite, duplicate filters sharing the same SMAC, add/delete reference balance, table exhaustion, T4/T5 paired row behavior, T6 single-entry writes, firmware SMT write errors, and teardown with active filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/smt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/smt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/smt.h

## Purpose
Declares the Chelsio Source MAC Table state model and public SMT APIs used by filter and firmware-event code.

## Important APIs, Types, and Functions
Defines SMT states `SMT_STATE_SWITCHING`, `SMT_STATE_UNUSED`, and `SMT_STATE_ERROR`, fixed `SMT_SIZE` of 256, `struct smt_entry`, and `struct smt_data`. Declares `t4_init_smt`, `cxgb4_smt_alloc_switching`, `cxgb4_smt_release`, and `do_smt_write_rpl`.

## Control Flow
The header has no runtime control flow. Its declarations establish the locking/state contract: the table has a global rwlock and each entry has its own spinlock protecting state, source MAC, and refcount updates.

## State and Persistence Behavior
`struct smt_entry` persists a hardware table index, source MAC, PF/VF selector, state, refcount, and lock. `struct smt_data` persists the table size and flexible array. Hardware persistence is handled by the implementation's CPL write path.

## Dependencies and Integration Points
Includes Linux spinlock, Ethernet address, and atomic headers and forward-declares `struct adapter` and `struct cpl_smt_write_rpl`. Included by `smt.c`, filter code, and main firmware reply dispatch.

## Risks
The fixed table size and state enum are hardware ABI assumptions. Refcount is a plain `int` protected by locks; users must obey the locking contract. Any layout changes affect allocation and teardown paths that use `kvzalloc_flex`/`kvfree`.

## Test Signals
Compile coverage with filter code enabled, add/delete filter tests that call allocation and release, and firmware reply dispatch tests for `CPL_SMT_WRITE_RPL` all validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/smt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/srq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/srq.c

## Purpose
Implements minimal Shared Receive Queue table support for Chelsio T6-class resources: allocation of driver SRQ bookkeeping and parsing of firmware SRQ table read replies.

## Important APIs, Types, and Functions
Exports `t4_init_srq` and `do_srq_table_rpl`. The relevant types are `struct srq_data` and `struct srq_entry` from `srq.h`; reply field extraction uses `struct cpl_srq_table_rpl` and `SRQT_*` macros from `t4_msg.h`.

## Control Flow
`t4_init_srq` allocates `struct srq_data`, records the firmware-reported table size, initializes the completion used by synchronous readers, and initializes the mutex. `do_srq_table_rpl` derives the table index from the reply TID, validates that the status is `CPL_CONTAINS_READ_RPL`, and on success copies decoded valid/index/PDID/queue-length/qbase/current-MSN/max-MSN values into `s->entryp`; it always completes the waiting operation before returning.

## State and Persistence Behavior
The persistent driver object is `adapter->srq`, with `srq_size`, a caller-provided `entryp` destination pointer, one completion, and one mutex. This file does not allocate the destination `srq_entry`; a reader must set `entryp` before issuing the firmware read. Hardware SRQ state remains in firmware; this module snapshots one reply into memory.

## Dependencies and Integration Points
Depends on `cxgb4.h`, `t4_msg.h`, and `srq.h`. `cxgb4_main.c` discovers SRQ resource ranges using firmware parameters, initializes `adapter->srq`, dispatches `CPL_SRQ_TABLE_RPL` to this file, and frees the SRQ data during adapter teardown. Upper-layer RDMA/offload diagnostics can use the completion and parsed entry to inspect SRQ table state.

## Risks
Risks include `adapter->srq` or `s->entryp` being unset when a reply arrives, only one outstanding SRQ table read being representable due to the single completion and entry pointer, truncation from narrow fields in `struct srq_entry`, and callers timing out if firmware replies are lost or dispatched incorrectly. Error replies complete without marking a valid entry, so readers must check `valid`.

## Test Signals
Signals include firmware parameter discovery of SRQ_START/SRQ_END, successful SRQ table read with completion before `SRQ_WAIT_TO`, invalid-status reply logging, concurrent-reader exclusion by the mutex, and teardown with no pending completion users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/srq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/srq.h

## Purpose
Declares the Chelsio SRQ table snapshot structures and firmware reply interface.

## Important APIs, Types, and Functions
Defines `SRQ_WAIT_TO` as a five-second timeout, `struct srq_entry` with valid/index/PDID/queue length/current MSN/max MSN/qbase fields, and `struct srq_data` with table size, destination entry pointer, completion, and mutex. Declares `t4_init_srq` and `do_srq_table_rpl`.

## Control Flow
No runtime control flow is present. The header encodes the synchronization model used by implementation and callers: serialize access with `srq_data.lock`, point `entryp` at caller storage, wait on `comp`, and check `entry.valid`.

## State and Persistence Behavior
The header's state is an in-memory snapshot of firmware SRQ table contents. It is not durable and does not own hardware resources; it mirrors values returned in `CPL_SRQ_TABLE_RPL`.

## Dependencies and Integration Points
Forward-declares `struct adapter` and `struct cpl_srq_table_rpl`. Included by `srq.c` and main adapter code that initializes/frees `adapter->srq` and dispatches replies.

## Risks
The structure fields are narrower than some extracted macro widths could imply, especially `idx`, `qlen`, and `pdid`; this should match expected firmware ranges. The single `entryp` pointer means callers must prevent overlapping reads.

## Test Signals
Build coverage with SRQ-enabled firmware paths, SRQ table read timeout handling, successful reply parsing, and lockdep coverage around the mutex/completion contract are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/srq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_chip_type.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_chip_type.h

## Purpose
Defines the compact chip-version/revision encoding used throughout the Chelsio T4/T5/T6 driver and provides helpers for chip family tests.

## Important APIs, Types, and Functions
Defines PCI device-ID version extraction with `CHELSIO_PCI_ID_VER`, family constants `CHELSIO_T4`, `CHELSIO_T5`, `CHELSIO_T6`, encoding/decoding macros `CHELSIO_CHIP_CODE`, `CHELSIO_CHIP_VERSION`, and `CHELSIO_CHIP_RELEASE`, enum values for `T4_A1`, `T4_A2`, `T5_A0`, `T5_A1`, `T6_A0`, first/last revision markers, and inline predicates `is_t4`, `is_t5`, and `is_t6`.

## Control Flow
Runtime logic is limited to inline family checks that compare `CHELSIO_CHIP_VERSION(chip)` against the family constants. All other behavior is compile-time macro expansion.

## State and Persistence Behavior
No mutable state exists. The encoded `enum chip_type` value is stored in adapter parameter structures elsewhere and acts as a stable hardware capability key across initialization, queue programming, register access, firmware selection, and debug collection.

## Dependencies and Integration Points
Included by `cxgb4.h`, which exposes `adapter->params.chip` to the whole driver. The predicates and version macro are used heavily in `sge.c`, `smt.c`, `cxgb4_main.c`, `t4_hw.c`, filter code, ethtool, debug collection, and ULD setup to select T4/T5/T6-specific register fields, WR formats, queue behavior, and feature availability.

## Risks
Incorrect encoding or PCI version extraction would misclassify hardware and select wrong firmware/register formats. Adding a new chip family requires updating constants, enum ranges, helper assumptions, firmware lookup, and every switch statement that treats unknown versions as errors. The helpers test only family, not revision-specific errata.

## Test Signals
Probe tests across T4/T5/T6 PCI IDs, firmware image selection, queue allocation on each family, debug register dump paths, and compile-time users of `is_t4`/`is_t5`/`is_t6` are the core validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_chip_type.h -->
