# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/Makefile

## Purpose

This Makefile registers the cpufreq shell selftest suite with kselftest and lists helper files needed at runtime.

## Important APIs, Types, and Functions

It sets `TEST_PROGS := main.sh`, `TEST_FILES := cpu.sh cpufreq.sh governor.sh module.sh special-tests.sh`, and `EXTRA_CLEAN` for generated cpufreq/dmesg logs.

## Control Flow

The common `../lib.mk` handles installation and execution. `main.sh` is the only test program; the other shell files are sourced helpers.

## State and Persistence Behavior

The Makefile itself persists build/run metadata and cleanup targets. Runtime state is managed by the scripts.

## Dependencies and Integration Points

It integrates with kselftest and expects shell helpers to be copied beside `main.sh`.

## Risks and Edge Cases

If helper files are not listed in `TEST_FILES`, installed tests will fail at `source`. Cleanup only targets known log names.

## Test Signals

Successful kselftest packaging includes all helper scripts and cleans generated log artifacts.
