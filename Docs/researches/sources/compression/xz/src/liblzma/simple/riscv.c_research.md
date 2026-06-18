# sources/compression/xz/src/liblzma/simple/riscv.c

## Purpose
Implements RISC-V BCJ filtering for RV32/RV64 instruction streams, covering JAL and sequential AUIPC+instruction pairs, with separate encode and decode paths plus standalone buffer APIs.

## Important APIs, Types, And Functions
- Macros `NOT_AUIPC_PAIR()` and `NOT_SPECIAL_AUIPC()` validate AUIPC pair and special-format conditions compactly.
- `riscv_encode()` converts JAL and AUIPC+inst2 to compression-friendly absolute-address forms.
- `riscv_decode()` reverses real and fake transformed forms.
- Conditional exports `lzma_simple_riscv_encoder_init()`/decoder init and standalone `lzma_bcj_riscv_encode()`/decode.

## Control Flow
The encoder requires at least 8 bytes and scans every two bytes because compressed 16-bit instructions can appear. JAL with rd x1 or x5 is converted by rearranging the 20-bit immediate into big-endian address-like bytes after adding PC. AUIPC with rd not x0/x2 is checked against the following 32-bit instruction; if it is not a pair, the scanner skips enough bytes to avoid decoder desynchronization on false AUIPC+AUIPC patterns. Valid pairs are encoded into a special AUIPC rd=x2 format that stores low bits of inst2 in the first word and the absolute address in big-endian order in the second word. AUIPC with rd x0 or x2 is skipped or fake-decoded if it already matches the special format so the transform remains bijective on arbitrary data.

The decoder mirrors this. It decodes JAL big-endian address bytes back to J-type immediate bits. For AUIPC, ordinary-looking pairs are fake-encoded into the special form, while special-form pairs are decoded by reading the big-endian absolute address, subtracting PC, reconstructing inst2, and rebuilding AUIPC with sign-extension compensation.

## State And Persistence
No filter-specific heap state. The wrapper tracks `now_pos`; standalone APIs mask start offset to an even boundary. Transform state is entirely local to each buffer scan.

## Dependencies And Integration Points
Includes `simple_private.h`, uses endian helpers, and is included only under RISC-V filter feature macros. Wrapper parameters are `unfiltered_max=8` and `alignment=2`.

## Risks
This is the most complex simple filter. It intentionally accepts relaxed AUIPC pairs for speed/size, so false positives and future compiler codegen patterns are central risks. The fake conversion is required for bijection on arbitrary byte streams; skipping distances are part of decoder synchronization. Big-endian storage is used inside an otherwise little-endian instruction stream for compression ratio. C-extension scanning by 2 bytes and the `size < 8` rule mean last-six-byte JALs are intentionally not converted.

## Test Signals
Golden vectors for JAL, AUIPC+JALR, AUIPC+ADDI, loads/stores, rd x0/x2 cases, fake special-format bytes, and non-pair AUIPC+AUIPC. Random-data encode/decode bijection tests are critical. Real RISC-V binaries from GCC/Clang should be benchmarked for ratio and tested under chunked buffer boundaries.
