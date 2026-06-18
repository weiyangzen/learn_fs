
# sources/distributed-fs/ceph-client/lib/tests/cmdline_kunit.c

## Purpose
`cmdline_kunit.c` tests command-line integer parsing helpers from `cmdline.c`, especially malformed tokens, leading/trailing integers, negative signs, separators, and range expansion.

## Important APIs, types, and functions
The suite calls `get_option()`, `get_options()`, `get_random_u8()`, `memchr_inv()`, `sprintf()`, `strlen()`, and KUnit assertions. Static tables pair input strings with expected return codes, pointer offsets, parsed counts, and expanded integer arrays.

## Control flow
`cmdline_do_one_test()` calls `get_option()` on a mutable output pointer and verifies both return code and consumed offset. Three tests compose no-int, leading-int, and trailing-int cases from the same punctuation table. `cmdline_do_one_range_test()` calls `get_options()` twice: once with a result capacity to validate parsed values, then with zero capacity to validate count-only behavior and ensure the data region stays zeroed. `cmdline_test_range()` iterates fixed range strings with expected expansions.

## State and persistence
All buffers are stack-local. Random bytes are used only to vary valid integer prefixes/suffixes; expected behavior depends on token structure, not specific value.

## Dependencies and integration points
It depends on KUnit, kernel string helpers, random helpers, and `get_option()`/`get_options()` implementations. It is built through `CONFIG_CMDLINE_KUNIT_TEST`.

## Risks and edge cases
The tests encode subtle pointer-consumption semantics for bare `-` and malformed negative ranges. Random values improve variety but can make reproducing exact input strings slightly less direct unless logs are added.

## Test signals
Failures report the pattern string and whether parsed count, pointer offset, value expansion, or validation-only behavior diverged.
