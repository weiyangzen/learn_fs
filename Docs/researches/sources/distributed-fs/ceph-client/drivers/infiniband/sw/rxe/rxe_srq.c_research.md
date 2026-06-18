# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_srq.c

## Purpose

`rxe_srq.c` implements shared receive queue validation, creation, resize/limit modification, and cleanup.

## Important APIs, Types, and Functions

The file exports `rxe_srq_chk_init()`, `rxe_srq_from_init()`, `rxe_srq_chk_attr()`, `rxe_srq_from_attr()`, and `rxe_srq_cleanup()`.

## Control Flow

Create validates max WR/SGE, normalizes minimums, initializes event context and limits, allocates a receive queue, exposes mmap info to userspace, and returns the SRQ number/capacity. Modify can resize the queue under producer/consumer locks and update the SRQ limit used for limit-reached events.

## State and Persistence Behavior

An SRQ persists its PD reference, receive queue, max WR/SGE, SRQ number, event handler/context, limit, and error flag. Posted WQEs persist in the queue until responders consume them.

## Dependencies and Integration Points

It depends on RXE queue allocation/resizing, mmap info, SRQ UAPI commands, device limits, pool cleanup, verbs SRQ methods, and responder SRQ consumption.

## Risks and Edge Cases

Resize ABI handling uses an mmap-info address from command input. Limit validation must not exceed current capacity. Error state blocks operations. Active resize requires both queue locks.

## Test Signals

Test create/query/destroy, post_srq_recv, multi-QP consumption, limit events, resize grow/shrink with queued WQEs, invalid attributes, and cleanup with QP references.
