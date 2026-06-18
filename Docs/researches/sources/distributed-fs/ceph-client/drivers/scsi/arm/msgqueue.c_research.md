# sources/distributed-fs/ceph-client/drivers/scsi/arm/msgqueue.c

## Purpose

`msgqueue.c` implements a tiny fixed-capacity SCSI message queue used by the Acorn and FAS216 drivers to build outgoing message sequences such as IDENTIFY, SIMPLE QUEUE TAG, SDTR, MESSAGE REJECT, INITIATOR ERROR, and ABORT.

## Important APIs, Types, and Functions

Internal helpers are `mqe_alloc()` and `mqe_free()`, which manage the queue's fixed free list. Exported APIs are `msgqueue_initialise()`, `msgqueue_free()`, `msgqueue_msglength()`, `msgqueue_getmsg()`, `msgqueue_addmsg()`, and `msgqueue_flush()`.

## Control Flow

Initialization links the embedded `entries[NR_MESSAGES]` array into a free list and clears the active queue. `msgqueue_addmsg()` pops a free entry, copies variadic message bytes into the fixed 8-byte message buffer, sets length and FIFO marker, and appends to the active list. Consumers call `msgqueue_msglength()` to program transfer counts and `msgqueue_getmsg()` by index to emit messages. Flush returns all active entries to the free list.

## State and Persistence Behavior

State is entirely embedded in `MsgQueue_t`: active list head, free-list head, and four preallocated entries. There is no dynamic allocation and no durable persistence. `msgqueue_free()` is intentionally empty because no external resources are owned.

## Dependencies and Integration Points

The module depends on standard kernel module headers and `msgqueue.h`. It exports its functions for use by `acornscsi.c` and `fas216.c`.

## Risks and Edge Cases

`msgqueue_addmsg()` does not validate `length <= sizeof(msg.msg)`, so callers must never enqueue messages longer than eight bytes. The queue capacity is four messages; overflow returns false and callers often do not check. There is no internal locking, so callers must serialize access through their host locks or interrupt exclusion. Variadic arguments are read as `unsigned int`, matching integer promotion for byte constants.

## Test Signals

Tests should cover initialization, four-message capacity, overflow return, flush reuse, indexed retrieval, total length calculation, zero-length messages if callers ever use them, and an audit that all current message lengths are at most eight bytes.
