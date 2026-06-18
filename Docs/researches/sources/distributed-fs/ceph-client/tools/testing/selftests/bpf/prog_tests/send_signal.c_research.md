# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/send_signal.c

## Purpose
Tests `bpf_send_signal()` and thread-targeted signal delivery from tracepoint, software perf, and hardware/NMI perf contexts, including remote process signaling. The source was read as a complete 293-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `sigusr1_handler()`, `sigusr1_siginfo_handler()`, `test_send_signal_common()`, `test_send_signal_tracepoint()`, `test_send_signal_perf()`, `test_send_signal_nmi()`, `test_send_signal()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <sys/time.h>`, `#include <sys/resource.h>`, `#include "test_send_signal_kern.skel.h"`, `#include "io_helpers.h"`.
- Generated skeletons/objects referenced: `bpf_program`, `test_send_signal_kern`.
- Primary APIs and types: `test_send_signal_kern__open_and_load/attach()`, `bpf_program__attach_perf_event()`, `perf_event_open`, `fork()`, pipes, `sigaction()/signal()`, `setpriority()`, `read_with_timeout()`, and SIGUSR1 handlers.

## Control Flow
`test_send_signal_common()` forks a child, installs handlers, coordinates readiness over pipes, loads/attaches either tracepoint or perf program, sets BSS target fields, triggers the event locally or remotely, waits for the child result, then kills/waits for cleanup. `test_send_signal()` runs 12 subtests across context, thread flag, and remote flag.

## State and Persistence Behavior
Global `sigusr1_received` records signal receipt in child context. Skeleton BSS fields define signal number, target pid, current pid, and thread-vs-process mode. Pipes coordinate parent/child; priority is temporarily raised and restored.

## Dependencies and Integration Points
Depends on generated `test_send_signal_kern.skel.h`, perf software/hardware events, signal permissions, fork/pipe support, and `io_helpers.h` timeout reads.

## Risks and Edge Cases
Hardware PMU may be unavailable and is skipped for known errno; signal timing is inherently racy; priority changes can fail under policy; child cleanup uses SIGKILL on error paths.

## Test Signals
Assertions check pipe/fork/signal setup, priority operations, skeleton attach or perf attach, child signal value 8, timeout read, and result byte correctness. Named assertion/check labels observed in the source include: `pipe_p2c`, `fork`, `sigaction`, `signal`, `getpriority`, `setpriority`, `pipe_write`, `pipe_read`, `sigusr1_received`, `skel_open_and_load`, `skel_attach`, `perf_event_open`.
