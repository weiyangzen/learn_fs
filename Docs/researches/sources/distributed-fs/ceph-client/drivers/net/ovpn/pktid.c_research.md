# sources/distributed-fs/ceph-client/drivers/net/ovpn/pktid.c

Purpose: Implements transmit packet-ID initialization and receive replay-window validation for OpenVPN AEAD packet IDs.

Important APIs, types, and functions: `ovpn_pktid_xmit_init()` initializes transmit sequence numbers to 1. `ovpn_pktid_recv_init()` clears receive state and initializes its spinlock. `ovpn_pktid_recv()` validates a `(pkt_id, pkt_time)` pair against monotonic time, zero-ID rejection, a sliding replay bitmap, and an expiry-driven floor.

Control flow: Receive validation locks the packet-ID state, expires old backtrack acceptance by raising `id_floor`, resets the replay window when packet time moves forward, rejects time rollback, accepts strict next IDs, handles forward jumps by clearing skipped bitmap positions, and handles backtracks only if inside the retained window, above `id_floor`, and not already seen.

State and persistence behavior: State lives in `struct ovpn_pktid_recv` inside a crypto key slot and is runtime-only. `expire` uses jiffies to narrow the acceptable backtrack range after `PKTID_RECV_EXPIRE`. `max_backtrack` records observed replay depth for diagnostics even though it is not exported here.

Dependencies and integration points: It depends on atomic/jiffies/spinlock primitives and protocol nonce sizing from `pktid.h`/`proto.h`. Crypto decrypt paths use this to prevent replay before accepting data-channel packets.

Risks and edge cases: Sequence ID zero is invalid and transmit wrap must force key renewal elsewhere. Time rollback is rejected, so userspace/key time generation must be monotonic per key. The bitmap math relies on power-of-two `REPLAY_WINDOW_SIZE`. Expiry updates `id_floor` only when validation runs, not by timer.

Test signals: Unit-style tests should cover zero ID, in-order sequences, forward jumps smaller/larger than the window, duplicate backtracks, backtracks below the floor after expiry, packet-time advance reset, packet-time rollback rejection, and concurrent receive validation under softirq context.
