<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dwarf.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dwarf.h

Purpose: Defines assembler CFI macro aliases for s390 assembly.

Important APIs/types/functions: `CFI_STARTPROC`, `CFI_ENDPROC`, `CFI_DEF_CFA_OFFSET`, `CFI_ADJUST_CFA_OFFSET`, `CFI_RESTORE`, `CFI_REL_OFFSET`, and conditional `CFI_VAL_OFFSET`. Source-visible declarations include: #define _ASM_S390_DWARF_H; #define CFI_STARTPROC .cfi_startproc; #define CFI_ENDPROC .cfi_endproc; #define CFI_DEF_CFA_OFFSET .cfi_def_cfa_offset; #define CFI_ADJUST_CFA_OFFSET .cfi_adjust_cfa_offset; #define CFI_RESTORE .cfi_restore; #define CFI_REL_OFFSET .cfi_rel_offset; #define CFI_VAL_OFFSET .cfi_val_offset; #define CFI_VAL_OFFSET #.

Control flow: Assembly files use these aliases to emit DWARF call-frame information, with optional macros becoming no-ops when unsupported.

State and persistence behavior: State is debug/unwind metadata emitted into object files.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates unwinder, objtool-like validation, crash dumps, and assembly entry code..

Risks: Wrong CFI causes unreliable stack traces and exception unwinding.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 38 lines, 954 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dwarf.h -->
