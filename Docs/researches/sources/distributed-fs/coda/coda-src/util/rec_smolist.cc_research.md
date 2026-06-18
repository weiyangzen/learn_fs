# sources/distributed-fs/coda/coda-src/util/rec_smolist.cc

## Purpose
Implements `rec_smolist`, a minimal recoverable circular singly-linked list designed to occupy only one pointer in persistent structures.

## Important APIs, Types, And Functions
`rec_smolist` implements `insert`, `append`, `remove`, `get`, `IsEmpty`, and print methods. `rec_smolist_iterator` precomputes the next link so current-entry removal during iteration is supported. `rec_smolink_print()` prints raw link state.

## Control Flow
Insert/append assert the link is not already in a list, then use `RVMLIB_MODIFY` to update the new link and list `last`. Removal finds the predecessor, updates predecessor and removed link, and fixes `last`. `get()` removes the head directly. The iterator starts at `last->next`, stores `nlink`, and stops after the last entry.

## State And Persistence
Only `last` in the list and `next` in each link are persistent topology. There is no count, constructor initialization, or object ownership. The header notes users must perform their own initialization.

## Dependencies And Integration Points
Depends on `rvmlib`, `util.h`, and transaction macros. It was designed for volume vnode arrays where compact recoverable list heads mattered.

## Risks
The constructor intentionally does not initialize `last`; callers must zero persistent storage before first use. No count makes corruption harder to detect. The list is single-membership by convention via `p->next == 0`.

## Test Signals
Initialize zeroed persistent list heads, insert/append/remove/get under transactions, remove current entries during iteration, recover after commit/abort, and verify uninitialized heads fail visibly in tests.
