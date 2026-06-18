# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/Makefile

## Purpose

`livepatch/Makefile` registers the livepatch selftest scripts, helper binary, module build directory, settings file, and common build behavior.

## Important APIs, Types, and Functions

It sets `TEST_GEN_FILES := test_klp-call_getpid`, `TEST_GEN_MODS_DIR := test_modules`, `TEST_PROGS_EXTENDED := functions.sh`, `TEST_PROGS` for the livepatch shell tests, `TEST_FILES := settings`, and includes `../lib.mk`.

## Control Flow and State

The common `lib.mk` rules compile `test_klp-call_getpid`, build kernel modules by recursing into `test_modules`, and expose each shell script to kselftest. Generated state is the helper binary and `.ko` files.

## Dependencies and Integration Points

It depends on a configured kernel build tree for modules, the livepatch scripts, `functions.sh`, and the test modules directory.

## Risks and Test Signals

Risks include omitting a script or module directory from the build graph, breaking install of `settings`, or running scripts without compiled modules. Signals are `make` producing helper/module artifacts and kselftest enumerating all listed scripts.
