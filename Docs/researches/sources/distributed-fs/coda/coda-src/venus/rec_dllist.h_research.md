# sources/distributed-fs/coda/coda-src/venus/rec_dllist.h

## Purpose
This header provides small wrappers around intrusive doubly-linked list operations so list mutations are logged in RVM before they change recoverable memory.

## Important APIs, Types, and Functions
`rec_list_head_init()` records the list head and initializes it. `rec_list_add()` records the new node, the old first node, and the back-link before calling `list_add()`. `rec_list_del()` records the node and, when linked, the adjacent list links before calling `list_del()`.

## Control Flow
Each helper must be called inside a transaction. The control flow is deliberately one-level: mark affected recoverable ranges, then delegate to normal dllist primitives.

## State and Persistence Behavior
These functions directly protect persistent list consistency. Missing any adjacent pointer in the recorded range could corrupt recoverable lists across a crash.

## Dependencies and Integration Points
It depends on `dllist.h` and `rvmlib.h`. It is used by persistent structures such as `Realm`/`RealmDB` to maintain RVM-backed intrusive lists.

## Risks and Test Signals
Risks are incomplete logging of pointer fields and using non-recoverable list helpers on persistent lists. Crash-recovery tests should add/delete nodes inside transactions and verify list integrity after restart.
