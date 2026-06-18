# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-pri.h

## Purpose
Defines the private RTRS protocol ABI, shared core transport structures, immediate-data encoding, and internal helper prototypes used by both client and server.

## Important APIs, Types, And Functions
Key constants include protocol version, `MAX_SESS_QUEUE_DEPTH`, immediate-data bit widths, service queue depth, max paths, minimum chunk size, heartbeat cadence, magic, and encoded protocol version. Defines `enum rtrs_imm_type`, `enum rtrs_msg_types`, flags, `struct rtrs_rdma_dev_pd`, `struct rtrs_ib_dev`, `struct rtrs_con`, `struct rtrs_path`, `struct rtrs_iu`, wire messages (`rtrs_msg_conn_req/rsp`, `info_req/rsp`, `rkey_rsp`, `rdma_read/write`, `rtrs_sg_desc`), core helper prototypes, immediate packing helpers, and sysfs stats macros.

## Control Flow
Client and server agree on connection private data, info exchange, IO request layout, immediate-data payloads, and heartbeat messages through this header. `rtrs_to_imm()` reserves 4 high bits for type and 28 bits for payload; IO response payloads split errno and message id.

## State And Persistence
Defines in-memory connection/path/IU state and on-wire little-endian protocol structures. No persistent storage is used, but changes here are protocol compatibility changes.

## Dependencies And Integration Points
Includes RDMA CM/verbs, UUID, and public `rtrs.h`. Core implementation in `rtrs.c` provides the declared helpers; client/server implementations consume both protocol structures and helper functions.

## Risks
Wire layout, endian annotations, private-data size limits, and immediate-data bit packing are critical. Queue depth and chunk size must fit in the 28-bit immediate payload. Stats macros depend on kobject layout.

## Test Signals
Version negotiation, malformed message rejection, queue-depth/chunk-size boundary tests, endian-sensitive interop, heartbeat traffic, and build coverage across client/server/core validate this header.
