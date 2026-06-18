# sources/distributed-fs/ceph-client/io_uring/advise.c

## Purpose
`advise.c` implements io_uring operations for `madvise` and `fadvise`, translating SQE fields into VM and VFS advisory calls.

## Important APIs, Types, And Functions
- `struct io_madvise` stores address, length, and advice.
- `struct io_fadvise` stores file, offset, length, and advice.
- `io_madvise_prep()` validates unused SQE fields, reads `addr`, `off`/`len`, and `fadvise_advice`, and forces async execution.
- `io_madvise()` calls `do_madvise(current->mm, ...)`.
- `io_fadvise_prep()` parses offset/length/advice and forces async for advice values that may block.
- `io_fadvise()` calls `vfs_fadvise(req->file, ...)`.

## Control Flow
Preparation copies SQE values into per-request command storage. Execution warns if a force-async operation somehow arrives in nonblocking issue mode, invokes the backing syscall helper, sets failure state for negative `fadvise` results, and completes through `IOU_COMPLETE`.

## State And Persistence
No persistent io_uring state is kept. Effects are advisory VM or file-cache state managed by MM/VFS.

## Dependencies And Integration Points
The file depends on io_uring request helpers, SQE layout, `CONFIG_ADVISE_SYSCALLS`, `CONFIG_MMU`, `do_madvise`, and `vfs_fadvise`. `advise.h` exposes operation hooks to the opcode table.

## Risks And Edge Cases
Unsupported MM/advice configurations return `-EOPNOTSUPP`. Length can be sourced from either `off`/`addr` or fallback `len`, so SQE field interpretation must match userspace ABI. Blocking advice must not execute from a nonblocking path.

## Test Signals
io_uring tests for `IORING_OP_MADVISE`/`FADVISE` should cover invalid reserved fields, unsupported configs, async forcing, and result parity with direct syscalls.
