# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitVec.h

## Purpose
Declares the page-vector communication state and entry points for BeeGFS storage read/write operations that work on `FhgfsChunkPageVec`.

## Important APIs and Types
`FhgfsCommKitVec` stores read/write union state, header length, successful page count, page vector, initial offset, target ID, message buffer, mirror/session flags, node/socket refs, result, and loop control. `CommKitVecHelper` carries shared app/logger/io info. Public helpers assign initial state, set first-write-done, compute remaining data size, compute current offset, and run read/write communication.

## Control Flow
Callers build a `FhgfsCommKitVec` with `FhgfsOpsCommKitVec_assignRWfileState()`, optionally set first-write-done/mirror flags, and pass it to `FhgfsOpsCommKitVec_rwFileCommunicate()`. Inline offset calculation derives current offset from page vector total minus remaining size.

## State and Persistence
The state is per page-vector I/O request. It references caller-owned page vector and message buffer. Result state uses BeeGFS negative error codes or positive byte counts.

## Dependencies and Integration Points
Includes remoting, page wrappers, chunk page vectors, Linux fs, common comm-kit types, and `RemotingIOInfo`. Used by page cache I/O paths.

## Risks
Caller must supply a valid 4 KiB-capable message buffer and live page vector. The inline constructor ignores `pageIdx` and `numPages` arguments, which may indicate legacy API drift. Mirror flags must be initialized or explicitly changed before communication.

## Test Signals
Compile users, validate offset/remaining calculations as page vectors advance, check constructor defaults, and run read/write page-vector communication tests for mirror and session-check combinations.
