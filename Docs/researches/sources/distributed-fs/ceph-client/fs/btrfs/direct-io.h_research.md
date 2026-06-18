# sources/distributed-fs/ceph-client/fs/btrfs/direct-io.h

## Purpose

`direct-io.h` declares the Btrfs direct I/O entry points and bioset lifecycle helpers implemented by `direct-io.c`. It is the narrow interface used by file read/write paths and module/filesystem initialization.

## Important APIs, Types, and Functions

The header forward declares `struct kiocb` and declares `btrfs_init_dio()`, `btrfs_destroy_dio()`, `btrfs_direct_write()`, and `btrfs_direct_read()`.

## Control Flow

There is no executable control flow. The API separates lifecycle setup/teardown of direct-I/O bio private storage from per-I/O read/write entry points.

## State and Persistence Behavior

The header owns no state. The implementation's bioset is initialized and destroyed through the lifecycle functions; reads and writes mutate filesystem state only through the implementation.

## Dependencies and Integration Points

Dependencies are minimal: Linux types and `struct kiocb`. Integration points are Btrfs file operations, iomap direct I/O, ordered extents, and filesystem initialization/cleanup.

## Risks and Edge Cases

Callers must ensure `btrfs_init_dio()` succeeds before direct I/O is available and pair it with `btrfs_destroy_dio()` on teardown. Direct read/write return values include buffered fallback behavior from the implementation, so callers should not assume every accepted request remains direct.

## Test Signals

Compile coverage should catch signature drift. Lifecycle tests should verify bioset initialization failure handling and teardown ordering, while file-operation tests should cover direct read/write fallback and completion behavior.
