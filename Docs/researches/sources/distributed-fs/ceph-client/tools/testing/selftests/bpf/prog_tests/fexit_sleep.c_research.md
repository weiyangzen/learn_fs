# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_sleep.c

## Purpose
Tests sleepable fexit behavior across a cloned child stack/thread context.

## Important APIs, types, and functions
Uses `fexit_sleep.lskel.h`, `clone()`-style helper `do_sleep()`, `mmap()` stack allocation, `sched.h`, and time/syscall headers. The child triggers sleep/syscall behavior while fexit programs observe it.

## Control flow and state
The test loads/attaches the lightweight skeleton, allocates a stack, starts a child with `do_sleep()`, waits for completion, and checks skeleton BSS counters/results. State is stack mapping, child task, and skeleton BSS.

## Dependencies and integration points
Depends on sleepable fexit trampoline support, clone/fork permissions, and generated lskel. Integrated as `test_fexit_sleep()`.

## Risks and test signals
Risks include scheduling/timing and stack cleanup. Passing signal is successful child completion and expected fexit observations in BSS.
