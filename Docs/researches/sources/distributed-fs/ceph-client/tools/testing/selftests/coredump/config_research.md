# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/config

## Purpose

This kselftest config declares the kernel features required by the coredump socket and stackdump tests.

## Important APIs, Types, and Functions

It requests `CONFIG_COREDUMP=y`, `CONFIG_NET=y`, and `CONFIG_UNIX=y`.

## Control Flow

There is no executable control flow. Kselftest/kernel config tooling reads the symbols to determine whether the running or target kernel can support the tests.

## State and Persistence Behavior

The file persists feature requirements only. It does not mutate runtime state.

## Dependencies and Integration Points

`CONFIG_COREDUMP` enables core dump infrastructure, while `CONFIG_NET` and `CONFIG_UNIX` are needed for AF_UNIX socket-based core dump delivery and socketpair/listener setup.

## Risks and Edge Cases

Missing symbols should cause skip or configuration failure rather than misleading runtime failures. The config does not express pidfd or debugfs-style requirements used by some helper calls.

## Test Signals

An environment satisfying these symbols can run the coredump tests; absent symbols predict failures opening socket core patterns or invoking coredump paths.
