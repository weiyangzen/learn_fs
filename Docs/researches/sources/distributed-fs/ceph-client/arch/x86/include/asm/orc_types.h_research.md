# sources/distributed-fs/ceph-client/arch/x86/include/asm/orc_types.h

## Purpose
Defines the compact ORC unwind entry format and register/type constants used by objtool and the in-kernel ORC unwinder.

## Important APIs, Types, And Functions
Defines ORC register constants `ORC_REG_UNDEFINED`, `ORC_REG_AX`, `ORC_REG_DX`, `ORC_REG_SP`, `ORC_REG_BP`, `ORC_REG_DI`, `ORC_REG_R10`, `ORC_REG_R13`, `ORC_REG_PREV_SP`, indirect variants, and `ORC_REG_MAX`; type constants `ORC_TYPE_UNDEFINED`, `END_OF_STACK`, `CALL`, `REGS`, and `REGS_PARTIAL`; and packed `struct orc_entry` with SP/BP offsets, base registers, type, and signal flag.

## Control Flow
Objtool emits one ORC entry for one or more code locations. At runtime the unwinder reads the entry for an IP and computes previous SP/BP or register frames according to these fields.

## State And Persistence
ORC entries are immutable metadata in kernel/module images. No mutable state is declared here.

## Dependencies And Integration Points
Depends on Linux types/compiler attributes and x86 bitfield byte order. It integrates with objtool, `orc_header.h`, module metadata, and the ORC unwinder.

## Risks And Edge Cases
The packed bitfield layout is ABI between objtool and the kernel; endian handling must stay correct. Offset ranges are 16-bit signed, so unusual stacks need correct representation.

## Test Signals
Objtool validation, live stack traces through entry code, interrupts, modules, and signal-like frames, plus ORC hash checks are useful.
