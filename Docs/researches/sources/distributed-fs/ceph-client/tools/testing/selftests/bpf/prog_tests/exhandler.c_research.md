# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/exhandler.c

## Purpose
Tests generated exception-handler kernel BPF behavior through `exhandler_kern` skeleton.

## Important APIs, types, and functions
Uses `exhandler_kern.skel.h` and selftest load/attach/run helpers. `test_exhandler()` delegates to the skeleton and checks expected output.

## Control flow and state
The file has simple open/load/attach/trigger/cleanup flow, with state in skeleton BSS and links.

## Dependencies and integration points
Depends on generated BPF object and kernel support for the tested exception-handler mechanism. Integrated as `test_exhandler()`.

## Risks and test signals
Risk is feature availability or verifier behavior drift. Passing signal is successful skeleton execution with expected BSS/result values.
