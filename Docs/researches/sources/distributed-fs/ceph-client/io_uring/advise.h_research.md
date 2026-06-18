# sources/distributed-fs/ceph-client/io_uring/advise.h

## Purpose
This header declares io_uring madvise/fadvise prep and issue handlers for use by the operation definition table.

## Important APIs, Types, And Functions
- `io_madvise_prep()` and `io_madvise()`.
- `io_fadvise_prep()` and `io_fadvise()`.

## Control Flow
No local control flow. The declarations connect `opdef` dispatch to `advise.c`.

## State And Persistence
No state is defined here.

## Dependencies And Integration Points
It depends on forward-visible `struct io_kiocb` and `struct io_uring_sqe` declarations from including context. It is part of the io_uring opcode integration surface.

## Risks And Edge Cases
Prototype drift with `advise.c` or `opdef` would cause build failures or operation dispatch mismatch.

## Test Signals
Build coverage and successful dispatch of advise operations validate this header.
