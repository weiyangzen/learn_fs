# sources/distributed-fs/ceph-client/tools/perf/util/srcline.h

## Purpose

`srcline.h` declares the address-to-source-line and inline-frame cache API used by perf symbol, report, and callchain code.

## Important APIs, Types, and Functions

It exposes `srcline_full_filename`, `srcline__unknown`, `SRCLINE_UNKNOWN`, `MAX_INLINE_NEST`, `struct inline_list`, and `struct inline_node`. The API includes `get_srcline()`, `__get_srcline()`, `get_srcline_split()`, `zfree_srcline()`, source-line tree functions, inline tree functions, `dso__parse_addr_inlines()`, `inline_node__delete()`, `inline_list__append()`, `inline_list__append_tail()`, `srcline_from_fileline()`, `new_inline_sym()`, and `addr2line_configure()`.

## Control Flow and Data Flow

Callers resolve an address to a display string or split filename/line, optionally parse inline frames, and cache results in DSO rbtree structures. Tree insert calls transfer ownership to the DSO-side cache.

## State and Persistence Behavior

The header documents ownership: source-line tree insertion and inline tree insertion take ownership. `SRCLINE_UNKNOWN` is a shared sentinel. Inline lists contain symbol pointers and source-line strings with deletion handled by `inline_node__delete()`.

## Dependencies and Integration Points

It depends on Linux list/rbtree/types headers and forward declarations for `dso` and `symbol`. It is a shared contract between address resolution backends, DSO caches, callchain display, and sort keys.

## Risks and Edge Cases

Ownership is the main risk: callers must use `zfree_srcline()` and not normal `free()` for possible sentinel values. Inline fake symbols must be handled through the delete helpers. Address keys must use the same address space convention for insert and lookup.

## Test Signals

Build coverage plus source-line cache and inline-cache lifetime tests should validate the contract.
