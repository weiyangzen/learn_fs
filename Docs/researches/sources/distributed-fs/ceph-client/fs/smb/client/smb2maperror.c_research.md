# sources/distributed-fs/ceph-client/fs/smb/client/smb2maperror.c

## Purpose

This file maps SMB2/NT status codes from response headers to Linux negative errno values. It wraps a generated sorted mapping table, performs binary search lookups, emits optional diagnostics and tracepoints, and exposes test-only symbols for KUnit verification.

## Important APIs, types, and functions

- `smb2_error_map_table[]` is built from generated `smb2_mapping_table.c` entries of `struct status_to_posix_error`.
- `cmp_smb2_status()` compares a raw status key with a table pivot for `__inline_bsearch()`.
- `smb2_get_err_map()` returns the mapping record for a CPU-endian SMB2 status code or `NULL`.
- `map_smb2_to_linux_error()` reads `struct smb2_hdr::Status`, returns `0` for success, maps known failures to POSIX errors, defaults unmapped failures to `-EIO`, and emits trace/debug output.
- `smb2_init_maperror()` verifies at init time that the generated table is sorted ascending by status code.
- Under `CONFIG_SMB_KUNIT_TESTS`, `smb2_get_err_map_test`, `smb2_error_map_table_test`, and `smb2_error_map_num` are exported to `smb2maperror_test`.

## Control flow

Successful responses immediately emit `trace_smb3_cmd_done()` and return `0`. Error responses suppress ordinary notice logging for expected continuation/EOF statuses unless CIFS FYI/RC logging is enabled. The CPU-endian status is looked up in the generated table; found entries supply `rc` and optional `pr_notice()`. All error exits emit debug mapping output and `trace_smb3_cmd_err()`. Unmapped or deliberately `-EIO` mappings also call `smb_EIO1()` for EIO tracing.

## State and persistence behavior

The mapping table is static read-only after compilation. The file changes no persistent state. It reads global logging flags such as `cifsFYI` and contributes to tracing/logging side effects.

## Dependencies and integration points

It depends on Linux errno definitions, CIFS debug and trace helpers, SMB2 protocol declarations, `smb2glob.h` for the mapping struct, and common SMB2 status constants. `smb2transport.c` calls this through the server operation mapping path after SMB2 responses arrive. Tests use the conditional exports.

## Risks and edge cases

The binary search depends on table sort order; `smb2_init_maperror()` catches generation/order errors at module init. Missing mappings collapse distinct server statuses to `-EIO`, which is safe but can reduce user-visible accuracy. Logging must avoid noisy expected statuses such as `STATUS_MORE_PROCESSING_REQUIRED` and `STATUS_END_OF_FILE`. The function assumes `buf` points to at least an SMB2 header; callers must validate frame length before mapping.

## Test signals

`smb2maperror_test.c` validates lookup coverage for every generated table row. Additional useful tests are module init failure injection with unsorted generated data, spot checks for important statuses, and integration tests verifying session setup continuations and EOF do not produce excessive notice logs.
