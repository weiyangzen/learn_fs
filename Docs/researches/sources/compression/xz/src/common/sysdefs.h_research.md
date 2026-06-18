<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/sysdefs.h -->
# sources/compression/xz/src/common/sysdefs.h

Purpose: central portability header for common includes, integer format fallbacks, Windows stdio selection, bool/alignment compatibility, and small utility macros.

Important APIs/types/functions: `memzero`, `my_min`, `my_max`, `ARRAY_SIZE`, `lzma_attr_alloc_size`, `FALLTHROUGH`, `alignas`, fallback `UINT*_C`, `PRI*`, `UINT*_MAX`, and `SIZE_MAX` validation.

Control flow: include generated `config.h` when available, select MinGW ANSI stdio behavior, include standard headers conditionally, define missing integer/printf macros, enforce 32/64-bit `size_t`, provide fake `bool` if needed, and select alignment/fallthrough attributes.

State and persistence: compile-time only.

Dependencies and integration: included broadly by xz, debug helpers, and common modules.

Risks: assumptions about integer widths are explicit; unsupported `size_t` widths hard-error. MinGW stdio choice affects binary size and formatting behavior.

Test signals: compile on C99, pre-C99-like, MinGW/UCRT/MSVCRT, big-endian, and unusual `size_t` platforms.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/sysdefs.h -->
