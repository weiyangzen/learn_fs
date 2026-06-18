# sources/distributed-fs/ceph-client/lib/cmdline.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cmdline.c` implements common parsers for kernel command-line and module-option strings. It handles integer lists/ranges, memory-size suffixes, option presence, and argument tokenization.

## Important APIs, Types, and Functions

Exported functions are `get_option`, `get_options`, `memparse`, and `next_arg`; `parse_option_str` is a visible helper without an export in this file. Internal helper `get_range()` expands `M-N` integer ranges.

## Control Flow

`get_option()` parses an optional leading negative sign and integer with `simple_strtoull()`, stores it when requested, and returns a code indicating no value, value, value plus comma, or a range hyphen. `get_options()` loops over comma-separated values and positive ranges, optionally in validation mode when `nints == 0`, storing count in `ints[0]`. `memparse()` parses a number and shifts by 10 for K through E suffixes. `parse_option_str()` scans comma-separated tokens for exact option names. `next_arg()` splits a mutable string into parameter and optional value, tracks quotes, removes quote wrappers, converts the delimiter to NUL, and skips trailing spaces.

## State and Persistence Behavior

There is no global state. Several APIs mutate caller-provided strings by inserting NUL terminators and advancing pointers.

## Dependencies and Integration Points

The file depends on kernel string, ctype, and simple numeric parsing helpers. It is integrated broadly with boot parameter handling, module parameter parsing, and drivers that parse compact numeric lists.

## Risks and Edge Cases

`get_options()` assumes `ints` is usable even in validation mode because it writes `ints[0]`. Negative ranges are not supported as ranges. `memparse()` can overflow silently through left shifts. `next_arg()` does not support escaping quotes, so embedded quotes can terminate parsing unexpectedly.

## Test Signals

Useful tests cover empty input, negative single values, comma lists, ranges, validation mode, full-array truncation, memory suffixes through exabytes, option-name boundary matching, quoted arguments with spaces, value quotes, and mutable string NUL placement.

## Read Coverage

Source read size: 275 lines, 5983 bytes.
