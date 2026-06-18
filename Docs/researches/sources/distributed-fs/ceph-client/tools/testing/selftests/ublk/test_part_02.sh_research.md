<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_02.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_02.sh

## Purpose
Verifies asynchronous partition scan does not hang ublk daemon teardown when fault-injected I/O blocks partition reads.

## Important APIs, Types, and Functions
_test_partition_scan_no_hang, _add_ublk_dev_no_settle, _get_ublk_daemon_pid, __ublk_kill_daemon, _ublk_del_dev.

## Control Flow
Adds a fault_inject ublk device with 60s I/O delay without waiting for udev settle, waits briefly for async scan to hit delay, kills the daemon, checks expected state DEAD or QUIESCED depending on recovery flag, then deletes the device.

## State and Persistence
State is transient but intentionally includes a blocked partition-scan I/O path and daemon state transition.

## Dependencies and Integration Points
Depends on fault_inject target, recovery option -r, partition scan behavior, and test_common.sh state helpers.

## Risks and Edge Cases
The test assumes 1s is enough to start partition scan and that expected state names remain stable.

## Test Signals
Pass is transition to DEAD without recovery and QUIESCED with recovery, both without blocking teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/test_part_02.sh -->
