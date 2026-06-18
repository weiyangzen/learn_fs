# sources/distributed-fs/ceph-client/tools/testing/selftests/cpu-hotplug/Makefile

## Purpose

This Makefile wires the CPU hotplug shell test into kselftest.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := cpu-on-off-test.sh`, includes `../lib.mk`, and defines `run_full_test` to run the script with `-a` and print a pass/fail line.

## Control Flow

Kselftest infrastructure runs the script by default. The explicit `run_full_test` target performs full-scope online/offline cycling.

## State and Persistence Behavior

The Makefile has no runtime state; the script it invokes mutates CPU online sysfs state.

## Dependencies and Integration Points

It depends on the kselftest Makefile framework and a shell environment capable of running CPU sysfs writes as root.

## Risks and Edge Cases

`run_full_test` can offline all hotpluggable CPUs except one, which is more intrusive than the default limited test.

## Test Signals

Build/install success exposes `cpu-on-off-test.sh`; `run_full_test` reports pass when the script returns success.
