# sources/distributed-fs/ceph-client/tools/objtool/arch/x86/decode.c

Purpose: full x86 objtool decoder and architecture adapter. It uses kernel x86 instruction decoding to classify control flow, stack effects, ftrace calls, retpoline/rethunk symbols, relocation semantics, and generated patch bytes.

Important APIs/types/functions: `arch_decode_instruction()` is the main opcode decoder; `arch_adjusted_addend()` and `arch_insn_adjusted_addend()` normalize relocation addends; `arch_pc_relative_reloc()` and `arch_absolute_reloc()` classify relocations; `arch_nop_insn()`/`arch_ret_insn()` provide patch bytes; `arch_decode_hint_reg()` maps ORC hint registers; `arch_is_retpoline()`, `arch_is_rethunk()`, and `arch_is_embedded_insn()` identify x86 thunk symbols.

Control flow: after detecting 32-bit versus 64-bit ELF, the file decodes one instruction with `insn_decode()`, unpacks REX/ModRM/SIB fields, and switches on primary opcode. It emits stack ops for pushes, pops, calls, `leave`, RSP/RBP moves, stack arithmetic, and selected memory loads/stores. It classifies calls, returns, dynamic jumps, conditional jumps, syscalls/sysrets, STAC/CLAC, CLD/STD, traps, bugs, ENDBR, NOPs, and RIP-relative LEA.

State and persistence behavior: writes instruction metadata and allocated stack-op lists. It may add pv_ops targets through `objtool_pv_add()` when decoding special `.init.text` paravirt writes under noinstr mode. It does not write ELF bytes directly; generated NOP/RET bytes are used by shared patching code.

Dependencies and integration points: embeds kernel `inat.c`/`insn.c`, uses x86 nops, ORC types, objtool ELF/check/builtin APIs, and x86 relocation constants. Its output is central to `check.c` validation, metadata generation, disassembly, and patch-hack paths.

Risks: x86 instruction coverage is intentionally focused on control-flow and stack-relevant behavior; new compiler patterns can evade stack-op modeling. Complex SIB addressing is skipped unless simple enough. Notrack prefixes on indirect branches warn. Addend adjustment around PC-relative relocations and `__pa_symbol()` is subtle and high risk.

Test signals: objtool x86 tests should cover prologues, DRAP, stack swizzles, alternatives, retpoline/rethunk, IBT ENDBR, noinstr paravirt, relocation addends, NOP/RET patching lengths, and disassembly of RIP-relative references.
