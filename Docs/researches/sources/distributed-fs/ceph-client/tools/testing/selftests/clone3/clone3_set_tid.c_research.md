# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_set_tid.c

## Purpose

`clone3_set_tid.c` is a detailed clone3 `set_tid` ABI test. It validates invalid set_tid sizes/values, PID reuse, `CLONE_NEWPID`, nested PID namespace mappings, PID leak cleanup on error paths, and `/proc/$pid/status` `NSpid` reporting. The complete 418-line file was read.

## Important APIs, Types, and Functions

Constants and globals include `MAX_PID_NS_LEVEL`, `pipe_1`, and `pipe_2`. Helpers are `child_exit()`, `call_clone3_set_tid()`, and `test_clone3_set_tid()`.

## Control Flow

`main()` verifies clone3, opens pipes, reads `/proc/sys/kernel/pid_max`, runs invalid-size and invalid-value test rows, skips root-only parts when non-root, then as root finds a free PID, reallocates it, tests namespace-specific PID creation, unshares a PID namespace, runs nested child tests, synchronizes with a clone3 child via pipes, reads `NSpid` from `/proc/<pid>/status`, and folds child kselftest counts back into the parent.

## State and Persistence Behavior

It creates and reaps many short-lived processes, unshares PID namespaces, uses pipes for synchronization, and reads procfs. No persistent files are written.

## Dependencies and Integration Points

It depends on clone3 `set_tid`, PID namespaces, root privileges for most positive tests, `/proc/sys/kernel/pid_max`, `/proc/$pid/status`, kselftest, and `clone3_selftests.h`.

## Risks and Edge Cases

The file assumes execution in the host PID namespace for several expected errors. Nested namespace depth can alter the `MAX_PID_NS_LEVEL - 1` comments. PID reuse is inherently timing-sensitive, though the test immediately uses a just-freed PID. Manual kselftest count adjustment is subtle.

## Test Signals

Signals include exact errno matches for invalid inputs, success for PID 1 in new namespaces, expected parent-visible PIDs, leak checks allowing later PID allocation, and `NSpid` containing the requested outer/middle/inner PID tuple.
