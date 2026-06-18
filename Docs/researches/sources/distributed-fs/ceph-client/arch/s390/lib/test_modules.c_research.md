# sources/distributed-fs/ceph-client/arch/s390/lib/test_modules.c

## Purpose
KUnit test verifying s390 module loading handles a very large number of relocations against vmlinux symbols.

## Important APIs, Types, And Functions
`test_modules_many_vmlinux_relocs()` calls 10,000 generated helper functions through the `REPEAT_10000` macro and asserts that the accumulated result is `49995000`. The KUnit suite is named `modules_test_s390`.

## Control Flow And State
The test initializes `result` to zero, expands 10,000 calls to `test_modules_return_N()`, then compares the sum with the arithmetic-series expected value. There is no persistent runtime state.

## Dependencies And Integration
Depends on KUnit, Linux module support, and generated declarations from `test_modules.h` with definitions/exported symbols in `test_modules_helpers.c`. Built under `CONFIG_S390_MODULES_SANITY_TEST`.

## Risks And Test Signals
Risks include macro expansion size/compile-time cost, mismatch with helper return definitions, and brittle expected-sum assumptions if generated range changes. The test directly signals relocation handling correctness for modules with many vmlinux relocations.
