# sources/distributed-fs/ceph-client/io_uring/cancel.h

## Purpose
The header defines shared cancellation data and APIs used across io_uring subsystems.

## Important APIs, Types, And Functions
- `struct io_cancel_data` carries context, userdata, file, opcode, flags, and sequence.
- Declarations cover async/sync cancel, try-cancel, match helpers, list removal, ring/request teardown, and generic task cancellation.
- `io_cancel_match_sequence()` marks requests with a sequence to avoid reprocessing in `ALL` cancellation scans.

## Control Flow
The inline sequence helper returns true if the request already saw the current cancel sequence, otherwise records it and returns false.

## State And Persistence
It references per-request `cancel_seq_set` and `work.cancel_seq`, and per-cancel `seq` from `ctx->cancel_seq`.

## Dependencies And Integration Points
It includes `io_uring_types.h` and is consumed by poll, waitid, futex, uring_cmd, io-wq cancellation, and ring teardown code.

## Risks And Edge Cases
The sequence helper mutates request state during matching; callers must only use it in contexts where request lifetime is protected. Prototype drift would affect many cancellation-capable subsystems.

## Test Signals
Cancel-all tests that would otherwise double count or loop over the same request validate sequence matching.
