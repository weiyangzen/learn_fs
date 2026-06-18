<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib1.c

## Purpose
`urandom_read_lib1.c` implements the semaphore-backed shared-library USDT probe and versioned library API symbols used by USDT/uprobe attachment tests.

## Important APIs, Types, And Functions
- `urandlib_read_with_sema_semaphore` is exported in `.probes`.
- `urandlib_read_with_sema()` fires `STAP_PROBE3(urandlib, read_with_sema, ...)`.
- `urandlib_api_v1()` is a compat version for `urandlib_api` at `LIBURANDOM_READ_1.0.0`.
- `urandlib_api_v2()` is the default version for `urandlib_api` at `LIBURANDOM_READ_2.0.0`.
- `urandlib_api_sameoffset()` is declared as both compat and default symbol version for same-offset symbol-version tests.

## Control Flow
The probe function fires a USDT and returns. Versioned APIs return constants `1`, `2`, and `3` to distinguish attach targets and symbol versions.

## State And Persistence
The semaphore variable is ELF section state in the shared object. No mutable runtime state is otherwise kept.

## Dependencies And Integration Points
It depends on `sdt.h` and libbpf internal version macros. It is linked as a shared library for `urandom_read.c`.

## Risks And Edge Cases
Symbol version directives are linker-sensitive; build scripts must preserve versioned aliases. The same-offset version case intentionally stresses resolver behavior.

## Test Signals
USDT tests expect library `urandlib:read_with_sema` hits and successful attachment to old/default/same-offset symbol versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/urandom_read_lib1.c -->
