# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/endian.c

## Purpose
Tests BPF endian conversion helpers/macros for 16-, 32-, and 64-bit values.

## Important APIs, types, and functions
Uses `test_endian.skel.h`, constants `IN16/IN32/IN64` and expected byte-swapped `OUT16/OUT32/OUT64`, and skeleton BSS/data fields populated by generated programs.

## Control flow and state
The test loads/attaches or test-runs the skeleton, triggers conversion, and checks outputs against constants. State is only skeleton runtime state.

## Dependencies and integration points
Depends on generated BPF program and selftest harness. Integrated as `test_endian()`.

## Risks and test signals
Risk is endian assumptions across host architectures; expected constants encode byte swaps. Passing signal is exact equality for all conversion widths.
