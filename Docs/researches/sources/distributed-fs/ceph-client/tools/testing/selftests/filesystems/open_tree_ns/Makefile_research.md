# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/open_tree_ns/Makefile

## Purpose

This Makefile builds the `open_tree_ns_test` binary for `OPEN_TREE_NAMESPACE` behavior.

## Important APIs, Types, and Functions

It declares warning, optimization, debug, and kernel header CFLAGS, `TEST_GEN_PROGS := open_tree_ns_test`, local headers `../wrappers.h ../statmount/statmount.h ../utils.h`, and links `open_tree_ns_test` with `../utils.c`.

## Control Flow, State, and Persistence

There is no runtime flow. The Makefile wires local support code into the kselftest binary.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on current kernel headers, wrappers, statmount helpers, utils, and kselftest rules. It integrates open_tree namespace tests into the filesystems suite. Risks are missing newer constants in older headers. Passing signal is successful generation of `open_tree_ns_test`.
