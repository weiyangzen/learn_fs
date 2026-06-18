# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/vfork_exec.c

## Purpose
Tests time namespace behavior across `vfork` plus `exec`, including validation from both the execed process and a thread.

## Important APIs, Types, and Functions
Functions include `tcheck`, `check_in_thread`, `check`, and `main`. It uses pthreads, `vfork`, `exec`, clock reads, and shared timens helpers.

## Control Flow
The parent creates a time namespace and sets offsets, then uses `vfork`/`exec` to re-run or run a checking path. The check compares current clock values against expected namespace-shifted values and also performs a threaded check to ensure namespace semantics are consistent with threads.

## State and Persistence Behavior
Namespace offsets survive through the process transition. Runtime state includes expected times passed through arguments or inherited state and thread-local checks. No persistent files are written.

## Dependencies and Integration Points
Depends on `vfork`, `exec`, pthreads, time namespace support, and kselftest. It integrates with process-creation and namespace inheritance semantics.

## Risks and Edge Cases
`vfork` has strict parent/child memory-sharing constraints before exec. Timing comparison must allow elapsed time during process creation. Privilege failures should be skipped cleanly.

## Test Signals
Signals are pass/fail from both direct and threaded checks after vfork/exec under shifted namespace time.
