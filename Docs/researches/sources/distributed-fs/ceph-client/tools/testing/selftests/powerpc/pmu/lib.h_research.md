# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/lib.h

## Purpose
`lib.h` declares the shared PMU helper API and small data structures for pipe synchronization and address-range tracking.

## Important APIs, Types, and Functions
It defines the `union pipe` fd layout, `struct addr_range`, external `libc`/`vdso` ranges, parent/child notification helpers, wait/kill helpers, `parse_proc_maps()`, and the perf paranoid requirement helper.

## Control Flow and State
There is no runtime control flow. The header establishes caller-owned pipe descriptors and global address-range state populated by `lib.c`.

## Dependencies and Integration Points
It includes standard integer, bool, stdio, string, and unistd headers and is included by PMU tests that coordinate child workloads or need mapping/perf-permission checks.

## Risks and Test Signals
Risks are descriptor-direction mistakes and global range use before `parse_proc_maps()`. Test signals are successful compile/link of helper users and deterministic synchronization in multi-process PMU tests.
