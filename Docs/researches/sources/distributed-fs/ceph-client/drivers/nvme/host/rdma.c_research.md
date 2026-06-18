# sources/distributed-fs/ceph-client/drivers/nvme/host/rdma.c

## Purpose

`rdma.c` is the NVMe over Fabrics RDMA host transport. It registers the `rdma` fabrics transport, creates controllers from fabrics options, resolves RDMA addresses/routes, creates RDMA CM IDs, completion queues, queue pairs, memory-registration pools, and NVMe queues, maps blk-mq requests into keyed SGL or inline capsules, handles send/receive completions, supports protection information through signature memory regions, and performs reconnect/error recovery for remote NVMe controllers.

## Important APIs, types, and functions

- `struct nvme_rdma_device` wraps an RDMA `ib_device`, protection domain, reference count, and maximum inline segment count. Instances are shared by controllers using the same RDMA device.
- `struct nvme_rdma_queue` represents one fabrics queue with response ring, queue size, command capsule size, RDMA CM ID, QP, CQ, state flags, queue lock, PI support, and CM completion state.
- `struct nvme_rdma_ctrl` embeds `struct nvme_ctrl` and stores queues, admin/I/O blk-mq tag sets, reconnect and error work, async-event SQE, RDMA device, address tuples, max fast-register pages, and queue mapping counts.
- `struct nvme_rdma_request` is request private data. It stores NVMe request/core command state, SQE DMA mapping, result/status, request refcount, send SGEs, memory-registration work request, data and metadata SG tables, selected queue, MR, and signature-MR flag.
- Queue setup uses `nvme_rdma_alloc_queue`, `nvme_rdma_create_queue_ib`, `nvme_rdma_create_cq`, `nvme_rdma_create_qp`, `nvme_rdma_start_queue`, and `nvme_rdma_conn_established`.
- Controller setup uses `nvme_rdma_alloc_ctrl`, `nvme_rdma_create_ctrl`, `nvme_rdma_setup_ctrl`, `nvme_rdma_configure_admin_queue`, and `nvme_rdma_configure_io_queues`.
- Request path uses `nvme_rdma_queue_rq`, `nvme_rdma_map_data`, `nvme_rdma_dma_map_req`, `nvme_rdma_map_sg_inline`, `nvme_rdma_map_sg_single`, `nvme_rdma_map_sg_fr`, `nvme_rdma_map_sg_pi`, `nvme_rdma_post_send`, and `nvme_rdma_post_recv`.
- Completion and recovery use `nvme_rdma_recv_done`, `nvme_rdma_process_nvme_rsp`, `nvme_rdma_send_done`, `nvme_rdma_inv_rkey_done`, `nvme_rdma_end_request`, `nvme_rdma_complete_rq`, `nvme_rdma_error_recovery`, and reconnect work functions.
- Registration surfaces are `nvme_rdma_transport`, `nvme_rdma_ib_client`, `nvme_rdma_ctrl_ops`, `nvme_rdma_mq_ops`, and `nvme_rdma_admin_mq_ops`.

## Control flow

Module initialization registers an RDMA IB client and then the NVMe fabrics transport. A user-space fabrics connect request calls `nvme_rdma_create_ctrl`, which allocates a controller, fills defaults such as RDMA port, parses remote and optional local addresses, rejects duplicate connects unless allowed, initializes reconnect/error/reset work, allocates queue array storage, initializes the generic NVMe controller, adds it to the core, marks it `CONNECTING`, and calls `nvme_rdma_setup_ctrl`.

Admin setup allocates queue zero, performs RDMA CM address and route resolution, creates CQ/QP/MR pools and response ring, connects the admin queue through `nvmf_connect_admin_queue`, enables the controller, sets max segment and integrity limits from RDMA capabilities, unquiesces the admin queue, and finishes NVMe core initialization. I/O setup asks the controller for an I/O queue count, maps fabrics read/write/poll queue counts, allocates queues, creates the I/O tag set on first setup, starts connect commands for queues, and updates blk-mq hardware queue counts on reconnect.

RDMA connection flow is event-driven by `nvme_rdma_cm_handler`. `ADDR_RESOLVED` creates RDMA resources and starts route resolution. `ROUTE_RESOLVED` sends an RDMA connect request with NVMe RDMA private data describing queue ID, host receive queue size, host submission queue size, and controller ID for I/O queues. `ESTABLISHED` posts all response receives and completes queue setup. Rejection and route/connect/address failures set `cm_error` and release the waiter.

Request submission maps the command capsule for DMA, asks the NVMe core to fill the command, starts the request, decides whether signature MR is needed for T10 PI, maps payload data, and posts a send. Payload mapping always sets NVMe SGL mode. Empty payloads get a null keyed SGL. Small write payloads may be sent inline when the target supports inline data and the capsule has room. A single mapped segment may use an unsafe global rkey only when the module is configured with `register_always=false`; otherwise fast registration is used. PI requests use an integrity MR and signature attributes to let the HCA generate or verify protection information.

Completions are split between receive and send work completions. A receive completion validates length, syncs the response CQE for CPU, special-cases async events, finds the blk-mq request by command ID, stores NVMe status/result, handles remote invalidation if present, optionally posts local invalidation for registered MRs, and then decrements the request refcount. A send completion also decrements the refcount. Only when both sides complete does `nvme_rdma_complete_rq` unmap data, check PI status if needed, unmap the command capsule, and call `nvme_complete_rq`.

Error recovery transitions a live controller to `RESETTING`, queues recovery work, tears down I/O and admin queues without removing tag sets, stops authentication and keep-alive, marks the controller `CONNECTING`, and either schedules reconnect based on fabrics policy or deletes the controller. Reset work follows a similar shutdown and setup path. RDMA device removal finds controllers using that IB device and deletes them.

## State and persistence behavior

Controller state follows the generic NVMe state machine: `NEW`, `CONNECTING`, `LIVE`, `RESETTING`, deletion states, and reconnect counters. RDMA queue flags distinguish allocation, live connection, and transport-resource readiness. CM setup state is communicated through `cm_error` and `cm_done`.

Memory registrations and response rings are queue-lifetime state. MR pools are created per QP and destroyed with the queue. Request-specific MRs are borrowed from pools, invalidated or returned on completion, and cleared before unmapping. The async event SQE is bound to admin queue lifetime. The shared RDMA device list is reference-counted and protected by `device_list_mutex`; controller list state is protected by `nvme_rdma_ctrl_mutex`.

There is no disk persistence in this file. The durable state is remote controller/session state managed through fabrics connect/disconnect, keep-alive, authentication, and reconnection policy. Module parameter `register_always` is read-only after load and affects whether global rkey use is allowed.

## Dependencies and integration points

This transport depends on the NVMe core, NVMe fabrics helpers, blk-mq, blk-integrity, RDMA CM, IB verbs, MR pool helpers, scatterlist DMA mapping, socket address parsing, and optional authentication/TLS-related core behavior through generic controller hooks.

The main integration contracts are `nvmf_transport_ops` for user-requested fabrics controllers, `nvme_ctrl_ops` for core register and lifecycle hooks, blk-mq ops for request handling, `ib_client` for RDMA device removal, and RDMA CM private data defined by NVMe/RDMA. The file also integrates with the core queue mapping helper `nvmf_map_queues` and with authentication cleanup via `nvme_auth_stop`.

## Risks and edge cases

- RDMA connection setup is asynchronous; CM event ordering, route failures, and object teardown must not race with queue destruction.
- Request completion relies on a two-completion refcount plus optional local invalidation. Missing an end path can hang requests; double completion can corrupt blk-mq state.
- Fast registration and invalidation are security-sensitive because stale rkeys could expose host memory. The `register_always=false` global-rkey path is explicitly unsafe and should be tested only in controlled environments.
- PI/signature MR handling modifies command control bits when hardware generates or verifies PI. Incorrect signature attributes can produce silent data-integrity failures or false NVMe PI errors.
- Reconnect can return with changed queue counts; tag-set updates and queue start ranges must match available controller queues.
- Error handling must distinguish live failures, setup failures, and deletion races. Several paths intentionally tolerate state-change failures only when deletion is already in progress.
- The controller duplicate-detection tuple must match fabrics semantics; false negatives create duplicate sessions, while false positives reject valid connections.

## Test signals

Validate connect/disconnect to an NVMe/RDMA target, admin queue setup, I/O queue counts, read/write workloads, queue polling, write/read queue mapping, reconnect after target restart, RDMA device removal, timeout-induced recovery, async events, no-payload admin commands, inline write payloads, fast registration, remote invalidation, local invalidation fallback, PI read/write with guard/reference/application tag failures, and duplicate connect rejection. Fault injection around RDMA CM failures, MR pool exhaustion, DMA map failures, post-send/post-recv failures, and reconnect queue-count changes is especially valuable.
