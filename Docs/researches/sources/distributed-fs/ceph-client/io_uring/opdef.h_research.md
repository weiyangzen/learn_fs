<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/opdef.h -->
# sources/distributed-fs/ceph-client/io_uring/opdef.h

## Purpose
`opdef.h` declares the opcode metadata structures and global tables that bind core io_uring submission to individual opcode handlers.

## Important APIs, Types, and Functions
- `struct io_issue_def` contains hot-path metadata: file requirement, block plug hint, ioprio/iopoll support, buffer selection support, workqueue hashing/unbound hints, poll direction/exclusive flags, audit skipping, vectored flag, 128-byte SQE flag, async data size, BPF filter payload size, issue/prep callbacks, and BPF populate callback.
- `struct io_cold_def` contains colder metadata: opcode name, SQE copy hook, cleanup hook, and fail hook.
- `io_issue_defs[]` and `io_cold_defs[]` are extern arrays indexed by opcode.
- `io_uring_op_supported()` reports build-time opcode availability.
- `io_uring_optable_init()` performs boot-time validation.

## Control Flow
The core initializes requests using `io_issue_defs[opcode].prep`, later issues through `.issue`, and consults metadata before either step. Cleanup and failure paths consult `io_cold_defs[opcode]`. BPF filtering uses `filter_pdu_size` and `filter_populate`.

## State and Persistence Behavior
The header defines static metadata contracts; actual state lives in the arrays in `opdef.c`. The tables are immutable after initialization.

## Dependencies and Integration Points
It forward-declares `struct io_uring_bpf_ctx` and relies on core `struct io_kiocb` and SQE types. It is included by `io_uring.h`, opcode handlers, and dispatch code.

## Risks and Edge Cases
- Bitfield metadata is compact and hot-path-sensitive; adding a new opcode capability requires updating both the struct and all relevant core consumers.
- Async data sizes must match the handler's expected `req->async_data` layout.
- `is_128` must be set for opcodes that consume 128-byte SQEs.

## Test Signals
Compile-time and boot-time table validation plus broad opcode selftests validate this header contract. New opcodes should add tests for metadata-driven rejection and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/opdef.h -->
