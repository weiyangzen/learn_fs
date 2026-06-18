# `sources/user-network-fs/samba/source4/torture/basic/cxd_known.h` Lines 6352-7290

## Purpose

This chunk is a data-only slice of Samba's `cxd_known[]` oracle table for the `BASE-CREATEX_*` torture tests. The table records known Windows XP Pro 2002 SP2 behavior for SMB `NTCREATEX` access and share-mode combinations, so the torture test can compare Samba/server behavior against an explicit reference result.

Lines 6352-7290 are entirely `struct createx_data` initializers. Every row in this chunk has:

- `.cxd_test = 2`, meaning `CXD_TEST_CREATEX_SHAREMODE`.
- `.cxd_flags = 0x1`, meaning `CXD_FLAGS_DIRECTORY`.
- A first `NTCREATEX` open described by `.cxd_access1` and `.cxd_sharemode1`.
- A second `NTCREATEX` open described by `.cxd_access2` and `.cxd_sharemode2`.
- Expected post-open operation statuses in `.cxd_result` for the first handle and `.cxd_result2` for the second handle.

The chunk is specifically about directory share-mode behavior. It covers the middle of the directory share-mode permutation matrix: share mode 3 continuing from the prior chunk, all of share mode 4 as the first open, and the beginning of share mode 5 as the first open.

## Important APIs, Types, And Constants

The relevant type is `struct createx_data`, declared near the top of the same header. Its input fields are `cxd_test`, `cxd_flags`, `cxd_access1`, `cxd_sharemode1`, `cxd_access2`, and `cxd_sharemode2`; its output fields are `cxd_result[CXD_MAX]` and `cxd_result2[CXD_MAX]`.

The result indexes are shared between file and directory tests:

- `CXD_CREATEX` is index 0 and stores the status of the open itself.
- For directories, index 1 is `CXD_DIR_ENUMERATE`.
- For directories, index 2 is `CXD_DIR_CREATE_CHILD`.
- For directories, index 3 is `CXD_DIR_TRAVERSE`.

All rows in this chunk use the directory flag, so the result arrays should be interpreted as open, enumerate, create-child, and traverse outcomes rather than file read/write/execute outcomes.

The access masks in this chunk are drawn from the normal share-mode access-group permutations used by `denytest.c`: `0`, `0x120089`, `0x120116`, `0x12019f`, `0x1200a0`, `0x1200a9`, `0x1201b6`, and `0x1201bf`. These are combinations of the grouped read, write, and execute file rights used by `sec_access_bit_groups[]`, represented in their expanded SMB access-mask form.

Share modes are numeric `NTCREATEX_SHARE_ACCESS_*` bitmasks. In this range, `.cxd_sharemode1` appears as 3, 4, and 5, while `.cxd_sharemode2` spans 0 through 7, with the chunk boundaries cutting through the 3:3 and 5:2 submatrices.

## Table Coverage In This Chunk

This chunk contains 939 initializer rows. Each row has both `cxd_result` and `cxd_result2`, because share-mode tests perform two opens and compare both handles' observed behavior.

The share-mode pair coverage is:

- `sharemode1=3, sharemode2=3`: 14 trailing rows from the previous permutation block.
- `sharemode1=3, sharemode2=4..7`: four complete 64-row access-pair blocks.
- `sharemode1=4, sharemode2=0..7`: eight complete 64-row access-pair blocks.
- `sharemode1=5, sharemode2=0..1`: two complete 64-row access-pair blocks.
- `sharemode1=5, sharemode2=2`: 29 leading rows, continuing in the next chunk.

Every expected status in this chunk is `NT_STATUS_OK`. There are no `NT_STATUS_ACCESS_DENIED`, sharing violations, object-name errors, or invalid-parameter outcomes in this range. That makes the chunk an all-success part of the known-good directory share-mode matrix: both opens should succeed, and both handles should be able to enumerate, create a child entry, and traverse to a known child file.

## Control Flow

The header itself has no executable control flow beyond static C initializer evaluation. The behavior is driven by `source4/torture/basic/denytest.c`.

The relevant flow in the consumer is:

1. `torture_createx_sharemodes_dir()` calls `torture_createx_sharemodes(..., dir=true, extended=false)`.
2. `torture_createx_sharemodes()` loops over `cxd_sharemode1` and `cxd_sharemode2` from 0 to 7, then over grouped access-mask permutations for `cxd_access1` and `cxd_access2`.
3. For each generated `struct createx_data`, `torture_createx_specific()` chooses directory helpers because `CXD_FLAGS_DIRECTORY` is set.
4. `createx_fill_dir()` fills an `RAW_OPEN_NTCREATEX` request with `FILE_ATTRIBUTE_DIRECTORY`, `NTCREATEX_OPTIONS_DIRECTORY`, `NTCREATEX_DISP_OPEN_IF`, the current access mask, and the current share access mask.
5. The first client opens `\createx_dir`; if that succeeds, `createx_test_dir()` records whether the handle can enumerate, create a child, and traverse to a known child.
6. For `CXD_TEST_CREATEX_SHAREMODE`, the second client performs the second open with `.cxd_access2` and `.cxd_sharemode2`, then runs the same directory operation checks on the second handle.
7. `cxd_find_known()` locates the matching row by comparing all six input fields, then the test compares the observed result arrays against `cxd_known[res].cxd_result` and `cxd_known[res].cxd_result2`.

Because every row in this chunk expects all OK statuses, any non-OK open or directory operation for these combinations is treated as a compatibility regression against the captured Windows behavior.

## State And Persistence Behavior

This chunk defines static, read-only test data at compile time. It does not allocate memory dynamically, mutate state, perform IO, or persist results.

The stateful behavior is in the consumer:

- `cxd_find_known()` keeps a static index cache and first tries the next table entry, relying on the generated test order matching the order of `cxd_known[]`.
- `torture_createx_specific()` creates and removes the test directory path `\createx_dir` for each case.
- `createx_test_dir()` creates temporary entries named `known` and `child` beneath the test directory, then unlinks them before returning.
- If the `CREATEX_DATA` environment variable is set in exhaustive access mode, generated `struct createx_data` records can be written to a data file, but this chunk itself is not written at runtime.

The row order is therefore part of the performance contract. Reordering rows would not change correctness because `cxd_find_known()` falls back to a full scan, but it would hurt the optimized path and progress through this very large table.

## Dependencies

The data depends on Samba's NT status constants, SMB raw open types, and security/access-mask definitions being available through the including compilation unit. The header is included by `source4/torture/basic/denytest.c`, which supplies the actual SMB client calls and helper macros.

Important direct dependencies in the consumer include:

- `smb_raw_open()` for both `NTCREATEX` opens.
- `smbcli_mkdir()`, `smbcli_rmdir()`, `smbcli_unlink()`, and `smbcli_close()` for setup and cleanup.
- `smb_raw_read()` and `smb_raw_write()` for file cases outside this chunk.
- `CHECK_STATUS`, `COMPARE_STATUS`, `NT_STATUS_IS_OK`, and `nt_errstr()` for assertion and diagnostic behavior.
- `torture_setting_bool()` and `torture_comment()` for SACL filtering, progress, and mismatch output.

The correctness of this chunk also depends on the historical Windows XP SP2 capture described in the header comment. The table is not derived dynamically from protocol documentation during test execution.

## Integration Points

The main integration point is the `BASE-CREATEX_SHAREMODE` directory test path in `denytest.c`. This table lets the test run a deterministic matrix and suppress output for cases that match the known oracle. If a row is missing or mismatched, the consumer prints a C initializer-style line so maintainers can update or investigate the known-results table.

The chunk also participates in the larger oversized-file chunking workflow for research. It is not a standalone source module: it begins and ends inside a larger static array, so the final merged per-file research document must combine it with neighboring chunk reports to describe the whole `cxd_known.h` table.

## Risks And Edge Cases

The biggest local risk is table drift. These rows encode one historical Windows version's behavior, and directory share-mode behavior can vary across Windows releases, SMB dialects, server configuration, filesystem semantics, or Samba changes intended to match newer behavior.

The all-OK status pattern is useful but also brittle. A single incorrect row that should deny or fail would silently weaken the test's ability to catch an over-permissive implementation. Conversely, if a server correctly differs from Windows XP SP2, this table will still report that as a failure.

The numeric access masks and share modes are dense and not self-documenting in the rows. Mistyping one hex access mask, share-mode number, or result array could move a case to the wrong matrix cell. Since `cxd_find_known()` matches all input fields, such a typo can make a generated test case appear unknown or make an adjacent case compare against the wrong expectations.

The chunk boundaries are mid-matrix. Lines 6352-6365 finish part of an existing `sharemode1=3/sharemode2=3` block, and lines 7262-7290 start but do not finish `sharemode1=5/sharemode2=2`. Any manual analysis or merge process must avoid treating this chunk as a complete logical permutation set by itself.

Cleanup assumptions are another risk in the consumer. `createx_test_dir()` closes and unlinks paths after operations, but unusual failures can leave temporary children behind, which may affect later rows unless the outer blank-slate cleanup succeeds.

## Test Signals

Strong test signals for this chunk are generated by the existing torture path:

- Running the directory share-mode test should generate matching `struct createx_data` inputs for every row in this chunk.
- For all 939 rows, both first and second `NTCREATEX` opens should return `NT_STATUS_OK`.
- For every successful handle in this chunk, directory enumerate, create-child, and traverse checks should all return `NT_STATUS_OK`.
- The mismatch printer in `torture_createx_specific()` should stay quiet for these rows; printed initializer lines indicate either a missing row or a behavioral mismatch.

Useful static checks include verifying that every row in lines 6352-7290 has `.cxd_test = 2`, `.cxd_flags = 0x1`, both result arrays present, and only `NT_STATUS_OK` statuses. A shape check should also verify that the range contains 939 rows and preserves the access-mask/share-mode ordering expected by `cxd_find_known()`'s next-entry optimization.
