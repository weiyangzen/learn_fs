# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/memfd_secret.c

## Purpose

`memfd_secret.c` tests the `memfd_secret` syscall and secretmem access restrictions. It verifies mlock accounting, disabled file I/O, blocked `vmsplice`, blocked `process_vm_readv`, and blocked ptrace reads.

## Important APIs, Types, and Functions

The file wraps `syscall(__NR_memfd_secret)` in `memfd_secret()`. It uses `mmap(MAP_SHARED)`, `ftruncate()`, `RLIMIT_MEMLOCK`, libcap `cap_set_proc()` to drop capabilities, `vmsplice()`, `process_vm_readv()`, `ptrace(PTRACE_ATTACH/PTRACE_PEEKDATA)`, pipes, and fork. Core test functions are `test_mlock_limit()`, `test_file_apis()`, `test_vmsplice()`, `test_process_vm_read()`, and `test_ptrace()`.

## Control Flow

`prepare()` captures page size and memlock limits, raises too-small limits to at least a page for test calculations, and drops capabilities with a bounded `RLIMIT_MEMLOCK`. `main()` creates a secret memfd, truncates it to one page, then runs six tests. Remote-access tests fork a child, pass the parent's mapped secret address through a pipe, and consider failure, skip, or signal termination as evidence that remote reads were blocked.

## State and Persistence Behavior

The secret fd and mappings are transient. The process modifies its own rlimit and drops capabilities, which persists for the remainder of the process. Pipes coordinate parent-child timing. Secret memory contents are filled with `PATTERN` to make unintended reads meaningful.

## Dependencies and Integration Points

It depends on `__NR_memfd_secret`, secretmem kernel support, `sys/capability.h`, and kselftest. It integrates with GUP-fast, pipe splice, ptrace, cross-process memory APIs, and memlock enforcement.

## Risks and Edge Cases

When `__NR_memfd_secret` is not defined or returns `ENOSYS`, the test skips. Some remote-access failures are intentionally broad because the child may exit with pass or be signaled. `test_mlock_limit()` assumes mapping twice the hard memlock limit fails after capability dropping.

## Test Signals

There are six planned checks: mlock limit respected, file I/O blocked, `vmsplice` blocked on a fresh page, `vmsplice` blocked on an existing page, `process_vm_readv` blocked or skipped if unsupported, and ptrace blocked.
