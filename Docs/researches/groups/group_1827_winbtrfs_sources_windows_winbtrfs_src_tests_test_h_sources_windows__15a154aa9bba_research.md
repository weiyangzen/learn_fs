# Group Research: group_1827_winbtrfs_sources_windows_winbtrfs_src_tests_test_h_sources_windows__15a154aa9bba

Scope confirmed against `Docs/research_subset_a.md`. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/test.h -->
# File Research: sources/windows/winbtrfs/src/tests/test.h

## Purpose

`test.h` is the shared header for the WinBtrfs user-mode test executable. It centralizes native Windows API declarations, missing/updated NT structure definitions, test helper types, exception wrappers, and cross-module declarations for the filesystem behavior tests under `src/tests`.

## Platform And API Compatibility Layer

The header includes Win32/NT headers and then fills gaps needed by the tests, especially for MinGW or older SDK declarations:

- Declares native `Nt*` routines used directly by the tests:
  - directory, file read/write, EA query/set, security query/set
  - token privilege/impersonation helpers
  - event, section, memory map, file lock, filesystem control calls
- Defines pseudo-handle macros for current thread/process.
- Adds file information class constants not always present in the compiler headers:
  - `FileIdInformation`, `FileIdExtdDirectoryInformation`, `FileDispositionInformationEx`
  - `FileRenameInformationEx`, `FileLinkInformationEx`, `FileCaseSensitiveInformation`
  - `FileStatInformation`, `FileStatLxInformation`
- Defines constants for Windows filesystem behavior tests:
  - EA need flag, word alignment, privilege IDs
  - rename/link extended flags including POSIX semantics and ignore-readonly behavior
  - disposition extended flags including POSIX delete, delete-on-close, force-image-section-check, ignore-readonly
  - case-sensitive-directory flag
  - special read/write offsets for current file pointer and append-to-EOF

## NT Structure Definitions

The file locally defines many NT structures used by tests so code can compile independently of SDK version:

- Directory/query structures:
  - `FILE_DIRECTORY_INFORMATION`
  - `FILE_FULL_DIR_INFORMATION`
  - `FILE_ID_FULL_DIR_INFORMATION`
  - `FILE_BOTH_DIR_INFORMATION`
  - `FILE_ID_BOTH_DIR_INFORMATION`
  - `FILE_NAMES_INFORMATION`
  - extended ID directory variants with 128-bit IDs and reparse tags
- File metadata structures:
  - `FILE_BASIC_INFORMATION`
  - `FILE_STANDARD_INFORMATION`
  - `FILE_STANDARD_INFORMATION_EX`
  - `FILE_NETWORK_OPEN_INFORMATION`
  - `FILE_STAT_INFORMATION`
  - `FILE_STAT_LX_INFORMATION`
  - `FILE_ID_INFORMATION`
  - `FILE_STANDARD_LINK_INFORMATION`
- Operation payloads:
  - rename/link information, including extended versions
  - disposition, allocation, EOF, valid data length, zero-data
  - object ID, reparse data, compression, case sensitivity
  - hard-link enumeration structures
  - oplock request/response buffers
  - EA query request structure
- Volume/query support:
  - `FS_INFORMATION_CLASS`
  - `FILE_FS_DRIVER_PATH_INFORMATION`
  - `OBJECT_BASIC_INFORMATION`
  - `EVENT_BASIC_INFORMATION`

The `#ifdef _MSC_VER` block backfills definitions normally provided by MinGW-oriented headers or expected differently across toolchains.

## Handle And Error Helpers

- `fs_type` records the detected filesystem under test: `unknown`, `ntfs`, or `btrfs`.
- `handle_closer` closes valid handles with `NtClose`.
- `unique_handle` wraps raw `HANDLE` values in `std::unique_ptr<HANDLE, handle_closer>`.
- `ntstatus_to_string(NTSTATUS)` is a very large switch mapping hundreds of NTSTATUS values to symbolic names, with a hex fallback for unknown values.
- `ntstatus_error` stores an `NTSTATUS` and exposes its symbolic text through `std::exception::what()`.
- `formatted_error` formats arbitrary failure messages using C++20 `std::vformat`.
- `varbuf<T>` wraps variable-length NT output buffers as a `std::vector<uint8_t>` with pointer-style conversions to `T*`.

## Shared Test Utility Declarations

The header declares common helpers implemented in `test.cpp` and other modules:

- File creation and metadata:
  - `create_file`
  - `query_information<T>`
  - `query_all_information`
  - `query_file_name_information`
  - `query_dir<T>`
- Test harness helpers:
  - `test`
  - `exp_status`
  - `disable_token_privileges`
  - `u16string_to_string`
- I/O helpers:
  - `random_data`
  - `write_file`, `read_file`
  - async/wait variants
  - EOF, allocation, valid-data-length, zero-data setters
  - event and privilege adjustment helpers
- Memory mapping:
  - `create_section`
  - `pe_image`
- File operation setters:
  - rename information
  - disposition information and extended disposition
  - link information
  - basic timestamps/attributes
  - DACL setter
  - EA writer

## Test Module Entry Points

`test.h` declares the per-feature test suites implemented by the sibling `.cpp` files:

- create/open-by-ID: `test_create`, `test_open_id`
- supersede and overwrite behavior
- I/O behavior
- mmap/image-section behavior
- rename and extended rename
- delete and extended delete
- hard links and extended link behavior
- oplock variants: level I, II, batch, filter, R, RW, RH, RWH
- case sensitivity
- reparse points
- alternate streams
- extended attributes
- file information classes
- security/DACL behavior

All observed sibling test modules include this header, making it the main compile-time contract for the test executable.

## Notable Details

- The file is test infrastructure, not driver/runtime filesystem code.
- It deliberately uses native NT APIs rather than higher-level Win32 wrappers so tests can validate exact kernel-visible filesystem semantics.
- The large `ntstatus_to_string` table is diagnostic glue: it improves assertion and exception messages when filesystem operations return unexpected statuses.
- `unique_handle` treats only `INVALID_HANDLE_VALUE` as a no-op in the deleter. Null handles are not specially ignored by the deleter, so callers must avoid storing null where closing it would be inappropriate.
- Many variable-length NT structures use trailing one-element arrays; callers must size buffers correctly.
- The declarations show the test suite exercises Windows-specific filesystem semantics that are important for WinBtrfs compatibility, including EAs, reparse points, hard links, alternate streams, POSIX-style rename/delete/link flags, case-sensitive directories, oplocks, memory-mapped sections, security descriptors, and Linux stat metadata.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/test.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/tests/test.rc.in -->
# File Research: sources/windows/winbtrfs/src/tests/test.rc.in

## Purpose

`test.rc.in` is the CMake-configured Windows resource script template for the WinBtrfs test executable. It embeds version metadata and the executable manifest into `test.exe`.

## Main Contents

- Includes `winresrc.h` behind `APSTUDIO_READONLY_SYMBOLS`.
- Selects English (United Kingdom) resources:
  - `LANG_ENGLISH`
  - `SUBLANG_ENGLISH_UK`
  - code page `1252`
- Defines a `VS_VERSION_INFO` block with:
  - `FILEVERSION` and `PRODUCTVERSION` from `@PROJECT_VERSION_MAJOR@`, `@PROJECT_VERSION_MINOR@`, and `@PROJECT_VERSION_PATCH@`
  - debug flag set when `_DEBUG` is defined
  - `FILEOS 0x4L`, `FILETYPE 0x1L`, executable subtype zero
- Defines string metadata:
  - file description: `WinBtrfs test program`
  - internal name: `test`
  - original filename: `test.exe`
  - product name: `WinBtrfs`
  - copyright: Mark Harmstone 2021-24
- Defines `VarFileInfo` translation `0x809, 1200`.
- Embeds manifest resource `1 RT_MANIFEST "@CMAKE_CURRENT_SOURCE_DIR@/src/tests/manifest.xml"`.

## Integration

CMake substitutes the `@...@` project version and source-directory variables before compiling the resource. The resulting resource identifies the test binary consistently with WinBtrfs versioning and ensures the test executable carries its manifest.

## Notable Details

- This file contains no test logic.
- It is Windows-build metadata only.
- The manifest path is source-tree-relative through CMake substitution, so builds depend on `src/tests/manifest.xml` being present.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/tests/test.rc.in -->