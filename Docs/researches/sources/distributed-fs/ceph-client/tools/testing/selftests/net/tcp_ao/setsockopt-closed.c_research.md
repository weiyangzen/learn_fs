# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/setsockopt-closed.c

## Purpose
`setsockopt-closed.c` is a broad TCP-AO UAPI validation test for closed or listening sockets. It verifies option size handling, invalid argument rejection, duplicate key detection, optmem pressure behavior, AO info setting/getting, and TCP_AO_GET_KEYS filtering semantics.

## Important APIs, Types, And Functions
The file centers on `__setsockopt_checked()`, `setsockopt_checked()`, `getsockopt_checked()`, `prepare_defs()`, `test_extend()`, `extend_tests()`, `test_optmem_limit()`, `test_einval_add_key()`, `test_einval_del_key()`, `test_einval_ao_info()`, `test_einval_get_keys()`, `duplicate_tests()`, `prepare_test_keys()`, `filter_keys_checked()`, and `filter_tests()`. It exercises `TCP_AO_ADD_KEY`, `TCP_AO_DEL_KEY`, `TCP_AO_INFO`, and `TCP_AO_GET_KEYS`.

## Control Flow
`client_fn()` prepares an auxiliary MD5 client address, then runs extension-size tests, invalid-input tests, key filtering tests, and duplicate detection. Each case creates a fresh socket through `prepare_defs()`, pre-installs the minimal AO state required for the command, mutates one field, and calls the checked wrapper with the expected errno. Successful AO add/info/get operations are verified by a follow-up getsockopt comparison or returned-size check.

## State, Persistence, And Dependencies
The test creates many short-lived sockets and closes each in the checked wrapper. `test_optmem_limit()` reads the current optmem value and adds keys until kernel allocation limits are hit. The test depends on TCP-AO UAPI structs, optional TCP-MD5 support for one conflict case, and helper functions for preparing default AO keys and verifying socket keys.

## Integration Points
This file is the main ABI conformance test for AO socket options. It ties kernel validation paths to exact userspace errno values, validates old/new structure size compatibility, confirms current/rnext key semantics, and checks `TCP_AO_GET_KEYS` filters by address, key IDs, current/rnext flags, and capacity reporting.

## Risks
Because the test expects exact errno values, intentional kernel ABI changes require updating it. It touches optmem behavior that changed from global to per-namespace across kernels; the harness handles that but parallel optmem tests are risky. Random key insertion order tests filter robustness but can complicate reproduction if ordering bugs appear.

## Test Signals
`main()` declares 126 planned checks. Passing signals include expected `EINVAL`, `ENOENT`, `EEXIST`, `EFAULT`, `EKEYREJECTED`, or `EMSGSIZE` results, accepted extended option sizes, rejected undersized/null options, optmem limit detection, matching getsockopt output, correct duplicate rejection, and accurate key filter match counts.
