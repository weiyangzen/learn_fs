# sources/distributed-fs/ceph-client/tools/testing/selftests/sgx/test_encl.c

## Purpose
Implements the code that runs inside the test enclave. It is a tiny freestanding command dispatcher used by host SGX tests to read/write enclave memory and execute SGX2 ENCLU operations.

## Important APIs, types, and functions
Defines a page-aligned initialized `encl_buffer`, ENCLU function IDs, and operation handlers: `do_encl_emodpe()`, `do_encl_eaccept()`, `do_encl_init_tcs_page()`, buffer/address get/put helpers, and no-op. Freestanding local `memcpy()` and `memset()` avoid libc. `encl_body()` dispatches through `encl_op_array`.

## Control flow
On entry, `encl_body()` receives an operation pointer, checks that the operation type is in range, and calls the matching handler. Memory handlers copy magic values between operation structs and enclave memory. `EACCEPT` and `EMODPE` build `sgx_secinfo` and call ENCLU helpers. TCS initialization writes the TCS page fields needed for dynamic TCS tests.

## State and persistence
The static `encl_buffer` persists for the life of the enclave and is used for host-visible round trips. Handlers mutate operation structs and target enclave pages.

## Dependencies and integration points
Compiled into `test_encl.elf` with `test_encl_bootstrap.S`; uses operation layouts from `defines.h` and ENCLU helpers from kernel SGX headers.

## Risks
Freestanding code has no runtime safety net. Host-provided addresses are trusted, so invalid operations intentionally produce enclave exceptions observed by host tests. TCS layout writes must match SGX hardware expectations.

## Test signals
Host tests observe successful magic value round trips, `eaccept_op.ret == 0`, clean `EEXIT`, or expected exception fields after invalid memory access.
