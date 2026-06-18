# sources/distributed-fs/ceph-client/kernel/cfi.c

## Purpose

`cfi.c` implements common kernel support for Clang Control Flow Integrity failure reporting, CFI type hashes used by BPF JIT code, and optional trap-address recognition for architectures that emit KCFI trap tables. It decides whether a CFI violation is reported as a warning or a fatal bug according to `CONFIG_CFI_PERMISSIVE`.

## Important APIs, types, and functions

- `cfi_warn` is `__ro_after_init` and defaults from `IS_ENABLED(CONFIG_CFI_PERMISSIVE)`.
- `report_cfi_failure()` logs the failed call site, optional target symbol, and expected type hash, then either calls `__warn()` and returns `BUG_TRAP_TYPE_WARN` or returns `BUG_TRAP_TYPE_BUG`.
- `DEFINE_CFI_TYPE(cfi_bpf_hash, __bpf_prog_runX)` and `DEFINE_CFI_TYPE(cfi_bpf_subprog_hash, __bpf_callback_fn)` publish KCFI type hashes for `bpf_func_t` and `bpf_callback_t` compatible call targets.
- Under `CONFIG_ARCH_USES_CFI_TRAPS`, `trap_address()` resolves relative `s32` trap entries, `is_trap()` scans a trap-table range, and `is_cfi_trap()` checks built-in and module trap tables.
- Under `CONFIG_MODULES`, `module_cfi_finalize()` finds a module's `__kcfi_traps` section and records the start/end pointers in `struct module`; `is_module_cfi_trap()` looks up the containing module under RCU.

## Control flow

On a CFI failure, architecture-specific trap or call checking code calls `report_cfi_failure()`. The function emits a precise kernel log message and returns a trap disposition to the generic bug handling path. In permissive mode it also emits a warning at the faulting address; otherwise the caller treats the failure as a bug.

For trap recognition, built-in kernel trap tables are provided by linker symbols `__start___kcfi_traps` and `__stop___kcfi_traps`. Module loading calls `module_cfi_finalize()` after ELF sections are available; it searches section names for `__kcfi_traps` and stashes the address range. Later `is_cfi_trap()` scans the built-in table first and then the relevant module table.

## State and persistence behavior

`cfi_warn` becomes read-only after init. Module state persists in `mod->kcfi_traps` and `mod->kcfi_traps_end` for each loaded module. The BPF CFI type hash variables are static kernel data emitted by `DEFINE_CFI_TYPE`; they are used as constants by architecture-specific BPF JIT implementations. No filesystem or user-visible persistent state is written.

## Dependencies and integration points

The file integrates with compiler-emitted CFI metadata (`linux/cfi_types.h`), kernel bug handling (`enum bug_trap_type`, `__warn()`), BPF JITs (`linux/bpf.h`), the module loader, ELF section headers, RCU-protected module address lookup, and linker-provided KCFI section boundaries. Architecture code supplies the actual trap handling and calls into `is_cfi_trap()` where supported.

## Risks and edge cases

- `is_trap()` linearly scans trap ranges. Very large trap tables could make fault-path lookup cost visible, though the path is exceptional.
- `module_cfi_finalize()` relies on exact section naming and section address/size correctness. Missing or malformed `__kcfi_traps` data leaves module trap detection disabled for that module.
- `report_cfi_failure()` may omit target details when the architecture cannot supply them; diagnostics remain useful but less specific.
- Permissive mode intentionally allows execution to continue after warning. That is valuable for bring-up but reduces hardening.
- BPF JIT code must use the published hashes consistently with the function pointer types; mismatches can cause false CFI failures.

## Test signals

Build tests should cover CFI enabled with and without `CONFIG_CFI_PERMISSIVE`, with and without `CONFIG_MODULES`, and on architectures with `CONFIG_ARCH_USES_CFI_TRAPS`. Runtime signals include intentional KCFI violation tests that verify warning versus bug behavior, module load tests confirming `__kcfi_traps` range population, and BPF JIT tests confirming generated indirect call targets carry the expected `cfi_bpf_hash` or `cfi_bpf_subprog_hash`.
