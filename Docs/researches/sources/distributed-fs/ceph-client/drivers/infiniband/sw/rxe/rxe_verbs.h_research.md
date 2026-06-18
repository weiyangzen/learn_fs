# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_verbs.h

## Purpose

`rxe_verbs.h` defines RXE's core RDMA object structures, QP protocol state, responder states, memory object state, access masks, device/port state, and conversion helpers.

## Important APIs, Types, and Functions

It defines `rxe_ucontext`, `rxe_pd`, `rxe_ah`, `rxe_cq`, `rxe_srq`, `rxe_qp`, `rxe_mr`, `rxe_mw`, multicast records, `rxe_port`, `rxe_dev`, `rxe_req_info`, `rxe_comp_info`, `rxe_resp_info`, `resp_res`, `enum resp_states`, and `to_r*()` helpers.

## Control Flow

The header has no standalone execution. Its structs and enums are manipulated by verbs, QP, requester, responder, completer, memory, multicast, and network modules.

## State and Persistence Behavior

Most persistent RXE runtime state is defined here: pools, counters, port attributes, QP queues/timers/tasks/protocol fields, CQ queues/notify flags, SRQ queues/limits, MR/MW access state, and multicast membership.

## Dependencies and Integration Points

It integrates RDMA core object types with RXE pools, tasks, counters, skbs/timers/workqueues, and memory registration state.

## Risks and Edge Cases

Embedded object layouts power `container_of()` conversions and pool macros. PSN comparison relies on 24-bit wrap semantics. Responder replay state and access masks must stay aligned with requester/responder behavior.

## Test Signals

Compile all RXE modules, test QP/MR/MW/SRQ/CQ lifecycles, PSN wraparound, responder replay, access enforcement, multicast attach/detach, and refcount leak detection.
