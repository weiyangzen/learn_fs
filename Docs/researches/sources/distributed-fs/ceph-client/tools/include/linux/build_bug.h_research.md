# sources/distributed-fs/ceph-client/tools/include/linux/build_bug.h

## Purpose

This header implements kernel-style compile-time assertion and build-bug helpers for tools builds.

## APIs, State, and Dependencies

It defines `BUILD_BUG_ON_ZERO`, `BUILD_BUG_ON_NOT_POWER_OF_2`, `BUILD_BUG_ON_INVALID`, `BUILD_BUG_ON_MSG`, `BUILD_BUG_ON`, `BUILD_BUG`, optional-message `static_assert`, and `ASSERT_STRUCT_OFFSET`. It depends on compiler assertion support from `<linux/compiler.h>` and uses `offsetof` where the offset assertion macro is used. There is no runtime state.

## Risks and Test Signals

These macros are intentionally compile-breaking; portability depends on compiler support for `_Static_assert` and attributes. Tests should include compile-pass and compile-fail cases for power-of-two, struct offsets, and constant-expression assertions.
