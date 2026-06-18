# sources/distributed-fs/ceph-client/include/linux/annotate.h

## Purpose
Provides objtool annotation macros for assembly and inline assembly so the kernel can describe special control-flow, instrumentation, CFI, retpoline, ENDBR, and livepatch data cases.

## Important APIs, Types, And Functions
With `CONFIG_OBJTOOL`, `__ASM_ANNOTATE()` emits records into discardable annotate sections. C-facing macros include `ASM_ANNOTATE_LABEL()`, `ASM_ANNOTATE()`, `ASM_ANNOTATE_DATA()`, `ANNOTATE_NOENDBR`, `ANNOTATE_RETPOLINE_SAFE`, `ANNOTATE_INSTR_BEGIN/END`, `ANNOTATE_IGNORE_ALTERNATIVE`, `ANNOTATE_INTRA_FUNCTION_CALL`, `ANNOTATE_UNRET_BEGIN`, `ANNOTATE_REACHABLE`, `ANNOTATE_NOCFI_SYM`, and `ANNOTATE_DATA_SPECIAL`. Assembly mode defines `ANNOTATE` and `ANNOTATE_DATA` macros.

## Control Flow, State, And Persistence
The macros do not change runtime state. They add metadata sections consumed by objtool during build-time validation and discarded from the final runtime image as appropriate.

## Dependencies And Integration Points
Depends on `linux/objtool_types.h` for annotation type constants. Integrates with objtool, x86/arm64 assembly, retpoline validation, CFI validation, alternatives, instrumentation markers, and livepatch extraction.

## Risks And Test Signals
Annotations can suppress real control-flow or CFI issues if overused, especially `ANNOTATE_NOCFI_SYM`. Test signals are objtool warnings, build coverage with and without `CONFIG_OBJTOOL`, section emission inspection, and architecture assembly builds using the macros from both C and assembly contexts.
