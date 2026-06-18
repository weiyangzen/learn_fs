# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/compute_live_registers.c

## Purpose
Runs generated verifier coverage for live-register computation.

## Important APIs, types, and functions
Uses `compute_live_registers.skel.h` and `RUN_TESTS(compute_live_registers)` from the selftest harness. The file has no local helpers beyond `test_compute_live_registers()`.

## Control flow and state
Control flow delegates entirely to the generated skeleton test runner. State is whatever the skeleton and harness maintain during open/load/run; this file introduces no persistent state.

## Dependencies and integration points
Depends on the generated BPF object and harness macros. Integrated as a single selftest entry.

## Risks and test signals
Risks are contained in the generated program and verifier expectations. Passing signal is `RUN_TESTS` success for all skeleton-defined subtests.
