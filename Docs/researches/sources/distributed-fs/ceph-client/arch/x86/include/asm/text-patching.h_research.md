<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/text-patching.h

Purpose: declares and implements x86 runtime text patching primitives and instruction emulation helpers. Important APIs include `text_poke()`, `text_poke_copy()`, `text_poke_kgdb()`, `text_poke_bp()`, `smp_text_poke_*()`, opcode size constants, `text_opcode_size()`, `text_gen_insn()`, `__text_gen_insn()`, and INT3 emulation helpers for jmp/call/ret/jcc.

Control flow: patching code writes new instruction bytes using safe text mappings or breakpoint-assisted patching, synchronizes CPUs, and uses INT3 handlers to emulate instructions while patching is in progress. Instruction generators compute relative displacements for CALL/JMP/JMP8 and verify range constraints.

State and persistence: mutates kernel text and uses `text_poke_mm`/temporary mapping addresses after boot. Dependencies include alternatives, static calls, ftrace/kprobes, KGDB, SMP synchronization, `pt_regs`, instruction encoding, and memory permissions.

Risks: patching live text is high risk: wrong displacement, instruction length, CPU synchronization, or INT3 emulation corrupts control flow. Test signals include alternatives, ftrace, kprobes, static calls, jump labels, livepatch-style stress, SMP patch batching, KGDB breakpoints, and objtool validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/text-patching.h -->
