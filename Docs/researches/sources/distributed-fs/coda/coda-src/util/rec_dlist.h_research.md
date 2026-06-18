# sources/distributed-fs/coda/coda-src/util/rec_dlist.h

## Purpose
Declares the recoverable intrusive doubly-linked list.

## Important APIs, Types, And Functions
`RCFN`, `rec_dlist`, `rec_dlist_iterator`, and `rec_dlink` mirror ordinary `dlist` types with transaction annotations and RVM allocation operators.

## Control Flow
Callers initialize a list, insert `rec_dlink`-derived objects inside transactions, remove/get entries, and iterate in either order.

## State And Persistence
List topology and counters are designed for RVM persistence. The comparison callback is process state.

## Dependencies And Integration Points
Includes `dlist.h` for shared enums and `rvmlib.h`.

## Risks
Using stack or nonrecoverable embedded links with recoverable lists can make recovery invalid. There is no locking.

## Test Signals
Compile transaction-annotated users and validate persisted head/tail/count behavior after recovery.
