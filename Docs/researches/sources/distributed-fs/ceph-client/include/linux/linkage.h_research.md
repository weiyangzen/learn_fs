# sources/distributed-fs/ceph-client/include/linux/linkage.h

Purpose: defines generic C/assembly linkage, syscall aliasing, page-aligned section, and assembler symbol annotation macros used throughout the kernel.

Important APIs and types: C-side macros include `asmlinkage`, `cond_syscall`, `SYSCALL_ALIAS`, `__page_aligned_data`, `__page_aligned_bss`, and `asmlinkage_protect()`. Assembly-side macros define symbol types, linkage kinds, alignment, deprecated `ENTRY`/`END` wrappers, generic `SYM_ENTRY`/`SYM_START`/`SYM_END`/`SYM_ALIAS`, function/code/data start/end/alias macros, and data label helpers.

Control flow: C syscall and low-level code use linkage attributes/aliases; assembly files wrap symbols with `SYM_*` macros so ELF type/size/alignment and objtool/debug info are correct.

State and persistence: no runtime state; it controls compiled object metadata and sections.

Dependencies and integration points: depends on compiler types, stringify/export helpers, and arch `asm/linkage.h`. Integrates generic kernel code with architecture assembly, linker scripts, syscall fallback, objtool, tracing, and module symbol metadata.

Risks and test signals: risks include malformed assembly due to `ASM_NL`, wrong symbol type/size, weak syscall alias errors, function alignment regressions, and arch override conflicts. Test allmodconfig builds, objtool validation, syscall tables with missing optional syscalls, module symbol resolution, and assembly debug info.
