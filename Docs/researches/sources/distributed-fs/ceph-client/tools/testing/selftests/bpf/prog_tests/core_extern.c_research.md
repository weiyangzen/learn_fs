# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/core_extern.c

## Purpose
Validates CO-RE external kconfig variable handling, including default kernel config lookup, custom kconfig strings, booleans/tristates/chars/strings/integer parsing, bounds, and expected load failures.

## Important APIs, types, and functions
Uses `test_core_extern.skel.h`, `bpf_object_open_opts.kconfig`, `uname()` plus `KERNEL_VERSION()`, skeleton data section comparison, and table-driven `struct test_case`. Each case carries config text, expected failure flag, and expected `test_core_extern__data`.

## Control flow and state
For each test case, the skeleton is opened with optional custom kconfig, loaded, attached, triggered by `usleep(1)`, and then its data section is compared word-by-word with expected data after filling dynamic kernel version and missing value. State is per-case skeleton data; no external persistence.

## Dependencies and integration points
Depends on libbpf kconfig extern resolution, generated tracepoint program, and kernel version parsing from `uname`. Integrated as `test_core_extern()`.

## Risks and test signals
Parsing edge cases are intentional risk areas. Test signals are load failure for bad configs and exact data-section equality for successful configs.
