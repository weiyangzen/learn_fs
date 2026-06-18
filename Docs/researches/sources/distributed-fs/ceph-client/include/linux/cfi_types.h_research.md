# sources/distributed-fs/ceph-client/include/linux/cfi_types.h

## Purpose

`cfi_types.h` provides macros for annotating assembly functions and exporting CFI type identifiers so Clang KCFI can validate indirect calls involving assembly or special call targets.

## Important APIs, Types, and Functions

For assembly, it defines `__CFI_TYPE`, `SYM_TYPED_ENTRY`, `SYM_TYPED_START`, and `SYM_TYPED_FUNC_START`. For C under `CONFIG_CFI`, `DEFINE_CFI_TYPE(name, func)` emits a read-only-after-init `u32` initialized from `__kcfi_typeid_<func>` and forces the function to be addressable.

## Control Flow

There is no normal runtime flow. The macros affect assembly symbol layout and C object emission at compile/link time so runtime CFI checks can compare type ids.

## State and Persistence Behavior

The generated type-id objects live in `.data..ro_after_init`. Assembly annotations place a 4-byte type id before typed entry points when CFI is enabled.

## Dependencies and Integration Points

Assembly mode includes `linux/linkage.h`. C mode depends on compiler-generated `__kcfi_typeid_*` symbols and `__ADDRESSABLE`. It integrates with low-level architecture entry code, BPF, and other indirectly called assembly routines.

## Risks and Edge Cases

Missing annotations on indirectly called assembly functions can trigger CFI failures. Symbol names must match compiler-visible declarations. Section and alignment changes can break architecture expectations.

## Test Signals

Build assembly-heavy configurations with `CONFIG_CFI`, inspect emitted type ids, run indirect-call paths into annotated assembly, and test disabled-CFI builds where macros should reduce to normal symbol starts.
