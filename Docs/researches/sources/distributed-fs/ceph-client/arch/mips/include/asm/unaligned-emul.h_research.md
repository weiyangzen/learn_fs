# sources/distributed-fs/ceph-client/arch/mips/include/asm/unaligned-emul.h

## Purpose

`unaligned-emul.h` provides byte-wise load/store macros for software emulation of unaligned MIPS memory accesses.

## Important APIs, Types, And Functions

Important APIs are `LoadHWU`, `LoadHWUE`, `LoadWU`, `LoadWUE`, `LoadHW`, `LoadHWE`, `LoadW`, `LoadWE`, `LoadDW`, `StoreHW`, `StoreHWE`, `StoreW`, `StoreWE`, and `StoreDW`; variants distinguish signed/unsigned, kernel/user access, word/doubleword, and endian order. Includes: `asm/asm.h`. Macros/constants: `_ASM_MIPS_UNALIGNED_EMUL_H`, `_LoadHW`, `_LoadW`, `_LoadHWU`, `_LoadWU`, `_LoadDW`, `_StoreHW`, `_StoreW`, `_StoreDW`, `LoadHWU`, `LoadHWUE`, `LoadWU`, `LoadWUE`, `LoadHW`, `LoadHWE`, `LoadW`, `LoadWE`, `LoadDW`, `StoreHW`, `StoreHWE`, `StoreW`, `StoreWE`, `StoreDW`.

## Control Flow

The macros build values one byte at a time using inline assembly, with exception-table fixups that set `-EFAULT` for user or kernel fault handling, then store back bytes in endian-correct order.

## State And Persistence

State is only the target memory value and result/error variable supplied by the caller.

## Dependencies And Integration Points

It integrates with address-error exception handling, `TIF_FIXADE`/`TIF_LOGADE`, user access helpers, endian macros, and FPU/instruction emulation paths that need safe unaligned reads.

## Risks

Risks are endian inversion, sign-extension errors, partial stores on fault, missing exception fixups, and 64-bit value corruption on 32-bit builds.

## Test Signals

Test signals are unaligned access emulation tests, big/little endian builds, user fault injection, and address-error signal behavior.
Static review signal: this source currently has 780 lines and 26856 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
