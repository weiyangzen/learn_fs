# subset-b-004485 Research

Grouped research for Intel IDPF virtchnl, PTP virtchnl, virtchnl2 ABI, LAN descriptor ABI, and XDP support files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl.c

## Purpose
Implements the IDPF driver's virtchnl2 control-plane transport and most higher-level mailbox operations. It negotiates virtchnl version and device capabilities, initializes and tears down mailbox queues, creates and destroys vports, configures queues and vectors, manages RSS, statistics, MAC filters, promiscuous mode, loopback, SR-IOV VF count, flow steering rules, LAN MMIO mapping, RX ptype lookup tables, and RDMA auxiliary virtchnl forwarding.

## Important APIs, Types, And Functions
The core transport type is the private `struct idpf_vc_xn_manager`, which owns a fixed ring of `struct idpf_vc_xn` transactions, a free bitmap, a spinlock, and a salt byte used in reply cookies. `idpf_vc_xn_exec()` is the central synchronous/asynchronous transaction API. It allocates a transaction slot, installs send/receive buffers and optional async callback, sends through `idpf_send_mb_msg()`, waits for completion for synchronous calls, and maps final transaction state to byte count or `-errno`.

`idpf_send_mb_msg()` prepares a control-queue message, allocates a DMA mailbox payload buffer, embeds the virtchnl opcode and software cookie, optionally routes PTP opcodes to a secondary mailbox, and calls `idpf_ctlq_send()`. `idpf_recv_mb_msg()` drains receive mailbox entries, dispatches link events to `idpf_recv_event_msg()`, forwards replies to `idpf_vc_xn_forward_reply()`, and reposts DMA buffers with `idpf_ctlq_post_rx_buffs()`.

Initialization APIs include `idpf_init_dflt_mbx()`, `idpf_vc_core_init()`, and `idpf_vc_core_deinit()`. Vport and queue APIs include `idpf_send_create_vport_msg()`, `idpf_vport_init()`, `idpf_check_supported_desc_ids()`, `idpf_send_config_queues_msg()`, `idpf_send_enable_queues_msg()`, `idpf_send_disable_queues_msg()`, `idpf_send_add_queues_msg()`, `idpf_send_delete_queues_msg()`, `idpf_queue_reg_init()`, and `idpf_vport_queue_ids_init()`. Public feature helpers include `idpf_send_get_stats_msg()`, `idpf_send_get_set_rss_lut_msg()`, `idpf_send_get_set_rss_key_msg()`, `idpf_add_del_mac_filters()`, `idpf_set_promiscuous()`, `idpf_add_del_fsteer_filters()`, capability probes, and `idpf_idc_rdma_vc_send_sync()`.

## Control Flow
The mailbox lifecycle starts with `idpf_init_dflt_mbx()`, which creates TX/RX control queues and moves adapter state to version check. `idpf_vc_core_init()` initializes transaction slots, runs a small state machine for `VIRTCHNL2_OP_VERSION` and `VIRTCHNL2_OP_GET_CAPS`, maps LAN MMIO regions from `VIRTCHNL2_OP_GET_LAN_MEMORY_REGIONS` or a BAR fallback, allocates vport arrays and parameter buffers, starts mailbox/service work, requests interrupts, fetches RX ptypes, initializes PTP, initializes available queue counters, and queues vport init work.

Most virtchnl operations follow a repeated pattern: fill a little-endian `virtchnl2_*` request, set `struct idpf_vc_xn_params`, call `idpf_vc_xn_exec()`, validate reply length with fixed `sizeof()` or `struct_size()`, convert little-endian fields into driver state, and return zero or a negative error. Queue configuration uses `idpf_send_chunked_msg()` to split flexible-array queue payloads so mailbox buffers do not exceed `IDPF_CTLQ_MAX_BUF_LEN`. Queue enable/disable operations can target a whole vport or a selected `idpf_queue_set`; disable waits for software marker completion so datapath drain is observable.

Reply flow is cookie based. The outgoing cookie encodes transaction index and salt. `idpf_vc_xn_forward_reply()` validates index, salt, opcode, and mailbox return value before copying bounded reply bytes and completing a waiter, or before invoking an async handler for `IDPF_VC_XN_ASYNC`. Link events are not matched to a transaction; `idpf_handle_event_link()` updates cached link speed/status and netdev carrier/Tx queues if the vport is up.

## State And Persistence
Persistent driver state updated here includes adapter capabilities, virtchnl version, LAN register mappings, requested vector chunks, vport parameter request/response buffers, vport IDs, vport queue register chunks, queue IDs, tail register virtual addresses, RSS LUT/key buffers, ptype lookup tables, available queue counters, link state, netdev statistics, MAC filter list flags, PTP initialization state, and transaction ring state. Concurrency controls include transaction spinlocks, transaction manager bitmap lock, `queue_lock`, `stats_lock`, MAC filter list spinlocks, completions, delayed work queues, and reset/remove flags. No filesystem state is written; persistence is kernel-resident driver state and hardware/control-plane configuration.

## Dependencies And Integration Points
The file depends on the IDPF core structures in `idpf.h`, the virtchnl2 ABI in `virtchnl2.h` and descriptor IDs, control queue APIs, Linux PCI/DMA/netdev primitives, libeth RX ptype helpers, PTP support, SR-IOV PCI helpers, and RDMA IDC integration. It integrates tightly with netdev carrier and statistics, ethtool flow steering/RSS operations, queue allocation and interrupt resource code, XDP queue flags through `idpf_queue_has(XDP)`, PTP secondary mailbox routing, and reset/remove workqueue flows.

## Risks
Cookie/salt handling is central to correctness; stale or mismatched replies are dropped, and timeout paths reuse slots after returning them to the free bitmap. Async transactions require non-stack receive storage if a handler needs persistent context, as noted in the header. Flexible-array reply validation is critical: several paths guard with `struct_size()` and `IDPF_CTLQ_MAX_BUF_LEN`, and regressions can cause overreads or truncated configuration. Queue accounting must match split/single queue model assumptions, especially for XDP Tx queues, completion queues, buffer queues, and NOIRQ vector use. `idpf_send_get_set_rss_lut_msg()` and RSS key handling depend on correct byte sizing of flexible arrays. Reset/remove paths must shut down transactions before mailbox teardown to avoid indefinite waits or register access after reset. MAC filter async failure handling removes filters from the driver's list but cannot fully recover CP-side uncertainty.

## Test Signals
Useful signals are successful probe through version/capability negotiation, absence of transaction timeouts in logs, correct carrier changes on link events, vport create/configure/enable/disable cycles for split and single queue builds, queue add/delete and vector alloc/dealloc under resets, ethtool RSS get/set and flow steering rules, MAC filter and promiscuous mode operations while rtnl is held, SR-IOV VF changes, PTP init behavior when caps are present or missing, RDMA auxiliary virtchnl round trips, and fault injection for short mailbox replies, invalid chunk counts, reset during `idpf_vc_xn_exec()`, and mailbox repost failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl.h

## Purpose
Declares the IDPF virtchnl2 transaction interface and mailbox/vport/queue feature APIs implemented by `idpf_virtchnl.c`. It is the shared contract used by IDPF core, queue, netdev, PTP, XDP, RDMA, RSS, MAC filter, and flow steering code to issue control-plane operations.

## Important APIs, Types, And Functions
`enum idpf_vc_xn_state` defines transaction lifecycle states: idle, waiting, completed success, completed failure, shutdown, and async. `struct idpf_vc_xn` stores the completion, lock, state, reply size and destination `kvec`, async callback, opcode, ring index, and salt. `struct idpf_vc_xn_params` is the caller-facing request descriptor for `idpf_vc_xn_exec()`, including send/receive buffers, timeout, async flag, callback, and opcode.

`struct idpf_queue_ptr` and `struct idpf_queue_set` provide a typed flexible-array container for selected queue operations. The header exposes queue-set allocation plus selected queue enable, disable, and config functions. It also declares the broader virtchnl control surface: default mailbox init/deinit, VC core init/deinit, mailbox send/receive, vport create/destroy/enable/disable/init/adjust, queue register and ID initialization, queue add/delete/config/enable/disable, vector allocation/mapping, max queue accounting, MAC filters, promiscuous mode, loopback, stats, SR-IOV, RSS key/LUT, descriptor support checks, capability checks, transaction shutdown, and RDMA synchronous send.

## Control Flow
This header has no runtime control flow, but it shapes call flow across the driver. Callers allocate or prepare driver objects, populate request-specific data, and call the declared virtchnl helpers. Replies are mediated through the transaction structures and mailbox receive loop. Queue operations can use whole-vport functions or construct a selected `idpf_queue_set` for partial operations such as XDP queue handling.

## State And Persistence
The header defines in-memory transaction and queue-selection state only. Transaction state is protected by spinlocks and completions; queue sets are temporary flexible objects that point to existing queue resources. The inline `idpf_vport_deinit_queue_reg_chunks()` frees persisted queue register chunk storage from vport config.

## Dependencies And Integration Points
It includes `virtchnl2.h` and forward-declares driver types from the IDPF core. It depends on Linux kernel primitives such as `struct completion`, `spinlock_t`, `struct kvec`, `struct ethtool_rx_flow_spec`, and network/PCI-facing types supplied by including code. It is included by `idpf_virtchnl.c`, PTP virtchnl code, XDP code, and other IDPF modules needing control-plane operations.

## Risks
This header exposes async callbacks with a documented lifetime hazard: async receive buffers cannot be stack-owned if a callback needs them after send context exits. The cookie masks assume an 8-bit transaction index and 8-bit salt; changing ring length or cookie packing must remain synchronized with reply decoding. The flexible `idpf_queue_set` API trusts callers to fill `num` entries with matching queue types and valid pointers before calling config/enable/disable helpers.

## Test Signals
Compile coverage is the primary signal because type declarations and prototypes must match implementation. Runtime signals come from exercising all declared flows: mailbox init/deinit, sync and async `idpf_vc_xn_exec()`, selected queue-set operations, vport lifecycle, RSS/MAC/promisc/stats APIs, and RDMA send callback. Static analysis should flag mismatched callback lifetimes, missing locks, and incorrect queue-set type unions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl_ptp.c

## Purpose
Implements PTP-specific virtchnl2 mailbox operations for IDPF. It negotiates PTP capabilities, fetches direct register offsets when direct access is supported, provides mailbox fallbacks for reading/setting/adjusting device clock time, obtains per-vport Tx timestamp latch capabilities, and asynchronously retrieves Tx timestamp latch values.

## Important APIs, Types, And Functions
`idpf_ptp_get_caps()` sends `VIRTCHNL2_OP_PTP_GET_CAPS`, records capability bits, base increment value, max adjustment, secondary mailbox peer information, and maps direct-access register offsets through `idpf_get_reg_addr()`. `idpf_ptp_get_dev_clk_time()`, `idpf_ptp_get_cross_time()`, `idpf_ptp_set_dev_clk_time()`, `idpf_ptp_adj_dev_clk_time()`, and `idpf_ptp_adj_dev_clk_fine()` are fixed-size mailbox wrappers around PTP clock operations.

`idpf_ptp_get_vport_tstamps_caps()` sends `VIRTCHNL2_OP_PTP_GET_VPORT_TX_TSTAMP_CAPS`, validates the flexible latch reply size, allocates `struct idpf_ptp_vport_tx_tstamp_caps`, creates free/in-use latch tracking lists, initializes locks and status entries, and stores direct latch offsets when applicable. `idpf_ptp_get_tx_tstamp()` builds an async request for in-use latch indexes. `idpf_ptp_get_tx_tstamp_async_handler()` matches returned latch indexes to tracked SKBs and calls `idpf_ptp_get_tstamp_value()` to extend timestamps and complete `skb_tstamp_tx()`.

## Control Flow
PTP capability negotiation happens after the main virtchnl core is initialized. The driver first asks for caps and decides direct versus mailbox access by calling `idpf_ptp_get_features_access()`. If direct access is enabled for a feature, the returned offsets are converted to MMIO addresses and stored; otherwise later clock operations use mailbox wrappers.

Per-vport timestamp setup is conditional on vport flags and PTP access modes. The latch caps request returns a variable number of latch entries. Each latch is represented by an allocated tracker object on a free list. During Tx timestamp collection, `idpf_ptp_get_tx_tstamp()` scans the in-use list, moves status entries from request to read-value state, sends latch indexes asynchronously, and the async handler later removes matching latches, timestamps and consumes SKBs, returns latch objects to the free list, and updates stats.

## State And Persistence
Adapter PTP state stores capability bits, increment and adjustment limits, secondary mailbox validity/peer IDs, and direct register addresses. Vport PTP state stores timestamp latch capabilities, free and in-use latch lists, latch status array, low-bit timestamp shift, SKB pointers, and timestamp counters. Locks include latch list spinlock and status spinlock. All state is in memory and must be released by the PTP teardown path outside this file.

## Dependencies And Integration Points
The file depends on `idpf_ptp.h`, `idpf_virtchnl.h`, the virtchnl2 PTP structs and opcodes, SKB timestamp APIs, list management, spinlocks, and the generic transaction API. It integrates with `idpf_virtchnl.c` through `idpf_vc_xn_exec()` and PTP mailbox routing, with netdev hardware timestamp reporting through `skb_tstamp_tx()`, and with direct MMIO clock access paths through populated register pointers.

## Risks
Reply size validation is strict for fixed messages and flexible latch arrays; mistakes can lead to invalid latch traversal. Latch state transitions must stay synchronized with list operations and SKB ownership, especially when async replies arrive late or not at all. `idpf_ptp_get_tx_tstamp()` can send an async message with zero latch entries if all status transitions fail; callers should tolerate a no-op reply. Secondary mailbox validity depends on the `0xffff` peer queue sentinel and must match the send path in `idpf_virtchnl.c`. Timestamp extension depends on cached PHC time elsewhere in the driver.

## Test Signals
Signals include PTP capability negotiation with direct-only, mailbox-only, mixed, and unsupported devices; correct register address setup; clock get/set/adjust returning exact message sizes; per-vport latch setup and teardown; Tx timestamp SKBs being completed once and consumed; stats increments; async error handling for invalid vport IDs, invalid latch indexes, short replies, and no available in-use latch; and behavior when secondary mailbox is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf_virtchnl_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/virtchnl2.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/virtchnl2.h

## Purpose
Defines the virtchnl2 wire ABI used between the IDPF data-plane driver and the device control plane. It assigns stable opcode, capability, queue, protocol, PTP, RSS, flow steering, and event constants, and declares the little-endian message structures exchanged over mailbox control queues.

## Important APIs, Types, And Structures
`enum virtchnl2_op` lists control-plane operations from version negotiation and capability exchange through vport lifecycle, queue configuration, vectors, RSS, SR-IOV, events, stats, PTP, LAN memory regions, and flow rules. Capability enums define checksum, segmentation, RSS/flow types, header split, RSC, other device features, PTP features, and sideband action types. Queue model/type enums describe single versus split queues and TX/RX/completion/buffer queue types.

Core message structs include `virtchnl2_version_info`, `virtchnl2_get_capabilities`, `virtchnl2_create_vport`, `virtchnl2_vport`, `virtchnl2_txq_info`, `virtchnl2_config_tx_queues`, `virtchnl2_rxq_info`, `virtchnl2_config_rx_queues`, `virtchnl2_add_queues`, `virtchnl2_vector_chunk(s)`, `virtchnl2_alloc_vectors`, RSS key/LUT/hash messages, `virtchnl2_get_ptype_info`, `virtchnl2_vport_stats`, `virtchnl2_event`, queue chunk and queue-vector map messages, loopback, MAC address list, promiscuous mode, PTP capability and timestamp messages, LAN memory region messages, and flow steering rule/action structures. `VIRTCHNL2_CHECK_STRUCT_LEN()` static assertions pin fixed struct sizes.

## Control Flow
This header has no executable control flow. It defines the protocol sequence consumed by `idpf_virtchnl.c`: negotiate version, request capabilities, create vports, configure and enable queues/vectors, and then perform feature operations such as RSS, stats, MAC filters, PTP, and flow steering. Flexible-array structures are sized by count fields and are typically sent in chunks when the payload can exceed a mailbox buffer.

## State And Persistence
The ABI describes serialized state owned by the control plane and cached by the driver: capabilities, vport IDs and flags, queue IDs and tail register chunks, vector IDs and register offsets, RSS tables and keys, packet type tables, PTP offsets/latches, LAN memory regions, and flow rule IDs/status. All multibyte fields use little-endian types because driver and control plane may run on platforms with different endianness. Existing enum values and struct layouts are persistent compatibility contracts and should not be renumbered or resized casually.

## Dependencies And Integration Points
The header includes Ethernet address definitions and uses Linux endian, bit, and flexible-array annotations. It is included by `idpf_virtchnl.h` and indirectly by the main IDPF control-plane implementation. It is paired with `virtchnl2_lan_desc.h` for descriptor ID values and with PTP, RSS, queue, and flow steering code that serializes these structs.

## Risks
ABI drift is the largest risk. Opcode values, enum values, struct sizes, padding, endian annotations, and flexible-array count semantics must remain compatible with firmware/control-plane implementations. Several comments note reserved values and mandatory protocol IDs; changing them can break negotiation or packet parsing. Flexible message structs need caller-side bounds checks against mailbox buffer size and reply size. Flow steering structures are large and bounded by maximum protocol headers, raw packet size, actions, and rule count; callers must ensure control-plane limits are respected.

## Test Signals
Compile-time `static_assert` checks catch fixed-size layout changes. Runtime signals include successful virtchnl version/capability negotiation, queue/vport/RSS/PTP/flow rule operations against real or emulated control planes, endian correctness tests on serialized buffers, short/oversized flexible-array reply rejection, and compatibility testing across firmware versions that implement virtchnl2 version 2.0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/virtchnl2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/virtchnl2_lan_desc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/virtchnl2_lan_desc.h

## Purpose
Defines virtchnl2 LAN transmit and receive descriptor identifiers, bit masks, and descriptor writeback formats used by the IDPF datapath. It is an ABI-style hardware descriptor contract for single queue and split queue receive paths and for selected transmit descriptor capabilities.

## Important APIs, Types, And Structures
`enum virtchnl2_tx_desc_ids` advertises supported TX descriptor profiles such as data, context, flex TSO context, flex L2 tag descriptors, flow scheduling, and descriptor-done. `enum virtchnl2_rx_desc_ids` and `enum virtchnl2_rx_desc_id_bitmasks` define base and flex RX descriptor IDs, including the shared profile ID for split queue and single queue flex NIC descriptors.

The header defines bit masks for splitq advanced flex descriptor fields, status/error sections, ptype, packet length, generation bit, buffer queue ID, header length, RSC, split header, timestamp valid bit, and base descriptor status/error fields. Descriptor structures include `virtchnl2_splitq_rx_buf_desc`, `virtchnl2_singleq_rx_buf_desc`, `virtchnl2_singleq_base_rx_desc`, `virtchnl2_rx_flex_desc_nic`, `virtchnl2_rx_flex_desc_adv_nic_3`, and the common `union virtchnl2_rx_desc`.

## Control Flow
This header has no executable control flow. Runtime code fills buffer descriptors before handing them to hardware and decodes writeback descriptors after hardware completion. XDP metadata and RX processing code read fields such as ptype, length, RSS hash, timestamp low/high bits, buffer ID, generation bit, and completion status using these layouts and masks.

## State And Persistence
Descriptor rings are DMA-visible state shared between driver and hardware. The structures describe on-ring memory layout and must match device writeback behavior exactly. Enum values and bit positions are persistent hardware/firmware ABI and cannot be renumbered without breaking descriptor negotiation and parsing.

## Dependencies And Integration Points
The header depends on Linux bit helpers. It is consumed by IDPF TX/RX code, XDP descriptor helpers in `xdp.h`, queue configuration in `idpf_virtchnl.c` through descriptor ID masks, checksum/RSS/timestamp extraction, and any datapath path that distinguishes single queue base/flex and split queue advanced descriptors.

## Risks
Bitfield interpretation bugs can corrupt packet length, completion status, RSS hash, buffer selection, timestamp validity, or checksum error handling. The split queue and single queue flex descriptors share RX descriptor ID 2, so callers must also use the negotiated queue model to choose the correct layout. Direct word access under `__LIBETH_WORD_ACCESS` assumes the descriptor struct layout and alignment match the optimized loads used elsewhere. Descriptor ABI changes require careful coordination with control-plane capability negotiation and hardware documentation.

## Test Signals
Signals include RX/TX traffic across single queue and split queue modes, checksum and RSS validation, timestamp metadata extraction, XDP receive metadata tests, ring wrap and generation-bit handling, base versus flex descriptor selection, compile-time structure size checks where present in consumers, and hardware/firmware interoperability tests for descriptor IDs advertised in vport creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/virtchnl2_lan_desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xdp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xdp.c

## Purpose
Implements IDPF XDP integration for split queue mode. It registers RX queue metadata with the kernel XDP core, manages dedicated XDP Tx queues, completes XDP transmissions through splitq completion queues, implements `ndo_xdp_xmit`, exposes XDP RX metadata operations for RSS hash and hardware timestamp, and handles XDP program/XSK pool setup through the netdev BPF hook.

## Important APIs, Types, And Functions
`idpf_xdp_rxq_info_init()`, `idpf_xdp_rxq_info_init_all()`, `idpf_xdp_rxq_info_deinit()`, and `idpf_xdp_rxq_info_deinit_all()` register or unregister `xdp_rxq_info` for each RX queue, attach page-pool or XSK memory models, and set splitq XDP SQ pointers. `idpf_xdp_copy_prog_to_rqs()` RCU-replaces RX queue BPF programs.

`idpf_xdpsqs_get()` converts a tail range of Tx queues into XDP SQs by assigning completion queues, clearing refill queues, setting XDP/NOIRQ flags, initializing libeth XDP SQ locks and timers, and setting thresholds. `idpf_xdpsqs_put()` reverses timer/lock state and clears flags. `idpf_xdpsq_poll()` parses 4-byte completion descriptors, `idpf_xdpsq_complete()` releases completed frames, and libeth macros generate bulk flush/xmit/timer helpers. `idpf_xdp_xmit()` is the netdev XDP transmit entry point. `idpf_xdp_set_features()` advertises metadata and XSK operations. `idpf_xdp()` handles `XDP_SETUP_PROG` and `XDP_SETUP_XSK_POOL`.

## Control Flow
RX queue setup iterates `idpf_q_vec_rsrc` groups with `idpf_rxq_for_each()`, selecting splitq or singleq queue arrays. For each RX queue, XDP RXQ info is registered against the netdev, queue index, NAPI ID, and optional XSK fragment size. Splitq queues also receive the vport's XDP SQ array and count so XDP redirect/transmit paths can find output queues.

When XDP is enabled, `idpf_xdpsqs_get()` prepares a dedicated set of Tx queues from `xdp_txq_offset` to `num_txq`. During transmit, libeth bulk helpers call `idpf_xdp_tx_prep()` to lock the XDP SQ and expose descriptor ring state, `idpf_xdp_tx_xmit()` from `xdp.h` fills descriptors, and `idpf_xdp_tx_finalize()` sets RS/tail/timer. Completion polling parses completion queue entries, releases XDP frame resources, decrements pending counters, and updates queue clean indices.

Program setup takes the fast path when removing, when netdev is not registered, or when enabling/disabling state does not change. Otherwise it stores the requested program in user config and initiates a soft reset with queue change so XDP SQ resources can be recalculated. XSK pool setup is delegated to `idpf_xsk_pool_setup()`.

## State And Persistence
State touched here includes per-RX `xdp_rxq_info`, RX queue `xdp_prog` RCU pointers, RX XSK memory model, RX page-pool attachment, RX queue pointers to XDP SQs, XDP Tx queue flags, timers, libeth locks, completion queue clean index and generation bit, Tx queue pending and xdp_tx counters, BPF program references in vport and user config, and netdev XDP feature flags. Program state persists in memory across vport reset through `cfg->user_config.xdp_prog`.

## Dependencies And Integration Points
The file depends on `idpf.h`, PTP helpers for RX timestamp extension, `idpf_virtchnl.h` for queue model state, `xdp.h`, `xsk.h`, Linux BPF/XDP APIs, libeth XDP helpers, page-pool/XSK memory models, NAPI IDs, and netdev feature advertising. It integrates with virtchnl queue configuration because XDP SQs are regular Tx queues flagged as XDP/NOIRQ and mapped through the queue/vector logic in `idpf_virtchnl.c`.

## Risks
XDP is restricted to split Tx queue mode; unsupported modes must return `-EOPNOTSUPP`. Queue accounting is sensitive: enabling XDP needs spare Tx queues, and failure to decrease regular SQs returns `-ENOSPC`. Completion parsing must correctly handle generation bits and ring wrap or frames can leak or be double-completed. BPF program references must be incremented, replaced under RCU, and released on old programs. XSK queues use a different memory model and must not detach page-pool state on deinit. Timestamp metadata depends on valid PTP queue flag and cached PHC time.

## Test Signals
Signals include loading/unloading XDP programs on up/down vports, soft reset success when XDP queue count changes, `ndo_xdp_xmit` success and `-ENETDOWN` when carrier/link is down, XDP redirect and TX completion under ring wrap, XSK pool setup, RX hash metadata returning `-ENODATA` when hash is absent, RX timestamp metadata with and without PTP valid bits, BPF reference leak checks, and traffic tests that verify regular Tx/Rx queues still work after XDP enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xdp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xdp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xdp.h

## Purpose
Declares IDPF XDP entry points and provides inline descriptor helpers for XDP transmit finalization and advanced RX descriptor metadata extraction. It bridges IDPF descriptor formats from `idpf_txrx.h` and `virtchnl2_lan_desc.h` with generic libeth XDP helpers.

## Important APIs, Types, And Functions
The header declares RXQ registration/deinit helpers, BPF program propagation, XDP SQ allocation/free, XDP SQ completion polling, bulk Tx flush, `idpf_xdp_set_features()`, netdev BPF setup `idpf_xdp()`, and `idpf_xdp_xmit()`. `idpf_xdp_tx_xmit()` writes one hardware flex Tx descriptor from a libeth XDP descriptor, setting descriptor type, EOP, optional checksum offload, DMA address, and length.

`idpf_xdpsq_set_rs()`, `idpf_xdpsq_update_tail()`, and `idpf_xdp_tx_finalize()` set the report-status bit, perform a DMA write barrier, update the hardware tail register, and queue cleanup timer when a batch needs flushing. `struct idpf_xdp_rx_desc` normalizes selected fields from `virtchnl2_rx_flex_desc_adv_nic_3`. Accessor macros expose buffer queue ID, generation bit, length, ptype, buffer ID, EOP, RSS hash, and timestamp low/high fields. `idpf_xdp_get_qw0()` through `idpf_xdp_get_qw3()` load descriptor qwords either by direct word access or by endian-safe field assembly.

## Control Flow
The inline Tx path is called from generated libeth bulk-flush helpers in `xdp.c`: prepare a queue, fill descriptors for frames, then finalize by setting RS and ringing the tail if requested or when the queue is near full. The RX metadata path in `xdp.c` calls the qword extraction helpers lazily, only reading the descriptor qwords needed for hash or timestamp operations.

## State And Persistence
The header manipulates hardware-visible Tx descriptors, queue `next_to_use`, pending count, tail MMIO register, and cleanup timer scheduling. RX descriptor helpers are read-only normalizers over DMA writeback descriptors. It does not own persistent state beyond inline updates to queue rings and locks supplied by callers.

## Dependencies And Integration Points
It includes `net/libeth/xdp.h` and `idpf_txrx.h`, and uses descriptor constants and structures from the IDPF Tx/Rx stack. It integrates with `xdp.c`, libeth XDP bulk APIs, IDPF queue flags and tail registers, virtchnl2 advanced RX descriptor layout, XSK metadata paths, and PTP/RSS metadata consumers.

## Risks
Descriptor packing must match hardware layout for both `__LIBETH_WORD_ACCESS` and portable endian-safe paths. Missing the DMA write barrier before tail update can expose incomplete descriptors to hardware. `idpf_xdp_tx_finalize()` has subtle flush conditions: it avoids unnecessary tail writes unless a flush is requested, frames were sent, or the queue is effectively full. RX descriptor field masks must stay synchronized with `virtchnl2_lan_desc.h`; otherwise hash, ptype, timestamp, or length metadata will be wrong.

## Test Signals
Signals include XDP transmit descriptor inspection under checksum and multi-frame flags, queue tail updates after flush, completion timer scheduling, descriptor qword extraction on little-endian and non-word-access builds, RX hash and timestamp metadata tests, static assertions for RX descriptor size, and ring boundary tests where `next_to_use` wraps to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xdp.h -->
