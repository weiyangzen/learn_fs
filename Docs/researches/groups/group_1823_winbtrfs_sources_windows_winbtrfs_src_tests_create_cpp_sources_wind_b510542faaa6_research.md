# Group Research: group_1823_winbtrfs_sources_windows_winbtrfs_src_tests_create_cpp_sources_wind_b510542faaa6

Scope confirmed against `Docs/research_subset_a.md`. All six listed WinBtrfs test source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/create.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/create.cpp

## Purpose

`create.cpp` is a WinBtrfs native-NT create/open semantics test suite. It validates file and directory creation, create disposition results, case-insensitive name collisions, file information returned after creation, directory enumeration records, share-access rules, path/name validation, UTF-16/UTF-8 edge cases, and `FILE_OPEN_BY_FILE_ID` / object-ID behavior.

## Main Helpers

- `query_object_basic_information()` wraps `NtQueryObject(ObjectBasicInformation)` and checks returned length.
- `check_dir_entry<T>()` verifies directory information records across many `FILE_*_DIR_INFORMATION` variants.
- `open_by_id<T>()` calls `NtCreateFile` with `FILE_OPEN_BY_FILE_ID` for 64-bit IDs and 16-byte object IDs.
- `create_or_get_object_id()` issues `FSCTL_CREATE_OR_GET_OBJECT_ID`.

## `test_create()` Coverage

- Creates a file and checks duplicate/case-only duplicate creation returns `STATUS_OBJECT_NAME_COLLISION`.
- Verifies initial metadata through basic, standard, name, access, mode, alignment, position, attribute-tag, compression, EA, internal, network-open, standard-link, stat, stat-LX, ID, and all-information queries.
- Confirms normalized-name query requires `SeChangeNotifyPrivilege`.
- Checks directory enumeration output for the file across standard, both, full, ID, extended-ID, and names information classes.
- Tests file/directory option interactions:
  - `FILE_NON_DIRECTORY_FILE`
  - `FILE_DIRECTORY_FILE`
  - ignored `FILE_ATTRIBUTE_DIRECTORY` for regular files
  - directory opens without explicit directory options.
- Tests attribute normalization for files and directories.
- Tests share-read, share-write, and share-delete compatibility and sharing violations.
- Tests missing paths, child creation under regular files, `FILE_OPEN_IF`, long names, emoji names, Btrfs stricter UTF-8/WTF-16 validation, invalid characters, and NT-API creation of `CON`.

## `test_open_id()` Coverage

- Creates a file, writes random data, records the 64-bit file ID, and verifies directory entry ID.
- Validates open-by-ID failures for missing root directory and wrong file/directory options.
- Opens by ID, reads content, checks filename and hardlinks.
- Verifies rename/delete through an ID-opened handle returns `STATUS_INVALID_PARAMETER`, while hardlink creation succeeds.
- Tests `FILE_DELETE_ON_CLOSE`, create dispositions, stale IDs, directories by ID, POSIX-deleted orphaned inodes, 16-byte object IDs, and traverse-privilege-sensitive filename queries.

## Important Dependencies

- Test helpers: `create_file`, `query_information`, `query_all_information`, `query_file_name_information`, `query_dir`, `query_links`, `set_link_information`, `set_rename_information`, `set_disposition_information`, `set_disposition_information_ex`, `write_file`, `read_file`.
- NT APIs: `NtCreateFile`, `NtQueryObject`, `NtFsControlFile`, `NtWaitForSingleObject`.

## Notable Edge Cases

- Expected name-validation behavior differs between NTFS and Btrfs for oversized UTF-8 names and invalid surrogate sequences.
- Open-by-ID handles are intentionally restricted for rename/delete.
- Filename queries from ID-opened handles remain privilege-sensitive.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/create.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/cs.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/cs.cpp

## Purpose

`cs.cpp` tests per-directory case-sensitivity semantics exposed through `FileCaseSensitiveInformation`.

## Main Helpers

- `set_case_sensitive()` calls `NtSetInformationFile(FileCaseSensitiveInformation)`.
- `create_file_cs()` wraps `NtCreateFile` without `OBJ_CASE_INSENSITIVE`.

## Test Coverage

- Creates `csdir`, sets `FILE_CS_FLAG_CASE_SENSITIVE_DIR`, and queries it back.
- Creates lowercase `cs1`, verifies exact-case enumeration succeeds and wrong-case enumeration/open/overwrite fails.
- Creates uppercase `CS1` as a distinct file and verifies open/overwrite/supersede dispositions target that inode by file ID.
- Verifies subdirectories inherit case sensitivity.
- Verifies setting case sensitivity on a regular file fails with `STATUS_INVALID_PARAMETER`.
- Tests ACL requirements: setting the flag requires `FILE_ADD_FILE | FILE_ADD_SUBDIRECTORY | FILE_DELETE_CHILD`.
- Tests setting/clearing on a non-empty directory, and clearing failure with `STATUS_CASE_DIFFERING_NAMES_IN_DIR` once names differ only by case.
- Tests normal-directory opens without `OBJ_CASE_INSENSITIVE`.
- Documents that alternate stream names are still opened case-insensitively in this path.

## Important Dependencies

- `FileCaseSensitiveInformation`
- `create_file`, `query_information`, `query_dir`, `set_dacl`, `exp_status`

## Notable Edge Cases

- Windows policy may need case-sensitive directory support enabled.
- Stream-name matching does not follow normal case-sensitive file-name behavior.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/cs.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/delete.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/delete.cpp

## Purpose

`delete.cpp` tests Windows delete disposition semantics for classic and extended delete APIs.

## Main Helpers

- `set_disposition_information()` sets `FileDispositionInformation`.
- `set_disposition_information_ex()` sets `FileDispositionInformationEx`.

## `test_delete()` Coverage

- Deletes files and directories with classic disposition.
- Verifies directory entries remain visible while handles are open, `DeletePending` updates, accessible links drop to zero, and entries disappear on close.
- Confirms non-empty directories return `STATUS_DIRECTORY_NOT_EMPTY` until children are closed.
- Tests clearing delete disposition, multiple handles, `DELETE` access enforcement, alternate data streams, `FILE_DELETE_ON_CLOSE`, readonly file rejection, and delete-on-close behavior for directories.

## `test_delete_ex()` Coverage

- Repeats core behavior with `FILE_DISPOSITION_DELETE`.
- Uses `FILE_DISPOSITION_DO_NOT_DELETE` to clear pending delete.
- Tests mapped image-section deletion with `FILE_DISPOSITION_FORCE_IMAGE_SECTION_CHECK`.
- Tests readonly deletion with `FILE_DISPOSITION_IGNORE_READONLY_ATTRIBUTE`.
- Tests POSIX semantics:
  - link count drops to zero;
  - original entry disappears when the deleting handle closes;
  - remaining handle becomes orphaned and no longer reports the original name/link parent.
- Tests `FILE_DISPOSITION_ON_CLOSE` cancellation and unsupported setting of delete-on-close on a handle not opened that way.

## Important Dependencies

- `FileDispositionInformation`, `FileDispositionInformationEx`
- `FILE_STANDARD_INFORMATION`, `FILE_STANDARD_LINK_INFORMATION`
- Helpers: `create_file`, `query_dir`, `query_information`, `query_file_name_information`, `query_links`, `set_link_information`, `write_file`, `create_section`, `pe_image`

## Notable Edge Cases

- Delete-pending visibility and link counts are tested separately.
- Delete-on-close is not immediately equivalent to delete-pending.
- POSIX delete produces orphaned naming behavior on still-open handles.
- Mapped image deletion depends on link count and force-image-section checking.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/delete.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/ea.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/ea.cpp

## Purpose

`ea.cpp` tests extended attribute support through `NtSetEaFile`, `NtQueryEaFile`, and create-time EA buffers.

## Main Helpers

- `ea_size()` computes aligned `FILE_FULL_EA_INFORMATION` size.
- `write_ea()` writes one EA, optionally with `FILE_NEED_EA`.
- `write_eas()` writes chained multiple EA entries.
- `read_ea()` reads all EAs.
- `create_file_ea()` passes EAs to `NtCreateFile`.
- `check_ea_dirent<T>()` checks directory-entry `EaSize`.
- `read_eas()` performs filtered/single-entry/indexed EA reads.

## Test Coverage

- New files with no EAs return `STATUS_NO_EAS_ON_FILE`.
- EA names are normalized uppercase and matched case-insensitively.
- Adds, replaces, and deletes EAs by zero-length value.
- Verifies `FILE_EA_INFORMATION`, `FILE_ALL_INFORMATION`, and multiple directory-information classes report expected aligned EA size.
- Writes multiple EAs in one chained buffer.
- Creates a file with create-time EAs.
- Verifies directories can carry EAs.
- Tests `FILE_NEED_EA` and `FILE_NO_EA_KNOWLEDGE` denial.
- Checks `FILE_WRITE_EA` and `FILE_READ_EA` access enforcement.
- Tests filtered reads, single-entry iteration, restart behavior, explicit EA index, `STATUS_NO_MORE_EAS`, and missing-EA zero-length return.
- Verifies volume handles reject EA read/write with `STATUS_INVALID_PARAMETER`.

## Important Dependencies

- `NtSetEaFile`, `NtQueryEaFile`, `NtCreateFile`
- `FILE_FULL_EA_INFORMATION`, `FILE_GET_EA_INFORMATION`, `FILE_EA_INFORMATION`, `FILE_ALL_INFORMATION`

## Notable Edge Cases

- Directory-entry `EaSize` is checked after closing handles because the test notes it may update on close.
- Requesting a non-existent EA returns a zero-length EA record for the requested name.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/ea.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/fileinfo.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/fileinfo.cpp

## Purpose

`fileinfo.cpp` tests `FileBasicInformation` timestamp and attribute set/query behavior.

## Main Helper

- `set_basic_information()` calls `NtSetInformationFile(FileBasicInformation)` and checks zero `IO_STATUS_BLOCK.Information`.

## Test Coverage

- Creates `fileinfo1`, captures initial `FILE_BASIC_INFORMATION`, and expects archive attributes.
- Setting all times/attributes to zero leaves existing values unchanged.
- Writes update last-write and change time while preserving creation time.
- Tests timestamp sentinels:
  - `-1` suppresses updates;
  - `-2` re-enables updates;
  - explicit timestamp values can be set.
- Checks access enforcement:
  - querying without `FILE_READ_ATTRIBUTES` returns `STATUS_ACCESS_DENIED`;
  - setting without `FILE_WRITE_ATTRIBUTES` returns `STATUS_ACCESS_DENIED`.
- Tests file attribute normalization:
  - hidden, normal, readonly;
  - directory attribute on a file fails;
  - reparse-point and sparse-file attributes are ignored.
- Tests directory attribute normalization:
  - directory is always retained;
  - hidden/readonly combine with directory;
  - reparse-point and sparse-file are ignored.

## Important Dependencies

- `NtSetInformationFile(FileBasicInformation)`
- `create_file`, `query_information`, `write_file`, `exp_status`
- `NtDelayExecution` to make timestamp changes observable.

## Notable Edge Cases

- Last access time is mostly ignored due to Windows policy variability.
- File and directory attribute normalization differ.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/fileinfo.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/io.cpp -->
# File Research: sources/windows/winbtrfs/src/tests/io.cpp

## Purpose

`io.cpp` tests native NT file I/O semantics: reads, writes, file positions, EOF, allocation, valid data length, unbuffered alignment, append-only writes, pending I/O completion, and zeroing ranges.

## Main Helpers

- `adjust_token_privileges()` wraps `NtAdjustPrivilegesToken`.
- `set_allocation()` sets `FileAllocationInformation`.
- `random_data()` generates random test buffers.
- `write_file()` / `read_file()` wrap direct synchronous I/O.
- `create_event()`, `write_file_wait()`, and `read_file_wait()` handle event-backed pending I/O.
- `set_position()` sets `FilePositionInformation`.
- `set_valid_data_length()` sets `FileValidDataLengthInformation`.
- `set_end_of_file()` sets `FileEndOfFileInformation`.
- `set_zero_data()` issues `FSCTL_SET_ZERO_DATA`.

## Shared `write_check()` Coverage

- Writes random data and verifies file pointer, allocation, EOF, compressed size, and full-content reads.
- EOF and beyond-EOF reads return `STATUS_END_OF_FILE`.
- Negative positions are rejected.
- Reads crossing EOF return only available data.
- Extending EOF creates zero-filled regions.
- Valid data length requires privilege, cannot be zero, and cannot exceed EOF.
- Truncating EOF preserves the prefix.
- In unbuffered mode, short reads/writes and unaligned positions fail.

## `test_io()` Coverage

- Enables `SeManageVolumePrivilege` for VDL tests.
- Runs normal I/O checks with 4096-byte and 200-byte sizes.
- Verifies VDL without privilege returns `STATUS_PRIVILEGE_NOT_HELD`.
- Tests allocation sizing, create-time preallocation, and directory rejection/ignore behavior.
- Tests synchronized file-pointer special offsets:
  - explicit offset;
  - `FILE_USE_FILE_POINTER_POSITION`;
  - `FILE_WRITE_TO_END_OF_FILE`;
  - invalid read with write-to-end marker.
- Tests non-synchronized handles requiring explicit offsets and rejecting file-pointer-position markers.
- Tests `FILE_APPEND_DATA` appends regardless of explicit offset.
- Tests `FILE_NO_INTERMEDIATE_BUFFERING` alignment requirements.
- Tests `FSCTL_SET_ZERO_DATA` for byte-range and sector-range zeroing.

## Important Dependencies

- `NtReadFile`, `NtWriteFile`, `NtCreateEvent`, `NtWaitForSingleObject`, `NtFsControlFile`
- `NtSetInformationFile` for allocation, position, VDL, and EOF.
- `SE_MANAGE_VOLUME_PRIVILEGE`
- `FILE_SYNCHRONOUS_IO_NONALERT`, `FILE_NO_INTERMEDIATE_BUFFERING`, `FILE_APPEND_DATA`, `FILE_USE_FILE_POINTER_POSITION`, `FILE_WRITE_TO_END_OF_FILE`

## Notable Edge Cases

- Synchronous and non-synchronous handles have different file-pointer rules.
- Append-only access overrides explicit write offsets.
- Unbuffered I/O enforces alignment, but EOF may temporarily be non-sector-sized.
- Setting allocation size to zero is expected to truncate EOF to zero.
- DASD I/O is listed as a FIXME and is not covered.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/io.cpp -->