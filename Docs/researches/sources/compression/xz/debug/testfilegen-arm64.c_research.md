<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/debug/testfilegen-arm64.c -->
# sources/compression/xz/debug/testfilegen-arm64.c

Purpose: generates raw ARM64 instruction bytes for testing the ARM64 BCJ filter.

Important APIs/types/functions: `put32le` writes little-endian words and advances pseudo-PC `pc4`; `putbl` emits branch-link encodings; `putadrp32` emits ADRP-like encodings with varied immediate/register bits.

Control flow: `main` emits boundary BL immediates, PC-relative negative cases, ADRP test cases, then page-aligns and iterates immediate sizes to cover positive and negative ADRP ranges.

State and persistence: only process-local `pc4`; generated binary test data is written to stdout.

Dependencies and integration: standalone C using stdint/stdbool/stdio. Its output feeds filter tests or manual compression/decompression comparisons.

Risks: no output error handling. Encodings are handcrafted and tightly coupled to ARM64 filter recognition rules; a rule change may require updated vectors.

Test signals: compress/decompress through ARM64 filter and compare to original; inspect generated instruction distribution around immediate and page-boundary edges.
<!-- END_FILE_RESEARCH: sources/compression/xz/debug/testfilegen-arm64.c -->
