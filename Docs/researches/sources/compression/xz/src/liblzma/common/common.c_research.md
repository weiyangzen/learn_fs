# sources/compression/xz/src/liblzma/common/common.c

Purpose: implements liblzma core public stream helpers, allocator wrappers, filter-chain lifecycle helpers, buffer copying, version APIs, and stream action sequencing.

Important APIs/types/functions: `lzma_version_number()`, `lzma_version_string()`, `lzma_alloc()`, `lzma_alloc_zero()`, `lzma_free()`, `lzma_bufcpy()`, `lzma_next_filter_init()`, `lzma_next_filter_update()`, `lzma_next_end()`, `lzma_strm_init()`, `lzma_code()`, `lzma_end()`, `lzma_get_progress()`, `lzma_get_check()`, `lzma_memusage()`, `lzma_memlimit_get()`, and `lzma_memlimit_set()`.

Control flow: stream initialization allocates/reinitializes `lzma_internal`, sets default supported actions and sequence state, and preserves allocator pointers. `lzma_code()` validates pointers, reserved fields, action support, and action sequencing; calls the active coder; updates stream pointers/counters; converts internal timeout return; manages `LZMA_BUF_ERROR` suppression; and transitions to run/end/error states based on return code.

State and persistence: owns `strm->internal`, nested coder state, stream sequence, last `avail_in`, supported actions, and buffer-error suppression. Allocation wrappers respect caller-provided allocator hooks.

Dependencies/integration: central to every encoder/decoder wrapper using `lzma_next_strm_init()`. Symbol-version aliases preserve compatibility for selected APIs on Linux builds.

Risks: action sequencing is API contract enforcement; mistakes can allow invalid flush/finish usage or make recoverable errors fatal. Pointer arithmetic avoids NULL+0 undefined behavior. Custom allocators must see matching alloc/free calls.

Test signals: broad library tests exercise this indirectly; focused tests should cover invalid arguments, repeated `LZMA_FINISH`, zero-output buffer behavior, memlimit accessors, progress callbacks, and custom allocators.
