<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc.h

## Purpose
Defines the opcode, operand, and macro table contracts used by the PowerPC disassembler that xmon embeds from binutils-derived sources.

## Important APIs, Types, And Functions
Key types are `ppc_cpu_t`, `struct powerpc_opcode`, `struct powerpc_operand`, and `struct powerpc_macro`. It declares `powerpc_opcodes`, `vle_opcodes`, `powerpc_operands`, and macro tables, plus flag constants such as `PPC_OPCODE_POWER8`, `PPC_OPCODE_VLE`, `PPC_OPERAND_RELATIVE`, and `PPC_OPERAND_OPTIONAL`.

## Control Flow
The header has no executable flow. Disassembler code indexes opcode tables, filters by CPU/dialect flags, uses masks to match instructions, and uses operand descriptors to extract or print operands.

## State And Persistence
All state is static table metadata owned by companion source files. The header fixes ABI-like structure layouts between xmon's PowerPC opcode database and printer.

## Dependencies And Integration Points
Included by xmon disassembly code alongside binutils-style `dis-asm.h` and opcode table implementations. It integrates xmon instruction dumps with the imported PowerPC instruction description database.

## Risks And Edge Cases
Structure layout, flag bit, or operand semantic changes can silently corrupt disassembly. The file is GPL/binutils-derived and must stay compatible with the generated/static opcode data.

## Test Signals
Signals are successful xmon instruction dumps, build coverage of `ppc-dis.c`/`ppc-opc.c`, and spot checks that dialect-specific instructions decode with expected mnemonics.

Source read size: 452 lines, 16307 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/xmon/ppc.h -->
