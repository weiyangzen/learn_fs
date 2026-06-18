# sources/distributed-fs/ceph-client/tools/testing/selftests/livepatch/test_modules/Makefile

## Purpose

`test_modules/Makefile` builds and cleans all kernel modules used by the livepatch selftests.

## Important APIs, Types, and Functions

It defines `TESTMODS_DIR`, default `KDIR`, an `obj-m` list covering all `test_klp_*` modules, and `modules`/`clean` targets that recurse into the kernel build tree with `KBUILD_EXTMOD=$(TESTMODS_DIR)`.

## Control Flow and State

If `KDIR` exists, `make modules` builds the modules and `make clean` removes generated module artifacts. If `KDIR` is missing, both targets skip the kernel recursion instead of failing.

## Dependencies and Integration Points

It depends on a configured kernel build directory, kbuild module infrastructure, and the parent livepatch Makefile's `TEST_GEN_MODS_DIR`.

## Risks and Test Signals

Risks include silent missing modules when `KDIR` does not exist and stale module lists. Signals are generated `.ko` files for every listed module and clean removal through kbuild.
