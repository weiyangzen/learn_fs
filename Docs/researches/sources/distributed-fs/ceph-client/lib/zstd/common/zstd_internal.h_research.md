# sources/distributed-fs/ceph-client/lib/zstd/common/zstd_internal.h

## Purpose
`zstd_internal.h` is the shared private contract across Zstd compression, decompression, and dictionary-related code. It defines common constants, default FSE distributions, block metadata, copy helpers, workspace heuristics, and private declarations that must stay consistent across modules.

## Important APIs, Types, and Constants
Key constants include block/frame header sizes, checksum size, minimum compressed block sizes, literal and sequence symbol limits, default FSE logs/norms for literal length, match length, and offset codes, plus maximum entropy header sizes. Types include `blockType_e`, `SymbolEncodingType_e`, `ZSTD_overlap_e`, `ZSTD_bufferMode_e`, `ZSTD_frameSizeInfo`, and `blockProperties_t`. Important helpers are `ZSTD_copy8()`, `ZSTD_copy16()`, `ZSTD_wildcopy()`, `ZSTD_limitCopy()`, and `ZSTD_cpuSupportsBmi2()`. Private declarations include `ZSTD_invalidateRepCodes()`, `ZSTD_getcBlockSize()`, and `ZSTD_decodeSeqHeaders()`.

## Control Flow and State
The header is mostly stateless, but it defines shared default tables and repcode initial values used to initialize or reset compression/decompression state. `ZSTD_wildcopy()` performs intentionally over-copying loops for speed and switches behavior based on overlap type. `ZSTD_cpuSupportsBmi2()` reads CPU feature state through `ZSTD_cpuid()`.

## Dependencies and Integration Points
It includes compiler, CPU, memory, debug, error, Linux Zstd public API, FSE, HUF, and Linux xxhash headers. It is an integration hub: entropy modules depend on its constants, block parsers use its block metadata, and compressor/decompressor implementations share its default normalized distributions.

## Risks and Test Signals
Risks are high because constants define wire-format limits and table sizes. `ZSTD_wildcopy()` can overread/overwrite by design, so callers must reserve `WILDCOPY_OVERLENGTH` slack and obey overlap preconditions. Copy helpers differ by architecture and compiler, including a GCC-specific temporary-buffer workaround. Tests should cover block header parsing, default sequence table decoding, small-offset overlap copies, 32-bit and 64-bit builds, BMI2 feature detection, and frame/literal edge cases around minimum sizes.
