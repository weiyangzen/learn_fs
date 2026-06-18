# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_removed_scheme_dir.sh

## Purpose

`sysfs_update_removed_scheme_dir.sh` is a regression test ensuring update commands do not trigger kernel bugs after a scheme sysfs directory is removed while monitoring is active.

## Important APIs, Types, and Functions

It uses DAMON admin sysfs, `dmesg -C`, `dmesg | grep BUG`, scheme count writes, and kdamond state commands `on`, `update_schemes_stats`, `update_schemes_tried_regions`, and `off`.

## Control Flow

The script configures one vaddr context monitoring its own pid with one scheme, starts DAMON, sleeps briefly, removes the scheme by writing `nr_schemes=0`, issues stats and tried-regions update commands, checks dmesg for BUG after each, then stops DAMON.

## State and Persistence Behavior

It mutates DAMON sysfs topology and live kdamond state, and clears kernel logs at start.

## Dependencies and Integration Points

It depends on root, DAMON sysfs, vaddr monitoring, dmesg access, and kernel debug reporting of BUG splats.

## Risks and Edge Cases

Clearing dmesg is intrusive. Lack of dmesg permission can affect detection. The test detects BUG strings, not all possible warnings or memory errors.

## Test Signals

Success is no `BUG` in dmesg after both update commands. Failure prints the triggering dmesg.
