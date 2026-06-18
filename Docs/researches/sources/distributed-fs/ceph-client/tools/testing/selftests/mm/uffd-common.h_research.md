<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.h

## Purpose
Common interface and shared type definitions for userfaultfd selftests. It centralizes includes, error macros, feature flags, memory backend abstractions, global test state, worker argument state, and declarations implemented in `uffd-common.c`.

## Important APIs, Types, and Functions
- Defines `UFFD_FLAGS` as `O_CLOEXEC | O_NONBLOCK | UFFD_USER_MODE_ONLY`.
- `struct uffd_global_test_opts` carries test geometry, mapping pointers, uffd fd/flags, pipes, counters, backend type, shared/private mode, write-protect enablement, and fork readiness.
- `struct uffd_args` carries per-thread CPU id, fault counters, apply-WP flag, global options pointer, and optional custom fault handler.
- `struct uffd_test_ops` abstracts memory allocation, page release, alias address rewriting, and PMD mapping checks.
- `struct uffd_test_case_ops` allows per-test `pre_alloc` and `post_alloc` hooks.
- Declares UFFD helpers, page helpers, stats helpers, open paths, and constants `TEST_ANON`, `TEST_HUGETLB`, and `TEST_SHMEM`.

## Control Flow
This header does not execute logic itself. It defines the contract followed by memory backends and test drivers: callers choose an operation table, set `uffd_test_case_ops` when needed, call `uffd_test_ctx_init()`, register mappings, run worker threads, then call `uffd_test_ctx_clear()`.

## State and Persistence Behavior
The header declares global operation pointers and, as an extern, `uffd_gtest_opts`; actual storage and mutation live in C files. All state is in-process and tied to kernel fds/mappings rather than persistent disk data.

## Dependencies and Integration Points
Includes `kselftest.h` and `vm_util.h`, plus Linux UFFD, mmap, syscall, pthread, poll, signal, wait, atomic, and integer headers. It is an integration point for all userfaultfd tests in this mm selftest area.

## Risks and Edge Cases
Because it exposes global backend pointers, tests must set `uffd_test_ops` before initialization. The error macros always exit, so helper failures are terminal. Compatibility depends on kernel UFFD definitions and architecture support for the included ABI headers.

## Test Signals
Signals are indirect: functions declared here return standard kselftest pass/skip/fail outcomes through their callers. Fatal helper errors print source file and line via `_err()`/`err()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/mm/uffd-common.h -->
