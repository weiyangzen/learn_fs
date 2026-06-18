# sources/compression/xz/src/liblzma/check/check.c

Purpose: implements public support/size queries for integrity checks and internal generic check init/update/finish dispatch.

Important APIs/types/functions: implements `lzma_check_is_supported`, `lzma_check_size`, `lzma_check_init`, `lzma_check_update`, and `lzma_check_finish`.

Control flow: public query functions range-check the check ID and index fixed arrays. Internal init/update/finish switch on `lzma_check`: none is a no-op; CRC32 initializes/updates/stores little-endian `uint32_t`; CRC64 does the same for `uint64_t`; SHA-256 delegates to SHA-256 helpers. Unsupported or reserved IDs fall through as no-ops for internal dispatch.

State and persistence: state is caller-provided `lzma_check_state`. No globals are mutated in this file.

Dependencies/integration: depends on feature macros `HAVE_CHECK_CRC32`, `HAVE_CHECK_CRC64`, `HAVE_CHECK_SHA256`, public `lzma/check.h`, internal `check.h`, CRC functions, endian conversion helpers, and SHA-256 wrappers. Block encoders/decoders and Index hash use these dispatchers.

Risks: support table must stay aligned with `.xz` Check ID assignments and build macros. Internal no-op behavior for unsupported IDs assumes callers validated check support before relying on results. Finish writes little-endian raw values, which display code must interpret correctly.

Test signals: `tests/test_check.c`; block encode/decode check validation; Index hash tests; stream decode tests with unsupported/no-check flags.
