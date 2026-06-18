<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_bits.c -->
# sources/distributed-fs/ceph-client/lib/tests/test_bits.c

## Purpose
KUnit and compile-time checks for bit construction and mask macros from `linux/bits.h`, especially typed `BIT_*`, `GENMASK*`, and input validation behavior.

## APIs, Types, and Functions
The file uses `_Generic` through `assert_type()` and `static_assert()` to validate result types and values for `BIT_U8()`, `BIT_U16()`, `BIT_U32()`, `BIT_U64()`, `GENMASK()`, `GENMASK_ULL()`, and typed `GENMASK_U8/U16/U32/U64()`. Runtime KUnit cases exercise `__GENMASK()`, `__GENMASK_ULL()`, `GENMASK()`, `GENMASK_ULL()`, `GENMASK_U128()` under `CONFIG_ARCH_SUPPORTS_INT128`, and `GENMASK_INPUT_CHECK()`.

## Control Flow, State, and Persistence
Compile-time assertions fire during build if macro types or constants change. Runtime tests are direct expectation checks over known mask ranges and over unknown variable inputs for `GENMASK_INPUT_CHECK()`. The `TEST_GENMASK_FAILURES` block intentionally contains invalid macro invocations for opt-in compile-failure testing. There is no runtime state.

## Dependencies and Integration
Depends on KUnit, `linux/bits.h`, and integer type definitions. It integrates with the `bits-test` KUnit suite and complements build-time macro diagnostics.

## Risks and Test Signals
Risks include architecture differences in `unsigned long` width, compiler behavior around constant expressions, and limited coverage for assembly users noted by the FIXME. Test signals are compile-time type/value assertions, runtime boundary masks at high bits, optional expected compile failures, and 128-bit checks when the architecture supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/test_bits.c -->
