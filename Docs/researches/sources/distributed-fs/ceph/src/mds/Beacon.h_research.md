# sources/distributed-fs/ceph/src/mds/Beacon.h

## Purpose
This header declares `Beacon`, the MDS monitor heartbeat and health-report dispatcher.

## Important APIs, Types, and Functions
`Beacon` derives from `Dispatcher` and exposes lifecycle (`init`, `shutdown`), messenger dispatch (`ms_dispatch2` and reset/refused stubs), MDSMap and health notifications, beacon sending, desired-state setters/getters, lagginess queries, and `send_and_wait()`. It uses `ceph::coarse_mono_clock` aliases for timing.

Important fields include `mutex`, `sender`, `cvar`, `last_send`, `beacon_interval`, `finished`, `MonClient *monc`, copied daemon identity and epoch, `CompatSet`, `want_state`, sequence tracking (`last_seq`, `seq_stamp`, `last_acked_stamp`), laggy tracking, and `MDSHealth health`. Two public booleans record missed ack/internal heartbeat dump signals.

## Control Flow
The header documents why a separate beacon class exists: it decouples monitor liveness messages from the main MDS lock. Public notification methods copy data into Beacon-owned state; private `_send()` and `_notify_mdsmap()` perform locked internal updates.

## State and Persistence Behavior
All state is volatile process state. The key invariant is that data needed for beacon messages is duplicated under Beacon's own mutex so the sender thread does not need to take the main MDS lock.

## Dependencies and Integration Points
It depends on Ceph dispatcher/messenger types, MDSMap daemon states, `MMDSBeacon` health structures, `MonClient`, and `MDSRank`. It is part of MDS daemon liveness and health integration with monitors.

## Risks and Test Signals
Header-level risks are locking discipline and stale copied fields. Tests and static analysis should verify every shared field is accessed under `mutex`, sender thread lifetime is bounded by `shutdown()`, and `get_want_state()` is safe concurrently with state updates.
