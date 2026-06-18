
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/free_timer.c

## Purpose

`free_timer.c` stress-tests BPF timer freeing/overwriting races by concurrently running one BPF program that starts timers and another that overwrites/free-replaces them.

## Important APIs, Types, and Functions

The file uses `free_timer.skel.h`, `bpf_object__find_program_by_name()`, `bpf_prog_test_run_opts()`, pthreads, barriers, CPU affinity, and acquire/release atomics around the `start` flag. `run_ctx` carries program handles, a barrier, loop count, and stop/start flags.

## Control Flow and Data Flow

After skeleton load, the harness resolves `start_timer` and `overwrite_timer`, starts two CPU-pinned threads, releases them, and runs ten synchronized iterations. The start thread runs the timer-start program, signals overwrite, waits, and repeats. The overwrite thread waits for the signal, runs the overwrite program, then releases the start thread.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is BPF timer/map state inside the skeleton and user-space synchronization state. Dependencies include BPF timer support, at least two CPUs for intended affinity, pthread barriers, and `bpf_prog_test_run_opts()`. Integration is the kernel timer lifetime path under concurrent replacement. Risks are scheduling/affinity limitations, races masked by low iteration count, and `EOPNOTSUPP` feature skips. Test signals are zero thread return bitmasks and no test-run errors or nonzero BPF retvals from either thread.
