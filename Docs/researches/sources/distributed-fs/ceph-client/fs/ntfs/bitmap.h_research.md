# sources/distributed-fs/ceph-client/fs/ntfs/bitmap.h

## Purpose

`bitmap.h` declares NTFS bitmap operations and provides inline convenience wrappers for setting or clearing bitmap ranges and individual bits.

## Important APIs, Types, And Functions

- `ntfs_trim_fs()` exposes filesystem discard over free clusters.
- `__ntfs_bitmap_set_bits_in_run()` is the implementation entry point that also supports internal rollback mode.
- `ntfs_bitmap_set_bits_in_run()` calls the implementation with rollback disabled.
- `ntfs_bitmap_set_run()` and `ntfs_bitmap_clear_run()` set or clear a range.
- `ntfs_bitmap_set_bit()` and `ntfs_bitmap_clear_bit()` mutate a single bit.

## Control Flow And Usage

Callers use the inline wrappers for ordinary bitmap changes and never pass rollback mode directly. Range helpers are thin enough that all validation and folio mutation happen in `bitmap.c`.

## State And Persistence Behavior

The header has no state. The declared operations mutate bitmap inode page cache and, for the volume bitmap, associated free-space state. Persistence is through dirty folio writeback.

## Dependencies And Integration Points

It includes Linux `fs.h` for `struct inode` and `volume.h` for `struct ntfs_volume`. It is used by allocation/freeing paths and fstrim support.

## Risks And Edge Cases

The inline wrappers do not validate count or bit positions; callers must rely on the implementation's validation. Single-bit helpers pass `count = 1`, avoiding the zero-count underflow risk in the implementation.

## Test Signals

Build tests should verify wrapper declarations match the implementation. Functional coverage should be driven through allocator paths, direct bitmap range mutation tests, and fstrim tests.
