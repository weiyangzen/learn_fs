# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs.c

## Purpose
Implements common RTRS core helpers shared by client and server: IU allocation/posting, CQ/QP creation, heartbeat transport, address parsing/formatting, and RDMA device/protection-domain pooling.

## Important APIs, Types, And Functions
Exports IU helpers (`rtrs_iu_alloc/free/post_recv/post_send/post_rdma_write_imm`), empty receive posting, `rtrs_cq_qp_create/destroy()`, heartbeat helpers (`rtrs_init_hb/start/stop/send_hb_ack()`), address helpers (`rtrs_addr_to_sockaddr()`, `sockaddr_to_str()`, `rtrs_addr_to_str()`), and device pool helpers (`rtrs_rdma_dev_pd_init/deinit()`, `rtrs_ib_dev_find_or_add()`, `rtrs_ib_dev_put()`).

## Control Flow
IU allocation creates DMA-mapped buffers with completion callbacks. Send helpers optionally chain caller-provided WRs before/tail after RTRS WRs. CQ/QP creation uses a dedicated CQ for direct poll queues and CQ pool for interrupt/workqueue contexts. Heartbeat work sends RDMA-write-with-immediate heartbeat messages on connection 0, tracks missed acknowledgements, and calls the side-specific error handler when the missed limit is exceeded.

## State And Persistence
Maintains per-connection QP/CQ fields, heartbeat delayed work fields in `struct rtrs_path`, and a refcounted pool of `struct rtrs_ib_dev` entries keyed by IB device GUID with shared PDs. No disk persistence exists.

## Dependencies And Integration Points
Uses RDMA CM, IB verbs, inet address parsing, RTRS private definitions, and logging macros. Client/server modules provide pool init/deinit callbacks for IB event handlers.

## Risks
DMA map/unmap symmetry, WR chain correctness, CQ ownership differences, heartbeat false positives, address parsing prefixes, and `node_guid`-based device pooling are key risk areas.

## Test Signals
Validate IU allocation failure unwind, zero-length SG rejection, CQ/QP creation for softirq/direct/workqueue poll contexts, heartbeat ack/loss recovery, address parse/format round trips for `ip:` and `gid:`, and refcounted PD cleanup on module unload.
