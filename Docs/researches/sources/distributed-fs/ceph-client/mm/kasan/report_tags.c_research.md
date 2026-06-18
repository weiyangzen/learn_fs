# sources/distributed-fs/ceph-client/mm/kasan/report_tags.c

## Purpose

`report_tags.c` contains shared report classification for tag-based KASAN modes. Because tag mismatch reports do not carry generic shadow poison classes, this file infers alloc/free history from the KASAN stack ring to classify slab out-of-bounds versus slab use-after-free.

## Important APIs, Types, and Functions

The important entry point is `kasan_complete_mode_report_info()`. Internal helper `get_common_bug_type()` detects wrapped access ranges and otherwise returns `invalid-access`. The file uses the external `stack_ring` with `struct kasan_stack_ring_entry`, `entry->ptr`, `entry->track`, `entry->is_free`, and `entry->size`.

## Control Flow

Common reporting calls `kasan_complete_mode_report_info()` after it has found the cache and object. If no object is available and no fixed bug type was set, the file assigns a common bug type. Otherwise it takes `stack_ring.lock`, reads the current ring position, and walks backward up to `stack_ring.size` entries. Matching requires the untagged object pointer, the pointer tag, and object size to match. The first matching free entry sets `free_track` and suggests `slab-use-after-free`; the first matching alloc entry sets `alloc_track` and suggests `slab-out-of-bounds`. Duplicate alloc or free entries stop the inference.

## State and Persistence Behavior

This file only reads the stack ring. The ring is a bounded in-memory history, so evidence can be overwritten, stale, or absent. It fills transient fields in `struct kasan_report_info`; it does not persist reports.

## Dependencies and Integration Points

It depends on `tags.c` for stack-ring allocation and writes, on common report handling in `report.c`, and on tag helpers for pointer reset/tag comparison. The lock pairing is important: `tags.c` uses the same ring lock to avoid seeing partially written entries.

## Risks and Edge Cases

The classification is explicitly best-effort. Another object with the same tag can reuse the address, entries can be overwritten, and a ring with disabled stack collection provides no alloc/free evidence. In such cases reports fall back to `invalid-access` or the fixed bug type supplied by common code.

## Test Signals

Signals include tag-mode KASAN reports that include alloc and free stack traces when stack collection is enabled, fallback classification when `kasan.stacktrace=off`, and ring-size stress tests that overwrite old evidence.
