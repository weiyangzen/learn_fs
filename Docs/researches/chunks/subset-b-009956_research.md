# sources/user-network-fs/samba/source4/torture/basic/cxd_known.h lines 1915-2769

## Scope

This chunk covers lines 1915-2769 of `sources/user-network-fs/samba/source4/torture/basic/cxd_known.h`, a contiguous slice of the static `cxd_known[]` initializer used by Samba torture tests for SMB `NTCreateX` access and share-mode behavior. The file begins by defining `enum cxd_test`, `enum cxd_flags`, `struct createx_data`, and `static const struct createx_data cxd_known[]`; this chunk is entirely inside the `CXD_TEST_CREATEX_SHAREMODE` portion of that array.

The rows in this window are all `cxd_test = 2` (`CXD_TEST_CREATEX_SHAREMODE`) and `cxd_flags = 0`, so they describe file, not directory, create/open behavior without the `CXD_FLAGS_MAKE_BEFORE_CREATEX` setup bit. Each line is one expected result record for two sequential opens against the same path, using two requested access masks and two share-mode masks.

## Purpose

The purpose of this chunk is to preserve known-good Windows XP SP2 behavior for specific file share-mode combinations. Samba's `source4/torture/basic/denytest.c` includes this header and uses `cxd_known[]` as an oracle: the live SMB server under test is asked to perform the same create/open operation, and the resulting `NTSTATUS` values are compared to the stored status vectors.

This chunk contributes the middle of the exhaustive base share-mode matrix. It covers 855 initializer rows:

- Lines 1915-1946: final 32 rows for `cxd_sharemode1 = 2`, `cxd_sharemode2 = 6`.
- Lines 1947-2010: full 64-row block for `cxd_sharemode1 = 2`, `cxd_sharemode2 = 7`.
- Lines 2011-2522: all eight 64-row blocks for `cxd_sharemode1 = 3`, `cxd_sharemode2 = 0..7`.
- Lines 2523-2714: full 64-row blocks for `cxd_sharemode1 = 4`, `cxd_sharemode2 = 0..2`.
- Lines 2715-2769: first 55 rows of the `cxd_sharemode1 = 4`, `cxd_sharemode2 = 3` block.

Within each complete 64-row block, the table iterates eight representative first-open access masks by eight representative second-open access masks. The visible masks are `0`, `0x120089`, `0x120116`, `0x12019f`, `0x1200a0`, `0x1200a9`, `0x1201b6`, and `0x1201bf`. These are grouped access combinations generated from `denytest.c`'s `sec_access_bit_groups[]`, not named constants in this header.

## Data Contract

Each row initializes a `struct createx_data` with these fields:

- `cxd_test`: selects the test family. In this chunk it is always `2`, matching `CXD_TEST_CREATEX_SHAREMODE`.
- `cxd_flags`: controls target type and setup. In this chunk it is always `0`, so the harness treats the target as a file and does not pre-create it via `CXD_FLAGS_MAKE_BEFORE_CREATEX`.
- `cxd_access1` and `cxd_sharemode1`: desired access and share mode for the first client open.
- `cxd_access2` and `cxd_sharemode2`: desired access and share mode for the second client open.
- `cxd_result[CXD_MAX]`: expected status vector for the first open and follow-up operations.
- `cxd_result2[CXD_MAX]`: expected status vector for the second open and follow-up operations.

`CXD_MAX` is four. Index `0` is `CXD_CREATEX`, the create/open result. Indexes `1`, `2`, and `3` are interpreted by the harness as post-open capability probes: file read, file write, and file execute for file targets. Directory aliases exist in the enum, but `cxd_flags = 0` means this chunk uses the file interpretation.

Most rows include four statuses for both result arrays. If a create/open fails, the harness stops comparing further operation statuses for that result vector after index `0`, but these rows generally record full vectors with `NT_STATUS_OK` and `NT_STATUS_ACCESS_DENIED` values because the expected first opens in this region are normally successful while individual follow-up operations may be denied by the granted access mask.

## Important APIs, Types, And Functions

This chunk itself contains no functions or macros; it is a static data table. Its important exported-by-inclusion artifacts are inherited from the header:

- `enum cxd_test`: names the test families, including `CXD_TEST_CREATEX_SHAREMODE`.
- `enum cxd_flags`: names the file-vs-directory and pre-create control bits.
- `struct createx_data`: the row schema consumed by the torture harness.
- `static const struct createx_data cxd_known[]`: the known-answer table containing this chunk.

The main consumer is `source4/torture/basic/denytest.c`:

- `CXD_MATCHES()` compares the six input fields of a generated `struct createx_data` against one `cxd_known[]` row.
- `cxd_find_known()` searches the table, using a static index shortcut to optimize the common sequential table order and falling back to a full linear scan.
- `torture_createx_specific()` performs the actual SMB opens and post-open checks, then compares live `cxd_result` and `cxd_result2` arrays with the matched known row.
- `torture_createx_sharemodes()` generates the share-mode matrix that corresponds to rows like this chunk.

## Control Flow And Runtime Use

At runtime, `torture_createx_sharemodes()` initializes a `struct createx_data`, sets `cxd_test` to `CXD_TEST_CREATEX_SHAREMODE`, and loops over all share-mode permutations for both clients. For each share-mode pair, it loops over grouped access masks for the first and second opens. The order of those loops matches the row ordering in `cxd_known[]`, which is why `cxd_find_known()` can check the next table index first.

For each generated row, `torture_createx_specific()` chooses file helper functions because `cxd_flags` has no directory bit in this chunk. It fills `open_parms1` from `cxd_access1/cxd_sharemode1` and `open_parms2` from `cxd_access2/cxd_sharemode2`, opens the first handle on `cli->tree`, optionally runs file read/write/execute probes against that handle, and then opens the second handle on `cli2->tree` and runs the same probes. The resulting status arrays are compared field-by-field to this table.

This chunk's rows are therefore not executed directly. They drive control flow by matching the generated `(test, flags, access1, sharemode1, access2, sharemode2)` tuple and providing the expected status arrays.

## State And Persistence Behavior

The table is compile-time static const data. It has no mutable state, I/O, allocation, or persistence of its own. Persistence enters through the broader test harness:

- The known values were captured from Windows XP Pro 2002 SP2, according to the header comment.
- `denytest.c` can write generated `struct createx_data` records to a `CREATEX_DATA` file when its data capture path is enabled.
- `cxd_find_known()` keeps a static integer cache of the last table position to speed sequential lookup. This means table order is a performance signal, even though the fallback scan preserves correctness if order changes.

Because the header is included into `denytest.c`, the `static const` table has translation-unit-local linkage. There is no cross-object ABI, but any edit changes the compiled torture binary's expected behavior.

## Dependencies And Integration Points

This chunk depends on Samba's NT status definitions for `NT_STATUS_OK` and `NT_STATUS_ACCESS_DENIED`, and on the surrounding header definitions for `CXD_MAX` and `struct createx_data`. It integrates with the SMB client torture stack in `denytest.c`, including:

- `smb_raw_open()` for `NTCreateX` opens.
- `smbcli_close()`, `smbcli_unlink()`, and `smbcli_deltree()` for cleanup around test paths.
- File capability probe helpers such as `createx_test_file()`.
- Torture framework result reporting through `COMPARE_STATUS()`, `torture_result()`, `torture_comment()`, and progress reporting.
- The `sacl_support` torture setting, though this chunk's visible access masks do not appear to include `SEC_FLAG_SYSTEM_SECURITY`.

The main integration contract is exact tuple matching. If a generated tuple has no matching row, the harness prints a C initializer for the observed result. If a row matches but statuses differ, the harness reports a comparison failure and also prints the observed initializer.

## Risks And Maintenance Notes

The largest risk is accidental table corruption. A single status change can silently redefine expected Windows-compatible behavior for one access/share-mode combination. Because rows are dense and visually similar, manual edits are high risk unless generated from trusted captures or reviewed with tooling.

The chunk starts and ends inside complete 64-row share-mode blocks, so chunk-level readers must not infer full block coverage from this document alone. In particular, `sharemode1=2/sharemode2=6` is already in progress at line 1915, and `sharemode1=4/sharemode2=3` continues past line 2769.

The row ordering is coupled to `denytest.c`'s generation order and `cxd_find_known()`'s sequential-index optimization. Reordering rows should not break semantic lookup because of the full scan fallback, but it can hurt test performance and make generated diff review harder.

The expected results are based on Windows XP SP2. Modern Windows SMB behavior may differ, but these rows intentionally encode the historical baseline expected by this Samba torture test. Treat updates as test-oracle changes, not mechanical formatting changes.

Formatting is also part of maintenance ergonomics: `denytest.c` prints missing or failing rows in a similar initializer shape. Keeping the same shape helps developers paste newly observed rows back into the table.

## Test Signals

The direct test signal is the `BASE-CREATEX_*` torture coverage that includes `torture_createx_sharemodes()`. For rows in this chunk, useful signals include:

- All generated tuples in the covered share-mode/access ranges are found by `cxd_find_known()`.
- `COMPARE_STATUS()` sees exact matches for `cxd_result` and, because this is share-mode testing, `cxd_result2`.
- No unexpected initializer rows are printed by the "not in cxd_known list or failed" path.
- Progress output advances through the known matrix without falling back to unknown-row reporting.

Chunk-specific regression signs include failures only around `sharemode1` values `2`, `3`, or `4` with `sharemode2` values `0..7`, especially where both opens return `NT_STATUS_OK` but read/write/execute probe statuses differ.

## Open Questions For Merge Lane

The final per-file merge should combine this with adjacent chunks to describe the full `cxd_known[]` table, including the earlier `CXD_TEST_CREATEX_ACCESS` rows, later directory-flag rows, and complete chunk boundaries for the share-mode matrix. This chunk alone cannot state the total number of rows in the header without relying on surrounding context, but it does confirm this slice is a dense mid-table portion of the `CXD_TEST_CREATEX_SHAREMODE` file-target matrix.
