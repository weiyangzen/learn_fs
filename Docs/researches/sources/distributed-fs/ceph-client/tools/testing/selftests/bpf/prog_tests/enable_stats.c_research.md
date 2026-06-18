# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/enable_stats.c

## Purpose
Runs generated tests for enabling BPF runtime statistics.

## Important APIs, types, and functions
Uses `test_enable_stats.skel.h` and selftest skeleton helpers inside `test_enable_stats()`.

## Control flow and state
The function opens/loads/runs generated programs and checks stats as encoded in the skeleton. This file keeps no custom persistent state.

## Dependencies and integration points
Depends on kernel support for BPF stats and the generated skeleton. Integrated as `test_enable_stats()`.

## Risks and test signals
Risks include stats support disabled or permission issues. Passing signal is generated skeleton success and expected stats observations.
