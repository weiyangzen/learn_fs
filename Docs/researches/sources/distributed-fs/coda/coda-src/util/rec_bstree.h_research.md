# sources/distributed-fs/coda/coda-src/util/rec_bstree.h

## Purpose
Declares the recoverable intrusive binary search tree.

## Important APIs, Types, And Functions
`RBSTCFN`, `rec_bstree`, `rec_bsnode`, and `rec_bstree_iterator` mirror the ordinary tree with transaction annotations and recoverable allocation operators.

## Control Flow
Callers allocate/initialize a recoverable tree, derive objects from `rec_bsnode`, mutate inside transactions, and restore nonpersistent comparator functions when needed.

## State And Persistence
Tree topology and counters are intended for RVM persistence. Comparator pointers are explicitly treated as potentially nonrecoverable.

## Dependencies And Integration Points
Includes `bstree.h` for shared enums and `rvmlib.h` for RVM APIs.

## Risks
Using the API outside transactions in persistent modes can fail assertions. Node lifetime and one-tree membership are caller responsibilities.

## Test Signals
Compile with transaction annotations, allocate from RVM, and validate recovery of topology after committed transactions.
