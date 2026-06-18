# sources/user-network-fs/samba/source4/torture/basic/cxd_known.h lines 4480-5412

## Scope

This chunk covers lines 4480-5412 of Samba's `source4/torture/basic/cxd_known.h`. The file is a static expected-results table for the `BASE-CREATEX_*` torture tests, not executable code. This range is a middle slice of `static const struct createx_data cxd_known[]`, specifically `CXD_TEST_CREATEX_SHAREMODE` rows.

The range starts near the end of the file-object sharemode matrix for `cxd_flags = 0` and then transitions at line 4574 into directory-object sharemode rows for `cxd_flags = CXD_FLAGS_DIRECTORY` (`0x1`). It contains 930 table entries: 91 file rows and 839 directory rows. Every row in this range uses `cxd_test = 2`, which maps to `CXD_TEST_CREATEX_SHAREMODE`.

## Purpose

The purpose of these rows is to preserve known Windows behavior for paired `NTCREATEX` opens with different access masks and SMB share modes. The table was recorded from Windows XP Professional 2002 Service Pack 2, according to the header comment earlier in the file, and is used as a regression oracle by `source4/torture/basic/denytest.c`.

Each row describes:

- the first open's object type, access mask, and share mode;
- the second open's access mask and share mode;
- the expected result of the first open plus follow-up operations on the first handle;
- the expected result of the second open plus follow-up operations on the second handle.

The chunk is valuable because SMB sharemode and access compatibility rules are subtle. These entries encode cases where the initial open succeeds but later read/write/execute or directory-enumerate/create-child/traverse probes are allowed or denied differently depending on access rights and whether the target is a file or directory.

## Important APIs, Types, And Data

The table shape is defined at the top of `cxd_known.h`:

- `enum cxd_test` names `CXD_TEST_CREATEX_SHAREMODE` as value `2`.
- `enum cxd_flags` uses `CXD_FLAGS_DIRECTORY` (`0x1`) to select directory behavior; no `CXD_FLAGS_MAKE_BEFORE_CREATEX` rows appear in this chunk.
- `struct createx_data` carries `cxd_access1`, `cxd_sharemode1`, `cxd_access2`, `cxd_sharemode2`, and two result arrays.
- `CXD_MAX` is four result slots. For file rows the slots mean `CXD_CREATEX`, `CXD_FILE_READ`, `CXD_FILE_WRITE`, and `CXD_FILE_EXECUTE`. For directory rows the same indexes are interpreted as `CXD_CREATEX`, `CXD_DIR_ENUMERATE`, `CXD_DIR_CREATE_CHILD`, and `CXD_DIR_TRAVERSE`.

The access-mask values in this range are the same eight grouped masks repeated through the sharemode matrix:

- `0`
- `0x120089`
- `0x120116`
- `0x12019f`
- `0x1200a0`
- `0x1200a9`
- `0x1201b6`
- `0x1201bf`

The sharemode coverage in this exact range is partial because the file is split into chunks. Lines 4480-4573 finish `cxd_flags = 0` file rows for first share mode `7`, second share modes `6` and `7`. Lines 4574-5412 begin `cxd_flags = 0x1` directory rows, covering complete 64-row access grids for `sharemode1 = 0` with `sharemode2 = 0..7`, complete grids for `sharemode1 = 1` with `sharemode2 = 0..4`, and the first seven rows of `sharemode1 = 1`, `sharemode2 = 5`.

## Control Flow

This header contributes data to the control flow in `denytest.c`:

1. `torture_createx_sharemodes_file()` and `torture_createx_sharemodes_dir()` call `torture_createx_sharemodes()` with `dir` false or true.
2. `torture_createx_sharemodes()` iterates all sharemode pairs, then iterates grouped access-mask permutations for both opens. For non-extended sharemode tests, those grouped masks are the rows represented here.
3. `torture_createx_specific()` builds the first `RAW_OPEN_NTCREATEX` request from `cxd_access1` and `cxd_sharemode1`. Because `cxd_test` is `CXD_TEST_CREATEX_SHAREMODE`, it also builds a second open for `cli2` from `cxd_access2` and `cxd_sharemode2`.
4. If the target is a file, `createx_fill_file()` and `createx_test_file()` are used. If the target is a directory, `createx_fill_dir()` and `createx_test_dir()` are used.
5. The actual statuses collected into `cxd_result` and `cxd_result2` are matched back to `cxd_known[]` via `cxd_find_known()`, which compares the test id, flags, access masks, and share modes.
6. Matching rows are checked with `COMPARE_STATUS`; unknown or failed cases are printed as C initializers so the table can be regenerated or extended.

The rows themselves have no branches, but their ordering matters for performance: `cxd_find_known()` keeps a static last index and first tries the next row before falling back to a full table scan. This works because the generator in `torture_createx_sharemodes()` walks the matrix in the same order as `cxd_known[]`.

## State And Persistence Behavior

This chunk defines immutable process-local state. `cxd_known[]` is `static const`, so it is compiled into the torture binary and is not modified at runtime.

Runtime state comes from the test harness:

- `torture_createx_specific()` mutates a stack `struct createx_data` with observed `NTSTATUS` values before lookup.
- If `CREATEX_DATA` is set for exhaustive data collection, `denytest.c` writes binary `struct createx_data` records to the configured file instead of comparing against this table. These rows are bypassed only for the data-capture path or for extended tests not represented in `cxd_known[]`.
- The test object named `\createx_dir` is repeatedly deleted with `smbcli_deltree()` or `smbcli_unlink()`, opened, probed, closed, and removed. Directory probe helpers create and remove `KNOWN` and `CHILD` entries under the opened directory.

No Samba server configuration or persistent database is directly changed by this header. Persistence risk is limited to the optional `CREATEX_DATA` capture path in the consumer and the temporary files/directories created on the target SMB share during torture execution.

## Dependencies And Integration Points

This header depends on symbols supplied by the including C file and Samba headers:

- `NTSTATUS` and constants such as `NT_STATUS_OK`, `NT_STATUS_ACCESS_DENIED`, and `NT_STATUS_UNSUCCESSFUL`.
- SMB access-mask constants used by the generator in `denytest.c`, including the grouped masks represented by `sec_access_bit_groups`.
- `RAW_OPEN_NTCREATEX`, `NTCREATEX_DISP_OPEN_IF`, `NTCREATEX_OPTIONS_DIRECTORY`, `FILE_ATTRIBUTE_NORMAL`, and `FILE_ATTRIBUTE_DIRECTORY` through the consumer's open setup.
- The `smb_raw_open`, `smb_raw_read`, `smb_raw_write`, `smbcli_close`, `smbcli_unlink`, and `smbcli_rmdir` client APIs used to produce and verify the result arrays.
- The two-client sharemode test setup: the first open uses `cli`, the second open uses `cli2`, allowing the torture test to detect server behavior with concurrent handles.

The integration point is narrow: `denytest.c` includes this header and treats `cxd_known[]` as the expected-results database for `BASE-CREATEX_ACCESS` and `BASE-CREATEX_SHAREMODE`. This chunk is specifically for the sharemode side of that database.

## Risks And Maintenance Notes

- The table is hand/generated oracle data. A single altered initializer can change test expectations without any compiler warning because the row still type-checks.
- Row order is semantically tied to the generator loop order and the `cxd_find_known()` sequential-search optimization. Reordering rows is likely to preserve correctness after fallback search, but can hurt test runtime and may hide assumptions in future tooling.
- The file and directory result slots share numeric indexes but have different meanings after `CXD_CREATEX`. Misreading a directory row as file read/write/execute data, or the reverse, gives the wrong behavioral interpretation.
- This chunk crosses a major object-type boundary at line 4574. Merge tooling should preserve that transition when assembling the final per-file report.
- Most directory rows in this range are all-OK rows: 845 of 930 rows contain no `NT_STATUS_ACCESS_DENIED`. That is expected for the directory matrix shown here, but it also means accidental broad replacement of statuses could look superficially plausible.
- The file rows at the start still contain many denied follow-up statuses even when `CXD_CREATEX` succeeds. Tests must compare all populated result slots, not only initial open success.
- The known results are from Windows XP SP2. Some behavior may differ on newer Windows versions, but changing this table changes the Samba compatibility target for these torture tests.
- Access masks are stored as raw hex constants. Maintenance needs cross-reference with Windows/Samba file and directory access bits to understand why a particular result changes.

## Test Signals

Useful validation for this chunk is mostly through the existing torture tests:

- Run `BASE-CREATEX_SHAREMODE` file coverage and confirm the rows around `cxd_flags = 0`, `sharemode1 = 7`, `sharemode2 = 6..7` compare cleanly.
- Run `BASE-CREATEX_SHAREMODE` directory coverage and confirm rows beginning at `cxd_flags = 0x1`, especially the transition from file to directory at line 4574.
- Exercise a server implementation that intentionally denies one of read/write/execute or directory child/traverse operations to confirm `COMPARE_STATUS` reports the exact row and result slot.
- Run with progress enabled and verify that known rows do not print regenerated initializer lines; unexpected printed lines indicate a lookup miss or status mismatch.
- Run with `CREATEX_DATA` set only when regenerating data; in normal comparison mode it should be unset so `cxd_known[]` remains the oracle.
- Include both file and directory variants because identical `cxd_result` indexes have different operation meanings after the initial create.
