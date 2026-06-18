# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_uninit.c

## Purpose
`verifier_uninit.c` tests basic verifier rejection of uninitialized and invalid register use. It also checks that `R0` must be initialized on every exit path.

## Important APIs, Types, and Functions
The file uses socket-section naked assembly and low-level instruction encoding from `../../../include/linux/filter.h`. It defines four tests: reading uninitialized `R2`, encoding an invalid register move from `R15`, exiting without setting `R0`, and a branch where only one path initializes `R0`.

## Control Flow
Each test is minimal. `read_uninitialized_register` moves `r2` to `r0`. `read_invalid_register` embeds a raw `BPF_MOV64_REG` instruction with source register `-1`, printed as invalid `R15`. `t_init_r0_before_exit` copies `r1` to `r2` then exits with unreadable `R0`. `before_exit_in_all_branches` conditionally skips the instructions that set `r0`.

## State and Persistence
There is no persistent state. The tested state is verifier register initialization and read-ok tracking. The branch test also exercises path-sensitive exit-state merging.

## Dependencies and Integration Points
The file depends on BPF verifier register validity checks, socket program loading, and selftest failure-message matching. Unprivileged behavior is also annotated, including a pointer comparison message for the branch case.

## Risks and Test Signals
Risks include accepting reads from unreadable registers, accepting invalid encoded register numbers, or allowing programs to exit without a defined return value. Test signals are expected messages `R2 !read_ok`, `R15 is invalid`, and `R0 !read_ok`.
