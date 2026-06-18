# sources/compression/xz/src/liblzma/common/common.h

Purpose: primary internal liblzma header defining export macros, compiler attributes, constants, internal coder interfaces, stream internals, and common helper declarations/macros.

Important APIs/types/functions: `LZMA_API`, visibility macros, symbol-version macros, `lzma_always_inline`, `likely/unlikely`, constants `LZMA_BUFFER_SIZE`, `LZMA_THREADS_MAX`, `LZMA_MEMUSAGE_BASE`, `LZMA_SUPPORTED_FLAGS`; types `lzma_next_coder`, `lzma_filter_info`, `lzma_init_function`, `lzma_code_function`, `lzma_end_function`, and `struct lzma_internal_s`; macros `LZMA_NEXT_CODER_INIT`, `return_if_error`, `lzma_next_coder_init`, and `lzma_next_strm_init`.

Control flow: header macros encode lifecycle patterns: initialize streams, reuse or free coders when init function changes, return on non-OK errors, and define valid stream action sequences. No standalone runtime execution occurs here.

State and persistence: defines layout for per-stream internal state and per-filter coder chains. These structures persist inside `lzma_stream` until `lzma_end()`.

Dependencies/integration: includes `sysdefs.h`, `mythread.h`, `tuklib_integer.h`, and public `lzma.h`. Every liblzma implementation file relies on this header.

Risks: structure layout and macro behavior affect the entire library. ABI/export macro mistakes can hide public symbols or export internals. `lzma_next_coder_init()` intentionally marks a coder as possibly initialized even if later allocation fails, so implementers must understand the lifecycle.

Test signals: full build matrix across Windows, Cygwin, ELF visibility, Linux symbol versions, static/shared PIC, and all encoder/decoder tests.
