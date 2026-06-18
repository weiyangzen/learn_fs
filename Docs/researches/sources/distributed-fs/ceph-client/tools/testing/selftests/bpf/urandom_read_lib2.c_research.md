<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib2.c

## Purpose
`urandom_read_lib2.c` implements the semaphore-less shared-library USDT probe for `urandom_read` USDT tests.

## Important APIs, Types, And Functions
- `urandlib_read_without_sema()` fires `STAP_PROBE3(urandlib, read_without_sema, iter_num, iter_cnt, read_sz)`.

## Control Flow
The function simply emits the USDT probe with three arguments and returns.

## State And Persistence
No runtime state is stored; USDT note metadata is emitted into the shared object.

## Dependencies And Integration Points
It depends on `sdt.h` and is linked into the shared-library side of `urandom_read`.

## Risks And Edge Cases
Group/name and argument ordering are the test ABI. If built into the wrong object, tests expecting shared-library USDTs will not attach.

## Test Signals
Each `urandom_read()` iteration should produce one `urandlib:read_without_sema` hit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib2.c -->
