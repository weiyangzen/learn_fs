# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-tar.c

Purpose: exercises ptrace access to TAR, PPR, and DSCR while a child is in a suspended transactional-memory section. It verifies the live suspended state, the checkpointed state, and the effect of writing checkpointed special-purpose registers before transaction abort recovery.

Important APIs/types/functions: `tm_spd_tar()` is the tracee, `trace_tm_spd_tar()` is the tracer, and `ptrace_tm_spd_tar()` owns fork/shared-memory setup. It uses `shmget/shmat/shmdt/shmctl`, `tbegin.`, `tsuspend.`, `tresume.`, `mfspr/mtspr`, `show_tar_registers()`, `show_tm_checkpointed_state()`, and `write_ckpt_tar_registers()`.

Control flow: the child loads baseline checkpoint values, enters TM, changes TAR/PPR/DSCR, suspends, installs a third visible state, then waits for the parent. The parent attaches with ptrace, validates live values as `TAR_3/PPR_3/DSCR_3`, validates checkpoint values as `TAR_1/PPR_1/DSCR_1`, writes `TAR_4/PPR_4/DSCR_4`, releases the child, and expects the abort path to observe those written checkpoint values.

State and persistence behavior: SysV shared memory carries two control flags plus a ready flag. Register state exists only in the child CPU/TM context; the persistent test signal is the child's exit status. Shared memory is removed after `wait()`.

Dependencies and integration points: depends on HTM availability, non-synthetic TM, `tm.h`, `ptrace.h`, and `ptrace-tar.h`. It integrates with kselftest through `test_harness()`.

Risks and test signals: busy-wait synchronization can hang if the child never reaches suspend. Failures report mismatched register tuples or abnormal child status. The test skips on systems without real HTM.
