# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/rdonly_maps.c

## Purpose
Tests read-only map sections and mmap/BSS-style global data immutability from user and BPF perspectives. The source was read as a complete 90-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_rdonly_maps()`.
- Includes and fixtures: `#include <test_progs.h>`.
- Generated skeletons/objects referenced: `bpf_link`, `bpf_object`, `bpf_program`.
- Primary APIs and types: `bpf_object__open_file()`, map/program lookup, skeleton-less libbpf APIs, `bpf_program__attach_*`, and BPF link cleanup.

## Control Flow
The test opens the object, locates read-only map content, loads/attaches the program, triggers it, and checks that read-only data is visible but not unexpectedly mutated.

## State and Persistence Behavior
Read-only maps hold constants/global data for the object lifetime. Attach link and object close release all fds.

## Dependencies and Integration Points
Depends on the compiled read-only maps BPF object, libbpf global data handling, and the trigger hook used by the program.

## Risks and Edge Cases
Global data section layout and mmap permissions are ABI-sensitive; mutable-vs-read-only expectations may change with libbpf loader behavior.

## Test Signals
Assertions cover object open, program attach, and observed map/global values after trigger. Named assertion/check labels observed in the source include: `obj_open`, `err %d errno %d\n`, `failed\n`, `prog '%s' not found\n`, `failed to set bss data: %d\n`, `attach_prog`, `failed to get bss data: %d\n`, `prog '%s' didn't run?\n`, `prog '%s' iters: %d, expected: %d\n`, `prog '%s' sum: %d, expected: %d\n`.
