# sources/distributed-fs/ceph-client/io_uring/truncate.h

Purpose: declares ftruncate prep and issue hooks.

Important APIs/types/functions: `io_ftruncate_prep()` and `io_ftruncate()`.

Control flow: none.

State and persistence: none.

Dependencies/integration: used by opcode dispatch.

Risks/test signals: build integration and ftruncate opcode tests cover this header.
