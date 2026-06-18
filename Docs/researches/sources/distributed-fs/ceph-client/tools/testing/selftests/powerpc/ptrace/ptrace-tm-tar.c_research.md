# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-tar.c

Purpose: validates ptrace visibility and checkpoint modification of TAR/PPR/DSCR while a child is inside a normal transaction rather than the separate suspended-state variant.

Important APIs/types/functions: `tm_tar()` creates the child transaction and suspended synchronization point; `trace_tm_tar()` attaches and uses TAR helpers from `ptrace.h`; `ptrace_tm_tar()` handles SysV shared memory and lifecycle.

Control flow: the child initializes checkpoint values, begins a transaction, changes the live transactional values, suspends only long enough to set a parent-visible flag, resumes, and loops. The parent waits for that flag, reads live registers (`TAR_2/PPR_2/DSCR_2`), reads checkpointed registers (`TAR_1/PPR_1/DSCR_1`), writes new checkpoint values, and detaches so the child abort path can validate them.

State and persistence behavior: a two-slot shared memory array carries release and ready flags. Register state is transient and verified through both ptrace and direct child `mfspr()` after abort.

Dependencies and integration points: real HTM, `ptrace-tar.h` constants, and powerpc ptrace regsets are required. It uses `test_harness()` for kselftest status.

Risks and test signals: the infinite transactional loop relies on the parent to change shared memory. Any ptrace, validation, or child-exit mismatch fails the test.
