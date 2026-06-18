# subset-b-006257 Research

Grouped research report for the NFC HCI, LLCP, and NCI source files in `sources/distributed-fs/ceph-client/net/nfc`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/command.c -->
# sources/distributed-fs/ceph-client/net/nfc/hci/command.c

Purpose: Implements public HCI command/event helper APIs on top of the local HCP transmit path. It converts gate-oriented operations into pipe-oriented HCP messages, provides synchronous command execution with wait queues, and manages administrative pipe operations such as create, open, close, delete, and clear-all.

Important APIs and functions: `nfc_hci_send_event`, `nfc_hci_send_cmd`, `nfc_hci_send_cmd_async`, `nfc_hci_set_param`, `nfc_hci_get_param`, `nfc_hci_disconnect_gate`, `nfc_hci_disconnect_all_gates`, and `nfc_hci_connect_gate` are exported entry points for HCI clients and drivers. Internally, `nfc_hci_execute_cmd` wraps `nfc_hci_hcp_message_tx` with an on-stack waiter, while `nfc_hci_execute_cb` stores the result skb or frees it on error.

Control flow: Callers address a gate; the file resolves `hdev->gate2pipe[gate]`, returns `-EADDRNOTAVAIL` for unmapped gates, and sends an HCP command/event through `nfc_hci_hcp_message_tx`. Synchronous commands enqueue a message and wait until the HCI core response path invokes the callback. Pipe connection first handles fixed admin/link-management pipes, otherwise creates a pipe on the admin pipe, opens it, and updates `hdev->pipes` plus `gate2pipe`.

State and persistence: The main persistent state is the in-memory gate-to-pipe table and pipe metadata on `struct nfc_hci_dev`. Session identity persistence is not implemented here, but this file is used by `core.c` session initialization to create or reset the active pipe topology.

Dependencies and integration points: Depends on `hci.h` HCP definitions, exported NFC HCI constants from `<net/nfc/hci.h>`, skb ownership rules, and the asynchronous completion machinery in `hcp.c`/`core.c`. Driver-specific gates are reached through the HCI device's configured gate table.

Risks: `nfc_hci_execute_cmd` waits without an explicit timeout in this function; timeout behavior depends on HCI core command timers firing the callback. `nfc_hci_create_pipe` trusts response layout after command success and should be exercised with malformed controller responses. `nfc_hci_clear_all_pipes` has a TODO for identity reference bytes, with a quirk for short clear commands.

Test signals: Mock an HCI device with a fake `nfc_hci_hcp_message_tx`/response path to verify sync completion, async callback forwarding, gate lookup failures, cleanup after open failure, and pipe table updates for fixed and dynamically created gates. Include controller error-code translation and short-clear quirk coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/command.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/core.c -->
# sources/distributed-fs/ceph-client/net/nfc/hci/core.c

Purpose: Provides the NFC HCI core: NFC device allocation/registration, LLC integration, HCP transmit and receive workers, command timeout handling, HCI session initialization, target discovery, NFC operation callbacks, and driver failure propagation.

Important APIs and functions: Exported functions include `nfc_hci_result_to_errno`, `nfc_hci_reset_pipes`, `nfc_hci_reset_pipes_per_host`, `nfc_hci_sak_to_protocol`, `nfc_hci_target_discovered`, `nfc_hci_allocate_device`, `nfc_hci_free_device`, `nfc_hci_register_device`, `nfc_hci_unregister_device`, `nfc_hci_driver_failure`, and `nfc_hci_recv_frame`. Core workers are `nfc_hci_msg_tx_work`, `nfc_hci_msg_rx_work`, and `nfc_hci_cmd_timeout`.

Control flow: Transmit work serializes queued `struct hci_msg` items, sends fragments through `nfc_llc_xmit_from_hci`, and holds one pending command until response or timeout. Receive flow enters from `nfc_hci_recv_frame`, passes through the selected LLC, reassembles HCP fragments in `nfc_hci_recv_from_llc`, dispatches responses immediately, and queues commands/events to `msg_rx_work`. NFC operations call driver hooks where available, with generic fallbacks for polling and transceive.

State and persistence: `struct nfc_hci_dev` stores pipe mappings, pending command, tx/rx queues, timers, work items, version fields, async callback state, quirks, init data, and shutdown state. Session initialization reads the admin session identity and either asks the driver to `load_session` or clears/reconnects all configured gates and stores a fresh identity.

Dependencies and integration points: Integrates with `net/nfc` device registration via `struct nfc_ops`, the HCI command helpers in `command.c`, HCP dispatch in `hcp.c`, LLC engines from `llc.c`, and optional driver callbacks in `struct nfc_hci_ops`. Reports discovered targets via `nfc_targets_found` and failures via `nfc_driver_failure`.

Risks: The command serialization path must avoid races among shutdown, timeout, response completion, and worker rescheduling. HCP fragment reassembly assumes fragment queue consistency and only reports allocation failure through driver failure. Target discovery uses controller-provided parameter lengths and can fail with `-EPROTO`; edge cases around multi-target status are still TODO.

Test signals: Use a fake LLC engine and fake NFC core device to validate command queue progression, response-before-timeout, timeout callback, shutdown cleanup, receive reassembly, event dispatch to driver hooks, session identity restore versus reset, and failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/hci.h -->
# sources/distributed-fs/ceph-client/net/nfc/hci/hci.h

Purpose: Defines local NFC HCI/HCP structures, constants, and internal function prototypes shared by HCI command, core, and HCP implementation files.

Important APIs and types: Key structures are `gate_pipe_map`, packed `hcp_message` and `hcp_packet`, `hcp_exec_waiter`, queued `hci_msg`, and packed admin pipe command/notification payloads. It exposes `nfc_hci_hcp_message_tx` and `nfc_hci_hcp_message_rx` to bridge command helpers and core dispatch.

Control flow: The header establishes HCP packet interpretation: packet header carries continuation/final state plus pipe; message header carries type and instruction. `HCP_HEADER`, `HCP_MSG_GET_TYPE`, and `HCP_MSG_GET_CMD` are used by transmit construction and receive dispatch.

State and persistence: No runtime state is stored here, but the declared data structures define how HCI messages persist while queued, fragmented, waiting for responses, and carrying callbacks.

Dependencies and integration points: Includes `<net/nfc/hci.h>` for public HCI constants and device definitions. Its constants must stay compatible with ETSI HCI framing and the HCI core's pipe table semantics.

Risks: Packed wire structs are cast over skb data, so callers must validate skb length before dereferencing. `NFC_HCI_FRAGMENT` is used with bit masking in both tx and rx paths; regressions here can break reassembly.

Test signals: Compile-time and unit-style skb tests should verify header packing/unpacking, packed struct sizes, and response/command/event type extraction for all HCP types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/hci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/hcp.c -->
# sources/distributed-fs/ceph-client/net/nfc/hci/hcp.c

Purpose: Implements HCP message transmit fragmentation and top-level receive dispatch for the HCI stack.

Important APIs and functions: `nfc_hci_hcp_message_tx` allocates `struct hci_msg`, fragments payloads according to `hdev->max_data_link_payload`, stores callbacks and completion delay, and queues the message for `core.c` transmit work. `nfc_hci_hcp_message_rx` dispatches completed HCP messages to response, command, or event handlers.

Control flow: Transmit prepends the HCP message header only in the first fragment, copies payload across fragments, sets the final-fragment bit on the last packet header, then appends the message to `hdev->msg_tx_queue` under `msg_tx_mutex`. Receive is a small type switch that calls `nfc_hci_resp_received`, `nfc_hci_cmd_received`, or `nfc_hci_event_received`.

State and persistence: Queued `struct hci_msg` owns an skb fragment queue, callback metadata, wait-response flag, and completion delay until the core tx/response path frees it.

Dependencies and integration points: Depends on `hci.h` wire definitions, `struct nfc_hci_dev` queue/mutex fields initialized in `core.c`, and downstream LLC transmission through the core tx worker.

Risks: Fragment sizing relies on `max_data_link_payload` being larger than the packet header; invalid driver configuration could underflow payload room. The `ptr` handling interleaves message header and payload bytes and should be regression-tested for zero-length and exact-boundary payloads. Shutdown detection happens after all fragments are allocated.

Test signals: Exercise zero payload commands, single-fragment payloads, multi-fragment payloads, allocation failure cleanup, shutdown rejection, final-fragment bit placement, and receive dispatch for all HCP message types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/hcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/llc.c -->
# sources/distributed-fs/ceph-client/net/nfc/hci/llc.c

Purpose: Manages pluggable HCI Link Layer Control engines and provides a uniform allocation/start/stop/rx/tx wrapper around NOP and SHDLC LLC implementations.

Important APIs and functions: `nfc_llc_init`, `nfc_llc_exit`, `nfc_llc_register`, `nfc_llc_allocate`, `nfc_llc_free`, `nfc_llc_start`, `nfc_llc_stop`, `nfc_llc_rcv_from_drv`, `nfc_llc_xmit_from_hci`, and `nfc_llc_get_data` are the main entry points. `nfc_llc_register` stores `struct nfc_llc_engine` records in a global list.

Control flow: Subsystem init registers the NOP engine and, conditionally, SHDLC. Allocation looks up an engine by name, allocates `struct nfc_llc`, calls the engine's `init`, stores rx headroom/tailroom, and returns a wrapper used by HCI core. Runtime calls are direct ops-table dispatches.

State and persistence: The global `llc_engines` list persists registered engines until `nfc_llc_exit`. Each allocated `struct nfc_llc` persists engine private state in `data` plus selected ops and rx head/tailroom.

Dependencies and integration points: Included by the HCI core allocation path. Engine names come from public `<net/nfc/llc.h>` constants and local `llc.h` ops.

Risks: The engine list is not protected by a lock; this is acceptable for init/exit-only registration but would be unsafe for dynamic runtime registration. Duplicate engine names are not rejected. Allocation returns NULL for unknown names without error detail.

Test signals: Validate init rollback if either engine registration fails, name lookup, allocation/deallocation paths, ops dispatch, duplicate-name behavior if registration becomes dynamic, and rx headroom propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/llc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/llc.h -->
# sources/distributed-fs/ceph-client/net/nfc/hci/llc.h

Purpose: Defines the internal LLC engine interface used by the HCI core to abstract different link-layer framing protocols.

Important APIs and types: `struct nfc_llc_ops` defines `init`, `deinit`, `start`, `stop`, `rcv_from_drv`, and `xmit_from_hci`. `struct nfc_llc_engine` records a registered engine name and ops. `struct nfc_llc` holds engine private data, ops, and receive headroom/tailroom. The header declares NOP and SHDLC registration functions.

Control flow: Engines implement the ops contract, `llc.c` registers engines and dispatches through this table, and the HCI core uses only the wrapper functions exported from `llc.c`.

State and persistence: No state is directly stored by the header, but its structures define the lifetime and ownership of engine private data.

Dependencies and integration points: Includes public NFC HCI and LLC headers and Linux skb types. The SHDLC registration declaration is compiled out to a no-op when `CONFIG_NFC_SHDLC` is disabled.

Risks: Engine callbacks receive raw skb ownership; each engine must consistently free or transfer skbs. The `init` callback returns a void pointer, so type safety for private data is entirely by convention.

Test signals: Build with and without `CONFIG_NFC_SHDLC`, verify ops signatures remain synchronized with all engines, and run ownership tests for tx/rx skb behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/llc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/llc_nop.c -->
# sources/distributed-fs/ceph-client/net/nfc/hci/llc_nop.c

Purpose: Implements the pass-through HCI LLC engine named `LLC_NOP_NAME`, used when no additional link-layer framing or connection management is needed.

Important APIs and functions: The local ops are `llc_nop_init`, `llc_nop_deinit`, `llc_nop_start`, `llc_nop_stop`, `llc_nop_rcv_from_drv`, and `llc_nop_xmit_from_hci`; `nfc_llc_nop_register` registers them with the LLC manager.

Control flow: Init records the HCI device, driver transmit callback, HCI receive callback, head/tailroom, and failure callback. Start and stop are no-ops. Receive forwards skbs directly to HCI with `rcv_to_hci`; transmit forwards skbs directly to the driver with `xmit_to_drv`.

State and persistence: A small `struct llc_nop` persists callback pointers and device context for the life of the LLC instance. RX headroom and tailroom are set to zero.

Dependencies and integration points: Used by `llc.c` and selected by name from HCI drivers. It integrates directly with HCI core callbacks and driver xmit callbacks.

Risks: There is no link supervision, retransmission, sequencing, or failure detection; any reliability must be provided by the underlying transport. The stored `llc_failure` callback is unused.

Test signals: Verify that rx and tx skbs are forwarded exactly once, start/stop return success, private state is freed, and HCI allocation receives zero rx head/tailroom for this engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/llc_nop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/llc_shdlc.c -->
# sources/distributed-fs/ceph-client/net/nfc/hci/llc_shdlc.c

Purpose: Implements the SHDLC HCI LLC engine, providing connection negotiation, sequencing, acknowledgements, receive ordering, retransmission, remote-not-ready handling, and failure callbacks for HCI transports that require SHDLC framing.

Important APIs and functions: Engine ops are `llc_shdlc_init`, `llc_shdlc_deinit`, `llc_shdlc_start`, `llc_shdlc_stop`, `llc_shdlc_rcv_from_drv`, and `llc_shdlc_xmit_from_hci`. Core protocol helpers include `llc_shdlc_connect`, `llc_shdlc_sm_work`, `llc_shdlc_rcv_i_frame`, `llc_shdlc_rcv_s_frame`, `llc_shdlc_rcv_u_frame`, `llc_shdlc_handle_send_queue`, `llc_shdlc_reset_t2`, and `llc_shdlc_requeue_ack_pending`.

Control flow: Start enters `SHDLC_CONNECTING`, sends RSET frames, waits on a connect wait queue, and transitions through negotiating/half-connected/connected based on UA/RSET reception. Runtime rx queues incoming frames and schedules the state-machine work item. Runtime tx queues HCI skbs; the state machine sends I-frames while window and remote-ready conditions allow, tracks sent frames in `ack_pending_q`, sends RR after T1, and retransmits after T2.

State and persistence: `struct llc_shdlc` stores state, hard fault, timers, wait queue, connect tries/result, negotiated window/SREJ support, send/receive sequence numbers (`ns`, `nr`, `dnr`), receive/send/ack-pending queues, remote-not-ready flag, tx head/tailroom, and callbacks. State persists only in memory for the active LLC instance.

Dependencies and integration points: Registered through `nfc_llc_register(LLC_SHDLC_NAME, ...)`, used by HCI core as an LLC engine. It calls driver `xmit_to_drv`, HCI `rcv_to_hci`, and `llc_failure` on hard faults.

Risks: This file is concurrency-sensitive because timers, rx callbacks, tx callers, and disconnect all converge on `sm_work` and `state_mutex`. Sequence comparisons use modulo-8 helpers and are easy to regress. Requeue/retransmit paths manipulate skb control fields and queues; ownership mistakes can leak or double-free skbs. Connect timeout is very short and retry behavior should match hardware expectations.

Test signals: Simulate RSET/UA negotiation, retry exhaustion, in-order and out-of-order I frames, RR/REJ/RNR handling, T1 ack generation, T2 retransmission, send-window saturation, disconnect cleanup, null-frame link death, and deinit with pending timers/queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/hci/llc_shdlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/llcp.h -->
# sources/distributed-fs/ceph-client/net/nfc/llcp.h

Purpose: Defines internal LLCP state, constants, local-device structures, socket structures, TLV/PDU constants, and cross-file function prototypes for the Linux NFC LLCP implementation.

Important APIs and types: Key types are `enum llcp_state`, `struct nfc_llcp_local`, `struct nfc_llcp_sock`, `struct nfc_llcp_sdp_tlv`, `struct llcp_sock_list`, and `struct nfc_llcp_ui_cb`. Constants define defaults and limits for LTO/RW/MIU, SAP ranges, LLCP versions, PDU types, TLV types, well-known SAPs, and DM reason codes.

Control flow: The header separates the implementation into socket management, TLV handling, command/PDU building, and core receive/transmit paths by declaring functions implemented in `llcp_core.c`, `llcp_commands.c`, and `llcp_sock.c`.

State and persistence: `struct nfc_llcp_local` persists per-NFC-device LLCP state: refcount, timers/work, tx/rx state, local and remote general bytes, remote link params, SAP bitmaps/counters, pending SDP requests, and socket lists. `struct nfc_llcp_sock` persists per-socket SAPs, service name, flow-control parameters, sequence numbers, queues, accept queue, and parent link.

Dependencies and integration points: Uses Linux networking sockets/skbs and NFC core types. Its prototypes are consumed by NFC device registration, DEP link callbacks, socket protocol registration, and generic netlink SDP result reporting.

Risks: Several fields are protected by different locks (`sdp_lock`, socket-list rwlocks, skb queue locks, socket locks), so users must respect locking boundaries. SAP range math and bitmap offsets are central to correctness and susceptible to off-by-one errors.

Test signals: Compile and runtime tests should cover structure initialization defaults, SAP range boundaries, TLV constants, sequence field extraction, and socket list locking assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/llcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/llcp_commands.c -->
# sources/distributed-fs/ceph-client/net/nfc/llcp_commands.c

Purpose: Builds and parses LLCP TLVs and constructs outbound LLCP PDUs for link management, connection setup, service discovery, connected I-frame data, unnumbered UI data, disconnect, DM, SYMM, CC, and RR.

Important APIs and functions: TLV APIs include `nfc_llcp_build_tlv`, `nfc_llcp_build_sdres_tlv`, `nfc_llcp_build_sdreq_tlv`, `nfc_llcp_free_sdp_tlv`, `nfc_llcp_free_sdp_tlv_list`, `nfc_llcp_parse_gb_tlv`, and `nfc_llcp_parse_connection_tlv`. PDU APIs include `nfc_llcp_send_disconnect`, `nfc_llcp_send_symm`, `nfc_llcp_send_connect`, `nfc_llcp_send_cc`, `nfc_llcp_send_snl_sdres`, `nfc_llcp_send_snl_sdreq`, `nfc_llcp_send_dm`, `nfc_llcp_send_i_frame`, `nfc_llcp_send_ui_frame`, and `nfc_llcp_send_rr`.

Control flow: Outbound connected setup builds MIUX/RW/service-name TLVs, allocates a PDU with `llcp_allocate_pdu`, and queues it on `local->tx_queue`. I-frame send copies the user message, fragments by remote MIU, queues per-socket PDUs, and calls `nfc_llcp_queue_i_frames` under the socket lock. UI frames bypass connected flow control and enqueue directly to the local tx queue after checking that the local object is still listed.

State and persistence: The file mutates remote parameters on `nfc_llcp_local` and `nfc_llcp_sock`, manages pending SDP request lists and timers, enqueues skbs onto local and socket tx queues, and stores UI source/destination SAPs in skb control data for recvmsg.

Dependencies and integration points: Depends on `llcp_core.c` for local lookup, raw socket mirroring, and I-frame scheduling; depends on `llcp_sock.c` for socket fields and user msg handling; uses `nfc_data_exchange` to send SYMM immediately.

Risks: TLV parsing does not fully validate that `offset + length + 2` stays within the array before each dereference. `nfc_llcp_build_sdreq_tlv` assumes `uri_len > 0` when checking the last byte. Fragmentation allocates a full temporary user buffer before splitting, which may be costly for large sends. Queue pressure checks depend on `remote_rw` being sane.

Test signals: Fuzz TLV arrays, test all fixed and variable TLV lengths, validate CONNECT/CC TLV composition, exercise I/UI fragmentation at MIU boundaries, force skb allocation failures, verify SDP timeout list handling, and ensure DM/RR queue ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/llcp_commands.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/llcp_core.c -->
# sources/distributed-fs/ceph-client/net/nfc/llcp_core.c

Purpose: Implements the LLCP link core: per-device local registration, SAP allocation, general-bytes negotiation, SYMM-driven tx/rx scheduling, PDU receive dispatch, connected-socket state transitions, SDP handling, raw socket mirroring, and MAC up/down integration.

Important APIs and functions: Public functions include `nfc_llcp_sock_link`, `nfc_llcp_sock_unlink`, `nfc_llcp_socket_remote_param_init`, `nfc_llcp_find_local`, `nfc_llcp_local_put`, `nfc_llcp_get_sdp_ssap`, `nfc_llcp_get_local_ssap`, `nfc_llcp_put_ssap`, `nfc_llcp_general_bytes`, `nfc_llcp_set_remote_gb`, `nfc_llcp_send_to_raw_sock`, `nfc_llcp_queue_i_frames`, `nfc_llcp_recv`, `nfc_llcp_data_received`, `nfc_llcp_mac_is_down`, `nfc_llcp_mac_is_up`, `nfc_llcp_register_device`, and `nfc_llcp_unregister_device`.

Control flow: The NFC core registers a local object per device. MAC up starts initiator tx work or target link timer. TX work sends one queued PDU or a SYMM keepalive, mirrors to raw sockets, calls `nfc_data_exchange`, and refreshes link timeout. RX completion stores `rx_pending`, cancels the link timer, runs `rx_work`, mirrors to raw sockets, dispatches by PDU type, schedules tx work, and frees the skb.

State and persistence: `llcp_devices` globally tracks local objects under a spinlock. Each local is kref-managed and also holds an `nfc_dev` reference. Persistent per-link state includes local/remote GB, remote MIU/LTO/WKS/OPT, SAP bitmaps/counters, pending SDP requests, socket lists, target index, RF/communication modes, timers, work items, and tx/rx queues.

Dependencies and integration points: Integrates with NFC DEP link callbacks, generic netlink SDP result delivery, raw NFC sockets, LLCP socket implementation, and PDU builders in `llcp_commands.c`.

Risks: `nfc_llcp_general_bytes` calls `nfc_llcp_local_put(local)` and then returns `local->gb`, which is risky if the local ref can drop to zero before the caller copies the bytes. Many receive paths assume PDU length is sufficient before indexing header/sequence/reason bytes. Socket release while tx work scans local queues is protected partly by skb queue locks but needs careful concurrency testing.

Test signals: Cover local refcounting and device unregister, SAP allocation/free for WKS/SDP/local ranges, remote GB parsing failures, SYMM timeout link down, PDU dispatch for all known PDU types, AGF nested PDU parsing, connect/CC/DM/DISC transitions, SDP request/response and timeout paths, raw socket mirroring, and MAC up/down lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/llcp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/llcp_sock.c -->
# sources/distributed-fs/ceph-client/net/nfc/llcp_sock.c

Purpose: Exposes LLCP as an NFC socket protocol supporting stream/seqpacket connected sockets, datagram UI sockets, and privileged raw LLCP sockets.

Important APIs and functions: Implements socket ops for bind, raw bind, listen, accept, connect, getname, poll, release, sendmsg, recvmsg, getsockopt, and setsockopt. Shared helpers include `sock_wait_state`, `nfc_llcp_accept_unlink`, `nfc_llcp_accept_enqueue`, `nfc_llcp_accept_dequeue`, `nfc_llcp_sock_alloc`, `nfc_llcp_sock_free`, `nfc_llcp_sock_init`, and `nfc_llcp_sock_exit`.

Control flow: Bind resolves the NFC device and local LLCP object, reserves a service SAP, stores service name/protocol, and links the socket. Listen changes bound stream/seqpacket sockets to `LLCP_LISTEN`. Connect reserves a local SAP, links the socket in `connecting_sockets`, sends CONNECT, and waits for `LLCP_CONNECTED` unless nonblocking. Sendmsg routes datagrams to UI frames and connected sockets to I-frames. Recvmsg dequeues skbs and fills datagram peer SAPs when needed.

State and persistence: Per-socket state lives in `struct nfc_llcp_sock`: service name allocation, SAPs, reserved SAP, local/device refs, queues, sequence numbers, remote params, parent and accept queue. Release sends DISC for connected sockets, disconnects accepted children, unlinks from local socket lists, releases SAPs, orphans the sock, and drops references.

Dependencies and integration points: Registered with `nfc_proto_register` as `NFC_SOCKPROTO_LLCP`. Uses LLCP core SAP/list helpers, command builders, NFC device refs, socket wait queues, Linux poll, and raw socket capabilities.

Risks: Bind rejects DSAP but allows zero-length service-name allocation paths that should be checked. Connect cleanup must unwind local refs, device refs, SAP reservation, connecting-list link, and service-name allocation correctly for each failure point. Release uses `llcp_sock->ssap` rather than `reserved_ssap` when freeing, so reserved SAP semantics should be tested. Recvmsg requeues partially read skbs for stream, datagram, and raw types, which is unusual for datagrams.

Test signals: Socket API tests should cover bind/listen/accept/connect success and failure, nonblocking connect, service-name and DSAP addressing, SAP exhaustion, accepted child cleanup, raw socket permission checks, poll masks, option bounds, datagram send/recv names, partial recv behavior, and release during active link teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/llcp_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/Kconfig -->
# sources/distributed-fs/ceph-client/net/nfc/nci/Kconfig

Purpose: Defines kernel configuration options for NFC Controller Interface support and optional NCI transports over SPI and UART.

Important APIs and symbols: `CONFIG_NFC_NCI` enables the core NCI protocol module, depending on `NFC`. `CONFIG_NFC_NCI_SPI` depends on `NFC_NCI && SPI` and selects `CRC_CCITT`. `CONFIG_NFC_NCI_UART` depends on `NFC_NCI && TTY`.

Control flow: Kconfig controls whether objects in `net/nfc/nci/Makefile` are built into the kernel or as modules. The SPI and UART options compile transport wrappers that sit under the NCI core.

State and persistence: No runtime state. The selected symbols persist in the kernel build configuration and determine module availability.

Dependencies and integration points: Integrates with the NFC subsystem menu, SPI framework, TTY framework, and CRC support for SPI transport.

Risks: Drivers depending on SPI or UART NCI support must select or depend on these symbols. Misconfiguration can build a controller driver without the needed NCI transport module.

Test signals: Build matrix coverage for `NFC_NCI=y/m`, SPI enabled/disabled, UART enabled/disabled, and module autoload expectations for NCI transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/Makefile -->
# sources/distributed-fs/ceph-client/net/nfc/nci/Makefile

Purpose: Describes how the NFC NCI core and optional transport modules are built.

Important APIs and targets: `obj-$(CONFIG_NFC_NCI) += nci.o` builds the core aggregate. `nci-objs := core.o data.o lib.o ntf.o rsp.o hci.o` defines the core module contents. `nci_spi-y += spi.o` and `obj-$(CONFIG_NFC_NCI_SPI) += nci_spi.o` build the SPI transport. `nci_uart-y += uart.o` and `obj-$(CONFIG_NFC_NCI_UART) += nci_uart.o` build the UART transport.

Control flow: Kbuild links the listed object files into `nci.ko` or built-in code according to Kconfig selections. Transport objects are separate modules so controller drivers can depend on only the transport they need.

State and persistence: No runtime state. Build graph state is determined by Kconfig symbols.

Dependencies and integration points: Must remain synchronized with exported symbols used by NCI drivers and with files present in the directory. Core includes HCI-over-NCI support by always linking `hci.o` into `nci.o`.

Risks: Adding new core source files without updating `nci-objs` silently omits code. Removing or renaming transport files without updating the Makefile breaks builds under matching config combinations.

Test signals: Build all enabled combinations and verify that exported symbols from `core.o`, `data.o`, `lib.o`, `ntf.o`, `rsp.o`, and `hci.o` are available from the core module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/core.c -->
# sources/distributed-fs/ceph-client/net/nfc/nci/core.c

Purpose: Implements the NCI core device, request serialization, command/data workqueues, NFC operation callbacks, RF discovery/activation/deactivation, NFCEE helpers, logical connection management, loopback, and driver-facing allocation/registration APIs.

Important APIs and functions: Exported APIs include `nci_allocate_device`, `nci_free_device`, `nci_register_device`, `nci_unregister_device`, `nci_recv_frame`, `nci_send_frame`, `nci_send_cmd`, `nci_request`, `nci_req_complete`, `nci_core_cmd`, `nci_prop_cmd`, `nci_core_reset`, `nci_core_init`, `nci_set_config`, `nci_nfcee_discover`, `nci_nfcee_mode_set`, `nci_core_conn_create`, `nci_core_conn_close`, and `nci_nfcc_loopback`.

Control flow: Requests are serialized by `req_lock`; `__nci_request` sends a request function and waits for `req_completion`. Open runs driver open/init, CORE_RESET, setup, CORE_INIT, post_setup, RF discovery map, then marks the device up. TX command work sends one command while `cmd_cnt` allows and arms a command timer. RX work validates inbound packet size and dispatches to response, notification, or data handlers. Data TX work sends queued data while connection credits allow.

State and persistence: `struct nci_dev` stores flags (`NCI_UP`, `NCI_INIT`, `NCI_UNREG`, data exchange flags), request status/result, workqueues, timers, command/rx/tx queues, connection list, RF connection pointer, HCI device, targets, current request parameters, active protocol, remote general bytes, ATS, and controller capabilities.

Dependencies and integration points: Hooks into `struct nfc_ops` for NFC core operations; calls lower driver `open`, `close`, `send`, and optional setup/security-element/firmware hooks; delegates packet bodies to `rsp.c`, `ntf.c`, and `data.c`; allocates an HCI-over-NCI helper through `hci.c`.

Risks: `nci_prop_cmd`, `nci_core_cmd`, `nci_core_reset`, and `nci_core_init` call `__nci_request` directly rather than `nci_request`, so callers must ensure serialization and device state. Close/unregister paths use workqueue flushes and timers with lock ordering that must avoid deadlocks with rx work and request completion. `nci_valid_size` rejects zero-length standard notifications/responses, so spec exceptions must be explicit.

Test signals: Exercise open success and each failure unwind point, command timeout and response completion, rx validation, proprietary/core op delegation, RF discovery state transitions, target activation/deactivation, data exchange busy handling, close during pending request/data exchange, logical connection create/close, and loopback connection reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/data.c -->
# sources/distributed-fs/ceph-client/net/nfc/nci/data.c

Purpose: Handles NCI data packet transmission, fragmentation, receive reassembly, status-byte handling for frame interfaces, and completion of NFC data exchanges.

Important APIs and functions: `nci_data_exchange_complete` completes pending exchanges and calls the stored callback. `nci_conn_max_data_pkt_payload_size` reports connection payload size. `nci_send_data` queues data to the NCI tx worker, fragmenting via `nci_queue_tx_data_frags` when needed. `nci_rx_data_packet` parses inbound data headers and calls `nci_add_rx_data_frag`.

Control flow: TX pushes an NCI data header with connection id, payload length, message type, and PBF. Large skbs are split into fragments sized by `conn_info->max_pkt_payload_len`, queued atomically, and the original skb is freed. RX strips the data header, optionally removes a trailing status byte for frame interfaces, reassembles continuation fragments in `ndev->rx_data_reassembly`, and either forwards target-mode data to NFC TM or completes the active exchange.

State and persistence: Uses per-connection `max_pkt_payload_len` and callbacks from `conn_info`, `ndev->tx_q`, `ndev->cur_conn_id`, `ndev->rx_data_reassembly`, `NCI_DATA_EXCHANGE`, and the data timer maintained by core.

Dependencies and integration points: Works with `nci_tx_work` in `core.c`, connection metadata created by `rsp.c`, RF mode from the NFC core device, and NFC target-mode delivery via `nfc_tm_data_received`.

Risks: RX reassembly stores only one partial packet for the whole device, so interleaved fragmented data on different connections would corrupt state. Status-byte removal assumes skb length is nonzero. `nci_data_exchange_complete` clears the data-exchange bit before invoking callbacks, intentionally allowing immediate reentry but requiring callback-safe state.

Test signals: Fragment at exact max size, one byte over max, multi-fragment payloads, allocation failure cleanup, credit-limited tx progression through core tx work, RX continuation/last reassembly, malformed empty frame-interface data, target-mode forwarding, and callback reentry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/hci.c -->
# sources/distributed-fs/ceph-client/net/nfc/nci/hci.c

Purpose: Implements HCI over NCI logical connections, allowing HCP command/event/response traffic to run over the NCI data path as specified by NCI 1.1.

Important APIs and functions: Exported APIs include `nci_hci_send_event`, `nci_hci_send_cmd`, `nci_hci_clear_all_pipes`, `nci_hci_open_pipe`, `nci_hci_set_param`, `nci_hci_get_param`, `nci_hci_connect_gate`, `nci_hci_dev_session_init`, `nci_hci_allocate`, and `nci_hci_deallocate`. Core helpers include `nci_hci_send_data`, `nci_hci_data_received_cb`, `nci_hci_cmd_received`, and `nci_hci_msg_rx_work`.

Control flow: HCI send paths resolve gate to pipe, build HCP headers, and call `nci_send_data` over `hci_dev->conn_info`. Synchronous commands use `nci_request` and receive their response through `nci_hci_data_received_cb`, which reassembles HCP fragments and completes the request. Non-response commands/events are queued to `msg_rx_work`; admin notifications update the pipe table and send a response.

State and persistence: `struct nci_hci_dev` holds pipe/gate tables, HCI init data, NFCEE id, HCI connection info, receive fragment queue, message receive queue, and rx work. Session init resets pipes, opens the admin pipe, reads session identity, optionally restores a driver session, or clears/reconnects configured gates and stores a session id.

Dependencies and integration points: Depends on NCI connection records from CORE_CONN_CREATE and NFCEE discovery notifications. Uses `nci_request`, `nci_send_data`, and driver callbacks such as `hci_event_received`, `hci_cmd_received`, and `hci_load_session`.

Risks: `nci_hci_send_cmd`, `set_param`, and `get_param` assume `conn_info->rx_skb` is present after a successful request. `nci_hci_hcp_message_rx` calls `nci_req_complete` after dispatch even though response handling also completes, which should be verified for harmless duplicate completion. Fragment reassembly needs malformed and allocation-failure coverage. Pipe table updates rely on controller-provided lengths and pipe IDs.

Test signals: Exercise HCI logical connection setup, session restore versus clear/reconnect, command response conversion, parameter get/set, event/cmd driver callbacks, HCP fragmentation/reassembly, admin pipe notifications, invalid pipe/gate handling, and missing `conn_info` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/hci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/lib.c -->
# sources/distributed-fs/ceph-client/net/nfc/nci/lib.c

Purpose: Provides a shared translation from NCI status codes to Linux errno values.

Important APIs and functions: `nci_to_errno` maps `NCI_STATUS_OK` to 0, protocol and parameter errors to `-EPROTO`, controller busy/rejected states to `-EBUSY`, timeout/transmission errors to timeout/communication errno values, and unknown/failure statuses to `-ENOSYS`. It is exported for NCI core and drivers.

Control flow: Simple switch over the controller status byte. It is used when request completion status is converted by `__nci_request` and when data-frame status bytes are processed.

State and persistence: No state.

Dependencies and integration points: Includes NCI public and core headers for status constants and is linked into the core `nci` module.

Risks: Any new NCI status codes not mapped here will collapse to `-ENOSYS`, which may obscure the failure cause. Some mappings are policy choices and should match userspace expectations.

Test signals: Unit-style tests for every known status code, unknown status fallback, and callers that compare exact errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/ntf.c -->
# sources/distributed-fs/ceph-client/net/nfc/nci/ntf.c

Purpose: Parses and handles NCI notification packets, including reset notifications, connection credits, generic/interface errors, RF discovery, RF activation/deactivation, and NFCEE discovery.

Important APIs and functions: `nci_ntf_packet` is the dispatcher. Supporting functions include `nci_core_reset_ntf_packet`, `nci_core_conn_credits_ntf_packet`, `nci_core_generic_error_ntf_packet`, `nci_core_conn_intf_error_ntf_packet`, RF parameter extractors, `nci_add_new_protocol`, `nci_add_new_target`, `nci_clear_target_list`, `nci_rf_discover_ntf_packet`, `nci_rf_intf_activated_ntf_packet`, `nci_rf_deactivate_ntf_packet`, and `nci_nfcee_discover_ntf_packet`.

Control flow: The dispatcher strips the NCI control header, offers proprietary notifications to driver ops, then handles core opcodes. Discovery notifications parse RF technology parameters, aggregate protocols on existing logical targets, and report targets when the final discovery notification arrives. Activation notifications update RF connection payload size/credits, store NFC-DEP general bytes or ISO-DEP ATS, and transition to poll-active or listen-active. Credit notifications add to connection credits and restart TX work.

State and persistence: Mutates `ndev->nci_ver`, manufacturer fields, target array/count, state atomics, RF connection credits and payload size, remote general bytes, target ATS, HCI NFCEE id/current params, tx queue, rx reassembly, and data-exchange flags.

Dependencies and integration points: Works with `core.c` request completion and state machine, `data.c` data exchange completion, NFC core target reporting and target-mode activation, driver proprietary/core notification hooks, and NCI HCI setup.

Risks: Parsing is length-aware in many places, but some activation parameter copies clamp length without always verifying enough remaining bytes for copied data. Protocol filtering depends on `ndev->poll_prots` and may drop proprietary mappings unless the driver implements `get_rfprotocol`. Deactivation purges data queues and completes exchanges with `-EIO`, so upper layers must tolerate abrupt cancellation.

Test signals: Fuzz all notification parsers, exercise multi-notification discovery, duplicate logical targets with multiple protocols, activation for ISO-DEP/NFC-DEP/frame/listen modes, credit replenishment, interface errors during exchange, deactivation modes, NFCEE discovery for HCI, and proprietary notification delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/ntf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/rsp.c -->
# sources/distributed-fs/ceph-client/net/nfc/nci/rsp.c

Purpose: Parses and handles NCI response packets, updating controller capability state, RF/request state, logical connection records, and request completion.

Important APIs and functions: `nci_rsp_packet` is the dispatcher. Response handlers include `nci_core_reset_rsp_packet`, `nci_core_init_rsp_packet_v1`, `nci_core_init_rsp_packet_v2`, `nci_core_init_rsp_packet`, `nci_core_set_config_rsp_packet`, `nci_rf_disc_map_rsp_packet`, `nci_rf_disc_rsp_packet`, `nci_rf_disc_select_rsp_packet`, `nci_rf_deactivate_rsp_packet`, `nci_nfcee_discover_rsp_packet`, `nci_nfcee_mode_set_rsp_packet`, `nci_core_conn_create_rsp_packet`, and `nci_core_conn_close_rsp_packet`.

Control flow: The dispatcher stops the command timer, logs opcode fields, strips the control header, dispatches proprietary responses to driver ops or core opcodes to local handlers, calls optional core response hooks, frees the skb, resets `cmd_cnt`, and queues the next command if one is pending. Some requests complete only after a later notification, such as RF_DISCOVER_SELECT success or active-target RF_DEACTIVATE success.

State and persistence: Mutates controller version/capability fields, supported RF interfaces, routing/control limits, manufacturer fields, NCI state, RF connection info, connection list, current HCI connection pointer, connection payload sizes, and credits. Connection records are devm-allocated and linked in `ndev->conn_info_list`.

Dependencies and integration points: Completes `core.c` synchronous requests via `nci_req_complete`, creates connection metadata consumed by `data.c` and `hci.c`, and delegates driver-specific response handling via proprietary/core ops tables.

Risks: Core init v1/v2 parsing relies on response lengths matching spec after the generic NCI size check; malformed but minimally sized packets can still cause offset issues. `nci_core_conn_create_rsp_packet` cleanup uses devm allocation/free patterns and must keep `hci_dev->conn_info` consistent. Some response handlers intentionally defer completion, so request timeout coverage is important.

Test signals: Validate reset/init parsing for NCI 1.x and 2.x, RF discovery success creating static RF connection, deferred completion paths, logical connection create/close including HCI connection selection, command queue restart after each response, proprietary response delegation, and malformed lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/nfc/nci/rsp.c -->
