# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/exec_target.c

## Purpose
Minimal exec target used by fork/exec microbenchmarks.

## Important APIs, Types, and Functions
Defines `_start()` directly and invokes the `exit` syscall with status 0 using `syscall(SYS_exit, 0)`.

## Control Flow
The program enters at `_start`, performs one syscall, and terminates without libc startup or teardown.

## State and Persistence
No mutable or persistent state.

## Dependencies and Integration Points
Built with `-nostdlib` by the benchmarks Makefile and launched by `fork.c` when measuring fork or vfork plus exec overhead.

## Risks and Test Signals
Risk is architecture/libc/syscall ABI mismatch. A successful exec returns quickly with exit code 0, isolating exec overhead from program initialization cost.
