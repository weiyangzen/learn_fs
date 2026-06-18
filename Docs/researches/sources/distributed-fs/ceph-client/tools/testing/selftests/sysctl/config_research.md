# sources/distributed-fs/ceph-client/tools/testing/selftests/sysctl/config

## Purpose
Declares the kernel module dependency for sysctl selftests.

## Important APIs, Types, And Functions
Contains `CONFIG_TEST_SYSCTL=m`, requesting the `test_sysctl` module that creates `/proc/sys/debug/test_sysctl` targets.

## Control Flow
No runtime control flow. `sysctl.sh` uses this file for user-facing skip guidance in built-in-only boot parameter tests.

## State And Persistence
No state.

## Dependencies And Integration Points
Integrated with `sysctl.sh` and kernel selftest config tooling.

## Risks
Some tests require the test sysctl support to be built in rather than loaded as a module, so this module config is not sufficient for every test case.

## Test Signals
Availability of the `test_sysctl` module and creation of the expected debug sysctl tree.
