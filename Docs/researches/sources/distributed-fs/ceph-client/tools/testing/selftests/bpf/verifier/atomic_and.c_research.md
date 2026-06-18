<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_and.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_and.c

## Purpose
This verifier test fragment defines test cases for `BPF_ATOMIC_AND` semantics with and without `BPF_FETCH`, including 64-bit, 32-bit, and `r0` source-register cases.

## Important APIs, Types, And Functions
- Each fragment entry is a `struct bpf_test` initializer consumed by `test_verifier.c`.
- Instructions use `BPF_ST_MEM`, `BPF_MOV64_IMM`, `BPF_MOV32_IMM`, `BPF_ATOMIC_OP(BPF_DW/W, BPF_AND | optional BPF_FETCH, ...)`, loads, jumps, and exits.
- Expected `.result = ACCEPT` verifies the verifier allows these atomic operations.

## Control Flow
The programs store initial stack values, perform atomic AND, check returned old values when `BPF_FETCH` is set, check memory now contains the AND result, and exit with nonzero codes on semantic mismatch. The non-fetch case also verifies the source register is not clobbered. The fetch cases verify old-value return and `r0` preservation/source-register behavior.

## State And Persistence
State is confined to BPF stack slots and registers during `BPF_PROG_TEST_RUN`. No maps or external fixtures are used.

## Dependencies And Integration Points
The file is included into generated verifier tests via `<verifier/tests.h>` and executed by `test_verifier.c`.

## Risks And Edge Cases
Atomic register clobber semantics are JIT-sensitive, especially the explicit `r0` checks. The 32-bit case relies on correct zero/sign behavior around a starting `-1` in `r0`.

## Test Signals
Verifier load must accept each case, and runtime return value must be zero. Nonzero exits indicate incorrect atomic result, incorrect fetched old value, or unintended register clobbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/atomic_and.c -->
