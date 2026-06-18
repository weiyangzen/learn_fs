# sources/distributed-fs/ceph-client/include/net/lapb.h

Purpose: Defines the internal Link Access Procedure Balanced control block, frame constants, state machine values, timers, queues, and helper prototypes for LAPB over network devices.

Important APIs/types/functions: Constants define LAPB I/S/U control frames, RR/RNR/REJ, SABM/SABME/DISC/DM/UA/FRMR, poll/final bits, FRMR error bits, command/response addresses, states 0-4, default mode/window/timers/retry count, and modulus values. `lapb_frame` stores decoded type, N(R), N(S), command/response, poll/final, and raw control bytes. `lapb_cb` stores netdev, mode, state, sequence variables, conditions, timers, queues, callback table, FRMR data, lock, and refcount.

Control flow: Interface callbacks notify connect/disconnect/data events. Input decodes frames and advances the state machine. Output kicks queued frames, establishes data link, sends enquiries/responses, retransmits, validates acknowledgements, and emits control/FRMR frames. Timers drive retransmission and delayed ACK behavior.

State and persistence: Per-link `lapb_cb` owns volatile protocol state: send/receive sequence counters, ack/write queues, timers, retry counts, window, state, and condition flags.

Dependencies/integration: Depends on public LAPB UAPI/callback definitions, net_device, sk_buff queues, timers, spinlocks, and refcounts.

Risks: Sequence/window validation and timer transitions are protocol-critical; queue cleanup/requeue must avoid skb leaks; debug macro currently prints only if level is below `LAPB_DEBUG`. Test signals include connect/disconnect handshakes, I-frame ack/reject paths, modulo-8/modulo-128 windows, T1/T2 expiry, FRMR generation, busy peer conditions, and queue cleanup on teardown.
