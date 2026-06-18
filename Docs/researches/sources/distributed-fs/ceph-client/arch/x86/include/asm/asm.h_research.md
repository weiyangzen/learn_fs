
# sources/distributed-fs/ceph-client/arch/x86/include/asm/asm.h

Purpose: common x86 assembly formatting, register-name, pointer-size, exception-table, and inline-assembly helper macros for both C inline asm and `.S` files.

Important APIs and control flow: `__ASM_FORM*`, `__ASM_SEL*`, `__ASM_SIZE`, `_ASM_REG`, `_ASM_PTR`, `_ASM_ALIGN`, and `_ASM_ARG*` abstract 32/64-bit syntax. `rip_rel_ptr()` materializes RIP-relative pointers. `_ASM_EXTABLE*` emits relative exception-table entries with fixup types, and `_ASM_EXTABLE_TYPE_REG` validates register operands through generated assembler macros. `ASM_OUTPUT`, `ASM_INPUT`, `COMMA`, `ASM_CALL_CONSTRAINT`, and `EAX_EDX_*` hide compiler constraint differences.

State, dependencies, and risks: there is no runtime state, but generated sections such as `__ex_table` and `_kprobe_blacklist` are persistent binary metadata. Dependencies include generated offsets, extable types, annotate/stringify helpers, and architecture register conventions. Risks include malformed inline asm strings, wrong register width under mixed 32/64-bit code, and exception table entries pointing to invalid fixups. Test signals are build coverage, objtool, exception-fixup paths, and fault-injection for uaccess/MSR operations.
