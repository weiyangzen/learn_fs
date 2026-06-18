<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/uevent_filtering.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/uevent_filtering.c

## Purpose
Tests kernel uevent netlink filtering across user and network namespace ownership combinations.

## Important APIs, Types, and Functions
read_nointr, write_nointr, wait_for_pid, uevent_listener, trigger_uevent, set_death_signal, do_test, TEST(uevent_filtering).

## Control Flow
Forks a listener, optionally unshares namespaces before or after opening a NETLINK_KOBJECT_UEVENT socket, synchronizes with eventfd, writes add to /sys/devices/virtual/mem/full/uevent, waits up to two seconds, and verifies whether the event is delivered.

## State and Persistence
Creates child processes, netlink sockets, signal handlers, and an eventfd; no persistent files are modified beyond triggering the sysfs uevent.

## Dependencies and Integration Points
Requires root, /sys/devices/virtual/mem/full/uevent, NETLINK_KOBJECT_UEVENT, CLONE_NEWUSER, CLONE_NEWNET, and kselftest_harness.

## Risks and Edge Cases
Timing-sensitive delivery window; child cleanup relies on death signal and explicit SIGTERM/SIGUSR1 paths.

## Test Signals
Pass means expected receive/no-receive behavior for all namespace matrix cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/uevent/uevent_filtering.c -->
