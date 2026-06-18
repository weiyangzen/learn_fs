# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_lockup.c

## Purpose
Stresses a BPF timer locking race intended to detect lockups or bad deadlock error propagation when two timer programs run on separate CPUs.

## APIs, Types, and Functions
Exports `test_timer_lockup()`. `timer_lockup_thread()` pins a pthread to a distinct CPU and repeatedly runs one BPF program with an IPv4 packet test context.

## Control Flow, State, and Persistence
The test requires at least two CPUs. It opens the skeleton, records BSS error pointers for timer1 and timer2, then starts two affinity-pinned threads running `timer1_prog` and `timer2_prog`. Threads stop when either error value is set or after enough attempts to declare the race unreproduced and skip. Final assertions allow `0` or `-EDEADLK` for both timer errors.

## Dependencies and Integration
Depends on pthread CPU affinity, `get_nprocs()`, `network_helpers` packet data, `timer_lockup.skel.h`, and `bpf_prog_test_run_opts`.

## Risks and Test Signals
Risks include race non-reproducibility, CPU affinity failure in constrained environments, and static globals retaining skip/error state across reruns in one process. Signals are no process lockup, no unexpected error values, and skip when the race cannot be reproduced in bounded attempts.
