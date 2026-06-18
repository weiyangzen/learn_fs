# sources/distributed-fs/ceph-client/drivers/input/tests/Makefile

## Purpose
This Makefile builds input-core KUnit tests.

## Important APIs, types, and functions
It contains one Kbuild assignment: `obj-$(CONFIG_INPUT_KUNIT_TEST) += input_test.o`.

## Control flow
When `CONFIG_INPUT_KUNIT_TEST` is enabled, Kbuild compiles `input_test.c` into the test object. Otherwise no input tests from this directory are built.

## State and persistence
There is no runtime state in this Makefile. Test inclusion is controlled by kernel configuration.

## Dependencies and integration points
The file connects the input test source to KUnit-enabled kernel builds. It must stay aligned with the Kconfig symbol that defines `CONFIG_INPUT_KUNIT_TEST`.

## Risks
Adding additional tests without updating this Makefile will leave them unbuilt. Renaming the Kconfig symbol or test source requires synchronized changes.

## Test signals
Enable `CONFIG_INPUT_KUNIT_TEST` and verify that the `input_core` KUnit suite is present and runs.
