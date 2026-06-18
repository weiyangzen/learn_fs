# sources/user-network-fs/samba/source4/torture/basic/cxd_known.h lines 8230-8670

## Scope

This chunk is the final slice of Samba's `source4/torture/basic/cxd_known.h` known-results table for the `BASE-CREATEX_*` torture tests. It contains 440 `struct createx_data` initializer rows plus the closing `};` for `static const struct createx_data cxd_known[]`.

All rows in this range are for:

- `cxd_test = 2`, which is `CXD_TEST_CREATEX_SHAREMODE`.
- `cxd_flags = 0x1`, which is `CXD_FLAGS_DIRECTORY`.
- `cxd_sharemode1 = 7`, the first create/open request sharing read, write, and delete.

The visible matrix completes the directory share-mode baseline for second-open share modes `1` through `7`. The first row starts after the `sharemode2 = 1` block has already begun, so `sharemode2 = 1` has 56 rows in this chunk; each later `sharemode2` value has the full 64-row access matrix.

## Purpose

`cxd_known.h` is a static oracle of Windows XP Pro SP2 behavior for Samba's `NTCREATEX` access and share-mode torture tests. This chunk records that, for directories whose first handle was opened with full sharing (`sharemode1 = 7`), every listed combination of grouped directory access masks and second-handle share modes succeeds.

Each row supplies expected status arrays for two opens:

- `cxd_result`: the first open and follow-up operations through that first handle.
- `cxd_result2`: the second open and follow-up operations through that second handle.

In this chunk, both arrays are always `{ NT_STATUS_OK, NT_STATUS_OK, NT_STATUS_OK, NT_STATUS_OK }`. For directory tests those four status slots are `CXD_CREATEX`, `CXD_DIR_ENUMERATE`, `CXD_DIR_CREATE_CHILD`, and `CXD_DIR_TRAVERSE` because the enum aliases directory operations onto the file operation slots.

## Important APIs, Types, And Data

The table rows use `struct createx_data`, defined near the top of `cxd_known.h`:

- `enum cxd_test cxd_test`: selects access, exhaustive access, share-mode, or extended share-mode test families.
- `enum cxd_flags cxd_flags`: marks directory testing and whether the object is created before the `NTCREATEX` call.
- `uint32_t cxd_access1` / `cxd_sharemode1`: access mask and share mode for the first open.
- `uint32_t cxd_access2` / `cxd_sharemode2`: access mask and share mode for the second open.
- `NTSTATUS cxd_result[CXD_MAX]`: first-handle expected statuses.
- `NTSTATUS cxd_result2[CXD_MAX]`: second-handle expected statuses, meaningful for `CXD_TEST_CREATEX_SHAREMODE`.

The access values in this chunk are the eight grouped access combinations generated from `sec_access_bit_groups[]` in `denytest.c`: `0`, `0x120089`, `0x120116`, `0x12019f`, `0x1200a0`, `0x1200a9`, `0x1201b6`, and `0x1201bf`. These are combinations of Samba's file read, write, and execute right groups, reused for directories as enumerate/create-child/traverse checks.

The share mode values are the normal 3-bit `NTCREATEX_SHARE_ACCESS_*` permutations. `7` means all share bits are allowed. Because the first open allows all share modes here, none of the second opens are expected to be denied by share conflict, even when the second open advertises narrower sharing.

## Control Flow

There is no executable control flow in this header chunk. Runtime behavior comes from `source4/torture/basic/denytest.c`, which includes `cxd_known.h` and consumes the rows through the `cxd_find_known()` lookup.

The relevant flow is:

1. `torture_createx_sharemodes_dir()` calls `torture_createx_sharemodes(..., dir=true, extended=false)`.
2. The share-mode test builds `struct createx_data cxd` with `cxd_test = CXD_TEST_CREATEX_SHAREMODE` and `cxd_flags = CXD_FLAGS_DIRECTORY`.
3. Nested loops enumerate `cxd_sharemode1`, `cxd_sharemode2`, and the grouped access-mask permutations for both opens.
4. `torture_createx_specific()` fills two `RAW_OPEN_NTCREATEX` requests with `createx_fill_dir()`.
5. It opens the directory with the first access/share tuple, runs `createx_test_dir()` to check enumerate/create-child/traverse behavior, then repeats for the second tuple on `cli2`.
6. If no capture data file is active, `cxd_find_known()` searches `cxd_known[]` for an exact key match and `COMPARE_STATUS` validates observed statuses against `cxd_result` and `cxd_result2`.

The rows in this chunk correspond to the end of that loop space: first share mode `7`, directory flag set, and the final second-share-mode/access combinations.

## State And Persistence Behavior

This header persists expected statuses as source-controlled test data. It does not allocate, mutate, or store runtime state by itself.

During execution, `denytest.c` creates or opens a test path named `\\createx_dir`, performs directory child/traverse probes, closes handles, and removes the path with `smbcli_rmdir()` or related cleanup calls. If `data_file_fd` is set, `torture_createx_specific()` writes the observed `struct createx_data` records to that file instead of comparing against `cxd_known[]`; otherwise this table is read-only oracle data.

This chunk has no failure or denied-open states. The state implication is that Samba should preserve directory usability for both handles across every listed access pair when the first handle granted full sharing.

## Dependencies And Integration Points

Primary dependencies and integration points are:

- `source4/torture/basic/denytest.c`: includes this header, generates the matching `createx_data` keys, performs SMB operations, and compares results.
- SMB raw client APIs: `smb_raw_open`, `smb_raw_read`/directory tests, `smbcli_close`, `smbcli_mkdir`, `smbcli_rmdir`, and `smbcli_unlink` are used by the consumer to produce statuses matching the table.
- NT status constants: all expected values here are `NT_STATUS_OK`.
- Security and share constants: access masks are built from `SEC_RIGHTS_FILE_READ`, `SEC_RIGHTS_FILE_WRITE`, and `SEC_RIGHTS_FILE_EXECUTE`; share modes correspond to the `NTCREATEX_SHARE_ACCESS_*` bit set.
- Torture harness settings: `sacl_support` can skip SACL-related cases in the broader test, and `progress` controls progress output, but this chunk's access masks are not SACL-only single-bit cases.
- Windows compatibility baseline: the table comment states these known results were captured from Windows XP Pro 2002 SP2.

## Risks And Maintenance Notes

- The table is large and positional. `cxd_find_known()` optimizes for sequential lookup by trying the next array entry first, so row ordering affects performance even though exact matching protects correctness.
- Chunk boundaries split the logical matrix. This chunk starts mid-`sharemode2 = 1` block and ends by closing the entire table; it should not be analyzed as a complete standalone matrix for all first-share-mode values.
- The all-OK pattern is easy to overgeneralize. It applies to directory share-mode tests where the first open has `sharemode1 = 7`; other chunks contain denied statuses for narrower first-share settings or other access/flag cases.
- The baseline is old Windows behavior. Changes to Samba's SMB1 `NTCREATEX` sharing semantics, directory access checks, or status mapping may intentionally diverge from XP, but this table will still flag that divergence.
- Access masks such as `0x12019f` are opaque literals in the table. The generator in `denytest.c` explains them as grouped rights; manual edits risk introducing masks that the test loops never generate.
- Because both `cxd_result` and `cxd_result2` are compared operation-by-operation, a regression can be more specific than open denial. Directory enumeration, child creation, or traversal status changes can fail even when both opens succeed.

## Test Signals

Useful validation signals for this chunk are:

- Running the directory share-mode torture path should reach these rows when `cxd_sharemode1 = 7` and `cxd_flags = CXD_FLAGS_DIRECTORY`.
- For every row in lines 8230-8669, both first and second `NTCREATEX` calls should return `NT_STATUS_OK`.
- `createx_test_dir()` should also return `NT_STATUS_OK` for directory enumerate, create-child, and traverse checks through both handles.
- A mismatch should print a row-shaped initializer from `torture_createx_specific()`, making it directly comparable with the table entry.
- Regenerating known data against the intended Windows-compatible baseline should keep this chunk as an all-OK matrix for `sharemode1 = 7`.
- The header should continue to compile as a complete initializer, with line 8670 closing `cxd_known[]`.
