# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pkt_md_access.c

## Purpose
Verifies packet metadata access from a BPF test-run path. The source was read as a complete 26-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_pkt_md_access()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <network_helpers.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `bpf_prog_test_run_opts()`, `network_helpers`, and the packet metadata BPF object loaded by selftest helpers.

## Control Flow
The test loads the metadata-access program, runs it with a network packet fixture, and validates syscall result and program retval.

## State and Persistence Behavior
Only local packet buffers and run options are mutated; no bpffs or namespace state persists.

## Dependencies and Integration Points
Requires packet test-run support and metadata fields accepted by the kernel verifier for the program type.

## Risks and Edge Cases
Kernel changes to metadata availability or context layout can break the test; incorrect packet fixture lengths can cause false negatives.

## Test Signals
Assertions cover test-run syscall success and expected retval. Named assertion/check labels observed in the source include: `test_run_opts err`, `test_run_opts retval`.
