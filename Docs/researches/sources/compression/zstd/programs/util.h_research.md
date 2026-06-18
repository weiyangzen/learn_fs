# sources/compression/zstd/programs/util.h

## Purpose

This header declares zstd CLI portability utilities for console policy, filesystem metadata, file-list management, directory mirroring, sleeps/priority, and CPU core counts.

## Important APIs, Types, and Functions

It defines `UTIL_fseek`, `UTIL_sleep`, `UTIL_sleepMilli`, `SET_REALTIME_PRIORITY`, `UTIL_STATIC`, `stat_t`, `mode_t`, `PATH_SEP`, and `STRDUP`. It declares confirmation and console helpers, stat/set-stat/chmod/utime wrappers, file-type checks, size helpers, `UTIL_HumanReadableSize_t`, extension and directory-mirroring functions, `FileNamesTable`, file-list create/merge/expand/search APIs, and `UTIL_countCores` plus physical/logical wrappers.

## Control Flow, State, and Persistence

The header describes ownership conventions: some file tables own buffers, read-only tables borrow names, merge consumes inputs, and `UTIL_refFilename` requires preallocated capacity. Actual persistence is limited to process-local utility globals in `util.c`.

## Dependencies and Integration Points

It includes `platform.h`, C/POSIX headers, zstd `mem.h`, and conditionally `libgen.h`. It is a core include for CLI, file I/O, tests, and benchmark support.

## Risks and Test Signals

Consumers must respect table ownership and borrowed-name lifetimes. Platform macros can alter ABI-visible typedefs. Tests should compile across Windows/POSIX, validate file table ownership/freeing, exercise `UTIL_HAS_CREATEFILELIST` and `UTIL_HAS_MIRRORFILELIST`, and verify path separator behavior.
