# sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc-dis.c

## Purpose
`ppc-dis.c` is the xmon PowerPC instruction disassembler, derived from GNU binutils. It decodes a 32-bit instruction word using opcode and operand tables and prints a textual instruction form through xmon's nonstdio layer.

## Important APIs, Types, And Functions
The public entry point is `print_insn_powerpc`. Internal helpers are `operand_value_powerpc`, which extracts and sign-extends operands, `skip_optional_operands`, which suppresses optional operands at default values, and `lookup_powerpc`, which scans `powerpc_opcodes` and validates operand extraction. It consumes `struct powerpc_opcode`, `struct powerpc_operand`, `powerpc_opcodes`, `powerpc_num_opcodes`, `powerpc_operands`, and `ppc_optional_operand_value` from `ppc.h`/`ppc-opc.c`.

## Control Flow
`print_insn_powerpc` builds a dialect mask from base PPC/common flags, 64-bit configuration, and runtime CPU features for HTM, AltiVec, and VSX. It looks up the opcode by mask and dialect, falls back to any dialect if allowed, prints the mnemonic, iterates operands, skips fake and optional operands as needed, formats registers, relative and absolute addresses, condition register bits, and immediates, then returns the instruction length. Unknown instructions print as `.long`.

## State And Persistence
The file holds no mutable persistent state except a small static condition-bit name table inside printing. Output is immediate xmon console text. Dialect selection is derived each call from CPU feature state.

## Dependencies And Integration Points
It depends on `asm/cputable.h`, `cpu_has_feature`, `nonstdio.h`, legacy `ansidecl.h`, opcode declarations in `ppc.h`, and `dis-asm.h`. Xmon command code calls it when `CONFIG_XMON_DISASSEMBLY` includes the disassembler objects.

## Risks
Opcode table order matters because lookup returns the first valid match. Operand extraction callbacks can mark instructions invalid; errors there affect decoding quality. The dialect mask must track new CPU features and ISA extensions or xmon will print valid instructions as `.long`. Imported coding style differs from kernel style and should be changed cautiously.

## Test Signals
Manual xmon disassembly of known instructions, build tests with and without CPU feature options, and comparison against objdump for representative PowerPC instructions are the best signals. Unknown instruction paths should print raw `.long` values without crashing.
