# sources/distributed-fs/ceph-client/drivers/infiniband/core/cm.c

## Purpose

`cm.c` implements the InfiniBand Connection Manager. It creates/listens/destroys CM IDs, sends and receives CM MADs, drives the connection state machine for REQ/REP/RTU/DREQ/DREP/REJ/MRA/LAP/APR/SIDR messages, assists QP state transitions, tracks duplicate/stale connections through timewait tables, registers MAD agents per CM-capable port, and exposes per-port CM counters in sysfs.

## Important APIs, Types, And Functions

- Public lifecycle and connection APIs: `ib_create_cm_id()`, `ib_destroy_cm_id()`, `ib_cm_listen()`, `ib_cm_insert_listen()`, `ib_send_cm_req()`, `ib_send_cm_rep()`, `ib_send_cm_rtu()`, `ib_send_cm_dreq()`, `ib_send_cm_drep()`, `ib_send_cm_rej()`, `ib_prepare_cm_mra()`, `ib_send_cm_sidr_req()`, `ib_send_cm_sidr_rep()`, `ib_cm_notify()`, `ib_cm_init_qp_attr()`, and `ibcm_reject_msg()`.
- Global `struct ib_cm cm` owns locks, device list, listener tree, remote ID/QP/SIDR trees, local ID xarray, random ID operand, timewait list, and CM workqueue.
- `struct cm_id_private` extends `struct ib_cm_id` with locks, refcount/completion, message pointer, AVs, private data, QP parameters, timeout/retry fields, queued work, timewait state, and ECE data.
- `struct cm_device` and `struct cm_port` represent a registered IB device and per-port MAD agents/counters.
- `struct cm_work` carries received MAD work, local/remote IDs, event payload, and optional path records.
- `struct cm_timewait_info` indexes remote IDs/QPNs and later becomes a delayed work item for timewait exit.

## Control Flow

Module init initializes global locks/trees/xarray, randomizes the local ID operand, creates `cm.wq`, and registers `cm_client`. `cm_add_one()` attaches to each CM-capable port, registers sysfs counter groups, creates a receive-capable GSI MAD agent and a send-only reply agent, sets the port CM capability bit, and links the `cm_device` into the global device list. Remove marks the device `going_down`, flushes queued work, nulls MAD agents under `mad_agent_lock`, unregisters agents/counters, and drops the device reference.

ID creation allocates `cm_id_private`, initializes state as `IB_CM_IDLE`, allocates a cyclic 32-bit local ID from the xarray, XORs it with `cm.random_id_operand`, and finalizes it into `cm.local_id_table` unless it is a shared listener created by `ib_cm_insert_listen()`. ID destruction is state-aware: listeners are removed from the listener tree, pending sends are cancelled, active connections may send REJ or DREQ, established IDs enter timewait when appropriate, SIDR requests may be rejected, queued work is drained, AVs/private data are destroyed, and final free uses RCU after the refcount completion.

Outbound active connection flow starts in `ib_send_cm_req()`: validate request parameters, create timewait info, build primary and optional alternate AVs from SA path records, fill local state and timeouts, allocate a tracked MAD send buffer, format a REQ, post it, and move to `IB_CM_REQ_SENT`. REP receipt validates state, inserts remote ID and remote QPN into duplicate/stale detection tables, fills remote QP and responder parameters, cancels the REQ send, moves to `IB_CM_REP_RCVD`, and queues a callback. `ib_send_cm_rtu()` then sends RTU and moves to `IB_CM_ESTABLISHED`.

Passive connection flow starts in `cm_req_handler()`: allocate a new CM ID for the incoming REQ, initialize response AV from the receive WC/GRH, create timewait info, set `IB_CM_REQ_RCVD`, use remote ID/QPN trees to reject duplicates/stale connections, find a matching listener, parse primary/alternate paths, rebuild AVs by path, finalize the new ID into the xarray, and deliver `IB_CM_REQ_RECEIVED` to the listener's handler. `ib_send_cm_rep()` replies and moves to `IB_CM_REP_SENT`; incoming RTU moves to `IB_CM_ESTABLISHED`.

Disconnect flow uses `ib_send_cm_dreq()` to send tracked DREQ from established state and move to `IB_CM_DREQ_SENT`; incoming DREQ cancels applicable outstanding messages, moves to `IB_CM_DREQ_RCVD`, and queues a callback. `ib_send_cm_drep()` enters timewait and sends DREP. Incoming DREP for a DREQ moves to timewait and cancels the outstanding send. Duplicate DREQs may elicit direct DREP responses.

MRA/REJ flow adjusts timeouts or terminates state. `ib_prepare_cm_mra()` moves pending received REQ/REP/LAP work into MRA-sent states. `cm_mra_handler()` extends tracked MAD timeouts and queues MRA events. `cm_send_rej_locked()` resets to idle or enters timewait depending on state; `cm_rej_handler()` mirrors that for received rejects and delivers an event.

SIDR flow uses `ib_send_cm_sidr_req()` for service ID resolution without normal connection timewait/xarray receive state. Incoming SIDR requests create a temporary CM ID indexed by remote request ID and SLID to suppress duplicates, find a listener, call its handler directly, and expect `ib_send_cm_sidr_rep()` to send the response and erase the SIDR tree entry. SIDR replies cancel the tracked request and deliver an event.

LAP/APR alternate path flow is unsupported on RoCE. Incoming LAP parses alternate path information, updates AV state, and queues a LAP event if the connection is established and LAP state allows it. APR replies reset LAP state to idle and cancel outstanding LAP sends.

MAD receive flow maps CM MAD attribute IDs to `ib_cm_event_type`, allocates `cm_work` with enough path records, increments receive counters, and queues the work unless the device is going down. Send completions update transmit/retry counters and call `cm_process_send_error()` for tracked sends. User callbacks are serialized per CM ID by `work_count` and `work_list` in `cm_queue_work_unlock()`/`cm_process_work()`.

`ib_cm_init_qp_attr()` synthesizes QP attributes for INIT/RTR/RTS from CM state: P_Key index, port, access flags, AH/path MTU/destination QPN/PSN, responder/initiator depths, retry/RNR settings, timeout, and alternate path migration fields.

## State And Persistence

All state is in memory. The global CM state uses `cm.lock` for listener and remote/timewait structures, `cm.device_lock` for the device list, `cm.local_id_table` for local ID lookup under RCU, and `cm.wq` for serialized asynchronous handling. Each CM ID has its own spinlock and refcount; tracked send MADs hold an extra CM ID reference until completion or cancellation. Timewait state persists only until the delayed work fires or the device/ID is destroyed.

Private data is copied for RTU/DREP or reused for duplicate replies. AVs hold references to `cm_device` through their `cm_port`; `cm_destroy_av()` releases those references. Sysfs counters are atomic per port and grouped as transmitted messages, transmit retries, received messages, and received duplicates.

## Dependencies And Integration Points

`cm.c` depends on the RDMA MAD layer, AH/path record helpers, GID/P_Key cache APIs from `cache.c`, CM message field accessors from `cm_msgs.h` and IBTA field definitions, tracepoints from `cm_trace.h`, RDMA device client registration, sysfs port attribute groups, workqueues, xarray, rbtree, RCU, and low-level port modification. It is consumed by upper-layer RDMA protocols that use `struct ib_cm_id` callbacks and QP initialization helpers.

## Risks

- The state machine is broad and lock-sensitive. Regressions can cause invalid transitions, duplicate callbacks, missed cancellations, or leaked references.
- Listener sharing only works for matching handlers with no context; misuse returns existing IDs or errors in subtle ways.
- Remote duplicate/stale detection depends on correct insertion/removal of remote ID and remote QPN timewait nodes.
- Destroy paths can send protocol messages and wait for references; incorrect timeout or refcount handling can lead to hangs, warnings, or use-after-free.
- Direct retry response messages use special context and are freed differently from tracked private messages.
- Device removal races are mitigated by `going_down`, workqueue flushes, and `mad_agent_lock`; any new queueing path must honor those gates.
- Path handling includes IB, RoCE, OPA extended LIDs, permissive LIDs, SGID attributes, and alternate paths. Small field conversion mistakes can break interoperability.
- QP attribute helpers expose live AH objects by value; callers must use them only in states accepted by CM and avoid assuming alternate path support on RoCE.

## Test Signals

High-value signals include full active/passive RC connection handshakes, rejection paths for invalid service IDs/GIDs/alternate paths, duplicate REQ/REP/DREQ/MRA behavior, stale connection timewait behavior, SIDR request/reply success and duplicate suppression, LAP/APR behavior on IB and rejection on RoCE, send-completion error events for REQ/REP/DREQ/SIDR, CM sysfs counter increments, QP INIT/RTR/RTS attribute generation, listener sharing semantics, and device removal while work and MAD sends are outstanding. Tracepoints in `cm_trace.h` provide detailed observability for these cases.
