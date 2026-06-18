# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/probe_user.c

## Purpose
Validates user-memory probing from BPF, including BSS initialization and kprobe attachment against user pointers. The source was read as a complete 111-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_probe_user()`.
- Includes and fixtures: `#include <test_progs.h>`.
- Generated skeletons/objects referenced: `bpf_link`, `bpf_object`, `bpf_program`.
- Primary APIs and types: `bpf_object__open_file()`, `bpf_object__find_map_by_name()`, BSS mmap/update logic, `bpf_program__attach_kprobe()`, `bpf_link`, and raw libbpf object/program APIs.

## Control Flow
The test opens the BPF object, locates/initializes BSS data, loads programs, attaches a kprobe, triggers user-memory reads, and checks BPF-observed values in BSS.

## State and Persistence Behavior
The BSS map is mutable shared state between user space and BPF. Link/object lifetime controls the attachment; no bpffs persistence is used.

## Dependencies and Integration Points
Depends on compiled BPF object, kprobe availability, libbpf BSS support, and selftest permissions.

## Risks and Edge Cases
Probe targets and user-memory access rules vary by architecture and kernel hardening; BSS layout mismatches can cause misleading failures.

## Test Signals
Assertions check object open, BSS size/initialization, kprobe attach, and expected BPF-written BSS values. Named assertion/check labels observed in the source include: `obj_open_file`, `prog '%s' not found\n`, `bss_size`, `set_bss_init`, `err %d\n`, `attach_kprobe`, `failed to get kprobe res: %d\n`.
