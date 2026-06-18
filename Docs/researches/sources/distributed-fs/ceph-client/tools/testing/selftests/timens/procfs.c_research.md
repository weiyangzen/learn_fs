# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/procfs.c

## Purpose
Tests procfs views affected by time namespaces, especially `/proc/uptime` and `btime` from `/proc/stat`.

## Important APIs, Types, and Functions
Functions include `switch_ns`, `init_namespaces`, `read_proc_uptime`, `read_proc_stat_btime`, `check_uptime`, `check_stat_btime`, and `main`. It uses parent/child namespace file descriptors and helpers from `timens.h`.

## Control Flow
The test opens the parent time namespace, unshares a child time namespace, verifies different namespace inodes, sets offsets, switches between namespace fds, reads procfs time values, and checks that uptime and boot-time reporting reflect namespace semantics.

## State and Persistence Behavior
Kernel namespace offsets and namespace file descriptors are runtime state. Procfs reads are transient; no files are modified except `/proc/self/timens_offsets`.

## Dependencies and Integration Points
Depends on `/proc/self/ns/time_for_children`, `/proc/self/timens_offsets`, `/proc/uptime`, `/proc/stat`, `setns`, and kselftest helpers. Integrates with procfs time namespace virtualization.

## Risks and Edge Cases
Parsing procfs text is format-sensitive. Switching namespaces requires privileges and open descriptors. Time advances during comparisons, so tests must allow small drift.

## Test Signals
Signals are successful namespace inode separation and expected shifted values in `/proc/uptime` and `btime`.
