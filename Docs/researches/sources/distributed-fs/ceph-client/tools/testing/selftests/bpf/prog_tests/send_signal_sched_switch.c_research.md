# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/send_signal_sched_switch.c

## Purpose
Serial stress path for BPF signal sending from the scheduler switch tracepoint context. The source was read as a complete 62-line C file in the Linux BPF selftests `prog_tests` harness.

## Important APIs, Types, and Functions
- Local functions: `sigusr1_handler()`, `serial_test_send_signal_sched_switch()`.
- Includes and fixtures: `#include <test_progs.h>`, `#include <stdio.h>`, `#include <stdlib.h>`, `#include <sys/mman.h>`, `#include <pthread.h>`, `#include <sys/types.h>`, `#include <sys/stat.h>`, `#include <fcntl.h>`, `#include "test_send_signal_kern.skel.h"`.
- Generated skeletons/objects referenced: `test_send_signal_kern`.
- Primary APIs and types: `test_send_signal_kern.skel.h`, `pthread`, `mmap`, file/syscall helpers, SIGUSR1 handler, and scheduler-triggering loops.

## Control Flow
The test installs a signal handler, loads the signal skeleton variant for sched_switch, creates activity that causes context switches, and waits until the signal is delivered from BPF.

## State and Persistence Behavior
Global signal flag/counter records delivery. Skeleton BSS configures target pid/signal. Temporary threads and mappings are cleaned at end.

## Dependencies and Integration Points
Depends on sched_switch tracepoint availability, generated skeleton, signal delivery from BPF, and serial execution to avoid handler interference.

## Risks and Edge Cases
Scheduler timing and system load can make delivery latency variable; shared signal handler state is not parallel-safe.

## Test Signals
Pass condition is observed SIGUSR1 delivery while the sched_switch-attached BPF program is active. Named assertion/check labels observed in the source include: `skeleton open_and_load failed\n`, `skeleton attach failed\n`, `Error creating thread, %s\n`.
