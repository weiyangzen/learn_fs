# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_worker.c

## Purpose

`drbd_worker.c` implements the DRBD sender/worker thread's asynchronous execution path. It handles lower-level bio completions, peer request completions, checksum and verify work, resync request generation, resync completion, outgoing replicated request transmission, bitmap/metadata maintenance work, diskless teardown, and the main worker loop for a connection.

## Important APIs, Types, and Functions

End-I/O handlers include `drbd_md_endio()`, `drbd_peer_request_endio()`, and `drbd_request_endio()`. Peer finalizers split read and write behavior through `drbd_endio_read_sec_final()` and `drbd_endio_write_sec_final()`. Checksum helpers are `drbd_csum_ee()` for peer-request page chains and `drbd_csum_bio()` for local bios.

Resync and verify are driven by `w_resync_timer()`, `resync_timer_fn()`, `make_resync_request()`, `make_ov_request()`, `drbd_resync_finished()`, and `drbd_start_resync()`. Rate control uses `struct fifo_buffer`, `fifo_alloc()`, `drbd_rs_controller()`, `drbd_rs_number_requests()`, and `drbd_rs_controller_reset()`.

Worker callbacks for network responses include `w_e_send_csum()`, `w_e_end_data_req()`, `w_e_end_rsdata_req()`, `w_e_end_csum_rs_req()`, `w_e_end_ov_req()`, and `w_e_end_ov_reply()`. Outgoing local request callbacks include `w_send_out_of_sync()`, `w_send_dblock()`, `w_send_read_req()`, `w_send_write_hint()`, and `w_restart_disk_io()`. Device work is multiplexed by `do_device_work()`, `get_work_bits()`, and `do_unqueued_work()`. `drbd_worker()` is the thread entry point.

## Control Flow

The worker thread waits in `wait_for_work()` for queued sender work or device flag work. It drains batches from `connection->sender_work`, optionally uncorks/corks TCP according to `net_conf`, closes write epochs with barriers when needed, handles signals, and invokes each work callback with a `cancel` argument derived from connection state. A callback returning nonzero while connected triggers `conn_request_state(... C_NETWORK_FAILURE, CS_HARD)`.

Local bio completion in `drbd_request_endio()` maps block status to DRBD request events and calls `__req_mod()` under `req_lock`; it also panics on delayed successful completion of a request previously aborted for disk-timeout safety. Peer request completion in `drbd_peer_request_endio()` records errors, decrements pending bios, and then queues final read replies or moves completed writes to `done_ee` and schedules ack sending.

Resync target flow starts from `drbd_start_resync()`, which runs before-resync helpers, serializes state with `state_mutex`, sets `C_SYNC_SOURCE` or `C_SYNC_TARGET`, initializes counters/marks, resets the resync LRU, chooses checksum-based resync when supported/configured, sends sync UUIDs as required by protocol version, and arms `resync_timer`. Timer work calls `make_resync_request()` for `C_SYNC_TARGET`, scanning dirty bitmap bits, merging adjacent blocks within bio and extent boundaries, honoring thin resync discard granularity, throttling against socket send-buffer pressure, and either sending data requests or reading local data for checksum requests. Online verify uses `make_ov_request()` to send checksum verify requests until capacity or stop sector is reached.

Completion callbacks compare checksums, send data replies or in-sync acknowledgements, update bitmap/resync accounting, and call `drbd_resync_finished()` when all work is done. `drbd_resync_finished()` removes resync LRU entries, computes throughput, checks bitmap out-of-sync weight, updates UUIDs and disk states, emits helper events such as `after-resync-target`, `out-of-sync`, or `unfence-peer`, resets counters, syncs metadata, and moves connection state back to `C_CONNECTED`.

## State and Persistence Behavior

The worker mutates request queues (`read_ee`, `active_ee`, `sync_ee`, `done_ee`), resync counters (`rs_total`, `rs_failed`, `rs_pending_cnt`, `rs_in_flight`, `rs_same_csum`, `ov_left`, `ov_position`), bitmap state, UUID history, and connection send epoch fields. It persists metadata via `drbd_md_sync()`, writes bitmap pages through `drbd_bm_write_lazy()`, `drbd_bm_write()`, and state-triggered bitmap I/O, and destroys local backing state in `drbd_ldev_destroy()` after diskless transition cleanup. `go_diskless()` attempts final bitmap writeout and may set `MDF_FULL_SYNC` if read errors prevented reliable detach persistence.

## Dependencies and Integration Points

This file depends on Linux bio/block APIs, crypto shash, timers, wait queues, socket/TCP corking, partition stats, slab allocation, memcontrol/mm helpers, and DRBD internals from `drbd_int.h`, `drbd_protocol.h`, and `drbd_req.h`. It integrates tightly with `drbd_state.c` through `_drbd_set_state()`, `conn_request_state()`, `drbd_force_state()`, `resume_next_sg()`, and `suspend_other_sg()`. It also uses bitmap, activity-log, transfer-log, UUID, metadata, khelper, and protocol send helpers.

## Risks and Edge Cases

This file is heavily concurrency-sensitive. Endio callbacks may run in IRQ/softirq context and must use irq-safe locking. Worker callbacks may block on network congestion, so several paths free peer request pages before sending to avoid distributed deadlock on buffer exhaustion. Resync throttling must avoid overrunning peer buffers while still making progress. Disk-timeout abort handling intentionally panics on later successful local completion to prevent silent memory corruption. Resync-finish handling retries if LRU entries remain because replies are still queued. Protocol-version branches around sync UUIDs and empty resyncs are compatibility-sensitive.

Memory pressure paths can defer checksum reads, fail verify digest allocation, or fail queued retry allocation. State may change between queued work and execution, so many paths re-check current `device->state` or `connection->cstate`. Incorrect accounting of `rs_pending_cnt`, `unacked_cnt`, `rs_in_flight`, or bitmap bits can hang resync completion or prematurely mark data in sync.

## Test Signals

Test coverage should include local read/write/discard completion success and failure, delayed completion after forced detach, peer read/write request completion, protocol A/B/C ack behavior, checksum-based resync equality and mismatch, thin resync zero-block handling, online verify mismatch reporting and stop sectors, resync pause/resume dependencies, socket congestion requeue, empty resync on older protocol versions, disk failure during resync, bitmap persistence after progress and completion, and worker shutdown draining with `cancel=1`. Logs from resync start/finish, verify mismatch, send failures, diskless transition, metadata sync timer expiry, and network-failure transition are strong integration signals.
