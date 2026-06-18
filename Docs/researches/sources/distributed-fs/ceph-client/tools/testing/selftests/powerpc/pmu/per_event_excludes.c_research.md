# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/per_event_excludes.c

## Purpose
`per_event_excludes.c` tests per-event exclude flags in a perf group, ensuring user/kernel/hypervisor exclusion attributes are honored independently for grouped POWER PMU events.

## Important APIs, Types, and Functions
The main routine is `per_event_excludes()`, using an array of `struct event`, the shared event lifecycle helpers, `parse_proc_maps()`/mapping helpers from `lib.h`, and kselftest assertions.

## Control Flow and State
The test initializes several events with different exclude settings, opens them as a group, runs code paths intended to generate user-space activity, reads counters, and compares which events should have counted. State is a perf event group, read result triples, and process mapping metadata.

## Dependencies and Integration Points
It integrates with perf group scheduling, per-event exclude_user/exclude_kernel semantics, ELF/mapping helpers, and PMU counting.

## Risks and Test Signals
Risks include noisy counts from unexpected code paths, permission restrictions, and platform differences in kernel/hypervisor event visibility. A pass means grouped events can carry distinct exclude attributes without the kernel collapsing them to the leader settings.
