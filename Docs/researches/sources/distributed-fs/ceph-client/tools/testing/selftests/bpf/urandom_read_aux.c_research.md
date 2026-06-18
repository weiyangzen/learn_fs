<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_aux.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_aux.c

## Purpose
`urandom_read_aux.c` provides the executable-local semaphore-less USDT function used by `urandom_read.c`.

## Important APIs, Types, And Functions
- `urand_read_without_sema()` fires `STAP_PROBE3(urand, read_without_sema, iter_num, iter_cnt, read_sz)`.

## Control Flow
The function has a single probe invocation and returns to the caller.

## State And Persistence
No state is stored. USDT metadata is emitted into the object at build time.

## Dependencies And Integration Points
It depends on `sdt.h` and is linked into the `urandom_read` executable so USDT tests can attach to `urand:read_without_sema`.

## Risks And Edge Cases
Probe argument order and group/name strings are ABI for tests; changing them breaks attach expectations.

## Test Signals
Each call from `urandom_read()` should produce one semaphore-less executable USDT hit with three integer arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_aux.c -->
