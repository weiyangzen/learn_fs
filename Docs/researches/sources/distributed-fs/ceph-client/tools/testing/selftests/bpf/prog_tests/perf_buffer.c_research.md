# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_buffer.c

## Purpose
Validates libbpf perf-buffer delivery from a BPF program on every online CPU, including per-CPU buffer enumeration, epoll fd exposure, direct per-buffer consumption, and CPU/data identity checks. The source was read as a complete 148-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `on_sample()`, `trigger_on_cpu()`, `serial_test_perf_buffer()`.
- Includes and fixtures: `#include <pthread.h>`, `#include <sched.h>`, `#include <sys/socket.h>`, `#include <test_progs.h>`, `#include "test_perf_buffer.skel.h"`, `#include "bpf/libbpf_internal.h"`.
- Generated skeletons/objects referenced: `test_perf_buffer`.
- Primary APIs and types: `test_perf_buffer__open_and_load()`, `test_perf_buffer__attach()`, `bpf_map_update_elem()`, `perf_buffer__new()`, `perf_buffer__poll()`, `perf_buffer__buffer_cnt()`, `perf_buffer__buffer_fd()`, `perf_buffer__consume_buffer()`, `parse_cpu_mask_file()`, `pthread_setaffinity_np()`.

## Control Flow
`serial_test_perf_buffer()` reads the online CPU mask, loads the skeleton, stores the current PID in `my_pid_map`, attaches the probe, creates a perf buffer with `on_sample()`, triggers the probe once on each online CPU using `trigger_on_cpu()`, polls, then drains and re-triggers each per-CPU buffer to verify targeted consumption.

## State and Persistence Behavior
State is mostly transient: `cpu_seen` records callbacks, the BPF map stores one PID filter, perf-buffer mmap/fds are owned by libbpf, and thread CPU affinity is changed while triggering samples. Cleanup frees the perf buffer, skeleton, and parsed CPU mask.

## Dependencies and Integration Points
Depends on generated `test_perf_buffer.skel.h`, libbpf perf-buffer internals, `/sys/devices/system/cpu/online`, pthread affinity support, kprobe attachment in the skeleton, and selftests `CHECK`/`ASSERT` helpers.

## Risks and Edge Cases
CPU hotplug or affinity failures can make online CPU counts drift; ASAN needs the callback no-sanitize annotation for mmap data; skipped offline CPUs must remain aligned with `perf_buffer__buffer_cnt()` ordering; perf event permissions can block attachment.

## Test Signals
Assertions cover PID map update, epoll fd sanity, sample CPU equality, seen CPU count, per-buffer fd uniqueness, successful drain/consume, and callback re-delivery after each per-buffer trigger. Named assertion/check labels observed in the source include: `cpu_data %d != cpu %d\n`, `cpu #%d, err %d\n`, `err %d\n`, `skeleton open/load failed\n`, `my_pid_update`, `bad fd: %d\n`, `last fd %d == fd %d\n`, `cpu %d, err %d\n`.
