# sources/distributed-fs/ceph-client/fs/smb/client/smb2maperror_test.c

## Purpose

This is a KUnit test module for SMB2 error mapping. It verifies that every generated `status_to_posix_error` table entry exported by `smb2maperror.c` can be found through the same binary-search lookup used by production code.

## Important APIs, types, and functions

- `test_cmp_map()` calls `smb2_get_err_map_test()` for one expected record and checks non-null result, status code equality, errno equality, and status-string equality.
- `maperror_test_check_search()` iterates from `0` to `smb2_error_map_num - 1` over `smb2_error_map_table_test`.
- `maperror_test_cases` registers the single exhaustive search test.
- `maperror_suite` names the KUnit suite `smb2_maperror`.

## Control flow

When the KUnit suite runs, it executes `maperror_test_check_search()`. The test loops over the exported generated table and delegates each row to `test_cmp_map()`. A missing lookup aborts that row with `KUNIT_ASSERT_NOT_NULL`; mismatched fields are reported with `KUNIT_EXPECT_*` checks.

## State and persistence behavior

The test does not mutate SMB client state and performs no I/O. It relies on read-only exported pointers/counts from the production mapping file when `CONFIG_SMB_KUNIT_TESTS` is enabled. It registers as a kernel test module with GPL metadata.

## Dependencies and integration points

The file includes KUnit, CIFS global definitions, `smb2glob.h`, and `smb2proto.h`. It depends on the production file exporting `smb2_get_err_map_test`, `smb2_error_map_table_test`, and `smb2_error_map_num` only for the `smb2maperror_test` module.

## Risks and edge cases

The test proves table rows are searchable, which indirectly detects sort/order problems and comparator mismatches. It does not check behavior for unknown statuses, log suppression, trace emission, `map_smb2_to_linux_error()` header parsing, or init-time order validation. Because it compares `status_string` with `KUNIT_EXPECT_STREQ`, table strings must be valid non-null C strings.

## Test signals

The direct signal is the KUnit suite `smb2_maperror`. A pass indicates every generated mapping row round-trips through `smb2_get_err_map_test()`. Complementary coverage should exercise unmapped status fallback and selected user-visible errno mappings through `map_smb2_to_linux_error()`.
