# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer_start_deadlock.c

## Purpose
Regression test ensuring `bpf_timer_start()` from a syscall-triggered BPF path does not deadlock when combined with the tracepoint path used by the BPF program.

## APIs, Types, and Functions
Defines `test_timer_start_deadlock()`, using the `timer_start_deadlock` skeleton and the `start_timer` BPF program.

## Control Flow, State, and Persistence
The skeleton opens/loads, attaches, retrieves the `start_timer` program fd, and runs it through `bpf_prog_test_run_opts()`. If the kernel deadlocks, the call never returns. On success it checks retval zero and BSS `tp_called == 1`.

## Dependencies and Integration
Depends on `timer_start_deadlock.skel.h`, syscall-program test-run support, and the test harness.

## Risks and Test Signals
The failure mode is a hang rather than a normal assertion. Passing signals are successful load/attach, returning test-run, retval zero, and tracepoint callback observed exactly once.
