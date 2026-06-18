# Research: sources/distributed-fs/ceph-client/tools/perf/bench/futex.h

Purpose: provides futex syscall wrappers and shared option state for perf futex benchmarks.

Important APIs/types/functions: `struct bench_futex_parameters` carries common options: threads, futex count, runtime, wake/requeue counts, shared/private, mlockall, multi, silent, and bucket count. Inline wrappers cover `futex_wait`, `futex_wake`, `futex_lock_pi`, `futex_unlock_pi`, and `futex_cmp_requeue`. It declares bucket helper functions from `futex.c`.

Control flow: wrappers call `syscall(SYS_futex, ...)` directly with operation plus private/shared flag, then return syscall result.

State and persistence: no internal state. The parameter struct is embedded as static state in benchmark files.

Dependencies and integration: depends on Linux futex ABI, syscall numbers, time types, and common bench users. It is the contract between futex benchmarks and raw kernel futex operations.

Risks: wrappers expose raw syscall return conventions; callers must inspect return and `errno` correctly. Operation flags are caller-composed, so misuse of `FUTEX_PRIVATE_FLAG` changes semantics.

Test signals: compile on supported Linux targets and exercise each futex benchmark path, especially PI and cmp-requeue operations.
