# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/fexit_test.c

## Purpose
Tests fexit attach behavior for normal and many-argument target functions.

## Important APIs, types, and functions
Uses `fexit_test.lskel.h`, `fexit_many_args.skel.h`, shared `fexit_test_common()`, generated attach helpers, and BSS result/counter checks.

## Control flow and state
`fexit_test()` runs the lightweight skeleton path; `fexit_many_args()` runs the many-argument path. Both load/attach, trigger target execution, validate BSS state, and destroy skeletons.

## Dependencies and integration points
Depends on fexit trampoline support and generated target tracing programs. Integrated via `test_fexit_test()` subtests.

## Risks and test signals
Risk is trampoline ABI or target prototype drift. Passing signals are expected counts and argument capture values in BSS.
