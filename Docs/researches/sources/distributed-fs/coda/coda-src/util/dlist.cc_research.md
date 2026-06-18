# sources/distributed-fs/coda/coda-src/util/dlist.cc

## Purpose
Implements an intrusive circular doubly-linked list with optional sorted insertion.

## Important APIs, Types, And Functions
`dlist` provides `insert`, `prepend`, `append`, `remove`, `first`, `last`, `get`, `clear`, `count`, `IsMember`, and print methods. `dlist_iterator` traverses ascending or descending. `dlink` is the embedded base object.

## Control Flow
Insertion rejects already-linked nodes, then either initializes a singleton circular list or splices around `head`/tail. Sorted insertion walks with `CmpFn` until the new node should precede the current node. Removal rewires predecessor/successor links and resets the removed node. Iteration starts at head or tail and stops after wrapping.

## State And Persistence
The list stores `head`, `cnt`, and comparator. Each node stores `next`/`prev`. It does not own or delete derived objects and has no persistence.

## Dependencies And Integration Points
Depends on `dlist.h`, `coda_assert`, and POSIX `write()` for diagnostics. Hash tables reuse `dlist` buckets and friend access to set `CmpFn`.

## Risks
The iterator is unsafe for deletion of the current entry. `remove()` assumes a non-empty list and a linked node; removing a node not on this list can corrupt memory. Destruction clears membership but does not free containing objects.

## Test Signals
Append/prepend/insert sorted objects, remove head/tail/middle/singleton, detect double insertion aborts, iterate both directions, clear lists, and validate behavior with null comparator.
