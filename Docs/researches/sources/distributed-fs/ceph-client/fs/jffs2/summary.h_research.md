# sources/distributed-fs/ceph-client/fs/jffs2/summary.h

## Purpose

`summary.h` defines the on-flash and in-memory summary formats, block-state constants shared between summary and scan code, summary sizing macros, and the summary API surface. It also provides stub macros when `CONFIG_JFFS2_SUMMARY` is disabled.

## Important APIs, Types, And Functions

The file defines block state constants `BLK_STATE_ALLFF`, `BLK_STATE_CLEAN`, `BLK_STATE_PARTDIRTY`, `BLK_STATE_CLEANMARKER`, `BLK_STATE_ALLDIRTY`, and `BLK_STATE_BADBLOCK`. `MAX_SUMMARY_SIZE` limits summary serialization to 64 KiB. `JFFS2_SUMMARY_NOSUM_SIZE` is the disabled sentinel.

On-flash structs include `jffs2_sum_inode_flash`, `jffs2_sum_dirent_flash`, `jffs2_sum_xattr_flash`, `jffs2_sum_xref_flash`, and `jffs2_sum_marker`. In-memory equivalents add linked-list `next` pointers and are combined by `union jffs2_sum_mem`. `struct jffs2_summary` is stored in `struct jffs2_sb_info` and tracks collected entry size/count/list/padding and the serialization buffer.

When enabled, the header declares the summary lifecycle, collection, scanning, and writing functions implemented in `summary.c`. When disabled, it maps the same names to no-op or zero-returning macros so callers do not need local `#ifdef`s.

## Control Flow

The compile-time switch is the central control flow. With summary support, scan, write, and nodemgmt paths actively collect and emit summaries. Without it, `jffs2_sum_active()` is zero and all collection, movement, writing, and scanning calls become inert.

## State And Persistence Behavior

The on-flash structs are packed because their exact byte layout is persisted. Offsets in summary entries are relative to the eraseblock start. `jffs2_sum_marker` at the end of a summarized block stores the offset and magic used by the scanner to locate the summary node. In-memory structs mirror persisted fields but add list linkage for collection before serialization.

## Dependencies And Integration Points

The header depends on Linux `uio` for `struct kvec` declarations and `linux/jffs2.h` for raw node and endian-wrapped integer types. It is included by scan, nodemgmt, writev, and summary implementation files.

## Risks And Edge Cases

Layout compatibility is critical. Any change to packed summary structs affects on-flash format and mount compatibility. Variable-length dirent names make `JFFS2_SUMMARY_DIRENT_SIZE(x)` sensitive to exact name length. Stub macro signatures must stay aligned with real functions to avoid configuration-specific build or behavior drift.

## Test Signals

Build tests should cover summary enabled and disabled. Format tests should assert expected struct sizes and serialized entry lengths, including dirent variable-length entries. Mount tests should verify marker offset interpretation, block-state constants, and no-op behavior when summary is disabled.
