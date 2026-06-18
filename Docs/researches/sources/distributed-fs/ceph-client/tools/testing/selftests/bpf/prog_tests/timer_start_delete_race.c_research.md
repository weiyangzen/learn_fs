# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_start_delete_race.c

## Purpose
Stresses a race between `bpf_timer_start()` and map element deletion that could otherwise produce a use-after-free when a timer becomes scheduled after async cancellation/free starts.

## APIs, Types, and Functions
Defines `struct ctx`, `start_timer_thread()`, `delete_elem_thread()`, and public `test_timer_start_delete_race()`. Each worker repeatedly runs a BPF program from `timer_start_delete_race.skel.h`.

## Control Flow, State, and Persistence
The test opens/loads the skeleton, starts two pthreads pinned to CPUs 0 and 1, flips a volatile start flag, and runs 1000 iterations of timer start and map delete test-runs. Any syscall or BPF retval error increments `ctx.errors`. The final assertion requires zero thread errors; deeper UAF detection is expected from KASAN or kernel crash diagnostics if the bug exists.

## Dependencies and Integration
Uses pthreads, CPU affinity, `bpf_prog_test_run_opts`, and the generated skeleton. It integrates with kernel map deletion, timer scheduling, async refcounting, and RCU tasks trace behavior.

## Risks and Test Signals
Risks include systems with fewer CPUs, affinity failures not asserted, race non-determinism, and memory-safety failures being external to user-space assertions. Signals are zero worker errors and no KASAN/kernel crash during the stress window.
