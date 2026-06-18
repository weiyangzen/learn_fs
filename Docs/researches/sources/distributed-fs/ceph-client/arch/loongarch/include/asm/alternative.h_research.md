# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/alternative.h

## Purpose

`alternative.h` provides C inline-assembly macros and `struct alt_instr` metadata for LoongArch alternatives. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

Important APIs are `ALTERNATIVE`, `ALTERNATIVE_2`, `alternative`, `alternative_2`, `ALTINSTR_ENTRY`, and `struct alt_instr`. Concrete declarations observed in the file: Includes: `linux/types.h`, `linux/stddef.h`, `linux/stringify.h`, `asm/asm.h`. Macros: `_ASM_ALTERNATIVE_H`, `b_replacement`, `e_replacement`, `alt_end_marker`, `alt_slen`, `alt_total_slen`, `alt_rlen`, `__OLDINSTR`, `OLDINSTR`, `alt_max_short`, `OLDINSTR_2`, `ALTINSTR_ENTRY`, `ALTINSTR_REPLACEMENT`, `ALTERNATIVE`, `ALTERNATIVE_2`, `alternative`, `alternative_2`. Types referenced or declared: `alt_instr`.

## Control Flow, State, And Persistence

Compile-time macros emit old instructions, replacement instructions, and metadata; boot/runtime alternative patching later selects code based on CPU feature bits.

## Dependencies And Integration Points

It integrates with CPU feature handling, linker sections, and low-level asm helpers.

## Risks And Test Signals

Risks are instruction length mismatch, bad feature selection, and clobbered inline-asm constraints. Test signals are alternative selftests, objdump, and feature-specific boot coverage.
 A local static signal for this file is that it has 112 lines and 3859 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
