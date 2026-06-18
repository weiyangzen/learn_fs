# sources/compression/xz/src/liblzma/api/lzma/check.h

Purpose: defines public integrity-check IDs and APIs for check support, check sizes, CRC calculation, and querying stream check type.

Important APIs/types/functions: declares enum `lzma_check` values `LZMA_CHECK_NONE`, `CRC32`, `CRC64`, and `SHA256`; defines `LZMA_CHECK_ID_MAX` and `LZMA_CHECK_SIZE_MAX`; exports `lzma_check_is_supported`, `lzma_check_size`, `lzma_crc32`, `lzma_crc64`, and `lzma_get_check`.

Control flow: applications query support before choosing checks for encoders; decoders can request warnings via container flags and then call `lzma_get_check()` immediately after `lzma_code()` returns `LZMA_NO_CHECK`, `LZMA_UNSUPPORTED_CHECK`, or `LZMA_GET_CHECK`. CRC functions are chunkable by passing the previous return value as the next seed.

State and persistence: public CRC functions are stateless from the caller perspective. Build configuration determines which check algorithms are supported, but check-size mapping is fixed for all IDs 0-15.

Dependencies/integration: `check.c` implements support/size dispatch; `crc32_fast.c` implements `lzma_crc32`; CRC64 and SHA-256 implementations are included through `check/Makefile.inc`. Stream headers, block checks, index hashing, and lzip decoding use these APIs.

Risks: calling `lzma_get_check()` outside the documented narrow return-code window is undefined. Unsupported future check IDs can be decoded but not verified. `LZMA_IGNORE_CHECK` can suppress payload integrity failures while header CRCs still run.

Test signals: `tests/test_check.c` validates CRCs and support; stream flags, block header, index hash, and lzip tests use CRC APIs for expected values.
