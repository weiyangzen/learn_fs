# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fentry_fexit.c

## Purpose
Tests that fentry and fexit lightweight skeletons can be loaded/attached together and observe expected counters.

## Important APIs, types, and functions
Uses `fentry_test.lskel.h` and `fexit_test.lskel.h`. `test_fentry_fexit()` opens/loads/attaches both skeletons and validates combined behavior.

## Control flow and state
State is the two lskel objects, links, and BSS counters. The test triggers target functions indirectly through sleep or skeleton attach behavior and then cleans both skeletons.

## Dependencies and integration points
Depends on BTF-enabled fentry/fexit attach support and generated lightweight skeletons. Integrated as a combined tracing selftest.

## Risks and test signals
Risk is attach target availability. Passing signal is successful load/attach and expected fentry/fexit BSS counts.
