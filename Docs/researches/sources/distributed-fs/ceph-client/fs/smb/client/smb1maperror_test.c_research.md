# sources/distributed-fs/ceph-client/fs/smb/client/smb1maperror_test.c

## Purpose
`smb1maperror_test.c` provides KUnit coverage for the SMB1 error mapping table search wrappers exported when `CONFIG_SMB1_KUNIT_TESTS` is enabled.

## Important APIs, types, and functions
The test helpers are `test_cmp_ntstatus_to_dos_err`, `test_cmp_smb_to_posix_error`, and macro-generated cases `check_search_ntstatus_to_dos_map`, `check_search_mapping_table_ERRDOS`, and `check_search_mapping_table_ERRSRV`. The suite is registered as `smb1_maperror`.

## Control flow
Each generated test iterates every exported table entry, searches by the key field, asserts that the result is non-null, and compares all relevant fields with the expected table element. The suite then runs the three table-search cases.

## State and persistence
The test has no persistent state. It reads exported pointers and counts from `smb1maperror.c`.

## Dependencies and integration points
It depends on KUnit, `smb1proto.h` test-only exports, and NT/DOS error definitions. It is gated by the SMB1 KUnit config and is intended to validate binary search correctness for generated mapping tables.

## Risks and test signals
The test catches unsorted or unsearchable table entries but does not directly test `map_smb_to_linux_error` behavior, logging, default `-EIO`, reconnect signaling, or special NTSTATUS overrides. Useful additions would construct SMB headers for zero status, NTSTATUS mapped/unmapped cases, legacy ERRDOS/ERRSRV, `ERRbaduid`, and reparse/privilege special cases.
