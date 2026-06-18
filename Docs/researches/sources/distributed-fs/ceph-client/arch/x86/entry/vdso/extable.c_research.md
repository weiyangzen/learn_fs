## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/extable.c

Purpose: kernel-side fixup logic for exceptions raised inside vDSO code, currently important for SGX vDSO enclave entry.

Important APIs/types: `struct vdso_exception_table_entry` with relative `insn` and `fixup` offsets, and `fixup_vdso_exception(struct pt_regs *regs, int trapnr, unsigned long error_code, unsigned long fault_addr)`.

Control flow: rejects debug and breakpoint traps, verifies the current mm has a vDSO mapping, computes the runtime base from `current->mm->context.vdso + image->extable_base`, scans `image->extable`, and when `regs->ip` matches a protected instruction rewrites RIP to the fixup and passes trap metadata in DI/SI/DX.

State/persistence: reads `mm->context.vdso`, `vdso_image`, and image exception-table metadata; mutates only the faulting task's `pt_regs`.

Integration points: vDSO image metadata, `_ASM_VDSO_EXTABLE_HANDLE` from `extable.h`, SGX vDSO assembly, x86 trap handling, and process mm context.

Risks: wrong relative offsets would send user execution to invalid vDSO code. Suppressing DB/BP fixup is intentional because enclave origin cannot be identified. Test signals include SGX enclave exception tests, vDSO extable readelf checks, trap fault injection, and mm/vDSO remap tests.
