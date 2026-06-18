# sources/distributed-fs/ceph-client/drivers/scsi/arm/msgqueue.h

## Purpose

`msgqueue.h` declares the fixed-size message queue used by ARM SCSI protocol engines for outgoing SCSI message phases. It provides the shared data structures and function prototypes implemented in `msgqueue.c`.

## Important APIs, Types, and Functions

`struct message` stores up to eight message bytes, length, and a FIFO position marker. `struct msgqueue_entry` links a message into either the active or free list. `MsgQueue_t` contains active and free heads plus `NR_MESSAGES` embedded entries. Public functions are `msgqueue_initialise`, `msgqueue_free`, `msgqueue_msglength`, `msgqueue_getmsg`, `msgqueue_addmsg`, and `msgqueue_flush`.

## Control Flow

Callers initialize a queue per host, add one or more messages before message-out phases, ask for total message length and indexed entries while programming the chip FIFO, and flush the queue when the message sequence is no longer needed or when reset/error handling starts.

## State and Persistence Behavior

The queue is fixed, in-memory, and host-owned. It does not allocate memory dynamically and has no persistence. The `fifo` field is written by protocol engines to remember where a message landed in a chip FIFO for later MESSAGE REJECT attribution.

## Dependencies and Integration Points

The header is consumed by `msgqueue.c`, `acornscsi.h`, and `fas216.h`. It has no kernel includes of its own and relies on including translation units to provide needed base types.

## Risks and Edge Cases

The fixed four-entry, eight-byte-message design is small but brittle. Callers must handle `msgqueue_addmsg()` failure and must not enqueue longer messages. Because there is no locking, misuse from concurrent interrupt and queue contexts could corrupt the linked lists.

## Test Signals

Validation should check ABI expectations for `NR_MESSAGES`, message byte capacity, FIFO marker behavior under MESSAGE REJECT, and all current call sites' message lengths and failure handling.
