# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/tests.conf

## Purpose

This include provides common build, boot, test, and randconfig test definitions selected by a caller's `${TEST}` variable. It lets multiple machine configs share the same test matrix while overriding the machine-specific defaults elsewhere.

## Important APIs, Types, And Data

It uses immediate variables `BOOT_TYPE` and `RUN_TEST`, both defaulted when not already defined. The file declares conditional `TEST_START` blocks for `TEST == boot`, `build`, `randconfig`, `randconfig && MULTI`, and `test`. Key options are `TEST_TYPE`, `BUILD_TYPE=${BOOT_TYPE}` or `randconfig`, `BUILD_NOCLEAN=1`, `MIN_CONFIG`, `MAKE_CMD`, and `TEST=${RUN_TEST}`.

## Control Flow

`ktest.pl` includes the file after machine defaults are set. Exactly one or more sections are included depending on the config-time `${TEST}` and `${MULTI}` variables. Build and boot tests run a single kernel build path; randconfig creates ten iterations through `TEST_START ITERATE 10`; the multi randconfig adds a boot-only variant using a smaller min config and default `make`.

## State And Persistence Behavior

The include does not write state directly. It controls ktest state through generated test cases and repeated iteration counters. Randconfig tests create changing `.config` files and build artifacts in the configured output directory. `BUILD_NOCLEAN=1` preserves build products across many normal build/boot/test cases.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${CONFIG_DIR}`, `${SSH}`, machine paths, and build options. It integrates with ktest's `build`, `boot`, `test`, and `randconfig` handling. The default `RUN_TEST` assumes `hackbench` is installed and runnable over the configured SSH connection.

## Risks And Edge Cases

`BUILD_NOCLEAN=1` improves speed but can preserve stale generated artifacts. Randconfig tests require an appropriate `MIN_CONFIG`; without a network-capable config, the test variant may fail after boot because SSH never comes up. `${TEST}` is a config variable, while `TEST = ...` is a runtime command option; confusing the two can select the wrong workflow or command.

## Test Signals

Dry-run should show the intended `TEST_TYPE`, `BUILD_TYPE`, and repeated randconfig count. Runtime signals include successful build-only result banners, monitor logs reaching the configured success line for boot tests, and target command exit status for `TEST_TYPE=test`.
