# sources/distributed-fs/ceph-client/tools/perf/util/string.c

## Purpose

`string.c` provides generic string helpers for perf: size parsing, glob and lazy matching, tail comparison, trace-filter expression generation, escaped/quoted token scanning and duplication, hex decoding, and character replacement.

## Important APIs, Types, and Functions

Public data includes `graph_dotted_line` and `dots`. Public functions include `perf_atoll()`, `strglobmatch()`, `strglobmatch_nocase()`, `strlazymatch()`, `strtailcmp()`, `asprintf_expr_inout_ints()` plus wrappers in the header, `asprintf__tp_filter_pids()` declared in the header but not present in this file, `strpbrk_esc()`, `strpbrk_esq()`, `strdup_esc()`, `strdup_esq()`, `hex()`, and `strreplace_chars()`.

## Control Flow and Data Flow

`perf_atoll()` parses decimal sizes with optional byte/K/M/G/T suffixes. Glob matching is recursive with support for `*`, `?`, character classes, ranges, complement, escapes, optional case-insensitivity, and optional whitespace ignoring for lazy matching. Escaped scanning walks to stop characters while skipping single-backslash escapes; quoted scanning extends that to quoted substrings. Duplication helpers remove escape characters and, for quoted strings, remove surrounding quotes while preserving quoted content semantics. `strreplace_chars()` counts target characters, allocates a larger string if needed, and copies replacement chunks.

## State and Persistence Behavior

There is no mutable global state beyond static string constants. Functions returning strings allocate caller-owned memory.

## Dependencies and Integration Points

It depends on Linux kernel/string/ctype helpers and standard allocation. It is used by filter parsing, event expression construction, command parsing, and display helpers.

## Risks and Edge Cases

`perf_atoll()` shifts signed values and can overflow silently for very large inputs. `hex()` assumes alphabetic input is a hex letter and does not reject characters above `F`/`f`. Recursive glob matching can be expensive for pathological patterns with many wildcards. Escape scanning has subtle behavior around double backslashes. `strreplace_chars()` copies one extra byte before replacement and should be covered by tests for adjacent and leading needles.

## Test Signals

Tests should cover suffix parsing and invalid suffixes, glob classes/ranges/escapes/case modes, lazy whitespace matching, tail comparison, in/not-in expression generation, escaped and quoted separators, malformed quotes, hex conversion, and replacement at beginning/middle/end/no match.
