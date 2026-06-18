<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/trampoline.S -->
# sources/distributed-fs/ceph-client/arch/s390/boot/trampoline.S

Purpose: Provides the final boot trampoline symbol used to enter the decompressed kernel with a supplied PSW.

Important APIs/types/functions: Defines `SYM_CODE_START(jump_to_kernel)` and `SYM_CODE_END(jump_to_kernel)`. The implementation executes `lpswe 0(%r2)`.

Control flow: The caller passes a pointer to a PSW in register 2 according to the s390 calling convention. The trampoline loads that PSW and never returns. It is intentionally separate from `__load_psw()` so GDB's `lx-symbols` breakpoint behavior does not collide with this transition.

State and persistence: No state is stored; CPU execution state changes to the loaded PSW.

Dependencies and integration points: Called from `startup_kernel()` after page tables, bootdata, alternatives, and stack protector setup are complete. It depends on the PSW structure layout and s390 linkage macros.

Risks: Any calling convention mismatch or invalid PSW causes immediate boot failure. The symbol name matters for debugger behavior.

Test signals: Successful transition from decompressor to kernel entry with DAT enabled, debugger breakpoint behavior, and objdump validation of the single `lpswe` sequence.

Source read size: 9 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/trampoline.S -->
