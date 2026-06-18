# sources/compression/zstd/lib/common/entropy_common.c

Purpose: shared FSE/HUF entropy utilities for reading normalized FSE counts and Huffman weight statistics, plus version/error wrappers for the entropy APIs.

Important functions: `FSE_versionNumber`, `FSE_isError`, `FSE_getErrorName`, `HUF_isError`, `HUF_getErrorName`, `FSE_readNCount`, `FSE_readNCount_bmi2`, `FSE_readNCount_body`, `HUF_readStats`, `HUF_readStats_wksp`, and `HUF_readStats_body`. BMI2-specialized bodies are compiled when `DYNAMIC_BMI2` is enabled.

Control flow: `FSE_readNCount_body()` decodes a compact normalized-count header. It handles small headers by copying into an 8-byte buffer and recursing, initializes counters to zero, extracts table log, then reads variable-width probabilities and zero-repeat runs while tracking remaining probability mass. It validates completion and reports consumed bytes. `HUF_readStats_body()` reads either direct 4-bit weights or FSE-compressed weights, computes rank stats and total weight, derives the implied final weight, validates tree consistency, and returns header size.

State and persistence: no persistent state. Destination arrays supplied by callers are filled with normalized counters, weights, rank stats, symbol counts, and table log values.

Dependencies/integration: depends on `mem.h`, `error_private.h`, `fse.h`, `huf.h`, and `bits.h`. It is used by both compression/decompression entropy table readers and dynamic BMI2 dispatch.

Risks: bit-level parsing is sensitive to truncated inputs, overlarge symbol counts, table-log limits, and malformed zero repeat runs. Workspace size must be sufficient for FSE decompression. BMI2 and default paths must stay behaviorally identical.

Test signals: malformed and boundary FSE headers, direct and FSE-compressed HUF weight headers, max symbol/table-log limits, small `srcSize < 8` path, BMI2 dispatch parity, and fuzzing through decompression table readers.
