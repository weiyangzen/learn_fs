# sources/distributed-fs/ceph-client/tools/arch/loongarch/include/asm/inst.h

## Purpose
LoongArch instruction-format helper header used by tools that inspect or synthesize LoongArch instructions.

## Important APIs, Types, and Functions
Defines opcode enums for branches, break, ERTN, load/store, pointer load/store, and AM swap; bitfield structs for instruction formats; `union loongarch_instruction`; `enum loongarch_gpr`; `LOONGARCH_INSN_NOP`; `LOONGARCH_INSN_SIZE`; and `emit_jirl()` via `DEF_EMIT_REG2I16_FORMAT()`.

## Control Flow, State, and Persistence
Consumers read or write the union's format-specific bitfields. The only emitted helper sets opcode, immediate, source register, and destination register fields for a JIRL instruction. No persistent state exists.

## Dependencies and Integration Points
Depends on `linux/bitops.h` and LoongArch encoding conventions. Integrates with objtool, ORC/unwinder, patching, or test code that needs instruction decoding.

## Risks and Test Signals
Risks include C bitfield layout assumptions, endian/compiler sensitivity, immediate range truncation, and opcode drift. Test signals are instruction encode/decode golden values, `emit_jirl()` byte-word checks, and LoongArch tools builds.
