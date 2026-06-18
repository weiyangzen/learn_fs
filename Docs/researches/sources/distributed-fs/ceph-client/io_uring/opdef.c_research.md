<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/opdef.c -->
# sources/distributed-fs/ceph-client/io_uring/opdef.c

## Purpose
`opdef.c` is the central opcode definition table for io_uring. It maps every `IORING_OP_*` opcode to hot issue metadata (`io_issue_defs`) and cold metadata (`io_cold_defs`), including required file behavior, polling support, buffer selection, async data size, BPF filter context size/population, prep/issue handlers, cleanup hooks, failure hooks, opcode names, and SQE copy hooks.

## Important APIs, Types, and Functions
- `io_issue_defs[]` is indexed by opcode and consumed by core submission/issue paths.
- `io_cold_defs[]` is indexed by opcode and consumed by cleanup, failure, tracing/name lookup, and SQE-copy paths.
- `io_no_issue()` is a sentinel issue function for opcodes such as linked timeout that should never be directly issued.
- `io_eopnotsupp_prep()` is used for conditionally unsupported opcodes when kernel config disables their subsystem.
- `io_uring_get_opcode()` returns the opcode name or `"INVALID"`.
- `io_uring_op_supported()` reports whether an opcode has real support in this build.
- `io_uring_optable_init()` validates table sizes and mandatory prep/issue/name entries at boot.

## Control Flow
Core request initialization reads `io_issue_defs[opcode]` to validate ioprio, IOPOLL compatibility, buffer-select support, SQE128/mixed SQE requirements, file requirements, block plug hints, async data sizes, and BPF filter payload size. It then calls the opcode prep function. Issue calls `def->issue()`, and async fallback uses metadata such as pollin/pollout, hash/unbound workqueue flags, and async size.

Cleanup and failure paths use `io_cold_defs[opcode]`: `cleanup` frees opcode-specific request state, `fail` adjusts opcode-specific failure state such as partial IO or zero-copy notification flags, `sqe_copy` snapshots SQE data before async retry, and `name` supports fdinfo/tracing/debug. `io_uring_optable_init()` runs during io_uring init before request cache creation.

## State and Persistence Behavior
The tables are static const global state. They encode persistent behavioral policy for every opcode in the build. Conditional entries use `io_eopnotsupp_prep` when `CONFIG_NET`, `CONFIG_EPOLL`, or `CONFIG_FUTEX` support is absent, allowing `io_uring_op_supported()` and prep-time validation to reject unsupported operations cleanly.

## Dependencies and Integration Points
This file includes nearly every opcode module header: xattr, nop, fs, splice, sync, advise, open/close, uring_cmd, epoll, statx, net, msg_ring, timeout, poll, cancel, rw, waitid, futex, truncate, zcrx, plus core refs/tctx/sqpoll/fdinfo/kbuf/rsrc. It is the dispatch glue between `io_uring.c` and all opcode implementations.

## Risks and Edge Cases
- Table order must exactly match `IORING_OP_*` numeric values and `IORING_OP_LAST`; mismatches are caught by boot-time build/BUG checks but can be severe.
- Missing cleanup/fail/sqe_copy hooks cause leaks or wrong retry behavior for opcodes with allocated state or userspace pointers.
- Incorrect `needs_file`, `iopoll`, `buffer_select`, `pollin/pollout`, or async size metadata changes core behavior before the handler runs.
- Conditional support must use `io_eopnotsupp_prep`; a null prep or issue pointer is a boot BUG.
- SQE128-only opcodes (`NOP128`, `URING_CMD128`) require `is_128` metadata so the core consumes the correct SQE footprint.

## Test Signals
Build-time `io_uring_optable_init()` checks are primary. Runtime tests should verify `io_uring_op_supported()` under different kernel configs, every opcode's prep/issue dispatch, cleanup/fail hooks for cancellation, buffer-select capability enforcement, IOPOLL rejection for unsupported ops, SQE128/mixed behavior, BPF filter payload population, and opcode names in diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/opdef.c -->
