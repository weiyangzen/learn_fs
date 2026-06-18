# sources/distributed-fs/ceph-client/tools/perf/util/data.c

## Purpose

`data.c` implements perf's `perf_data` file abstraction for reading and writing `perf.data` as a regular file, pipe, or directory layout. It handles opening, closing, directory member files, backup rotation, read/write/seek wrappers, output switching, kcore side paths, and perf magic detection.

## Important APIs, Types, and Functions

Public APIs include `perf_data__open()`, `perf_data__close()`, `perf_data__read()`, `perf_data__write()`, `perf_data__seek()`, `perf_data_file__write()`, `perf_data_file__seek()`, `perf_data__switch()`, `perf_data__create_dir()`, `perf_data__open_dir()`, `perf_data__close_dir()`, `perf_data__size()`, `perf_data__make_kcore_dir()`, `perf_data__kallsyms_name()`, `perf_data__guest_kallsyms_name()`, `has_kcore_dir()`, and `is_perf_data()`.

## Control Flow

Opening first detects stdin/stdout pipe use, defaults a missing path to `perf.data`, rotates an existing writable file to `.old`, detects directory inputs in read mode, then opens either the directory header file or a single regular file. Directory creation builds `data.N` files and raises `RLIMIT_NOFILE` on `EMFILE`. Directory opening scans regular `data.*` members. Read/write/seek dispatch through stdio for pipes or file-descriptor helpers for regular files. Switching renames current output and optionally reopens the original path at a requested position.

## State and Persistence Behavior

Persistent effects include creating/truncating perf data files, creating perf data directories, rotating existing output to `.old`, deleting old backups via `rm_rf_perf_data()`, creating `kcore_dir`, and renaming switched outputs. Runtime state is stored in `struct perf_data` and nested `perf_data_file` descriptors, file sizes, directory version, and directory file arrays.

## Dependencies and Integration Points

The file depends on POSIX file APIs, perf header magic checks, resource-limit helpers, debug printing, `rm_rf_perf_data()`, and `readn`/`writen`. It is used broadly by perf record, report, inject, archive, data convert, and auxtrace readers through `perf_data__fd()`.

## Risks and Edge Cases

Pipe detection must not accidentally close standard streams incorrectly. Directory layouts require a `DIR_FORMAT` version and at least one `data.*` file. Existing output rotation can fail on unknown files in `.old`. Ownership checks reject files not owned by root or the effective user unless forced. `has_kcore_dir()` uses prefix matching for `kcore_dir`, so callers should not treat it as an exact path validator. Output switching returns a file descriptor even after rename warnings, so callers must inspect errors carefully.

## Test Signals

Tests should cover read/write regular files, stdin/stdout pipes, empty file rejection, ownership force behavior, output backup rotation, directory create/open/size/close, `RLIMIT_NOFILE` retry behavior, output switching with `at_exit` true and false, kcore kallsyms path discovery, guest kallsyms path discovery, and magic detection on valid and invalid files.
