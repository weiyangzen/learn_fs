# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/error_logs/Makefile

## Purpose

This Makefile registers the device error log scanner as a kselftest program.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := test_device_error_logs.py` and includes `../../lib.mk`.

## Control Flow

The kselftest framework runs the Python script.

## State and Persistence Behavior

No runtime state is stored by the Makefile.

## Dependencies and Integration Points

It integrates with devices selftests and common kselftest packaging.

## Risks and Edge Cases

If the Python script is not executable or dependencies are missing, the kselftest run fails.

## Test Signals

The Makefile succeeds when the script is installed/runnable by kselftest.
