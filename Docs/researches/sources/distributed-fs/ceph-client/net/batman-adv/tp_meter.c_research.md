# sources/distributed-fs/ceph-client/net/batman-adv/tp_meter.c

## Purpose
Implements the batman-adv throughput meter, an ICMP-based active measurement facility driven from netlink/batctl. It creates sender and receiver sessions, sends synthetic payload traffic through normal batman-adv unicast routing, ACKs received byte ranges, estimates RTT/RTO, applies TCP-like slow start/congestion avoidance/NewReno fast recovery, reports completion or errors to userspace, and tears sessions down safely.

## Important APIs And Functions
Public APIs are `batadv_tp_meter_init`, `batadv_tp_start`, `batadv_tp_stop`, `batadv_tp_stop_all`, and `batadv_tp_meter_recv`. Important internals include `batadv_tp_session_cookie`, `batadv_tp_cwnd`, `batadv_tp_update_cwnd`, `batadv_tp_update_rto`, `batadv_tp_batctl_notify`, `batadv_tp_list_find`, `batadv_tp_list_find_session`, `batadv_tp_vars_release`, `batadv_tp_list_detach`, sender cleanup/shutdown/finish/timer functions, `batadv_tp_send_msg`, `batadv_tp_recv_ack`, `batadv_tp_avail`, `batadv_tp_send`, `batadv_tp_start_kthread`, receiver timer/shutdown, `batadv_tp_send_ack`, `batadv_tp_handle_out_of_order`, `batadv_tp_ack_unordered`, `batadv_tp_init_recv`, and `batadv_tp_recv_msg`.

## Control Flow
`batadv_tp_start` generates a session id and ICMP uid, rejects inactive meshes, duplicate destination sessions, and `BATADV_TP_MAX_NUM` overflow, allocates a sender `batadv_tp_vars`, initializes cwnd/RTO/session state, adds it to `bat_priv->tp_list`, schedules finish work, and starts `kbatadv_tp_meter`. The sender thread resolves the destination originator and primary interface, arms the RTO timer, schedules test-length completion, and sends `BATADV_TP_MSG` packets while the congestion window has room. ACK processing updates RTT/RTO, resets timers, tracks duplicate ACKs, performs fast retransmit/recovery, advances `last_acked`, increases cwnd, accounts total acknowledged bytes, and wakes the sender.

Receiver flow starts when a `BATADV_TP_MSG` with `BATADV_TP_FIRST_SEQ` arrives. It creates a receiver session if one does not exist, arms an inactivity timer, tracks `last_recv`, stores out-of-order ranges in a sorted list, advances contiguous received bytes, and sends cumulative ACKs echoing the sender timestamp. `batadv_tp_meter_recv` dispatches TP MSG versus ACK and consumes the skb. Stop paths mark senders not-sending, wake or wait for completion, detach receivers, shutdown timers, and synchronize RCU users.

## State And Persistence
All state is volatile per mesh: `bat_priv->tp_list`, `tp_num`, per-session refcounts, role, other endpoint, session bytes, ICMP uid, `sending`, `last_sent`, `last_acked`, `last_recv`, duplicate ACK count, fast recovery state, cwnd/ss_threshold/RTO/SRTT/RTTVAR, unacked out-of-order list, timers, waitqueue, completion, delayed finish work, and a global prerandom payload buffer. No disk persistence exists; userspace receives session result notifications over netlink.

## Dependencies And Integration Points
Depends on `send` for normal routed transmission, `originator` and `hard-interface` for endpoint resolution, `netlink` for throughput meter notifications, the batman-adv event workqueue, kernel kthreads/timers/completions/waitqueues, and `uapi/linux/batadv_packet.h`/`batman_adv.h` TP constants. Receive integration is via `routing.c` ICMP `BATADV_TP` handling.

## Risks
Session lifetime is complex: list membership, timer references, kthread references, and caller references must be balanced. Sender shutdown uses `atomic_dec_and_test(&sending)`, so double-stop races must not underflow into inconsistent reasons. RTO and sequence arithmetic intentionally exercise wrap-around near `BATADV_TP_FIRST_SEQ`; incorrect comparisons can break measurements. Receiver creation requires the first sequence packet, so loss of the first packet prevents session setup. `BATADV_TP_REASON_CANT_SEND` is treated as non-fatal in the sender loop, which can spin through transient routing failures until timeout. Out-of-order list growth is bounded only by traffic/session behavior and memory allocation success.

## Test Signals
Strong signals include start/stop duplicate and max-session tests, injected kthread/allocation failures, ACK-driven cwnd/RTO transitions, duplicate ACK fast recovery, timeout backoff to unreachable, sequence wrap-around, receiver out-of-order merging, inactivity timeout cleanup, netlink result notifications, and `batadv_tp_stop_all` under live sender/receiver sessions. Lockdep, KASAN, and timer/workqueue race tests are especially relevant.
