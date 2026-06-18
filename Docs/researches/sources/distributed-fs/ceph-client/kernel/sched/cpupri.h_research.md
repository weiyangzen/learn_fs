# sources/distributed-fs/ceph-client/kernel/sched/cpupri.h

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpupri.h` declares the CPU-priority data structures and APIs used by real-time scheduler balancing. The header was read as a complete 30-line source.

## Important APIs, Types, and Functions

`CPUPRI_NR_PRIORITIES` is `MAX_RT_PRIO + 1`. Priority constants define invalid, normal, RT buckets, and a higher-than-RT bucket. `struct cpupri_vec` contains an atomic CPU count and cpumask for one priority bucket. `struct cpupri` contains the bucket array and `cpu_to_pri` reverse map. Declared APIs are `cpupri_find()`, `cpupri_find_fitness()`, `cpupri_set()`, `cpupri_init()`, and `cpupri_cleanup()`.

## Control Flow

The header has no executable flow. It provides the contract for root-domain setup, rq priority updates, and RT/deadline balancing lookups.

## State and Persistence Behavior

The declared state is root-domain memory and persists until root-domain teardown. It is not persistent across boot.

## Dependencies and Integration Points

The header depends on atomic operations, cpumasks, and RT priority definitions. It is implemented by `cpupri.c` and consumed by RT and deadline scheduler classes.

## Risks and Edge Cases

The constants must remain aligned with `convert_prio()` and RT priority ranges. Callers must treat lookup results as recommendations because concurrent rq priority changes can race with reads.

## Test Signals

Compile coverage with RT/deadline classes, root-domain allocation tests, and migration workloads that exercise priority lookup and update APIs.
