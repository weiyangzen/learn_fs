# sources/compression/zstd/programs/util.c

## Purpose

This file implements zstd CLI utility behavior: user confirmation, stat/chmod/chown/utime wrappers, file-type checks, console fakes for tests, file size and human-readable formatting, file-list loading/merging/expansion, mirrored output directory creation, and CPU core counting.

## Important APIs, Types, and Functions

Public functions mirror `util.h`. File metadata APIs include `UTIL_stat`, `UTIL_fstat`, `UTIL_setFileStat`, `UTIL_setFDStat`, `UTIL_utime`, `UTIL_chmod`, and file-type predicates. File-list APIs include `UTIL_createFileNamesTable_fromFileList`, `UTIL_allocateFileNamesTable`, `UTIL_mergeFileNamesTable`, `UTIL_expandFNT`, and `UTIL_createExpandedFNT`. Output directory helpers include `UTIL_createMirroredDestDirName` and `UTIL_mirrorSourceFilesDirectories`. Core counting is implemented per Windows, Apple, Linux, FreeBSD, other BSD/Cygwin, and fallback.

## Control Flow, State, and Persistence

Metadata wrappers optionally trace nested calls via global `g_traceFileStat` and `g_traceDepth`. File-list loading stats the list path, permits regular files, FIFOs, and `/dev/fd` or `/proc/self/fd` style paths, reads up to 50 MB, converts newlines to NUL separators, and assembles an owned `FileNamesTable`. Directory expansion recursively walks platform directory APIs and optionally skips symlinks. Mirrored output rejects path components equal to `..`, trims leading root/current-directory markers, creates unique parent directories, and copies source directory modes where possible. Core counts are cached in static variables.

## Dependencies and Integration Points

It depends on `platform.h`, libc filesystem APIs, Windows APIs, POSIX directory APIs, and zstd common `U64`. `zstdcli.c`, `fileio`, test binaries, benchmark tools, and CLI shell tests rely on it.

## Risks and Test Signals

Risks include platform-specific stat semantics, permission/owner update failures hidden as counts, file-list memory limits, pathname edge cases in mirrored output, symlink recursion policy, and static core-count caching that can conflate logical and physical calls if called in a different order on some platforms. Tests should cover file lists from files/FIFOs/fd paths, symlink filtering, `..` rejection, output-dir mirroring, mtime/permissions preservation, console fake flags, block/FIFO detection, and core-count fallbacks.
