<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/outqueue.h -->
# sources/compression/xz/src/liblzma/common/outqueue.h

Purpose: Declares the output queue structures and functions used by multithreaded liblzma coders.

Important APIs/types: `lzma_outbuf` is a flexible-array output buffer with worker pointer, allocation size, produced/consumed positions, finish state, finish return, and Block size metadata. `lzma_outq` stores active FIFO, cache, memory counters, and buffer limits. Inline helpers are `lzma_outq_has_buf()`, `lzma_outq_is_empty()`, and `lzma_outq_outbuf_memusage()`.

Control flow/state: The header documents which fields require mutex protection. `pos`, `decoder_in_pos`, and `finished` are shared between worker and main threads. `finish_ret` must not be `LZMA_OK` for a finished buffer because it signals completion/error when the head is drained.

Dependencies/integration: Includes `common.h` and is implemented by `outqueue.c`. Used by multithreaded stream decoder and encoder components.

Risks/tests: The contract depends on caller discipline around mutexes and on buffer-size overflow checks before `lzma_outq_outbuf_memusage()`. Tests should include thread sanitizer coverage in users of the queue and assertion coverage for invalid finish states.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/outqueue.h -->
