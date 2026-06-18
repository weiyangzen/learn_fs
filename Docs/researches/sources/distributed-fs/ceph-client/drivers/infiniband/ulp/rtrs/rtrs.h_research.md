# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs.h

## Purpose
Defines the public RTRS API used by kernel upper layers to open client sessions, submit RDMA requests, run servers, and convert addresses.

## Important APIs, Types, And Functions
Forward-declares opaque client/server handles and defines `struct rtrs_addr`, client link events, `struct rtrs_clt_ops`, permit wait/type enums, `struct rtrs_clt_req_ops`, `struct rtrs_attrs`, server link events, and `struct rtrs_srv_ops`. Public functions cover client open/close/permit/request/query/direct CQ polling; server open/close/respond/set private data/query path name/query depth; and address string conversions.

## Control Flow
Client users call `rtrs_clt_open()`, get permits, submit `rtrs_clt_request()` with control kvec and optional SG data, receive completion through `conf_fn`, and return permits. Server users call `rtrs_srv_open()`, receive link callbacks and RDMA events through `rtrs_srv_ops`, then complete each event with `rtrs_srv_resp_rdma()`.

## State And Persistence
The header exposes opaque handles only; implementation state is private and volatile. User private pointers are stored in sessions and returned to callbacks.

## Dependencies And Integration Points
Depends on Linux socket and scatterlist types. It is the API boundary between RTRS and consumers such as RNBD-like block/storage layers.

## Risks
Callback contracts are central: server `rdma_ev()` returning nonzero triggers error response, while async success requires later response with the provided op id. Permit misuse can stall or corrupt queue slot ownership. Address strings must use supported prefixes.

## Test Signals
Compile external consumers, verify callback ordering, permit exhaustion/release, request size limits surfaced by query attrs, server response semantics, link events, and address conversion error handling.
