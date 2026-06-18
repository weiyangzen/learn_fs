# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asmmacro.h

## Purpose

`asmmacro.h` defines higher-level LoongArch assembly macros for saving/restoring registers, FPU/LSX/LASX state, interrupt state, per-CPU access, TLB operations, and stack/task helpers. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API is the macro collection included by exception entry, context switch, FPU, and VM assembly. Concrete declarations observed in the file: Includes: `linux/sizes.h`, `asm/asm-offsets.h`, `asm/regdef.h`, `asm/fpregdef.h`, `asm/loongarch.h`. Macros: `_ASM_ASMMACRO_H`, `TASK_STRUCT_OFFSET`.

## Control Flow, State, And Persistence

Runtime flow is generated at macro expansion sites; this header shapes how low-level paths preserve architectural state.

## Dependencies And Integration Points

It integrates with generated offsets, register definitions, LoongArch CSR definitions, FPU/vector code, and exception entry.

## Risks And Test Signals

Risks are register corruption, wrong offset use, broken 32/64-bit state handling, and vector-state save bugs. Test signals are boot, context-switch stress, signal/FPU tests, vector extension tests, and objdump review.
 A local static signal for this file is that it has 682 lines and 24914 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
