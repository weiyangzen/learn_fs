# sources/distributed-fs/ceph-client/tools/include/linux/cfi_types.h

## Purpose

This header provides Clang CFI/KCFI type annotation macros for kernel-derived assembly and C code in tools builds.

## APIs, State, and Dependencies

For assembly with `CONFIG_CFI`, it defines `__CFI_TYPE`, `SYM_TYPED_ENTRY`, `SYM_TYPED_START`, and `SYM_TYPED_FUNC_START` to emit type identifiers before symbols. Without CFI, typed starts map to normal symbol starts. For C with `CONFIG_CFI`, `DEFINE_CFI_TYPE` emits a read-only type-id object referencing `__kcfi_typeid_<func>`. There is no normal runtime state, but emitted objects and assembly labels affect binary metadata.

## Risks and Test Signals

The macros rely on compiler-emitted KCFI symbols and correct assembly syntax. Incorrect use can break indirect-call checking or symbol layout. Tests should build assembly and C users with and without `CONFIG_CFI` and inspect object symbols.
