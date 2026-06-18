# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/wait_inotify.c

## Purpose

`wait_inotify.c` is a small helper program that blocks until an inotify modify event occurs on a specified cgroup file. It is used by cpuset partition root state tests. The complete 87-line file was read.

## Important APIs, Types, and Functions

It defines `usage`, global `file` and `verbose`, `fail_message()`, and `main()`.

## Control Flow

`main()` parses optional `-v`, validates exactly one file argument, opens the file to ensure it exists, creates an inotify fd, adds an `IN_MODIFY` watch, then polls up to 10 seconds per iteration until `POLLIN` is observed. Verbose mode reads and prints the number of inotify events before exit.

## State and Persistence Behavior

It does not mutate the watched file. It creates a transient inotify watch and closes the fd before exiting.

## Dependencies and Integration Points

It depends on libc, inotify, poll, and cgroup files. `test_cpuset_prs.sh` shells out to this binary in its invalid-partition inotify test.

## Risks and Edge Cases

`fail_message()` passes caller-controlled `msg` as a format string with `file`; current callers use fixed strings. The option parsing mutates `argv`/`argc` manually after `getopt()`, which works for the simple `-v` use but is unusual. Poll timeout loops forever on repeated timeouts, so a missing event can hang until test harness timeout.

## Test Signals

The helper succeeds by exiting 0 after an `IN_MODIFY` event; verbose mode additionally reports how many event records were read.
