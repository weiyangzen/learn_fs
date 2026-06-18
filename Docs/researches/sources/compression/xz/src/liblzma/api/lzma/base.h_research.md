# sources/compression/xz/src/liblzma/api/lzma/base.h

Purpose: defines foundational liblzma API types, return codes, streaming actions, allocator hooks, `lzma_stream`, and core stream lifecycle functions.

Important APIs/types/functions: declares `lzma_bool`, `lzma_reserved_enum`, `lzma_ret`, `lzma_action`, `lzma_allocator`, opaque `lzma_internal`, `lzma_stream`, `LZMA_STREAM_INIT`, `lzma_code`, `lzma_end`, `lzma_get_progress`, `lzma_memusage`, `lzma_memlimit_get`, and `lzma_memlimit_set`.

Control flow: callers initialize `lzma_stream` with `LZMA_STREAM_INIT`, initialize a coder from another header, repeatedly call `lzma_code()` with an action (`LZMA_RUN`, flush/barrier, or `LZMA_FINISH` depending on coder), then call `lzma_end()`. Return codes distinguish success, stream end, check warnings, memory failures, format/options/data errors, buffer stalls, programming errors, and seek requests.

State and persistence: `lzma_stream` carries input/output pointers, totals, allocator pointer, opaque internal coder state, seek position, and reserved ABI space. Allocator lifetime rules differ between single-threaded and multithreaded use; multithreaded coders may retain allocator pointers until `lzma_end()`.

Dependencies/integration: all liblzma encoders/decoders and block/index/filter APIs use these types. The xz CLI stores a global `lzma_stream` and tracks progress through these fields/functions.

Risks: misuse of `lzma_code()` actions or mutating `avail_in` after finish/flush can produce `LZMA_PROG_ERROR`. `LZMA_BUF_ERROR` is intentionally delayed and nonfatal but often signals truncated input. ABI reserved fields must remain untouched by applications.

Test signals: nearly every liblzma test exercises this contract; focused signals include stream encode/decode tests, progress tests, memory-limit tests, and `xz` CLI compression/decompression flows.
