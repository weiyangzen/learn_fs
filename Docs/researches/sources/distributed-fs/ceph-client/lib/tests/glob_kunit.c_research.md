
# sources/distributed-fs/ceph-client/lib/tests/glob_kunit.c

## Purpose
`glob_kunit.c` tests `glob_match()` pattern matching. It covers exact strings, empty patterns, character classes, negated classes, ranges, bracket corner cases, `?`, `*`, and multi-asterisk backtracking.

## Important APIs, types, and functions
The central fixture is `struct glob_test_case` with `pat`, `str`, and `expected`. `glob_case_to_desc()` formats parameter descriptions. `KUNIT_ARRAY_PARAM()` generates one KUnit parameter per fixture, and `glob_test_match()` compares `glob_match()` with the expected boolean.

## Control flow
The single parameterized test runs through all fixtures. Early cases validate exact and empty behavior. Middle cases focus on bracket parsing, including `!` negation, ranges, literal `-`, `[` and `]`. Later cases exercise wildcard length constraints and backtracking over repeated `*` segments.

## State and persistence
All state is constant fixture data plus KUnit parameter plumbing. There is no mutable global state.

## Dependencies and integration points
It depends on `<linux/glob.h>`, module metadata, and KUnit. It is built with `CONFIG_GLOB_KUNIT_TEST`.

## Risks and edge cases
The suite is table-driven and easy to extend, but failures in complex backtracking only identify the pattern/string pair, not internal matcher state. It does not cover path separators or locale-specific behavior; it tests the kernel glob semantics directly.

## Test signals
KUnit parameter descriptions include both pattern and string, and failure messages include expected result. Pass means every listed glob fixture matches the encoded semantics.
