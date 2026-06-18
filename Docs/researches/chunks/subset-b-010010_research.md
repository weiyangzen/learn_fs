# sources/user-network-fs/samba/source4/torture/vfs/fruit.c lines 7331-8891

## Scope

This chunk covers lines 7331-8891 of `sources/user-network-fs/samba/source4/torture/vfs/fruit.c`. It is the tail of Samba's SMB2 `vfs_fruit` torture tests. The range starts in the middle of the `osx_adouble_dir_w_xattr` AppleDouble directory fixture byte array, then defines several focused tests and suite factories:

- Directory AppleDouble conversion and delete/open behavior around `test_delete_trigger_convert_sharing_violation()`.
- AAPL-negotiated locking and case-insensitive find checks.
- The main `torture_vfs_fruit()` suite registration for all general fruit tests.
- Netatalk-specific stream-name and locking-conflict tests, plus their suite.
- File-ID, Time Machine volume-size, conversion, unfruit, and AFPInfo validation suite/test entry points.

The chunk depends heavily on helpers and fixtures defined earlier in the same file, including `BASEDIR`, `AFPINFO_STREAM`, `AFPRESOURCE_STREAM_NAME`, `osx_adouble_w_xattr`, `test_zero_file_id()`, `enable_aapl()`, `write_stream()`, `check_stream()`, `check_stream_list()`, `torture_setup_file()`, `torture_write_afpinfo()`, and `torture_afpinfo_new()`. Those helpers are not redefined in this range.

## Purpose

The covered code tests Samba's `vfs_fruit` compatibility layer for macOS SMB clients and Netatalk interoperability. The behavior under test is mostly not ordinary file I/O; it is the translation between Apple metadata/resource forks, NTFS-style alternate data streams, AppleDouble sidecar files, AAPL SMB2 create contexts, sparsebundle Time Machine accounting, and Netatalk-compatible byte-range locking.

The chunk validates that:

- AppleDouble directory data can coexist with an existing non-empty `AFP_AfpInfo` stream and another named stream without causing a sharing violation during a later directory delete-style open.
- A read-only SMB2 handle can still take an exclusive byte-range lock after AAPL negotiation.
- AAPL directory search remains case-insensitive and returns the original file name for a differently cased pattern.
- Fruit stream names containing colon-mapped private-use UTF-8 bytes are exposed consistently whether created over SMB or as local xattrs.
- Netatalk emulation byte-range locks cause an expected `NT_STATUS_SHARING_VIOLATION` on a second tree open even when SMB share modes themselves would otherwise be compatible.
- Time Machine sparsebundle volume-size reporting uses configured maximum size, parsed `Info.plist` band size, and current band count to synthesize `RAW_QFS_SIZE_INFORMATION`.
- AppleDouble conversion migrates Finder info and extended attributes into SMB streams, drops an empty resource fork, and optionally deletes now-empty AppleDouble sidecar files.
- The `net vfs stream2adouble` unfruit path can convert SMB streams back into an exact AppleDouble sidecar payload.
- AFPInfo validation rejects or tolerates an invalid write depending on torture settings, and leaves the AFPInfo header normalized to the expected signature and version.

## Important APIs, Types, And Functions

The static fixture `osx_adouble_dir_w_xattr` is an AppleDouble v2 encoded directory sidecar. The included comment before the chunk describes two entries: Finder info/extended attributes and a resource fork containing a mostly blank resource payload. The byte array includes an `ATTR` extended-attribute section for `com.apple.quarantine` and a resource fork payload. In this chunk it is written to `BASEDIR\\._dir` to trigger server-side directory AppleDouble conversion paths.

`test_delete_trigger_convert_sharing_violation()` builds a directory scenario with three metadata sources: a real directory, an AppleDouble sidecar for that directory, and explicit SMB streams on the directory. It writes non-zero Finder info using `AfpInfo`, rewrites the sidecar fixture, adds a second named stream, and finally opens the directory with `SEC_STD_DELETE`. The test passes if this open and close complete without surfacing a sharing violation from conversion-triggered internal opens.

`test_readonly_exclusive_lock()` negotiates AAPL extensions with `enable_aapl()`, creates a normal file, writes data, reopens it read-only with `SEC_FILE_READ_DATA | SEC_FILE_READ_ATTRIBUTE`, and sends an SMB2 lock request with `SMB2_LOCK_FLAG_EXCLUSIVE | SMB2_LOCK_FLAG_FAIL_IMMEDIATELY`. The expected status is `NT_STATUS_OK`, proving lock rights are not incorrectly tied to data-write access in this fruit/AAPL path.

`test_case_insensitive_find()` creates `BASEDIR\\TestFile.txt`, then searches the open directory handle using pattern `TESTFILE.TXT` at `SMB2_FIND_ID_BOTH_DIRECTORY_INFO` level. It expects exactly one result and verifies the returned `id_both_directory_info.name.s` is the original mixed-case name.

`torture_vfs_fruit()` is the general suite factory. It creates the `fruit` suite and registers all one-tree and two-tree tests for copyfile, metadata, resource forks, AAPL create contexts, stream names, AFPInfo edge cases, copy-chunk streams, AppleDouble conversion, NFS ACEs, empty streams, writing AFPInfo, delete-triggered conversion, read-only exclusive locks, and case-insensitive find.

`test_stream_names_local()` requires `torture:localdir`. It creates one SMB stream whose logical name contains a colon mapped to UTF-8 private-use bytes (`0xef 0x80 0xa2`), creates a second stream by directly setting a local `user.DosStream.bar:baz:$DATA` xattr, and checks the SMB stream list contains both mapped stream names plus the default data stream.

`test_fruit_locking_conflict()` uses two SMB2 trees. On the first tree it creates and opens `locking_conflict.txt`, then applies two exclusive byte-range locks: one at `0x7ffffffffffffffc` for the Netatalk resource-fork deny-write marker area, and one from offset 0 through `0x7ffffffffffffff7`. It then attempts to open the file for read/write on the second tree and expects `NT_STATUS_SHARING_VIOLATION`.

`torture_vfs_fruit_netatalk()` registers Netatalk-oriented tests that require `fruit:metadata=netatalk`: reading Netatalk metadata, local-xattr stream names, and the two-tree locking conflict.

`torture_vfs_fruit_file_id()` registers `test_zero_file_id()` under a suite requiring `fruit:zero_file_id=yes`. The implementation of `test_zero_file_id()` is earlier in the file; this chunk only exposes it as the `fruit_file_id` suite.

`test_timemachine_volsize()` creates `test.sparsebundle`, writes a minimal `Info.plist` with `band-size` set to `8192`, creates a `bands` directory, obtains a root handle, and calls `smb2_getinfo_fs()` for `RAW_QFS_SIZE_INFORMATION`. It first checks that zero bands do not crash the server, then creates two band files and asserts the synthesized geometry: `sectors_per_unit == 2`, `bytes_per_sector == 512`, `total_alloc_units == 32`, and `avail_alloc_units == 16`.

`test_convert_xattr_and_empty_rfork_then_delete()` is a two-share conversion test. It creates a normal file and an AppleDouble sidecar containing xattrs and an empty resource fork, negotiates AAPL on the fruit-enabled tree, runs a directory `smb2_find_level()` to trigger server-side conversion, and then checks that four streams exist: default data, AFPInfo, a `com.apple.metadata:_kMDItemUserTags` stream with colon mapping, and `foo:bar` with colon mapping. It also asserts that opening the AFP resource fork returns `NT_STATUS_OBJECT_NAME_NOT_FOUND`, proving the empty resource fork was removed.

`unconvert_adfile_data` is the exact expected AppleDouble v2 output for the unfruit path. It encodes a resource fork with `bar\0`, Finder info beginning with `FOO BAR `, and an embedded `ATTR` section containing one attribute named `org.samba:woohoo` with value `bar\0`.

`test_unconvert()` creates a file with AFPInfo Finder info, a named stream whose colon is represented by private-use UTF-8, and an AFP resource stream. It then runs an external command built from torture settings: `<net> --recursive vfs stream2adouble <sharename> <BASEDIR>/`. The test opens `BASEDIR\\._unconvert` through a second share without fruit, verifies its size equals `sizeof(unconvert_adfile_data)`, and compares the entire sidecar file byte-for-byte with `check_stream()`.

`test_fruit_validate_afpinfo()` creates a file, writes valid AFPInfo first, then opens the AFPInfo stream directly and attempts to write a 60-byte buffer with payload at offset 16 but without a valid header at offset 0. The `validate_afpinfo` torture setting controls whether `NT_STATUS_INVALID_PARAMETER` is expected. After the write attempt, the test checks that the first 8 bytes of the AFPInfo stream are normalized to `AFP_Signature` and `AFP_Version` using `PUSH_BE_U32()`.

## Control Flow

Most tests follow the same torture pattern: clear stale state with `smb2_deltree()` or `smb2_util_unlink()`, create a deterministic fixture under `BASEDIR`, perform one SMB2 operation that exercises fruit behavior, assert exact `NTSTATUS` and data results, then remove the test tree in a `done:` block.

`test_delete_trigger_convert_sharing_violation()` is deliberately ordered to stress conversion side effects. It creates both a real directory and an AppleDouble sidecar, writes AppleDouble data, writes AFPInfo directly to the directory, rewrites the sidecar, adds another named stream, and only then opens the directory for delete access. This sequence checks that fruit's on-demand sidecar conversion does not conflict with already materialized streams on the same directory.

`test_stream_names_local()` combines remote SMB and local filesystem setup. The SMB-created stream name is built from `fname` plus the first expected mapped stream name. The locally created xattr uses raw colon syntax in `user.DosStream.bar:baz:$DATA`, and `check_stream_list()` confirms the server presents the local xattr with the same private-use colon mapping conventions as the SMB-created stream.

`test_fruit_locking_conflict()` is stateful across two connections. The first open and locks establish the Netatalk conflict model; the second open happens on `tree2` specifically to verify inter-client conflict behavior rather than self-open behavior on one handle. It returns `false` by default and flips to `true` only after the expected sharing violation and close path complete.

`test_timemachine_volsize()` has two query phases. The first query after creating an empty `bands` directory is a crash guard. The second query after creating two bands performs precise allocation-unit assertions. Cleanup closes the root handle if it was opened and deletes the sparsebundle.

`test_convert_xattr_and_empty_rfork_then_delete()` uses a directory enumeration as the conversion trigger. The important transition is not file open or stream read; it is `smb2_find_level()` on the containing directory after AAPL has been negotiated. After that, all checks are performed through stream enumeration, failed resource-fork open, stream content reads, and a second directory enumeration for sidecar deletion policy.

`test_unconvert()` crosses out of the SMB2 torture helper layer by calling `system()`. It prepares the stream-backed file over the fruit share, runs `net vfs stream2adouble`, then validates the generated sidecar from a second non-fruit share. The cleanup line that would delete `BASEDIR` is commented out, so this test can leave its fixture behind for inspection or due to historical debugging needs.

## State And Persistence Behavior

The tests mutate share contents under fixed names. `BASEDIR` is the main scratch directory for most chunk tests, while `readonly_lock_test.txt`, `TestFile.txt`, `test.sparsebundle`, and `test_fruit_validate_afpinfo` are standalone names. Most tests clean up at exit, but failures before cleanup can leave sidecars, streams, or sparsebundle directories.

Apple metadata persists in several forms:

- AppleDouble sidecar files named `._dir`, `._test_adouble_conversion`, and `._unconvert`.
- SMB alternate data streams such as `AFP_AfpInfo`, `AFP_AfpResource`, and colon-mapped named streams.
- Local xattrs named as `user.DosStream.*` for Netatalk/streams_xattr behavior.
- Parsed sparsebundle state in `Info.plist` and `bands/*` for Time Machine size synthesis.

The conversion tests intentionally move state between those forms. `test_convert_xattr_and_empty_rfork_then_delete()` starts with AppleDouble data and expects Finder info and xattrs to appear as streams, while empty resource-fork state disappears. `test_unconvert()` does the reverse by starting with streams and expecting a deterministic AppleDouble sidecar.

Settings influence persistent outcomes. `delete_empty_adfiles` changes whether an empty AppleDouble sidecar should remain visible after conversion. `validate_afpinfo` changes whether an invalid AFPInfo write is expected to fail. `localdir`, `net`, and `sharename` are required for tests that interact with the local filesystem or external Samba tooling.

## Dependencies And Integration Points

The code integrates with Samba's torture framework through `torture_suite_create()`, `talloc_strdup()`, `torture_suite_add_1smb2_test()`, `torture_suite_add_2smb2_test()`, `torture_suite_add_2ns_smb2_test()`, `torture_assert_*`, `torture_comment()`, and `torture_skip()`.

SMB2 protocol operations are central: `smb2_create()`, `smb2_util_close()`, `smb2_util_write()`, `smb2_lock()`, `smb2_find_level()`, `smb2_getinfo_fs()`, `smb2_getinfo_file()`, `smb2_util_mkdir()`, `smb2_util_roothandle()`, `smb2_deltree()`, and `smb2_util_unlink()`. The tests use generated protocol structs such as `struct smb2_create`, `struct smb2_find`, `struct smb2_lock`, `struct smb2_lock_element`, `union smb_fsinfo`, `union smb_fileinfo`, and `union smb_search_data`.

Fruit-specific integration depends on AAPL negotiation via `enable_aapl()`, stream constants for AFPInfo/resource forks, AppleDouble parsing in the server, and Samba configuration options including `vfs objects = catia fruit streams_xattr`, `fruit:metadata=netatalk`, `fruit:zero_file_id=yes`, `fruit:time machine max size = 32K`, and `fruit:delete_empty_adfiles`.

The Netatalk path relies on byte-range lock offsets that encode Netatalk open/deny state. The local stream-name test requires a local filesystem path to the same share so `torture_setup_local_xattr()` can write xattrs outside the SMB protocol and then verify how the server projects them back as named streams.

The unfruit conversion path depends on the external Samba `net` binary and its `vfs stream2adouble` command. That makes `test_unconvert()` more environment-sensitive than pure SMB2 tests: it requires correct torture settings, a usable command path, and a second share view without fruit.

## Risks And Maintenance Notes

The chunk contains tests that are sensitive to exact server configuration. Running them without the expected fruit, catia, streams_xattr, Netatalk metadata, zero-file-id, or Time Machine settings can produce failures that reflect test-environment mismatch rather than product regression.

Several assertions depend on exact byte encodings. The AppleDouble fixtures and expected `unconvert_adfile_data` must stay synchronized with Samba's AppleDouble encoding rules, colon mapping, endianness, and xattr layout. A legitimate format change needs fixture updates and should preserve the documented semantic payload.

The `test_case_insensitive_find()` assertion compares the returned name to the original mixed-case spelling. That is correct for this test, but case-preserving behavior can vary with backend filesystem and share configuration; changes here should be checked against the intended Samba behavior and macOS client expectations.

`test_unconvert()` invokes `system(cmd)` with values from torture settings. It is a test-only path, but it still depends on shell command construction, path correctness, and local environment. The disabled cleanup at the end means this test can leave `BASEDIR` in place.

Locking tests use very high byte offsets to emulate Netatalk. Those constants are protocol-compatibility markers, not arbitrary stress offsets. Changing them risks no longer exercising the intended conflict path.

Cleanup is mostly best-effort. Some paths use `CHECK_STATUS`/`CHECK_VALUE` macros that jump to cleanup through shared state, but external command failure, assertion exits, or commented cleanup can leave files and streams behind. Concurrent test runs against the same share may interfere because names are fixed.

## Test Signals

Strong positive signals from this chunk include:

- `test_delete_trigger_convert_sharing_violation()` opens and closes the directory with delete access after sidecar and stream setup without `NT_STATUS_SHARING_VIOLATION`.
- `test_readonly_exclusive_lock()` receives `NT_STATUS_OK` for an exclusive byte-range lock on a read-only handle.
- `test_case_insensitive_find()` returns one `SMB2_FIND_ID_BOTH_DIRECTORY_INFO` result for `TESTFILE.TXT`, with the preserved name `TestFile.txt`.
- `test_stream_names_local()` reports exactly the two colon-mapped named streams plus `::$DATA`.
- `test_fruit_locking_conflict()` receives `NT_STATUS_SHARING_VIOLATION` on the second tree open after Netatalk-style locks are present.
- `test_timemachine_volsize()` reports 2 sectors per unit, 512 bytes per sector, 32 total allocation units, and 16 available allocation units after two 8 KiB bands under a 32 KiB max-size configuration.
- `test_convert_xattr_and_empty_rfork_then_delete()` sees four expected streams, cannot open the empty resource fork, reads `TESTSLOW` from AFPInfo at the expected offset, reads `baz` from the colon-mapped `foo:bar` stream, and sees the expected directory entry count based on `delete_empty_adfiles`.
- `test_unconvert()` produces an AppleDouble sidecar with exactly `sizeof(unconvert_adfile_data)` bytes and byte-for-byte matching content.
- `test_fruit_validate_afpinfo()` either rejects invalid AFPInfo writes with `NT_STATUS_INVALID_PARAMETER` or accepts them when configured, and in both cases verifies the first 8 bytes are the canonical AFP signature/version.

Useful regression indicators are unexpected stream-list ordering or counts, failure to map private-use colon bytes consistently, a resource fork still visible after empty-rfork conversion, Time Machine allocation values off by one band or allocation unit, failure to surface Netatalk lock conflicts, and AFPInfo headers left invalid after a failed write.

## Chunk Boundary Notes

The range begins mid-array at line 7331, so the complete AppleDouble directory fixture commentary starts before this chunk. The chunk ends with the full `test_fruit_validate_afpinfo()` function but does not show where, if anywhere, that public test symbol is registered by another suite. Whole-file reports should merge this chunk with earlier `fruit.c` chunks before making complete claims about helper definitions, all fixture origins, or complete suite exposure.
