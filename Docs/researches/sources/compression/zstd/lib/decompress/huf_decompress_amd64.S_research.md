# sources/compression/zstd/lib/decompress/huf_decompress_amd64.S

## Purpose
Provides x86-64 BMI2 assembly implementations of the Huffman four-stream fast decode loops used by `huf_decompress.c`. It accelerates the fixed table-log fast path for X1 and X2 decoders while leaving argument setup, final stream completion, and corruption validation in C.

## Important Symbols And Macros
The exported hidden symbols are `HUF_decompress4X1_usingDTable_internal_fast_asm_loop`, `_HUF_decompress4X1_usingDTable_internal_fast_asm_loop`, `HUF_decompress4X2_usingDTable_internal_fast_asm_loop`, and `_HUF_decompress4X2_usingDTable_internal_fast_asm_loop`. Both underscored and non-underscored labels are emitted to satisfy Darwin and ELF naming conventions.

The file includes `portability_macros.h` for symbol visibility and CET branch macros. `LOCAL_LABEL()` abstracts Darwin versus ELF private-label syntax. Register aliases map four output pointers, four input pointers, four bit containers, the DTable pointer, and an output limit to named registers. The loops use BMI2 instructions such as `shrxq` and `shlxq`, plus `bsfq` for consumed-bit counting.

## Control Flow
Each function starts with `ZSTD_CET_ENDBRANCH`, emits CFI unwind metadata, saves all general-purpose registers, reads the single `HUF_DecompressFastArgs*` argument from `%rdi` on System V or `%rcx` on Windows, loads `ip[]`, `op[]`, `bits[]`, and `dt`, and stores bounds values on the stack.

The X1 loop computes a safe `olimit` from the remaining output bytes in stream 4 divided by 5 and remaining input bytes divided by 7. It exits if no full iteration is safe or if input pointers are no longer ordered. Each iteration performs five table lookups per stream from the top 11 bits, writes one byte per lookup, reloads bit containers according to trailing-zero counts, advances outputs by five, and repeats until `op3` reaches the computed limit.

The X2 loop computes safe iterations from all four output segment ends divided by 10 and input bytes divided by 7. Each decode lookup reads a 32-bit DTable entry, writes up to two output bytes, shifts the bit container by encoded `nbBits`, and advances the output pointer by encoded length. After five lookups per stream, it reloads all bit containers and loops until the safe limit is reached.

On exit, both functions restore stack temporaries, write updated `ip[]`, `op[]`, and `bits[]` back into `HUF_DecompressFastArgs`, restore all registers, and return to C. The C caller then validates stream positions and completes remaining bytes with portable bitstream decoders.

## State And Persistence
No persistent state or heap allocation exists. The only state transfer is through the `HUF_DecompressFastArgs` memory layout defined in `huf_decompress.c`. The assembly deliberately preserves all registers for a conservative ABI boundary and assumes no red zone.

## Dependencies And Integration Points
The file is guarded by `ZSTD_ENABLE_ASM_X86_64_BMI2`, so it is only active when the build enables this optimized path. It integrates directly with `HUF_decompress4X1_usingDTable_internal_fast()` and `HUF_decompress4X2_usingDTable_internal_fast()`, which have already validated that the machine is little-endian 64-bit, the table log is the fast decoder log, and enough input/output exists for the loop.

ELF builds emit `.note.GNU-stack` to avoid executable-stack markings. There is also an aarch64 GNU property note inside an ELF/aarch64 guard because this file may be assembled empty on that target and still needs BTI/PAC metadata.

## Risks And Edge Cases
The central risk is ABI and structure-layout coupling. Any change to `HUF_DecompressFastArgs` field order, DTable entry packing, or fast decoder table log must be mirrored here. The loops rely on BMI2 instruction availability; incorrect dispatch can crash with illegal instructions. Bounds are conservative but manual: the safe-iteration math must keep input reads above `ilowest` and output writes within the four output segments.

Portability risks include assembler syntax differences, Windows versus System V argument registers, CFI correctness, CET branch support, and Darwin symbol prefixes. Because the loop exits before finishing streams, C-side reconstruction of `BIT_DStream_t` must continue to agree with how this assembly reloads bit containers and counts consumed bits.

## Test Signals
Build tests should assemble this file on ELF and Darwin x86-64 BMI2 targets and verify non-x86 targets tolerate the guarded empty body. Runtime tests should compare decompression output with `HUF_flags_disableAsm` versus assembly enabled across X1/X2 table types, random literal blocks, corrupted jump tables, short streams that force fallback, and CPU feature dispatch modes. Sanitizer/fuzzer signal is strongest when exercising boundaries where the loop exits and C finishing code resumes.
