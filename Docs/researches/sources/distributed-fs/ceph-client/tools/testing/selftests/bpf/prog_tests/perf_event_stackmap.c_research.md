# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_event_stackmap.c

## Purpose
Checks stack map capture from a BPF program attached to a software perf event, using both user and kernel stack collection paths. The source was read as a complete 117-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_perf_event_stackmap()`.
- Includes and fixtures: `#include <pthread.h>`, `#include <sched.h>`, `#include <test_progs.h>`, `#include "perf_event_stackmap.skel.h"`.
- Generated skeletons/objects referenced: `bpf_program`, `perf_event_stackmap`.
- Primary APIs and types: `perf_event_open` through `bpf_program__attach_perf_event()`, `perf_event_stackmap__open_and_load()`, skeleton maps/programs, `pthread`/CPU helper paths, and selftests polling/wait macros.

## Control Flow
The test loads the `perf_event_stackmap` skeleton, creates a perf event, attaches the program, generates CPU activity, and inspects BPF-side counters/maps to confirm stack traces are collected and symbolized enough for the expected selftest conditions.

## State and Persistence Behavior
Persistent state is limited to perf-event fd/link lifetime and stack-map contents inside the loaded BPF object. Skeleton destruction closes links and maps.

## Dependencies and Integration Points
Depends on `perf_event_stackmap.skel.h`, perf event availability, stack-map verifier support, and kernel stack/user stack helper behavior.

## Risks and Edge Cases
Stack collection is sensitive to perf_event_paranoid, frame-pointer/unwind configuration, CPU scheduling, and unavailable PMU features; failures can be environmental rather than logic regressions.

## Test Signals
The key signal is successful perf-event attachment plus expected BPF map/counter updates after load and trigger activity. Named assertion/check labels observed in the source include: `skeleton open failed\n`, `skeleton load failed: %d\n`, `err %d, errno %d\n`, `attach_perf_event`, `failed\n`.
