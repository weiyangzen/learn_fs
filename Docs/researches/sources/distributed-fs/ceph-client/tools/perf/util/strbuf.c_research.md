# sources/distributed-fs/ceph-client/tools/perf/util/strbuf.c

## Purpose

`strbuf.c` implements a growable, NUL-terminated byte/string buffer for perf utilities. It is modeled on Git-style strbuf behavior and supports appending bytes, chars, formatted text, and file-descriptor contents.

## Important APIs, Types, and Functions

Public functions are `strbuf_init()`, `strbuf_release()`, `strbuf_detach()`, `strbuf_grow()`, `strbuf_addch()`, `strbuf_add()`, `strbuf_addf()`, and `strbuf_read()`. The file defines the global `strbuf_slopbuf[1]` used by empty buffers.

## Control Flow and Data Flow

Initialization points empty buffers at `strbuf_slopbuf`. `strbuf_grow()` computes required allocation as `len + extra + 1`, detects overflow, uses `alloc_nr()` growth when larger, and avoids reallocating the static slop buffer. Add functions grow first, copy/write data, and update length through `strbuf_setlen()`. Formatted appends try `vsnprintf()` once, grow to the reported size if needed, then retry with a saved `va_list`. `strbuf_read()` grows by a hint or 8192 bytes, reads until EOF, grows between chunks, and rolls back to the old length or releases if the first read fails.

## State and Persistence Behavior

All state is caller-owned in `struct strbuf`. `strbuf_detach()` transfers the allocated buffer to the caller and reinitializes the shell. `strbuf_release()` frees only allocated buffers and returns the object to empty state.

## Dependencies and Integration Points

It depends on `cache.h` for `alloc_nr()`, Linux string/kernel helpers, zalloc, debug logging, stdio, errno, and `read()`. It is used wherever perf builds dynamic strings, including sort help generation.

## Risks and Edge Cases

`strbuf_setlen()` asserts `len < alloc`; callers that manually grow then set length must respect available capacity. `strbuf_grow()` returns `-E2BIG` on overflow. A broken `vsnprintf()` can be detected and reported as `-EINVAL`. Partial read failure rolls back previous content, which is useful but may surprise callers expecting partial data.

## Test Signals

Tests should cover empty initialization, growth from slop, formatted append requiring retry, detach ownership, release idempotence, binary data append, overflow guards, and `strbuf_read()` success and rollback behavior.
