# sources/compression/xz/src/liblzma/simple/arm64.c

## Purpose
Implements ARM64 BCJ filtering for BL and ADRP instructions and exposes standalone buffer encode/decode APIs when enabled.

## Important APIs, Types, And Functions
- `arm64_code()` converts BL and selected ADRP immediates.
- `arm64_coder_init()` wires wrapper settings.
- Conditional filter-chain exports `lzma_simple_arm64_encoder_init()` and decoder init.
- Standalone APIs `lzma_bcj_arm64_encode()` and `lzma_bcj_arm64_decode()`.

## Control Flow
The function rounds size to 4 bytes and scans 32-bit little-endian instructions. BL is detected by top opcode bits and converted by adding/subtracting `pc >> 2` to the 26-bit immediate. ADRP is detected with mask `0x9F000000`, extracts immediate pieces, skips values outside a +/-512 MiB compromise range, clears immediate fields, adds/subtracts page PC, and writes the transformed immediate back. Standalone APIs mask start offset to a 4-byte boundary.

## State And Persistence
No persistent filter-specific state. Wrapper tracks `now_pos`.

## Dependencies And Integration Points
Uses `read32le()`/`write32le()` from common headers through `simple_private.h`. The wrapper uses `unfiltered_max=4` and `alignment=4`.

## Risks
BL uses only six opcode bits, so false positives in non-code data are a known ratio tradeoff. ADRP conversion assumes useful range and may depend on section alignment. Auto-vectorization is explicitly disabled for Clang due to code size/performance risk.

## Test Signals
Inverse tests for BL and ADRP, standalone API tests, start-offset masking, random-data bijection checks, and benchmark coverage for Clang/GCC builds.
