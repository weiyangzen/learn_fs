# Research: subset-b-004441

This grouped report covers Huawei hinic3 NIC queue/RSS/TX/RX support and legacy Intel 82586/82596 Ethernet drivers under `sources/distributed-fs/ceph-client/drivers/net/ethernet`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_nic_io.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_nic_io.c

## Purpose
`hinic3_nic_io.c` owns the hinic3 NIC data-path queue-pair lifecycle below the netdev TX/RX queues. It allocates per-function NIC I/O state, reserves doorbells and a coherent TX consumer-index table, creates SQ/RQ work queues, attaches them to `hinic3_nic_io`, and programs queue context/root context into firmware through command queues.

## Important APIs, Types, And Functions
- `struct hinic3_sq_ctxt`, `struct hinic3_rq_ctxt`, `struct hinic3_qp_ctxt_hdr`, `struct hinic3_sq_ctxt_block`, `struct hinic3_rq_ctxt_block`, and `struct hinic3_clean_queue_ctxt` describe the firmware queue-context payloads sent to `L2NIC_UCODE_CMD_MODIFY_QUEUE_CTX` and `L2NIC_UCODE_CMD_CLEAN_QUEUE_CTX`.
- `hinic3_init_nic_io()` allocates `struct hinic3_nic_io`, marks NIC service in use, initializes the function table, stores RX buffer length, fetches feature capability, and masks it to supported/default feature bits.
- `hinic3_free_nic_io()` clears the function service-used state and frees the NIC I/O object.
- `hinic3_init_nicio_res()` reads the hardware maximum queue count, allocates SQ/RQ doorbell addresses, and allocates the coherent CI table sized by `HINIC3_CI_TABLE_SIZE(max_qps)`.
- `hinic3_alloc_qps()`/`hinic3_free_qps()` allocate and destroy arrays of `struct hinic3_io_queue` for SQs and RQs, using `hinic3_wq_create()` with SQ/RQ WQEBB sizes.
- `hinic3_init_qps()` publishes the queue arrays into `nic_io`, initializes each SQ CI pointer to a 64-byte CI slot, clears hardware-visible CI, and installs common SQ/RQ doorbell bases.
- `hinic3_init_qp_ctxts()` prepares SQ and RQ context batches, cleans offload context, sets root context, and configures each SQ CI table entry.
- `hinic3_free_qp_ctxts()` cleans the root context.

## Control Flow
Initialization is layered. `hinic3_init_nic_io()` creates software state and enables the NIC service. `hinic3_init_nicio_res()` reserves PCI/device resources shared by all queues. A dynamic queue-parameter caller then invokes `hinic3_alloc_qps()` to allocate SQ/RQ WQs, followed by `hinic3_init_qps()` to publish queues into the live `nic_io`. `hinic3_init_qp_ctxts()` then sends SQ contexts in batches of at most `HINIC3_Q_CTXT_MAX` entries, sends RQ contexts the same way, cleans prior LRO/TSO context, programs the root context, and arms the SQ CI table for every queue.

SQ context preparation reads local PI/CI, records first WQ page PFN and WQ block PFN, enables owner bit, sets VLAN insertion mode, and applies prefetch thresholds. RQ context preparation computes hardware indices shifted for normal RQ WQE format, records MSI-X entry, sets 16-byte WQE/CQE format, and supplies the PI DMA address and WQ block PFNs. Cleanup sends `L2NIC_UCODE_CMD_CLEAN_QUEUE_CTX` for both SQ and RQ queue types.

## State And Persistence Behavior
State is runtime-only. Persistent state is limited to device/firmware contexts and coherent DMA memory while the driver is loaded and interface resources are active. `nic_io->ci_vaddr_base` is a coherent table where hardware updates SQ consumer indices; each queue gets a 64-byte slot. `nic_io->sq`, `nic_io->rq`, `num_qps`, `max_qps`, doorbell bases, `rx_buf_len`, and `feature_cap` are held in memory and released on teardown. Queue owner bits and WQ producer/consumer indices are transient protocol state shared with hardware.

## Dependencies And Integration Points
This file depends on `hinic3_hwdev`, `hinic3_hwif`, `hinic3_hw_comm`, `hinic3_cmdq`, `hinic3_nic_cfg`, `hinic3_nic_dev`, and `hinic3_wq`. It integrates with TX/RX files through `struct hinic3_io_queue` arrays, with firmware through `hinic3_cmdq_direct_resp()`, with device configuration through `hinic3_set_root_ctxt()`, `hinic3_clean_root_ctxt()`, and `hinic3_set_ci_table()`, and with PCI/DMA through doorbell allocation and coherent memory.

## Risks And Edge Cases
- Queue counts are rejected when zero or above `max_qps`, but callers must still keep SQ/RQ depths power-of-two so lower WQ allocation succeeds.
- Firmware command payloads are endian-swabbed before submission; field changes must preserve hardware layout exactly.
- `clean_qp_offload_ctxt()` uses logical OR between two cleanup calls, returning boolean-like failure rather than the first negative errno.
- On `hinic3_init_qp_ctxts()` failure after some CI table entries are set, cleanup is limited to root context cleanup, so callers must sequence broader teardown.
- Hardware-visible CI table slots are cleared on queue initialization; stale coherent memory would affect completion accounting.

## Test Signals
Useful validation signals include successful `hinic3_init_qp_ctxts()` on multi-queue devices, no firmware errors from `MODIFY_QUEUE_CTX`/`CLEAN_QUEUE_CTX`, correct TX completion advancement from the CI table, RX/TX traffic on all queues, queue count boundary tests, and teardown/reopen cycles that leave no leaked doorbells, WQs, or coherent allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_nic_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_nic_io.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_nic_io.h

## Purpose
`hinic3_nic_io.h` defines the public queue and doorbell contract used by the hinic3 NIC data path. It exposes `struct hinic3_io_queue`, `struct hinic3_nic_io`, queue-pair parameter structures, inline SQ index helpers, the doorbell write helper, and lifecycle prototypes implemented by `hinic3_nic_io.c`.

## Important APIs, Types, And Functions
- `HINIC3_SQ_WQEBB_SHIFT`, `HINIC3_RQ_WQEBB_SHIFT`, and `HINIC3_SQ_WQEBB_SIZE` define queue element sizes used by WQ allocation and descriptor programming.
- `enum hinic3_rq_wqe_type` currently exposes `HINIC3_NORMAL_RQ_WQE`.
- `struct hinic3_io_queue` holds a `struct hinic3_wq`, owner bit, queue id, MSI-X entry, doorbell address, and SQ hardware CI pointer.
- `hinic3_get_sq_local_ci()`, `hinic3_get_sq_local_pi()`, and `hinic3_get_sq_hw_ci()` provide masked software/hardware index access.
- `struct hinic3_nic_db` and `hinic3_write_db()` encode and write the 64-bit doorbell.
- `struct hinic3_dyna_qp_params` carries requested queue count/depths and returned SQ/RQ arrays.
- `struct hinic3_nic_io` stores live SQ/RQ arrays, queue counts, coherent CI table, doorbell bases, RX buffer length, and feature capability.

## Control Flow
TX and RX paths obtain a `struct hinic3_io_queue` from `nic_dev->nic_io`. Producers advance the WQ producer index via `hinic3_wq` helpers, then call `hinic3_write_db()` with the queue, COS, SQ/RQ data-path flag, and producer index. TX completion reads `hinic3_get_sq_hw_ci()` from the coherent CI slot and returns WQEBBs using the local CI.

## State And Persistence Behavior
All structures are per-driver runtime state. `cons_idx_addr` points into coherent DMA memory that survives while NIC I/O resources are active. Doorbell MMIO addresses are stored once per SQ/RQ class and shared by queues. `struct hinic3_nic_io` does not persist across device removal or driver unload.

## Dependencies And Integration Points
The header depends on `linux/bitfield.h` and `hinic3_wq.h`. It is consumed by `hinic3_nic_io.c`, `hinic3_tx.c`, `hinic3_rx.c`, and any higher-level NIC device code that allocates/configures queue pairs.

## Risks And Edge Cases
- `hinic3_write_db()` type-puns a local `struct hinic3_nic_db` into a 64-bit write; layout and endianness must remain exactly two 32-bit little-endian words.
- `DB_ADDR()` uses low PI bits to select the doorbell offset, so queue producer indices and MMIO mapping size must match hardware expectations.
- `hinic3_get_sq_hw_ci()` assumes `cons_idx_addr` is initialized and points to coherent memory before TX polling begins.

## Test Signals
Doorbell validation should show packets transmitted and RX buffers replenished after `hinic3_write_db()`. TX completion tests should observe hardware CI movement in the CI table and no false queue-full conditions under wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_nic_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_pci_id_tbl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_pci_id_tbl.h

## Purpose
`hinic3_pci_id_tbl.h` centralizes PCI device IDs for hinic3 physical and virtual functions.

## Important APIs, Types, And Functions
- `PCI_DEV_ID_HINIC3_PF` is `0x0222`.
- `PCI_DEV_ID_HINIC3_VF` is `0x375F`.

## Control Flow
There is no control flow. The constants are intended for PCI device-id tables in probe code elsewhere in the hinic3 driver.

## State And Persistence Behavior
No runtime state is stored. The identifiers are compile-time constants.

## Dependencies And Integration Points
This header has only include guards. It integrates with PCI probe/registration code that matches Huawei hinic3 PF/VF devices.

## Risks And Edge Cases
Incorrect IDs would prevent device binding or bind the driver to unsupported hardware. Any future revision support should be added with explicit compatibility validation.

## Test Signals
Build-time usage in PCI tables and runtime probe logs for PF/VF devices are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_pci_id_tbl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_queue_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_queue_common.c

## Purpose
`hinic3_queue_common.c` implements allocation and freeing of DMA-backed queue pages used by hinic3 work queues. It abstracts queues as an array of aligned coherent pages with element/page geometry recorded in `struct hinic3_queue_pages`.

## Important APIs, Types, And Functions
- `hinic3_queue_pages_init()` computes elements per page, number of pages, and shift values for element lookup.
- `hinic3_queue_pages_alloc()` allocates the `pages` metadata array and then allocates each aligned coherent queue page via `hinic3_dma_zalloc_coherent_align()`.
- `hinic3_queue_pages_free()` frees all allocated DMA pages and the metadata array.
- `__queue_pages_free()` is the partial/full cleanup helper.

## Control Flow
Callers initialize `qpages` with queue depth, page size, and element size. Allocation creates the metadata array, defaults alignment to page size when not specified, then allocates every page. On allocation failure, it frees the subset already allocated. Freeing walks pages in reverse order and resets `qpages->pages` to `NULL`.

## State And Persistence Behavior
The allocated pages are coherent DMA memory visible to hardware and persist until explicit queue destruction. Geometry fields are derived from the queue configuration and used by `get_q_element()` in the header to index descriptors.

## Dependencies And Integration Points
This file depends on `hinic3_hwdev.h` for the device and on aligned DMA helpers from `hinic3_common.h` through `hinic3_queue_common.h`. It is used by `hinic3_wq.c` to back SQ/RQ WQs.

## Risks And Edge Cases
- `num_pages` is calculated as `max(q_depth / elem_per_page, 1)`, so callers should provide queue depths and page/element sizes that divide as expected; the WQ layer enforces power-of-two depths and element sizes.
- `get_q_element()` assumes `num_pages` is a power of two for masking; queue geometry must preserve that invariant.
- Allocation failure must leave no partial DMA pages, which this implementation handles through `__queue_pages_free()`.

## Test Signals
Stress queue creation/destruction at minimum and maximum depths, verify no DMA leaks on mid-allocation failure injection, and run TX/RX traffic across wraparound boundaries to validate `get_q_element()` geometry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_queue_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_queue_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_queue_common.h

## Purpose
`hinic3_queue_common.h` defines `struct hinic3_queue_pages` and the inline queue-element lookup used by hinic3 WQs to address DMA-backed descriptor arrays.

## Important APIs, Types, And Functions
- `struct hinic3_queue_pages` stores the aligned DMA page array, page size, page count, element-size shift, and elements-per-page shift.
- `hinic3_queue_pages_init()`, `hinic3_queue_pages_alloc()`, and `hinic3_queue_pages_free()` are implemented in the `.c` file.
- `get_q_element()` maps an unmasked logical element index to a virtual descriptor pointer and optionally returns remaining elements in the same page.

## Control Flow
Callers allocate and initialize `qpages`, then repeatedly call `get_q_element()` with ring indices. The function masks the page index with `num_pages - 1`, computes element offset inside the page, and returns `page->align_vaddr + offset`.

## State And Persistence Behavior
The header stores no global state. The `qpages` object is per queue and points at coherent DMA pages owned by its caller.

## Dependencies And Integration Points
It depends on `linux/types.h` and `hinic3_common.h` for aligned DMA metadata. It is included by `hinic3_wq.h` and indirectly by NIC I/O, TX, and RX paths.

## Risks And Edge Cases
- `get_q_element()` assumes `num_pages`, `elem_size`, and `elem_per_page` are powers of two because it uses shifts and bit masks.
- Callers can pass unmasked indices, but the queue must be sized so natural wraparound and `idx_mask` behavior remain valid.
- If `remaining_in_page` drives multi-WQEBB writes, a bad geometry calculation could split descriptors incorrectly across pages.

## Test Signals
Descriptor pointer calculations should be validated by queue wraparound TX/RX tests and by WQ multi-WQEBB allocation tests that cross page boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_queue_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rss.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rss.c

## Purpose
`hinic3_rss.c` manages Receive Side Scaling setup for hinic3. It allocates RSS key/indirection resources, chooses queue count, initializes default RSS hash types, programs hash key/type/indirection table into hardware, enables or disables RSS, and cleans software RSS resources.

## Important APIs, Types, And Functions
- `hinic3_try_to_enable_rss()` is the capability-gated setup path. It reads max queues, checks RSS feature support, allocates RSS key/indir arrays, sets the RSS flag, selects queue count, initializes default RSS parameters, and preloads hardware RSS resources with RSS disabled.
- `hinic3_rss_init()` enables RSS at interface start by calling `hinic3_set_hw_rss_parameters(netdev, 1)`.
- `hinic3_rss_uninit()` disables RSS with `hinic3_rss_cfg(..., 0, 0)`.
- `hinic3_clear_rss_config()` frees `rss_hkey` and `rss_indir`.
- `hinic3_rss_set_indir_tbl()` sends the indirection table through command queue `L2NIC_UCODE_CMD_SET_RSS_INDIR_TBL`.
- `hinic3_set_rss_type()`, `hinic3_rss_set_hash_type()`, `hinic3_rss_set_hash_key()`, and `hinic3_rss_cfg()` use management mailbox commands for RSS context, hash engine, key, and enable state.

## Control Flow
Capability setup starts by determining `max_qps` from hardware. If only one queue or no RSS feature is present, the driver clears RSS and uses available queues directly. Otherwise it allocates `rss_hkey` and `rss_indir`, fills a random-ish netdev RSS key, selects default queue count via `netif_get_num_default_rss_queues()`, enables default IPv4/IPv6/TCP/UDP hash types, writes hardware RSS key, fills the indirection table with `ethtool_rxfh_indir_default()`, programs indir/type/hash engine, and leaves RSS disabled until `hinic3_rss_init()` is called.

## State And Persistence Behavior
RSS state lives in `struct hinic3_nic_dev`: `rss_hkey`, `rss_indir`, `rss_hash_type`, `rss_type`, `q_params.num_qps`, `max_qps`, and `HINIC3_RSS_ENABLE` flag. Hardware holds RSS tables and key after mailbox/cmdq programming. The state is re-created at driver/device setup and freed by `hinic3_clear_rss_config()`.

## Dependencies And Integration Points
This file depends on ethtool RSS helpers, `hinic3_cmdq`, `hinic3_mbox`, `hinic3_nic_cfg`, `hinic3_hwif`, and `hinic3_nic_dev`. It integrates with netdev queue sizing, feature discovery from `hinic3_nic_io`, management firmware, and hardware L2NIC microcode.

## Risks And Edge Cases
- On RSS allocation or hardware programming failure, the driver falls back to one queue and clears RSS config.
- `hinic3_set_rss_type()` returns `MGMT_STATUS_CMD_UNSUPPORTED` directly for unsupported firmware; callers currently treat any nonzero result as failure.
- `hinic3_rss_cfg_hash_type()` stores enum values through a pointer and must keep set/get opcode semantics correct.
- Queue count must be initialized before building indirection table, or entries could point outside the configured queue set.

## Test Signals
Validate probe on hardware with and without RSS support, multi-queue packet distribution, ethtool RSS hash/key visibility if exposed elsewhere, fallback to single queue on injected mailbox/cmdq failures, and clean disable on interface stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rss.h

## Purpose
`hinic3_rss.h` exposes the RSS lifecycle API for the hinic3 NIC driver.

## Important APIs, Types, And Functions
- `hinic3_rss_init()` enables/programs RSS for an active netdev.
- `hinic3_rss_uninit()` disables RSS on teardown.
- `hinic3_try_to_enable_rss()` performs capability/resource setup and queue-count selection.
- `hinic3_clear_rss_config()` frees RSS key and indirection arrays.

## Control Flow
Higher-level probe/configuration code calls `hinic3_try_to_enable_rss()` before queue allocation so `q_params.num_qps` is set. Interface open calls `hinic3_rss_init()` to enable hardware RSS; close/unload calls `hinic3_rss_uninit()` and eventually `hinic3_clear_rss_config()`.

## State And Persistence Behavior
The header has no state. It declares functions that mutate `struct hinic3_nic_dev` fields via `netdev_priv()`.

## Dependencies And Integration Points
It includes `linux/netdevice.h` and integrates with hinic3 netdev setup code.

## Risks And Edge Cases
The API ordering matters: clearing RSS config before uninit/init users finish would leave null key/indir pointers. Queue allocation should consume the post-RSS `num_qps` value.

## Test Signals
Build coverage for all call sites and runtime open/close with RSS enabled/disabled are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rx.c

## Purpose
`hinic3_rx.c` implements hinic3 receive queue allocation, page-pool backed buffer provisioning, CQE interpretation, SKB construction, checksum/VLAN/LRO metadata handling, GRO handoff, and RX polling.

## Important APIs, Types, And Functions
- `hinic3_alloc_rxqs()`/`hinic3_free_rxqs()` allocate static `struct hinic3_rxq` objects for all possible queues and initialize stats/geometric fields.
- `hinic3_alloc_rxqs_res()` allocates per-active-RQ dynamic resources: `rx_info`, coherent CQE array, page pool, and initial page fragments.
- `hinic3_configure_rxqs()` binds dynamic resources and NIC I/O RQs into live RX queue objects, associates CQEs with RQ WQEs, and posts initial buffers.
- `hinic3_rx_poll()` is the NAPI poll function for one RX queue.
- `rx_alloc_mapped_page()`, `hinic3_rx_fill_buffers()`, `hinic3_fetch_rx_buffer()`, `packaging_skb()`, `hinic3_add_rx_frag()`, and `recv_one_pkt()` implement buffer lifecycle and SKB construction.
- `hinic3_rx_csum()` interprets CQE offload status and sets `skb->ip_summed`/`csum_level`.
- `hinic3_lro_set_gso_params()` converts hardware LRO count into GSO metadata.

## Control Flow
Resource allocation first creates RX queue objects for `max_qps`, then allocates dynamic resources for configured RQs. Each RQ receives a coherent CQE array and a page pool configured for DMA-from-device fragments. `hinic3_configure_rxqs()` wires each software RXQ to the underlying RQ WQ, writes the fixed CQE DMA address into every RQ WQE, and posts page buffers by filling WQE buffer addresses and ringing the RQ doorbell.

During polling, `hinic3_rx_poll()` checks the CQE at `cons_idx & q_mask`. If `RXDONE` is not set it stops. Otherwise it reads VLAN/length after an `rmb()`, builds an SKB from one or more page-pool fragments, handles checksum/VLAN/LRO metadata, records queue id, sets protocol, and submits to GRO or `netif_receive_skb()` for frag-list packets. It clears CQE status, accounts LRO replenishment pressure, and refills buffers once `delta >= HINIC3_RX_BUFFER_WRITE`.

## State And Persistence Behavior
RX queue state is per queue and runtime-only: ring indices (`cons_idx`, `next_to_alloc`, `next_to_update`, `delta`), page-pool pages in `rx_info`, coherent CQE arrays, MSI-X/vector state, queue geometry, and DIM/coalescing fields. Page ownership transitions from page pool to hardware, then to SKB/page recycle or back to the page pool.

## Dependencies And Integration Points
The file depends on Linux netdevice, VLAN, GRO, and page-pool APIs plus `hinic3_nic_io.h` for RQ doorbells/WQ access. It integrates with NAPI through `rxq->irq_cfg->napi`, with TX/RX queue allocation orchestration through dynamic resource structs, and with hardware through CQEs and RQ WQEs.

## Risks And Edge Cases
- CQE status is the ownership/completion marker; memory ordering via `rmb()` must remain before reading packet length/offload fields.
- `hinic3_rx_fill_buffers()` posts `delta - 1` entries, preserving a ring sentinel; bad delta accounting can starve RX or overrun the ring.
- Small packets are copied into the SKB linear area and full pages are returned; larger packets become frags marked for recycle. Incorrect page clearing would double-free or leak page-pool pages.
- `hinic3_pull_tail()` assumes at least one frag for nonlinear SKBs and enough header bytes in the first frag.
- LRO path increments `num_wqe` only when `num_lro` is set; replenish threshold behavior depends on `lro_replenish_thld`.

## Test Signals
Tests should cover small/large packets, multi-fragment packets, VLAN tag insertion, RX checksum on/off and error CQEs, VXLAN checksum level, LRO/GSO metadata, RX refill under pressure, allocation failure paths, queue wraparound, and repeated open/close with page-pool destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rx.h

## Purpose
`hinic3_rx.h` defines RX CQE/WQE formats, CQE bitfield helpers, RX queue state, dynamic RX resources, and public RX lifecycle/polling functions for hinic3.

## Important APIs, Types, And Functions
- `RQ_CQE_OFFOLAD_TYPE_*`, `RQ_CQE_SGE_*`, and `RQ_CQE_STATUS_*` masks decode CQE packet type, IP type, tunnel format, VLAN enable, length, checksum error, LRO count, and RX done state.
- `struct hinic3_rxq_stats` stores per-RXQ counters with `u64_stats_sync`.
- `struct hinic3_rq_cqe` is the hardware completion format.
- `struct hinic3_rq_wqe` contains buffer and CQE DMA addresses posted to hardware.
- `struct hinic3_rx_info` tracks one page-pool page and offset.
- `struct hinic3_rxq` is the live RX queue object.
- `struct hinic3_dyna_rxq_res` carries dynamic resources before they are attached to a live RXQ.

## Control Flow
The header supports allocation/configuration code in `hinic3_rx.c`: dynamic resources are filled first, then copied into `hinic3_rxq`; polling decodes CQEs with the macros and updates the queue indices.

## State And Persistence Behavior
`struct hinic3_rxq` holds all active RX queue state and references DMA/coherent/page-pool resources owned by queue lifecycle code. It persists only while the netdev queue configuration is active.

## Dependencies And Integration Points
It includes bitfield, DIM, and netdevice headers and references `struct hinic3_io_queue`, `struct hinic3_irq_cfg`, and page-pool objects used by NIC device and interrupt code.

## Risks And Edge Cases
- The misspelled `OFFOLAD` macro names are part of local API; renaming requires touching all users.
- Field widths in macros must match firmware CQE layout.
- `q_mask` assumes power-of-two depth.
- `dev` is documented as the device for DMA mapping but the implementation primarily uses the page pool and PCI device for coherent CQE allocation.

## Test Signals
Compile-time coverage of CQE field users, runtime CQE decode validation, and queue stats consistency under RX traffic are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_tx.c

## Purpose
`hinic3_tx.c` implements hinic3 transmit queue allocation, SKB DMA mapping into SQ descriptors, checksum/TSO/UFO/VLAN offload programming, doorbell submission, completion polling, and TX queue flushing.

## Important APIs, Types, And Functions
- `hinic3_alloc_txqs()`/`hinic3_free_txqs()` allocate static TXQ objects for all possible queues and initialize stats.
- `hinic3_alloc_txqs_res()`/`hinic3_free_txqs_res()` allocate/free dynamic TX descriptors, SKB tracking, and DMA-info arrays.
- `hinic3_configure_txqs()` binds dynamic resources and SQs to active TX queues and computes stop/start thresholds.
- `hinic3_xmit_frame()` is the netdev transmit entry point.
- `hinic3_send_one_skb()` validates carrier/queue space, prepares offload/task data, allocates WQEBBs, maps SKB fragments, writes descriptor control, and rings the SQ doorbell.
- `hinic3_tx_poll()` reclaims completed TX WQEs based on hardware CI.
- `hinic3_flush_txqs()` forces hardware TX drop/stop and resets subqueues during teardown.

## Control Flow
Transmit starts in `hinic3_xmit_frame()`, which drops if carrier is down or queue mapping is invalid. `hinic3_send_one_skb()` pads short frames, computes SGE/WQEBB needs, stops the subqueue if free WQEBBs are below threshold, prepares offload metadata, reserves queue elements, maps the linear SKB and frags for DMA, updates BDs/task WQE if needed, records the SKB in `tx_info[pi]`, updates BQL/netdev queue state, writes SQ control fields, and rings the SQ doorbell with local PI.

Completion polling reads hardware CI from the coherent CI table, walks `tx_info` entries from local CI while complete WQEBB spans are available, unmaps DMA, consumes SKBs through NAPI, advances local WQ CI by total WQEBBs, and wakes the subqueue based on free WQEBBs.

## State And Persistence Behavior
TXQ state includes `tx_info` per WQ index, per-SKB `dma_info` arrays, SQ pointer, queue thresholds, and stats. Hardware-visible state includes WQ descriptors, owner bits, producer index via doorbell, and CI updates through coherent memory. All state is runtime-only and released when queues are destroyed.

## Dependencies And Integration Points
The file depends on Linux VLAN, IP/IPv6, checksum, I/O polling, BQL netdev queue helpers, `hinic3_nic_io`, `hinic3_nic_cfg`, and `hinic3_wq`. It integrates with firmware/device control through `hinic3_force_drop_tx_pkt()` and with netdev through `ndo_start_xmit` and NAPI completion.

## Risks And Edge Cases
- DMA rollback is handled if mapping fails after WQ reservation; this relies on restoring both `prod_idx` and owner bit.
- `hinic3_tx_csum()` only offloads VXLAN UDP tunnels on the standard port; other encapsulations fall back to `skb_checksum_help()`.
- Compact WQE mode is only used for no-offload, single-SGE packets under `HINIC3_COMPACT_WQEE_SKB_MAX_LEN`; oversized compact candidates are dropped.
- `PLDOFF` above `SQ_CTRL_MAX_PLDOFF` invalidates offload and drops the packet.
- `hinic3_tx_poll()` assumes `tx_info->skb` is valid for any completed span; corrupted completion accounting can dereference null/stale SKBs.
- Stats structures are initialized but this file does not visibly update most counters, so observability may be incomplete.

## Test Signals
Validate line-rate TX, fragmented SKBs up to `HINIC3_MAX_SQ_SGE`, short frame padding, queue stop/wake behavior, TSO for IPv4/IPv6, VXLAN tunnel checksum/TSO, VLAN insertion, DMA mapping failure injection, TX completion wraparound, and `hinic3_flush_txqs()` during interface stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_tx.h

## Purpose
`hinic3_tx.h` defines hinic3 SQ descriptor/task formats, TX offload bitfields, TX queue state, dynamic TX resources, and public TX lifecycle/submit/poll functions.

## Important APIs, Types, And Functions
- `VXLAN_OFFLOAD_PORT_LE`, `TCP_HDR_DATA_OFF_UNIT_SHIFT`, `TRANSPORT_OFFSET`, `HINIC3_COMPACT_WQEE_SKB_MAX_LEN`, `HINIC3_TX_POLL_WEIGHT`, and default thresholds parameterize TX behavior.
- `enum sq_wqe_data_format`, `enum sq_wqe_ec_type`, `enum sq_wqe_tasksect_len_type`, and `enum hinic3_tx_offload_type` describe descriptor mode and offload flags.
- `SQ_CTRL_*`, `SQ_CTRL_QUEUE_INFO_*`, and `SQ_TASK_INFO*` macros encode hardware WQE control/task fields.
- `struct hinic3_sq_wqe_desc`, `struct hinic3_sq_task`, and `struct hinic3_sq_wqe_combo` describe the descriptor pieces assembled by `hinic3_tx.c`.
- `struct hinic3_txq_stats`, `struct hinic3_dma_info`, `struct hinic3_tx_info`, `struct hinic3_txq`, and `struct hinic3_dyna_txq_res` define software TX state.

## Control Flow
The implementation fills a `hinic3_sq_wqe_combo` from WQ elements, maps an SKB into `hinic3_dma_info`, encodes offload choices in `hinic3_sq_task` and descriptor control words, and stores the SKB/WQEBB count in `hinic3_tx_info` for later completion reclamation.

## State And Persistence Behavior
The header describes per-queue and per-packet runtime state only. No state persists beyond queue lifetime.

## Dependencies And Integration Points
It includes Linux bitops, IP/IPv6, netdevice, and checksum headers and relies on `struct hinic3_io_queue`/`struct hinic3_sq_bufdesc` from NIC I/O/WQ headers. Public functions are used by the hinic3 netdev open/close/NAPI paths.

## Risks And Edge Cases
- Hardware field masks are protocol-critical; changing bit positions breaks descriptor interpretation.
- `SQ_CTRL_QUEUE_INFO_GET()` expects a little-endian descriptor value and converts internally.
- `HINIC3_MAX_SQ_SGE` must remain aligned with dynamic DMA-info allocation and hardware maximum.
- `HINIC3_DEFAULT_STOP_THRS`/`START_THRS` are clamped by queue depth in implementation.

## Test Signals
Build and runtime TX offload tests, descriptor decode review against hardware spec, and queue threshold behavior under backpressure are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_wq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_wq.c

## Purpose
`hinic3_wq.c` implements hinic3 generic work queue creation/destruction/reset and multi-WQEBB allocation. It maps logical queue entries onto one or more coherent DMA pages and, when needed, creates an indirection table for hardware chip logical addressing.

## Important APIs, Types, And Functions
- `hinic3_wq_create()` validates depth/element size, initializes geometry, allocates pages, and builds the WQ block.
- `hinic3_wq_destroy()` frees WQ pages and optional WQ block indirection table.
- `hinic3_wq_reset()` clears producer/consumer indices and zeroes each queue page.
- `hinic3_wq_get_multi_wqebbs()` reserves multiple WQ elements and returns first/second contiguous pieces when the reservation crosses a page boundary.
- `hinic3_wq_is_0_level_cla()` reports whether a queue fits in one direct-mapped page.
- `wq_init_wq_block()`, `wq_alloc_pages()`, and `wq_free_pages()` are internal allocation helpers.

## Control Flow
Creation checks `q_depth` against `[64, 65536]`, requires power-of-two depth and WQEBB size, aligns the hardware page size to `HINIC3_MIN_PAGE_SIZE`, initializes `qpages`, allocates pages, then either points `wq_block_*` at the first queue page for level-0 CLA or allocates a minimum-page-size DMA page containing big-endian page physical addresses for level-1 CLA. Multi-WQEBB reservation advances `prod_idx`, returns the current index, and splits the descriptor span only if it crosses the current DMA page.

## State And Persistence Behavior
Each `struct hinic3_wq` owns coherent DMA queue pages plus an optional coherent indirection table. Producer/consumer indices are software runtime state; hardware sees pages through context programming in `hinic3_nic_io.c`.

## Dependencies And Integration Points
This file depends on `linux/dma-mapping.h`, `hinic3_hwdev`, `hinic3_queue_common`, and `hinic3_wq.h`. It is used by SQ/RQ allocation in `hinic3_nic_io.c` and descriptor access in TX/RX paths.

## Risks And Edge Cases
- Multi-page WQs are limited by `WQ_MAX_NUM_PAGES`, derived from the minimum page size divided by 64-bit page addresses.
- The WQ block stores page addresses as big-endian 64-bit values, unlike most NIC descriptors that use little-endian fields.
- `hinic3_wq_get_multi_wqebbs()` assumes callers have already checked free space.
- Reset zeroes descriptor memory but does not notify hardware by itself.

## Test Signals
Create/destroy WQs at min/max supported depths, verify level-0 vs level-1 CLA programming, exercise TX descriptors crossing page boundaries, and run queue reset/reopen cycles with no stale descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_wq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_wq.h

## Purpose
`hinic3_wq.h` defines generic hinic3 work queue structures and inline producer/consumer helpers used by SQ/RQ implementations.

## Important APIs, Types, And Functions
- `struct hinic3_sq_bufdesc` is the 16-byte SQ buffer descriptor used for additional SGEs.
- `struct hinic3_wq` stores queue pages, producer/consumer indices, queue depth/mask, and hardware WQ block address/table.
- `hinic3_wq_get_used()`, `hinic3_wq_free_wqebbs()`, `hinic3_wq_get_one_wqebb()`, `hinic3_wq_put_wqebbs()`, and `hinic3_wq_get_first_wqe_page_addr()` are hot-path helpers.
- `hinic3_wq_create()`, `hinic3_wq_destroy()`, `hinic3_wq_reset()`, `hinic3_wq_get_multi_wqebbs()`, and `hinic3_wq_is_0_level_cla()` are implemented in `hinic3_wq.c`.

## Control Flow
Producers call `hinic3_wq_get_one_wqebb()` or `hinic3_wq_get_multi_wqebbs()` to reserve descriptors and advance `prod_idx`. Completion paths call `hinic3_wq_put_wqebbs()` to advance `cons_idx`. Free space always subtracts one sentinel entry to avoid full/empty ambiguity.

## State And Persistence Behavior
The WQ object holds per-queue runtime state and coherent DMA memory pointers. Indices are 16-bit unmasked counters that naturally wrap; `idx_mask` maps them to ring slots.

## Dependencies And Integration Points
It includes `linux/io.h` and `hinic3_queue_common.h`, and it is included by NIC I/O, TX, and RX code.

## Risks And Edge Cases
- `hinic3_wq_free_wqebbs()` relies on unsigned 16-bit arithmetic and one unused entry; incorrect producer/consumer updates can report false free space.
- `hinic3_wq_get_one_wqebb()` performs no availability check.
- Hardware page address returned by `hinic3_wq_get_first_wqe_page_addr()` must match queue context expectations.

## Test Signals
Ring wraparound tests, descriptor reservation under near-full conditions, completion reclamation, and page-boundary multi-WQEBB reservations validate this header’s contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic3/hinic3_wq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/82596.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/82596.c

## Purpose
`82596.c` is the legacy m68k VME Intel 82596 Ethernet driver for MVME16x and BVME6000 boards. It is a standalone version of the i596 data-path core using platform-specific MMIO, word-swapped bus pointers, noncached shared pages, and netdev operations.

## Important APIs, Types, And Functions
- Descriptor/control structures include `struct i596_tbd`, `struct i596_cmd`, `struct tx_cmd`, `struct tdr_cmd`, `struct mc_cmd`, `struct sa_cmd`, `struct cf_cmd`, `struct i596_rfd`, `struct i596_rbd`, `struct i596_scb`, `struct i596_iscp`, `struct i596_scp`, and `struct i596_private`.
- `CA()` and `MPU_PORT()` are board-dependent channel-attention/port-command helpers for MVME16x and BVME6000.
- `i82596_probe()` detects supported board type, reads MAC address from board storage, allocates a shared page, sets cache mode, initializes private state, and registers the netdev.
- `i596_open()` requests interrupts, initializes RX buffers and chip memory, and starts the netdev queue.
- `init_i596_mem()` resets the chip, programs SCP/ISCP/SCB, queues configure/address/TDR commands, and starts the receive unit.
- `i596_start_xmit()`, `i596_add_cmd()`, `i596_interrupt()`, `i596_rx()`, `i596_close()`, `i596_reset()`, and `set_multicast_list()` implement the data path and control path.

## Control Flow
Module init calls `i82596_probe()`, which supports one device. Open allocates IRQs, builds an RX RFD/RBD ring with SKBs, starts the 82596 command/receive units, and starts the netdev queue. TX stops the queue, pads short frames, chooses the next TX command/TBD slot, writes word-swapped bus pointers, pushes cache for the packet on m68k, queues the command, increments stats, and restarts the queue. Interrupt handling acknowledges command completion, command-unit inactive, frame received, and receive-unit inactive bits; completed TX commands free SKBs and clear command slots, RX completions either pass large SKBs in place or copy small frames, then recycle descriptors and restart RX if needed.

## State And Persistence Behavior
The driver stores all private shared state in a single page assigned to `dev->ml_priv` and made noncached on m68k. Runtime state includes command queue head/tail/backlog, RFD/RBD heads, TX ring index, last restart packet count, and SCB error counters. Module cleanup unregisters netdev, restores cache mode, frees the page, and frees netdev.

## Dependencies And Integration Points
It depends on m68k board headers (`mvme16xhw.h`, `bvme6000hw.h`), cache management, legacy `virt_to_bus()`, netdevice APIs, and architecture-specific IRQ/register definitions. Kconfig builds this file for `CONFIG_MVME16x_NET` and `CONFIG_BVME6000_NET`.

## Risks And Edge Cases
- It relies heavily on 32-bit word-swapped bus pointers and m68k cache control; incorrect cache mode or pointer swapping breaks DMA.
- TX ring full drops packets rather than returning persistent backpressure.
- `I596_NULL` is a pointer sentinel and many loops depend on it being exact.
- RX copybreak path and in-place path have different alignment/cache behavior.
- Some cleanup paths assume the single probed device exists and was registered successfully.

## Test Signals
Validation requires architecture/board boot tests, probe on MVME/BVME hardware or emulator, open/close cycles, RX/TX traffic, multicast/promiscuous changes, TX timeout recovery, receive-unit-not-ready recovery, and cache/DMA coherency stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/82596.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/Kconfig

## Purpose
`Kconfig` declares configuration options for legacy Intel 82586/82593/82596 Ethernet devices and gates them by architecture/platform support.

## Important APIs, Types, And Functions
- `NET_VENDOR_I825XX` is the vendor menu switch, defaulting to `y` when `NET_VENDOR_INTEL` is enabled.
- `ARM_ETHER1` builds Acorn Ether1 support for `ARM && ARCH_ACORN`.
- `BVME6000_NET` builds 82596 support for BVME6000.
- `LASI_82596` builds HP PA-RISC LASI 82596 support for `GSC`.
- `MVME16x_NET` builds 82596 support for Motorola MVME16x.
- `SNI_82596` builds SNI RM 82596 support for `SNI_RM`.
- `SUN3_82586` builds Sun3 onboard 82586 support for `SUN3`.

## Control Flow
There is no runtime control flow. Kconfig selection determines which driver objects the Makefile builds and which platform code can reference these drivers.

## State And Persistence Behavior
No runtime state. The file controls compile-time configuration.

## Dependencies And Integration Points
It integrates with the kernel networking driver menu and `drivers/net/ethernet/i825xx/Makefile`. Platform dependencies prevent compiling hardware-specific drivers on unsupported architectures.

## Risks And Edge Cases
Incorrect dependencies can cause build failures from architecture-specific headers or hide valid drivers. `NET_VENDOR_I825XX` being only a menu gate means disabling it skips all child prompts.

## Test Signals
Kconfig allmodconfig/allyesconfig on supported architectures and dependency resolution for unsupported architectures are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/Makefile

## Purpose
`Makefile` maps i825xx Kconfig symbols to driver objects.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_ARM_ETHER1) += ether1.o`
- `obj-$(CONFIG_SUN3_82586) += sun3_82586.o`
- `obj-$(CONFIG_LASI_82596) += lasi_82596.o`
- `obj-$(CONFIG_SNI_82596) += sni_82596.o`
- `obj-$(CONFIG_MVME16x_NET) += 82596.o`
- `obj-$(CONFIG_BVME6000_NET) += 82596.o`

## Control Flow
No runtime control flow. The build system includes objects according to enabled config symbols. Both MVME16x and BVME6000 select the same `82596.o` source, which has internal conditional support for both boards.

## State And Persistence Behavior
No state.

## Dependencies And Integration Points
It integrates directly with the Kbuild system and the Kconfig symbols in the same directory.

## Risks And Edge Cases
If both `MVME16x_NET` and `BVME6000_NET` are enabled, Kbuild references `82596.o` through two config lines; the source itself handles both via `IS_ENABLED()`. Object duplication should be checked in Kbuild behavior for combined configs.

## Test Signals
Build matrix coverage for each config symbol and combined MVME/BVME settings validates the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/ether1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/ether1.c

## Purpose
`ether1.c` is the Acorn Ether1 expansion-card Ethernet driver built around an Intel 82586. It manages the card’s banked onboard RAM, initializes 82586 command/receive structures, handles transmit/receive interrupts, and registers an `ecard_driver`.

## Important APIs, Types, And Functions
- `ether1_inw_p()`, `ether1_outw_p()`, `ether1_writebuffer()`, and `ether1_readbuffer()` access banked card RAM through the page register and optimized ARM copy loops.
- `ether1_ramtest()`, `ether1_reset()`, `ether1_init_2()`, and `ether1_init_for_open()` validate card memory and initialize 82586 SCP/ISCP/SCB/config/address/multicast/TDR/NOP/RFD/RBD structures.
- `ether1_txalloc()` allocates space from the card RAM TX circular area.
- `ether1_sendpacket()` builds TX/TBD/data/NOP blocks in card RAM and links the previous NOP to the new TX command.
- `ether1_xmit_done()` and `ether1_recv_done()` process completed TX/RX descriptors.
- `ether1_interrupt()` acknowledges SCB events and dispatches TX/RX/RU/CU handling.
- `ether1_probe()` maps the expansion card, reads IDPROM MAC address, tests RAM, registers netdev, and stores driver data.

## Control Flow
Probe requests ecard resources, maps the IOCFAST region, resets/tests card RAM, reads MAC, installs netdev ops, and registers. Open requests IRQ, initializes the 82586 command chain and receive ring in onboard RAM, then starts the netdev queue. TX pads short packets, reserves card-RAM regions for TX command/TBD/data/NOP, writes them, patches the prior NOP link under IRQ exclusion, and stops the queue if a future full-size frame would not fit. Interrupts acknowledge SCB bits, process command completions, restart CU/RU when needed, and recycle RX descriptors by moving the suspend marker.

## State And Persistence Behavior
`struct ether1_priv` stores MMIO base, TX linked-list pointers, RX head/tail, bus type, and reset/restart flags. The 82586 state itself lives in the card’s 64 KiB RAM as descriptor rings and command blocks. No persistent state survives device removal.

## Dependencies And Integration Points
It depends on Acorn expansion-card APIs (`ecard_*`), ARM I/O/DMA headers, netdevice APIs, and `ether1.h` descriptor definitions. It integrates with the kernel netdev model through `ether1_netdev_ops`.

## Risks And Edge Cases
- Banked RAM access disables local IRQs selectively; concurrent descriptor updates must preserve page-register correctness.
- `ether1_txalloc()` uses software head/tail pointers over card RAM and must handle wraparound without colliding with pending TX blocks.
- Multicast filter function is empty, so multicast/promiscuous behavior is limited despite netdev callback presence.
- Reset during TX interrupt is tracked by flags but remains a fragile legacy path.
- The optimized ARM assembly copy routines are architecture-specific and sensitive to odd lengths.

## Test Signals
Probe/RAM-test logs, TX/RX traffic, TX ring wraparound, watchdog reset recovery, RU suspended recovery, odd-length packet copy correctness, and ecard remove/open/close cycles are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/ether1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/ether1.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/ether1.h

## Purpose
`ether1.h` defines private state, register offsets, control bits, and Intel 82586 descriptor/control structures for the Acorn Ether1 driver. Most definitions are visible only when `__ETHER1_C` is defined by `ether1.c`.

## Important APIs, Types, And Functions
- `struct ether1_priv` stores mapped base address, TX/RX ring pointers, bus type, and reset/init flags.
- Register macros include `REG_PAGE`, `REG_CONTROL`, `ETHER1_RAM`, `IDPROM_ADDRESS`, and control bits `CTRL_RST`, `CTRL_LOOPBACK`, `CTRL_CA`, and `CTRL_ACK`.
- Descriptor typedefs include `tdr_t`, `tx_t`, `tbd_t`, `rfd_t`, `rbd_t`, `nop_t`, `mc_t`, `sa_t`, `cfg_t`, `scb_t`, `iscp_t`, and `scp_t`.
- Command/status macros define 82586 commands, SCB command bits, RX/TX status bits, TDR result bits, and configuration byte fields.

## Control Flow
The header does not execute logic but establishes the binary layout used by `ether1.c` when writing structures into card RAM and reading status back from the 82586.

## State And Persistence Behavior
State is represented by `struct ether1_priv` in netdev private memory and by descriptors written to card RAM. The header itself stores no state.

## Dependencies And Integration Points
It is tightly coupled to `ether1.c` via `__ETHER1_C` and `priv(dev)`. It integrates with Intel 82586 hardware layout and Acorn Ether1 register mapping.

## Risks And Edge Cases
- Struct sizes and field order must match 82586 hardware format and the fixed offsets used in `ether1.c`.
- `I82586_NULL` is `-1` and must be written as a 16-bit/offset sentinel where expected.
- Header visibility depends on `__ETHER1_C`, so external reuse is intentionally prevented.

## Test Signals
Successful initialization command statuses, correct TX/RX descriptor parsing, and no RAM layout mismatch warnings during `ether1_init_for_open()` validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/ether1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/lasi_82596.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/lasi_82596.c

## Purpose
`lasi_82596.c` is the PA-RISC LASI onboard Intel 82596 Ethernet wrapper. It supplies LASI-specific channel-attention and MPU-port accessors, allocates noncoherent DMA memory, obtains the MAC address, and includes `lib82596.c` as the shared 82596 implementation.

## Important APIs, Types, And Functions
- `ca()` writes LASI channel attention via `gsc_writel()`.
- `mpu_port()` writes 82596 port commands through LASI CPU port registers, optionally swapping 16-bit halves for specific hardware revisions.
- `lan_init_chip()` probes a `parisc_device`, allocates netdev/private DMA memory, reads MAC via PDC or fallback EEPROM, sets options, and calls `i82596_probe()` from `lib82596.c`.
- `lan_remove_chip()` unregisters netdev and frees DMA/netdev resources.
- `lan_tbl`, `lan_driver`, `lasi_82596_init()`, and `lasi_82596_exit()` register the PA-RISC driver.

## Control Flow
The wrapper defines `SYSBUS`, `SWAP32`, `SWAP16`, and `NONCOHERENT_DMA` before including `lib82596.c`; this specializes the shared driver to PA-RISC DMA and endian behavior. Probe validates IRQ, allocates an Ethernet netdev, maps base/IRQ, reads MAC, allocates a noncoherent `struct i596_dma`, and delegates netdev registration/data-path setup to `i82596_probe()`.

## State And Persistence Behavior
Wrapper state is in netdev private `struct i596_private`, including LASI options and the noncoherent DMA block address. Platform driver data stores the netdev pointer. State is removed on driver removal.

## Dependencies And Integration Points
It depends on PA-RISC GSC/PDC/parisc-device APIs, Linux DMA mapping, and `lib82596.c`. It integrates with the shared i596 netdev ops through preprocessor hooks.

## Risks And Edge Cases
- Noncoherent DMA requires correct `dma_sync_*` calls from the included core; missing syncs can corrupt descriptors.
- The remove path frees DMA with `sizeof(struct i596_private)` rather than `sizeof(struct i596_dma)` in the visible code, which is a risk worth auditing.
- `running_on_qemu` changes MPU-port delay behavior.
- MAC fallback reads a fixed `LAN_PROM_ADDR`.

## Test Signals
Probe on supported PA-RISC systems, DMA coherency under RX/TX load, PDC and EEPROM MAC paths, remove/unload memory accounting, and TDR/link logs validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/lasi_82596.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/lib82596.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/lib82596.c

## Purpose
`lib82596.c` is a shared, include-based Intel 82596 netdev implementation used by platform wrappers such as LASI and SNI. The including file supplies endian macros, `SYSBUS`, `ca()`, `mpu_port()`, and optional noncoherent-DMA behavior.

## Important APIs, Types, And Functions
- Shared descriptor structures include `struct i596_dma`, `struct i596_private`, `struct i596_cmd`, TX/RX descriptor types, SCB/ISCP/SCP, and setup command types.
- `virt_to_dma()` converts addresses inside the coherent/noncoherent `i596_dma` block to device DMA addresses.
- `dma_sync_dev()`/`dma_sync_cpu()` become real syncs only when `NONCOHERENT_DMA` is defined.
- `init_rx_bufs()`, `remove_rx_bufs()`, and `rebuild_rx_bufs()` manage RX SKB/DMA rings.
- `init_i596_mem()` resets/programs the chip, queues configure/address/TDR commands, requests IRQ, and starts RX.
- `i596_add_cmd()`, `i596_cleanup_cmd()`, `i596_reset()`, `i596_start_xmit()`, `i596_rx()`, `i596_interrupt()`, `i596_open()`, `i596_close()`, and `set_multicast_list()` implement the core netdev behavior.
- `i82596_probe()` validates descriptor sizes, initializes private state, sets netdev ops, and registers the netdev.

## Control Flow
Platform wrapper probe allocates `struct i596_dma` and calls `i82596_probe()`. Netdev open builds RX rings and initializes hardware. TX maps SKB data to DMA, fills a TX command/TBD pair, queues it on the command unit, and updates packet stats. Interrupts process completed command queue entries, unmap/free TX SKBs, handle TDR/config completion, process RX frames, rebuild/restart RX on receive-unit inactive, write SCB acknowledgements, and issue channel attention. Close aborts CU/RU, drains commands, frees IRQ, and removes RX buffers.

## State And Persistence Behavior
All hardware-shared descriptors live in the `i596_dma` block allocated by the wrapper. `i596_private` tracks command backlog, TX ring index, RX descriptor heads, options, DMA address, and MMIO hooks. RX SKBs are DMA-mapped until recycled or close; TX SKBs are DMA-mapped until command completion or cleanup.

## Dependencies And Integration Points
The file is intentionally not compiled alone. It depends on include-time definitions from `lasi_82596.c` or `sni_82596.c`, Linux netdevice/DMA/IRQ APIs, and hardware callbacks `ca()`/`mpu_port()`. It optionally supports netpoll via `CONFIG_NET_POLL_CONTROLLER`.

## Risks And Edge Cases
- Include-based reuse means symbols are `static` within each wrapper but macro contracts are implicit and fragile.
- DMA coherency differs between wrappers; `NONCOHERENT_DMA` must be set correctly.
- RX path may drop packets if replacement SKB allocation fails after unmapping a filled buffer.
- Command backlog timeout resets the board from `i596_add_cmd()`, which can run in contexts that already interacted with queue state.
- Descriptor size/build assertions protect layout but only for selected structures.
- `set_multicast_list()` can queue multicast commands even while prior ones are active; config command has a guard but multicast command has less explicit serialization.

## Test Signals
Wrapper-specific build tests, open/close, RX/TX traffic, command completion interrupts, receive-unit inactive recovery, multicast/promiscuous changes, netpoll if enabled, DMA mapping failure tests, and noncoherent sync validation are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/lib82596.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sni_82596.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sni_82596.c

## Purpose
`sni_82596.c` is the SNI RM platform wrapper for the Intel 82596 shared driver. It maps platform resources, reads the board-specific MAC layout, defines little-endian 82596 access macros, and includes `lib82596.c`.

## Important APIs, Types, And Functions
- `ca()` writes channel attention through `lp->ca`.
- `mpu_port()` writes 32-bit or two 16-bit MPU-port commands depending on `OPT_MPU_16BIT`.
- `sni_82596_probe()` maps MPU/CA/IDPROM resources, allocates netdev, reads MAC bytes in reversed IDPROM order, allocates coherent `struct i596_dma`, and calls `i82596_probe()`.
- `sni_82596_driver_remove()` unregisters netdev, frees coherent DMA, unmaps resources, and frees netdev.
- `sni_82596_driver`, `sni_82596_init()`, and `sni_82596_exit()` register the platform driver.

## Control Flow
The wrapper defines `SYSBUS`, `SWAP32`, `SWAP16`, and `OPT_MPU_16BIT` before including `lib82596.c`. Probe obtains three memory resources plus an options resource, maps MPU and CA registers, maps IDPROM temporarily to read the MAC, checks IRQ, stores options/MMIO pointers in `i596_private`, allocates coherent DMA, and delegates to shared registration.

## State And Persistence Behavior
Runtime state is held in `struct i596_private` inside netdev private memory: options, CA/MPU mappings, DMA block pointer/address, and the shared core state. Platform device driver data stores the netdev pointer.

## Dependencies And Integration Points
It depends on Linux platform-device/resource APIs, MMIO accessors, coherent DMA, and `lib82596.c`. It exposes `MODULE_ALIAS("platform:snirm_82596")`.

## Risks And Edge Cases
- Resource type call `platform_get_resource(dev, 0, 0)` for options relies on flags/IORESOURCE_BITS rather than a named resource, so platform data must match exactly.
- Remove path frees DMA with `sizeof(struct i596_private)` rather than `sizeof(struct i596_dma)` in the visible code, mirroring a suspicious size mismatch risk.
- Probe has multiple mapping/allocation failure branches; each must unmap only resources already mapped.
- MAC byte order is board-specific and intentionally reversed from IDPROM offsets.

## Test Signals
Platform resource probing, 16-bit and 32-bit MPU modes, MAC address correctness, TX/RX traffic, unload cleanup, and error-injection on resource/DMA allocation validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sni_82596.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sun3_82586.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sun3_82586.c

## Purpose
`sun3_82586.c` is a Sun3 onboard Intel 82586 Ethernet driver. It uses Sun3 OBIO control bits and DVMA memory to initialize 82586 SCP/ISCP/SCB structures, run TX/RX rings, handle interrupts, recover from receiver-not-ready, and register a single netdev on supported Sun3 models.

## Important APIs, Types, And Functions
- Hardware macros `sun3_attn586()`, `sun3_reset586()`, `sun3_disint()`, `sun3_enaint()`, and `sun3_active()` manipulate OBIO control bits.
- Address conversion macros `make32()`, `make24()`, and `make16()` translate between 82586 offsets and CPU/DVMA addresses with byte swapping.
- `struct priv` holds DVMA base/memory pointers, 82586 control pointers, RFD/RBD state, TX command/buffer state, and counters.
- `sun3_82586_probe()` and `sun3_82586_probe1()` detect supported models, map OBIO, allocate aligned DVMA memory, check the chip, set MAC from IDPROM, and register netdev.
- `alloc586()`, `init586()`, `alloc_rfa()`, and `startrecv586()` initialize chip memory and rings.
- `sun3_82586_send_packet()`, `sun3_82586_interrupt()`, `sun3_82586_rcv_int()`, `sun3_82586_xmt_int()`, `sun3_82586_rnr_int()`, `sun3_82586_timeout()`, and `set_multicast_list()` implement data/control paths.

## Control Flow
Module init probes only Sun3 3/160 and 3/260 models. Probe maps OBIO, allocates DVMA memory, verifies the chip by observing ISCP busy clear, initializes private pointers, chooses receive-buffer count based on memory size, and registers netdev. Open disables interrupts, allocates/initializes 82586 state, starts RX, enables interrupts, requests IRQ, and starts the queue. TX copies the SKB into the single configured transmit buffer, starts or resumes the command unit, and frees the SKB. Interrupts acknowledge SCB status bits, process received frames, handle RNR by aborting/rebuilding/restarting RX, and process TX completion/error status. Multicast changes reinitialize the chip.

## State And Persistence Behavior
All 82586-visible state resides in DVMA memory allocated during probe and referenced by `dev->mem_start`/`mem_end` and `struct priv`. The driver keeps one TX buffer by default (`NUM_XMIT_BUFFS == 1`) and a receive frame area sized for 8/16/32 KiB memory. State is not persistent across module load.

## Dependencies And Integration Points
It depends on Sun3 architecture headers (`idprom`, `machines`, `sun3mmu`, `dvma`), the companion `sun3_82586.h` descriptor definitions, and Linux netdevice APIs. It integrates with fixed Sun3 OBIO hardware rather than a discoverable bus.

## Risks And Edge Cases
- The timeout handler is declared `void` but contains a `return 0` inside a disabled branch if `NO_NOPCOMMANDS` is not defined; current macro configuration avoids compiling that path.
- Many wait macros busy-loop and reset hardware on timeout; failures can leave the device disabled.
- The driver stops the queue for every TX and relies on TX interrupt to wake it.
- Multicast changes reinitialize the whole device, which can disrupt in-flight traffic.
- Oversized RX frames are dropped after walking RBDs to the last buffer.

## Test Signals
Sun3 boot/probe, open/close, TX interrupt wakeups, RX frame delivery, RNR recovery, multicast/promiscuous reconfiguration, TX timeout restart, and DVMA memory leak checks are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/i825xx/sun3_82586.c -->
