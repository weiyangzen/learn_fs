# sources/distributed-fs/ceph-client/fs/squashfs/page_actor.c

## Purpose

`page_actor.c` abstracts decompressor output destinations. It supports output to linear intermediate buffers and direct output to page-cache pages, including handling missing pages with optional temporary buffers for streaming decompressors.

## Important APIs, Types, and Functions

Public constructors are `squashfs_page_actor_init()` and `squashfs_page_actor_init_special()`. Internal operations are cache-mode `cache_first_page()`, `cache_next_page()`, `cache_finish_page()` and direct-mode `direct_first_page()`, `direct_next_page()`, `direct_finish_page()` via `handle_next_page()`.

## Control Flow

Intermediate-buffer actors simply return successive buffer pointers. Direct actors track expected page index and returned page count; when a page is missing they either return a temporary buffer if the backend requires one or an error pointer. Direct next/finish unmap any locally mapped page.

## State and Persistence Behavior

Actor state is temporary for one decompression/read. It tracks page arrays or buffer arrays, current mapping address, last real page, expected output length, page index, and whether a temporary buffer is allowed.

## Dependencies and Integration Points

Used by `block.c`, `cache.c`, `file_direct.c`, `file.c` readahead, compression wrappers, and decompressor setup option reading. It depends on backend `alloc_buffer` semantics.

## Risks and Edge Cases

Callers must not sleep between actor page mapping calls and finish. Direct actor gap handling is subtle: non-streaming wrappers may tolerate skipped pages, streaming wrappers need a temporary page. Failure to unmap local mappings would break highmem/local-map rules.

## Test Signals

Direct and cached file modes, readahead with partially missing pages, highmem/local kmap debug, and every compression backend because wrappers consume actor pages differently.
