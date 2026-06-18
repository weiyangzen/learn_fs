# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/ksft_ksm.sh

## Purpose
Wrapper entry point for the MM selftest `ksm` category.

## Important APIs, types, and functions
The script invokes `./run_vmtests.sh -t ksm` with shell exit-on-error.

## Control flow
Delegates to the runner, which handles KSM tests and sysfs setup.

## State and persistence behavior
No local state; underlying KSM tests may modify `/sys/kernel/mm/ksm` controls.

## Dependencies and integration points
Requires KSM kernel support, runner script, and built KSM test binaries.

## Risks and edge cases
KSM sysfs permission or disabled kernel support can lead to skips/failures in the delegated target.

## Test signals
Wrapper success means the `ksm` target returned success.
