# sources/distributed-fs/ceph/src/rgw/rgw_string.h

## Purpose
`rgw_string.h` provides small reusable string utilities for case-insensitive comparisons, numeric conversion, `string_view` conversion, efficient concatenation/join, and wildcard matching.

## Important APIs, Types, and Functions
`ltstr_nocase` and `stringcasecmp()` wrap `strcasecmp()`/`strncasecmp()`. `stringtoll()`, `stringtoull()`, `stringtol()`, and `stringtoul()` parse decimal strings and reject trailing characters. `sview2cstr()` copies a `string_view` into a small-vector-backed C string. `sarrlen()` returns string literal length at compile time. `string_size()`, `string_cat_reserve()`, and `string_join_reserve()` precompute lengths to avoid repeated reallocations. `MATCH_CASE_INSENSITIVE` and `match_wildcards()` expose glob matching.

## Control Flow
Most helpers are inline templates. Concatenation and join compute total reserve size through `detail::sum()` and `string_traits`, then append `string_view` arguments in order.

## State and Persistence Behavior
No persistent state. Output strings and vectors are caller-owned.

## Dependencies and Integration Points
The header uses Boost small_vector, C string conversion functions, and RGW callers across auth, policy, and request parsing. `match_wildcards()` is implemented in `rgw_string.cc`.

## Risks
The integer parsers only check max sentinels, not `errno`, so some underflow/overflow and range truncation cases can slip through. `stringcasecmp(s1, ofs, size, s2)` trusts offsets. `string_traits<const char*>` calls `strlen()` and cannot handle null pointers. Literal size specialization throws on unterminated arrays.

## Test Signals
Test numeric conversions at boundaries and invalid suffixes, string literals and mutable arrays, char delimiter joins, `string_view` with embedded nulls, and wildcard matching through the exported declaration.
