# sources/compression/xz/src/liblzma/api/lzma.h

Purpose: umbrella public header for liblzma, defining portability macros and including all public API subheaders in the correct dependency order.

Important APIs/types/functions: sets up standard integer and size types unless `LZMA_MANUAL_HEADERS` is defined, including compatibility typedefs/macros for old MSVC. Defines `LZMA_API_IMPORT`, `LZMA_API_CALL`, `LZMA_API(type)`, `lzma_nothrow`, and GCC attribute wrappers. It then defines `LZMA_H_INTERNAL` and includes version, base, VLI, check, filter, BCJ, delta, LZMA1/2, container, stream flags, block, index, index hash, and hardware headers.

Control flow: compile-time only. C++ users get `extern "C"` around subheader declarations. After inclusion, `LZMA_H_INTERNAL` is undefined to prevent direct subheader re-inclusion by applications.

State and persistence: no runtime state; it defines ABI and source-compatibility surface.

Dependencies/integration: installed as the canonical include for all liblzma consumers. The subheader order matters because later headers depend on earlier types such as `lzma_ret`, `lzma_vli`, `lzma_check`, and `lzma_filter`.

Risks: header portability code is ABI-sensitive. Changes to calling convention, import/static handling, or integer macro fallback can break downstream builds, especially C++, old MSVC, MinGW, Cygwin, and projects that define manual headers.

Test signals: downstream-style compile tests, C++ compile coverage, Windows builds, and any test that includes only `<lzma.h>` without prior standard headers.
