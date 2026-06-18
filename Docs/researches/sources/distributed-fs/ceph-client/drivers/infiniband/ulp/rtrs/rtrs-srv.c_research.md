# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-srv.c

## Purpose
Implements the RTRS server kernel module: listener setup, session/path acceptance, exported server APIs, server memory buffer registration, IO request dispatch to upper layers, responses, heartbeat handling, stats, and cleanup.

## Important APIs, Types, And Functions
Exports `rtrs_srv_open()`, `rtrs_srv_close()`, `rtrs_srv_resp_rdma()`, `rtrs_srv_set_sess_priv()`, `rtrs_srv_get_path_name()`, and `rtrs_srv_get_queue_depth()`. Major internal functions include `rtrs_rdma_connect()`, `get_or_create_srv()`, `__alloc_path()`, `create_con()`, `process_info_req()`, `process_io_req()`, `process_read()`, `process_write()`, `send_io_resp_imm()`, `rdma_write_sg()`, `map_cont_bufs()`, and `rtrs_srv_close_work()`.

## Control Flow
`rtrs_srv_open()` registers an IB client; on first IB device, the server creates IP and IB CM listeners. Connect requests validate magic/version/cids, find or create a session by paths UUID, create or find a path by session UUID, allocate QPs, then accept with queue/max IO metadata. After the client sends `INFO_REQ`, the server posts receives, validates pathname uniqueness, registers and advertises memory regions, creates sysfs, marks the path connected, starts heartbeat, and invokes link callbacks. Client IO arrives as RDMA-write-with-immediate into a registered chunk; immediate payload identifies buffer and offset. The server decodes read/write messages, calls `ops.rdma_ev()`, and later upper layers complete via `rtrs_srv_resp_rdma()`, which posts either an immediate status or RDMA writes data back to the client's SG descriptor.

## State And Persistence
State is volatile: global listener context, sessions keyed by paths UUID, paths keyed by session UUID, registered MRs, per-buffer chunks, DMA address array, operation IDs, inflight percpu refs, workqueue close state, and sysfs objects.

## Dependencies And Integration Points
Uses RDMA CM, IB verbs, RTRS core helpers, private wire structs, server sysfs/stats/trace modules, and upper-layer `rtrs_srv_ops`.

## Risks
Important risks are CM lifetime, duplicate path/session handling, zombie connecting paths, memory registration invalidation/rkey refresh, send queue backpressure wait list, operation ID lifetime, and immediate-data bounds. Module parameters must preserve immediate payload encodability.

## Test Signals
Test listener creation on IP and IB port spaces, valid/invalid connection private data, duplicate path rejection, info handshake, read/write callbacks, response queuing under send queue pressure, `always_invalidate` on/off, heartbeat timeout, sysfs disconnect, device removal, and module parameter boundary checks.
