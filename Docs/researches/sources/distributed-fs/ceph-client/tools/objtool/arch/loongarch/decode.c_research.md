# sources/distributed-fs/ceph-client/tools/objtool/arch/loongarch/decode.c

Purpose: LoongArch implementation of the objtool architecture contract. It classifies fixed-width LoongArch instructions, extracts branch immediates, emits stack operations for CFI tracking, exposes relocation sizing, and provides generated NOP/RET bytes.

Important APIs/types/functions: `arch_reg_name` maps CFI register numbers to LoongArch names. `arch_ftrace_match()` recognizes `_mcount`. `arch_jump_destination()` computes branch targets as `offset + immediate * 4`. `arch_decode_instruction()` is the central decoder and delegates to helpers for `reg0i26`, `reg1i21`, `reg2i12`, `reg2i14`, `reg2i16`, and `reg3` encodings. `arch_initial_func_cfi_state()` initializes CFA at SP with all saved registers undefined. `arch_reloc_size()` and `arch_jump_table_sym_offset()` adapt generic jump table handling to LoongArch relocation types.

Control flow: the decoder rejects non-LoongArch ELF machines, requires `LOONGARCH_INSN_SIZE`, initializes the instruction as `INSN_OTHER`, reads a `union loongarch_instruction`, and tries encoding-specific decoders in priority order. Calls/jumps/returns/traps/bugs/nops are assigned objtool `enum insn_type` values. Stack effects are represented as allocated `struct stack_op` nodes so `check.c` can update CFA and saved-register state without knowing LoongArch opcodes.

State and persistence behavior: this file mutates only in-memory `struct instruction` fields and per-function `frame_pointer` state. It returns static buffers for generated NOP/RET instruction bytes and does not write ELF data directly; ELF writes occur later through shared objtool code.

Dependencies and integration points: depends on LoongArch kernel instruction definitions in `asm/inst.h`, ORC register constants in `asm/orc_types.h`, objtool CFI/ELF/check APIs, and `arch/elf.h` relocation aliases. Its stack operations feed `update_cfi_state()` in `check.c`; relocation sizing feeds jump table and metadata relocation generation.

Risks: the function names use `fomat` typos but are internal. The decoder is intentionally selective, so unsupported instructions become `INSN_OTHER`; missing stack-affecting opcodes can create false CFI warnings. Direct pointer casting from section data assumes alignment/endian behavior matches host build expectations. The special LoongArch `jirl` cases are narrow and could miss new ABI patterns.

Test signals: objtool tests should cover LoongArch prologues/epilogues with `addi.d`, `ld.d`, `st.d`, `ldptr.d`, `stptr.d`, direct and dynamic branches, `break` trap/bug cases, and ORC generation from compiled LoongArch objects. Regression signals include new "unsupported stack register modification" warnings or unresolved jump destinations.
