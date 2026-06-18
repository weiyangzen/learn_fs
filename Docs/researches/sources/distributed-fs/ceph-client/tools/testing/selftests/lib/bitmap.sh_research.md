# sources/distributed-fs/ceph-client/tools/testing/selftests/lib/bitmap.sh

## Purpose

`bitmap.sh` is the kselftest wrapper for the kernel bitmap library test module.

## Important APIs, Types, and Functions

It invokes `../kselftest/module.sh "bitmap" test_bitmap`, delegating module loading, result interpretation, and skip/fail handling to the shared module test helper.

## Control Flow and State

The script has no branching of its own. It executes `module.sh` with the human-readable test name and module name. Runtime state is whatever `module.sh` creates while loading and unloading `test_bitmap`.

## Dependencies and Integration Points

It depends on `test_bitmap` being buildable/loadable as a kernel module and on `module.sh` existing in the selftests tree.

## Risks and Test Signals

Risks are missing module support or stale module names. Signals come from `module.sh`: pass when the module test completes successfully, skip when prerequisites are absent, and fail on module test errors.
