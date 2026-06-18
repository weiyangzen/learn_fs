# sources/distributed-fs/openafs/src/volser/voltrans_inline.h

## Purpose

`voltrans_inline.h` provides small inline helpers for updating the debug/tracking fields of a `struct volser_trans`. The fields record the most recent Rx call and procedure name for transaction status reporting and for aborting calls when a transaction is deleted.

## Important APIs

`TSetRxCall_r` updates `lastProcName` and `rxCallPtr` while the caller already holds the transaction object lock. `TClearRxCall_r` clears `rxCallPtr` under the same precondition. `TSetRxCall` and `TClearRxCall` are locking wrappers around those raw variants. Procedure names are copied with `strlcpy` into the fixed `lastProcName` buffer.

## Control Flow Role

RPC implementations call these helpers before and after long-running or externally visible work. `VolMonitor` reports the stored fields, and `DeleteTrans` can signal the tracked call with `RX_CALL_DEAD`.

## State and Persistence Behavior

The helpers modify only in-memory fields in `struct volser_trans`. Indirectly, accurate `rxCallPtr` state affects whether transaction deletion can abort a live Rx call, and accurate `lastProcName` improves diagnosis of stuck or long-running operations.

## Dependencies and Integration Points

This header includes `volser.h` for `struct volser_trans` and lock macros. It is used by `volprocs.c`; the stored fields are read by `VolMonitor` and used by `DeleteTrans` in `voltrans.c`.

## Risks and Edge Cases

The `_r` variants require the transaction lock in pthread builds. Passing `NULL` for `name` leaves the previous `lastProcName`, and `TClearRxCall` clears only the call pointer. In non-pthread builds, transaction object locks are no-ops, so correctness relies on the wider LWP/global-lock model.

## Test Signals

Tests should inspect `SAFSVolMonitor` during active dump/restore/forward calls, after completion, and after transaction deletion. Race-focused tests should verify no stale live `rxCallPtr` remains after normal completion and that deletion of a transaction with an active call marks the call dead.
