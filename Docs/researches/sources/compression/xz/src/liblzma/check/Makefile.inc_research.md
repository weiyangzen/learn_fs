# sources/compression/xz/src/liblzma/check/Makefile.inc

Purpose: Automake source fragment selecting integrity-check and checksum implementation files for liblzma.

Important APIs/types/functions: adds generator utilities to `EXTRA_DIST`; always adds `check/check.c`, `check/check.h`, `check/crc_common.h`, `check/crc_x86_clmul.h`, `check/crc32_arm64.h`, and `check/crc32_loongarch.h`. Selects `crc32_small.c` for `COND_SMALL`, otherwise `crc32_fast.c` and endian tables, plus optional x86 assembly. Conditionally adds CRC64 small/fast sources and optional SHA-256 implementation.

Control flow: build conditionals choose small-size versus fast table implementations and include optional algorithms based on configure results.

State and persistence: build-only. Generated CRC table helper programs are distributed but not runtime state.

Dependencies/integration: included from `src/liblzma/Makefile.am`; must match configure feature macros used by `check.c`, `check.h`, and CRC common headers.

Risks: mismatches between build conditionals and C preprocessor macros can expose API functions without implementation or include architecture headers on unsupported compilers. CRC32 is assumed always enabled.

Test signals: small/full builds, CRC64/SHA256 disabled builds, architecture-optimized builds, `tests/test_check.c`, and symbol-map validation.
