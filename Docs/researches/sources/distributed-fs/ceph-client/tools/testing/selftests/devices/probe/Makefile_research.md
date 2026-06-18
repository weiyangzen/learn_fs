# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/Makefile

## Purpose

This Makefile registers the discoverable-device probe test and board database with kselftest.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := test_discoverable_devices.py`, `TEST_FILES := boards`, and includes `../../lib.mk`.

## Control Flow

Kselftest runs the Python probe script and installs the `boards` directory as data.

## State and Persistence Behavior

The Makefile itself has no runtime state.

## Dependencies and Integration Points

It integrates platform-specific YAML device descriptions with the devices selftest framework.

## Risks and Edge Cases

Missing `boards` data at install time makes the runtime script fail to find a matching board file.

## Test Signals

Successful packaging includes the Python script and board YAML directory.
