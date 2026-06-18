# Group Research: group_1824_winbtrfs_sources_windows_winbtrfs_src_tests_links_cpp_sources_windo_46604c725450

Scope verified against `Docs/research_subset_a.md`: `sources/windows/winbtrfs` is included in subset A. All three listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/links.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/links.cpp

## Purpose

`links.cpp` is the WinBtrfs user-mode integration test coverage for Windows hardlink semantics. It exercises `FileHardLinkInformation`, `FileLinkInformation`, and `FileLinkInformationEx` against real file handles and directory entries, validating the driver's link counts, accessible link counts, delete-pending behavior, replacement rules, security checks, POSIX replacement behavior, and mapped-image protections.

## Key Coverage

- Hardlink creation and enumeration through `NtQueryInformationFile` and `NtSetInformationFile`.
- `FILE_STANDARD_INFORMATION` and `FILE_STANDARD_LINK_INFORMATION` link counts.
- Delete-pending accounting when one hardlink is removed while another remains open.
- Directory, readonly, open-target, invalid-name, nonexistent-path, and ACL denial cases.
- Directory-relative hardlink creation through `RootDirectory`.
- Same-name and case-change behavior.
- `FileLinkInformationEx` replacement, readonly override, and POSIX semantics.
- Mapped `SEC_IMAGE` replacement denial for normal and POSIX hardlink replacement.

## Dependencies

Uses shared test helpers from `test.h`: `create_file`, `query_information`, `query_file_name_information`, `query_dir`, `set_disposition_information`, `set_rename_information`, `set_dacl`, `write_file`, `read_file`, privilege helpers, and assertion wrappers. It also uses `pe_image` and `create_section` from the mmap test support path.

## Research Summary

This file is a dense behavioral specification for WinBtrfs hardlink semantics. It should be read alongside the WinBtrfs file information and namespace mutation code, especially hardlink creation, replacement, delete disposition, hardlink enumeration, ACL checks, and POSIX replacement handling.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/links.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/manifest.xml -->
# File Research: sources/windows/winbtrfs/src/tests/manifest.xml

## Purpose

`manifest.xml` is the Windows application manifest for the WinBtrfs test executable.

## Contents

- Declares assembly identity `btrfs-test`, version `0.0.0.0`.
- Marks compatibility with Windows Vista, 7, 8, 8.1, and 10.
- Sets the active code page to UTF-8.
- Requests `requireAdministrator` execution level with `uiAccess="false"`.

## Research Summary

The manifest supports the test suite’s assumptions: elevated execution, Windows compatibility metadata, and UTF-8 process code page behavior. This matters for privileged filesystem tests, ACL/token operations, low-level NT APIs, and Unicode filename coverage.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/manifest.xml -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/mmap.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/mmap.cpp

## Purpose

`mmap.cpp` is the WinBtrfs user-mode integration test coverage for Windows section objects and memory-mapped file behavior. It validates `NtCreateSection`, `NtMapViewOfSection`, cache coherency, byte-range locks, truncation, deletion, rename/link replacement, and `SEC_IMAGE` image-section restrictions.

## Helper Functions

- `create_section`: wraps `NtCreateSection`.
- `map_view`: wraps `NtMapViewOfSection`, accepting `STATUS_IMAGE_NOT_AT_BASE`.
- `unmap_view`: wraps `NtUnmapViewOfSection`.
- `lock_file`: wraps `NtLockFile`.
- `pe_image`: builds a minimal PE image with one `.data` section for `SEC_IMAGE` tests.

## Key Coverage

- Empty-file section creation fails with `STATUS_MAPPED_FILE_SIZE_ZERO`.
- Directory section creation fails with `STATUS_INVALID_FILE_FOR_SECTION`.
- Oversized section creation fails with `STATUS_SECTION_TOO_BIG`.
- Read-write section creation without write access fails with `STATUS_ACCESS_DENIED`.
- File writes are visible through mappings, and mapping writes are visible through file reads.
- Byte-range locks do not block section creation.
- Extending a mapped file succeeds, but truncation fails with `STATUS_USER_MAPPED_FILE`.
- Delete disposition on mapped files fails with `STATUS_CANNOT_DELETE`.
- Data-mapped files can be replaced by rename or hardlink.
- Image-mapped files cannot be overwritten, renamed over, deleted, or hardlink-replaced.

## Dependencies

Uses shared helpers from `test.h`: file creation, file I/O, EOF/disposition/rename/link setters, random data generation, assertion wrappers, and NTSTATUS exception handling.

## Research Summary

This file is the main WinBtrfs regression suite for Windows Cache Manager and Memory Manager integration. It verifies section creation rules, data coherency, mapped-file truncation protection, delete behavior, namespace replacement rules, and strict handling for mapped executable images.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/mmap.cpp -->