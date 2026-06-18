
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/helper_restricted.c

## Purpose

`helper_restricted.c` checks that a set of BPF programs using restricted helpers fail verifier load as expected.

## Important APIs, Types, and Functions

The test uses `test_helper_restricted.skel.h`, skeleton metadata `prog_cnt`, iterates generated `skeleton->progs`, toggles autoload with `bpf_program__set_autoload()`, and calls `test_helper_restricted__load()`.

## Control Flow and Data Flow

For each program slot, the harness opens a fresh skeleton, enables autoload for all programs up to the skeleton's program count, attempts load, asserts error, destroys, and repeats until every program has participated.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is per-open skeleton autoload configuration and verifier result. Dependencies are the paired restricted-helper BPF object and verifier policy. Integration is helper availability enforcement by program type/context. Risks are unusual loop shape relying on `prog_cnt` discovered from the first skeleton and missing exact verifier message checks. Test signal is load failure for each attempted configuration.
