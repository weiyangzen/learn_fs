<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math.c

## Purpose
This is the main classic FPU math-emulation dispatcher for PowerPC. It fetches a faulting instruction, decodes it, calls the appropriate operation handler, updates FPSCR/CR/register state, and advances NIP.

## Important APIs, types, and functions
Externally visible entry point is `int do_mathemu(struct pt_regs *regs)`. Static `record_exception` maps soft-fp exception flags to FPSCR status, summary, and enabled-exception bits. The file declares handler prototypes through `FLOATFUNC` and defines opcode/type constants for D, DU, X, XE, XEU, arithmetic, compare, and FPSCR operations.

## Control flow
`do_mathemu` fetches the 32-bit instruction from user NIP, selects a function pointer and operand layout by primary/minor opcode, computes FPR and effective-address operands, flushes live FP state to `thread_struct`, invokes the handler, mirrors FPSCR condition bits to CR1 when Rc is set, records exceptions, handles update-form base register writes, and advances NIP by four. Illegal or unknown opcodes return `-ENOSYS`; user fetch faults return `-EFAULT`; enabled FP exceptions return `1`.

## State and persistence behavior
It mutates `current->thread.TS_FPR`, `regs->ccr`, update-form GPRs, `regs->nip`, and global per-thread soft-fp FPSCR state. Memory load/store handlers can copy to/from user addresses.

## Dependencies and integration points
It integrates with exception handling for unavailable/unimplemented FP instructions, soft-fp headers, `asm/sfp-machine.h`, `flush_fp_to_thread`, and all per-instruction handler files in this directory.

## Risks and edge cases
Risks include exact opcode decoding, update-form legality, using raw `void *` operands for integer immediates, exception enable semantics, and keeping hardware FP state coherent with saved thread state. It only handles 32-bit classic FPU instructions, not prefixed or VSX forms.

## Test signals
Signals are successful emulation of FP unavailable traps, correct NIP advancement, expected FPSCR/CR state, and `-ENOSYS` for illegal instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/math.c -->
