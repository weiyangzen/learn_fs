# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event.c

## Purpose
`event.c` is the shared perf-event wrapper for powerpc PMU selftests. It normalizes `perf_event_attr` initialization, opens events for common pid/cpu/group combinations, controls descriptors with ioctl, reads scaled counter data, and prints event reports.

## Important APIs, Types, and Functions
Important functions are `perf_event_open()`, `event_init_opts()`, `event_init_named()`, `event_init()`, `event_init_sampling()`, `event_open_with_options()`, `event_open_with_group()`, `event_open_with_pid()`, `event_open_with_cpu()`, `event_open()`, `event_close()`, `event_enable()`, `event_disable()`, `event_reset()`, `event_read()`, and report helpers.

## Control Flow and State
Initialization zeroes `struct event`, fills raw or hardware type/config fields, sets disabled/exclude flags, and for sampling enables `PERF_SAMPLE_REGS_INTR` defaults. Open helpers call the syscall with selected pid/cpu/group values and store the fd. Control helpers issue perf ioctls. Reading fills the `result` value/running/enabled triple for scaled counter reporting. State is per `struct event` plus optional mmap buffer ownership held by callers.

## Dependencies and Integration Points
The wrapper depends on Linux `perf_event.h`, syscall numbers, ioctl constants, and `event.h`. It is used by PMU event-code tests, sampling tests, and other powerpc perf selftests.

## Risks and Test Signals
Risks include assuming `read_format` layout, leaking fds on failed grouped opens, and test misuse of raw versus hardware event types. Signals are consistent open/close behavior, correct negative-open handling, and readable counts after enable/workload/disable cycles.
