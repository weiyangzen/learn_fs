# sources/distributed-fs/ceph-client/tools/perf/util/data.h

## Purpose

`data.h` declares the `perf_data` abstraction used to access perf data streams, files, and directory-backed captures.

## Important APIs, Types, and Functions

`enum perf_data_mode` selects read or write. `enum perf_dir_version` distinguishes single-file and directory formats. `struct perf_data_file` wraps a path plus either fd or `FILE *`, size, and stdio mode. `struct perf_data` stores top-level path, backing file, pipe/dir/force/update flags, mode, and directory member files. Inline helpers expose fd, mode, pipe/dir/single-file status. The header declares open/close/read/write/seek/switch, directory, size, kcore, kallsyms, and magic-check helpers.

## Control Flow

The header only provides inline dispatchers. `perf_data_file__fd()` selects `fileno(fptr)` for stdio-backed pipes or the raw fd otherwise. Mode and layout predicates guide implementation and callers.

## State and Persistence Behavior

The structures are mutable runtime state representing open descriptors, file sizes, directory contents, and user-requested behavior. Persistent filesystem changes are performed by `data.c`, not this header.

## Dependencies and Integration Points

Dependencies are standard I/O, booleans, unistd, and Linux integer types. The API is consumed by most perf commands and by auxtrace/data-conversion code that needs file descriptors and seek/read/write wrappers.

## Risks and Edge Cases

Callers must initialize mode and path/flags consistently before opening. `perf_data__fd()` assumes an open file. Directory state must be closed with `perf_data__close_dir()` or `perf_data__close()`. `perf_data__is_single_file()` is based on directory version, so version initialization matters for directory captures.

## Test Signals

Compile tests should catch ABI changes. Runtime tests should verify inline helpers against pipe, regular file, and directory objects; stdio-backed pipes; in-place update opens; and directory version transitions.
