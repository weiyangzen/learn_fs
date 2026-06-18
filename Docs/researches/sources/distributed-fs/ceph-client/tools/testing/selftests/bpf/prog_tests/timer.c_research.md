# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/timer.c

## Purpose
Exercises BPF timer functionality, including normal timer callbacks, async cancellation, spin-lock stress, NMI-context races, map-in-map timer lifetime, verifier failure cases via `timer_failure`, and interrupt-context behavior.

## APIs, Types, and Functions
Test entry points are `serial_test_timer()`, `serial_test_timer_stress()`, `serial_test_timer_stress_async_cancel()`, `serial_test_timer_async_cancel()`, `serial_test_timer_stress_nmi_race()`, `serial_test_timer_stress_nmi_update()`, `serial_test_timer_stress_nmi_cancel()`, and `test_timer_interrupt()`. Helpers include `perf_event_open()`, `spin_lock_thread()`, `timer_stress_runner()`, `run_nmi_test()`, `timer()`, `timer_cancel_async()`, and `test_timer()`.

## Control Flow, State, and Persistence
`test_timer()` opens/loads the `timer` skeleton, skipping on `EOPNOTSUPP`, then invokes a supplied scenario. The normal timer test attaches programs, runs a test program, detaches, sleeps briefly, and checks callback counters, BSS values, pinned callback counters, error flags, and completion bits. Stress tests run many `bpf_prog_test_run_opts()` calls across eight pthreads while toggling async cancellation. NMI tests fork a CPU-consuming child, attach a perf-event program to CPU cycles, and assert hit/update/cancel counters. `test_timer_interrupt()` checks timer callback interrupt context through `timer_interrupt`.

## Dependencies and Integration
Uses libbpf skeletons `timer`, `timer_failure`, and `timer_interrupt`, perf events, pthreads, fork/wait, `bpf_prog_test_run_opts`, and test harness serial entry points. It integrates with kernel timer map value semantics and perf-event attachment.

## Risks and Test Signals
Risks include timing flakiness from short sleeps, perf hardware event unavailability, races that are hard to reproduce, and architecture/preemption differences in interrupt accounting. Signals are exact counter values, zero BPF-side error flags, expected verifier failures from `RUN_TESTS(timer_failure)`, perf-event skip on unsupported hardware, and no hangs under concurrent timer operations.
