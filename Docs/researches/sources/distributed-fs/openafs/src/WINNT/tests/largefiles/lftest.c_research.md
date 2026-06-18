# sources/distributed-fs/openafs/src/WINNT/tests/largefiles/lftest.c

## Purpose

`lftest.c` is a Windows large-file smoke test for AFS-mounted paths. It writes a fixed test string at several offsets spaced just under 1 GiB apart, flushes the AFS volume through `fs.exe flushvolume`, reopens the file, and verifies the strings can be read back from the same 64-bit offsets.

## Important APIs, Types, and Functions

- Uses Win32 file APIs: `CreateFile`, `SetCurrentDirectory`, `SetFilePointerEx`, `WriteFile`, `ReadFile`, `LockFile`, `UnlockFile`, and `CloseHandle`.
- `teststr` is the expected string payload.
- `test_write(HANDLE, LARGE_INTEGER)` locks 4096 bytes at an offset, seeks, writes `teststr` plus terminator, unlocks, and reports failures.
- `test_read(HANDLE, LARGE_INTEGER)` locks/seeks/reads at the same offset, prints the read data, compares to `teststr`, and unlocks.
- `main()` opens `largefile.test`, writes seven offsets, runs `fs.exe flushvolume <path>`, reopens, and reads the offsets.

## Control Flow

The program requires one path argument, changes into that directory, opens or creates `largefile.test` with read/write sharing, random access, and write-through attributes, then iterates `i = 0..6` with `offset = i * (0x40000000 - 4)`. After writes, it closes the handle, shells out to flush the AFS volume for the provided path, reopens the file, and repeats the same offset sequence for reads and comparison.

## State and Persistence

The test creates or modifies `largefile.test` in the target directory and leaves it in place. It also changes the process current directory. No cleanup removes the test file.

## Dependencies and Integration Points

The program is Windows-only and expects `fs.exe` from OpenAFS to be on `PATH`. It is meant to run against an AFS path or another filesystem being checked for sparse/large-file offset correctness and locking behavior.

## Risks and Edge Cases

- Return values from `test_write()` and `test_read()` are ignored in `main()`, so the process can still exit zero after individual failures.
- `sprintf(cmdline, "fs.exe flushvolume %s", argv[1])` does not quote the path and can fail or be unsafe with spaces/metacharacters.
- The file is opened with `OPEN_ALWAYS`, so stale content can remain outside tested offsets.
- Lock length is only 4096 bytes while payload is short; this is adequate for the test string but not a full region integrity check.

## Test Signals

Console output reports each successful write/read and prints detailed Win32 `GetLastError()` diagnostics on lock, seek, read, write, or unlock failures. A string comparison failure is the core correctness signal after flush/reopen.
