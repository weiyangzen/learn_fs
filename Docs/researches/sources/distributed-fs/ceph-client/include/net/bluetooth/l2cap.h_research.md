# sources/distributed-fs/ceph-client/include/net/bluetooth/l2cap.h

## Purpose

`l2cap.h` defines the Bluetooth L2CAP protocol constants, wire structures, channel/connection state, retransmission/flow-control state machines, socket private data, timer helpers, and public L2CAP core APIs.

## Important APIs, Types, and Functions

The header defines default MTUs, flush/ERTM/window/retransmission/monitor/ack/connect/info/move/security timeouts, socket address and options, link-mode bits, signaling command codes, feature masks, FCS options, fixed channels, control-field masks/shifts, supervisory/SAR values, rejection/result/status codes, PSM/CID ranges, configuration option structures, ERTM/streaming/LE/ext-flow modes, QoS/EFS data, LE credit-based and enhanced credit-based connection/reconfigure structures, and info/move/update messages.

`struct l2cap_chan` is the per-channel state object: HCI connection pointer, kref, nesting, state, source/destination addresses and CIDs, MTUs, mode/type/policy/security, configuration buffers/counters, FCS/window/retransmission/MPS/credit settings, receive availability, TX/RX state, config/connection flags, sequence numbers, SDU reassembly, remote/local flow specs, delayed timers, TX/SREJ/retransmission queues, global/connection lists, protocol private data, ops table, and mutex. `struct l2cap_ops` lets socket or fixed-channel users provide callbacks for new connections, receive, teardown, close, state changes, ready/defer/resume/suspend/shutdown, send timeout, peer PID, skb allocation, and filtering. `struct l2cap_conn` binds an HCI connection/channel to L2CAP-level MTU, feature/fixed-channel state, info timer, RX reassembly, TX ident allocator, pending RX work, SMP channel, channel list, users, lock, and kref.

Inline helpers manage channel locks, delayed timer hold/put pairing, sequence arithmetic, and no-op/default ops. Exported APIs initialize sockets, identify L2CAP sockets, defer responses, add PSM/SCID, create/close/connect/reconfigure/send channels, mark busy/RX availability, check security, initialize ERTM, add/list/delete channels, manage connection refs, and register L2CAP users.

## Control Flow

L2CAP receives ACL data from HCI, reassembles L2CAP PDUs, dispatches signaling commands on fixed channels, creates/configures connection-oriented channels, and passes payloads to `l2cap_ops`. Connection setup negotiates PSM/CID, MTU, RFC mode, FCS, extended windows, EFS, and credit parameters before channels become ready. ERTM and streaming paths use TX/RX states, sequence numbers, SREJ/retransmission queues, and retrans/monitor/ack timers. LE credit-based channels track local/remote credits and can use enhanced credit-based multi-CID setup. Timer helpers intentionally hold channel refs while delayed work is pending.

## State and Persistence Behavior

All state is runtime-only in L2CAP channels, HCI-backed L2CAP connections, socket private data, queues, delayed work, sequence lists, and registered users. Channel refs use `kref`; timer scheduling adds/releases references to keep channels alive. No file-backed persistence exists.

## Dependencies and Integration Points

The header depends on Bluetooth common/HCI types, sk_buffs, atomics, unaligned helpers, mutexes, krefs, IDA, workqueues, and sockets. It integrates with HCI ACL receive/send, SMP, ATT, RFCOMM, fixed channels, LE credit sockets, BR/EDR sockets, and Bluetooth management/security.

## Risks and Edge Cases

Timer ref pairing is subtle: setting a timer that was not already pending holds the channel, and clearing a pending timer drops it. Sequence arithmetic depends on `tx_win_max + 1` and must match normal versus extended control fields. Flexible arrays in enhanced credit structures require length checks and maximum CID enforcement. `__set_ack_timer(c)` references `chan->ack_timer` in the macro body, so call sites must provide a visible `chan` identifier despite the `c` parameter. ERTM/SREJ/retransmission state has many race-prone transitions with local/remote busy flags.

## Test Signals

Test BR/EDR and LE connect/config/disconnect flows, fixed channels, dynamic PSM and SCID allocation, MTU/MPS/window/FCS negotiation, ERTM retransmission and SREJ behavior, streaming mode, LE credits and enhanced credit multi-CID limits, reconfigure validation, timer hold/put balance, busy/RX availability backpressure, security checks, HCI disconnect cleanup, malformed signaling PDUs, and disabled/forced ERTM or ECRED module parameters.
