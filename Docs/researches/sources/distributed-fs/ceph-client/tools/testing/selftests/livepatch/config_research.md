# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/config

## Purpose

`livepatch/config` declares the minimum kernel configuration expected by the livepatch selftests.

## Important APIs, Types, and Functions

It lists `CONFIG_LIVEPATCH=y` and `CONFIG_DYNAMIC_DEBUG=y`.

## Control Flow and State

The file contains declarative config requirements only. It does not execute and writes no state.

## Dependencies and Integration Points

It integrates with kselftest config checking and with the shell harness, which needs livepatch sysfs/debug output and dynamic debug controls.

## Risks and Test Signals

Risks are missing prerequisites causing confusing runtime skips or failures. Signals are config checks passing and `functions.sh` being able to manipulate dynamic debug and livepatch sysfs.
