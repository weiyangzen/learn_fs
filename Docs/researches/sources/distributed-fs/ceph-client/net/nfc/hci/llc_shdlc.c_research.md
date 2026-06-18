# sources/distributed-fs/ceph-client/net/nfc/hci/llc_shdlc.c

Purpose: Implements the SHDLC HCI LLC engine, providing connection negotiation, sequencing, acknowledgements, receive ordering, retransmission, remote-not-ready handling, and failure callbacks for HCI transports that require SHDLC framing.

Important APIs and functions: Engine ops are `llc_shdlc_init`, `llc_shdlc_deinit`, `llc_shdlc_start`, `llc_shdlc_stop`, `llc_shdlc_rcv_from_drv`, and `llc_shdlc_xmit_from_hci`. Core protocol helpers include `llc_shdlc_connect`, `llc_shdlc_sm_work`, `llc_shdlc_rcv_i_frame`, `llc_shdlc_rcv_s_frame`, `llc_shdlc_rcv_u_frame`, `llc_shdlc_handle_send_queue`, `llc_shdlc_reset_t2`, and `llc_shdlc_requeue_ack_pending`.

Control flow: Start enters `SHDLC_CONNECTING`, sends RSET frames, waits on a connect wait queue, and transitions through negotiating/half-connected/connected based on UA/RSET reception. Runtime rx queues incoming frames and schedules the state-machine work item. Runtime tx queues HCI skbs; the state machine sends I-frames while window and remote-ready conditions allow, tracks sent frames in `ack_pending_q`, sends RR after T1, and retransmits after T2.

State and persistence: `struct llc_shdlc` stores state, hard fault, timers, wait queue, connect tries/result, negotiated window/SREJ support, send/receive sequence numbers (`ns`, `nr`, `dnr`), receive/send/ack-pending queues, remote-not-ready flag, tx head/tailroom, and callbacks. State persists only in memory for the active LLC instance.

Dependencies and integration points: Registered through `nfc_llc_register(LLC_SHDLC_NAME, ...)`, used by HCI core as an LLC engine. It calls driver `xmit_to_drv`, HCI `rcv_to_hci`, and `llc_failure` on hard faults.

Risks: This file is concurrency-sensitive because timers, rx callbacks, tx callers, and disconnect all converge on `sm_work` and `state_mutex`. Sequence comparisons use modulo-8 helpers and are easy to regress. Requeue/retransmit paths manipulate skb control fields and queues; ownership mistakes can leak or double-free skbs. Connect timeout is very short and retry behavior should match hardware expectations.

Test signals: Simulate RSET/UA negotiation, retry exhaustion, in-order and out-of-order I frames, RR/REJ/RNR handling, T1 ack generation, T2 retransmission, send-window saturation, disconnect cleanup, null-frame link death, and deinit with pending timers/queues.
