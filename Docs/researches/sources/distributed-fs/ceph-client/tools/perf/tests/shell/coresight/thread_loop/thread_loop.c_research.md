<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/thread_loop.c -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/thread_loop.c

## Purpose

This workload creates one or more threads executing a tight arm64 assembly loop and optionally prints each Linux TID for CoreSight CID/VMID trace validation.

## Research

The file defines `_GNU_SOURCE`, supplies a fallback `SYS_gettid` value for arm64, and wraps `gettid()` with `syscall`. `thrfn` prints the TID when `SHOW_TID` is set, then runs inline assembly that increments and compares registers until a loop count is reached. `new_thr` starts a pthread. `main` validates thread count 1 to 256 and loop count in millions 1 to 4000, multiplies by 1,000,000, starts threads, and joins them. State is fixed-size thread args and optional stdout TID list. Dependencies are pthreads, arm64 inline assembly syntax, Linux gettid syscall, and environment variable `SHOW_TID`. Integration is with `thread_loop_check_tid_*.sh` and `perf_dump_aux_tid_verify`. Risks include inline assembly operand constraints not updating C variable expectations, stdout buffering, syscall-number assumptions outside arm64, and long runtimes at high loop counts. Test signal is every printed TID found in AUX dump CID/VMID fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/thread_loop.c -->
