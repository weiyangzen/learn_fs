# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-clt.h

## Purpose
Defines the private client-side RTRS model shared by client implementation, client stats, sysfs, and trace code.

## Important APIs, Types, And Functions
Declares `enum rtrs_clt_state` for connection lifecycle and `enum rtrs_mp_policy` for path selection. Core data structures are `struct rtrs_clt_stats`, `struct rtrs_clt_con`, `struct rtrs_permit`, `struct rtrs_clt_io_req`, `struct rtrs_rbuf`, `struct rtrs_clt_path`, and `struct rtrs_clt_sess`. Inline helpers convert embedded core types (`to_clt_con()`, `to_clt_path()`), compute permit size, and locate a permit in the packed permit arena. It also declares sysfs entry points, reconnect/path management hooks, IB event handling, and client stats helpers implemented in sibling files.

## Control Flow
The header encodes ownership boundaries. `rtrs-clt.c` owns session/path/request state transitions; stats code owns the `rtrs_clt_stats` counters; sysfs code manipulates reconnect and dynamic path operations through declared hooks. Permits carry both a `mem_id` and immediate-data offset, tying request slots to server remote buffers.

## State And Persistence
All state is volatile kernel memory exposed partly through sysfs. `rtrs_clt_sess` persists for the open session and owns paths, global queue parameters, permit map, callbacks, and kobjects. `rtrs_clt_path` persists per RDMA route and owns connection arrays, remote buffer descriptors, request slots, reconnect work, heartbeat state via embedded `rtrs_path`, and path stats.

## Dependencies And Integration Points
Includes `rtrs-pri.h` and Linux device APIs. It is consumed by client core, client sysfs/stats, and potentially trace code.

## Risks
The types embed concurrency-sensitive fields: RCU lists, per-CPU path pointers, wait queues, work items, refcounted IO requests, and kobjects. Any layout or semantic change affects multiple compilation units.

## Test Signals
Build coverage for all client sibling files, sysfs path operations, stats reset/read, multipath IO, and reconnect/failover behavior validates this contract.
