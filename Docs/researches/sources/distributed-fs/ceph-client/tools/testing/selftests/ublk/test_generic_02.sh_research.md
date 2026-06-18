# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_generic_02.sh

## Purpose
This test checks that ublk multi-queue dispatch does not reorder sequential writes unexpectedly.

## Important APIs, Types, and Functions
It uses `_have_program bpftrace`, `_have_program fio`, `_add_ublk_dev -t null -q 2`, `_get_disk_dev_t()`, `bpftrace trace/seq_io.bt`, `taskset`, and fio sequential write workload.

## Control Flow
The script skips without bpftrace or fio, adds a two-queue null device, starts a bpftrace probe waiting for a `BPFTRACE_READY` marker, runs a CPU-pinned direct sequential write workload, stops bpftrace, and fails if the trace output contains `out_of_order:`.

## State and Persistence
It creates a ublk null device, temporary trace output file, and background bpftrace process, all cleaned up on normal paths.

## Dependencies and Integration Points
It depends on trace scripts under `trace/`, bpftrace permissions, fio, taskset, and null target behavior.

## Risks
Probe attachment timing is handled by polling the ready marker. Tracing permissions or missing BTF can skip/fail. CPU pinning is used to focus queue behavior.

## Test Signals
Pass means no out-of-order events were observed by bpftrace during sequential writes.
