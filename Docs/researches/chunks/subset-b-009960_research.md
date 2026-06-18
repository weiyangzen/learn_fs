# sources/user-network-fs/samba/source4/torture/basic/cxd_known.h lines 5413-6351

## Scope

This chunk covers lines 5413-6351 of `source4/torture/basic/cxd_known.h`. The range is a 939-row slice of the `static const struct createx_data cxd_known[]` oracle table used by Samba's `BASE-CREATEX_*` torture tests. Every row in this slice has:

- `cxd_test = 2`, which is `CXD_TEST_CREATEX_SHAREMODE`.
- `cxd_flags = 0x1`, which is `CXD_FLAGS_DIRECTORY`.
- Two create/open parameter sets: `cxd_access1`/`cxd_sharemode1` for the first directory open and `cxd_access2`/`cxd_sharemode2` for the second concurrent directory open.
- Expected status arrays `cxd_result` and `cxd_result2`, each containing four `NT_STATUS_OK` entries.

The chunk starts in the middle of the directory share-mode matrix, at rows for first share mode `1` and second share mode `5`, and ends in the middle of rows for first share mode `3` and second share mode `3`. It is not a function boundary; it is one contiguous piece of a larger generated/recorded Windows XP compatibility table.

## Purpose

The purpose of this data is to encode known Windows behavior for `NTCreateX` share-mode compatibility on directories. The surrounding torture harness opens a directory with one access/share tuple, optionally performs directory operations through that handle, then opens the same directory through a second SMB connection with another access/share tuple and compares the observed statuses against this table.

Within this slice, all listed combinations are expected to succeed. That means Windows allowed the first directory open, allowed the first handle's directory operation probes, allowed the second directory open, and allowed the second handle's directory operation probes for the covered access and share-mode combinations. This is important because directory share-mode behavior often differs from file behavior and from naive read/write/delete conflict rules.

The table was documented at file scope as having been taken from Windows XP Pro 2002 Service Pack 2. It is therefore a compatibility oracle, not a derived rule engine. Samba's test suite uses it to catch regressions in server-side create/share/access semantics by comparing live server behavior against these known results.

## Important APIs, Types, And Data Fields

The relevant declarations are earlier in the same header:

- `enum cxd_test` defines `CXD_TEST_CREATEX_SHAREMODE` as value `2`.
- `enum cxd_flags` defines `CXD_FLAGS_DIRECTORY` as `0x1` and `CXD_FLAGS_MAKE_BEFORE_CREATEX` as `0x2`.
- `enum { CXD_CREATEX, CXD_FILE_READ/CXD_DIR_ENUMERATE, CXD_FILE_WRITE/CXD_DIR_CREATE_CHILD, CXD_FILE_EXECUTE/CXD_DIR_TRAVERSE, CXD_MAX }` defines the four result slots used for either file or directory tests.
- `struct createx_data` stores the test selector, flags, first and second access masks/share modes, and expected `NTSTATUS` arrays for both handles.
- `cxd_known[]` is the static table consumed by `source4/torture/basic/denytest.c`.

The fields in this chunk have these meanings in the consumer:

- `cxd_access1` and `cxd_access2` are the SMB `NTCreateX` access masks passed as `open_parms.ntcreatex.in.access_mask`.
- `cxd_sharemode1` and `cxd_sharemode2` are passed as `open_parms.ntcreatex.in.share_access`.
- `cxd_result[0]` is the first `smb_raw_open()` result.
- `cxd_result[1]` is the first handle's directory-enumeration slot. The directory path currently sets this to `NT_STATUS_OK` after creating a known child through a bypass handle.
- `cxd_result[2]` is the first handle's child-creation attempt through the opened directory root fid.
- `cxd_result[3]` is the first handle's traverse/open-known-child attempt through that root fid.
- `cxd_result2[]` is the same four-slot status vector for the second SMB connection's handle.

The access masks repeated in this slice include `0`, `0x120089`, `0x120116`, `0x12019f`, `0x1200a0`, `0x1200a9`, `0x1201b6`, and `0x1201bf`. These are grouped access-mask permutations produced by the harness from `sec_access_bit_groups[]`; the chunk records their observed behavior for selected share-mode pairings rather than naming each bit combination in place.

## Control Flow

The header has no executable control flow. Runtime behavior comes from `denytest.c`:

1. `torture_createx_sharemodes_dir()` calls `torture_createx_sharemodes(..., dir=true, extended=false)`.
2. The harness initializes `struct createx_data cxd` with `cxd_test = CXD_TEST_CREATEX_SHAREMODE` and `cxd_flags = CXD_FLAGS_DIRECTORY`.
3. Nested loops iterate all share-mode permutations for `cxd_sharemode1` and `cxd_sharemode2`, then iterate grouped access-mask permutations for `cxd_access1` and `cxd_access2`.
4. `torture_createx_specific()` selects directory helpers because `CXD_FLAGS_DIRECTORY` is set.
5. `createx_fill_dir()` builds a `RAW_OPEN_NTCREATEX` request using directory attributes, `NTCREATEX_DISP_OPEN_IF`, and `NTCREATEX_OPTIONS_DIRECTORY`.
6. The first open runs through `smb_raw_open(cli->tree, ...)`. If it succeeds, `createx_test_dir()` probes directory behavior and closes the handle.
7. Because this is a share-mode test, the second open runs on `cli2->tree` with the second access/share tuple, probes behavior if open succeeds, and closes that handle.
8. `cxd_find_known()` looks for an exact tuple match in `cxd_known[]`; if found, the observed status arrays are compared to the expected arrays in the table.
9. If a tuple is missing from the table or a comparison fails, the harness prints a C initializer-style row that can be used to update or inspect the oracle.

The chunk's all-OK rows therefore represent the comparison path where both open/probe sequences are expected to pass without conflict.

## State And Persistence Behavior

The table itself is compile-time read-only state. It does not persist data and does not mutate process state.

The live test harness creates and removes transient share objects:

- `CREATEX_NAME` is `\\createx_dir`.
- Directory tests create or use that directory as the target under test.
- `createx_test_dir()` creates `\\createx_dir\\KNOWN` through a bypass handle, attempts to create `CHILD` relative to the tested directory handle, attempts to open `KNOWN` relative to that handle, then unlinks both children.
- The share-mode driver starts from a blank slate by calling `smbcli_deltree()` and `smbcli_unlink()` on `CREATEX_NAME`.

There is a small process-local cache in `cxd_find_known()`: a static index is incremented and checked before the full table scan. This relies on the harness generating tuples in the same order as the table. If the table order and generator order drift, correctness remains because the function falls back to a full scan, but performance degrades.

For exhaustive tests not represented by this chunk, `CREATEX_DATA` can redirect observed `struct createx_data` records to a data file. The ordinary `CXD_TEST_CREATEX_SHAREMODE` path represented here compares against `cxd_known[]` instead.

## Dependencies And Integration Points

This chunk integrates with Samba's torture and SMB client layers through `denytest.c`:

- SMB raw client calls: `smb_raw_open()`, `smbcli_close()`, `smbcli_deltree()`, `smbcli_unlink()`, and `smbcli_rmdir()`.
- Raw SMB open structures: `union smb_open`, `RAW_OPEN_NTCREATEX`, `NTCREATEX_DISP_OPEN_IF`, `NTCREATEX_OPTIONS_DIRECTORY`, and directory/file attributes.
- Status handling: `NTSTATUS`, `NT_STATUS_OK`, `NT_STATUS_UNSUCCESSFUL`, `NT_STATUS_IS_OK()`, `nt_errstr()`, and the local `COMPARE_STATUS` macro.
- Torture reporting: `torture_comment()`, `torture_result()`, `torture_warning()`, and the optional progress output.
- Test settings: `sacl_support` can skip cases involving `SEC_FLAG_SYSTEM_SECURITY`; this chunk's access masks are ordinary grouped masks and do not show SACL-specific statuses.

The practical integration point is the `BASE-CREATEX_SHAREMODE` directory test. A Samba server that returns a sharing violation, access denied, path error, or operation failure for one of these rows will fail comparison against this oracle.

## Risks And Maintenance Notes

- This is data with protocol semantics. Editing one row can change the expected compatibility contract for a large matrix of SMB directory create/share behavior.
- The rows are positional only for performance, not correctness. However, preserving generator order matters because `cxd_find_known()` first tries the next static index before scanning the full table.
- The chunk begins and ends inside larger share-mode/access cross-products. Merge/reconciliation work must avoid treating the range as a self-contained logical table.
- All statuses in this slice are `NT_STATUS_OK`. That uniformity is a useful signal, but it also makes accidental row corruption hard to notice by visual scanning unless the access/share tuple itself is checked.
- The expected behavior is based on Windows XP SP2. Modern Windows versions may differ, but the test's stated oracle is the recorded XP behavior unless the wider test policy is intentionally changed.
- Directory probes reuse result slots whose enum aliases overlap file and directory operation names. Readers must interpret slots `1..3` as directory enumerate/create-child/traverse when `CXD_FLAGS_DIRECTORY` is set.
- The second open uses a second SMB client connection. Share-mode regressions can therefore arise from server-wide share reservation handling, not only from per-connection handle logic.
- Cleanup failures in the harness can make later rows fail even if the table is correct, because all rows reuse `\\createx_dir` and child names under it.

## Test Signals

The direct signal for this chunk is the `BASE-CREATEX_SHAREMODE` directory torture path reaching these tuples and comparing every observed slot to `NT_STATUS_OK`.

Useful positive signals:

- The first directory `NTCreateX` succeeds for each listed `cxd_access1` and `cxd_sharemode1`.
- The first handle's directory probe slots remain `NT_STATUS_OK`.
- The second directory `NTCreateX` succeeds for each listed `cxd_access2` and `cxd_sharemode2` while the test is exercising share compatibility.
- The second handle's directory probe slots remain `NT_STATUS_OK`.
- The test prints progress rather than generated replacement rows, because generated rows indicate missing oracle entries or comparison failures.

Focused negative signals:

- `NT_STATUS_SHARING_VIOLATION` or `NT_STATUS_ACCESS_DENIED` for any row in this chunk means the server no longer matches the recorded Windows directory share-mode behavior for that tuple.
- A printed initializer for a tuple in lines 5413-6351 means either the table lookup did not find the row or a status differed from the expected all-OK vector.
- Slower execution without failures can indicate the tuple order no longer aligns with the static-index fast path in `cxd_find_known()`, forcing repeated full scans of the large `cxd_known[]` table.
