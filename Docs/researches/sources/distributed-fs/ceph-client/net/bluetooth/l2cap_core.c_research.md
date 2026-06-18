# sources/distributed-fs/ceph-client/net/bluetooth/l2cap_core.c

## Purpose

`l2cap_core.c` is the core Linux Bluetooth L2CAP implementation. It manages L2CAP channels on top of HCI ACL and LE links, performs BR/EDR and LE signaling, handles fixed, connectionless, raw, and connection-oriented channels, negotiates configuration modes, enforces security, implements Basic, Enhanced Retransmission Mode (ERTM), Streaming, LE Credit Based Flow Control, and Enhanced Credit Based Flow Control (ECRED), and reassembles fragmented ACL data into L2CAP frames.

The file is the control and data-plane hub between HCI connection events and higher-level L2CAP sockets/users. It is not itself the user-space socket shim; instead it exposes channel and connection primitives used by socket code and other Bluetooth modules.

## Important APIs, types, and functions

Global module parameters are `disable_ertm` and `enable_ecred`. `l2cap_feat_mask` advertises baseline fixed-channel and connectionless support, with ERTM/Streaming/FCS added conditionally. `chan_list` plus `chan_list_lock` is the global channel registry used for listener lookup and debugfs output.

Channel creation and lifetime APIs include `l2cap_chan_create`, `l2cap_chan_set_defaults`, `l2cap_chan_hold`, `l2cap_chan_hold_unless_zero`, `l2cap_chan_put`, `l2cap_add_psm`, `l2cap_add_scid`, `l2cap_chan_add`, `__l2cap_chan_add`, `l2cap_chan_del`, `l2cap_chan_close`, `l2cap_chan_connect`, `l2cap_chan_reconfigure`, `l2cap_chan_send`, `l2cap_chan_busy`, `l2cap_chan_rx_avail`, and `l2cap_chan_list`. These operate on `struct l2cap_chan`, whose fields track state, CIDs, PSM, MTUs, mode, security level, retransmission windows, credit counters, queues, timers, and callbacks in `chan->ops`.

Connection lifetime APIs include `l2cap_conn_add`, `l2cap_conn_del`, `l2cap_conn_get`, `l2cap_conn_put`, and `l2cap_conn_hold_unless_zero`. `struct l2cap_conn` binds L2CAP to `struct hci_conn` and `struct hci_chan`, owns the per-connection channel list, signaling identifier allocator, feature negotiation state, pending RX queue, RX reassembly state, users list, and timers/work items.

Signaling command handlers are split by transport. BR/EDR signaling uses `l2cap_sig_channel`, `l2cap_bredr_sig_cmd`, `l2cap_connect_req`, `l2cap_connect_create_rsp`, `l2cap_config_req`, `l2cap_config_rsp`, `l2cap_disconnect_req`, `l2cap_disconnect_rsp`, `l2cap_information_req`, and `l2cap_information_rsp`. LE signaling uses `l2cap_le_sig_channel`, `l2cap_le_sig_cmd`, `l2cap_conn_param_update_req`, `l2cap_le_connect_req`, `l2cap_le_connect_rsp`, `l2cap_le_credits`, `l2cap_ecred_conn_req`, `l2cap_ecred_conn_rsp`, `l2cap_ecred_reconf_req`, and `l2cap_ecred_reconf_rsp`.

Configuration negotiation is handled by `l2cap_build_conf_req`, `l2cap_parse_conf_req`, `l2cap_parse_conf_rsp`, `l2cap_build_conf_rsp`, `l2cap_conf_rfc_get`, `set_default_fcs`, `l2cap_txwin_setup`, and helpers for MTU, RFC, FCS, EFS, and EWS options. `l2cap_ertm_init` initializes ERTM state after negotiation succeeds.

Data transmission starts at `l2cap_chan_send`. It builds PDUs through `l2cap_create_connless_pdu`, `l2cap_create_basic_pdu`, `l2cap_create_iframe_pdu`, `l2cap_create_le_flowctl_pdu`, `l2cap_segment_sdu`, `l2cap_segment_le_sdu`, and sends through `l2cap_do_send` or `l2cap_send_acl`. ERTM/Streaming control headers are packed and unpacked by `__pack_control`, `__unpack_control`, `__pack_enhanced_control`, `__pack_extended_control`, `__unpack_enhanced_control`, and `__unpack_extended_control`.

ERTM reliability is implemented by sequence-list helpers (`l2cap_seq_list_init`, `l2cap_seq_list_append`, `l2cap_seq_list_pop`, `l2cap_seq_list_contains`, `l2cap_seq_list_clear`), TX state functions (`l2cap_tx`, `l2cap_tx_state_xmit`, `l2cap_tx_state_wait_f`, `l2cap_ertm_send`, `l2cap_ertm_resend`, `l2cap_retransmit`, `l2cap_retransmit_all`), RX state functions (`l2cap_rx`, `l2cap_rx_state_recv`, `l2cap_rx_state_srej_sent`, `l2cap_rx_state_wait_p`, `l2cap_rx_state_wait_f`, `l2cap_stream_rx`), and timers (`l2cap_retrans_timeout`, `l2cap_monitor_timeout`, `l2cap_ack_timeout`, `l2cap_chan_timeout`, `l2cap_info_timeout`).

Lower-layer HCI integration is through `l2cap_cb` with `l2cap_connect_cfm`, `l2cap_disconn_cfm`, and `l2cap_security_cfm`, plus exported `l2cap_connect_ind`, `l2cap_disconn_ind`, and `l2cap_recv_acldata`. Init/exit are `l2cap_init` and `l2cap_exit`.

## Control flow

Outbound channel setup starts with `l2cap_chan_connect`. It validates PSM/CID and mode, resolves an HCI route, starts or reuses an ACL/LE HCI connection, creates an `l2cap_conn` if needed, checks ECRED grouping limits, attaches the channel, transitions to `BT_CONNECT`, starts the channel timer, and if the HCI link is already connected immediately starts security and signaling. BR/EDR connection-oriented channels wait for information feature-mask negotiation and security before sending `L2CAP_CONN_REQ`; LE credit channels send `L2CAP_LE_CONN_REQ` or grouped `L2CAP_ECRED_CONN_REQ`.

Inbound BR/EDR connection requests arrive on the signaling channel, find a listening PSM through `l2cap_global_chan_by_psm`, validate link security and dynamic CID range, allocate a child channel using `pchan->ops->new_connection`, attach it to the connection, and respond with success, pending, or rejection. If accepted immediately, configuration request negotiation begins. If security or deferred authorization is pending, state moves to `BT_CONNECT2` and later resumes through `l2cap_conn_start`, `l2cap_security_cfm`, or explicit deferred response helpers.

BR/EDR configuration is a two-sided state machine tracked by `chan->conf_state`. `l2cap_config_req` accumulates continuation fragments, parses remote options, sends a configuration response, and starts a local config request if necessary. `l2cap_config_rsp` consumes the peer response, handles success/pending/unknown/unacceptable outcomes, sends revised requests when allowed, and marks `CONF_INPUT_DONE`. Once input and output are done, FCS is selected, ERTM/Streaming state is initialized if needed, timers are cleared, and `chan->ops->ready` is invoked.

LE Credit Based Flow Control setup is shorter: `l2cap_le_connect_req` validates SPSM, MTU, MPS, security, key size, and SCID, creates a child channel, initializes credits, and either defers or replies with `L2CAP_LE_CONN_RSP`. Outbound `l2cap_le_connect_rsp` sets DCID, output MTU, remote MPS, TX credits, and marks ready; authentication/encryption responses can raise the channel security level and retry. ECRED extends this to multiple SCIDs in one request/response and supports grouped deferred accept and later reconfiguration.

Transmission in Basic mode builds one L2CAP PDU and passes it to HCI. Connectionless mode prepends the PSM. LE flow-control modes segment SDUs by remote MPS, queue PDUs, decrement `tx_credits` as packets are sent, suspend when credits are exhausted, and resume when `L2CAP_LE_CREDITS` arrives. ERTM and Streaming segment SDUs into I-frames; Streaming sends immediately without recovery, while ERTM queues, assigns TX sequence numbers, respects the remote transmit window, uses retransmission and monitor timers, and reacts to RR/RNR/REJ/SREJ supervisory frames.

Receive starts at `l2cap_recv_acldata`, which looks up or creates the `l2cap_conn`, holds it safely, locks the connection, and reassembles ACL fragments using `conn->rx_skb` and `conn->rx_len`. Complete L2CAP frames go to `l2cap_recv_frame`, which checks HCI state, validates frame length, rejects blocked LE devices, and dispatches by CID to BR/EDR signaling, LE signaling, connectionless, or data-channel handlers.

Data channel receive uses `l2cap_data_channel` to find the channel by SCID and mode. Basic mode delivers directly after MTU validation. LE credit modes call `l2cap_ecred_data_rcv`, which decrements receive credits, validates SDU/MPS/MTU boundaries, reassembles fragments, delivers completed SDUs, and returns credits according to receiver availability. ERTM/Streaming use `l2cap_data_rcv`, which unpacks control, validates FCS and control bits, enforces MPS, optionally filters, and dispatches into RX/TX state machines.

HCI connection confirmation creates `l2cap_conn`, instantiates fixed channels from global listeners, runs feature negotiation for ACL links, starts LE security/connection parameter update behavior for LE links, and queues pending RX processing. HCI disconnect confirmation tears down users, pending work, RX state, channels, HCI channel, and connection references. Security confirmation resumes pending channels, starts connection signaling, rejects channels, or handles encryption loss according to security level.

## State and persistence behavior

There is no durable storage. All state is runtime kernel memory, HCI state, timers, queues, debugfs, and module parameters.

Global channel state is maintained in `chan_list`, protected by `chan_list_lock`, for listener lookup, PSM uniqueness, fixed-channel discovery, and debugfs enumeration. Per-connection channel state is maintained in `conn->chan_l`, protected by `conn->lock`; per-channel mutable state is protected by `chan->lock` with nesting metadata for lockdep.

Reference counting uses `kref` on both `l2cap_chan` and `l2cap_conn`, plus HCI connection/channel references. Channel add takes a channel reference and usually an HCI connection reference; channel delete reverses those and purges mode-specific queues/timers after teardown. Connection delete cancels timers/work, purges pending RX, unregisters users, destroys the identifier allocator, deletes all channels, deletes the HCI channel, clears `hcon->l2cap_data`, and drops the connection reference.

Signaling identifiers are allocated from `conn->tx_ida` by `l2cap_get_ident` and released by `l2cap_put_ident` when response-type commands are received. BR/EDR reserves higher IDs for external tools, while LE uses the full range.

Timers and work items are persistent only while objects are live: channel connect/disconnect timeout, ERTM retransmission, monitor, and delayed ACK timers; connection feature-info timeout; identity-address update timer; and pending RX work. ERTM state includes sequence counters, unacked frame count, SREJ/retransmission sequence lists, transmit queue, SREJ queue, SDU reassembly buffers, and local/remote busy flags. LE credit state includes `tx_credits`, `rx_credits`, `rx_avail`, `mps`, SDU reassembly fields, and queued TX PDUs.

## Dependencies and integration points

The file depends on Linux kernel networking primitives (`sk_buff`, queues, delayed work, mutexes, rwlocks, IDA, CRC16), Bluetooth core headers (`bluetooth.h`, `hci_core.h`, `l2cap.h`), and SMP security (`smp.h`). It calls HCI APIs including `hci_connect_acl`, `hci_connect_le`, `hci_connect_le_scan`, `hci_send_acl`, `hci_chan_create`, `hci_chan_del`, `hci_conn_security`, `hci_conn_check_link_mode`, `hci_conn_enter_active_mode`, `hci_le_conn_update`, `hci_conn_hash_lookup_handle`, `hci_register_cb`, and `hci_unregister_cb`.

Upper-layer integration happens through `chan->ops` callbacks: `new_connection`, `state_change`, `ready`, `recv`, `close`, `teardown`, `defer`, `suspend`, `resume`, `filter`, `alloc_skb`, `get_sndtimeo`, `set_shutdown`, and `get_peer_pid`. Socket code and other Bluetooth modules use the exported channel APIs and `l2cap_user` registration hooks to bind services to an L2CAP connection.

Debug and observability are provided through a `debugfs` file named `l2cap`, `BT_DBG`/`BT_ERR` logging, module parameters, and state/error callbacks into channel owners.

## Risks and edge cases

This file is concurrency sensitive. HCI callbacks, socket operations, delayed work, and receive paths all touch channels and connections. Bugs in the lock hierarchy among `hci_dev_lock`, `conn->lock`, `chan->lock`, and `chan_list_lock` can deadlock; missing holds around channel lookup can become use-after-free. The fixed-channel discovery loop deliberately releases the global lock before channel locking, so changes there need care.

Protocol parser hardening is central. Signaling handlers validate command lengths, identifiers, CID ranges, MTU/MPS minima, continuation buffers, and response lengths, but many malformed remote inputs reach deep state-machine code. Boundary tests around `cmd_len`, config option lengths, flexible ECRED arrays, frame length fields, ACL continuation order, and FCS trimming are high value.

ERTM is a complex reliability state machine. Sequence wrap, large transmit windows, SREJ queues, duplicate frames, poll/final handling, retry limits, local/remote busy transitions, and resegmentation placeholders are all risky. The code contains explicit comments about double-poll invalid packets and use-after-free risk after delivering skb data to upper layers; these should be treated as regression-sensitive areas.

Credit-based LE flow control must avoid credit overflow, credit starvation, and double frees. `l2cap_ecred_data_rcv` intentionally returns zero after internal error handling because it owns skb cleanup. Changes around this path can easily produce leaks, double frees, or incorrect disconnect behavior. The receive-availability callback can dynamically return credits, so upper-layer buffer accounting affects peer liveness.

Configuration negotiation has retry limits and asymmetric state. Mis-handling `CONF_LOC_CONF_PEND`, `CONF_REM_CONF_PEND`, `CONF_INPUT_DONE`, `CONF_OUTPUT_DONE`, EFS/EWS support, or the `disable_ertm` parameter can leave channels stuck in `BT_CONFIG`, accept unsupported modes, or silently downgrade mode incorrectly.

Security is interleaved with connection setup. BR/EDR and LE have different security APIs and failure results; key-size enforcement depends on encryption state and FIPS level. Regressions can either reject legitimate channels or allow channels before authentication/encryption requirements are met.

Connection teardown is broad. `l2cap_conn_del` cancels work, purges RX, destroys IDA state, unregisters users, tears down all channels, and clears HCI pointers. Any callback that assumes `conn->hchan`, `conn->hcon`, or `chan->conn` remains valid after teardown must hold the right reference and recheck state.

## Test signals

Channel API tests should cover PSM allocation uniqueness, dynamic PSM ranges for BR/EDR versus LE, fixed-channel CID binding, invalid PSM/CID rejection, mode gating by `disable_ertm` and `enable_ecred`, outbound connection state transitions, duplicate CID rejection, and source/destination address propagation from HCI.

BR/EDR signaling tests should cover connect request success, bad PSM, invalid SCID, SCID in use, security pending/failure, deferred authorization, feature-info timeout and command reject, configuration continuation, unknown and unacceptable config options, ERTM/Streaming downgrade, EFS/EWS negotiation, disconnect request/response, echo, and fixed-channel information response.

LE signaling tests should cover LE connection request/response validation for MTU/MPS/SCID/SPSM, security escalation and retry, credit overflow disconnect, ECRED multi-channel request/response with partial failures, deferred grouped ECRED accept, ECRED reconfiguration invalid CID/MTU/MPS cases, disabled ECRED behavior, and connection parameter update acceptance/rejection.

Data-plane tests should cover ACL complete/start/continuation reassembly, short first fragments that do not include the length field, overlong starts, unexpected continuations, pending RX before HCI connected, blocked-device LE drops, Basic MTU enforcement, connectionless PSM dispatch, raw signaling clones, and debugfs enumeration.

ERTM/Streaming tests should cover FCS success/failure, I-frame segmentation/reassembly with all SAR values, malformed SAR ordering, MPS violation disconnect, RR/RNR/REJ/SREJ supervisory handling, retry-limit disconnect, retransmission timeout, monitor timeout, delayed ACK timer, local busy enter/clear, remote busy recovery, duplicate/unexpected/invalid sequence classification, sequence wrap, and behavior when upper-layer receive frees skb immediately.

Lifecycle tests should cover HCI connect confirmation success/failure, fixed-channel child creation, security confirmation paths, encryption loss handling, HCI disconnect cleanup, channel timeout by state, user register/unregister/remove callbacks, pending work cancellation, module init/exit, and module parameter effects.
