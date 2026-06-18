# sources/distributed-fs/coda/coda-src/util/olist.cc

## Purpose
Implements an intrusive circular singly-linked list with tail pointer, head insertion, tail append, removal, tag search, and iteration.

## Important APIs, Types, And Functions
`olist` provides `insert`, `append`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, `FindObject`, and print methods. `olist_iterator` scans the circular list. `olink` is the embedded link base and supports `otagmatch()`.

## Control Flow
Insertion and append reject already-linked objects, initialize singleton lists by pointing a node to itself, or splice after tail. Removal walks from tail to find the predecessor, rewires links, resets `p->next`, and updates tail. Iteration begins at `tail->next` and stops after returning tail.

## State And Persistence
State is `tail`, `cnt`, and each node's `next` pointer. The list does not own derived objects and has no persistence.

## Dependencies And Integration Points
Depends on `olist.h`, `coda_assert`, and POSIX writes for diagnostics. `ohash` and other utilities use it as an intrusive bucket/list primitive.

## Risks
Current-entry deletion is explicitly unsafe for the iterator. `FindObject()` relies on caller-provided compare functions and `olink::otagmatch()` passes `(this, tag)` despite comments implying tag/object order. Copy constructor and assignment abort at runtime.

## Test Signals
Insert/append/remove singleton, head, tail, and middle nodes; search by tag; iterate to exactly tail; clear lists; and verify double insertion aborts.
