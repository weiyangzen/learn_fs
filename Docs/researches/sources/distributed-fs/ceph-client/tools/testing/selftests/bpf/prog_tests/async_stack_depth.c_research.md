# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/async_stack_depth.c

Purpose: minimal wrapper that runs all subtests embedded in the `async_stack_depth` skeleton/BPF object.

Important APIs/types/functions: includes `async_stack_depth.skel.h` and calls `RUN_TESTS(async_stack_depth)` from `test_progs.h`.

Control flow: the macro handles skeleton open/load/attach/run behavior according to the generated selftest conventions.

State and persistence behavior: no local state; all state belongs to the skeleton and BPF programs.

Dependencies and integration points: generated skeleton and test harness macro support.

Risks: this file provides no additional userspace assertions, so meaningful coverage is entirely in the BPF-side test object and harness macro expansion.

Test signals: pass/fail/skip signals are produced by `RUN_TESTS`.
