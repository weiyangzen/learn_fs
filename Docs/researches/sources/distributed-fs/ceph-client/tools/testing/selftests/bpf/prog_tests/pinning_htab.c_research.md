# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/pinning_htab.c

## Purpose
Minimal hash-table pin/unpin smoke test through skeleton APIs. The source was read as a complete 37-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `unpin_map()`, `test_pinning_htab()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "test_pinning_htab.skel.h"`.
- Generated skeletons/objects referenced: `test_pinning_htab`.
- Primary APIs and types: `test_pinning_htab__open_and_load()`, `bpf_object__find_map_by_name()`, `bpf_map__pin()`, `bpf_map__unpin()`.

## Control Flow
The test opens/loads the hash-table skeleton, finds the map by name, pins it, and unpins it through a helper.

## State and Persistence Behavior
Only the temporary bpffs pin for the hash map is persistent; it is removed by `bpf_map__unpin()`.

## Dependencies and Integration Points
Requires generated `test_pinning_htab.skel.h`, bpffs, and libbpf map pinning.

## Risks and Edge Cases
Existing pin path conflicts and missing bpffs permissions are the main environmental failures.

## Test Signals
Assertions cover skeleton load, map lookup, pin success, and unpin success. Named assertion/check labels observed in the source include: `skel open_and_load`, `bpf_object__find_map_by_name`, `bpf_map__pin`, `bpf_map__unpin`.
