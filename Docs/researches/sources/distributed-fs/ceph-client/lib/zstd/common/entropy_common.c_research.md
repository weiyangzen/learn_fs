# sources/distributed-fs/ceph-client/lib/zstd/common/entropy_common.c

Purpose: Implements shared FSE/HUF entropy helper functions used by zstd compression and decompression, primarily error wrappers and parsing compact normalized-count/Huffman-weight headers.

Important APIs/functions:
- `FSE_versionNumber()`.
- `FSE_isError()`, `FSE_getErrorName()`.
- `HUF_isError()`, `HUF_getErrorName()`.
- `FSE_readNCount()`, `FSE_readNCount_bmi2()`, and internal `FSE_readNCount_body()` parse normalized FSE counts from a compact bit header.
- `HUF_readStats()`, `HUF_readStats_wksp()`, and internal body functions parse Huffman weights and rank statistics, optionally using BMI2 paths.

Control flow:
- FSE count parsing reads tableLog, then iteratively decodes signed normalized counts and zero-run repeats from a little-endian bitstream, updating `remaining`, threshold, and symbol index until the distribution sums to one remaining slot.
- Short headers are copied into an 8-byte local buffer for the main parser.
- HUF stats parsing supports a direct nibble-packed header (`iSize >= 128`) or an FSE-compressed weights header. It then computes rank stats, infers the final symbol weight, validates power-of-two totals, and returns bytes consumed.
- BMI2-specific variants are compiled only under `DYNAMIC_BMI2`; otherwise flags are ignored.

State and persistence:
- Stateless across calls. Caller-provided arrays receive normalized counters, weights, rank stats, table log, and symbol counts.
- Uses stack workspace for the public `HUF_readStats()` wrapper.

Dependencies and integration:
- Includes `mem.h`, `error_private.h`, `fse.h`, `huf.h`, and `bits.h`.
- Calls `FSE_decompress_wksp_bmi2()` for compressed Huffman weight headers.
- Used by zstd block/header entropy decode paths.

Risks:
- This is a malformed-input boundary. Bounds checks on `hbSize`, `srcSize`, `maxSVPtr`, `hwSize`, and bit counts must remain exact.
- `ZSTD_highbit32()` requires nonzero inputs; the code validates totals before calling in most places.
- BMI2 dispatch must produce identical results to default path.

Test signals:
- Fuzz FSE normalized count headers and HUF stats headers.
- Boundary tests for tiny headers, too-small max symbol values, tableLog too large, too many zeros, invalid final weight, and workspace sizes.
- Compare BMI2 and non-BMI2 decoding results.
