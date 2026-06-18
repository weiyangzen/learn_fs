# subset-b-004462 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_virtchnl_pf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_virtchnl_pf.c

Purpose: this is the i40e PF-side SR-IOV and virtchnl implementation. It owns VF lifecycle, VF resource allocation, PF-to-VF notifications, mailbox request dispatch, queue/interrupt programming, MAC/VLAN/RSS/promiscuous settings, RDMA queue-vector routing, ADq queue channels, cloud filters, and the PF netdev `ndo_*` VF administration hooks.

Important APIs and functions: exported entry points include `i40e_alloc_vfs`, `i40e_free_vfs`, `i40e_pci_sriov_configure`, `i40e_vc_process_vf_msg`, `i40e_vc_process_vflr_event`, `i40e_vc_reset_vf`, `i40e_reset_vf`, `i40e_reset_all_vfs`, link/reset notification helpers, and VF netlink handlers such as `i40e_ndo_set_vf_mac`, `i40e_ndo_set_vf_port_vlan`, `i40e_ndo_set_vf_bw`, `i40e_ndo_set_vf_link_state`, `i40e_ndo_set_vf_spoofchk`, `i40e_ndo_set_vf_trust`, and `i40e_get_vf_stats`. Internal validators (`i40e_vc_isvalid_vsi_id`, queue/vector checks, `i40e_check_vf_permission`, `i40e_validate_cloud_filter`) are security-critical because mailbox input is guest-controlled.

Control flow: SR-IOV enable allocates `struct i40e_vf` records, seeds default caps/state, then resets all VFs so `i40e_alloc_vf_res` creates each VF VSI. VF mailbox handling first converts absolute VF id to local index, rejects disabled/out-of-range VFs, validates the virtchnl payload with `virtchnl_vc_validate_vf_msg`, then dispatches by opcode. Most handlers synchronize against reset-visible state, validate VF-owned VSI/queue ids, program HMC/register/AQ state, and reply through `i40e_vc_send_resp_to_vf`. Reset flow clears active/init state, triggers VFR or handles VFLR, waits for hardware completion, stops rings, frees/reallocates VSI resources, remaps queues, re-enables the VF, and writes `VIRTCHNL_VFR_VFACTIVE`.

State and persistence: VF configuration is stored in `struct i40e_vf` fields such as `default_lan_addr`, `port_vlan_id`, `pf_set_mac`, `trusted`, `spoofchk`, `tx_rate`, `link_forced`, `link_up`, `num_req_queues`, `adq_enabled`, per-channel VSI ids/rates, cloud filter list, and RDMA qvlist. MAC, port VLAN, trust, spoof check, rate limit, requested queues, ADq state, and forced link state survive VF reset because reset rebuilds hardware from these cached fields. Runtime state uses `vf_states` bits and PF global bits such as `__I40E_VIRTCHNL_OP_PENDING`, `__I40E_VF_DISABLE`, and `__I40E_VFS_RELEASING`.

Dependencies and integration: the file depends on `i40e.h`, LAN HMC helpers, AQ commands, virtchnl structures, PCI SR-IOV APIs, netdevice VF ops, VSI filter management, RSS helpers, ring control, and iWARP/RDMA client callbacks. It is the PF counterpart to VF drivers such as iavf: resource negotiation, queue setup, VLAN/MAC filtering, RSS, and reset events all cross the virtchnl mailbox boundary.

Risks: guest-controlled messages can request invalid DMA rings, queue maps, filters, or capability combinations, so all length/range/state checks are important. Reset paths are concurrency-sensitive; the code relies on state bits and waits to avoid accessing freed VSI/queue memory. Filter accounting and trusted-VF limits protect shared hardware MAC/VLAN resources. ADq/cloud-filter handling has many field/mask combinations and must avoid leaking filters across trust changes or channel teardown. Test signals include SR-IOV enable/disable, VF reset/VFLR storms, mailbox fuzzing, MAC/VLAN add/delete limits, port VLAN reset persistence, VF trust transitions, ADq channel add/delete with cloud filters, forced link state, queue resize requests, RSS configuration, and VF stats correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_virtchnl_pf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_virtchnl_pf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_virtchnl_pf.h

Purpose: this header defines the PF-side VF data model and exported SR-IOV/virtchnl interfaces for the i40e driver. It is the contract used by `i40e_virtchnl_pf.c` and other PF modules that need to reset VFs, process mailbox messages, publish VF netdevice operations, or notify VFs of link/reset changes.

Important APIs/types: it declares `enum i40e_vf_states`, `enum i40e_vf_capabilities`, `enum i40e_queue_ctrl`, `struct i40evf_channel`, `struct i40e_mdd_vf_events`, and `struct i40e_vf`. `struct i40e_vf` holds the PF pointer, VF id, virtchnl API version, driver capability mask, default MAC, port VLAN, trust/spoof/link/rate settings, VSI ids, queue counts, malicious-driver-detection counters, state/capability bitmaps, ADq channel state, cloud filter list, and RDMA queue-vector list. Function declarations expose SR-IOV allocation/free/configure, mailbox processing, VFLR processing, VF reset, link/reset notifications, netlink VF administration hooks, MSI restore, and stats collection.

Control flow and state: this header centralizes the state bits that gate virtchnl handling: `INIT`, `ACTIVE`, `RDMAENA`, `DISABLED`, promiscuous bits, `PRE_ENABLE`, `RESETTING`, and `RESOURCES_LOADED`. The constants for VLAN ids, queue-type mapping, VLAN priority masks, promisc flags, and reset wait counts are used by validation and hardware programming in the C file.

Dependencies and integration: it includes Linux virtchnl and netdevice headers plus `i40e_type.h`. It integrates PF code with PCI SR-IOV, netdev VF callbacks, link notification paths, and i40e hardware type definitions.

Risks and test signals: correctness depends on bit numbers staying aligned with code that uses `test_bit`/`set_bit`, and on cached VF fields being complete enough to rebuild VFs after reset. Tests should cover compile-time API consumers, VF reset state transitions, ADq channel array bounds, port VLAN priority extraction, and netdev VF handler availability under `CONFIG_PCI_IOV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_virtchnl_pf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_xsk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_xsk.c

Purpose: this file implements i40e AF_XDP zero-copy support. It associates XSK buffer pools with queue ids, switches Rx software rings between normal buffers and XDP buffers, runs XDP programs on zero-copy Rx buffers, converts passed packets to SKBs, transmits AF_XDP Tx descriptors through XDP Tx rings, completes XDP/AF_XDP frames, and implements `ndo_xsk_wakeup`.

Important APIs/functions: exported functions are `i40e_xsk_pool_setup`, `i40e_realloc_rx_bi_zc`, `i40e_clear_rx_bi_zc`, `i40e_alloc_rx_buffers_zc`, `i40e_clean_rx_irq_zc`, `i40e_clean_xdp_tx_irq`, `i40e_xsk_wakeup`, `i40e_xsk_clean_rx_ring`, `i40e_xsk_clean_tx_ring`, and `i40e_xsk_any_rx_ring_enabled`. Internals include `i40e_xsk_pool_enable/disable`, `i40e_run_xdp_zc`, `i40e_construct_skb_zc`, `i40e_handle_xdp_result_zc`, `i40e_xmit_zc`, and batch Tx descriptor filling.

Control flow: pool enable validates the VSI is main, qid is in real Rx/Tx ranges, maps the XSK pool for DMA, marks `af_xdp_zc_qps`, and if the interface is running disables the queue pair, reallocates Rx BI storage to `rx_bi_zc`, re-enables the queue, and wakes NAPI. Disable reverses the bit, DMA-unmaps the pool, and reallocates normal Rx BI storage. The Rx clean path consumes completed descriptors, handles programming-status descriptors, builds multi-buffer XDP frames, runs XDP, handles redirect/tx/drop/pass/exit results, replenishes XSK buffers, finalizes XDP Tx/redirect, updates stats, and maintains need-wakeup state. Tx path peeks AF_XDP descriptors, fills hardware descriptors in batches, sets RS on the last frame, updates tail/stats, and completes frames when hardware head advances.

State and persistence: persistent queue state lives in the VSI `af_xdp_zc_qps` bitmap, ring `xsk_pool`, `rx_bi_zc`, `next_to_use`, `next_to_clean`, `next_to_process`, and XDP Tx activity counters. DMA mappings are tied to pool enable/disable, not persisted across queue recreation.

Dependencies and integration: it integrates with `net/xdp_sock_drv.h`, XDP BPF APIs, NAPI/GRO, i40e Tx/Rx common helpers, queue-pair enable/disable routines, DMA sync helpers from XSK, and i40e interrupt writeback helpers. It is active only when XDP is enabled on the VSI.

Risks and test signals: risks include DMA mapping leaks on enable error paths, wrong software ring type during live queue transitions, multi-buffer fragment lifetime mistakes, need-wakeup stalls, descriptor wrap bugs, and mixing driver XDP_TX frames with AF_XDP Tx completions. Tests should exercise pool bind/unbind while up and down, Rx XDP_PASS/DROP/TX/REDIRECT/ABORTED, fragmented XDP buffers, Tx wraparound, need-wakeup behavior, queue disable cleanup, and `ndo_xsk_wakeup` error cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_xsk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_xsk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_xsk.h

Purpose: this header declares the i40e AF_XDP zero-copy entry points used by the main Tx/Rx, XDP, and netdev code. It also defines the Tx batch size used by `i40e_xsk.c`.

Important APIs/types: it forward-declares `struct i40e_ring`, `struct i40e_vsi`, `struct net_device`, and `struct xsk_buff_pool`; defines `PKTS_PER_BATCH` as 4 for unrolled AF_XDP Tx descriptor filling; and declares queue-pair enable/disable, pool setup, zero-copy Rx buffer allocation/cleaning, XDP Tx cleanup, wakeup, Rx BI reallocation, and zero-copy Rx BI clearing.

Control flow and state: callers use `i40e_xsk_pool_setup` from XSK pool bind/unbind paths, `i40e_clean_rx_irq_zc` and `i40e_clean_xdp_tx_irq` from NAPI paths, and cleanup helpers from queue teardown. The header does not store state itself, but its API assumes ring/VSI fields such as XSK pool pointers, zero-copy queue bitmaps, and descriptor indexes are maintained by the implementation.

Dependencies and integration: it depends only on Linux integer types and i40e/XSK forward declarations, keeping inclusion light for other driver modules. It bridges generic AF_XDP netdev callbacks with i40e-specific queue and descriptor handling.

Risks and test signals: API mismatch can break build integration across XDP, queue setup, and Rx/Tx files. `PKTS_PER_BATCH` is performance-sensitive and tied to an unroll pragma in the implementation. Test signals are compile coverage with XDP/XSK enabled, queue bind/unbind smoke tests, and NAPI cleanup paths invoking the declared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_xsk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/Makefile

Purpose: this Makefile wires the Intel Ethernet Adaptive Virtual Function driver into the kernel build. It builds the composite `iavf.o` object when `CONFIG_IAVF` is enabled.

Important build APIs: it adds `$(src)` to both `ccflags-y` and `subdir-ccflags-y`, then defines `iavf-y` as `iavf_main.o`, `iavf_ethtool.o`, `iavf_virtchnl.o`, `iavf_fdir.o`, `iavf_adv_rss.o`, `iavf_txrx.o`, `iavf_common.o`, and `iavf_adminq.o`. It conditionally adds `iavf_ptp.o` when `CONFIG_PTP_1588_CLOCK` is set.

Control flow and dependencies: build selection starts from Kconfig via `obj-$(CONFIG_IAVF) += iavf.o`; kbuild then links the listed objects into the driver. The file establishes that admin queue, common AQ helpers, virtchnl, Tx/Rx, ethtool, Flow Director, and advanced RSS are always part of the iavf module, while PTP is optional.

State and persistence: no runtime state is defined here, but the object list determines which features are compiled and therefore which symbols must remain consistent across source files.

Risks and test signals: missing objects cause unresolved symbols or feature absence; stale include paths can hide header dependency issues. Test signals are `CONFIG_IAVF=m/y` builds with and without `CONFIG_PTP_1588_CLOCK`, plus modpost symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf.h

Purpose: this is the main private header for the iavf VF driver. It defines driver-wide constants, adapter/VSI/q-vector state, filter tracking objects, capability macros, state-machine values, and cross-module function prototypes.

Important APIs/types: major types include `struct iavf_vsi`, `struct iavf_q_vector`, `struct iavf_mac_filter`, `struct iavf_vlan_filter`, `struct iavf_channel_config`, `struct iavf_cloud_filter`, and the central `struct iavf_adapter`. Enums define adapter lifecycle states (`__IAVF_STARTUP` through `__IAVF_RUNNING`), VLAN filter states, traffic-class state, cloud-filter state, and critical sections. Macros expose descriptor sizing, queue/vector limits, RSS capability choices (`RSS_PF`, `RSS_AQ`, `RSS_REG`), VLAN/CRC/TC/FDIR/advanced-RSS/QoS/RXDID/PTP capability checks, and AQ request bits.

Control flow: adapter initialization progresses through version negotiation, resource retrieval, extended capabilities, software setup, down/running states, reset, and communication failure. The `aq_required` bitmask queues virtchnl requests for the admin queue worker; `extended_caps` sequences newer capability negotiations. Prototypes connect main, virtchnl, Tx/Rx, ethtool, Flow Director, advanced RSS, VLAN, QoS, PTP, reset, and filter-management modules.

State and persistence: `struct iavf_adapter` holds workqueues, reset/admin/config workers, waitqueues, vectors, rings, MSI-X entries, netdev/PDI handles, hardware struct, current/last state, link state, negotiated PF version, VF resources, VLAN v2 caps, supported Rx descriptor ids, PTP data, current stats, RSS key/LUT/hash algorithm/hashcfg, ADq/cloud filters, Flow Director filters, and advanced RSS list. MAC/VLAN/cloud/FDIR/advanced-RSS list state is protected by spinlocks and later reconciled with PF responses.

Dependencies and integration: it includes core Linux networking, PCI, interrupt, workqueue, VLAN/IP/TCP/SCTP/IPv6, traffic-control, net shaper, virtchnl, iavf type, Tx/Rx, FDIR, advanced RSS, and PTP-related types. It is the common include for almost every iavf source file.

Risks and test signals: state enum ordering is significant for watchdog/reset logic. AQ and extended capability bits must stay synchronized with `iavf_virtchnl.c`. Filter state machines must handle PF rejection and reset replay. Tests should cover build coverage, PF version negotiation, reset recovery, capability-dependent VLAN/RSS/PTP/RXDID paths, MAC/VLAN list locking, FDIR/advanced-RSS limits, and state transition logging via `iavf_change_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq.c

Purpose: this file implements the VF Admin Queue ring machinery. It allocates and configures Admin Send Queue (ASQ) and Admin Receive Queue (ARQ) descriptor rings, posts DMA buffers, sends commands, polls/completes writebacks, cleans received events, and tears queues down.

Important APIs/functions: exported functions include `iavf_init_adminq`, `iavf_shutdown_adminq`, `iavf_asq_done`, `iavf_asq_send_command`, `iavf_fill_default_direct_cmd_desc`, and `iavf_clean_arq_element`. Internal helpers allocate/free ASQ/ARQ descriptor rings and per-descriptor DMA buffers, configure VF AdminQ registers (`IAVF_VF_ATQ*`, `IAVF_VF_ARQ*`), initialize/shutdown each queue, and clean ASQ completions.

Control flow: initialization validates queue depths and buffer sizes, sets ASQ timeout, initializes ASQ, then ARQ. Each queue allocates descriptor memory, allocates buffer-info arrays, allocates DMA buffers, initializes indexes, and writes base/length/tail registers. `iavf_asq_send_command` locks ASQ, validates the queue and head register, copies command details/cookies, checks indirect buffer size and async/postpone flags, reclaims completed descriptors, copies descriptor and optional indirect buffer to the ring, bumps tail unless postponed, optionally waits for firmware head advancement, copies writeback data/status, maps AdminQ return codes, saves optional writeback descriptors, and unlocks. ARQ cleaning locks ARQ, compares hardware head with next-to-clean, copies event descriptor/buffer to caller, reposts the DMA buffer, updates tail and indexes, and returns pending count.

State and persistence: all runtime state is in `hw->aq`: ASQ/ARQ ring memory, command-detail memory, DMA buffer arrays, descriptor counts, next indexes, queue mutexes, last AQ status, and timeout. Queue state is transient hardware/driver state rebuilt on reset or probe; nothing is persisted beyond the adapter lifetime.

Dependencies and integration: it depends on iavf register definitions, type/status headers, allocation helpers, `libie_aq_desc`, and `iavf_debug_aq`. Higher layers use this as the transport for PF mailbox messages and direct AQ operations such as RSS and shutdown.

Risks and test signals: risks include DMA allocation unwind leaks, descriptor wrap errors, deadlocks around ASQ/ARQ mutexes, timeouts when PF/FW stops processing, stale buffer length/address when reposting ARQ descriptors, and incorrect async/postpone behavior. Test signals include probe/remove cycles, reset reinitialization, AQ timeout injection, full queue handling, indirect buffer size rejection, ARQ event drain, and shutdown when ASQ is already dead.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq.h

Purpose: this header defines iavf Admin Queue data structures and helpers shared by AdminQ implementation and common AQ command wrappers.

Important APIs/types: it defines `IAVF_ADMINQ_DESC`, descriptor alignment, `struct iavf_adminq_ring`, `struct iavf_asq_cmd_details`, `IAVF_ADMINQ_DETAILS`, `struct iavf_arq_event_info`, and `struct iavf_adminq_info`. It declares `iavf_fill_default_direct_cmd_desc` and provides `iavf_aq_rc_to_posix` for converting firmware AQ return codes to Linux errno values. Constants include `IAVF_AQ_LARGE_BUF` and `IAVF_ASQ_CMD_TIMEOUT`.

Control flow and state: `iavf_adminq_info` embeds ASQ and ARQ rings, queue depths and buffer sizes, firmware/API version fields, ASQ/ARQ mutexes, and last status codes. `iavf_asq_cmd_details` controls optional callbacks, cookies, flag overrides, async/postpone behavior, and writeback descriptor capture. `iavf_arq_event_info` is the handoff object for received PF events.

Dependencies and integration: it includes OS dependency, status, and AdminQ command definition headers. It integrates the low-level ring implementation with higher-level common code and error reporting.

Risks and test signals: structure layout and descriptor macros must match ring memory allocated in `iavf_adminq.c`. Error conversion must stay aligned with `enum libie_aq_err`; invalid codes return `-ERANGE`, while AQ timeout maps to `-EAGAIN`. Tests should cover compile layout, timeout conversion, and ASQ command-detail behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq_cmd.h

Purpose: this header defines iavf Admin Queue opcode values and the command/response payload layouts used by software and firmware.

Important APIs/types: `enum iavf_admin_queue_opc` lists AQ opcodes for versioning, queue shutdown, resource ownership, capabilities, switch/VSI management, MAC/VLAN/cloud filters, scheduler bandwidth, PHY/link, NVM, virtualization mailbox (`send_msg_to_pf/vf/peer`), alternate structure, LLDP, tunnels/RSS, async events, OEM, and debug commands. The file defines compile-time structure-length checks, `struct iavf_aqc_queue_shutdown`, `struct iavf_aqc_vsi_properties_data`, `struct iavf_aqc_get_veb_parameters_completion`, link-speed bits/enums, `struct iavf_aqc_pf_vf_message`, RSS key command/data structures, and RSS LUT command layout.

Control flow: command wrappers fill a `libie_aq_desc`, overlay the appropriate 16-byte direct command structure through `libie_aq_raw`, optionally attach indirect buffers using address fields, and send through `iavf_asq_send_command`. Static length assertions enforce firmware ABI size expectations.

State and persistence: no runtime state is stored here. The header defines on-wire/hardware ABI constants; changing them affects PF/FW communication and persisted hardware programming semantics such as VSI properties, VLAN modes, queue mapping, RSS key/LUT, and mailbox cookies.

Dependencies and integration: it includes `linux/net/intel/libie/adminq.h` for the base AQ descriptor and shared flags. It is consumed by `iavf_adminq.h`, `iavf_adminq.c`, and `iavf_common.c`.

Risks and test signals: ABI drift is the primary risk. Incorrect opcode values, field masks, endian annotations, or structure sizes can break firmware/PF compatibility. Test signals are compile-time struct-length assertions, AdminQ smoke tests for shutdown/RSS/mailbox, PF version compatibility, and runtime AQ error codes when commands are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adv_rss.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adv_rss.c

Purpose: this file implements iavf advanced RSS ethtool support. It converts driver packet-header/hash-field selections into `virtchnl_rss_cfg` protocol-header messages that can be sent to the PF, searches configured RSS rules, and logs rule status.

Important APIs/functions: exported functions are `iavf_fill_adv_rss_cfg_msg`, `iavf_find_adv_rss_cfg_by_hdrs`, and `iavf_print_adv_rss_cfg`. Internal helpers fill virtchnl headers for IPv4, IPv6, TCP, UDP, SCTP, and GTP variants. Hash-field bitmasks drive calls to `VIRTCHNL_ADD_PROTO_HDR_FIELD_BIT`; packet header bits drive `VIRTCHNL_SET_PROTO_HDR_TYPE`.

Control flow: `iavf_fill_adv_rss_cfg_msg` chooses symmetric or asymmetric Toeplitz, sets tunnel level to outer layer, appends at most one L3 header, one L4 header, and optional GTP header(s), and rejects unsupported or ambiguous L3/L4/GTP combinations. GTP handling maps GTPC/GTPU forms to the proper virtchnl protocol header type; selected GTPU forms append an IPv4 header for destination-IP hashing. Lookup iterates `adapter->adv_rss_list_head` by `packet_hdrs`. Print builds a human-readable hash option string from packet header and hash field masks.

State and persistence: RSS rule state itself lives in `struct iavf_adv_rss` nodes on the adapter list and is declared in the header. This file populates the per-rule `cfg_msg` payload and reads rule fields for lookup/logging.

Dependencies and integration: it depends on `iavf.h`, virtchnl protocol header macros, adapter advanced-RSS list state, ethtool rule creation paths, and PF support for `VIRTCHNL_VF_OFFLOAD_ADV_RSS_PF`.

Risks and test signals: risks include exceeding virtchnl header count, accepting invalid combined L3/L4 masks, mismapping GTP tunnel variants, and `hash_opt` logging truncation or stale text if future fields exceed the static buffer. Tests should cover IPv4/IPv6 TCP/UDP/SCTP combinations, symmetric/asymmetric mode, invalid mixed L3/L4 masks, each GTP variant, duplicate header lookup, and PF accept/reject completion handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adv_rss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adv_rss.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adv_rss.h

Purpose: this header defines the iavf advanced RSS rule model, packet header masks, hash-field masks, and exported helper prototypes.

Important APIs/types: it defines `enum iavf_adv_rss_state_t` for add/delete request, pending, and active states; `enum iavf_adv_rss_flow_seg_hdr` for IPv4/IPv6, TCP/UDP/SCTP, and GTP control/user-plane variants; grouped masks for L3, L4, and GTP headers; `enum iavf_adv_rss_flow_field` and corresponding 64-bit hash-field masks; and `struct iavf_adv_rss` containing list linkage, packet headers, hash fields, symmetric flag, state, and the prepared `virtchnl_rss_cfg` message.

Control flow and state: ethtool paths allocate/update `struct iavf_adv_rss`, set state to request/pending/active as PF messages are sent and completed, and use the helper functions to build and find rules. The field enum explicitly notes that it must fit within 64 bits because hash masks are `u64`.

Dependencies and integration: the header forward-declares `struct iavf_adapter` and relies on virtchnl RSS configuration types through including contexts. It is included by `iavf.h`, making advanced RSS state part of the adapter.

Risks and test signals: adding fields beyond 64 bits would break mask representation. Header bit combinations must stay aligned with `iavf_adv_rss.c` parsing and PF virtchnl expectations. Tests should cover add/delete state transitions, duplicate packet header detection, mask construction, and compile coverage for all exported helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adv_rss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_alloc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_alloc.h

Purpose: this header declares the iavf memory allocation abstraction used by AdminQ and shared hardware-code layers.

Important APIs/types: it defines `enum iavf_memory_type` values for ARQ/ASQ/ATQ buffers and rings, page descriptors, backing pages, jumbo backing pages, and reserved memory. It declares `iavf_allocate_dma_mem`, `iavf_free_dma_mem`, `iavf_allocate_virt_mem`, and `iavf_free_virt_mem`.

Control flow and state: callers pass an `iavf_hw` pointer, destination memory descriptor, memory type, size, and alignment for DMA allocations. AdminQ uses these APIs to allocate descriptor rings and indirect command/event buffers, then frees them during queue shutdown or unwind.

Dependencies and integration: this file forward-declares `struct iavf_hw`; concrete memory descriptor types are supplied by included iavf type headers in callers. It abstracts OS allocation details away from common Intel hardware code.

Risks and test signals: allocation type values may be used for diagnostics or platform-specific behavior, so reordering can be risky. Tests should cover AdminQ allocation/unwind paths, DMA alignment, zero-size/oversize failures, and remove/reset cleanup with no leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_common.c

Purpose: this file provides common iavf hardware/AdminQ helpers: status stringification, AdminQ debug dumps, ASQ liveness checks, queue shutdown command, RSS LUT/key AQ commands, VF-to-PF virtchnl message sending, and parsing PF-provided VF resources into the hardware struct.

Important APIs/functions: exported functions include `iavf_stat_str`, `iavf_debug_aq`, `iavf_check_asq_alive`, `iavf_aq_queue_shutdown`, `iavf_aq_set_rss_lut`, `iavf_aq_set_rss_key`, `iavf_aq_send_msg_to_pf`, and `iavf_vf_parse_hw_config`. Internal helpers implement get/set RSS LUT/key command preparation.

Control flow: RSS helpers build AQ descriptors for get/set RSS LUT or key, mark them as indirect buffer commands with read flags, encode VSI id and table type using bitfield macros, and send through `iavf_asq_send_command`. `iavf_aq_send_msg_to_pf` builds the virtualization mailbox command, stores virtchnl opcode/status in descriptor cookies, marks indirect buffer flags when a payload exists, defaults to async send, and relies on AdminQ completion/event handling later. Resource parsing copies PF-reported queue/vector counts, DCB flag, and default MAC addresses from SR-IOV VSI resources into `hw`.

State and persistence: the file reads and updates `hw->aq.asq_last_status`, uses `hw->debug_mask`, writes `hw->err_str` for unknown status strings, and populates `hw->dev_caps` and `hw->mac` from PF resource messages. RSS key/LUT data is supplied by callers and programmed through PF/FW rather than stored here.

Dependencies and integration: it depends on virtchnl, bitfield helpers, iavf type/AdminQ/prototype headers, AdminQ command definitions, and `libie_aq_desc`. It is used by VF initialization, RSS configuration, shutdown/remove, and all VF-to-PF messaging paths.

Risks and test signals: debug dumps can expose command buffers in logs when masks are enabled. Async mailbox send means callers must handle later completion and PF communication failures. Resource parsing assumes at least one VSI resource and that SR-IOV VSI carries the permanent/default MAC. Tests should cover status-string mapping, AQ debug gated by mask, RSS key/LUT AQ command encoding, queue shutdown on unload, mailbox send with empty/large payloads, and parsing resource messages with multiple VSIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_devids.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_devids.h

Purpose: this header defines PCI device IDs recognized by the iavf VF driver.

Important APIs/types: it declares constants for `IAVF_DEV_ID_VF` (`0x154C`), `IAVF_DEV_ID_VF_HV` (`0x1571`), `IAVF_DEV_ID_ADAPTIVE_VF` (`0x1889`), and `IAVF_DEV_ID_X722_VF` (`0x37CD`).

Control flow and integration: PCI id tables in the driver use these constants to bind the iavf module to supported virtual-function devices. The IDs distinguish common Intel Ethernet VF variants, Hyper-V-facing VF, adaptive VF, and X722 VF.

State and persistence: no runtime state exists here; these are compile-time hardware binding constants.

Risks and test signals: wrong IDs can prevent probe or bind the driver to unsupported devices. Tests should cover modalias generation, PCI id table compile references, module autoloading, and probe on supported VF hardware or emulated PCI IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_devids.h -->
