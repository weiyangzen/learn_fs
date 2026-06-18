# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/perf_skip.c

## Purpose
Exercises perf event overflow skip behavior, signal delivery, and breakpoint interaction when a BPF perf-event program is attached. The source was read as a complete 138-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `handle_sigio()`, `handle_sigtrap()`, `serial_test_perf_skip()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include "test_perf_skip.skel.h"`, `#include <linux/compiler.h>`, `#include <linux/hw_breakpoint.h>`, `#include <sys/mman.h>`.
- Generated skeletons/objects referenced: `bpf_link`, `bpf_program`, `test_perf_skip`.
- Primary APIs and types: `sigaction()`, `fcntl(F_SETFL/F_SETOWN_EX)`, `ioctl(PERF_EVENT_IOC_REFRESH)`, `bpf_program__attach_perf_event()`, hardware breakpoint constants, `mmap()`, and generated `test_perf_skip` skeleton.

## Control Flow
The serial test installs SIGIO/SIGTRAP handlers, loads and attaches the BPF program to a perf event, arms async notification, refreshes the event, and verifies which signals are delivered as the perf event and breakpoint paths fire.

## State and Persistence Behavior
Global signal counters (`sigio_count`, `sigtrap_count`) are the observable state. The perf event fd, async owner, BPF link, and mapped breakpoint target are temporary and cleaned up before return.

## Dependencies and Integration Points
Depends on `test_perf_skip.skel.h`, Linux perf event and hardware breakpoint support, process-directed signals, and serial execution to avoid signal interference.

## Risks and Edge Cases
Signal timing and hardware breakpoint availability vary across architectures and virtualization; global handlers make concurrency unsafe, hence serial test naming.

## Test Signals
Assertions check signal codes, handler installation, async fcntl setup, perf refresh, attach success, and exact SIGIO/SIGTRAP count transitions. Named assertion/check labels observed in the source include: `si_code`, `sigaction`, `signal`, `skel_load`, `perf_event_open`, `fcntl(F_SETFL, O_ASYNC)`, `fcntl(F_SETOWN_EX)`, `ioctl(PERF_EVENT_IOC_REFRESH)`, `bpf_program__attach_perf_event`, `sigio_count`, `sigtrap_count`.
