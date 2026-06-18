# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_schemes_tried_regions_hang.py

## Purpose

`sysfs_update_schemes_tried_regions_hang.py` is a regression reproducer for hangs while repeatedly updating DAMON tried bytes/tried region related state for a process with an access pattern that should not match.

## Important APIs, Types, and Functions

It launches `sleep 2`, starts `_damon_sysfs.Kdamonds` with a vaddr context and one scheme whose access pattern requires `nr_accesses=[200, 200]`, and repeatedly calls `update_schemes_tried_bytes()`.

## Control Flow

The script starts DAMON on the sleep process, then loops until the process exits, issuing tried-bytes update commands as fast as the loop permits. Any update error fails the test.

## State and Persistence Behavior

It mutates live DAMON state and polls a short-lived child process. No explicit stop is called after the child exits.

## Dependencies and Integration Points

It depends on DAMON vaddr and tried-bytes update support. It targets update-command liveness rather than content accuracy.

## Risks and Edge Cases

If the kernel hangs, the test stalls. The script does not sleep in the update loop, so it can be CPU-intensive for two seconds.

## Test Signals

Exit 0 after the sleep process exits indicates no hang or update error. Any printed update failure is a regression signal.
