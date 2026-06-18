# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt.c

## Purpose
Implements the RTRS client kernel module: session/path creation, RDMA CM connection setup, permits, RDMA read/write request submission, failover, reconnect, heartbeat handling, and exported client APIs from `rtrs.h`.

## Important APIs, Types, And Functions
Exports `rtrs_clt_open()`, `rtrs_clt_close()`, `rtrs_clt_get_permit()`, `rtrs_clt_put_permit()`, `rtrs_clt_request()`, `rtrs_clt_rdma_cq_direct()`, and `rtrs_clt_query()`. Internal key paths include `init_path()`, `init_conns()`, `rtrs_send_path_info()`, `rtrs_rdma_conn_established()`, `rtrs_clt_read_req()`, `rtrs_clt_write_req()`, `complete_rdma_req()`, `fail_all_outstanding_reqs()`, and reconnect/close work handlers. It uses `struct rtrs_clt_sess`, `struct rtrs_clt_path`, `struct rtrs_clt_con`, `struct rtrs_clt_io_req`, and `struct rtrs_permit` from `rtrs-clt.h`.

## Control Flow
Open allocates a client device, creates one path per address, establishes all CM/QP connections, sends an info request over connection 0, receives exported server buffers, posts receive WRs, creates sysfs path files, then allocates global permits. Requests acquire a permit externally, choose a connected path by multipath policy, copy user control payload into an IU, map/fast-register SG data if present, and send an RDMA write-with-immediate to the server. Completions decode immediate payloads, process IO responses, handle rkey refresh responses, invalidate local MRs when needed, unmap DMA, and call the upper-layer confirmation callback.

## State And Persistence
State is in memory only: path state machine, RCU path list/per-CPU current path, bitmap-backed permits, request arrays, stats, workqueue items, and sysfs kobjects. Reconnects preserve path/session identity, but connection and memory registration state is rebuilt.

## Dependencies And Integration Points
Depends on RDMA CM, IB verbs, RTRS core helpers, private wire format, client stats/sysfs/trace modules, and upper-layer callbacks. It integrates with sysfs for manual path operations and with heartbeats from `rtrs.c`.

## Risks
High-risk areas are request lifetime/refcounting around local invalidation, reconnect races, failover using copied request metadata, immediate-data bit packing, send/recv WR sizing, and RCU/per-CPU path pointer replacement. Queue depth changes across reconnect deliberately disable auto-reconnect.

## Test Signals
Exercise module load/unload, open/close with multiple paths, read/write success and error callbacks, permit exhaustion/wakeups, server disconnect and reconnect, device removal, sysfs reconnect/path removal, multipath policies, direct CQ polling, malformed info/rkey responses, and MR invalidation paths.
