# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tp_btf_nullable.c

## Purpose
Runs BTF tracepoint nullable argument tests supplied by the `test_tp_btf_nullable` skeleton.

## APIs, Types, and Functions
Only public entry point is `test_tp_btf_nullable()`, which calls `RUN_TESTS(test_tp_btf_nullable)` when the BPF test module is available.

## Control Flow, State, and Persistence
The test checks `env.has_testmod`, skips if missing, and delegates all subtest execution to the skeleton test runner. There is no user-space state beyond the environment flag.

## Dependencies and Integration
Depends on `test_progs.h`, `test_tp_btf_nullable.skel.h`, and the kernel BPF test module that exposes the required tracepoints and BTF signatures.

## Risks and Test Signals
Main risk is missing or incompatible test module. Signals are skip without testmod and skeleton subtest success when nullable BTF tracepoint handling works.
