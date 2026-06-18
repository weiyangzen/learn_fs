# sources/compression/lz4/tests/checkFrame.c

Purpose: verifies LZ4 frame headers and decoded block sizes against expected block size ID and byte size.

Important APIs/functions: `createCResources()`, `freeCResources()`, `frameCheck()`, `FUZ_usage()`, and `main()`. Uses `LZ4F_getFrameInfo()` and `LZ4F_decompress()`.

Control flow: parse `-b#` and `-B#`, open the compressed file, then stream through frames. At frame starts it checks `blockSizeID`; while decompressing it tracks partial blocks and validates full block decoded sizes except final/checksum edge cases.

State and persistence: local buffers/decompression context; static display/no-prompt/pause flags. No persistent output.

Dependencies/integration: includes `util.h`, `lz4frame.h` multiple times for include-safety testing, `lz4.h`, and `xxhash.h`; built by `tests/Makefile`.

Risks: expected parameters must match compressed data; final-block handling is nuanced; failures return numeric error codes.

Test signals: catches regressions in frame block-size selection and header emission.
