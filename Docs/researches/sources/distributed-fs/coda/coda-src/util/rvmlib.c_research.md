# sources/distributed-fs/coda/coda-src/util/rvmlib.c

## Purpose
Provides Coda's wrapper layer around RVM/RDS transactions, per-LWP transaction state, recoverable allocation/free, and range logging.

## Important APIs, Types, And Functions
Global `RvmType` selects `UNSET`, `RAWIO`, `UFS`, or `VM`. APIs include `rvmlib_init_threaddata`, `rvmlib_thread_data`, `rvmlib_set_thread_data`, `_rvmlib_begin_transaction`, `rvmlib_end_transaction`, `rvmlib_abort`, `rvmlib_set_range`, `rvmlib_modify_bytes`, `rvmlib_strdup`, `rvmlib_malloc`, `rvmlib_free`, `rvmlib_check_trans`, and `rvmlib_in_transaction`.

## Control Flow
For RAWIO/UFS, thread data is stored in an LWP rock. Beginning a transaction initializes a tid, remembers file/line, and calls `rvm_begin_transaction()`. Ending commits with or without flush and coordinates delayed RDS frees. Aborting calls `rvm_abort_transaction()` and clears pending frees. Set-range and modify functions log bytes before mutation. Allocation dispatches to `malloc` in VM mode or `rds_malloc` in persistent modes; free uses `free` or queues an RDS fake free.

## State And Persistence
Per-thread state includes active tid, RDS intention list, and transaction start location. Persistent state is managed by RVM/RDS when `RvmType` is RAWIO/UFS. VM mode treats recoverable operations as ordinary heap operations and does not start real transactions.

## Dependencies And Integration Points
Depends on RVM, RDS, LWP rocks, `util.h`, and `coda_assert`. Every `rec_*` data structure and RVM-backed bitmap/varl object integrates through this layer.

## Risks
Many functions assert or abort on misuse rather than returning errors. `rvmlib_in_transaction()` returns false in VM mode, which can surprise generic checks. Transaction nesting is rejected. `rvmlib_free` is declared inline in a C file, which can be toolchain-sensitive. Function assumes per-LWP rock setup before persistent operations.

## Test Signals
Run begin/end/abort in VM, RAWIO, and UFS modes; nested begin failure; set-range without transaction; allocation/free with flush and no_flush; RDS delayed free paths; per-thread isolation; and recovery after committed and aborted mutations.
