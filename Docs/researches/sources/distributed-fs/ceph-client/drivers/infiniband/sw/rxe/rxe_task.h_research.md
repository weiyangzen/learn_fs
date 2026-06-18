# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_task.h

## Purpose

`rxe_task.h` defines RXE task states, task structure, and scheduler APIs used by QP send/receive processing.

## Important APIs, Types, and Functions

It defines task states `IDLE`, `BUSY`, `ARMED`, `DRAINING`, `DRAINED`, and `INVALID`; `struct rxe_task`; and declarations for workqueue allocation/destruction, task init, scheduling, cleanup, disable, and enable.

## Control Flow

QP setup initializes tasks with requester/responder callbacks. Runtime code schedules tasks when work arrives. QP reset and cleanup disable, drain, reenable, or invalidate them.

## State and Persistence Behavior

State is per task and persists with the QP. The callback convention is that zero means continue and nonzero means idle/stop.

## Dependencies and Integration Points

The header depends on workqueue and spinlock types and is included by `rxe_verbs.h` and QP implementation files.

## Risks and Edge Cases

Callbacks that violate the return convention can spin or stop early. Direct state mutation outside `rxe_task.c` can lose work or run after cleanup.

## Test Signals

Compile all users and test schedule while busy, reset disable/enable, cleanup under queued work, and task callback return behavior.
