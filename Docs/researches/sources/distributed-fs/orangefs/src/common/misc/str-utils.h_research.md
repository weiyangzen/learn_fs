# sources/distributed-fs/orangefs/src/common/misc/str-utils.h

## Purpose

`str-utils.h` declares the shared OrangeFS string, path, handle-range, and tokenization helpers implemented in `str-utils.c`. It is the lightweight public contract consumed by config parsing, path manipulation, and option parsing code.

## Important APIs

The header declares path helpers (`PINT_merged_path_len`, `PINT_merge_paths`, `PINT_is_dot_dir`, slash cleanup, segment count and extraction, base-dir and prefix removal), handle-range helpers (`PINT_parse_handle_ranges`, `PINT_merge_handle_range_strs`), comma-list helpers (`PINT_split_string_list`, `PINT_free_string_list`), fallback libc declarations guarded by `HAVE_STRNLEN` and `HAVE_STRSTR`, and `PINT_split_keyvals` for comma-separated `key:value` strings.

## Control flow and ownership contract

Functions fall into three ownership categories. In-place mutators operate on caller-owned mutable strings. Buffer writers require caller-supplied output buffers and max lengths. Allocators such as `PINT_get_next_path`, `PINT_split_string_list`, `PINT_merge_handle_range_strs`, and `PINT_split_keyvals` return heap memory that callers must free with `free()` or `PINT_free_string_list()` as appropriate.

`PINT_string_next_segment()` has an iterator-style contract: callers initialize `*inout_segp` to NULL and provide persistent `opaquep` storage across calls. It may temporarily alter the input path while iteration proceeds.

## State and persistence behavior

The header exposes no global state and no persistence. State is either caller-provided iterator state, caller-owned buffers, or returned heap allocations.

## Dependencies and integration points

The header depends on `pvfs2-internal.h` and `pvfs2-types.h` for PVFS limits, error codes, and handle extent types. It is included by server config code and other common path handling code.

## Risks and edge cases

- The `inline` declarations for `PINT_merged_path_len` and `PINT_is_dot_dir` rely on compiler/linker behavior matching the definitions in the C file.
- Several APIs require mutable path strings despite accepting names that may look read-only. Passing string literals to in-place or iterator functions is unsafe.
- Allocating APIs use different freeing conventions, so call sites need clear ownership review.

## Test signals

Header-level coverage should compile consumers in configurations with and without `HAVE_STRNLEN` and `HAVE_STRSTR`. API tests should verify ownership expectations, mutable input requirements, and compatibility with PVFS path and handle types.
