# sources/user-network-fs/samba/source4/torture/vfs/fruit.c lines 1-7330

## Chunk Scope

This chunk covers the first 7,330 lines of Samba's `source4/torture/vfs/fruit.c`. It starts at the file header and includes most of the SMB2 torture tests for `vfs_fruit`: AFP metadata packing, resource fork stream behavior, AppleDouble conversion fixtures, AAPL create-context negotiation, stream enumeration, copyfile/copychunk behavior, NFS ACE handling, and the empty-stream matrix. The range ends inside the `osx_adouble_dir_w_xattr` AppleDouble fixture; the tests that consume that directory fixture are outside this chunk.

Large static byte arrays are present in this range. They are not executable control flow, but they are important test fixtures: `metadata_xattr`, `osx_adouble_w_xattr`, `osx_adouble_without_xattr`, `osx_adouble_non_empty_rfork_w_xattr`, and the beginning of `osx_adouble_dir_w_xattr`. The comments decode their AppleDouble or Netatalk metadata structure and document expected FinderInfo, resource fork, and extended-attribute payloads.

## Purpose

`fruit.c` is a Samba torture test file for the `vfs_fruit` module and related SMB2/Mac interoperability behavior. The tests exercise how Samba exposes Apple metadata and resource forks through SMB named streams, Apple AAPL SMB2 extensions, AppleDouble conversion, Netatalk extended attributes, stream lifecycle rules, and macOS-compatible quirks.

The code is built around observable SMB2 semantics rather than internal `vfs_fruit` implementation details. It creates files/directories on a test share, writes or injects Apple metadata, negotiates AAPL extensions when needed, then asserts exact stream lists, NTSTATUS values, EOF sizes, read data, copychunk responses, ACL shapes, and directory enumeration metadata. Many tests encode macOS behavior that Samba intentionally emulates, including non-intuitive AFP_AfpInfo reads beyond the logical 60-byte size and different deletion semantics for metadata streams versus resource forks.

## Important Fixtures

- `metadata_xattr` models a Netatalk metadata extended attribute containing file dates, FinderInfo with type/creator `BARRFOOO`, and AFP file info. `test_read_netatalk_metadata` writes it directly to the local share path using `setxattr()` and then verifies Samba exposes it as `AFP_AfpInfo`.
- `osx_adouble_w_xattr` is an AppleDouble file with FinderInfo, resource fork, and embedded `ATTR` extended attributes. Its xattrs include macOS metadata and a stream name containing an illegal NTFS colon encoded through the private-use character convention.
- `osx_adouble_without_xattr` is an AppleDouble file with resource fork and FinderInfo but without embedded xattr data. It is used to verify conversion still migrates FinderInfo and resource data.
- `osx_adouble_non_empty_rfork_w_xattr` is like the xattr fixture but with the resource fork payload intentionally made non-empty in the checked area. `test_adouble_conversion` expects bytes `0xf0` through `0xff` at offset 16 of `AFP_AfpResource`.
- `osx_adouble_dir_w_xattr` begins at the end of this chunk. The decoded comment shows an AppleDouble record for a directory with FinderInfo, a quarantine xattr, and a resource fork entry. Its consumer tests continue after line 7330.

## Important APIs, Types, And Helpers

- `BASEDIR`, `FNAME_CC_SRC`, and `FNAME_CC_DST` define shared test names. Most tests create all state under `vfs_fruit_dir` and clean it with `smb2_deltree()`.
- `CHECK_STATUS` and `CHECK_VALUE` are local assertion macros that report a torture failure and jump to `done`.
- `AFPINFO_EA_NETATALK` and `AFPRESOURCE_EA_NETATALK` select the platform-specific xattr names used by Netatalk interop tests. FreeBSD/`attropen` platforms use unprefixed names; Linux-style platforms use `user.org.netatalk.*`.
- `AfpInfo` comes from `MacExtensions.h`. `torture_afpinfo_new()` initializes signature, version, and backup time. `torture_afpinfo_pack()` serializes the 60-byte AFP info blob with `RSIVAL()` and copies FinderInfo at offset 16.
- `torture_write_afpinfo()` opens `<file>:AFP_AfpInfo` with `NTCREATEX_DISP_OVERWRITE_IF` and writes the packed 60-byte blob.
- `check_stream()` opens a named stream, reads an exact byte count at an offset, and compares a selected subrange. If the expected value is `NULL`, missing streams are considered success.
- `read_stream()` returns the number of bytes read from a stream and treats `NT_STATUS_END_OF_FILE` as a non-fatal condition for EOF boundary tests.
- `write_stream()` opens a file or stream with `NTCREATEX_DISP_OPEN_IF` and writes data at an offset.
- `torture_setup_local_xattr()` bridges SMB-level tests with local filesystem state by using the configured `localdir`/share path and `setxattr()`.
- `torture_setup_file()` creates either a file or directory over SMB2 with broad share access and normalizes cleanup before creation.
- `enable_aapl()` sends an SMB2 CREATE on the root path with the `AAPL` create context and verifies returned server capabilities. This call intentionally changes AAPL behavior for the SMB session.
- `check_stream_list()` and `check_stream_list_handle()` query `RAW_FILEINFO_STREAM_INFORMATION`, sort both expected and actual stream names, and compare exact stream sets.
- The copy helpers (`write_pattern`, `check_pattern`, `test_setup_copy_chunk`, `check_copy_chunk_rsp`, `copy_one_stream`, `copy_finderinfo_stream`) construct SMB2 FSCTL copychunk requests and validate file/stream copy results.
- `check_nfs_sd()` validates that a security descriptor has exactly one NFS mode, one NFS uid, and one NFS gid ACE domain entry.
- `struct tcase`, `struct tcase_results`, and `subtcase_t` drive the empty-stream matrix. They encode expected size, open status, and stream visibility before and after closing handles for AFPInfo, AFPResource, and ordinary streams.

## Control Flow And Test Coverage

The test functions generally follow a common pattern:

1. Allocate a temporary talloc context.
2. Remove any prior `BASEDIR` tree or test file.
3. Create a base directory and file.
4. Optionally negotiate AAPL extensions or inject local xattrs/AppleDouble files.
5. Open, write, truncate, delete, copy, enumerate, or query SMB2 streams.
6. Assert exact NTSTATUS values, stream lists, file sizes, and data bytes.
7. Close handles and clean the test tree.

The first group validates AFP metadata and resource forks:

- `test_read_netatalk_metadata()` requires a configured `localdir`, writes the Netatalk metadata xattr locally, and verifies `AFP_AfpInfo` reads expose the AFP signature and FinderInfo. It also checks odd EOF behavior for reads at offsets 59, 60, and 61.
- `test_read_afpinfo()` creates an AFPInfo stream through SMB and verifies the same read-boundary behavior, including the macOS-compatible behavior where reads with offsets up to 60 return data as if from offset 0.
- `test_write_atalk_metadata()` writes FinderInfo type/creator data and reads it back from `AFP_AfpInfo`.
- `test_write_atalk_rfork_io()` writes `AFP_AfpResource` at sparse offsets, checks resulting resource fork sizes, and truncates the resource fork to one byte.
- `test_rfork_truncate()` verifies that truncating an open resource fork to zero removes visibility for new opens while preserving valid behavior for existing and newly recreated handles.
- `test_rfork_create()` verifies that creating an empty resource fork does not make it visible as a real stream until it has data.
- `test_rfork_fsync()` covers the regression noted for bug 15182: creating, writing, and flushing a resource fork must succeed.
- `test_rfork_create_ro()` confirms that `OPEN_IF` with read-only access can create/open a resource fork without requiring write access.

The AppleDouble conversion tests then use the embedded fixture arrays:

- `test_adouble_conversion()` writes `._test_adouble_conversion` using `osx_adouble_non_empty_rfork_w_xattr`, then reads the base file's `AFP_AfpResource`, `AFP_AfpInfo`, xattr-derived stream, and expected stream list. This is Samba-only and skips on an OS X server.
- `test_adouble_conversion_wo_xattr()` uses `osx_adouble_without_xattr`, negotiates AAPL, triggers server-side conversion via `smb2_find_level()`, and verifies only default, AFPInfo, and AFPResource streams exist.

The AAPL and directory enumeration block tests session-level Apple extension behavior:

- `test_aapl()` sends an `AAPL` create context requesting server caps, volume caps, and model info. It validates command, reply bitmap, server capability bits, model string conversion from UTF-16LE, and AAPL-enriched `SMB2_FIND_ID_BOTH_DIRECTORY_INFO` results. After writing FinderInfo and a 3-byte resource fork, it expects the resource fork length in `short_name_buf[0..7]` and FinderInfo at `short_name_buf + 8`.
- `test_readdir_attr_illegal_ntfs()` creates a file whose visible name includes the private-use replacement for an illegal NTFS colon, writes metadata/resource fork data, and checks AAPL directory enumeration preserves the encoded name while returning macOS metadata.
- `test_stream_names()` creates a stream whose name encodes an illegal colon and verifies stream enumeration returns the normalized `:foo<private-use>bar:$DATA` plus the default stream.

The copy tests exercise SMB server-side copy semantics:

- `test_copyfile()` first verifies a zero-chunk `FSCTL_SRV_COPYCHUNK` without AAPL copyfile support returns success with zero total bytes copied. It then negotiates AAPL `SUPPORTS_OSX_COPYFILE`, creates a source file with default data, an AFP resource fork, and an additional named stream, issues zero-chunk copyfile semantics, and verifies main file data plus both streams were copied.
- `test_copy_chunk_streams()` verifies ordinary named streams, `AFP_AfpResource`, and `AFP_AfpInfo` can be copied with one explicit copychunk descriptor.

The deletion/truncation tests focus on lifecycle differences:

- `test_afpinfo_enoent()` verifies that opening missing `AFP_AfpInfo` with stat-style access returns `NT_STATUS_OBJECT_NAME_NOT_FOUND`.
- `test_create_delete_on_close()` and `test_setinfo_delete_on_close()` show `AFP_AfpInfo` can be deleted by create delete-on-close or setinfo delete-on-close. While a delete-on-close handle is open, new opens see `NT_STATUS_DELETE_PENDING`; after close, stream enumeration drops back to default only.
- `test_setinfo_eof()` confirms `AFP_AfpInfo` cannot be extended past 60 bytes, and truncation to 1 or 0 succeeds but does not remove or alter the FinderInfo stream.
- `test_afpinfo_all0()` writes a valid AFPInfo blob with zero FinderInfo and confirms stream enumeration suppresses the AFPInfo stream even while the stream handle remains usable for metadata updates.
- `test_create_delete_on_close_resource()` and `test_setinfo_delete_on_close_resource()` show `AFP_AfpResource` differs: delete-on-close does not remove the resource stream in the same way AFPInfo does.
- `test_setinfo_eof_resource()` shows setting resource fork EOF to 1 changes its size, and setting EOF to 0 deletes the resource stream.
- `test_setinfo_stream_eof()` applies the same style of checks to an ordinary `:foo` stream, including EOF 21, EOF 0 removal, EOF 1 recreation, AAPL-enabled zero truncation, base-file truncation, and writes after EOF zeroing.

Other covered behavior:

- `test_null_afpinfo()` uses compounded SMB2 create+read to verify a newly created AFPInfo stream reads as the default 60-byte metadata blob, then writes and validates FinderInfo.
- `test_delete_file_with_rfork()` verifies deleting a base file also removes its resource fork backing state.
- `test_rename_and_read_rsrc()` verifies a base file rename fails while a resource fork is open, with expected status differing between macOS and Samba, and that writes through the open resource fork handle still work.
- `test_invalid_afpinfo()` uses a second non-fruit share to create an invalid AFPInfo stream. The fruit share must hide the bad stream and fail opens with `OBJECT_NAME_NOT_FOUND`.
- `test_writing_afpinfo()` runs a large offset/size matrix for writes to `AFP_AfpInfo`. It expects all-zero writes to be invalid, accepts only writes large enough to contain a valid AFPInfo header/signature according to offset/size, and checks stream visibility/FinderInfo results. It has an option for the macOS Radar 45759458 behavior via `broken_osx_45759458`.
- `test_zero_file_id()` verifies `create.out.on_disk_id` is non-zero normally but all zero after AAPL is negotiated when the share is configured for `fruit:zero_file_id=yes`.
- `test_nfs_aces()` negotiates AAPL, gets a security descriptor, adds duplicate NFS uid/gid ACEs, writes it back, and verifies Samba condenses the NFS mode/uid/gid domain entries back to exactly one each.
- `test_empty_stream()` opens a second SMB2 connection and runs the table-driven empty-stream matrix across AFPInfo read-only, AFPInfo read/write, AFPResource read-only, AFPResource read/write, ordinary stream read-only, and ordinary stream read/write cases. Each case checks size, open status from same and different clients, stream visibility while handles are open, final status after close, EOF-zero behavior, overwrite behavior, and delete-on-close behavior.

## State And Persistence Behavior

The tests manipulate three kinds of persistent state:

- SMB files and named streams on the test share, mostly under `vfs_fruit_dir`.
- Local filesystem extended attributes when a test needs Netatalk interop or AppleDouble conversion seed data.
- Session-level AAPL extension state, which is enabled by a special SMB2 CREATE context and then affects later operations in the same SMB session.

`AFP_AfpInfo` is treated as a logical 60-byte metadata stream. Its serialized form includes signature, version, backup time, and FinderInfo. Several tests assert that this stream may be suppressed from enumeration when it contains only default or zero FinderInfo. Writes that cannot form a valid AFPInfo are rejected with `NT_STATUS_INVALID_PARAMETER`.

`AFP_AfpResource` is treated like the resource fork data stream. It may have sparse writes, real EOF changes, and deletion when EOF is set to zero. The tests intentionally distinguish it from AFPInfo, which has fixed-size logical metadata behavior.

AppleDouble conversion persists data by creating `._` files and then triggering server-side conversion through stream access or directory enumeration. After conversion, the base file should expose migrated AFPInfo, AFPResource, and xattr-derived streams; later chunks cover additional conversion/deletion cases.

The empty-stream tests are especially stateful. They verify that stream visibility can depend on whether a handle remains open, whether data has actually been written, whether EOF was set to zero, and whether a second SMB2 client sees the same state.

## Dependencies And Integration Points

Primary dependencies visible in this chunk:

- Samba torture framework: `struct torture_context`, `torture_assert_*`, `torture_skip`, suite registration helpers outside this range, and SMB2 test utilities.
- SMB2 client APIs: `smb2_create`, `smb2_create_send/recv`, `smb2_read`, `smb2_util_write`, `smb2_util_close`, `smb2_getinfo_file`, `smb2_setinfo_file`, `smb2_find_level`, `smb2_ioctl`, `smb2_lock`, `smb2_flush`, and utility helpers for unlink/rmdir/deltree/testdir/testfile.
- SMB2 create contexts: `smb2_create_blob_add()`, `smb2_create_blob_find()`, and `SMB2_CREATE_TAG_AAPL`.
- Mac extension constants and types from `MacExtensions.h`, including AFP stream names, AFP info sizes, signatures, and AAPL capability bits.
- NDR ioctl structures for `FSCTL_SRV_REQUEST_RESUME_KEY` and `FSCTL_SRV_COPYCHUNK`.
- Security descriptor APIs and Unix NFS SID domains for AAPL NFS ACE tests.
- Local xattr APIs from `system/filesys.h` for Netatalk metadata injection.
- Runtime torture settings: `localdir`, `osx`, and `broken_osx_45759458` adjust expectations or skip behavior.

The tests are integration tests for share configurations. Some require Samba with `vfs_fruit`; some require `fruit:metadata=netatalk`, `fruit:zero_file_id=yes`, AAPL support, streams/xattr behavior, a second non-fruit share, or a local path setting.

## Risks And Edge Cases

- AAPL negotiation is session-scoped. Tests that call `enable_aapl()` can change behavior for later operations on the same tree/session, so ordering and cleanup matter.
- AFPInfo semantics are intentionally surprising: fixed logical size, special read offsets, invalid short writes, stream suppression for zero/default FinderInfo, and no deletion on EOF zero. Regressions here can look like ordinary stream behavior but break macOS clients.
- AFPResource semantics are closer to ordinary data streams, but not identical. Zero-length resource forks may be hidden, and open handles must remain coherent across truncate/recreate cases.
- AppleDouble conversion relies on exact binary fixture layout. Small fixture changes can alter expected FinderInfo, resource fork bytes, xattr-derived stream names, or conversion trigger behavior.
- Stream names with illegal NTFS characters use private-use Unicode substitutions in source literals. Incorrect normalization can break stream enumeration and AAPL readdir attributes even if raw stream I/O still works.
- Copyfile semantics overload zero-chunk `FSCTL_SRV_COPYCHUNK` after AAPL copyfile negotiation. The same ioctl has different expected total bytes before and after negotiation.
- Several tests skip or change expectations on macOS servers. Samba and macOS compatibility are deliberately compared but not identical.
- The empty-stream matrix closes handles inside helper routines and also has outer cleanup. Handle lifetime bugs can mask stream visibility issues or cause false sharing/delete-pending results.
- This chunk stops at the beginning of the directory AppleDouble byte array. Any final interpretation of directory AppleDouble conversion must be reconciled with the following chunk where the fixture and consumer tests complete.

## Test Signals

Strong validation signals for this chunk include:

- `smbtorture` fruit suite cases passing for metadata read/write, resource fork I/O, resource fork truncation/create/fsync, AAPL negotiation, stream names, copyfile, copychunk streams, NFS ACEs, invalid AFPInfo, AFPInfo write matrix, stream EOF, and empty-stream behavior.
- Exact NTSTATUS checks: `OK`, `OBJECT_NAME_NOT_FOUND`, `DELETE_PENDING`, `INVALID_PARAMETER`, `ALLOTTED_SPACE_EXCEEDED`, and macOS/Samba-specific rename failures.
- Stream list checks returning only expected streams, especially default-only suppression for empty AFPInfo/resource/ordinary streams and exact inclusion of `AFP_AfpInfo`, `AFP_AfpResource`, and encoded illegal-colon streams after data writes or conversion.
- Byte checks for FinderInfo values such as `BARRFOOO`, `SMB,OLE!`, `TESTSLOW`, `WAVEPTul`, and `FOO BAR `.
- Resource fork size checks after sparse writes, EOF changes, copyfile, and copychunk.
- AAPL directory enumeration checks for returned capability bits, model string, resource fork length, FinderInfo in `short_name_buf`, and zero on-disk file IDs when configured.
- Cross-client checks in `test_empty_stream()` confirming same-client and different-client visibility agree with the table expectations while handles are open and after they close.
- Samba-only AppleDouble conversion tests skipping on macOS while passing on Samba with fixture-derived metadata and streams.
