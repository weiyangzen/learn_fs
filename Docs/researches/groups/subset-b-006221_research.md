# Research: subset-b-006221

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_c_st.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_c_st.c

Purpose: Defines the LLC type 2 connection-component state transition table. It is the declarative core consumed by `llc_conn_service()` in `llc_conn.c`: events are matched by `llc_conn_ev_*` predicates, optionally qualified by `llc_conn_ev_qlfy_*` predicates, then action vectors of `llc_conn_ac_*` functions are executed before moving to a next `LLC_CONN_STATE_*`.

Important APIs/types/functions: Exports `struct llc_conn_state llc_conn_state_table[NBR_CONN_STATES]`. The file is composed of `struct llc_conn_state_trans`, `llc_conn_action_t` arrays, and `llc_conn_ev_qfyr_t` arrays. It references the connection states ADM, SETUP, NORMAL, BUSY, REJ, AWAIT, AWAIT_BUSY, AWAIT_REJ, D_CONN, RESET, ERROR, and TEMP. It depends heavily on action helpers from `llc_c_ac.h` and event/qualifier helpers from `llc_c_ev.h`.

Control flow: The table is ordered by event categories used by `llc_build_offset_table()` and `llc_find_offset()`: primitive requests, local busy/simple events, initiate P/F cycle, timers, and received frames. Common transitions cover shared disconnect, reset, SABME, DISC, DM, FRMR, invalid sequence/control cases, and timeout escalation. State-specific blocks encode setup handshakes, normal data transfer, receiver busy/reject handling, await states during poll/final cycles, disconnect confirmation, reset recovery, and FRMR error recovery.

State and persistence behavior: No runtime state is stored in this file; all state lives in `struct llc_sock` fields such as `state`, `vS`, `vR`, `p_flag`, `f_flag`, `s_flag`, `remote_busy_flag`, `cause_flag`, retry counters, and timers. This file determines how those fields are mutated through action callbacks and when upper-layer indications/confirmations are requested.

Dependencies and integration points: Integrated by `llc_conn.c` through `llc_conn_state_table` and the offset table built at init. Its action lists call into PDU builders, timer control, skb queues, and socket notification paths. Correct behavior also depends on `llc_c_ev.c` classifying incoming PDUs and timer events consistently with this table's grouping.

Risks and test signals: Ordering is critical because transitions are scanned linearly from a category offset; inserting a transition in the wrong category can make an event unreachable or misclassified. Many transitions differ only by qualifiers such as retry count, P/F flag, remote busy, expected `N(S)`, or status-setting side effects, so regressions are likely in edge cases: simultaneous SABME/DISC, invalid `N(R)`, timeout at `n2`, local busy entry/exit, and REJ recovery. Useful tests are packetdrill-style LLC2 handshakes, timer-forced retransmission tests, invalid sequence fuzzing, and checking `/proc/net/llc/core` state/timer fields while exercising connect, data, busy, reset, and disconnect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_c_st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_conn.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_conn.c

Purpose: Implements the LLC type 2 connection driver: socket allocation/init/free, state-machine dispatch, established/listener lookup, received connection PDU handling, transmit queue handling, ACK removal/resend, timer defaults, and backlog processing.

Important APIs/types/functions: Exports `llc_conn_state_process()`, `llc_conn_send_pdu()`, `llc_conn_rtn_pdu()`, resend helpers, `llc_conn_remove_acked_pdus()`, `llc_lookup_established()`, `llc_data_accept_state()`, `llc_build_offset_table()`, SAP socket add/remove helpers, `llc_conn_handler()`, `llc_sk_alloc()`, `llc_sk_stop_all_timers()`, `llc_sk_free()`, and `llc_sk_reset()`. Global sysctls back timer defaults: `sysctl_llc2_ack_timeout`, `sysctl_llc2_p_timeout`, `sysctl_llc2_rej_timeout`, and `sysctl_llc2_busy_timeout`.

Control flow: `llc_conn_handler()` decodes source/destination LLC addresses, finds an established socket or listener, creates a child socket for passive opens, locks the socket, and either processes the PDU immediately or queues it to backlog. `llc_conn_state_process()` clears indication/confirmation fields, runs `llc_conn_service()`, then translates resulting primitives into socket receive queueing, stream state changes, write-space notification, or close/reset handling. `llc_conn_service()` locates the current state table, qualifies the event, executes actions, and commits `next_state`.

State and persistence behavior: Per-connection state is stored in `struct llc_sock`: state machine state, sequence variables, flags, timers, retry/window sizes, and `pdu_unack_q`. I-PDUs are cloned before transmit and the original is retained in `pdu_unack_q` for ACK tracking unless using loopback. Socket membership is persisted in SAP hash tables with RCU/nulls-list lookup and explicit SAP reference counts.

Dependencies and integration points: Uses `llc_conn_state_table` from `llc_c_st.c`, action/event definitions from LLC connection headers, PDU accessors from `llc_pdu.c`, SAP state from `llc_sap.c`, Linux socket state constants, network namespace checks, `dev_queue_xmit()`, backlog APIs, timers, and RCU/nulls socket hash traversal.

Risks and test signals: High-risk areas are skb ownership/refcount transitions, backlog lock ordering, SLAB_TYPESAFE_BY_RCU revalidation, child socket creation on listen sockets, sequence arithmetic in `llc_conn_remove_acked_pdus()`, and the transmit clone/unack queue path. Tests should cover connect/listen/accept, duplicate established lookup, timer expiry while user owns the socket, I-PDU retransmit, ACK advancement, loopback behavior, and stream state transitions from SYN_SENT/ESTABLISHED/CLOSING to close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_core.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_core.c

Purpose: Provides minimal LLC core registration and SAP lifetime management. It owns the global SAP list and registers the 802.2 packet handler with the network stack.

Important APIs/types/functions: Defines and exports `LIST_HEAD(llc_sap_list)`, `llc_sap_find()`, `llc_sap_open()`, and `llc_sap_close()`. Internal helpers allocate SAPs, initialize `sk_lock`, local-address nulls hash buckets, state, refcount, and look up by LSAP under `llc_sap_list_lock` or RCU.

Control flow: Module init registers a `packet_type` for `ETH_P_802_2` with `.func = llc_rcv`; exit removes it. Upper layers call `llc_sap_open()` to reserve a unique LSAP and attach an optional receive callback. `llc_sap_find()` is used on packet receive to take a safe reference. `llc_sap_close()` removes the SAP from the RCU list and frees it after grace period, warning if sockets remain attached.

State and persistence behavior: The persistent state is process-global: `llc_sap_list`, each `struct llc_sap`'s LSAP, receive callback, socket hashes, `sk_count`, and refcount. SAP entries are RCU-visible and require balanced holds/puts by users.

Dependencies and integration points: Depends on Linux module, packet socket dispatch, RCU list management, netdevice Ethernet protocol IDs, and `llc_rcv()` from `llc_input.c`. It is the shared registry used by both connection and datagram LLC paths.

Risks and test signals: Duplicate LSAP opens must fail, close with live sockets is dangerous, and callback publication must be compatible with RCU readers. Useful signals include module load/unload, SAP open/find/close races, repeated LSAP bind attempts, and receive delivery after close under RCU stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_if.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_if.c

Purpose: Provides upper-layer APIs for connection-oriented LLC operations: send data, initiate a connection, and disconnect.

Important APIs/types/functions: Exports `llc_build_and_send_pkt()`, `llc_establish_connection()`, and `llc_send_disc()`. These functions construct `llc_conn_state_ev` primitives on skbs and enter the connection state machine through `llc_conn_state_process()`.

Control flow: Data send rejects ADM/out-of-data states and active poll cycles, marks failed data requests, stamps `LLC_DATA_PRIM` request metadata, assigns `skb->dev`, and lets the connection table build/transmit the I-PDU. Connection establishment builds local/remote LLC addresses, checks for an existing established socket, allocates a zero-length event skb, and posts a `LLC_CONN_PRIM` request. Disconnect validates stream/established state, sets TCP state to `TCP_CLOSING`, and posts a `LLC_DISC_PRIM` request.

State and persistence behavior: This file mostly creates transient event skbs, but it reads and affects persistent socket state via `llc->state`, `llc->p_flag`, `llc->failed_data_req`, `sk_state`, and `sk_socket->state` indirectly through the state machine.

Dependencies and integration points: Depends on `llc_conn.c` for state processing and established lookup, `llc_c_st.c` for data-accept state, SAP addressing from `llc_sock`, and Linux TCP-style socket state constants used by the LLC socket layer.

Risks and test signals: Risks include consuming skbs on failure, duplicate connection behavior when an established socket already exists, and returning Linux errno values consistently despite the underlying state machine returning LLC-style statuses. Test upper-layer send during ADM, busy, and P/F wait states; connect to an existing established peer; connect allocation failure; and disconnect from invalid and established states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_if.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_input.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_input.c

Purpose: Implements the minimal 802.2 receive path and dispatches validated LLC frames to station, SAP, or connection handlers.

Important APIs/types/functions: Exports `llc_add_pack()`, `llc_remove_pack()`, and `llc_set_station_handler()`. Internal helpers include `llc_pdu_type()` for destination classification and `llc_fixup_skb()` for header length validation, pulling, transport-header setup, and length trimming.

Control flow: `llc_rcv()` drops promiscuous other-host traffic, ensures a private skb, validates/pulls the LLC header, dispatches NULL DSAP frames to the station handler, looks up the destination SAP, classifies U/I/S PDUs, and either calls an upper-layer SAP callback, clones to that callback plus LLC handler, or drops. Handler tables are indexed by `LLC_DEST_SAP` and `LLC_DEST_CONN`.

State and persistence behavior: Handler pointers are static global state. Publication uses memory barriers and `synchronize_net()` on removal to protect lockless receive-side reads. The receive function mutates skb data/headers and may clone when both protocol callback and LLC state-machine handler are present.

Dependencies and integration points: Registered from `llc_core.c` as the packet handler. Uses SAP lookup from `llc_core.c`, PDU macros from `llc_pdu.h`, station handler from `llc_station.c`, SAP handler from `llc_sap.c`, and connection handler from `llc_conn.c`.

Risks and test signals: Header length handling is security-sensitive: malformed short 802.2 frames, bogus length fields, and non-Ethernet mac lengths should be dropped. Handler installation/removal races, invalid U-PDU commands, and clone failure should be tested. Functional signals include UI delivery to datagram sockets, SABME/DISC delivery to connection sockets, and NULL DSAP XID/TEST station responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_output.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_output.c

Purpose: Provides the minimal LLC output path for MAC header construction and connectionless UI transmission.

Important APIs/types/functions: Exports `llc_mac_hdr_init()` and `llc_build_and_send_ui_pkt()`. The MAC helper supports Ethernet and loopback devices through `dev_hard_header()`. The UI helper initializes LLC U-PDU headers and queues the frame with `dev_queue_xmit()`.

Control flow: `llc_build_and_send_ui_pkt()` writes DSAP/SSAP/command fields via `llc_pdu_header_init()`, converts the frame to a UI command, calls `llc_mac_hdr_init()`, and either transmits or frees the skb on header failure.

State and persistence behavior: No persistent state is kept. The functions mutate the outgoing skb in place and consume it by successful queueing or freeing on error.

Dependencies and integration points: Used by datagram/connectionless upper layers and SAP action helpers. Relies on netdevice hardware header support, PDU initializer macros, and the device address in `skb->dev`.

Risks and test signals: Unsupported device types return `-EINVAL`; callers must not reuse consumed skbs. Tests should cover Ethernet, loopback, unsupported ARP types, invalid destination SAP/MAC combinations, and ensuring UI frames carry the expected DSAP/SSAP/control bytes before transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_pdu.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_pdu.c

Purpose: Encapsulates LLC PDU control-field accessors and builders for I, S, and U frame types, including connection-management and station/SAP PDUs.

Important APIs/types/functions: Implements command/response bit setting, poll/final bit set/decode, builders for DISC, I, REJ, RNR, RR, SABME, DM, FRMR, UA, and response variants. It also builds FRMR info by copying rejected control bytes and encoding sequence/invalidity indicators.

Control flow: Builders write the control bytes directly through `llc_pdu_sn_hdr()` or `llc_pdu_un_hdr()`. I/S PDUs encode `N(S)` and `N(R)` shifted into even bits and store P/F in `ctrl_2`. U PDUs encode command/response values and P/F in `ctrl_1`. FRMR appends a `struct llc_frmr_info` payload with `skb_put()`.

State and persistence behavior: No module-level state. All behavior is skb-local, mutating headers and sometimes extending frame length. Correctness relies on callers allocating enough headroom/body for the selected PDU type.

Dependencies and integration points: Called by connection actions, SAP actions, station replies, and output helpers. It depends on layout and bit macros from `llc_pdu.h`; its encodings must match event classifiers in `llc_c_ev.c`, `llc_s_ev.c`, and `llc_input.c`.

Risks and test signals: Bit encoding errors directly break interoperability. The U-PDU P/F setter uses a compound OR expression that deserves regression coverage around clearing and setting the bit. Tests should validate raw header bytes for every builder, FRMR payload length/content, round-trip P/F decode, and sequence number modulo handling around 0/127.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_pdu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_proc.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_proc.c

Purpose: Exposes LLC socket and connection-core diagnostics under `/proc/net/llc`.

Important APIs/types/functions: Provides `llc_proc_init()` and `llc_proc_exit()`. It defines seq_file operations for `socket` and `core`, iterator helpers over `llc_sap_list` and each SAP's `sk_laddr_hash`, and a state-name table for `LLC_CONN_STATE_*`.

Control flow: Init creates `/proc/net/llc/socket` and `/proc/net/llc/core`; failure unwinds previously created entries. Seq iteration starts under `rcu_read_lock_bh()`, locates sockets by logical position, keeps the current SAP `sk_lock` held while walking a hash bucket, advances across buckets and SAPs, and unlocks in stop. Show functions render socket addressing/queues/state/user/link or LLC2 internals like retry count, windows, flags, timer pending bits, backlog presence, and socket ownership.

State and persistence behavior: This file stores only the proc directory pointer and static names. It reads live socket/SAP state and timer state without changing protocol behavior.

Dependencies and integration points: Depends on `llc_sap_list` from `llc_core.c`, `llc_sock` layout from LLC connection headers, seq_file/proc APIs, user namespace UID formatting, and timer/backlog helpers.

Risks and test signals: Iterator locking is delicate: early returns intentionally keep `sap->sk_lock` until seq stop. State-name indexing assumes valid LLC states. Test by opening/reading proc files while sockets are created/destroyed, with multiple SAP hash buckets populated, and with connections in each major state. KASAN/lockdep are useful for iterator lifetime issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_s_ac.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_s_ac.c

Purpose: Implements SAP-component action callbacks used by the SAP state machine for UI, XID, TEST, and status operations.

Important APIs/types/functions: Defines `llc_sap_action_unitdata_ind()`, `llc_sap_action_send_ui()`, XID command/response actions, TEST command/response actions, `llc_sap_action_report_status()`, `llc_sap_action_xid_ind()`, and `llc_sap_action_test_ind()`. Internal `llc_prepare_and_xmit()` initializes MAC headers, clones the skb, preserves owner when present, and transmits the clone.

Control flow: Indication actions mark received PDUs for upper-layer return through `llc_sap_rtn_pdu()`. Send actions construct the appropriate U-PDU header and control bytes, then queue a clone. Response actions decode source/destination MAC/SAP from the received skb, allocate a new frame, initialize it as a response, build a MAC header, and transmit.

State and persistence behavior: No persistent state. It mutates event skbs or creates response skbs. The original request skb remains owned by the SAP state process and is later freed or delivered.

Dependencies and integration points: Consumed by `llc_s_st.c` transition arrays and called by `llc_sap.c`. Depends on PDU helpers, `llc_alloc_frame()`, `llc_mac_hdr_init()`, Ethernet length fields, and `dev_queue_xmit()`.

Risks and test signals: TEST response length derives from the Ethernet length minus the 3-byte U header and is guarded by `skb->mac_len`; malformed length fields can still stress allocation and trim assumptions. Clone allocation failures and MAC header failures must not leak skbs. Tests should cover UI request, XID request/response, TEST with payload echo, malformed short Ethernet frames, and owner propagation on cloned sends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_s_ac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_s_ev.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_s_ev.c

Purpose: Provides SAP state-machine event predicate functions. Each returns 0 for a match and 1 for non-match, matching the transition scanner convention in `llc_sap.c`.

Important APIs/types/functions: Predicates include activation/deactivation requests, received UI, UNITDATA request, XID request, received XID command/response, TEST request, and received TEST command/response. They inspect `struct llc_sap_state_ev` metadata and U-PDU command/response fields.

Control flow: For primitive events, predicates match event type, primitive, and primitive type. For received PDUs, they require PDU event type, U-PDU type, command or response direction, and the expected UI/XID/TEST opcode. The SAP state table calls these in ordered transition arrays.

State and persistence behavior: No persistent state and no mutation except reading skb control/header data. Event metadata must already be initialized by `llc_sap.c` or upper-layer builders.

Dependencies and integration points: Used by `llc_s_st.c`; depends on PDU macros from `llc_pdu.h` and event layout from `llc_s_ev.h`. Its classifications must stay aligned with `llc_input.c`'s decision to send U UI/XID/TEST frames to SAP handling.

Risks and test signals: Return polarity is easy to misuse. Command/response macro alignment matters because XID and TEST opcodes are shared in similar fields. Tests should feed crafted UI/XID/TEST command and response frames, wrong primitive types, and non-U PDUs to ensure only intended transitions match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_s_ev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_s_st.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_s_st.c

Purpose: Defines the SAP component's two-state transition table for LLC type 1 style operations.

Important APIs/types/functions: Exports `struct llc_sap_state llc_sap_state_table[LLC_NR_SAP_STATES]`. It defines transitions for `LLC_SAP_STATE_INACTIVE` and `LLC_SAP_STATE_ACTIVE`, with action arrays referencing SAP action callbacks from `llc_s_ac.c` and event predicates from `llc_s_ev.c`.

Control flow: INACTIVE accepts activation and moves to ACTIVE after reporting status. ACTIVE handles UNITDATA/UI delivery, UNITDATA requests, XID request/command/response, TEST request/command/response, and deactivation. Most active transitions remain ACTIVE; deactivation returns to INACTIVE.

State and persistence behavior: The table itself is static. Runtime state is `sap->state`, changed by `llc_sap_next_state()` after action success. The active transitions can request upper-layer indications by setting event fields via actions.

Dependencies and integration points: Consumed by `llc_sap.c`; depends on consistent event metadata from upper-layer send helpers and receive handling. It integrates with `llc_s_ac.c` for actual transmission and indication effects.

Risks and test signals: Transition ordering matters because the scanner returns the first matching event. Inactive behavior is minimal, so unexpected active-only PDUs should be rejected. Tests should cover activation, deactivation, UI receive and send, XID/TEST command-response pairs, and action failure preventing state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_s_st.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_sap.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_sap.c

Purpose: Implements SAP driver routines for frame allocation, upper-layer primitive metadata, SAP state-machine processing, TEST/XID sends, datagram socket lookup, multicast delivery, and SAP PDU receive dispatch.

Important APIs/types/functions: Exports/defines `llc_alloc_frame()`, `llc_save_primitive()`, `llc_sap_rtn_pdu()`, `llc_build_and_send_test_pkt()`, `llc_build_and_send_xid_pkt()`, and `llc_sap_handler()`. Internal helpers handle SAP transition lookup/action execution, dgram unicast lookup, multicast matching, and clone fanout.

Control flow: Send helpers populate `llc_sap_state_ev` source/destination addresses and primitive fields before entering `llc_sap_state_process()`. Receive handling decodes the destination address; multicast frames are cloned to all matching datagram sockets on the device, while unicast frames look up one datagram socket by netns/local MAC/SAP. `llc_sap_state_process()` runs the transition table and queues indications to the owning socket unless it is a listener.

State and persistence behavior: It does not own global SAP state but reads/mutates SAP and socket-associated state. It assigns skb ownership with `sock_hold()` and `sock_efree`, writes `sockaddr_llc` metadata into skb control storage, and uses socket queues for delivery. Multicast fanout temporarily stores held socket pointers in a stack array.

Dependencies and integration points: Called from `llc_input.c` via SAP type handler. Uses `llc_sap_state_table`, SAP actions/events, PDU decoders, net namespace checks, SAP socket hash tables maintained by `llc_conn.c`, and Linux datagram socket receive queueing.

Risks and test signals: High-risk points are skb ownership, multicast clone failure paths, nulls-list RCU revalidation, and listener exclusion during SAP indications. Tests should cover datagram unicast, multicast to many sockets, clone allocation failure, namespace isolation, socket removal during lookup, and correctness of saved `sockaddr_llc` fields for UI/XID/TEST.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_sap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_station.c -->
## sources/distributed-fs/ceph-client/net/llc/llc_station.c

Purpose: Implements the LLC station component for NULL DSAP XID and TEST commands.

Important APIs/types/functions: Provides `llc_station_init()` and `llc_station_exit()`, which install/remove the station receive handler through `llc_set_station_handler()`. Internal predicates detect NULL DSAP XID/TEST command U-PDUs, and action helpers send XID/TEST responses.

Control flow: `llc_station_rcv()` checks whether the incoming frame is a NULL DSAP XID command or TEST command, sends the corresponding response, then frees the original skb. XID responses are allocated with `struct llc_xid_info` space and use LSAP 0. TEST responses calculate payload size from the 802.2 length field minus the U header, echo data, build a MAC header, and transmit.

State and persistence behavior: The station file itself stores no protocol state; its only persistent effect is registering the global station handler in `llc_input.c`.

Dependencies and integration points: Receives frames from `llc_input.c` when DSAP is zero. Uses frame allocation from `llc_sap.c`, MAC header setup from `llc_output.c`, and PDU helpers from `llc_pdu.c`.

Risks and test signals: Length-derived TEST response sizing and short MAC headers are important validation points. Tests should inject NULL DSAP XID and TEST commands, non-command U frames, non-NULL DSAP frames, malformed short Ethernet frames, allocation failure, and verify generated responses use local device MAC as source and requester MAC as destination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/llc_station.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/sysctl_net_llc.c -->
## sources/distributed-fs/ceph-client/net/llc/sysctl_net_llc.c

Purpose: Registers sysctl entries for LLC2 timeout tuning and an LLC station sysctl directory.

Important APIs/types/functions: Provides `llc_sysctl_init()` and `llc_sysctl_exit()`. The `llc2_timeout_table` exposes `ack`, `busy`, `p`, and `rej` entries backed by the global timeout integers defined in `llc_conn.c`, using `proc_dointvec_jiffies`.

Control flow: Init registers `net/llc/llc2/timeout` with the timeout table and `net/llc/station` as an empty table. If either registration fails, init calls exit to unregister any partial state. Exit unregisters non-NULL headers and clears them.

State and persistence behavior: Persistent state is the two `ctl_table_header *` handles and the global timeout variables modified through sysctl. These values affect future timer setup and expiration lengths used by LLC connection sockets.

Dependencies and integration points: Depends on init_net sysctl registration, LLC timeout globals from `<net/llc.h>`, and the connection initialization path that copies sysctl values into per-socket timer `expire` fields.

Risks and test signals: The sysctls are global to `init_net` rather than per network namespace in this file. Tests should cover registration failure unwind, read/write of jiffies-backed values, module unload cleanup, and confirming new sockets inherit updated timeout values while existing timer structures keep their configured expires unless reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/llc/sysctl_net_llc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/Kconfig -->
## sources/distributed-fs/ceph-client/net/mac80211/Kconfig

Purpose: Defines build-time configuration for the generic mac80211 IEEE 802.11 networking stack and its optional rate-control, mesh, LED, debugfs, tracing, KUnit, and debug features.

Important APIs/types/functions: Kconfig symbols include `MAC80211`, `MAC80211_HAS_RC`, `MAC80211_RC_MINSTREL`, the default rate-control choice and `MAC80211_RC_DEFAULT`, `MAC80211_KUNIT_TEST`, `MAC80211_MESH`, `MAC80211_LEDS`, `MAC80211_DEBUGFS`, `MAC80211_MESSAGE_TRACING`, `MAC80211_DEBUG_MENU`, many debug booleans for MLME/STA/HT/OCB/IBSS/powersave/mesh/TDLS, `MAC80211_DEBUG_COUNTERS`, and `MAC80211_STA_HASH_MAX_SIZE`.

Control flow: Selecting `MAC80211` depends on `CFG80211` and selects cryptographic and CRC primitives required by 802.11 security and frame handling. If mac80211 is enabled, rate-control support can select Minstrel and set `"minstrel_ht"` as the default. Optional features are gated by dependencies such as `KUNIT`, `LEDS_CLASS`, `CFG80211_DEBUGFS`, `TRACING`, `MAC80211_MESH`, and the debug menu.

State and persistence behavior: This file does not create runtime state; it shapes build artifacts, module availability, selected object compilation, defaults, and visible configuration prompts. The string `MAC80211_RC_DEFAULT` persists into build configuration and can influence runtime default rate-control selection unless overridden by module parameters.

Dependencies and integration points: Integrates with the Linux Kconfig system and the broader wireless stack. Driver Kconfigs can depend on or select mac80211-related symbols; debug and test symbols control compilation of additional instrumentation and KUnit suites.

Risks and test signals: Dependency mistakes can hide required options or allow builds without required crypto/rate-control support. Debug options are explicitly warned as unsuitable for production due to overhead and remotely triggerable logging. Test signals include `make olddefconfig`, dependency visibility checks with `CFG80211=n`, allmodconfig/allnoconfig coverage, KUnit build with `MAC80211_KUNIT_TEST`, and verifying mesh-only debug symbols appear only when mesh support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/Kconfig -->
