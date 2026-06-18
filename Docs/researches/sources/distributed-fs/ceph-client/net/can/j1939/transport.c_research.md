# sources/distributed-fs/ceph-client/net/can/j1939/transport.c

## Purpose
Implements SAE J1939 transport protocol handling for CAN: simple single-frame sends, TP connection-managed and broadcast transfers, and ETP extended transfers. It segments outgoing payloads into 7-byte data packets, reassembles incoming multi-packet payloads, handles RTS/CTS/DPO/EOMA/ABORT control frames, and reports transport progress or failure back to J1939 sockets.

## Important APIs, Types, and Functions
The file operates on `struct j1939_session`, `struct j1939_priv`, `struct j1939_sk_buff_cb`, and socket-owned `sk_buff` queues. Exported or externally used entry points include `j1939_tp_send()`, `j1939_session_activate()`, `j1939_tp_recv()`, `j1939_simple_recv()`, `j1939_cancel_active_session()`, `j1939_tp_init()`, `j1939_session_get()`, `j1939_session_put()`, `j1939_session_skb_queue()`, and `j1939_session_timers_cancel()`. Internal control paths include `j1939_session_tx_rts()`, `j1939_session_tx_cts()`, `j1939_session_tx_dpo()`, `j1939_session_tx_dat()`, `j1939_session_tx_eoma()`, `j1939_xtp_rx_rts()`, `j1939_xtp_rx_cts()`, `j1939_xtp_rx_dpo()`, `j1939_xtp_rx_dat()`, `j1939_xtp_rx_eoma()`, and `j1939_xtp_rx_abort()`. `enum j1939_xtp_abort` maps wire abort reasons to Linux errno values.

## Control Flow
Outgoing payloads enter through `j1939_tp_send()`, which rejects reserved TP/ETP PGNs, chooses `J1939_SIMPLE`, `J1939_TP`, or `J1939_ETP` by size, forbids broadcast ETP, fixes address-claim state, creates a refcounted session, and sets packet counters. `j1939_session_activate()` inserts the session into `priv->active_session_list` unless another active session with the same address tuple and direction exists. Timers drive transmission: simple sessions clone and send the original skb, TP/ETP transmitters send RTS, react to CTS/DPO, transmit data packets, and finish on EOMA. Receivers allocate a fresh skb sized to the advertised payload, validate size and PGN, send CTS windows, copy incoming data into the reassembly skb, and complete on BAM final data or EOMA.

Incoming frames enter through `j1939_tp_recv()`. The PGN selects data or control handling and sets TP versus ETP type. `j1939_tp_cmd_recv()` dispatches control commands in both local directions because looped-back frames can confirm local sends. Bad PGNs, duplicate sequence/control frames, unexpected data, timeouts, and resource limits trigger aborts and timer-driven cleanup.

## State and Persistence
Session state is in memory only. Sessions are kref-managed; timers take references and release them from callbacks. Active sessions are protected by `priv->active_session_list_lock`; queued skb fragments use the skb queue lock. Important mutable fields include `state`, `err`, `last_cmd`, `last_txcmd`, `transmission`, `tskey`, `pkt.total`, `pkt.rx`, `pkt.tx`, `pkt.tx_acked`, `pkt.last`, `pkt.block`, and `pkt.dpo`. Static tunables `j1939_tp_block`, `j1939_tp_packet_delay`, and `j1939_tp_padding` influence packet windowing, inter-packet delay, and padding. There is no persistent storage; hardware/bus effects are CAN frames already transmitted.

## Dependencies and Integration Points
Depends on PF_CAN/J1939 private helpers in `j1939-priv.h`, CAN skb extensions, address-claim fixups, J1939 socket queues/error queues, `j1939_send_one()`, and network-device registration state. It integrates with local loopback semantics, socket timestamp keys, per-interface J1939 private state, and netdevice shutdown cancellation.

## Risks
The high-risk areas are refcount/timer interactions, active-session list races, handling of locally looped-back frames, and wire-state validation. Duplicate RTS handling intentionally forces receiver deactivation in one corner case to avoid an abort timer being canceled without restart. Miscomputed packet offsets can read/write outside a queued skb, guarded by explicit overflow checks. Broadcast sessions do not send aborts, so receiver resource failures are less visible. Error values sometimes store positive errno constants rather than negative values, matching existing error-queue conventions but worth review when consumed by callers.

## Test Signals
Strong signals include multi-packet unicast TP success with RTS/CTS/EOMA, BAM broadcast receive completion, ETP transfers over the TP maximum, ETP broadcast rejection, timeout-to-abort paths, CTS(0) hold behavior, duplicate/bad-sequence aborts, concurrent same-address session rejection, CAN TX queue `-ENOBUFS` retry behavior, local loopback confirmation for simple and segmented sends, netdevice unregister cancellation, and socket error-queue events for TX/RX ACK and abort.
