# sources/distributed-fs/ceph-client/tools/perf/util/strbuf.h

## Purpose

`strbuf.h` defines the growable buffer API and invariants used by perf utility code.

## Important APIs, Types, and Functions

It declares `strbuf_slopbuf`, `struct strbuf { alloc, len, buf }`, `STRBUF_INIT`, lifecycle functions, `strbuf_avail()`, `strbuf_grow()`, `strbuf_setlen()`, append helpers, formatted append, and `strbuf_read()`.

## Control Flow and Data Flow

Callers initialize or statically create a buffer, grow or append into it, optionally manipulate the available tail directly, then set the length. The buffer is always NUL-terminated, even when used for byte data.

## State and Persistence Behavior

The object owns its allocated buffer unless the caller detaches it. An empty object points at `strbuf_slopbuf`. `strbuf_setlen()` forces allocation when called on an unallocated buffer.

## Dependencies and Integration Points

The header depends on assert, stdarg, stddef, string, Linux compiler attributes, and sys/types. It is a generic helper used by sort/help and other string-building code.

## Risks and Edge Cases

The comments say `buf` is malloced, but the implementation uses a static slop buffer for empty state; callers must follow the API and not free `buf` directly. Direct tail writes require a later valid `strbuf_setlen()`.

## Test Signals

Compile coverage and API-level buffer append/grow/detach tests validate the contract.
