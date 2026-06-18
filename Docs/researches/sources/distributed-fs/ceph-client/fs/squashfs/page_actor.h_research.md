# sources/distributed-fs/ceph-client/fs/squashfs/page_actor.h

## Purpose

This header defines `struct squashfs_page_actor` and inline helpers for the decompressor output abstraction.

## Important APIs, Types, and Functions

Key fields include the buffer/page union, `pageaddr`, `tmp_buffer`, operation function pointers, `last_page`, page counts, output length, `alloc_buffer`, `returned_pages`, and `next_index`. Public helpers are `squashfs_page_actor_init()`, `squashfs_page_actor_init_special()`, `squashfs_page_actor_free()`, `squashfs_first_page()`, `squashfs_next_page()`, `squashfs_finish_page()`, and `squashfs_actor_nobuff()`.

## Control Flow

Inline helpers dispatch through function pointers set by the constructors. `squashfs_page_actor_free()` frees temporary storage and returns the last real page only if every supplied page was consumed; otherwise it returns an error pointer.

## State and Persistence Behavior

The header defines temporary per-read actor state. It does not own persistent filesystem state.

## Dependencies and Integration Points

It is included by low-level I/O, decompressor wrappers, direct file reads, and cache code. The return convention of `squashfs_page_actor_free()` is used by direct read and readahead code to validate output completion.

## Risks and Edge Cases

The union requires callers to use the constructor matching the destination type. `squashfs_actor_nobuff()` disables fallback buffering and is used for raw copy paths; misuse can turn skipped pages into errors.

## Test Signals

Build coverage, direct/cached read tests, page-gap tests, and backend-specific decompression tests validate the contract.
