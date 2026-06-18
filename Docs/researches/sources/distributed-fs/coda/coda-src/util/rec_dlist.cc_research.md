# sources/distributed-fs/coda/coda-src/util/rec_dlist.cc

## Purpose
Implements a recoverable circular doubly-linked intrusive list.

## Important APIs, Types, And Functions
`rec_dlist` supports recoverable allocation, `Init`, `DeInit`, `SetCmpFn`, `insert`, `prepend`, `append`, `remove`, `first`, `last`, `get`, `count`, `IsMember`, and printing. `rec_dlink` has `Init()` and print helpers. `rec_dlist_iterator` scans ascending/descending.

## Control Flow
List algorithms match `dlist`, but every changed list/link object is logged with `RVMLIB_REC_OBJECT()`. `SetCmpFn()` conditionally logs when a transaction exists because callback pointers may be volatile process state.

## State And Persistence
The list head/count and link next/prev pointers are recoverable state. Derived objects embedding `rec_dlink` are expected to live in recoverable storage when persistence is desired.

## Dependencies And Integration Points
Depends on `rec_dlist.h` and `rvmlib`. Used by recoverable hash tables and Coda RVM metadata lists.

## Risks
`DeInit()` aborts when entries remain. Mutations require transactions. Iteration is not safe for deleting the current node. Comparator pointer persistence must be managed by callers.

## Test Signals
Run all ordinary `dlist` operations inside transactions, verify RVM abort rolls back topology, call `DeInit()` on empty/nonempty lists, and test comparator reset after restart.
