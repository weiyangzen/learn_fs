# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/asm.h

## Purpose

`asm.h` defines LoongArch assembly portability macros for register sizes, load/store mnemonics, stack alignment, symbol annotations, relocation/address loading, and prefetch helpers. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Key APIs include `SZREG`, `REG_L`, `REG_S`, `LONG_L`, `PTR_L`, `FEXPORT`, `LEAF`, `NESTED`, `END`, `la_abs`, `la_pcrel`, and related relocation macros. Concrete declarations observed in the file: Macros: `__ASM_ASM_H`, `PREF`, `PREFX`, `STACK_ALIGN`, `SZREG`, `REG_L`, `REG_S`, `REG_ADD`, `REG_SUB`, `INT_ADD`, `INT_ADDI`, `INT_SUB`, `INT_L`, `INT_S`, `INT_SLLI`, `INT_SLLV`, `INT_SRLI`, `INT_SRLV`, `INT_SRAI`, `INT_SRAV`, `LONG_ADD`, `LONG_ADDI`, `LONG_ALSL`, `LONG_BSTRINS`, and 43 more.

## Control Flow, State, And Persistence

No runtime flow; macros expand into assembly instructions and ELF symbol metadata.

## Dependencies And Integration Points

It integrates with almost every LoongArch assembly source, linker behavior, and toolchain relocation support.

## Risks And Test Signals

Risks are 32/64-bit mnemonic mismatch, bad symbol alignment, and relocation-mode incompatibility. Test signals are full assembly build, objdump symbol checks, and 32/64-bit defconfig builds.
 A local static signal for this file is that it has 239 lines and 4894 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
