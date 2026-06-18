# subset-b-004519 Research

Grouped research for Marvell OcteonTX2 NIC and Prestera switch driver files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_struct.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_struct.h

## Purpose
`otx2_struct.h` defines the low-level NIX completion queue entry, send queue entry, receive parser, scatter/gather, and error/status layouts used by the OcteonTX2/CN10K RVU Ethernet data path. It is the bitfield contract between the driver and NIX hardware, consumed by TX/RX, XDP, QoS, timestamp, and offload paths.

## Important APIs, Types, and Functions
The file exports enums for CQE/SQE sizes, SQE subdescriptor kinds, load types, checksum L3/L4 encoding, CQE types, send memory algorithms, CQ/RQ/SQ interrupt bits, SQ operation errors, MNQ errors, and send completion statuses. Important structures include `nix_cqe_hdr_s`, `nix_rx_parse_s`, `nix_rx_sg_s`, `nix_send_comp_s`, `nix_cqe_rx_s`, `nix_cqe_tx_s`, `nix_sqe_hdr_s`, `nix_sqe_ext_s`, `nix_sqe_sg_s`, and `nix_sqe_mem_s`.

## Control Flow
There is no executable flow in this header. Runtime flow is imposed by descriptor ordering: RX CQEs contain a header, parser result, and SG descriptors; TX SQEs are built as a send header followed by optional extended, SG, and memory subdescriptors. `otx2_txrx.c` reads CQE types/status and writes SQE subdescriptor fields according to these layouts.

## State and Persistence
All state represented here is hardware ring state or mailbox-programmed descriptor interpretation. Bitfield values persist only while CQEs/SQEs reside in DMA-backed queue memory. Error/status enums feed interrupt handling and cleanup decisions.

## Dependencies and Integration Points
The header depends on Linux fixed-width integer types through included driver headers. It integrates with `otx2_txrx.c`, `otx2_xsk.c`, `qos_sq.c`, CN10K IPsec/LSO helpers, and hardware register/mailbox definitions in `otx2_reg.h` and `otx2_common.h`.

## Risks and Edge Cases
Bitfield layout correctness is critical and architecture-sensitive; endian assumptions and descriptor size mismatches can corrupt packet parsing or transmission. Several fields are reused for timestamp, VLAN insertion, shaping, and checksum offload, so changes need hardware documentation coverage. Error enums must stay synchronized with firmware/AF behavior.

## Test Signals
Useful signals include RX/TX traffic with checksum, VLAN, TSO, XDP, AF_XDP, PTP timestamp, and QoS enabled; CQ/SQ interrupt error injection; sparse/packed struct layout build checks; and hardware trace dumps validating parser words and completion status decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_tc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_tc.c

## Purpose
`otx2_tc.c` implements TC offload for the RVU NIC: clsact flower ingress rules, matchall ingress/egress policing, MCAM rule management, redirect/mirror actions, skb mark support, and HTB handoff. It converts Linux TC flow rules into NPC MCAM and NIX scheduler/policer mailbox requests.

## Important APIs, Types, and Functions
Exports include `otx2_setup_tc()`, `otx2_setup_tc_cls_flower()`, `otx2_init_tc()`, `otx2_shutdown_tc()`, `otx2_tc_apply_ingress_police_rules()`, `otx2_add_mcam_flow_entry()`, `otx2_del_mcam_flow_entry()`, and `otx2_tc_add_to_flow_list()`. Core helpers are `otx2_tc_prepare_flow()`, `otx2_tc_parse_actions()`, `otx2_tc_add_flow()`, `otx2_tc_del_flow()`, `otx2_tc_get_flow_stats()`, and rate helpers such as `otx2_get_txschq_rate_regval()`.

## Control Flow
`otx2_setup_tc()` dispatches `TC_SETUP_BLOCK` to ingress/egress clsact callbacks and `TC_SETUP_QDISC_HTB` to QoS. Flower replace allocates an `otx2_tc_flow`, validates supported dissector keys, fills an `npc_install_flow_req`, parses actions, assigns/reorders an MCAM entry by priority, and syncs it through the AF mailbox. Destroy reverses MCAM programming, CN10K policer mapping, multicast group allocation, and list membership. Stats read MCAM counters and update TC stats deltas. Matchall installs program scheduler rate or CN10K ingress policers directly.

## State and Persistence
Software state lives in `flow_cfg->flow_list_tc`, `flow_cfg->nr_flows`, `flow_cfg->mark_flows`, `nic->rq_bmap`, TC flags, and per-flow cached request/stats. Hardware state persists in NPC MCAM entries, MCAM counters, NIX multicast groups, CN10K leaf bandwidth profiles, and scheduler PIR registers until deleted or interface reset.

## Dependencies and Integration Points
The file depends on Linux flow dissector, `pkt_cls`, TC action APIs, AF mailbox alloc/sync helpers, CN10K policer helpers, representor metadata, QoS APIs, and netdev feature gating. Representor TC paths temporarily bind master `otx2_nic` fields to a representor's `flow_cfg` and `pcifunc`.

## Risks and Edge Cases
Only specific dissector keys and actions are supported; unsupported masks must fail cleanly. MCAM priority reordering deletes/reinstalls entries and must preserve counters. Ingress policing is CN10K-only and consumes RQs, with RQ 0 reserved. The mark-flow refcount clearing logic is sensitive because TC mark enablement affects RX skb marks. Multicast mirror group cleanup must run on all delete/error paths. Interface-down cases intentionally defer some ingress policer reprogramming.

## Test Signals
Exercise flower add/delete/stats for DMAC, VLAN/CVLAN, IPv4/IPv6, ports, TCP flags, MPLS, ICMP, IPsec SPI, mark, redirect, queue mapping, mirror, drop, and accept. Test matchall police on ingress/egress, unsupported key/action errors with extack text, MCAM exhaustion, rule priority ordering, interface down/up with stored ingress policers, CN10K vs OTX2 platform gating, and representor TC rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_tc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_txrx.c

## Purpose
`otx2_txrx.c` is the core RVU NIC packet data path. It polls CQEs through NAPI, builds SKBs from RX buffers, handles XDP and AF_XDP, completes TX, constructs SQEs for normal TX, TSO, timestamping, VLAN/checksum offload, CN10K IPsec, and drains/cleans queues during teardown.

## Important APIs, Types, and Functions
Exports include `otx2_napi_handler()`, `otx2_refill_pool_ptrs()`, `otx2_sq_append_skb()`, `otx2_cleanup_rx_cqes()`, `otx2_cleanup_tx_cqes()`, `otx2_rxtx_enable()`, `otx2_free_pending_sqe()`, `otx2_xdp_sqe_add_sg()`, `otx2_read_free_sqe()`, and `otx2_xdp_sq_append_pkt()`. Internal anchors include `otx2_rx_napi_handler()`, `otx2_tx_napi_handler()`, `otx2_rcv_pkt_handler()`, `otx2_snd_pkt_handler()`, `otx2_sqe_add_hdr/ext/sg/mem()`, and TSO/PTP helpers.

## Control Flow
NAPI walks up to four CQ types per interrupt context, polls RX and TX CQ tails, processes CQEs, returns CQEs to hardware, refills pools, and re-enables interrupts if the budget is not exhausted. RX validates parser errors, optionally runs XDP, builds skb frags from SG descriptors, sets hash/checksum/mark/timestamp metadata, and submits GRO frags. TX completion unmaps DMA, returns XDP frames or AF_XDP completions, handles PTP TX timestamps, completes netdev queues, and wakes stopped queues. TX submission checks SQE space, handles software TSO fallback, maps fragments, fills descriptors, appends timestamp memory ops if needed, and flushes through LMT.

## State and Persistence
Ring state lives in `otx2_snd_queue` producer/consumer indices and SG side arrays, CQ head/tail/pend counters, page pools, AF_XDP pools, and hardware aura/pool pointers. Packet lifetime state is tracked by DMA mappings in `sg_list`, skb/xdp frame pointers, timestamp scratch buffers, and CQE invalidation fields. Hardware RX/TX enablement persists through NIX mailbox messages.

## Dependencies and Integration Points
This file consumes descriptor definitions from `otx2_struct.h`, queue definitions from `otx2_txrx.h`, hardware operations from `otx2_common.h`, PTP helpers, CN10K IPsec, XDP/XSK APIs, page pool, GRO, net DIM, DMA/IOMMU translation, and NIX register access. VF, PF, QoS, representor, and XSK modules call its exported queue functions.

## Risks and Edge Cases
SQE space accounting and SG array limits control backpressure; bugs can corrupt rings or leak DMA mappings. RX error handling must free buffers only when packets are dropped. XDP paths differ for page-pool vs AF_XDP buffers and must update `pool_ptrs` accurately. PTP one-step timestamping rewrites packet payload and may need UDP checksum repair. Software TSO stores mappings on the first SQE while completion arrives on the last segment. Cleanup paths must not race live NAPI.

## Test Signals
Run TCP/UDP/IPv4/IPv6 traffic with checksum, VLAN, TSO/GSO UDP, XDP PASS/TX/DROP/REDIRECT, AF_XDP zero-copy TX/RX, PTP RX/TX and one-step sync, IPsec offload, representor mode, queue stop/wake, RXALL error delivery, MTU extremes, interface close while traffic is active, and net DIM/adaptive interrupt coalescing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_txrx.h

## Purpose
`otx2_txrx.h` declares the data-path queue model and packet-buffer sizing constants for the RVU NIC. It is the shared interface between queue setup, TX/RX processing, XDP/XSK, QoS send queues, and representor/VF data paths.

## Important APIs, Types, and Definitions
Constants describe channel bases, alignment/headroom, Ethernet/MTU limits, page-pool sizing, GSO/fragment limits, CQ interrupt thresholds, CQ status bits, and `OTX2_RX_MATCH_ID_MASK`. Data types include `queue_stats`, `otx2_rcv_queue`, `sg_list`, `otx2_snd_queue`, `cq_type`, `otx2_cq_poll`, `otx2_pool`, `otx2_cq_queue`, and `otx2_qset`. The inline `otx2_iova_to_phys()` abstracts IOMMU translation. Prototypes expose NAPI, TX append/flush, and pool refill functions.

## Control Flow
The header itself has only the IOVA translation inline. Its structures define control flow used by the implementation: CINTs map to up to RX, TX, XDP, and QoS CQs; CQ queues point to receive pools; SQs hold descriptor memory, LMT addresses, SG tracking, timestamp memory, optional IPsec queues, and XSK pools.

## State and Persistence
All queue state is runtime-only and tied to device open/resource allocation. Persistent state across packets includes SQ/CQ indices, queue memory pointers, page-pool and XSK pool associations, refill scheduling flags, and per-queue stats.

## Dependencies and Integration Points
The header includes kernel Ethernet, IOMMU, VLAN, XDP, and XSK APIs. It is included by `otx2_txrx.c`, `otx2_xsk.c`, `qos_sq.c`, `rep.h`, and common setup code that allocates or configures qsets.

## Risks and Edge Cases
The queue structures are cacheline-aligned and shared with hot paths, so field changes can affect performance and races. `OTX2_MAX_CQ_CNT` and `CQS_PER_CINT` constrain representor and QoS queue mapping. Buffer sizing macros must leave enough headroom for XDP metadata, skb shared info, timestamps, and MTU changes.

## Test Signals
Compile all users after structure changes. Runtime tests should validate queue counts, CINT-to-CQ mapping, RX buffer sizing for MTU and XDP limits, IOMMU and non-IOMMU DMA translation, XSK pool attachment, and per-queue stats under multi-queue traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_vf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_vf.c

## Purpose
`otx2_vf.c` is the PCI/netdev driver for OcteonTX2/CN10K RVU virtual functions, including regular VFs, LBK VFs, and SDP representor VFs. It owns VF probe/remove, mailbox setup with PF/AF, netdev operations, feature setup, queue/resource attachment, TC/QoS/devlink/XSK initialization, and reset/rx-mode work.

## Important APIs, Types, and Functions
The module registers `otx2vf_driver` for AFVF/VF/SDP IDs. Netdev ops include open/stop/xmit/select queue/rx mode/MAC/MTU/features/stats/timeout/TC/hwtstamp. Important helpers include `otx2vf_vfaf_mbox_init()`, `otx2vf_register_mbox_intr()`, mailbox work handlers, `otx2vf_probe()`, `otx2vf_remove()`, `otx2vf_xmit()`, `otx2vf_change_mtu()`, and `otx2vf_reset_task()`.

## Control Flow
Probe enables PCI, allocates netdev queues including QoS headroom, maps CSRs/mailbox, initializes hardware ops, verifies mailbox readiness, attaches NPA/NIX resources, reallocates MSI-X vectors, initializes LMT/PTP/MAC/features/IPsec, registers netdev, workqueues, MCAM/TC/devlink/XSK/DCB/QoS. Open delegates to common `otx2_open()` and forces carrier for LBK/SDP devices. TX validates length, calls `otx2_sq_append_skb()`, and stops/wakes queues based on SQB availability. Remove reverses pause/PFC, work, devlink, netdev, IPsec/PTP/MCAM/TC/QoS/resources/mailbox/IRQ/bitmap state.

## State and Persistence
Driver state lives in `struct otx2_nic` attached to the netdev: flags, mailbox, queue counts, LMT/IPsec/PTP/devlink resources, workqueues, TC and QoS state, XSK bitmap, and feature flags. Hardware mailbox state and attached LF resources persist until detach/remove.

## Dependencies and Integration Points
The file integrates with PCI, MSI-X, DMA/IOMMU, common RVU resource management, PF/AF mailbox protocol, CN10K ops, IPsec, PTP, ethtool, DCB, devlink, TC, QoS, and the TX/RX data path. It depends on `otx2_common.h`, `otx2_reg.h`, `otx2_ptp.h`, `cn10k.h`, and `cn10k_ipsec.h`.

## Risks and Edge Cases
Probe has many staged resources; unwind order must match allocation. VF mailbox mapping differs by OTX2/CN10K/CN20K platform. Queue count is based on online CPUs and QoS adds additional TX queues. MTU changes restart the device if up. Feature toggles must coordinate NTUPLE and TC offload. XSK bitmap allocation happens late and must be freed on all error/remove paths.

## Test Signals
Test VF bind/unbind on OTX2, CN10K, CN20K, LBK, and SDP IDs; mailbox deferral; netdev open/stop; TX queue busy recovery; MTU changes under traffic; rx mode changes; reset work; TC flower and HTB offloads; PTP/IPsec/DCB presence; XSK pool setup; and failure injection through probe unwind labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_xsk.c

## Purpose
`otx2_xsk.c` implements AF_XDP zero-copy support for RVU NIC queues. It maps user XSK pools for DMA, switches selected RX/TX queues into zero-copy operation, cleans/reinitializes receive queues, wakes NAPI, attaches pools to SQs, and pushes XSK TX descriptors into NIX send queues.

## Important APIs, Types, and Functions
Exports include `otx2_xsk_pool_setup()`, `otx2_xsk_pool_enable()`, `otx2_xsk_pool_disable()`, `otx2_xsk_pool_alloc_buf()`, `otx2_xsk_wakeup()`, `otx2_attach_xsk_buff()`, and `otx2_zc_napi_handler()`. Internal helpers include `otx2_xsk_ctx_disable()`, `otx2_clean_up_rq()`, and `otx2_xsk_sq_append_pkt()`.

## Control Flow
Pool enable validates queue bounds, DMA-maps the XSK pool, marks the zero-copy bitmap, drains and disables the old RQ context, reprograms RSS to remove the queue, and triggers NAPI wakeup. Disable detaches the SQ XSK pool, drains RQ state, clears the bitmap, unmaps DMA, and restores RSS participation. RX buffer allocation obtains `xdp_buff` objects from the XSK pool and stores them on the pool stack. TX NAPI peeks a batch of XSK TX descriptors, converts addresses to DMA, builds one-fragment SQEs, and flushes them.

## State and Persistence
State is kept in `pf->af_xdp_zc_qidx`, `otx2_pool->xsk_pool`, `otx2_pool->xdp[]/xdp_top`, and `otx2_snd_queue->xsk_pool`. Hardware RQ/aura/pool contexts are disabled and recreated around mode changes. DMA mappings persist while the pool is enabled.

## Dependencies and Integration Points
The file depends on XDP socket driver APIs, NIX/NPA mailbox helpers, RSS table programming, RX/TX cleanup in `otx2_txrx.c`, SQE descriptor helpers, and queue state from `otx2_txrx.h`. `otx2_txrx.c` calls `otx2_zc_napi_handler()` during TX completion/idle and treats AF_XDP frames specially on completion.

## Risks and Edge Cases
Queue IDs must be valid for both RX and TX. Mode switching while the interface is down is rejected or short-circuited. RSS must be updated so zero-copy RX queues are not used by normal traffic. XSK address alignment adjusts `xdp->data`; mistakes can corrupt packet data. A possible typo in non-CN10K RQ disable writes `rq_aq->sq.ena`/`sq_mask.ena` while `ctype` is RQ, which deserves platform-specific review.

## Test Signals
Run AF_XDP zero-copy bind/unbind, RX/TX traffic, need-wakeup behavior, queue wakeup with and without scheduled NAPI, RSS distribution before/after enable, interface-down setup errors, DMA map/unmap failure injection, and mixed XDP program actions on XSK-backed queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_xsk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_xsk.h

## Purpose
`otx2_xsk.h` declares the AF_XDP zero-copy interface used by RVU NIC setup and data-path code.

## Important APIs, Types, and Functions
The header forward-declares `struct otx2_nic` and `struct xsk_buff_pool`, then declares pool setup/enable/disable, zero-copy buffer allocation, netdev wakeup, zero-copy NAPI TX handling, and SQ pool attachment functions.

## Control Flow
There is no executable logic here. The declarations define the call graph: netdev/XSK setup calls `otx2_xsk_pool_setup()`, queue setup calls `otx2_attach_xsk_buff()`, RX refill calls `otx2_xsk_pool_alloc_buf()`, and TX completion/idle paths call `otx2_zc_napi_handler()`.

## State and Persistence
The header exposes no state directly; state resides in `otx2_nic`, queue pools, send queues, and XSK pool objects managed by `otx2_xsk.c` and `otx2_txrx.c`.

## Dependencies and Integration Points
It is included by `otx2_txrx.c` and the XSK implementation. It relies on netdev, DMA, and queue structures already visible to include sites through common driver headers.

## Risks and Edge Cases
Prototype changes require synchronized updates in TX/RX and netdev XSK call sites. Because `otx2_xsk_pool_alloc_buf()` references `struct otx2_pool` without a local forward declaration, include ordering must continue to provide that type.

## Test Signals
Compile tests with AF_XDP enabled and disabled configurations, plus runtime XSK bind/wakeup/TX/RX coverage, are sufficient signals for this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/otx2_xsk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos.c

## Purpose
`qos.c` implements TC HTB offload for RVU NIC transmit scheduling. It maintains a software QoS class tree, allocates NIX transmit scheduler queues, programs parent/topology/scheduling/shaping registers, manages extra QoS send queues, and maps class IDs to netdev TX queues.

## Important APIs, Types, and Functions
Public entry points are `otx2_setup_tc_htb()`, `otx2_get_txq_by_classid()`, `otx2_clean_qos_queues()`, and `otx2_qos_config_txschq()`. Important helpers allocate root/leaf nodes, validate priorities/quantum/DWRR, read/prepare/fill scheduler config, allocate/free txschq resources, push mailbox configuration, enable/disable SQs, delete leaves, and convert leaves to inner nodes.

## Control Flow
`otx2_setup_tc_htb()` dispatches HTB commands. Create allocates a root node and scheduler queue. Leaf allocation validates parent, priority, DWRR/static constraints, reserves a QoS qid, creates child scheduler chains down to MDQ, computes new scheduler allocation needs, applies hardware config, enables SQs if the netdev is up, updates real TX queue count, and rolls back on errors. Leaf-to-inner converts an existing leaf into an inner node and adds a child. Delete paths disable SQs, destroy node hardware/software state, compact qid usage, reset qdisc state, or collapse last child back to a leaf.

## State and Persistence
Software state lives in `pfvf->qos`: hash table, root tree, lock, qid-to-SMQ map, QoS SQ bitmap, major/default class, and link config level. Each node records class ID, scheduler level, qid, priority, rate/ceil, quantum, DWRR/static state, children, and allocated scheduler queue. Hardware state persists in NIX scheduler queues and SQ/aura/pool contexts until freed or interface teardown.

## Dependencies and Integration Points
The file depends on Linux TC HTB offload, NIX mailbox scheduler allocation/config, `otx2_tc.c` rate encoding, `qos_sq.c` SQ enable/disable, common queue/resource helpers, netdev real queue APIs, and qdisc reset internals.

## Risks and Edge Cases
Scheduler tree mutation has complex rollback; partial hardware allocation must be freed without losing the old tree. Only one DWRR group per parent is allowed. Static priority collisions and quantum limits differ by platform. VF roots start at TL2 while PF roots use TL1. Deleting a non-last QoS queue compacts qids and resets affected qdiscs. Interface-down configuration stores state for later hardware replay.

## Test Signals
Exercise all HTB commands: create/destroy, leaf alloc, leaf-to-inner, leaf delete, last leaf delete/force, query queue, invalid priorities/quantum, deep trees to MDQ limit, DWRR/static mixtures, PF vs VF roots, interface down/up replay through `otx2_qos_config_txschq()`, SQ flush through `otx2_clean_qos_queues()`, and traffic shaping accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos.h

## Purpose
`qos.h` defines the RVU NIC QoS/HTB data model and public helpers shared by TC, scheduler-tree, and QoS send-queue code.

## Important APIs, Types, and Definitions
Constants set maximum QoS levels, priorities, and leaf nodes. `enum qos_smq_operations` distinguishes SQ configuration from SMQ flush. Public prototypes cover scheduler rate encoding, HTB setup, QoS qid allocation/free, and QoS SQ enable/disable. `struct otx2_qos_cfg` carries requested/allocated scheduler queues and index bookkeeping. `struct otx2_qos` stores global QoS state. `struct otx2_qos_node` models each class/scheduler node.

## Control Flow
This header has no runtime control flow. It provides the state containers used by `qos.c` to construct and mutate HTB trees and by `qos_sq.c` to allocate/release SQ backing resources.

## State and Persistence
`otx2_qos` persists for the device lifetime and tracks the active tree, bitmap of QoS SQs, class hash table, and queue-to-SMQ mapping. `otx2_qos_node` instances persist while TC HTB classes exist.

## Dependencies and Integration Points
The header depends on Linux netdevice and rhashtable/list/bitmap support, NIX scheduler constants from common headers, and `struct otx2_nic`. It is included by `otx2_tc.c`, `qos.c`, and related common code.

## Risks and Edge Cases
Array sizes are bounded by `OTX2_QOS_MAX_LEAF_NODES` and `MAX_TXSCHQ_PER_FUNC`; mismatches with hardware queue counts can cause allocation failures. `qos_lock` protects child lists but readers using RCU/hash paths need matching lifetime discipline. Public constants duplicate a local define in `qos_sq.c`, so future changes should stay synchronized.

## Test Signals
Build coverage for QoS-enabled code, HTB tree mutation tests, queue bitmap exhaustion, class lookup by qid/classid, and lockdep under concurrent TC updates are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos_sq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos_sq.c

## Purpose
`qos_sq.c` manages the backing NPA/NIX resources for dynamically allocated QoS send queues. It allocates SQB aura/pool memory, initializes QoS SQs, disables contexts, drains pending descriptors, frees SQBs, and exposes qid allocation helpers for the HTB tree manager.

## Important APIs, Types, and Functions
Exports are `otx2_qos_get_qid()`, `otx2_qos_free_qid()`, `otx2_qos_enable_sq()`, and `otx2_qos_disable_sq()`. Key internals include `otx2_qos_sq_aura_pool_init()`, `otx2_qos_sq_free_sqbs()`, `otx2_qos_sqb_flush()`, `otx2_qos_ctx_disable()`, `otx2_qos_nix_npa_ndc_sync()`, and `otx2_qos_aura_pool_free()`.

## Control Flow
Enable derives the real SQ index from `hw->non_qos_queues + qidx`, locks the mailbox, initializes the NPA aura/pool and SQB buffers, then calls common SQ initialization. Disable validates that the queue is a live QoS queue, waits for SQB head/tail to settle, flushes SMQ, performs NIX/NPA NDC sync, cleans TX CQEs, disables SQ/aura/pool contexts by mailbox AQ writes, frees SQB pages and queue memory, and frees aura/pool qmem.

## State and Persistence
State spans the QoS SQ bitmap, `qid_to_sqmap`, SQB pointers/counts in `otx2_snd_queue`, NPA aura/pool contexts, SQ context, queue memory (`sqe`, `tso_hdrs`, `timestamps`), and CQ completion state. Resources persist only while a QoS class owns the qid and the interface is up.

## Dependencies and Integration Points
The file uses `otx2_txrx.h` queue structures, `otx2_struct.h` descriptor formats, NPA/NIX AQ mailbox helpers, common SQ initialization, SMQ flush helpers, DMA mapping/IOMMU translation, and `otx2_cleanup_tx_cqes()` from the data path. It is called by `qos.c`.

## Risks and Edge Cases
Mailbox lock coverage is split between callers and helpers; nested or missing locks can deadlock or race. Error unwind during SQB allocation must remove buffers from aura and unmap pages correctly. Disable returns early when interface is down because common teardown already freed SQs. The code verifies indices to avoid disabling non-QoS queues. CN10K LMTST uses a different AQ message type.

## Test Signals
Test repeated HTB class add/delete under traffic, QoS queue exhaustion, interface down while QoS queues exist, DMA allocation failure injection, CN10K and non-CN10K AQ paths, SQB leak checks, TX CQ cleanup correctness, and qid bitmap compaction after deletes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/qos_sq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/rep.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/rep.c

## Purpose
`rep.c` implements the RVU e-switch representor PCI driver. It exposes one netdev/devlink port per represented PF/VF, shares master RVU resources for TX/RX, relays events to PF/VF firmware, supports TC flower offload through the master MCAM path, and manages representor resources and lifecycle.

## Important APIs, Types, and Functions
Module entry uses `rvu_rep_driver`. Public functions are `rvu_rep_create()`, `rvu_rep_destroy()`, and `rvu_event_up_notify()`. Important helpers include `rvu_rep_mcam_flow_init()`, `rvu_rep_setup_tc()`, `rvu_rep_notify_pfvf()`, `rvu_rep_napi_init()`, `rvu_rep_rsrc_init/free()`, `rvu_get_rep_cnt()`, `rvu_rep_probe()`, and netdev ops open/stop/xmit/stats/MTU/offload stats/setup TC.

## Control Flow
Probe initializes RVU resources and asks firmware for representor count/map, then registers devlink. `rvu_rep_create()` initializes queues/resources, allocates netdevs, registers devlink ports and netdevs, sets NAPI/CQ IRQs, and enables e-switch mode. Representor TX validates length and uses master SQ `rep_id`. TC setup initializes per-representor MCAM flow state on demand, temporarily points master `otx2_nic` fields at representor context, then calls `otx2_setup_tc_cls_flower()`. Stats are fetched asynchronously by mailbox. Destroy disables e-switch, tears down CQs/NAPI/netdevs/devlink/resources.

## State and Persistence
Master `otx2_nic` stores representor count, PF map, shared qset, flags, and reps array. Each `rep_dev` stores netdev, stats, delayed stats work, devlink port, flow config, flags, rep ID, pcifunc, and MAC. Hardware e-switch state, MCAM entries, queue contexts, and firmware-visible representor events persist until destroy/remove.

## Dependencies and Integration Points
The file integrates with PCI, devlink port functions, TC flow blocks, RVU mailbox messages, common MCAM/queue resource helpers, `otx2_txrx.c`, `otx2_tc.c`, and representor events from PF/VF firmware.

## Risks and Edge Cases
`rvu_rep_mcam_flow_init()` allocates `flow_ent` but does not free it in the shown destroy path that only `kfree(rep->flow_cfg)`, so leak review is warranted. TC setup mutates shared master fields and must not race concurrent representor operations. `rvu_rep_state_evt_handler()` trusts `rvu_rep_get_repid()` result before indexing. Partial create unwind must unregister only successfully registered reps. Stats work scheduling after unregister needs cancellation discipline.

## Test Signals
Test representor probe/create/destroy/remove, firmware state events, devlink MAC get/set, MTU and port state notification, TX/RX traffic per representor, offload stats, TC flower add/delete/stats, MCAM allocation failure, e-switch enable/disable, IRQ/NAPI teardown under traffic, and leak detection for flow config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/rep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/rep.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/rep.h

## Purpose
`rep.h` declares the RVU representor driver's public types, PCI device ID, and lifecycle/event APIs.

## Important APIs, Types, and Definitions
It defines `PCI_DEVID_RVU_REP`, `struct rep_stats`, `struct rep_dev`, flag `RVU_REP_VF_INITIALIZED`, inline `otx2_rep_dev()`, and prototypes for `rvu_rep_create()`, `rvu_rep_destroy()`, and `rvu_event_up_notify()`.

## Control Flow
The only executable logic is `otx2_rep_dev()`, which identifies representor PCI devices by device ID. The prototypes connect common PF/devlink code and mailbox event handlers to `rep.c`.

## State and Persistence
`rep_dev` persists per representor netdev and tracks master device linkage, devlink port, flow configuration, stats work, VF init state, pcifunc, rep ID, and MAC. `rep_stats` stores cached counters and an atomic discard counter.

## Dependencies and Integration Points
The header includes PCI, RVU register, TX/RX, and common driver headers. It is consumed by `rep.c` and TC code that needs `struct rep_dev` for redirect/representor handling.

## Risks and Edge Cases
`OTX2_MAX_CQ_CNT` bounds representor count via queue capacity. The header exposes internals used across modules, so field changes can affect TC redirect and stats paths. `flow_cfg` ownership/lifetime must be clear because representor TC allocates it lazily.

## Test Signals
Compile representor-enabled builds, verify PCI ID matching, create maximum representor counts, and exercise TC redirect paths that cast target netdev private data to `rep_dev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/nic/rep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/Kconfig

## Purpose
`Kconfig` defines build-time configuration symbols for the Marvell Prestera switch ASIC driver and its PCI transport.

## Important APIs, Types, and Definitions
`CONFIG_PRESTERA` is a tristate switch ASIC driver depending on `NET_SWITCHDEV`, `VLAN_8021Q`, and either bridge support or bridge disabled, selecting `NET_DEVLINK` and `PHYLINK`. `CONFIG_PRESTERA_PCI` is a tristate PCI interface driver depending on `PCI`, `HAS_IOMEM`, and `PRESTERA`, defaulting to the base driver state.

## Control Flow
No runtime flow exists. The configuration controls which objects from the Prestera Makefile are built and whether the PCI transport module is available.

## State and Persistence
State is build configuration only. Module names exposed in help text are `prestera` and `prestera_pci`.

## Dependencies and Integration Points
This file integrates with the kernel Kconfig system and gates the source files in the same directory. The selected devlink/phylink dependencies match APIs used by `prestera.h` and implementation files.

## Risks and Edge Cases
Bridge dependency uses `depends on BRIDGE || BRIDGE=n`, allowing non-bridge builds while preventing incompatible modular combinations. Missing selected symbols would cause build failures across switchdev/devlink/phylink users.

## Test Signals
Build `PRESTERA=y/m/n`, `PRESTERA_PCI=y/m`, bridge built-in/module/disabled combinations, and minimal configs to verify dependency propagation and module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/Makefile

## Purpose
`Makefile` wires Prestera source files into the kernel build, defining the core `prestera` composite module and optional `prestera_pci` module.

## Important APIs, Types, and Definitions
`obj-$(CONFIG_PRESTERA) += prestera.o` builds the aggregate driver from main, hardware, DSA, RX/TX, devlink, ethtool, switchdev, ACL, flow, flower, span, counter, router, router hardware, and matchall objects. `obj-$(CONFIG_PRESTERA_PCI) += prestera_pci.o` builds the PCI transport.

## Control Flow
There is no runtime flow. Build flow links all `prestera-objs` into one module/object when `CONFIG_PRESTERA` is enabled.

## State and Persistence
The persistent effect is the object composition used by the kernel build system. It determines which implementation files share one module namespace and init/exit lifecycle.

## Dependencies and Integration Points
It depends on the Kconfig symbols from the adjacent `Kconfig`. ACL and counter files in this subset are part of the `prestera.o` aggregate and integrate with flow/flower/matchall/router files not in this work item.

## Risks and Edge Cases
Adding/removing objects changes module link coverage. Because many subsystems are linked into one aggregate, missing object entries can appear as unresolved symbols only for specific configs.

## Test Signals
Run kernel builds for built-in and module variants, verify `prestera_acl.o` and `prestera_counter.o` are included, and test `CONFIG_PRESTERA_PCI` independently follows `CONFIG_PRESTERA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera.h

## Purpose
`prestera.h` is the central public header for the Prestera switch driver. It defines core switch, port, device, event, interface, LAG, flood-domain, FDB/MDB, stats, phylink, router, and firmware abstractions plus cross-subsystem function declarations.

## Important APIs, Types, and Definitions
Major structures include `prestera_switch`, `prestera_device`, `prestera_port`, `prestera_lag`, port stats/caps/config/state, event payloads, `prestera_iface`, flood-domain/MDB types, and router state. Inline MMIO helpers `prestera_read()`/`prestera_write()` access PP registers. Prototypes cover device registration, port lookup/config, router init/fini, workqueue helpers, learning/flood/PVID/bridge lock, LAG lookup, MDB/flood-domain management, and netdev checks.

## Control Flow
The header provides only inline register access. Runtime flow is orchestrated by implementation files: the low-level device supplies `recv_pkt`, `recv_msg`, and `send_req`; the registered switch owns ports, event handlers, netdev notifier, devlink/trap/ACL/span/router/counter subsystems, and phylink state.

## State and Persistence
`prestera_switch` persists for the driver instance and aggregates global state. `prestera_port` persists per netdev and caches MAC/PHY config/state, VLANs, LAG membership, delayed stats, and phylink objects. Router, LAG, counter, ACL, and switchdev state are pointers managed by their subsystems.

## Dependencies and Integration Points
The header depends on notifier, skb/workqueue/phylink/devlink, Ethernet UAPI, and many forward-declared Prestera subsystems. It is included broadly by hardware, flow, ACL, counter, router, switchdev, and PCI/device files.

## Risks and Edge Cases
Because it is a wide shared contract, structure layout changes can affect many object files. Locking expectations are embedded in comments such as `state_mac_lock` and port list `rwlock_t`; users must respect them. Workqueue helpers imply deferred operations that need drain ordering at unload.

## Test Signals
Build all Prestera objects after any field/prototype change. Runtime signals include switch registration/unregistration, port discovery, phylink transitions, stats caching, LAG/VLAN/switchdev operations, router init/fini, and devlink/trap/ACL/counter interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_acl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_acl.c

## Purpose
`prestera_acl.c` implements Prestera ACL object management: flow-block rulesets, rule hashes, VTCAM allocation/reuse, hardware rule entries, counters, policers, jump chains, and port/index binding. It bridges higher-level flower/flow code to Prestera hardware VTCAM APIs.

## Important APIs, Types, and Functions
Public APIs include ACL init/fini, ruleset get/lookup/put/offload/bind/unbind/keymask/prio/index helpers, rule create/destroy/add/del/lookup/stats, rule entry find/create/destroy, VTCAM id get/put, PCL ID setup, and chain-to-counter-client mapping. Internal types are `prestera_acl`, `prestera_acl_ruleset`, `prestera_acl_rule_entry`, and `prestera_acl_vtcam`.

## Control Flow
Ruleset creation validates chain support, allocates a UID/PCL ID, initializes a rule hash, and inserts the ruleset hash. Offload obtains or creates a matching VTCAM and binds nonzero chains by interface index. Rule add inserts the rule by cookie, stamps PCL ID into the keymask, creates a hardware rule entry with actions, binds chain 0 to all block ports on first rule, links the rule, and updates priority range. Rule delete removes hash/list state, destroys hardware entry/actions, refreshes priority range, and unbinds the block when the last base-chain rule is gone.

## State and Persistence
`struct prestera_acl` owns ruleset/rule-entry rhashtables, VTCAM list, global rule list, and UID idr. Rulesets hold refcounts, keymask, VTCAM id, PCL id, chain/block key, offload state, rule count, and priority range. Rule entries own hardware id, action resources, counters, and policers until destroyed.

## Dependencies and Integration Points
The file depends on Linux rhashtable/idr/list/refcount, `prestera_hw` VTCAM/policer APIs, `prestera_counter`, `prestera_flow_block`, and structures in `prestera_acl.h`/`prestera.h`. Flower and matchall code provide rule arguments and keymasks.

## Risks and Edge Cases
VTCAM fallback can fit a keymask into an existing broader VTCAM when creation fails; this must preserve match semantics. Refcounts across rulesets, jump rulesets, VTCAMs, and counter blocks are critical. Error unwind must release policers/counters and remove hardware rules. Egress supports only chain 0; ingress chain masks are limited. `prestera_acl_ruleset_offload()` error path calls put with `ruleset->vtcam_id` before assignment after bind failure, which deserves review.

## Test Signals
Test ruleset create/lookup/refcount/put, chain limits, keymask sharing/fallback, rule add/delete with accept/drop/trap/jump/police/count, first/last port block bind/unbind, counter stats, duplicate cookies/entries, VTCAM destroy failures, policer creation failures, and ACL fini warnings for leaked rules/VTCAMs/UIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_acl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_acl.h

## Purpose
`prestera_acl.h` declares the Prestera ACL public API and wire-format-like match/action structures used by flower, flow-block, counter, and hardware layers.

## Important APIs, Types, and Definitions
It defines PCL ID masks/macros, rule-match setter macros, match type enum, action enum, ACL interface types, `prestera_acl_match`, action payloads, `prestera_acl_rule_entry_key`, `prestera_acl_hw_action_info`, flat `prestera_acl_rule_entry_arg`, `prestera_acl_rule`, and `prestera_acl_iface`. Prototypes cover ACL lifecycle, rule lifecycle, stats, rule entries, rulesets, keymask/PCL ID, VTCAM IDs, and chain-to-client mapping.

## Control Flow
There is no executable flow beyond macros that copy values into match arrays. The header defines how callers build keys/masks/actions before `prestera_acl.c` resolves them into hardware objects.

## State and Persistence
`prestera_acl_rule` persists per offloaded rule and links to its ruleset, optional jump ruleset, hardware rule entry, cookie, chain, priority, and flat creation arguments. Rule entry arguments are intentionally flat so object keys can be resolved before storage in internal entries.

## Dependencies and Integration Points
The header includes `prestera_counter.h` and forward-declares switch/ACL/flow-block types. It is used by Prestera flower/flow code, ACL implementation, hardware code, and counter integration.

## Risks and Edge Cases
Match arrays are indexed by enum values, so enum reordering changes ABI between software layers. PCL ID packs user ID and chain into 10 bits; chain/user ranges must stay within masks. The flat argument struct stores both validity bits and payloads, so callers must initialize it to zero before setting actions.

## Test Signals
Compile all ACL users, validate PCL ID construction for chain/user limits, add rules with each match/action type, test jump/police/count combinations, and run sparse/struct initialization checks for uninitialized validity bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_counter.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_counter.c

## Purpose
`prestera_counter.c` manages Prestera hardware counter blocks for ACL and related offloads. It allocates counter IDs from hardware blocks by client, polls counter blocks asynchronously in bulk, exposes packet/byte stats, clears counters on read/free, and releases hardware blocks when unused.

## Important APIs, Types, and Functions
Public APIs are `prestera_counter_init()`, `prestera_counter_fini()`, `prestera_counter_get()`, `prestera_counter_put()`, and `prestera_counter_stats_get()`. Internal structures are `prestera_counter` and `prestera_counter_block`. Helpers manage block list lookup/add/get/put, IDR allocation, refcounts, ready/invalid flags, and delayed work polling via `prestera_counter_stats_work()`.

## Control Flow
Initialization creates a manager, block list, mutex, and schedules delayed polling. Counter allocation finds a non-full block for the client or gets a new hardware block, then allocates a cyclic counter ID. If allocation occurs while the block is updating, the counter flag is marked invalid so stale in-flight stats are cleared before use. Poll work triggers a hardware block snapshot, reschedules after a short delay to fetch bulk chunks, stores stats, marks invalid counters ready after clearing them, rotates to the next block, and schedules the next poll. Stats get returns zero until ready, then returns and clears cached stats.

## State and Persistence
Manager state includes block array, current index, total read count, and fetch-in-progress flag. Block state includes hardware block id/offset/count/client, IDR of allocated counters, refcount, mutex, cached stats array, per-counter ready flags, updating/full booleans. Hardware counter blocks persist until `prestera_counter_block_put()` releases them.

## Dependencies and Integration Points
The file depends on Prestera hardware counter APIs (`block_get/release`, `trigger`, `counters_get`, `abort`, `clear`), delayed work, mutexes, IDR, refcounts, and `prestera_acl.c` count actions/stat reads.

## Risks and Edge Cases
Delayed polling is asynchronous and can race allocation/free without correct block locks and refcounts. `prestera_counter_block_put()` frees `stats` but the shown code does not free `counter_flag`, which looks like a memory leak. `prestera_counter_is_ready()` reads flags without locking. Abort paths reset manager fetch state and rotate blocks, so repeated hardware errors can stall fresh stats. Stats are cleared on every read, providing delta-like behavior.

## Test Signals
Test allocation/free across multiple clients, block exhaustion and new block creation, allocation during an active update, stats polling over more than 256 counters, hardware trigger/fetch/abort failures, concurrent stats_get/put, ACL count action integration, module unload with no live blocks, and leak detection for block arrays/flags/stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_counter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_counter.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_counter.h

## Purpose
`prestera_counter.h` declares the public counter manager API used by Prestera ACL and other offload subsystems.

## Important APIs, Types, and Definitions
It defines `struct prestera_counter_stats` with packet and byte counters, forward-declares switch/counter/block types, and declares init/fini, counter get/put, and stats get functions.

## Control Flow
No runtime flow exists in the header. Callers initialize the manager on switch setup, request counters by hardware client, attach returned block/id pairs to offloaded objects, read stats, and put counters during teardown.

## State and Persistence
The opaque `prestera_counter` persists on `prestera_switch`. `prestera_counter_block` and counter IDs are opaque handles whose lifecycle is controlled by get/put. Stats are returned as packet/byte snapshots from cached polling state.

## Dependencies and Integration Points
The header depends only on Linux integer types and is included by ACL interfaces and the counter implementation. `prestera_acl.h` embeds counter block pointers and counter IDs in ACL action state.

## Risks and Edge Cases
Because block internals are opaque, callers must not infer readiness or lifetime; they must call `prestera_counter_put()` exactly once for successful `get()`. Stats can be zero before a poll has populated a newly allocated counter.

## Test Signals
Compile ACL/count-action users, test get/put symmetry, stats reads before and after polling, and switch fini warnings when counters remain allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_counter.h -->
