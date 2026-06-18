# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/section_names.c

## Purpose
Verifies libbpf section-name parsing tables for program type and expected attach type inference. The source was read as a complete 261-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_prog_type_by_name()`, `test_attach_type_by_name()`, `test_section_names()`.
- Includes and fixtures: `#include <test_progs.h>`.
- Generated skeletons/objects referenced: none in this C file; it uses raw object/helper loading or framework macros.
- Primary APIs and types: `libbpf_prog_type_by_name()`, `libbpf_attach_type_by_name()`, local test case arrays, and selftests assertion macros.

## Control Flow
`test_section_names()` iterates known section-name patterns, checking program type resolution and attach type resolution separately for valid and invalid names.

## State and Persistence Behavior
No persistent state; all data is static/local test vectors.

## Dependencies and Integration Points
Depends on libbpf section parser behavior and the list of section patterns supported by this kernel/libbpf snapshot.

## Risks and Edge Cases
New section aliases or parser refactors require updating expected tables; tests can fail due to intentional libbpf API expansion.

## Test Signals
Failures identify section strings whose inferred program or attach type differs from expected. Named assertion/check labels observed in the source include: `prog: unexpected rc=%d for %s\n`, `prog: unexpected prog_type=%d for %s\n`, `prog: unexpected expected_attach_type=%d for %s\n`, `attach: unexpected rc=%d for %s\n`, `attach: unexpected attach_type=%d for %s\n`.
