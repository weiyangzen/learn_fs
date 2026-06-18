# sources/distributed-fs/ceph-client/tools/arch/loongarch/include/asm/orc_types.h

## Purpose
Defines LoongArch ORC unwind record types shared by objtool-style generation and unwinder consumers.

## Important APIs, Types, and Functions
Exports base register constants `ORC_REG_*`, unwind type constants `ORC_TYPE_*`, and `struct orc_entry` with SP/FP/RA offsets, base-register selectors, type, and signal flag.

## Control Flow, State, and Persistence
No runtime control exists here; generated ORC tables persist arrays of `struct orc_entry` that an unwinder uses to reconstruct caller state.

## Dependencies and Integration Points
Depends on `linux/types.h`. Integrated by LoongArch ORC metadata producers and consumers.

## Risks and Test Signals
Risk is packed bitfield/offset ABI drift between table generator and unwinder. Test signals include ORC table generation, unwinding through calls, interrupts, partial register frames, and end-of-stack entries.
