# Group Research: group_1826_winbtrfs_sources_windows_winbtrfs_src_tests_rename_cpp_sources_wind_65f14564da94

Scope confirmed in `Docs/research_subset_a.md`: `sources/windows/winbtrfs` is part of subset A. The referenced internal group report path was not present in the workspace, so this report is based on complete reads of every listed source file.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/rename.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/rename.cpp

## Purpose

`rename.cpp` is the WinBtrfs test-suite coverage for Windows rename semantics. It exercises both legacy `FileRenameInformation` and Windows 10 1709+ `FileRenameInformationEx`, with particular focus on NT status compatibility, security checks, case behavior, target replacement, POSIX rename semantics, directory handling, and special name validation.

## Main Entrypoints

- `set_rename_information(...)`: builds `FILE_RENAME_INFORMATION`, calls `NtSetInformationFile(..., FileRenameInformation)`, and asserts `iosb.Information == 0`.
- `set_rename_information_ex(...)`: builds `FILE_RENAME_INFORMATION_EX`, calls `NtSetInformationFile(..., FileRenameInformationEx)`, and asserts `iosb.Information == 0`.
- `test_rename(const u16string& dir)`: legacy rename behavior tests.
- `test_rename_ex(HANDLE token, const u16string& dir)`: extended rename flag behavior tests.

## Behavior Covered

`test_rename` validates basic file and directory renames, same-name renames, case-only renames, overwriting existing files with and without `ReplaceIfExists`, and expected failures when the target is open. It verifies post-rename state through both `FileNameInformation` and directory enumeration.

The file covers moves across directories, including absolute target paths and relative target names under a `RootDirectory` handle. It also verifies sharing side effects when a directory handle prevents enumeration, and confirms old entries disappear while new entries appear.

Permission-sensitive coverage is extensive. Tests assert that renaming requires source `DELETE`, that the destination parent needs `FILE_ADD_FILE` or `FILE_ADD_SUBDIRECTORY`, and that replacing a target requires either target `DELETE` or parent `FILE_DELETE_CHILD`. It includes denied cases for missing parent access, missing source delete access, and overwriting targets protected by DACLs.

Type and attribute handling are explicitly tested. File-over-directory and directory-over-file replacement are expected to fail. Readonly targets reject replacement unless extended flags override that later. System targets can be replaced. Empty directory replacement has different behavior under extended POSIX semantics.

Name validation covers Windows-invalid characters, too-long UTF-8 names, and malformed UTF-16 surrogate sequences. The expected status depends on `fstype`: NTFS may accept names that WinBtrfs rejects as `STATUS_OBJECT_NAME_INVALID`.

`test_rename_ex` adds coverage for:
- `FILE_RENAME_REPLACE_IF_EXISTS`
- `FILE_RENAME_IGNORE_READONLY_ATTRIBUTE`
- `FILE_RENAME_POSIX_SEMANTICS`
- sharing violations when POSIX replacement target lacks `FILE_SHARE_DELETE`
- orphaned replaced files remaining usable through open handles
- `FILE_STANDARD_INFORMATION`, `FILE_STANDARD_LINK_INFORMATION`, and hardlink enumeration after POSIX replacement
- directory replacement with POSIX semantics, including non-empty directory failure
- mapped `SEC_IMAGE` targets rejecting normal and POSIX replacement

## Integration Points

This file depends heavily on shared helpers from `test.cpp` and `test.h`: `create_file`, `query_dir`, `query_file_name_information`, `query_information`, `query_links`, `set_disposition_information`, `set_dacl`, `create_section`, `pe_image`, `adjust_token_privileges`, and `disable_token_privileges`.

## Research Notes

This is one of the strongest compatibility oracles in the test suite because it encodes exact NTSTATUS expectations for subtle rename cases. The POSIX semantics section is especially important for implementing Windows behavior over Btrfs inode/link semantics, since it checks delete-pending state, accessible link counts, total link counts, and renamed/orphaned link visibility.

## Open FIXMEs In File

The file notes missing coverage for security descriptor changes after cross-directory moves, inability to rename the root directory, and several newer `FILE_RENAME_*` storage reserve/pin-state flags.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/rename.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/reparse.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/reparse.cpp

## Purpose

`reparse.cpp` tests WinBtrfs handling of reparse points: symbolic links, mount points, Microsoft-owned generic tags, third-party GUID tags, directory reparse points, alternate-stream reparse points, privilege requirements, tag/GUID conflict rules, and query/open behavior with and without `FILE_OPEN_REPARSE_POINT`.

## Main Helpers

- `set_symlink(...)`: constructs `REPARSE_DATA_BUFFER` with `IO_REPARSE_TAG_SYMLINK`.
- `set_mount_point(...)`: constructs mount point reparse data with null-terminated substitute and print names.
- `set_ms_reparse_point(...)`: sets Microsoft-style generic reparse data without GUID.
- `set_reparse_point_guid(...)`: sets non-Microsoft generic reparse data with `REPARSE_GUID_DATA_BUFFER`.
- `query_reparse_point(...)` and `query_reparse_point_guid(...)`: issue `FSCTL_GET_REPARSE_POINT`.
- `delete_reparse_point(...)` and `delete_reparse_point_guid(...)`: issue `FSCTL_DELETE_REPARSE_POINT`.
- `check_reparse_dirent<T>(...)`: validates directory enumeration name and tag reporting across multiple directory information classes.

## Behavior Covered

The test begins by enabling `SeCreateSymbolicLinkPrivilege`, then creates target/source files and verifies relative symlink behavior. It checks that opening without `FILE_OPEN_REPARSE_POINT` resolves to the target ID, while opening with it returns the link object ID.

It verifies that symlink and mount-point attributes surface through:
- `FILE_BASIC_INFORMATION`
- `FILE_EA_INFORMATION`
- `FILE_STAT_INFORMATION`
- `FILE_STAT_LX_INFORMATION`
- `FILE_ATTRIBUTE_TAG_INFORMATION`
- multiple `NtQueryDirectoryFile` directory information classes

Deletion behavior is tested for wrong tags, correct tags, repeated delete attempts, and querying after deletion. Tag mismatch and `STATUS_NOT_A_REPARSE_POINT` are explicitly asserted.

The symlink section covers overwrite semantics: overwriting through a symlink affects the target, while opening with `FILE_OPEN_REPARSE_POINT` overwrites the link object. It also covers invalid reparse data on non-empty files, symlinks with EAs, invalid targets, absolute symlinks, and directory symlinks.

Mount point coverage includes setting on directories, opening through mount points, preserving directory attributes, resolving child paths, rejecting mount points on files, rejecting mount points on non-empty directories unless tag semantics permit it, and tag mismatch when changing an existing mount point to symlink.

Generic reparse tags are split into Microsoft-owned and GUID-backed non-Microsoft forms. The tests verify set/query/update/delete behavior, required GUID use for non-Microsoft tags, conflict statuses for wrong GUIDs, tag mismatch for changed tags, and open failures without `FILE_OPEN_REPARSE_POINT` when the tag is not handled.

Directory reparse points are tested for both Microsoft and GUID tags. A special fake Microsoft directory tag with the directory bit set is allowed on a non-empty directory and can be opened without `FILE_OPEN_REPARSE_POINT`, documenting the “D bit” behavior.

The end of the file validates access requirements. Setting symlinks without sufficient handle access fails, both `FILE_WRITE_ATTRIBUTES` and `FILE_WRITE_DATA` paths are accepted in specific cases, symlink creation fails without `SeCreateSymbolicLinkPrivilege`, while mount points and generic reparse tags do not require that symlink privilege.

Alternate data streams receive dedicated reparse coverage: streams can receive symlink, Microsoft generic, and GUID generic tags; mount points on streams are rejected as not directories; and opening base file/stream without `FILE_OPEN_REPARSE_POINT` reports unhandled tags as expected.

## Integration Points

This file relies on `create_file`, `query_information`, `query_dir`, `set_basic_information`, `write_file_wait`, `write_ea`, `adjust_token_privileges`, and `disable_token_privileges` from the shared test harness.

## Research Notes

This file is an important map of Windows reparse compatibility requirements for WinBtrfs. The test matrix distinguishes target resolution from reparse-object access, Microsoft tags from GUID tags, file reparse points from directory reparse points, and privilege checks from ordinary access-mask checks.

## Open FIXME In File

The file ends with a missing coverage note for `FSCTL_SET_REPARSE_POINT_EX`.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/reparse.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/security.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/security.cpp

## Purpose

`security.cpp` tests Windows security descriptor behavior on WinBtrfs: access-mask reporting, DACL/SACL/label storage, owner and group operations, privilege-gated security changes, inherited ACE behavior, mandatory integrity labels, traverse checks, and denied security queries/updates.

## Main Helpers

- `create_file_sd(...)`: wraps `NtCreateFile` with an explicit security descriptor.
- `create_file_with_acl(...)`: creates a security descriptor with one `ACCESS_ALLOWED_ACE` for Everyone.
- `set_dacl(...)`: sets a DACL on an existing handle.
- `get_acl(...)`: queries DACL, SACL, or label ACLs and validates returned self-relative security descriptor layout.
- `sid_to_string(...)` and `compare_sid(...)`: SID formatting and comparison helpers.
- `set_owner(...)`, `get_owner(...)`, `set_group(...)`, `get_group(...)`: owner/group operations.
- `set_audit(...)`: writes a system audit ACE.
- `set_mandatory_access(...)`: writes a mandatory label ACE.
- `duplicate_token(...)`, `adjust_token_level(...)`, `set_thread_token(...)`: token setup for impersonation/integrity tests.

## Behavior Covered

The first section checks `FILE_ACCESS_INFORMATION` for handles opened with `GENERIC_READ`, `GENERIC_WRITE`, and `GENERIC_EXECUTE`, asserting exact expanded access masks.

DACL coverage creates and modifies ACLs containing Everyone ACEs, then re-queries and validates ACE type, flags, mask, and SID bytes. It includes maximum access masks and explicitly empty or restricted DACLs.

Owner and group tests show privilege boundaries. Setting an arbitrary owner fails without `SeRestorePrivilege`, while setting group succeeds in the tested path. After enabling `SeRestorePrivilege`, setting/querying owner succeeds.

SACL coverage validates `ACCESS_SYSTEM_SECURITY` failure without `SeSecurityPrivilege`, then enables the privilege, opens the file, writes an audit ACE, and verifies that SACL persists after privilege changes.

Mandatory integrity label coverage writes a high-integrity `SYSTEM_MANDATORY_LABEL_NO_WRITE_UP` label, then impersonates a duplicated medium-integrity token. The test confirms write access is denied and `MAXIMUM_ALLOWED` excludes write access while still allowing read/delete-related rights.

Creation-time security descriptor tests create a file with an explicit DACL and verify that the handle’s granted access remains the requested `READ_CONTROL`, while the stored DACL grants `FILE_READ_DATA` to Everyone. Creating a file with another user as owner is expected to fail with `STATUS_INVALID_OWNER`.

Inheritance coverage creates directories with `OBJECT_INHERIT_ACE` and `OBJECT_INHERIT_ACE | CONTAINER_INHERIT_ACE`, then verifies inherited ACE flags on child files and directories, including `INHERIT_ONLY_ACE` behavior for container inheritance.

Traverse behavior is explicitly tested. A directory missing `FILE_TRAVERSE` denies child creation. Adding `FILE_TRAVERSE` allows it. Removing `FILE_TRAVERSE` again still allows child creation after enabling `SeChangeNotifyPrivilege`, documenting the bypass-traverse-checking privilege.

The final section opens a file with only `FILE_READ_ATTRIBUTES` and verifies that owner, group, DACL, SACL, label queries and all corresponding set operations fail with `STATUS_ACCESS_DENIED`.

## Integration Points

This file uses shared harness primitives `create_file`, `query_information`, `exp_status`, `adjust_token_privileges`, and `disable_token_privileges`. It also exports `set_dacl`, which is reused by rename tests for destination permission scenarios.

## Research Notes

`security.cpp` is both a security descriptor serialization test and an access-check compatibility test. It is important for any WinBtrfs code touching Windows ACL persistence, owner/group translation, privilege checks, integrity labels, or inherited ACE propagation.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/security.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/streams.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/streams.cpp

## Purpose

`streams.cpp` tests alternate data stream behavior in WinBtrfs. It covers default stream reporting, named stream creation and deletion, streams on directories, stream data I/O, stream renames, conversion between default and named streams, stream naming rules, reserved Btrfs-backed stream names, and case-insensitive stream lookup.

## Main Helper

- `query_streams(HANDLE h)`: repeatedly calls `NtQueryInformationFile(..., FileStreamInformation)`, grows the buffer on `STATUS_BUFFER_OVERFLOW`, and returns copied `FILE_STREAM_INFORMATION` records.

## Behavior Covered

The initial tests create a base file and verify it reports one `::$DATA` stream with zero size/allocation and `FILE_STANDARD_INFORMATION_EX.AlternateStream == false`. Creating `stream1:stream` is expected to use the same file ID as the base file and set `AlternateStream == true`.

The file checks that creating a stream on a nonexistent base path creates the base file. It rejects stream creation with `FILE_DIRECTORY_FILE`, tests directory streams separately, and confirms directory default stream reporting uses an empty stream name rather than `::$DATA`.

Data-path coverage writes to a named stream, reads it back, validates stream size/allocation reporting, calls zero-data operations, truncates via end-of-file, and confirms resulting bytes and metadata.

Disposition coverage distinguishes deleting a stream from deleting the base file. Deleting `stream6:stream` leaves `stream6` visible, while deleting `stream7` removes the base file and its stream. Stream create/open/open-if/overwrite/overwrite-if/supersede dispositions are all exercised.

Rename coverage is detailed. Renaming a stream using a full path is invalid, while a relative stream name such as `:stream2` succeeds. Renaming a named stream to `::$DATA` requires replacement and converts it back to the default stream. Directory stream conversion to `::$DATA` is rejected. A base file can be renamed to a named stream, making the handle report `AlternateStream == true`.

The file validates `::$DATA` and `:$DATA` suffix handling, including case-insensitive `$data`. It also tests opening named streams with explicit `$DATA` type suffixes.

Name validation covers long stream names, emoji names, long UTF-8 emoji sequences, malformed UTF-16 surrogate sequences, unusual characters, and WinBtrfs-reserved stream names such as `DOSATTRIB`, `reparse`, `EA`, and `casesensitive`. As in rename tests, some expected statuses depend on `fstype == fs_type::ntfs`.

The final case confirms case-insensitive lookup across both base filename and stream name by creating `stream16:stream` and opening `STREAM16:STREAM`.

## Integration Points

This file uses shared helpers from `test.cpp` and `test.h`: `create_file`, `query_information`, `write_file`, `write_file_wait`, `read_file`, `read_file_wait`, `set_zero_data`, `set_end_of_file`, `set_disposition_information`, `set_rename_information`, `query_dir`, and global `fstype`.

## Research Notes

This file documents the WinBtrfs mapping between Windows alternate data streams and Btrfs extended metadata/storage. Reserved stream names are particularly important because they collide with internal WinBtrfs metadata streams that NTFS would otherwise allow.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/streams.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/supersede.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/supersede.cpp

## Purpose

`supersede.cpp` is a focused test for `FILE_SUPERSEDE` create disposition behavior.

## Main Entrypoint

- `test_supersede(const u16string& dir)`

## Behavior Covered

The test first creates a file using `FILE_SUPERSEDE` with `FILE_ATTRIBUTE_READONLY` and verifies that the resulting attributes include both `FILE_ATTRIBUTE_READONLY` and `FILE_ATTRIBUTE_ARCHIVE`.

It then supersedes an already open file while share modes allow read/write/delete sharing, expecting `FILE_SUPERSEDED`. After closing, it supersedes again with no special attributes and verifies that the archive bit remains.

Attribute clearing is tested for hidden and system files. Superseding while clearing `FILE_ATTRIBUTE_HIDDEN` or `FILE_ATTRIBUTE_SYSTEM` is expected to fail with `STATUS_ACCESS_DENIED`.

Directory supersede behavior is intentionally rejected: creating a directory with `FILE_SUPERSEDE | FILE_DIRECTORY_FILE` should return `STATUS_INVALID_PARAMETER`.

The final case validates case behavior. A file created as `supersede2` is superseded through path `SUPERSEDE2`, but `FileNameInformation` is expected to still end with `\supersede2`, documenting case-preserving behavior for supersede on an existing file.

## Integration Points

Uses shared harness helpers `create_file`, `query_information`, `query_file_name_information`, `exp_status`, and `formatted_error`.

## Research Notes

This small file isolates disposition semantics that overlap with overwrite and rename tests but are cleaner here: attribute inheritance/reset, hidden/system protection, directory invalidity, and case preservation.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/supersede.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/test.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/test.cpp

## Purpose

`test.cpp` is the shared executable harness for the WinBtrfs filesystem behavior tests. It provides low-level NT wrappers, result reporting, filesystem detection, test dispatch, temporary test directory setup, and process-token privilege control.

## Main Facilities

- Global `enum fs_type fstype`: records detected filesystem type as unknown, NTFS, or Btrfs.
- `create_file(...)`: wraps `NtCreateFile`, verifies returned `iosb.Information`, and returns `unique_handle`.
- `query_all_information(...)`: two-step `FileAllInformation` query with dynamic name buffer sizing.
- `query_information<T>(...)`: template mapping C++ result types to `FILE_INFORMATION_CLASS`, with explicit instantiations.
- `query_dir<T>(...)`: template wrapper for `NtQueryDirectoryFile` across multiple directory information classes.
- `test(...)`: runs one test lambda, catches exceptions, prints PASS/FAIL, and updates counters.
- `exp_status(...)`: asserts that a callable throws the expected NTSTATUS, or succeeds when expected status is `STATUS_SUCCESS`.
- `query_file_name_information(...)`: dynamic `FileNameInformation` or `FileNormalizedNameInformation` query.
- `disable_token_privileges(...)`: disables all privileges in the supplied token.
- `u16string_to_string(...)`: converts UTF-16 test names/messages for output.
- `do_tests(...)`: dispatches named tests or `all`.
- `fs_driver_path(...)`: uses `FileFsDriverPathInformation` to detect whether NTFS or WinBtrfs is in the stack.
- `get_driver_path(...)`, `get_version(...)`, `driver_string(...)`: report driver binary and version.
- `wmain(...)`: command-line entrypoint.

## Test Dispatch

`do_tests` opens the process token with adjustment/query/duplicate rights, disables privileges, then dispatches the suite by name. Registered tests include create, supersede, overwrite, open-by-ID, I/O, mmap, rename, rename_ex, delete, links, oplocks, case sensitivity, reparse, streams, EA, fileinfo, and security.

For each selected test group it prints `Running test <name>`, resets per-group counters, invokes the function, and prints `Passed X/Y`. For `all`, it also prints a total summary.

## Directory and Filesystem Setup

`wmain` accepts either `<dir>` or `<test> <dir>`, strips trailing backslashes, converts the path to an NT `\??\...` path, appends a timestamp child directory, and creates that directory as the test root.

Filesystem type detection avoids `FileFsAttributeInformation` and instead checks whether `\FileSystem\NTFS` or `\Driver\btrfs` appears in the driver path for the test root. The result controls conditional expectations in files such as `rename.cpp` and `streams.cpp`.

## Query Helper Details

`query_dir<T>` supports `FILE_DIRECTORY_INFORMATION`, `FILE_BOTH_DIR_INFORMATION`, `FILE_FULL_DIR_INFORMATION`, ID variants, extended ID variants, `FILE_NAMES_INFORMATION`, and `FILE_REPARSE_POINT_INFORMATION`. It aligns the query buffer to 8 bytes, handles `STATUS_BUFFER_OVERFLOW` for variable-length directory records, and copies each returned record into stable `varbuf<T>` storage.

`query_information<T>` maps many file information types used across the test suite, including stat, LX stat, attribute tag, compression, network open, standard link, file ID, and standard information extended aliases.

## Research Notes

This harness defines the contract used by all listed test files. Its strict `iosb.Information` checks, exact NTSTATUS assertions, and filesystem-type conditional behavior make the suite useful as a compatibility oracle rather than a loose smoke test.

## Open FIXMEs In File

The harness notes future coverage for synchronous I/O access requirements, opening with `RootDirectory`, directory querying variants, notifications, IOCTL/FSCTL coverage, volume information, volume labels, locking, object IDs, IO completions, share access, reflinks, subvolumes, snapshots, send/receive, and Linux/Windows concept mapping.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/test.cpp -->