# sources/distributed-fs/ceph-client/io_uring/splice.h

Purpose: declares io_uring splice and tee prep/issue/cleanup hooks.

Important APIs/types/functions: prototypes are `io_tee_prep()`, `io_tee()`, `io_splice_cleanup()`, `io_splice_prep()`, and `io_splice()`.

Control flow: none.

State and persistence: no state is defined; the cleanup prototype signals that splice may hold a fixed-resource reference.

Dependencies/integration: used by opdef dispatch and cleanup handling for splice/tee opcodes.

Risks/test signals: build integration and fixed-file splice tests cover the header contract.
