# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_link.c

## Purpose
Validates BPF link metadata and detach semantics for perf-event-attached programs. The source was read as a complete 92-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `burn_cpu()`, `test_perf_link()`.
- Includes and fixtures: `#include <linux/compiler.h>`, `#include <test_progs.h>`, `#include "testing_helpers.h"`, `#include "test_perf_link.skel.h"`.
- Generated skeletons/objects referenced: `test_perf_link`.
- Primary APIs and types: `syscall(__NR_perf_event_open)`, `test_perf_link__open_and_load()`, `bpf_program__attach_perf_event()`, `bpf_link__fd()`, `bpf_link_get_info_by_fd()`, `bpf_link__destroy()`, and `burn_cpu()` workload generation.

## Control Flow
`test_perf_link()` opens a software perf event, loads the skeleton, attaches the program as a BPF link, queries link info for type/id/prog id, burns CPU until the program runs, destroys the link, then burns CPU again to confirm run count stops.

## State and Persistence Behavior
State includes the perf event fd, the BPF link fd, and skeleton BSS run counters. Once the link is destroyed, no persistent attachment should remain.

## Dependencies and Integration Points
Requires generated `test_perf_link.skel.h`, software perf events, link-info kernel support, and testing helper timeouts.

## Risks and Edge Cases
Timing-sensitive CPU burning can be flaky on constrained hosts; old kernels may lack link metadata fields; perf_event_open can fail due to policy.

## Test Signals
Assertions check perf fd, skeleton load, link fd/type/id/prog id, run-count timeout while attached, and unchanged run count after detach. Named assertion/check labels observed in the source include: `perf_fd`, `skel_load`, `link_fd`, `link_type`, `link_id`, `link_prog_id`, `run_cnt_timeout`, `run_cnt_before_after`.
