# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/with_stress.sh

## Purpose

`with_stress.sh` is a bash harness that runs a command repeatedly while background cgroup stressors operate. The complete 101-line script was read.

## Important APIs, Types, and Functions

It defines `stress_fork()`, `stress_subsys()`, and `init_and_check()`, plus arrays `stresses` and `stress_pids`, and options `-c`, `-d`, `-h`, and `-s`.

## Control Flow

The script parses options, finds cgroup2, checks that the chosen controller can be enabled and disabled, starts requested stress functions in the background, repeatedly runs the remaining command until duration expires or the command fails, then terminates and waits for stress processes before returning the command status.

## State and Persistence Behavior

`stress_fork()` repeatedly launches `/usr/bin/true`. `stress_subsys()` repeatedly writes `+controller` and `-controller` to the root `cgroup.subtree_control`. State is intended to be transient, but the last controller state depends on where the loop is killed.

## Dependencies and Integration Points

It depends on bash, cgroup v2, a writable root `cgroup.subtree_control`, `/usr/bin/true`, `date`, `mount`, `awk`, and the command under test.

## Risks and Edge Cases

Killing stress loops may leave the selected controller enabled or disabled. The command is invoked as `$*`, so arguments with spaces are not preserved robustly. If a stressor exits early, the harness does not notice until cleanup. Stress can create false failures in timing-sensitive tests.

## Test Signals

Exit status mirrors the repeatedly executed command. Successful use demonstrates that a cgroup test survives concurrent fork and subtree-control churn for the configured duration.
