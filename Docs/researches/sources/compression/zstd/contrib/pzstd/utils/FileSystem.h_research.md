<!-- BEGIN_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/FileSystem.h -->
# sources/compression/zstd/contrib/pzstd/utils/FileSystem.h

## Purpose
`FileSystem.h` provides a small portability wrapper for file status, size, regular-file, and directory checks.

## Important APIs, Types, And Functions
It aliases platform `stat`/`_stat64` as `file_status` and defines `status`, `file_size`, `is_regular_file`, and `is_directory` overloads using `StringPiece`.

## Control Flow
Functions call the platform stat routine, populate `std::error_code` on failure, and query mode bits to classify files.

## State And Persistence
No persistent state is owned. Calls read filesystem metadata only.

## Dependencies And Integration Points
`Pzstd.cpp` uses these helpers for input-size estimation and directory rejection. `Options.cpp` uses zstd `util.h` for broader traversal, so this file is focused on lightweight checks.

## Risks
Stat behavior differs across Windows/POSIX, especially symlinks and large files. Callers must inspect `error_code`.

## Test Signals
Indirect pzstd file-processing tests exercise size/directory behavior; direct unit tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/compression/zstd/contrib/pzstd/utils/FileSystem.h -->
