# sources/compression/zstd/tests/fuzz/regression_driver.c

## Purpose

`regression_driver.c` is a standalone corpus replay driver for zstd fuzz targets. It reads files from command-line paths, loads each file into memory, and calls the fuzz target's `LLVMFuzzerTestOneInput()` function, allowing deterministic regression testing outside libFuzzer.

## Important APIs And Functions

The only local function is `main()`. It uses `UTIL_createExpandedFNT()` when available to expand file name tables with link following, otherwise `UTIL_createFNT_fromROTable()`. It reads file metadata and contents through `UTIL_getFileSize()`, `UTIL_isRegularFile()`, `fopen()`, `fread()`, and `fclose()`, then invokes `LLVMFuzzerTestOneInput(buffer, fileSize)`.

## Control Flow

The driver constructs a file table from `argv[1..]`, warns on an empty table, and iterates each path. Non-regular files are skipped and cause a nonzero return. Files larger than 128 MiB assert-fail. The read buffer is grown only when the next file is larger than the current buffer, so repeated corpus entries reuse allocation.

After replaying all regular files, it prints a summary showing number of files tested and success/failure, releases the buffer and file table, and returns the accumulated status.

## State And Persistence

State is local to process execution: expanded file table, reusable heap buffer, tested count, and return flag. No corpus mutation or persistent record is written. Fuzz targets may maintain their own static state depending on `STATEFUL_FUZZING`.

## Dependencies And Integration Points

It includes `fuzz.h` for the fuzzer entry declaration, `fuzz_helpers.h` for assertions, and zstd `util.h` for file-list utilities. It is meant to be linked with one fuzz target implementation at a time and used by regression scripts or manual corpus replay.

## Risks And Edge Cases

Path expansion may include files that disappear before replay; the driver treats that as failure but continues. It relies on `UTIL_getFileSize()` being valid for regular files and asserts exact `fread()` length. Very large corpus files are rejected. No partial-read retry logic is present, so unusual filesystems or I/O errors become assertion failures.

## Test Signals

The main signal is successful replay of known crash reproducer files without assertion or sanitizer failures. The final process exit code distinguishes all-regular replay success from skipped/missing/non-regular path failures.
