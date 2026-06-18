<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_01.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_01.sh

## Purpose
Stress test that runs fio while removing null, loop, and stripe devices.

## Important APIs, Types, and Functions
run_io_and_remove or run_io_and_kill_daemon wrappers, fio, _have_feature, background jobs and wait.

## Control Flow
Prepares backing files, starts several target/mode workloads in parallel, injects device removal or daemon death while I/O is in flight, waits for each wave, and preserves the first observed failure in ERR_CODE.

## State and Persistence
Uses temporary backing files and transient ublk devices; test_stress_05 additionally has a local run_io_and_remove that sends SIGKILL to the daemon before deletion.

## Dependencies and Integration Points
Depends on fio, test_common.sh stress helpers, null/loop/stripe targets, and optional ZERO_COPY, AUTO_BUF_REG, PER_IO_DAEMON, and BATCH_IO feature gates.

## Risks and Edge Cases
Highly timing-sensitive and intentionally destructive to active devices; diagnostics can interleave and some feature-gated branches are skipped silently when unsupported.

## Test Signals
Pass means all lifecycle-under-I/O scenarios complete with zero helper status; missing fio/features return skip where gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_stress_01.sh -->
