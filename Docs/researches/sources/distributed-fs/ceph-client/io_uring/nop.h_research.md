<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/nop.h -->
# sources/distributed-fs/ceph-client/io_uring/nop.h

## Purpose
`nop.h` declares the prep and issue functions for NOP-style io_uring operations.

## Important APIs, Types, and Functions
- `io_nop_prep()` validates and prepares NOP SQEs.
- `io_nop()` issues the prepared no-op request.

## Control Flow
The opcode table calls these functions for `IORING_OP_NOP` and `IORING_OP_NOP128`.

## State and Persistence Behavior
The header itself stores no state; request-local state is defined in `nop.c`.

## Dependencies and Integration Points
It depends on core `io_kiocb` and SQE types from io_uring headers and is consumed by `opdef.c`.

## Risks and Edge Cases
The header's minimal contract means all capability distinctions, including NOP128 and CQE32 support, must remain in `opdef.c` and `nop.c`.

## Test Signals
Build coverage plus NOP/NOP128 runtime tests validate this interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/nop.h -->
