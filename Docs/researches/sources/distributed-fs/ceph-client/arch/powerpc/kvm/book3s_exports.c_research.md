# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_exports.c

## Purpose

`book3s_exports.c` is a small symbol-export file for Book3S KVM entry trampolines. It makes the low-level guest-entry trampoline symbols visible to loadable KVM variants when the corresponding PR or HV Book3S implementation can be built as a module or used across compilation units.

## Important APIs, Types, And Functions

The file exports `kvmppc_hv_entry_trampoline` when `CONFIG_KVM_BOOK3S_HV_POSSIBLE` is enabled and exports `kvmppc_entry_trampoline` when `CONFIG_KVM_BOOK3S_PR_POSSIBLE` is enabled. Both are exported with `EXPORT_SYMBOL_GPL`, so consumers must be GPL-compatible modules.

## Control Flow

There is no runtime control flow beyond module symbol registration. The preprocessor selects which exports exist based on the configured Book3S KVM modes.

## State And Persistence Behavior

The file has no mutable runtime state and no persistent storage behavior. Its only effect is on the kernel module symbol table.

## Dependencies And Integration Points

It includes the KVM PowerPC and Book3S headers that declare the trampoline symbols. It integrates with architecture assembly entry code and the Linux module loader. HV and PR code that branches through these trampolines relies on these exports when linked modularly.

## Risks

The main risk is configuration or declaration drift: exporting a trampoline only when the corresponding implementation is possible must match the build system and symbol definitions. Removing or renaming these exports can break module loading even though the file has no direct runtime behavior.

## Test Signals

Build signals are the key checks: Book3S PR-only, HV-only, and combined configurations should link without unresolved trampoline symbols. Runtime module-load tests should confirm the KVM module loads and guest entry reaches the assembly trampoline rather than failing during relocation.
