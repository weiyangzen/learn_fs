# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwcm.h

## Purpose
This private header defines the iWARP CM internal state machine and private wrapper around the public `iw_cm_id`. It is consumed by `iwcm.c` to track connection lifecycle, queued work capacity, QP association, and destruction/connect synchronization.

## Important APIs, Types, And Functions
`enum iw_cm_state` defines `IW_CM_STATE_IDLE`, `LISTEN`, `CONN_RECV`, `CONN_SENT`, `ESTABLISHED`, `CLOSING`, and `DESTROYING`. `struct iwcm_id_private` embeds `struct iw_cm_id`, state, flags, associated QP pointer, destroy completion, connect waitqueue, spinlock, refcount, and a free list of preallocated work items. Flags are `IWCM_F_DROP_EVENTS` and `IWCM_F_CONNECT_WAIT`.

## Control Flow
The header itself has no runtime flow, but its state names document transitions implemented in `iwcm.c`: IDLE to LISTEN or CONN_SENT, LISTEN to child CONN_RECV, CONN_RECV/CONN_SENT to ESTABLISHED, ESTABLISHED to CLOSING, and terminal cleanup through DESTROYING.

## State And Persistence
All fields are runtime-only per iWARP connection ID. The spinlock protects state/QP transitions, the waitqueue coordinates connect/accept downcalls with disconnect/destroy, the refcount keeps queued events alive, and the work free list guarantees provider upcalls can enqueue work without allocating.

## Dependencies And Integration Points
The header depends on public RDMA CM/QP types and kernel completion, waitqueue, spinlock, refcount, and list primitives. External code should use the public `iw_cm_id` API rather than these internals.

## Risks And Test Signals
State or flag changes require updates to every switch in `iwcm.c`, including `BUG()` paths. Tests are indirect through iWARP CM active/passive connect, reject, disconnect, destroy, event dropping, and queued-work reference handling.
