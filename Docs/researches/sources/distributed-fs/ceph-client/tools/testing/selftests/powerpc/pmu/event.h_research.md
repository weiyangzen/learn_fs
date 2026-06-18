# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/event.h

## Purpose
`event.h` declares the powerpc PMU selftest perf-event abstraction and the `struct event` state shared by all PMU test programs.

## Important APIs, Types, and Functions
`struct event` embeds `struct perf_event_attr`, an fd, a result triple of value/running/enabled, a name, and an optional mmap buffer pointer. The header declares initialization, open, close, enable, disable, reset, read, and report functions implemented in `event.c`.

## Control Flow and State
The header has no runtime flow, but it fixes the state layout that tests mutate: attributes are configured before open, fd tracks the kernel perf handle, result stores the last counter read, and `mmap_buffer` is used by sampling tests.

## Dependencies and Integration Points
It includes Linux perf UAPI definitions and `utils.h`, and is the common include for event-code, sampling, and top-level PMU tests.

## Risks and Test Signals
Risks are layout mismatches with `event.c`, callers using uninitialized events, and stale fd values after close. Test signals are clean compilation of all PMU tests and predictable event lifecycle behavior.
