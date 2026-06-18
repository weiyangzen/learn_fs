# File Research: sources/block-storage/mdadm/test

## Purpose
Top-level bash runner for the mdadm test suite.

## Main Responsibilities
- Locates the system `mdadm`, sets default test directories, device names, log paths, loop/LVM/disk mode, and control flags.
- Wraps `mdadm()` to capture stderr, zero components before create/build, settle udev, and temporarily raise speed limits for stop operations.
- Parses command-line options for test selection, raid type filters, logging, loop count, broken/big test skips, device backend, and setup/cleanup.
- Sources `tests/func.sh` after resolving test directory.
- Runs each test script in a subshell with `set -ex`, captures logs, checks dmesg unless the test injects errors, and handles skip/broken/keep-going behavior.
- Provides `setup` and `cleanup` modes.

## Integration
This script is the user-facing entry point for the shell tests under `tests/` and `clustermd_tests/`.

## Risks and Edge Cases
- It intentionally operates on system mdadm and real kernel md state; it requires root and a clean RAID environment.
- The wrapper zeros any non-md `/dev/` argument for create/build commands, so it is destructive outside a controlled test environment.
