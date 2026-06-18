# sources/compression/xz/src/liblzma/common/stream_encoder_mt.c Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_encoder_mt.c -->
## sources/compression/xz/src/liblzma/common/stream_encoder_mt.c

### Purpose
`stream_encoder_mt.c` implements the multithreaded `.xz` Stream encoder. It splits input into independent Blocks, compresses them in worker threads, preserves output order with `lzma_outq`, builds the Stream Index, and exposes progress and memory-usage APIs for `lzma_stream_encoder_mt()`.

### Important APIs, Types, And Functions
`worker_thread` owns one input buffer, one output buffer slot, copied filters, a Block encoder, progress counters, and thread synchronization. `lzma_stream_coder` owns stream sequence state, block size, filter chain/cache, Index, output queue, timeout, worker pool, and aggregate progress. Core functions are `worker_encode()`, `worker_start()`, `threads_stop()`, `threads_end()`, `initialize_new_thread()`, `get_thread()`, `stream_encode_in()`, `wait_for_work()`, `stream_encode_mt()`, `stream_encoder_mt_update()`, `get_options()`, `get_progress()`, `stream_encoder_mt_init()`, `lzma_stream_encoder_mt()`, and `lzma_stream_encoder_mt_memusage()`.

### Control Flow
Initialization validates `lzma_mt`, derives filters from either an explicit chain or preset, computes Block and output-buffer sizes, validates Check support, allocates or reuses worker structures, initializes `lzma_outq`, writes the Stream Header, and seeds progress. During encoding, the main thread writes the Stream Header, then loops over completed outqueue buffers and input admission. `stream_encode_in()` obtains a worker/output buffer, copies up to `block_size` bytes to the worker input buffer, and marks a Block finished on full block or flush/finish/barrier. Workers encode a Block, reserve header space first, then either finalize compressed Block header or fall back to `lzma_block_uncomp_encode()` for incompressible data that filled the output buffer. Completed outbuffers are marked readable, appended to the Index when drained, and then the Index and Footer are encoded.

### State, Persistence, And Dependencies
All mutable state is in the coder and worker structures. Thread state transitions are `THR_IDLE`, `THR_RUN`, `THR_FINISH`, `THR_STOP`, and `THR_EXIT`; synchronization uses `mythread_mutex`, `mythread_cond`, and the shared `thread_error`. The output stream is persistent only through caller-provided output buffers. Dependencies include `filter_encoder`, `easy_preset`, `block_encoder`, `block_buffer_encoder`, `index_encoder`, `outqueue`, Check support, symbol-versioning macros, and liblzma allocator conventions.

### Integration Points
The public API supports `LZMA_RUN`, `LZMA_FULL_FLUSH`, `LZMA_FULL_BARRIER`, and `LZMA_FINISH`; sync flush is intentionally disabled. `get_progress()` feeds `lzma_get_progress()`. Linux symbol-version aliases preserve ABI compatibility with older patched liblzma versions. The memory-usage function mirrors initialization option handling and is important for callers that enforce memory limits before starting compression.

### Risks
Concurrency invariants are the main risk: workers must never publish outbuffers out of order, thread errors must stop the pool without deadlock, and filter-cache ownership must not leak on failed thread acquisition. Timeout semantics return `LZMA_TIMED_OUT` only after the first blocking point in a single call. The final memory-usage sum adds `outq_memusage` twice in the return expression after already adding it to `total_memusage`, which is worth verifying against intended accounting. Filter updates are rejected while a worker is active, so callers must use Block boundaries.

### Test Signals
High-value tests include deterministic round trips across thread counts, tiny output buffers, `timeout` behavior, full flush/barrier boundaries, incompressible Blocks, worker error propagation, progress accounting while workers run, filter updates only at legal boundaries, and memory usage comparisons against allocations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_encoder_mt.c -->
