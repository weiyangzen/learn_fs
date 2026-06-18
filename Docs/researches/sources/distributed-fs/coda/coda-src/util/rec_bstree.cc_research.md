# sources/distributed-fs/coda/coda-src/util/rec_bstree.cc

## Purpose
Implements the recoverable/RVM-backed analogue of `bstree`, preserving intrusive tree mutations transactionally.

## Important APIs, Types, And Functions
`rec_bstree` supports recoverable `new/delete`, `Init`, `DeInit`, `SetCmpFn`, `ClearStatistics`, `insert`, `remove`, `first`, `last`, `get`, `count`, `IsMember`, `IsOrdered`, and printing. `rec_bsnode` is the embedded recoverable node. `rec_bstree_iterator` traverses in order.

## Control Flow
The algorithm matches `bstree`: unbalanced insertion by comparator with address tie-breaks, splice-based removal, min/max get, and successor/predecessor iteration. Every persistent pointer/count/stat mutation is preceded by `RVMLIB_REC_OBJECT()` when `RvmType` requires logging.

## State And Persistence
Tree and node topology can live in RVM through `rvmlib_rec_malloc` and transaction range logging. Compare-function pointers may be nonrecoverable and can be reset outside a transaction when needed.

## Dependencies And Integration Points
Depends on `rec_bstree.h`, `rvmlib`, and ordinary `bstree` enums. Used by Coda metadata structures that need recoverable sorted indexes.

## Risks
All structural mutations require an active transaction for RAWIO/UFS RVM modes. Like the ordinary tree, it is unbalanced and iterator deletion is unsafe. Function pointers are not persistent data and must be restored after restart or reinitialization.

## Test Signals
Run insert/remove/get/order tests inside RVM transactions, simulate abort/recovery, reset comparison function after restart, verify statistics clearing persists, and compare behavior with ordinary `bstree`.
