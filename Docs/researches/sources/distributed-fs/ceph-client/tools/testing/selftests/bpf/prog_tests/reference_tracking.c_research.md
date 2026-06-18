# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/reference_tracking.c

## Purpose
Runs verifier reference-tracking tests from object files and validates object naming/open behavior. The source was read as a complete 64-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_reference_tracking()`.
- Includes and fixtures: `#include <test_progs.h>`.
- Generated skeletons/objects referenced: `bpf_object`.
- Primary APIs and types: `bpf_object__open_file()`, `bpf_object__name()`, object load error handling, and selftests object iteration.

## Control Flow
`test_reference_tracking()` opens BPF object fixtures for reference acquisition/release scenarios, checks object name, and expects load success or verifier rejection according to each case.

## State and Persistence Behavior
Only object fds/logs are transient. Reference state is modeled inside verifier during program load.

## Dependencies and Integration Points
Depends on compiled reference-tracking BPF object files and verifier reference-lifetime rules.

## Risks and Edge Cases
Failure expectations are tightly coupled to verifier reference diagnostics and object naming conventions.

## Test Signals
Assertions check object name, object open, and success/failure of verifier load cases. Named assertion/check labels observed in the source include: `wrong obj name '%s', expected '%s'\n`, `obj_open_file`.
