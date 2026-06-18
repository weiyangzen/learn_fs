# sources/distributed-fs/ceph-client/arch/x86/include/asm/linkage.h

## Purpose
Defines x86 assembly linkage, alignment, return, CFI, and symbol-start macros used by assembly and low-level C code.

## Important APIs, Types, And Functions
Key macros include `notrace`, `_THIS_IP_`, x86-32 `asmlinkage`, `__ALIGN`, `FUNCTION_PADDING`, `ASM_FUNC_ALIGN`, `SYM_F_ALIGN`, assembler/C `RET` and `ASM_RET`, `__CFI_TYPE()`, `SYM_TYPED_FUNC_START()`, `SYM_FUNC_START*()`, `SYM_FUNC_ALIAS_MEMFUNC`, and `SYM_PIC_ALIAS()`. Return macros route through `__x86_return_thunk` under rethunk mitigation or append `int3` under SLS mitigation.

## Control Flow
The preprocessor selects alignment and padding based on `CONFIG_FUNCTION_ALIGNMENT`, `CONFIG_CALL_PADDING`, export/VDSO contexts, and mitigation options. Assembly entry macros then emit aligned symbols, ENDBR where needed, CFI type stubs, and safe return sequences.

## State And Persistence
No runtime state. It affects generated text layout, symbol tables, CFI metadata, and patchable padding.

## Dependencies And Integration Points
Depends on `linux/stringify.h` and `asm/ibt.h`. It integrates with objtool, kCFI, retbleed/SLS mitigations, alternative patching, exportable assembly routines, VDSO builds, and position-independent startup aliases.

## Risks And Edge Cases
Alignment or padding mistakes break alternatives, ftrace/livepatch expectations, kCFI symbol layout, or mitigation validation. The RET macro must stay consistent with `nospec-branch.h` thunks and build contexts that intentionally disable exports.

## Test Signals
Builds with kCFI, IBT, call padding, SLS, rethunk, VDSO, UML, and x86-32 should pass objtool validation and boot smoke tests.
