# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_memcg_path_leak.sh

## Purpose

`sysfs_memcg_path_leak.sh` is a regression test for memory leaks when repeatedly writing DAMOS filter `memcg_path`.

## Important APIs, Types, and Functions

It uses DAMON sysfs, debugfs kmemleak at `/sys/kernel/debug/kmemleak`, and shell writes to configure one filter under one scheme.

## Control Flow

The script requires root, DAMON sysfs, and kmemleak. It creates one kdamond/context/scheme/filter, writes the same memcg path string 128 times, triggers `kmemleak` scan, and fails if the kmemleak report is non-empty.

## State and Persistence Behavior

It mutates DAMON sysfs and kmemleak scan state. It does not start kdamond monitoring.

## Dependencies and Integration Points

It depends on kmemleak being enabled and readable, plus DAMON filter sysfs support.

## Risks and Edge Cases

Existing kmemleak reports unrelated to this test can cause false failures. The script does not clear kmemleak before the repeated writes.

## Test Signals

Empty kmemleak output after scan is success; any report is printed and exits failure.
