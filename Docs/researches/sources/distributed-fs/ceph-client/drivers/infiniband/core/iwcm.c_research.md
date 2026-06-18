# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwcm.c

## Purpose
This file implements the kernel iWARP Connection Manager. It provides `iw_cm_id` creation/destruction, active connects, passive listens, accept/reject/disconnect operations, provider event handling, QP state helpers, sysctl tuning for listen backlog, and RDMA netlink registration for iWARP port mapper messages.

## Important APIs, Types, And Functions
Exported APIs include `iwcm_reject_msg()`, `iw_create_cm_id()`, `iw_cm_disconnect()`, `iw_destroy_cm_id()`, `iw_cm_listen()`, `iw_cm_reject()`, `iw_cm_accept()`, `iw_cm_connect()`, and `iw_cm_init_qp_attr()`. Internal state is `struct iwcm_id_private`, which wraps public `struct iw_cm_id` with state, flags, QP pointer, waitqueue/completion, spinlock, refcount, and preallocated work list. Core helpers include `iw_cm_map()`, `cm_event_handler()`, `cm_work_handler()`, `cm_conn_req_handler()`, `cm_conn_rep_handler()`, `cm_conn_est_handler()`, and `cm_close_handler()`.

## Control Flow
IDs start in `IDLE`. Listening preallocates backlog work items, moves to `LISTEN`, maps the local address through IWPM, and calls provider `iw_create_listen()`. Active connect preallocates four work items, sets `CONNECT_WAIT`, references the QP, moves to `CONN_SENT`, maps addresses, and calls provider `iw_connect()`. Provider upcalls run in interrupt context, grab a preallocated work item, optionally copy private data, take an ID reference, and queue ordered work. The workqueue performs state transitions for request, reply, established, disconnect, and close events. Destroy sets `DROP_EVENTS`, waits for connect/accept downcalls, tears down listens or live connections, rejects pending passive requests, drops QP references, and removes IWPM mappings.

## State And Persistence
Connection state is runtime-only in `iwcm_id_private::state`: `IDLE`, `LISTEN`, `CONN_RECV`, `CONN_SENT`, `ESTABLISHED`, `CLOSING`, and `DESTROYING`. Flags `IWCM_F_DROP_EVENTS` and `IWCM_F_CONNECT_WAIT` coordinate teardown and downcall waiting. Work items are preallocated to avoid interrupt-context allocation. Mapped addresses persist in the public ID until destroy removes mapinfo.

## Dependencies And Integration Points
The file depends on provider iWARP ops, RDMA QP modify, IWPM port mapping, RDMA netlink, sysctl, ordered workqueues, wait queues, and public `<rdma/iw_cm.h>`. Upper layers receive callbacks through `iw_cm_id::cm_handler`.

## Risks And Test Signals
Risks are state-machine races among provider upcalls, application accept/reject/disconnect/destroy, and queued work. The design relies on fixed preallocated work counts, and invalid provider event ordering can hit `BUG()`. Tests should cover active connect success/reject/reset/timeout, passive accept/reject, destroy during pending connect or accept, disconnect before accept, simultaneous disconnect, provider close after destroy, backlog exhaustion, private-data lifetime, QP reference balancing, wildcard mapping, IWPM unavailable/downlevel behavior, sysctl changes, and lockdep/KCSAN stress.
