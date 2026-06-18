# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/Makefile

## Purpose

This Makefile registers Python kselftests for x86 bug mitigation behavior, focused here on indirect target selection (ITS).

## Important APIs, Types, and Functions

It sets `TEST_PROGS := its_sysfs.py its_permutations.py its_indirect_alignment.py its_ret_alignment.py` and `TEST_FILES := common.py`, then includes `../../lib.mk`.

## Control Flow

kselftest copies/runs the four Python programs and installs `common.py` as supporting data. Build compilation is not involved.

## State and Persistence Behavior

Only kselftest output/copy state is produced. The tests themselves may create runtime logs, but this Makefile does not.

## Dependencies and Integration Points

It integrates Python tests with kselftest. The Python tests depend on kernel vulnerability sysfs, optional vmlinux/debug data, drgn, pyelftools, capstone, and virtme-ng.

## Risks and Edge Cases

Missing `common.py` would break all tests. Dependencies are runtime Python modules rather than Makefile dependencies, so failures are handled as test skips or runtime errors by scripts.

## Test Signals

kselftest should enumerate all four Python programs and make `common.py` available in the test directory.
