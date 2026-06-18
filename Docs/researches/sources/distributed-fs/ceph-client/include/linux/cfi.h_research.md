# sources/distributed-fs/ceph-client/include/linux/cfi.h

## Purpose

`cfi.h` declares Clang Control Flow Integrity support hooks for reporting CFI failures, reading function type hashes, identifying trap sites, and finalizing module CFI metadata.

## Important APIs, Types, and Functions

Under `CONFIG_CFI`, it exposes `cfi_warn`, `report_cfi_failure()`, `report_cfi_failure_noaddr()`, `cfi_get_offset()`, `cfi_get_func_hash()`, and BPF hash symbols `cfi_bpf_hash` and `cfi_bpf_subprog_hash`. Under `CONFIG_ARCH_USES_CFI_TRAPS`, it declares `is_cfi_trap()` and possibly `module_cfi_finalize()`. Fallback stubs return neutral values when features are disabled.

## Control Flow

When an indirect-call CFI check fails, architecture trap or bug handling calls the report helpers. Hash lookup reads the compiler-emitted KCFI type id located before a function entry, with architecture overrides allowed for nondefault prefix offsets. Module load may finalize CFI trap metadata.

## State and Persistence Behavior

Runtime state includes `cfi_warn` policy, read-only type hash symbols, and module CFI metadata. No filesystem persistence is owned.

## Dependencies and Integration Points

It includes bug handling, module declarations, and architecture CFI hooks. It integrates with compiler-emitted KCFI metadata, BPF indirect call checks, module loading, and architecture exception handling.

## Risks and Edge Cases

`cfi_get_func_hash()` reads memory before a function pointer and returns zero on fault; wrong architecture offset breaks hash matching. Disabled-config stubs must compile away safely. Module finalization is architecture-dependent.

## Test Signals

Build with and without `CONFIG_CFI`, test deliberate CFI failures in warn/panic modes, validate BPF type hashes, load/unload modules with CFI traps, and check hash reads for valid and invalid function pointers.
