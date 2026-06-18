# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/datasym.c

## Purpose
This workload repeatedly accesses a static data symbol with a controlled layout so perf tests can attribute samples to data symbols and offsets.

## Important APIs, Types, And Functions
The file defines aligned `struct buf` with `data1`, 55 reserved bytes, and `data2`, plus a volatile static instance `workload_datasym_buf1`. Workload entry `datasym()` uses `signal()`, `alarm()`, and `atoi()`, and is registered with `DEFINE_WORKLOAD(datasym)`.

## Control Flow
The workload parses an optional duration, installs SIGINT/SIGALRM handlers, arms an alarm, and loops until `done`. Each iteration increments `data1`, conditionally performs an extra increment at value 123, then accumulates `data1` into `data2`.

## State, Dependencies, And Integration
Persistent state is only the process-lifetime static volatile buffer in the data section. The 64-byte alignment and initialized reserved byte are deliberate to create a visible data symbol and cache-line-shaped layout. It integrates with perf data-symbol and memory-access sampling tests.

## Risks And Test Signals
The conditional branch is an Arm N1 SPE erratum workaround to avoid a pathological repeated instruction stream. Risks include compiler layout changes if attributes are altered and sampling bias on affected hardware. Downstream success is observing accesses to `workload_datasym_buf1` and its fields.
