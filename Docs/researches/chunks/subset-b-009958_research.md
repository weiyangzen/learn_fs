# sources/user-network-fs/samba/source4/torture/basic/cxd_known.h lines 3625-4479

## Scope

This chunk is an interior slice of the static `cxd_known[]` table used by Samba's `BASE-CREATEX_*` torture tests. The assigned range begins in the middle of the non-directory `CXD_TEST_CREATEX_SHAREMODE` matrix at `cxd_sharemode1=6`, `cxd_sharemode2=1`, and ends in the same matrix at `cxd_sharemode1=7`, `cxd_sharemode2=6`. It does not include the table's type definitions or section header, so the surrounding file context is required to interpret the row fields.

All 855 rows in this range are `struct createx_data` initializers with:

- `cxd_test = 2`, meaning `CXD_TEST_CREATEX_SHAREMODE`;
- `cxd_flags = 0`, meaning ordinary file tests, not directory tests and not pre-created object tests;
- both `cxd_result` and `cxd_result2` populated with four `NTSTATUS` slots.

## Purpose

`cxd_known.h` is a checked-in reference corpus for `NTCreateX` access and share-mode behavior. The file comments say the known results were taken from Windows XP Pro 2002 SP2, and the Samba torture suite compares live server behavior against these expected status arrays.

This chunk specifically covers two-handle file share-mode combinations. Each row describes:

- the access mask and share mode used for the first create/open request;
- the access mask and share mode used for the second create/open request from a second SMB client;
- the expected result of the first open plus follow-up file operations on that first handle;
- the expected result of the second open plus follow-up file operations on that second handle.

The data encodes Windows-compatible semantics for whether two opens can coexist and what read, write, and execute-style reads are then allowed on each handle.

## Data Shape And Important Types

The relevant surrounding definitions are:

- `enum cxd_test`: assigns `CXD_TEST_CREATEX_SHAREMODE` the value `2`.
- `enum cxd_flags`: bit `CXD_FLAGS_DIRECTORY` switches between file and directory behavior; this chunk always leaves it clear.
- `enum` result indexes: `CXD_CREATEX`, `CXD_FILE_READ`, `CXD_FILE_WRITE`, and `CXD_FILE_EXECUTE` are the four slots used for file rows.
- `struct createx_data`: stores input fields `cxd_test`, `cxd_flags`, `cxd_access1`, `cxd_sharemode1`, `cxd_access2`, `cxd_sharemode2`, plus output arrays `cxd_result[CXD_MAX]` and `cxd_result2[CXD_MAX]`.
- `static const struct createx_data cxd_known[]`: the full immutable known-result table that includes this chunk.

The access masks visible here are the grouped access permutations generated from `denytest.c`'s `sec_access_bit_groups`: `SEC_RIGHTS_FILE_READ`, `SEC_RIGHTS_FILE_WRITE`, and `SEC_RIGHTS_FILE_EXECUTE`. Common combined masks include `0`, `0x120089`, `0x120116`, `0x12019f`, `0x1200a0`, `0x1200a9`, `0x1201b6`, and `0x1201bf`. The share modes range over the 8 permutations of `NTCREATEX_SHARE_ACCESS_{NONE,READ,WRITE,DELETE}`; in this slice `sharemode1` is mostly `6` then `7`, while `sharemode2` progresses from `1` through `6`.

## Control Flow Represented

The table itself has no executable control flow, but each row corresponds to one pass through `torture_createx_specific()` in `denytest.c`:

1. The harness fills `open_parms1` with `cxd_access1` and `cxd_sharemode1`.
2. For `CXD_TEST_CREATEX_SHAREMODE`, it also fills `open_parms2` with `cxd_access2` and `cxd_sharemode2`.
3. Client 1 calls `smb_raw_open()` and stores the create status in `cxd_result[CXD_CREATEX]`.
4. If the first open succeeds, `createx_test_file()` records read, write, and execute-read outcomes in the remaining first-result slots.
5. Client 2 repeats the open and file-operation probes, storing statuses in `cxd_result2`.
6. `cxd_find_known()` finds the matching `cxd_known[]` row and `COMPARE_STATUS` checks each observed status against the stored Windows reference values.

For example, rows with `cxd_access1 = 0x12019f` often have all first-result slots as `NT_STATUS_OK`, reflecting a broad first-handle access mask. Rows with narrower masks retain `NT_STATUS_OK` for the open but deny the follow-up operations not covered by that handle's access rights. The second-result array varies independently based on both the second access mask and whether the first handle's share mode allows the requested second-handle access.

## State And Persistence Behavior

This chunk is persistent golden test data. It is compiled into the torture binary through `denytest.c`'s include of `cxd_known.h`; there is no runtime mutation of the table.

Runtime state lives in temporary `struct createx_data cxd` instances built by the test loops. `torture_createx_sharemodes()` mutates that temporary object while iterating share-mode and access-group permutations, then uses this static table as the expected reference. If the environment variable path for generated `CREATEX_DATA` is used in other modes, `torture_createx_specific()` can write binary `struct createx_data` records to disk, but this known table is the checked-in textual form used for normal comparisons.

The state under test is SMB server open/share state: the first successful handle can constrain whether the second client can open the same path and what access the second handle can exercise. The file object is cleaned up by `smbcli_unlink()` after each specific test, keeping cases isolated.

## Dependencies And Integration Points

Primary integration points:

- `sources/user-network-fs/samba/source4/torture/basic/denytest.c`: includes this header, defines `CXD_MATCHES`, `cxd_find_known()`, `torture_createx_specific()`, `createx_test_file()`, and `torture_createx_sharemodes()`.
- SMB torture raw APIs: `smb_raw_open()`, `smb_raw_read()`, `smb_raw_write()`, `smbcli_close()`, and `smbcli_unlink()` execute the live operations whose statuses are compared to this table.
- NT status constants: rows use `NT_STATUS_OK` and `NT_STATUS_ACCESS_DENIED`; `COMPARE_STATUS` and `nt_errstr()` are used by the harness when validating or printing regenerated rows.
- Access/share constants: the values originate from Samba's file access-right and `NTCREATEX_SHARE_ACCESS_*` definitions.
- Test entry points: `torture_createx_sharemodes_file()` drives the non-directory, non-extended share-mode run represented by this chunk; directory and extended variants use other table sections or generated output paths.

## Risks And Maintenance Notes

The rows are highly regular and order-sensitive. `cxd_find_known()` has a fast path that tries the next table index before falling back to a full scan, relying on the table order matching the generator loops for performance. Reordering rows without preserving the generated iteration sequence would not necessarily break correctness, but it would make the fast path less effective.

The expected values are compatibility data from an old Windows release. Changes in Samba's interpretation of access masks, generic rights expansion, share-access conflict checks, or execute-read behavior may produce large diffs here. Such diffs should be reviewed as protocol-semantic changes, not mechanical table churn.

Because the chunk starts and ends inside the matrix, local analysis should not infer section completeness from this file alone. Adjacent chunks contain the preceding `sharemode1=5/6` rows and the remaining `sharemode1=7`, `sharemode2=6/7` rows, followed later by directory data.

The rows contain only successful create/open statuses or access-denied outcomes in this range. There are no path-not-found, sharing-violation, invalid-parameter, or object-name-collision expectations visible here, so a regression that changes denial flavor could show up as a status mismatch even if the high-level operation is still denied.

## Test Signals

Useful signals in this exact line range:

- 855 `CXD_TEST_CREATEX_SHAREMODE` file rows.
- 855 rows with `cxd_flags = 0`, so the file operation slots are read, write, and execute-read rather than directory enumerate, child-create, and traverse.
- 855 rows with `cxd_result2`, confirming this is two-open share-mode data rather than single-open access-only data.
- `sharemode1=6` appears in 434 rows and `sharemode1=7` appears in 421 rows.
- `sharemode2` coverage in this slice spans values `1` through `6`, with partial coverage at both ends because the chunk starts and ends mid-block.
- Status tokens are dominated by `NT_STATUS_OK`, with many `NT_STATUS_ACCESS_DENIED` entries in operation slots where the open succeeds but the handle lacks the requested read/write/execute capability.

The chunk should remain stable when `BASE-CREATEX_SHAREMODE` preserves Windows-compatible two-handle file open behavior for these access and share-mode permutations. It should fail loudly through the torture comparison path if Samba starts permitting or denying a first or second handle operation differently from the stored `cxd_known[]` reference.
