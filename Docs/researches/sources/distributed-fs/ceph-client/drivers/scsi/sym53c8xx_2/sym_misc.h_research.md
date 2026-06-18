# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_misc.h

## Purpose

`sym_misc.h` provides small infrastructure helpers for the `sym53c8xx_2` driver: an intrusive doubly linked queue abstraction, bitmap macros, and a compile-time log2-round-up expression used by CCB hash calculations.

## Important APIs, Types, And Functions

`SYM_QUEHEAD` is the queue node/header type. Core helpers are `sym_que_init()`, `sym_que_first()`, `sym_que_last()`, `sym_que_empty()`, `sym_que_splice()`, `sym_que_move()`, `sym_remque_head()`, and `sym_remque_tail()`. Low-level insertion/removal is performed by `__sym_que_add()` and `__sym_que_del()`, with macro aliases `sym_insque()`, `sym_remque()`, `sym_insque_head()`, and `sym_insque_tail()`. `sym_que_entry()` wraps `container_of()`.

Bitmap macros `sym_set_bit()`, `sym_clr_bit()`, and `sym_is_bit()` operate on `u32` arrays. `_LGRU16_()` computes a rounded-up base-2 logarithm for 16-bit constants using chained ternary fragments.

## Control Flow And State

The queue implementation uses a circular sentinel model. Empty queues point `flink` and `blink` back to the head. Insertions splice a new node between a previous and next node; removals reconnect neighbors without reinitializing the removed node. `sym_que_splice()` prepends a whole non-empty list into another head, while `sym_que_move()` transfers all elements and reinitializes the origin.

There is no locking in this header. Queue safety depends entirely on callers holding the correct host lock or being in serialized initialization/teardown code.

## Dependencies And Integration Points

The queue type is embedded in `struct sym_ccb`, `struct sym_hcb`, and optional LUN queueing structures defined in `sym_hipd.h`. It supports free, busy, completion, waiting, and started CCB lists. `_LGRU16_()` is used in the DSA-to-CCB hash macro to keep hash calculation matched to the `struct sym_ccb` size.

## Risks And Test Signals

Because `sym_remque()` does not poison or reinitialize nodes, double removal or reusing a node in two queues can corrupt the list silently. `sym_que_splice()` leaves the donor list linked into the destination rather than resetting it, while `sym_que_move()` does reset the origin; callers must choose the correct semantic. Bitmap macros assume valid indexes and a `u32 *` backing store.

Test signals are queue integrity under command allocation/completion stress, abort paths that move busy CCBs to completion queues, and debug queue tracing with `DEBUG_QUEUE`.
