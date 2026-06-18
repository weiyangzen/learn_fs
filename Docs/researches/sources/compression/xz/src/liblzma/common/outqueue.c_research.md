<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/outqueue.c -->
# sources/compression/xz/src/liblzma/common/outqueue.c

Purpose: Implements `lzma_outq`, a FIFO of output buffers with a same-size cache for multithreaded encoding/decoding.

Important APIs: `lzma_outq_memusage()`, `lzma_outq_init()`, `lzma_outq_end()`, `lzma_outq_clear_cache()`, `lzma_outq_clear_cache2()`, `lzma_outq_prealloc_buf()`, `lzma_outq_get_buf()`, `lzma_outq_is_readable()`, `lzma_outq_read()`, and `lzma_outq_enable_partial_output()`.

Control flow: The queue allows up to `2 * threads` allocated buffers to keep workers busy when completion order differs from output order. `lzma_outq_prealloc_buf()` ensures `lzma_outq_get_buf()` cannot fail. Finished head buffers are moved to cache by `move_head_to_cache()`, and cache is cleared when sizes differ. `lzma_outq_read()` copies from the head buffer, returns the buffer's `finish_ret` when fully consumed, and optionally reports Block size metadata.

State/persistence: `lzma_outq` persists linked-list head/tail, read offset, cache list, allocated/in-use memory counters, buffer counts, and buffer limit. Each `lzma_outbuf` persists worker pointer, output positions, finish status, finish return, and Block size metadata.

Dependencies/integration: Used by `stream_decoder_mt.c` and multithreaded encoder code. Relies on caller-held mutexes for fields documented as shared between worker and main threads.

Risks/tests: The implementation does not enforce locking; races are prevented by callers. Tests should cover memory accounting, cache retention by size, reading partial and finished buffers, non-`LZMA_STREAM_END` finish errors, thread limits, and clearing caches under changing block sizes.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/outqueue.c -->
