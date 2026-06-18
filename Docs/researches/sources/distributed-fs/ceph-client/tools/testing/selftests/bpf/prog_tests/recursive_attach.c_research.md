# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/recursive_attach.c

## Purpose
Covers fentry recursive attachment, attach-target setting, BTF-id presence, chain behavior, and stress attaching from multiple threads. The source was read as a complete 219-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `test_recursive_fentry_chain()`, `test_recursive_fentry()`, `test_fentry_attach_btf_presence()`, `test_fentry_attach_stress()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "fentry_recursive.skel.h"`, `#include "fentry_recursive_target.skel.h"`, `#include <bpf/btf.h>`, `#include "bpf/libbpf_internal.h"`.
- Generated skeletons/objects referenced: `fentry_recursive`, `fentry_recursive_target`.
- Primary APIs and types: `fentry_recursive_target__open_and_load()`, `fentry_recursive__open/load/attach()`, `bpf_program__set_attach_target()`, `bpf_link__fd()`, `bpf_prog_test_run_opts()`, BTF APIs, and pthread joins.

## Control Flow
Chain tests load target and recursive fentry skeletons, set attach targets, attach links, and run target programs. BTF-presence tests validate attach target metadata. Stress tests create threads that attach repeatedly and join them.

## State and Persistence Behavior
State includes target program fds, fentry links, BSS counters, and thread-local attach attempts. All links/skeletons are destroyed at cleanup.

## Dependencies and Integration Points
Depends on generated fentry skeletons, BTF availability, fentry attach support, and pthreads.

## Risks and Edge Cases
Recursive attach and stress cases are timing-sensitive; BTF id lookup behavior can differ across kernels; improper cleanup can leave links until process exit.

## Test Signals
Assertions check target load, attach-target setting, load/attach success/failure, link fd, target test-run, and pthread joins. Named assertion/check labels observed in the source include: `fentry_recursive_target__open_and_load`, `fentry_recursive__open`, `bpf_program__set_attach_target`, `fentry_recursive__load`, `fentry_recursive__attach`, `link_fd`, `fentry_target test_run`, `fentry_target`, `pthread_join`.
