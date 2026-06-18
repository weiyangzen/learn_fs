# sources/distributed-fs/ceph-client/fs/btrfs/accessors.c

## Purpose
Provides out-of-line Btrfs extent-buffer set/get primitives for 8-, 16-, 32-, and 64-bit little-endian fields, plus a node-key reader. These functions are the low-level implementation behind many typed metadata accessors declared in `accessors.h`.

## Important APIs, Types, And Functions
The macro `DEFINE_BTRFS_SETGET_BITS(bits)` generates `btrfs_get_8/16/32/64()` and `btrfs_set_8/16/32/64()`. `report_setget_bounds()` emits a Btrfs warning when a requested metadata member exceeds the extent-buffer length. `memcpy_split_src()` copies a value that spans two folios. `btrfs_node_key()` reads a `struct btrfs_disk_key` from a node pointer slot.

## Control Flow
Each generated getter computes `member_offset = (unsigned long)ptr + off`, maps that logical extent-buffer offset to a folio index and offset-in-folio, checks bounds against `eb->len`, then either reads the value directly with `get_unaligned_le*()` or assembles bytes from the current and next folio when the field crosses a folio boundary. Setters perform the same offset and bounds logic, then write directly with `put_unaligned_le*()` or split bytes across adjacent folios.

`btrfs_node_key()` uses `btrfs_node_key_ptr_offset()` from the header to find the node pointer slot and `read_eb_member()` to copy the embedded disk key out of the extent buffer.

## State And Persistence
Getters are read-only. Setters mutate in-memory extent-buffer folios; those changes become persistent only when higher-level Btrfs writeback commits the metadata block. Bounds failures are reported through kernel warnings and return zero/no-op rather than crashing directly.

## Dependencies And Integration Points
This file depends on `extent_io.h` for `struct extent_buffer`, folio layout helpers, and read/write semantics; `fs.h` for filesystem information such as `fs_info`; `messages.h` for `btrfs_warn()`; and `accessors.h` for declarations and higher-level offset macros. It is compiled into Btrfs through the Makefile core object list.

## Risks
These helpers sit on a critical metadata boundary. Bad offset arithmetic, incorrect folio-boundary handling, or missing bounds checks could corrupt on-disk metadata or read stale memory. Returning zero on out-of-bounds reads can mask an upstream corruption path, so warning visibility matters. The split-field path is especially important for metadata block sizes larger than page/folio size.

## Test Signals
Tests should exercise 1-, 2-, 4-, and 8-byte fields at normal offsets, exactly at folio boundaries, and spanning folio boundaries; out-of-bounds reads/writes; little-endian conversion; and node-key extraction. Btrfs extent-buffer KUnit/sanity tests and tree-checker failures are strong signals for regressions here.
