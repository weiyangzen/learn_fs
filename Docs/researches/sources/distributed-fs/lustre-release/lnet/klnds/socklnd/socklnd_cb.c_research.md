# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/socklnd_cb.c

## Purpose
Implements socklnd's active data path and worker threads: TX allocation/free, LNet send entry, packet launch, RX state machine, scheduler loop, socket-read/write callbacks, hello negotiation wrappers, connection daemon loop, reconnect/backoff logic, keepalive, timeout scanning, ENOMEM retry, and reaper destruction.

## Important APIs and functions
TX functions include `ksocknal_alloc_tx`, `ksocknal_alloc_tx_noop`, `ksocknal_free_tx`, `ksocknal_tx_done`, `ksocknal_txlist_done`, `ksocknal_send`, `ksocknal_launch_packet`, `ksocknal_queue_tx_locked`, and `ksocknal_tx_prep`. RX functions include `ksocknal_new_packet`, `ksocknal_process_receive`, and `ksocknal_recv`. Worker entry points are `ksocknal_scheduler`, `ksocknal_connd`, and `ksocknal_reaper`. Connection setup helpers include `ksocknal_send_hello`, `ksocknal_recv_hello`, and `ksocknal_connect`.

## Control flow
`ksocknal_send` converts an LNet message into a `ksock_tx`, extracts page fragments, marks zero-copy eligibility, and calls `ksocknal_launch_packet`. Launch finds an existing matching connection, creates an on-demand peer when possible, starts connection attempts, or queues the TX on the peer until a connection arrives. Socket callbacks only mark readiness and queue the conn on the scheduler. The scheduler alternates RX and TX work: RX reads headers/payload fragments, calls `lnet_parse`, waits for `ksocknal_recv` to provide payload buffers, verifies checksums, handles zero-copy requests, and finalizes LNet messages. TX packs headers, sends nonblocking header/page fragments, handles partial sends, ENOMEM retry, zero-copy request tracking, health status, and connection closure on hard errors.

## State and persistence
State is volatile and list based. TX descriptors carry residual bytes, deadlines, connection refs, and health status until completion. Connections carry readiness/scheduled flags for each direction. `ksnd_connd_routes` and `ksnd_connd_connreqs` feed connection daemons. The reaper owns deathrow, zombie, and ENOMEM lists and periodically scans peer hash buckets for socket errors, RX/TX deadlines, stale queued TXs, stale zero-copy requests, and keepalive needs.

## Dependencies and integration points
Calls `socklnd.c` for peer/connection lifecycle, `socklnd_proto.c` through `ksock_proto`, `socklnd_lib.c` for socket I/O, LNet parse/finalize/notify APIs, acceptor connect helpers, and libcfs scheduler/CPT utilities.

## Risks and test signals
Most risks are race related: callbacks racing termination, `lnet_parse` racing `ksocknal_recv`, scheduler refs, ENOMEM reschedule, zero-copy ACK loss, and connection attempts racing passive accepts. Tests should exercise partial reads/writes, socket EOF mid-message, checksum injection, send error simulation, zero-copy request/ACK ranges, keepalive NOOPs, peer timeout detection, connd dynamic grow/shrink, and orderly unload with active traffic.
