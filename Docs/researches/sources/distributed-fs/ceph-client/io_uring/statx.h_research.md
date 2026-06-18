# sources/distributed-fs/ceph-client/io_uring/statx.h

Purpose: declares statx prep, issue, and cleanup hooks.

Important APIs/types/functions: `io_statx_prep()`, `io_statx()`, and `io_statx_cleanup()`.

Control flow: none.

State and persistence: none in the header; cleanup declaration reflects delayed filename ownership.

Dependencies/integration: consumed by io_uring opcode dispatch and cleanup tables.

Risks/test signals: build coverage and statx cancellation tests validate the contract.
