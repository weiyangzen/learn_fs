<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read.c

## Purpose
`urandom_read.c` is a USDT target executable. It reads `/dev/urandom`, fires semaphore and non-semaphore USDT probes from the main executable and shared libraries, and calls versioned library APIs for symbol-versioning attach tests.

## Important APIs, Types, And Functions
- `urandom_read()` reads `BUF_SIZE` chunks, calls `urand_read_without_sema()`, fires `STAP_PROBE3(urand, read_with_sema, ...)`, then calls shared-library probe functions.
- `urand_read_with_sema_semaphore` is placed in `.probes` for semaphore-backed USDT.
- `COMPAT_VERSION(urandlib_api_old, urandlib_api, LIBURANDOM_READ_1.0.0)` declares access to an older symbol version.
- `handle_sigpipe()` marks `parent_ready` when a supervising parent closes stdout.
- `main()` optionally reports its PID until parent synchronization, then runs probe loops and versioned API calls.

## Control Flow
The program opens `/dev/urandom`, parses optional count and parent-sync mode, repeatedly prints its PID until SIGPIPE indicates the parent is ready, performs `count` random reads and USDT triggers, calls library APIs, closes the fd, and exits.

## State And Persistence
State is process-local: `/dev/urandom` fd, `parent_ready`, and USDT semaphore variable. USDT metadata and semaphores live in ELF sections for tracing tools; no disk state is modified.

## Dependencies And Integration Points
It depends on `sdt.h`, libbpf internal symbol-version macros, shared objects built from `urandom_read_lib1.c` and `urandom_read_lib2.c`, and BPF USDT/uprobe tests that attach to executable and shared-library probes.

## Risks And Edge Cases
Parent synchronization intentionally uses SIGPIPE from a closed stdout pipe, which is unusual but useful for trace attach ordering. Missing shared libraries or symbol versions break link/runtime behavior. `/dev/urandom` open failure exits early.

## Test Signals
BPF-side tests expect probe hit counts equal to read iterations for executable and library USDTs, correct semaphore handling, and successful attachment to default/compat/same-offset versioned symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read.c -->
