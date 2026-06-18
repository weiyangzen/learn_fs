<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/srso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/srso.c

## Purpose

`srso.c` is a focused x86 selftest for AMD SRSO Safe-RET mitigation behavior using raw performance counters. It samples retired returns and retired mispredicted returns while the process sleeps and tells the operator that the mitigation is working if the two counts are nearly equal.

## Important APIs, Types, and Functions

The program uses `__cpuid(1)` to restrict execution to Zen 1 through Zen 4 CPUID ranges. It configures two `perf_event_attr` objects with `PERF_TYPE_RAW`, raw configs `0xc8` and `0xc9`, `exclude_user=1`, and `exclude_hv=1`, opens them with `perf_event_open`, resets/enables both counters, sleeps for ten seconds, disables them, reads counts, and prints the retired/mispredicted return totals.

## Control Flow and State

The flow is linear: validate CPU family/model, open both perf counters, enable them around a fixed sleep window, then print the two counts. Kernel state is limited to per-process perf events and hardware counter state for the measurement interval.

## Dependencies and Integration Points

It depends on AMD Zen hardware, raw PMU event encodings for retired returns and retired mispredicted returns, `perf_event_open` permissions, and PMU availability. It integrates with CPU mitigation regression testing by providing a coarse runtime signal rather than an automated pass/fail threshold.

## Risks and Test Signals

Risks include unsupported CPUID ranges, unavailable raw PMU events, perf permission restrictions, noisy system activity during the ten-second sleep, and lack of an enforced numeric threshold. The test signal is the printed count pair; Safe-RET is considered healthy when retired and mispredicted return counts are close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/srso.c -->
