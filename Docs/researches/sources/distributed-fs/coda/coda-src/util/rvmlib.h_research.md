# sources/distributed-fs/coda/coda-src/util/rvmlib.h

## Purpose
Declares the RVM utility abstraction used by Coda's recoverable data structures.

## Important APIs, Types, And Functions
`rvm_type_t`, `rvm_perthread_t`, global `RvmType`, transaction begin/end/abort APIs, range/byte modification, recoverable malloc/free/strdup wrappers, thread-data functions, `RVMLIB_REC_OBJECT`, `RVMLIB_MODIFY`, and transaction assertion macros define the contract.

## Control Flow
Callers initialize thread data, begin a transaction, mark ranges or use `RVMLIB_MODIFY`, allocate/free recoverable memory, and end or abort the transaction.

## State And Persistence
The header defines per-thread transaction state and integration with RVM/RDS persistent storage. In VM mode operations degrade to ordinary memory.

## Dependencies And Integration Points
Includes RVM, RDS, LWP, util, and transaction annotation headers. It is included by all recoverable container headers.

## Risks
Macros evaluate object lvalues directly and require correct transaction context. `RvmType` is a global mode switch supplied by programs, so mixed-mode misuse can be catastrophic.

## Test Signals
Compile C and C++ recoverable users, verify annotations, and run transaction lifecycle tests around each macro.
