# sources/distributed-fs/ceph-client/tools/objtool/include/objtool/arch.h

Purpose: architecture abstraction contract for objtool instruction classification, stack operations, relocation behavior, patch bytes, special thunk recognition, and disassembly setup.

Important APIs/types/functions: defines `enum insn_type`, stack operation source/destination enums and structs, `struct stack_op`, and arch hook prototypes such as `arch_decode_instruction()`, `arch_initial_func_cfi_state()`, `arch_jump_destination()`, `arch_insn_adjusted_addend()`, `arch_nop_insn()`, `arch_ret_insn()`, `arch_decode_hint_reg()`, `arch_pc_relative_reloc()`, `arch_reloc_size()`, and optional disassembly init.

Control flow: none directly; it defines the interface used by shared objtool code to call into selected architecture implementation.

State and persistence behavior: stack-op and instruction type definitions determine how decoded state flows into CFI validation and metadata generation. No persistence by itself.

Dependencies and integration points: includes objtool file and CFI declarations, and BFD types under `DISAS`. Implemented by x86, LoongArch, and PowerPC files in this work item.

Risks: adding a new `INSN_*` or stack op requires updates in decoders, validators, disassembler, and possibly ORC writers. Weak default hooks in shared code hide unsupported architecture behavior unless tested.

Test signals: architecture implementations should compile against this header and common validation tests should exercise every instruction type and stack-op variant used by decoders.
