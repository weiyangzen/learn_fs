# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_qp.c

## Purpose

`rxe_qp.c` implements RXE queue pair validation, creation, modification, reset/error transitions, send/receive queue setup, per-QP socket/timer/task initialization, responder resource allocation, and cleanup.

## Important APIs, Types, and Functions

Important entry points are `rxe_qp_chk_init()`, `rxe_qp_from_init()`, `rxe_qp_chk_attr()`, `rxe_qp_from_attr()`, `rxe_qp_to_init()`, `rxe_qp_to_attr()`, `rxe_qp_error()`, `rxe_qp_chk_destroy()`, and `rxe_qp_cleanup()`.

## Control Flow

Create validates type/capabilities, takes PD/CQ/SRQ references, initializes common fields, creates a kernel UDP send socket, allocates SQ and optional RQ queues, initializes send/receive tasks, sets RC timers, and marks the QP valid in RESET. Modify validates legal transitions, handles RESET/SQD/ERR side effects, and updates attributes such as PSNs, AVs, MTU, access flags, retries, and atomic depths. Cleanup invalidates, drains, deletes timers, destroys tasks/queues, and releases references/resources.

## State and Persistence Behavior

QP state includes PD/CQ/SRQ references, SQ/RQ queues, requester/completer/responder protocol state, socket, source port, AVs, timers, skb counters, task state, and responder resources for RDMA read/atomic/flush replay.

## Dependencies and Integration Points

The file depends on queues, tasks, requester/responder/completer callbacks, RDMA QP state validation, socket APIs, timers, AV helpers, pool cleanup, and verbs create/modify/query/destroy paths.

## Risks and Edge Cases

State transitions are concurrency-sensitive under `state_lock`. Reset must stop tasks, drain protocol engines, clear queues, and reenable tasks safely. RC timers only exist for RC QPs. SRQ-backed QPs skip per-QP RQ allocation. Atomic resource sizing must match protocol semantics.

## Test Signals

Test create/modify/query/destroy across RC/UC/UD/GSI, invalid transitions, reset/error under traffic, SQD drain events, RC retry/RNR timers, SRQ-backed QPs, max atomic depth changes, MTU/path changes, and destroy while attached to multicast.
