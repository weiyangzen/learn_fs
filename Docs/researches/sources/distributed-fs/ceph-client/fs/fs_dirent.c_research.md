# sources/distributed-fs/ceph-client/fs/fs_dirent.c

## Purpose

`sources/distributed-fs/ceph-client/fs/fs_dirent.c` provides small exported conversion helpers between generic filesystem on-disk file type values, POSIX mode bits, and userspace dirent `DT_*` values. The complete 105-line file was read for this report.

## Important APIs, Types, and Functions

The exported helpers are `fs_ftype_to_dtype()`, `fs_umode_to_ftype()`, and `fs_umode_to_dtype()`. Static lookup tables are `fs_dtype_by_ftype[]` and `fs_ftype_by_dtype[]`.

## Control Flow

`fs_ftype_to_dtype()` bounds-checks the `FT_*` input and returns `DT_UNKNOWN` for invalid values. `fs_umode_to_ftype()` maps mode bits through `S_DT(mode)` into `FT_*`. `fs_umode_to_dtype()` composes those two conversions.

## State and Persistence Behavior

There is no mutable or persistent state. The static tables are compile-time constants used by filesystems that store generic file type values or need to emit directory-entry types.

## Dependencies and Integration Points

The file depends on `linux/fs_dirent.h` definitions for `FT_*` and `DT_*`, and exports GPL symbols for filesystem implementations.

## Risks and Edge Cases

The main risk is table drift if `FT_*`, `DT_*`, or `S_DT()` semantics change. Invalid file types intentionally degrade to unknown rather than failing.

## Test Signals

Unit-style checks for every `FT_*`, every supported `DT_*`, representative `S_IF*` modes, and out-of-range `filetype` values would cover behavior.
