# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_12.sh

## Purpose
This test validates per-I/O daemon task distribution when load is imbalanced toward one queue.

## Important APIs, Types, and Functions
It uses bpftrace `trace/count_ios_per_tid.bt`, fio, `_add_ublk_dev -t null -q 4 -d 16 --nthreads 6 --per_io_tasks`, CPU-pinned fio, and trace output counting.

## Control Flow
The script starts bpftrace for the ublk device, issues direct writes pinned to CPU 0, stops tracing, and counts trace lines containing `@`. It expects all six server threads to handle some I/O.

## State and Persistence
It creates a null ublk device, background bpftrace process, and temporary output file, then cleans up.

## Dependencies and Integration Points
It depends on `kublk` per-I/O task scheduling, bpftrace, fio, and trace scripts.

## Risks
Tracing can fail due to permissions. The test checks participation, not equal distribution, because tag allocation may not be round-robin yet.

## Test Signals
Pass means every configured server thread handled at least one I/O despite CPU-pinned workload.
