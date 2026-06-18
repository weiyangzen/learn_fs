# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-vmxcopy.c

Purpose: tests that kernel VMX copy loops during a page fault do not leak suspended transactional vector state into checkpointed state after abort.

Important APIs/types/functions: `test_vmxcopy()` creates a temp file mapping, uses VSR40, triggers a page faulting store while suspended, aborts, and compares vector value.

Control flow: the test maps file-backed pages, loads `vecin` into VSR40, begins a transaction, suspends, zeroes VSR40, stores into the mapping to force a kernel copy/page path, aborts, and stores VSR40 to `vecout`. If the transaction aborted, `vecout` must equal original `vecin`.

State and persistence behavior: temporary file is unlinked after mapping; mapped pages and fd are cleaned up on normal path. Vector register state is transient.

Dependencies and integration points: requires real HTM, ppc64le, VSX instructions, filesystem temp file support, and mmap.

Risks and test signals: uses assertions for setup. Failure prints leaked vector state and returns nonzero.
