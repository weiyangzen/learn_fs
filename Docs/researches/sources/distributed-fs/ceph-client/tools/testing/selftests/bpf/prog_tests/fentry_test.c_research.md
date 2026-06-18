# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fentry_test.c

## Purpose
Tests fentry attach behavior for normal and many-argument target functions.

## Important APIs, types, and functions
Uses `fentry_test.lskel.h`, `fentry_many_args.skel.h`, shared `fentry_test_common()`, generated attach helpers, and BSS counters/results.

## Control flow and state
`fentry_test()` runs the lightweight skeleton path; `fentry_many_args()` runs the many-arguments skeleton path. Both load/attach, trigger target functions, and check BSS values. State is skeleton BSS and links.

## Dependencies and integration points
Depends on fentry trampoline support and generated target/trace programs. Integrated via `test_fentry_test()` subtests.

## Risks and test signals
Risk is function prototype or trampoline ABI drift. Passing signal is expected counts and argument values in BSS after triggers.
