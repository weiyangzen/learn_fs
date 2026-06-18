# sources/distributed-fs/ceph-client/tools/perf/util/srccode.c

## Purpose

`srccode.c` caches source files and returns raw source-line slices for annotation or source-code display. It avoids repeatedly opening and scanning the same files by mmaping source content and indexing line starts.

## Important APIs, Types, and Functions

The private `struct srcfile` stores hash/list nodes, filename, line pointer array, mmap pointer, line count, and map length. Public functions are `find_sourceline()` and `srccode_state_free()`. Helpers include `countlines()`, `fill_lines()`, `free_srcfile()`, and `find_srcfile()`.

## Control Flow and Data Flow

`find_sourceline(fn, line, lenp)` calls `find_srcfile()`. The cache lookup hashes by filename and moves hits to the front of `srcfile_list`. On a miss, the cache prunes least-recently-used entries while file count or mapped bytes exceed `MAXSRCFILES` or `MAXSRCCACHE`, opens and stats the file, mmap maps a page-rounded size, counts lines, allocates a line-start array, fills it, links the entry into both hash and LRU lists, and returns the selected line start plus byte length up to newline.

## State and Persistence Behavior

State is process-local: a 64-bucket filename hash, an LRU list, total mapped size, and source-file count. Mappings persist until pruned or process exit. `find_sourceline()` returns a non-NUL-terminated pointer into an mmap owned by the cache, so callers must copy or print with the returned length. `srccode_state_free()` releases the last `srcfile` string in a caller-owned state object.

## Dependencies and Integration Points

The file depends on Linux lists, hlist hashing, `mmap`, `open`, `fstat`, page size from internal lib support, perf debug logging, and `str_hash()`. It integrates with source annotation paths that need fast repeated line lookup.

## Risks and Edge Cases

If `open()` succeeds but `fstat()` fails, the current code returns without closing the descriptor. Empty files and out-of-range line numbers return `NULL`. `find_sourceline()` computes `p - l` after `memchr()`; the line indexer should ensure a newline or map-end path is valid, but malformed edge cases deserve attention. Returned pointers become invalid after cache pruning. The code is not thread-synchronized.

## Test Signals

Tests should cover empty files, files without a trailing newline, repeated lookup moving entries to the LRU front, cache pruning by count and size, missing files, long lines, and callers honoring the non-NUL-terminated result length.
