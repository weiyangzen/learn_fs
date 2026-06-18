# sources/distributed-fs/ceph-client/tools/objtool/arch/powerpc/decode.c

Purpose: minimal PowerPC objtool architecture implementation, primarily enough to classify simple branch/call control flow and expose relocation sizing.

Important APIs/types/functions: `arch_reg_name` names 32 GPRs plus RA. `arch_ftrace_match()` recognizes `_mcount`. `arch_decode_instruction()` decodes PowerPC opcode 18 branch/call forms, sets instruction length to 4 or 8 for opcode 1, and stores immediate/AA flag. `arch_jump_destination()` handles absolute versus relative branch targets. `arch_initial_func_cfi_state()` initializes CFA at SP and RA at CFA+0.

Control flow: instructions are byte-swapped as needed, opcode is extracted from the high six bits, and only branch opcode 18 is classified. Branch with link becomes `INSN_CALL`, non-link branch becomes `INSN_JUMP_UNCONDITIONAL`; `bl .+4` is ignored as `INSN_OTHER`.

State and persistence behavior: mutates `struct instruction` fields only. Unsupported helpers such as hint decoding and NOP/RET generation call `exit(-1)`, signaling that corresponding objtool features are not implemented for PowerPC in this tree.

Dependencies and integration points: uses generic objtool headers and endian helpers. `arch_reloc_size()` recognizes PPC 32-bit relocation types for table walking and metadata generation.

Risks: no stack operation decoding, no dynamic branch classification, and several arch hooks abort. Enabling ORC, stack validation, or patching paths that need NOP/RET generation would fail hard.

Test signals: basic objtool runs for PowerPC should validate branch destination handling without invoking unsupported actions. Any test enabling `--orc`, unwind hints, or patch hacks should expose the `exit(-1)` limitations.
