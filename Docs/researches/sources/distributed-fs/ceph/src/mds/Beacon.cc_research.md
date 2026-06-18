# sources/distributed-fs/ceph/src/mds/Beacon.cc

## Purpose
This file implements the MDS beacon subsystem. A `Beacon` runs a separate sender thread so monitor heartbeats and health reports continue even when the main MDS is busy holding its own lock. It sends `MMDSBeacon` messages to monitors, tracks acknowledgements and lagginess, and snapshots health metrics from `MDSRank`.

## Important APIs, Types, and Functions
`Beacon::init()` copies the initial MDSMap epoch and starts the `mds-beacon` thread. `shutdown()` stops and joins that thread. `ms_dispatch2()` receives monitor beacon replies and sends them to `handle_mds_beacon()`. `send()` and `send_and_wait()` submit immediate beacons, with the latter waiting for ack or timeout. `_send()` constructs `MMDSBeacon` with fsid, gid, daemon name, epoch, desired state, sequence, features, health, compat set, target filesystem, and boot-time sys info. `notify_mdsmap()` and `set_want_state()` update copied epoch/state under the beacon lock. `is_laggy()` compares time since last ack to `mds_beacon_grace`.

`notify_health()` is the broad health collector. It copies health metrics for dummy injection, damage table entries, slow journal trimming, late cap release, client cache recall pressure, oldest client tid/flush lag, slow MDS requests, slow metadata IOs, read-only mode, broken root squash clients, oversized cache, laggy clients deferred due to laggy OSDs, and replay progress estimates.

## Control Flow
The sender thread loops until `finished`. On each iteration it computes time since last send; near the beacon interval it calls `_send()`, otherwise it waits for the remaining interval. If `_send()` failed because the internal heartbeat map is unhealthy, the next wait interval is shortened to 500 ms. If the condition-variable wait times out after a send, it records a missed ack. Replies are matched by sequence number in `seq_stamp`; matching replies update `last_acked_stamp`, compute RTT, clear laggy state when RTT is below grace, erase old sequence stamps, and wake waiters.

`_send()` refuses to send when Ceph's internal heartbeat map is unhealthy, intentionally allowing monitors to see lagginess instead of masking a wedged MDS. Otherwise it increments `last_seq`, records the timestamp, builds a beacon message, optionally adds boot sys-info, sends through `MonClient`, and updates `last_send`.

## State and Persistence Behavior
Beacon state is in-memory and protected by `mutex`: sender thread state, condition variable, last send/ack times, sequence stamps, desired MDS state, MDSMap epoch, compat set, laggy markers, and copied health metrics. It does not persist data directly, but monitor-visible daemon liveness and health state are derived from this state.

## Dependencies and Integration Points
It integrates with `MonClient`, messenger dispatch, `MMDSBeacon`, MDSMap, `MDSRank`, `MDLog`, `MDCache`, `Locker`, `SessionMap`, `Objecter`, `HeartbeatMap`, config options, and cluster log health codes. It assumes `notify_health()` is called with the MDS lock held and asserts that condition.

## Risks and Test Signals
Risks include sender-thread shutdown races, stale copied MDSMap state, missed ack false positives, holding beacon mutex while traversing health data, and summary threshold mistakes that hide specific client metrics. Tests should cover ack matching/out-of-order replies, `send_and_wait()` timeout, heartbeat unhealthy skip, laggy enter/exit, state transitions via `set_want_state()`, shutdown during wait, and health metric generation for each major warning family.
