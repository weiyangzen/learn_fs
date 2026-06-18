# sources/compression/xz/src/liblzma/check/check.h

Purpose: internal integrity-check interface and SHA-256 provider abstraction for liblzma.

Important APIs/types/functions: includes `common.h`; determines `HAVE_INTERNAL_SHA256` when no usable external SHA-256 API is found; maps external providers from CommonCrypto, `<sha256.h>`, or `<sha2.h>` through `LZMA_SHA256FUNC`; defines `LZMA_CHECK_BEST`; declares `lzma_check_state` with final/check buffer and union state; declares `lzma_check_init/update/finish`; declares or inlines SHA-256 init/update/finish wrappers.

Control flow: compile-time provider selection determines whether SHA-256 calls are external inline wrappers or internal functions. Darwin CommonCrypto updates split input into `UINT32_MAX` chunks because its API takes 32-bit lengths.

State and persistence: `lzma_check_state` is stack/struct-owned by callers and can hold CRC or SHA-256 state. No global state here.

Dependencies/integration: used by Block coders, Index hashing, SHA-256 implementation, and `check.c`. `LZMA_CHECK_BEST` drives Index hash reliability based on enabled algorithms.

Risks: configure detection must define matching context and function macros. The union layout is internal and may change, so it must not leak into public ABI. External provider wrappers assume provider semantics match expected SHA-256 behavior.

Test signals: `tests/test_check.c`, `tests/test_index_hash.c`, block checksum tests, and builds across platforms with internal and external SHA-256 providers.
