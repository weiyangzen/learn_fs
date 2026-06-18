# sources/user-network-fs/samba/source4/torture/basic/cxd_known.h lines 1060-1914

## Scope

This chunk covers lines 1060-1914 of Samba's `source4/torture/basic/cxd_known.h`. The range is entirely inside the `static const struct createx_data cxd_known[]` initializer and contains 855 consecutive expected-result rows for `CXD_TEST_CREATEX_SHAREMODE` with `cxd_flags = 0`.

The chunk is data, not executable code. It records Windows XP SP2 reference behavior for SMB1 `NTCREATEX` file opens when two clients open the same file with selected access masks and share modes, then attempt follow-up file operations. The range starts after the `sharemode1=1, sharemode2=0` block has begun, covers all remaining `sharemode1=1` file rows, and continues into `sharemode1=2` rows through part of the `sharemode2=6` block. Directory rows and the later `cxd_flags = CXD_FLAGS_DIRECTORY` data are outside this chunk.

## Purpose

The table is an oracle for the `BASE-CREATEX_*` Samba torture tests. For each combination of first-open access mask, first-open share mode, second-open access mask, and second-open share mode, it stores the expected status results observed on Windows XP Pro 2002 SP2. The torture test uses these rows to decide whether Samba or another SMB server matches Windows-compatible `NTCREATEX` sharing and access behavior.

This chunk specifically exercises ordinary file opens (`cxd_flags = 0`) for `CXD_TEST_CREATEX_SHAREMODE`. Each row captures:

- `cxd_result`: statuses for the first handle's create/open and subsequent file operations.
- `cxd_result2`: statuses for the second handle's create/open and subsequent file operations.
- `cxd_access1` and `cxd_sharemode1`: access mask and share mode used by the first client.
- `cxd_access2` and `cxd_sharemode2`: access mask and share mode used by the second client.

The rows encode compatibility expectations around read, write, execute/read-for-execute, and all-access combinations under share access permutations. Failures are primarily `NT_STATUS_ACCESS_DENIED`; successful actions are `NT_STATUS_OK`.

## Important APIs, Types, And Data Shape

The relevant declarations are earlier in the same header:

- `enum cxd_test` classifies the test family. This chunk uses `CXD_TEST_CREATEX_SHAREMODE` (`2`) only.
- `enum cxd_flags` describes whether the target is a directory and whether it should be pre-created. This chunk uses only `0`, meaning a regular file target with no special setup flag.
- `enum cxd_results` indexes the result arrays. For files, index `0` is `CXD_CREATEX`, index `1` is `CXD_FILE_READ`, index `2` is `CXD_FILE_WRITE`, and index `3` is `CXD_FILE_EXECUTE`.
- `struct createx_data` is the record type. The input fields are `cxd_test`, `cxd_flags`, `cxd_access1`, `cxd_sharemode1`, `cxd_access2`, and `cxd_sharemode2`; the output fields are `cxd_result[CXD_MAX]` and `cxd_result2[CXD_MAX]`.
- `cxd_known[]` is a `static const` array included by `denytest.c`.

The access-mask values in this range are the access-group permutations used by `torture_createx_sharemodes()` rather than exhaustive single-bit rows:

- `0`
- `0x120089`
- `0x120116`
- `0x12019f`
- `0x1200a0`
- `0x1200a9`
- `0x1201b6`
- `0x1201bf`

The line range covers `cxd_sharemode1` values `1` and `2`. It covers `cxd_sharemode2` values `0` through `7`, but because this is a chunk boundary, it begins and ends in the middle of broader sharemode blocks. Within the assigned lines, `sharemode2` distribution is: `0` has 64 rows, `1` has 119 rows, `2` through `5` have 128 rows each, `6` has 96 rows, and `7` has 64 rows.

## Control Flow

The table rows are consumed by `source4/torture/basic/denytest.c`:

1. `torture_createx_sharemodes()` initializes a `struct createx_data`, selects file mode when `dir == false`, and sets `cxd_test` to `CXD_TEST_CREATEX_SHAREMODE` for non-extended runs.
2. It iterates all eight share-mode permutations for both handles and iterates grouped access-mask permutations for both handles.
3. For each combination, it calls `torture_createx_specific()`.
4. `torture_createx_specific()` fills `RAW_OPEN_NTCREATEX` open parameters for the first handle with `cxd_access1`/`cxd_sharemode1`.
5. For `CXD_TEST_CREATEX_SHAREMODE`, it also fills a second `RAW_OPEN_NTCREATEX` request for a second SMB client with `cxd_access2`/`cxd_sharemode2`.
6. It opens the first file handle, records `result[CXD_CREATEX]`, then runs `createx_test_file()` when the open succeeds.
7. `createx_test_file()` attempts `RAW_READ_READX`, `RAW_WRITE_WRITEX`, and read-for-execute on the handle, storing results at `CXD_FILE_READ`, `CXD_FILE_WRITE`, and `CXD_FILE_EXECUTE`.
8. It repeats the same create and follow-up operation sequence for the second handle, storing statuses in `cxd_result2`.
9. `cxd_find_known()` locates the matching `cxd_known[]` row by exact input fields. It first tries the next sequential row as an optimization, then falls back to a linear scan.
10. If a known row is found, `COMPARE_STATUS` checks each observed status against `cxd_result` and, for sharemode tests, `cxd_result2`.
11. If no row is found or comparison fails, the test prints a C initializer-style row that can be copied back into the known-results table after validating the behavior.

The table's row order matters for performance but not for correctness. `cxd_find_known()` caches the previous index and expects test generation order to usually match table order. If the sequence drifts, the full scan still finds matching rows, but the large table becomes more expensive to search.

## State And Persistence Behavior

The header itself has no mutable state and performs no persistence. It is compiled into the torture binary as a static constant data set.

Runtime state is owned by `denytest.c`:

- `torture_createx_specific()` creates and removes the test object named `\\createx_dir` using either file or directory helpers. This chunk covers file rows, so creation uses `createx_make_file()` only when requested by flags; these rows have no make-before-create flag.
- The first and second opens run through separate SMB client states (`cli` and `cli2`) so share-mode interactions are tested as multi-client behavior.
- Successful handles are closed after follow-up operations.
- Before the sharemode test starts, `torture_createx_sharemodes()` deletes any stale `\\createx_dir` file or tree.
- Optional exhaustive-data capture uses the `CREATEX_DATA` environment variable and `data_file_fd`, but `cxd_find_known()` explicitly does not use known rows for the exhaustive test variants. This chunk belongs to the ordinary non-extended known set.

The statuses in this chunk are persistent compatibility evidence: they are not regenerated at runtime unless a test failure or missing-row case prints replacement initializer text.

## Dependencies And Integration Points

Primary integration points:

- `denytest.c` includes this header directly and depends on the exact `struct createx_data` layout.
- SMB raw client APIs supply the observed behavior: `smb_raw_open()`, `smb_raw_read()`, `smb_raw_write()`, `smbcli_close()`, and cleanup helpers such as `smbcli_unlink()`.
- SMB protocol constants used by the consumer include `RAW_OPEN_NTCREATEX`, `NTCREATEX_DISP_OPEN_IF`, `FILE_ATTRIBUTE_NORMAL`, access masks, and `share_access`.
- NT status constants in this chunk are from Samba's NTSTATUS definitions, primarily `NT_STATUS_OK` and `NT_STATUS_ACCESS_DENIED`.
- Torture harness APIs provide diagnostics and control: `torture_comment()`, `torture_result()`, `torture_setting_bool()`, and status-comparison macros.

This data also indirectly defines expected behavior for Samba's server-side share-mode and access-check implementation. A server change in deny-mode conflict resolution, file read/write/execute access checks, generic access mapping, or SMB1 `NTCREATEX` semantics can surface as failures against these rows.

## Risks And Maintenance Notes

- The source of truth is old Windows XP SP2 behavior. That is intentional for this torture test, but modern Windows versions may differ in edge cases. Updating rows without a clear target-platform decision can change the compatibility contract.
- The table is large and manually represented as C initializers. Single-row mistakes are easy to introduce and hard to review visually because many adjacent rows differ only by one access mask, share mode, or status.
- The chunk boundary starts and ends mid-matrix. The final per-file synthesis must reconcile this report with adjacent chunks before making whole-table claims about all sharemode combinations.
- The repeated rows assume the generation order in `torture_createx_sharemodes()`. Reordering generation is safe functionally because of the fallback scan, but it weakens the cached-index optimization and can slow the torture run.
- `cxd_result` and `cxd_result2` have four logical slots for file tests. Some unrelated rows elsewhere in the header may stop early after a failed create, but rows in this chunk generally initialize the full four-status arrays for both handles.
- The table stores numeric access masks rather than symbolic names. Maintenance requires understanding the grouped access masks from `sec_access_bit_groups` in `denytest.c`; otherwise it is easy to misclassify what a row is testing.
- Because the expected statuses are used for a live SMB interoperability test, filesystem backend differences, privilege differences, SACL support settings, and access-mask mapping changes can all look like data regressions.

## Test Signals

Strong signals for this chunk come from running the `BASE-CREATEX_SHAREMODE` file torture path:

- The first open should return the `cxd_result[0]` status for every row in this range.
- When the first open succeeds, read, write, and execute/read-for-execute should match `cxd_result[1]`, `cxd_result[2]`, and `cxd_result[3]`.
- The second open and its follow-up operations should match `cxd_result2[0..3]`.
- Failures should print an initializer containing the exact `cxd_test`, `cxd_flags`, access masks, share modes, and observed status arrays, making drift easy to compare with this header.
- There should be no missing-row diagnostics for non-extended file sharemode combinations covered by lines 1060-1914.
- Since the chunk has 855 rows and 6,840 total stored status values, accidental truncation or empty output in generated research/checking lanes can be caught by verifying the row count and non-empty `cxd_result2` coverage.

Useful regression dimensions include first-handle share mode `1` and `2`, second-handle share modes `0` through `7`, zero access masks, full grouped masks such as `0x12019f` and `0x1201bf`, and combinations where one handle can create/open successfully while the peer's follow-up read/write/execute path returns `NT_STATUS_ACCESS_DENIED`.
