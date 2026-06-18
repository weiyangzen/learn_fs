# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/l3_bank_test.c

## Purpose
`l3_bank_test.c` is a focused PMU workload test for an L3-bank-related raw event. It allocates a buffer, touches cache-line-spaced offsets, and expects the event to count activity without setup failure.

## Important APIs, Types, and Functions
The central function is `l3_bank_test()`, run through `test_harness()`. It uses `event_init()`, `event_open()`, `event_enable()`, `event_disable()`, `event_read()`, `event_close()`, and `FAIL_IF` from the selftest utilities.

## Control Flow and State
The test allocates `MALLOC_SIZE`, opens the selected PMU event, enables it, performs a simple memory workload over the allocation, disables and reads the event, then releases resources. State is transient heap memory and one perf event descriptor.

## Dependencies and Integration Points
It depends on the local PMU event wrapper, malloc/free, and kernel support for the raw event. It integrates with the kselftest harness as a standalone PMU program.

## Risks and Test Signals
Risks are weak workload signal, event-code unavailability on some CPUs, and memory allocation failure. A pass indicates the L3 event can be programmed and sampled around a memory workload without perf errors.
