# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/uninit_stack.c

## Purpose
Delegates uninitialized stack verifier/runtime tests to the generated `uninit_stack` skeleton.

## APIs, Types, and Functions
Only entry point is `test_uninit_stack()`, which invokes `RUN_TESTS(uninit_stack)`.

## Control Flow, State, and Persistence
All subtest selection and assertions live in generated skeleton test metadata. The C wrapper has no persistent state.

## Dependencies and Integration
Depends on `uninit_stack.skel.h` and the `test_progs` `RUN_TESTS` framework.

## Risks and Test Signals
Risks are limited to skeleton generation and test harness integration. Signals are individual skeleton subtests passing or failing under `RUN_TESTS`.
