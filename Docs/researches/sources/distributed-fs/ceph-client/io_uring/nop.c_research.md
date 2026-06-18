<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/nop.c -->
# sources/distributed-fs/ceph-client/io_uring/nop.c

## Purpose
`nop.c` implements `IORING_OP_NOP` and `IORING_OP_NOP128`. Besides a basic no-op completion, it supports test/control flags for injected results, file lookup, fixed-file lookup, fixed-buffer lookup, task-work completion, and 32-byte CQE payloads.

## Important APIs, Types, and Functions
- `struct io_nop` stores result, optional fd, flags, and extra CQE32 payload words.
- `io_nop_prep()` validates `nop_flags`, reads injected result, optional fd, fixed buffer index, and CQE32 extra fields.
- `io_nop()` performs optional file/fixed-buffer lookup, marks failure on negative result, sets normal or 32-byte CQE result, and optionally completes through task_work.

## Control Flow
Prep accepts only `NOP_FLAGS`. If `IORING_NOP_INJECT_RESULT` is set, `sqe->len` becomes the completion result; otherwise result is zero. `IORING_NOP_FILE` records an fd and `IORING_NOP_FIXED_FILE` controls fixed vs normal lookup. `IORING_NOP_FIXED_BUFFER` stores `buf_index`. `IORING_NOP_CQE32` requires a ring configured for CQE32 or mixed CQE and stores extra fields from `off` and `addr`.

Issue optionally resolves a file, optionally finds a fixed buffer resource, marks failure on errors, writes `req->cqe`, and either returns `IOU_COMPLETE` or queues `io_req_task_complete` and returns `IOU_ISSUE_SKIP_COMPLETE` for task-work testing.

## State and Persistence Behavior
State is request-local. A normal file lookup sets `req->file` and follows core cleanup. Fixed file lookup sets `REQ_F_FIXED_FILE`. Fixed buffer lookup attaches resource state through the resource subsystem. CQE32 extras are stored in `req->big_cqe` through `io_req_set_res32()`.

## Dependencies and Integration Points
This module depends on core request helpers and registered resource lookup. `opdef.c` wires it to both NOP opcodes, with `NOP128` marked as requiring a 128-byte SQE in mixed/128 modes.

## Risks and Edge Cases
- CQE32 NOP must reject rings without CQE32/mixed CQE support.
- Injected negative results must call `req_set_fail()` to interact correctly with links and CQE-skip semantics.
- Task-work completion returns skip-complete so the core does not post a duplicate CQE.

## Test Signals
Tests should cover plain NOP, injected positive/negative results, linked NOP failure, normal/fixed file lookup, fixed buffer lookup failure, task-work completion, CQE32 extra data, and NOP128 submission in SQE128/mixed modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/nop.c -->
