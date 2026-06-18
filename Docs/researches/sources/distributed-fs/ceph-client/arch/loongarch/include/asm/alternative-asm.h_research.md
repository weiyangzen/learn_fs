# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/alternative-asm.h

## Purpose

`alternative-asm.h` defines assembly macros for LoongArch runtime instruction alternatives. The source was read as part of the `subset-b-000694` architecture research pass.

## Important APIs And Types

The API emits original and replacement instruction regions plus `.altinstructions` metadata for one or two feature alternatives. Concrete declarations observed in the file: Includes: `asm/asm.h`. Macros: `_ASM_ALTERNATIVE_ASM_H`, `old_len`, `new_len1`, `new_len2`, `alt_max_short`. Types referenced or declared: `alt_instr`.

## Control Flow, State, And Persistence

Runtime patching is performed by alternative code elsewhere; this header contributes annotated sections during assembly.

## Dependencies And Integration Points

It integrates with CPU feature detection, `alternative.h`, linker sections, and boot-time patching.

## Risks And Test Signals

Risks are length mismatches, bad section metadata, and patching the wrong instruction stream. Test signals are objdump of `.altinstructions`, boot on CPUs with/without features, and alternative patch debug logs.
 A local static signal for this file is that it has 83 lines and 2088 bytes, so future edits that radically change size or declaration sets should prompt a fresh architecture review.
