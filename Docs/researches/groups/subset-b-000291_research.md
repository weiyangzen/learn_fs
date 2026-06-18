# subset-b-000291 Research

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_encoder.c -->
## sources/compression/xz/src/liblzma/common/stream_encoder.c

### Purpose
`stream_encoder.c` implements the single-threaded `.xz` Stream encoder. It wraps Block encoding, Index encoding, Stream Header/Footer generation, filter-chain updates, and Index record accounting behind the public `lzma_stream_encoder()` entry point.

### Important APIs, Types, And Functions
The private `lzma_stream_coder` holds the stream sequence, a Block encoder, copied filters, Block options, Index encoder, `lzma_index`, and a small header/footer buffer. `block_encoder_init()` validates Block options and initializes `lzma_block_encoder_init()`. `stream_encode()` is the main `lzma_next_coder.code` callback. `stream_encoder_update()` supports `lzma_filters_update()`. `stream_encoder_init()` prepares a fresh stream, and `lzma_stream_encoder()` exposes supported actions.

### Control Flow
Encoding proceeds through `SEQ_STREAM_HEADER`, `SEQ_BLOCK_INIT`, `SEQ_BLOCK_HEADER`, `SEQ_BLOCK_ENCODE`, `SEQ_INDEX_ENCODE`, and `SEQ_STREAM_FOOTER`. The header and Block header are copied from the internal buffer. Nonempty input starts a Block; empty input with `LZMA_FINISH` skips directly to Index encoding, allowing empty Streams. Block actions map full flush/barrier/finish to `LZMA_FINISH` for the Block layer, except `LZMA_SYNC_FLUSH` is passed through. When a Block ends, its unpadded and uncompressed sizes are appended to the Index. Finishing initializes the Index encoder, writes the Index, computes `backward_size`, emits the Footer, and returns `LZMA_STREAM_END`.

### State, Persistence, And Dependencies
State is entirely in-memory in `lzma_stream_coder`; the persistent output is the byte stream written through caller buffers. The Index persists Block size records until the Footer can be generated. The file depends on Block/Header/Index helpers, stream flag encoding, filter-copy/free helpers, allocator discipline, and `lzma_next_coder` callbacks.

### Integration Points
This is used by the high-level liblzma stream API and by applications that need `.xz` output with a single encoding thread. It supports `LZMA_RUN`, `LZMA_SYNC_FLUSH`, `LZMA_FULL_FLUSH`, `LZMA_FULL_BARRIER`, and `LZMA_FINISH`, and integrates with runtime filter updates via `next->update`.

### Risks
Filter updates are valid only before the Index/Footer phase; mid-Block updates depend on downstream filter support. `block_encoder_is_initialized` is subtle: it avoids reinitializing a Block after validation/update, but must be cleared after use. Incorrect Index accounting would corrupt Footer backward size. Header/footer buffer reuse relies on every sequence setting `buffer_size` and `buffer_pos` correctly.

### Test Signals
Useful tests are round-trip `.xz` Streams with empty input, multiple full flushes, sync flush, filter update before and during Blocks, unsupported Check IDs, and output buffers that force partial header/footer copies.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_encoder.c -->

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

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_common.c -->
## sources/compression/xz/src/liblzma/common/stream_flags_common.c

### Purpose
`stream_flags_common.c` provides shared constants and comparison logic for `.xz` Stream Header/Footer flags. It centralizes the magic byte sequences and validates semantic consistency between decoded flags.

### Important APIs, Types, And Functions
It defines hidden `lzma_header_magic` and `lzma_footer_magic`. The exported `lzma_stream_flags_compare()` checks version, Check ID, Check equality, and optionally Backward Size equality when both values are known.

### Control Flow
Comparison accepts only version `0` structures. It rejects invalid Check IDs as programming errors, returns data error for Check mismatches, and compares Backward Size only when neither side is `LZMA_VLI_UNKNOWN`. Backward Size validation is delegated to `is_backward_size_valid()`.

### State, Persistence, And Dependencies
There is no mutable state. The constants are used by encoder and decoder files. Dependencies are the shared stream flags header, VLI constants, and public return codes.

### Integration Points
Decoded Stream Header/Footer pairs use this function to verify that a file's opening and closing flags match. It is also useful when comparing two Footers because known Backward Sizes are compared when available.

### Risks
The function intentionally treats unknown Backward Size as a wildcard, so callers that require Footer-to-Footer equality must ensure both sides have concrete values. Invalid caller-filled structures are reported as `LZMA_PROG_ERROR`, not data corruption.

### Test Signals
Tests should cover matching flags, Check mismatch, unknown versus known Backward Size, invalid Check IDs, invalid Backward Size alignment/range, and nonzero version rejection.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_common.h -->
## sources/compression/xz/src/liblzma/common/stream_flags_common.h

### Purpose
`stream_flags_common.h` declares shared Stream Flags helpers for `.xz` Header/Footer encoding and decoding.

### Important APIs, Types, And Functions
It defines `LZMA_STREAM_FLAGS_SIZE`, declares hidden `lzma_header_magic` and `lzma_footer_magic`, and provides inline `is_backward_size_valid()`.

### Control Flow
The inline validator checks that `backward_size` is within the `.xz` minimum and maximum and is a multiple of four. It is used before encoding Footers and before comparing known Backward Sizes.

### State, Persistence, And Dependencies
The header has no state. It depends on `common.h` for constants, visibility attributes, integer types, and `lzma_stream_flags`.

### Integration Points
This header is included by stream flag encoder, decoder, and common comparison code. Its magic declarations are the link between Header/Footer byte validation and the shared constant definitions.

### Risks
All callers rely on this helper matching the `.xz` spec. A future format version would need changes here and in every caller that currently accepts only `version == 0`.

### Test Signals
Boundary tests around `LZMA_BACKWARD_SIZE_MIN`, `LZMA_BACKWARD_SIZE_MAX`, off-by-one values, and non-four-byte alignment validate the helper.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_decoder.c -->
## sources/compression/xz/src/liblzma/common/stream_flags_decoder.c

### Purpose
`stream_flags_decoder.c` decodes `.xz` Stream Headers and Footers into `lzma_stream_flags`, verifying magic bytes, CRC32, reserved bits, Check ID, and Footer Backward Size.

### Important APIs, Types, And Functions
The private `stream_flags_decode()` interprets the two Stream Flags bytes. Public APIs are `lzma_stream_header_decode()` and `lzma_stream_footer_decode()`.

### Control Flow
Header decoding checks the six-byte magic, verifies CRC32 over Stream Flags, decodes flags, and sets `backward_size` to `LZMA_VLI_UNKNOWN` because the Header does not contain it. Footer decoding checks the two-byte Footer magic at the end, verifies CRC32 over Backward Size plus Stream Flags, decodes flags, and converts the stored `(backward_size / 4) - 1` representation back to bytes. Under fuzzing builds, CRC mismatches can be ignored to let fuzzers reach deeper paths.

### State, Persistence, And Dependencies
There is no retained state. The file depends on stream magic constants, `lzma_crc32`, endian readers, and public format constants.

### Integration Points
Stream decoders use these functions to identify `.xz` streams, distinguish format errors from data errors, and later compare Header/Footer flags with `lzma_stream_flags_compare()`.

### Risks
CRC bypass under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION` must never be enabled in production. Reserved-bit validation is strict; future format versions would currently report options errors. Footer size conversion assumes the fixed `.xz` Footer layout.

### Test Signals
Tests should include valid Header/Footer pairs, bad magic, bad CRC, reserved flag bits, every supported Check ID, Footer Backward Size decoding, and fuzzing-mode-specific CRC behavior if that build mode is used.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_encoder.c -->
## sources/compression/xz/src/liblzma/common/stream_flags_encoder.c

### Purpose
`stream_flags_encoder.c` writes `.xz` Stream Headers and Footers from `lzma_stream_flags`, including magic bytes, Stream Flags bytes, CRC32, and Footer Backward Size encoding.

### Important APIs, Types, And Functions
The private `stream_flags_encode()` writes the two-byte flags field. Public APIs are `lzma_stream_header_encode()` and `lzma_stream_footer_encode()`.

### Control Flow
Header encoding accepts only version `0`, copies header magic, writes reserved-zero byte plus Check ID, computes CRC32 over Stream Flags, and writes it little-endian. Footer encoding accepts only version `0`, validates `backward_size`, stores `(backward_size / 4) - 1`, writes Stream Flags, computes CRC32 over Backward Size plus flags, and appends Footer magic.

### State, Persistence, And Dependencies
There is no retained state. The output buffer receives exactly `LZMA_STREAM_HEADER_SIZE` bytes for both Header and Footer. Dependencies include `is_backward_size_valid()`, stream magic constants, `lzma_crc32`, and endian writers.

### Integration Points
Stream encoders call this file before Block output and after Index output. Correct Footer generation depends on Index size calculation by `lzma_index_size()`.

### Risks
Invalid Check IDs are treated as programming errors. Footer encoding requires a known, aligned Backward Size, so callers must not pass `LZMA_VLI_UNKNOWN`. Layout assertions protect the fixed 12-byte Header/Footer size.

### Test Signals
Tests should compare encoded bytes against known fixtures, mutate Check IDs and versions, validate Backward Size boundary handling, and round-trip through the decoder.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_flags_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/string_conversion.c -->
## sources/compression/xz/src/liblzma/common/string_conversion.c

### Purpose
`string_conversion.c` converts between user-facing filter-chain strings and `lzma_filter` arrays. It also lists supported filter names/options. This is the library-side counterpart of xz-style preset/filter syntax, but it avoids locale-sensitive parsing and keeps messages translatable by xz.

### Important APIs, Types, And Functions
`lzma_str_to_filters()` parses presets and explicit chains. `lzma_str_from_filters()` stringifies filter arrays. `lzma_str_list_filters()` produces help/listing text. Internal helpers include fixed-buffer string builder `lzma_str`, option metadata `option_map`, string-to-value maps, `parse_lzma12_preset()`, `parse_options()`, `parse_filter()`, `str_to_filters()`, and `strfy_filter()`. The static `filter_name_map` binds filter names to IDs, option sizes, parsers, and stringification ranges.

### Control Flow
Parsing skips leading spaces and treats digit or `-digit` input as an LZMA2 preset. Otherwise it parses up to four filters separated by spaces or `--`, allocates zeroed option structures, dispatches filter-specific parsers, validates `.xz`-allowed filters unless `LZMA_STR_ALL_FILTERS` is set, and optionally validates the chain with `lzma_validate_chain()`. Option parsing handles `name=value`, maps named values, parses decimal `uint32_t` without `strtoul()`, accepts KiB/MiB/GiB suffixes only for flagged options, writes fields by `offsetof`, and advances the input pointer for accurate error positions. Stringification walks filters, maps IDs back to names, optionally emits encoder/decoder options, and supports getopt-long syntax and no-space chain separators.

### State, Persistence, And Dependencies
All state is temporary except allocated filter options or returned strings, which the caller must later free through liblzma conventions. The output string uses a fixed 800-byte allocation. Dependencies include `filter_common.h`, filter feature macros, LZMA/delta/BCJ option types, `lzma_lzma_preset()`, `lzma_validate_chain()`, and allocator helpers.

### Integration Points
This API is used by applications that accept human-readable filter strings and by tools that need to print or list available filter chains. Compile-time feature macros determine which filters appear in `filter_name_map`.

### Risks
The fixed string buffer is intentionally not reallocated; adding filters/options without increasing `STR_ALLOC_SIZE` can trip `LZMA_PROG_ERROR`. Parsing allocates each filter options object before validation, so every error path must free partial results. `LZMA_STR_NO_VALIDATION` can return chains that later fail encoder/decoder initialization. Error messages are static strings; callers should use `error_pos` to report location.

### Test Signals
Tests should cover presets, explicit LZMA1/LZMA2 options, BCJ and delta options, multiplier suffix variants, duplicate commas, missing names/values, too-long names, unsupported flags, all stringification flags, NULL options for filters that allow/disallow them, and error-position accuracy.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/string_conversion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_decoder.c -->
## sources/compression/xz/src/liblzma/common/vli_decoder.c

### Purpose
`vli_decoder.c` decodes liblzma variable-length integers from byte buffers, supporting both single-call and incremental decoding.

### Important APIs, Types, And Functions
The exported `lzma_vli_decode()` updates `*vli`, `*vli_pos`, and `*in_pos` while returning `LZMA_OK`, `LZMA_STREAM_END`, `LZMA_DATA_ERROR`, `LZMA_BUF_ERROR`, or `LZMA_PROG_ERROR` depending on mode and progress.

### Control Flow
With `vli_pos == NULL`, the function enters single-call mode, initializes a local position and `*vli`, and treats empty input as data error. In incremental mode, it initializes `*vli` only at byte position zero and validates that partial state is sane. It consumes bytes, adds seven-bit payloads at `7 * position`, stops on a byte without the continuation bit, rejects non-minimal encodings such as trailing zero payload in multibyte values, and rejects integers that exceed `LZMA_VLI_BYTES_MAX`.

### State, Persistence, And Dependencies
Incremental state is held by caller-owned `*vli` and `*vli_pos`. There is no internal persistence. The file depends on VLI constants and common return codes.

### Integration Points
Index, Block Header, filter flags, and other format decoders use this function to parse `.xz` integers from bounded buffers or streaming input.

### Risks
Callers must preserve `*vli` and `*vli_pos` exactly between incremental calls. Single-call and incremental modes intentionally differ on short input errors (`LZMA_DATA_ERROR` versus `LZMA_BUF_ERROR`/`LZMA_OK`), which tests and callers must account for.

### Test Signals
Tests should cover one-byte values, maximum VLI, overlong encodings, truncated single-call and incremental inputs, invalid partial state, and exact `in_pos` advancement.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_encoder.c -->
## sources/compression/xz/src/liblzma/common/vli_encoder.c

### Purpose
`vli_encoder.c` encodes liblzma variable-length integers, supporting both single-call output and incremental output across small buffers.

### Important APIs, Types, And Functions
The exported `lzma_vli_encode()` takes a `lzma_vli`, optional `vli_pos`, output buffer pointers, and returns completion or buffer/prog errors according to mode.

### Control Flow
Single-call mode uses a local position and expects sufficient output space. Incremental mode returns `LZMA_BUF_ERROR` if called with no output space. The function validates `vli_pos` and range, shifts away already-emitted seven-bit groups, writes continuation bytes while the remaining value is at least `0x80`, and writes a final byte without the high bit. Completion returns `LZMA_OK` in single-call mode and `LZMA_STREAM_END` in incremental mode.

### State, Persistence, And Dependencies
Incremental state is caller-owned `*vli_pos`; no state is retained internally. Dependencies are `common.h`, VLI constants, and output-position conventions.

### Integration Points
Format encoders use this for Index, Block Header, and filter property integer fields.

### Risks
Single-call callers that under-allocate output space get `LZMA_PROG_ERROR`, so size calculation via `lzma_vli_size()` is expected. Incremental callers must pass the same original VLI and preserved `vli_pos` on later calls.

### Test Signals
Tests should cover boundary values, maximum VLI, invalid values above maximum, exact-sized output, one-byte-at-a-time incremental output, and empty-output error behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_size.c -->
## sources/compression/xz/src/liblzma/common/vli_size.c

### Purpose
`vli_size.c` calculates how many bytes are needed to encode a liblzma variable-length integer.

### Important APIs, Types, And Functions
The exported `lzma_vli_size()` returns a byte count from 1 through `LZMA_VLI_BYTES_MAX`, or `0` for values above `LZMA_VLI_MAX`.

### Control Flow
The function rejects out-of-range values, then repeatedly shifts by seven bits until the value becomes zero, counting emitted groups.

### State, Persistence, And Dependencies
There is no state. It depends on VLI constants from `common.h`.

### Integration Points
Encoders use this to size headers, Index fields, and buffers before calling `lzma_vli_encode()`.

### Risks
Returning zero is the only error signal. Callers must not confuse it with a valid size, because every valid VLI uses at least one byte.

### Test Signals
Tests should check 0, 127, 128, every 7-bit boundary, `LZMA_VLI_MAX`, and `LZMA_VLI_MAX + 1`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/vli_size.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/Makefile.inc -->
## sources/compression/xz/src/liblzma/delta/Makefile.inc

### Purpose
`delta/Makefile.inc` lists liblzma Delta filter sources for Automake builds, separating common, encoder, and decoder files by feature condition.

### Important APIs, Types, And Functions
It appends common Delta files to `liblzma_la_SOURCES` unconditionally, then conditionally appends `delta_encoder.c/.h` under `COND_ENCODER_DELTA` and `delta_decoder.c/.h` under `COND_DECODER_DELTA`.

### Control Flow
There is no runtime flow. Build-time conditionals determine whether encoder and/or decoder code is compiled.

### State, Persistence, And Dependencies
The file affects build metadata only. It depends on configure-generated Automake conditionals.

### Integration Points
The top-level liblzma build includes this file to assemble the library source list according to enabled filters.

### Risks
Common files are always included, so disabling both encoder and decoder still compiles shared Delta validation/state code. Missing condition alignment with headers would cause unresolved symbols in filter registration code.

### Test Signals
Build matrix tests should cover encoder-only, decoder-only, both, and neither where supported by configure options.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/Makefile.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_common.c -->
## sources/compression/xz/src/liblzma/delta/delta_common.c

### Purpose
`delta_common.c` implements shared initialization, teardown, and option validation for the Delta encoder and decoder.

### Important APIs, Types, And Functions
`lzma_delta_coder_init()` allocates/reuses `lzma_delta_coder`, validates options, initializes distance, position, history, and the next filter. `lzma_delta_coder_memusage()` validates `lzma_options_delta` and returns coder size. `delta_coder_end()` frees chained coders and the Delta coder.

### Control Flow
Initialization allocates the coder on first use, installs the common end function, validates that options describe byte-type Delta with distance in range, resets `pos` and `history`, then initializes the next filter in the chain. Memusage returns `UINT64_MAX` for invalid options.

### State, Persistence, And Dependencies
Delta state is `distance`, one-byte `pos`, 256-byte history, and the `next` coder. There is no persistence beyond streaming history. Dependencies include `delta_private.h`, allocator helpers, and filter-chain initialization.

### Integration Points
Both encoder and decoder wrappers call this after installing their `code` callback. Filter registration uses the memusage function to validate options.

### Risks
History reset on initialization is essential; reuse without reset would corrupt streams. Only byte-wise Delta is supported, so future Delta types must extend validation and encode/decode loops.

### Test Signals
Tests should validate option rejection, distance boundaries, coder reuse after reinit, history reset between streams, and chaining with another filter.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_common.h -->
## sources/compression/xz/src/liblzma/delta/delta_common.h

### Purpose
`delta_common.h` declares shared Delta filter support used by public encoder/decoder headers and private implementation files.

### Important APIs, Types, And Functions
It includes `common.h` and declares `lzma_delta_coder_memusage()`.

### Control Flow
There is no control flow.

### State, Persistence, And Dependencies
The header introduces no state and depends on liblzma common types.

### Integration Points
Delta encoder and decoder headers include this file so filter registration can reference the shared memory-usage validator.

### Risks
Keeping only the memusage declaration public to Delta internals keeps initialization details private; external modules needing `lzma_delta_coder_init()` must include `delta_private.h`.

### Test Signals
Build tests catch declaration/definition drift; runtime tests exercise the function through encoder/decoder option validation.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_decoder.c -->
## sources/compression/xz/src/liblzma/delta/delta_decoder.c

### Purpose
`delta_decoder.c` implements the Delta filter decoder and Delta property decoding.

### Important APIs, Types, And Functions
`decode_buffer()` reverses byte Delta in-place. `delta_decode()` runs the next coder, then decodes the newly produced output range. `lzma_delta_decoder_init()` installs the decode callback and calls common initialization. `lzma_delta_props_decode()` parses the one-byte distance property into `lzma_options_delta`.

### Control Flow
The decoder calls the next filter first, tracking the output start offset. It then adds the historical byte at `distance + pos` modulo 256 to each new byte and stores the decoded byte back into history. Property decoding requires exactly one byte and maps stored distance `0..255` to liblzma distance `1..256`.

### State, Persistence, And Dependencies
State is the shared Delta history ring in `lzma_delta_coder`. The file depends on `delta_private.h`, chained filter callbacks, and allocator helpers.

### Integration Points
Raw and Block decoder chains use this when a Delta filter appears before an LZMA/LZMA2 filter. The property decoder is used while parsing filter flags.

### Risks
The decoder assumes `coder->next.code` is present; Delta decode is modeled as postprocessing another filter's output in this path. The modulo-256 history ring depends on `pos-- & 0xFF` behavior.

### Test Signals
Round-trip tests for all distances, chunked output buffers, chained decode after LZMA2, property-size rejection, and NULL/zero-size output behavior are relevant.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_decoder.h -->
## sources/compression/xz/src/liblzma/delta/delta_decoder.h

### Purpose
`delta_decoder.h` declares Delta decoder entry points for liblzma filter registration and property parsing.

### Important APIs, Types, And Functions
It declares `lzma_delta_decoder_init()` and `lzma_delta_props_decode()`.

### Control Flow
There is no control flow in the header.

### State, Persistence, And Dependencies
No state is defined. It depends on `delta_common.h`.

### Integration Points
Filter decoder tables include this header to initialize Delta decode chains and parse stored filter properties.

### Risks
The declarations expose internal liblzma functions, not public API. Signature drift would break filter registration builds.

### Test Signals
Compile tests and decoder/property round-trip tests validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_encoder.c -->
## sources/compression/xz/src/liblzma/delta/delta_encoder.c

### Purpose
`delta_encoder.c` implements byte Delta encoding, filter-chain update forwarding, and Delta property encoding.

### Important APIs, Types, And Functions
`copy_and_encode()` encodes from input to output when Delta is first in the chain. `encode_in_place()` postprocesses output from a preceding filter. `delta_encode()` selects direct or chained mode. `delta_encoder_update()` forwards updates to the next filter because Delta options are immutable mid-stream. `lzma_delta_encoder_init()` installs callbacks, and `lzma_delta_props_encode()` writes the one-byte distance property.

### Control Flow
In direct mode, the encoder copies the minimum available input/output, subtracts the historical byte, updates history with original input, and returns stream end on flushing/finishing after all input is consumed. In chained mode, it calls the next coder first and subtracts history from the newly written output bytes in-place. Property encoding validates options through the shared memusage function and stores `dist - 1`.

### State, Persistence, And Dependencies
Streaming state is the 256-byte original-data history ring and distance. The file depends on common Delta initialization, next-filter update helpers, and allocator conventions.

### Integration Points
Delta can appear as a filter in raw or `.xz` encoder chains before LZMA/LZMA2. Property encoding is used by filter flags encoders.

### Risks
Mid-stream option changes are intentionally ignored for Delta and only forwarded downstream, so callers expecting distance changes will not get them. Direct mode must handle NULL input/output only when computed size is zero.

### Test Signals
Tests should cover direct and chained mode, all distance boundaries, partial buffers, flush/finish return codes, property encoding validation, and attempted option updates.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_encoder.h -->
## sources/compression/xz/src/liblzma/delta/delta_encoder.h

### Purpose
`delta_encoder.h` declares Delta encoder entry points for filter-chain construction and property serialization.

### Important APIs, Types, And Functions
It declares `lzma_delta_encoder_init()` and `lzma_delta_props_encode()`.

### Control Flow
There is no runtime control flow.

### State, Persistence, And Dependencies
No state is defined. It depends on `delta_common.h`.

### Integration Points
Encoder filter tables include this header when Delta encoder support is compiled.

### Risks
These are internal declarations; mismatches with filter tables or conditionals cause build/link failures.

### Test Signals
Compile matrix and Delta encode/property tests validate this file indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_private.h -->
## sources/compression/xz/src/liblzma/delta/delta_private.h

### Purpose
`delta_private.h` defines the shared private state structure for Delta encoder and decoder implementations.

### Important APIs, Types, And Functions
`lzma_delta_coder` contains the next coder, Delta distance, ring position, and `history[LZMA_DELTA_DIST_MAX]`. It also declares `lzma_delta_coder_init()`.

### Control Flow
There is no control flow in the header.

### State, Persistence, And Dependencies
The state captures streaming history of original decoded bytes. It depends on `delta_common.h` for common liblzma types and constants.

### Integration Points
Delta encoder and decoder implementation files include this header to share initialization and state layout.

### Risks
The history buffer size must remain consistent with valid Delta distances and with modulo indexing in encoder/decoder loops. Changing the struct affects both directions.

### Test Signals
Round-trip tests across distance 1 and 256 and sanitizer runs with partial buffers are good signals for state layout correctness.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/delta/delta_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/liblzma.pc.in -->
## sources/compression/xz/src/liblzma/liblzma.pc.in

### Purpose
`liblzma.pc.in` is the pkg-config template for liblzma consumers.

### Important APIs, Types, And Functions
It defines substitution variables for install prefix, library directory, include directory, package URL/version, public C flags, static API C flags, public libs, and private libs.

### Control Flow
There is no runtime flow. Configure substitutes `@prefix@`, `@PACKAGE_VERSION@`, `@PTHREAD_CFLAGS@`, and related variables into the installed `.pc` file.

### State, Persistence, And Dependencies
The installed `.pc` file persists build/install metadata for downstream build systems. `Libs.private` carries extra libraries needed for static linking.

### Integration Points
Downstream projects call `pkg-config --cflags --libs liblzma` or `--static` and receive include/library flags from this template.

### Risks
Incorrect `Libs.private` or `Cflags.private` can break static consumers. `Cflags.private: -DLZMA_API_STATIC` changes symbol import/export behavior and must stay aligned with headers.

### Test Signals
Install-tree tests should run `pkg-config --modversion`, dynamic link checks, and static link checks against a trivial program using `lzma_version_number()`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/liblzma.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/Makefile.inc -->
## sources/compression/xz/src/liblzma/lz/Makefile.inc

### Purpose
`lz/Makefile.inc` lists generic LZ encoder/decoder source files for Automake builds.

### Important APIs, Types, And Functions
Under `COND_ENCODER_LZ`, it includes `lz_encoder.c`, `lz_encoder.h`, hash helpers, hash table, and match-finder implementation. Under `COND_DECODER_LZ`, it includes `lz_decoder.c` and `lz_decoder.h`.

### Control Flow
Build-time conditionals select encoder and decoder support independently. There is no runtime behavior.

### State, Persistence, And Dependencies
The file affects build metadata only and depends on configure-generated conditionals.

### Integration Points
LZMA1/LZMA2 filters depend on these generic LZ layers, so their build options must imply the corresponding LZ encoder/decoder condition.

### Risks
Misconfigured conditionals can omit shared LZ files while LZMA filters still reference them. The generated hash table is included only through the encoder source dependency list.

### Test Signals
Configure/build matrix tests for encoder-only, decoder-only, and full builds validate this file.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/Makefile.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_decoder.c -->
## sources/compression/xz/src/liblzma/lz/lz_decoder.c

### Purpose
`lz_decoder.c` implements the generic LZ output window used by LZ77-derived decoders such as LZMA and LZMA2. It owns dictionary allocation/wrapping and bridges filter-specific LZ decoders to the liblzma filter-chain API.

### Important APIs, Types, And Functions
Private `lzma_coder` stores `lzma_dict`, a filter-specific `lzma_lz_decoder`, optional next coder, completion flags, and a temporary buffer for non-last filters. `lz_decoder_reset()`, `decode_buffer()`, `lz_decode()`, `lz_decoder_end()`, `lzma_lz_decoder_init()`, and `lzma_lz_decoder_memusage()` are the key functions.

### Control Flow
`decode_buffer()` wraps the dictionary when it reaches the allocated end by copying the last repeat window to the front. It sets a write limit based on caller output space, calls the filter-specific decoder, copies newly decoded bytes to caller output, and honors `dict.need_reset`. If this LZ decoder is not the last chain element, `lz_decode()` fills a temporary buffer from the next filter, decodes from that buffer into the dictionary, and enforces that this decoder and the next decoder finish consistently. Initialization creates or reuses the base coder, asks the filter-specific initializer for dictionary options, rounds small dictionaries up to 4096 bytes, aligns size, allocates repeat/extra space, seeds preset dictionaries, and initializes the next filter.

### State, Persistence, And Dependencies
State is the dictionary buffer, `full` count, wrap flag, reset flag, filter-specific coder, and optional temporary upstream data. There is no persistence beyond streaming history. Dependencies include `lz_decoder.h`, allocator helpers, and filter-specific LZ decoder factories.

### Integration Points
LZMA and LZMA2 decoder modules call `lzma_lz_decoder_init()` with their own `lz_init` callback. Inline dictionary helpers from `lz_decoder.h` are used by those filter-specific decoders.

### Risks
Dictionary sizing is security-critical: distance validation relies on `full` and repeat-window layout. The small-dictionary round-up may accept some corrupt files that use distances between the true dictionary size and 4096. Non-last-filter mode has strict finish ordering and can report `LZMA_DATA_ERROR` if extra bytes remain.

### Test Signals
Tests should exercise tiny dictionaries, preset dictionaries, dictionary wrap, repeated matches crossing wrap boundaries, reset requests, chained filter mode, truncated streams, and memory-usage overflow boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_decoder.h -->
## sources/compression/xz/src/liblzma/lz/lz_decoder.h

### Purpose
`lz_decoder.h` defines the generic LZ decoder dictionary API and optimized inline helpers used by LZMA/LZMA2 decoders.

### Important APIs, Types, And Functions
It defines decoder configuration macros, `LZ_DICT_EXTRA`, `LZ_DICT_REPEAT_MAX`, `LZ_DICT_INIT_POS`, `lzma_dict`, `lzma_lz_options`, `lzma_lz_decoder`, `LZMA_LZ_DECODER_INIT`, `lzma_lz_decoder_init()`, `lzma_lz_decoder_memusage()`, and inline helpers such as `dict_get()`, `dict_repeat()`, `dict_put()`, `dict_write()`, and `dict_reset()`.

### Control Flow
The main inline flow is dictionary access. `dict_repeat()` validates available output space, computes the back-reference source, copies byte-by-byte for overlaps, otherwise uses `memcpy()` or SSE2 32-byte chunks depending on configuration, updates `pos` and `full`, and reports whether bytes remain. `dict_write()` copies raw bytes into the dictionary and decrements a remaining counter.

### State, Persistence, And Dependencies
`lzma_dict` holds buffer position, fill level, limit, allocation size, wrap state, and reset requests. Compile-time CPU/endian features choose the copy strategy. Dependencies include `common.h` and optionally `<immintrin.h>`.

### Integration Points
Filter-specific decoders call these helpers to output literals, repeated matches, raw chunks, and reset requests into the generic dictionary window.

### Risks
The SSE2 path may intentionally copy extra bytes, so allocation must include `LZ_DICT_EXTRA`. Distance validity must be checked by callers before `dict_repeat()`. Changes to `LZ_DICT_REPEAT_MAX` must stay aligned with LZMA maximum match length and extra-copy size.

### Test Signals
Sanitizer tests around `dict_repeat()` overlap/non-overlap paths, SSE2/non-SSE builds, dictionary wrap, invalid distances, and raw chunk writes are strong coverage.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder.c -->
## sources/compression/xz/src/liblzma/lz/lz_encoder.c

### Purpose
`lz_encoder.c` implements the generic LZ input window and match-finder allocation layer used by LZMA-family encoders. It fills the sliding window, manages match-finder buffers, and delegates symbol encoding to a filter-specific LZ encoder.

### Important APIs, Types, And Functions
Private `lzma_coder` contains a filter-specific `lzma_lz_encoder`, `lzma_mf`, and optional next coder. Key functions are `move_window()`, `fill_window()`, `lz_encode()`, `lz_encoder_prepare()`, `lz_encoder_init()`, `lzma_lz_encoder_memusage()`, `lz_encoder_end()`, `lz_encoder_update()`, `lz_encoder_set_out_limit()`, `lzma_lz_encoder_init()`, and `lzma_mf_is_supported()`.

### Control Flow
`lz_encode()` repeatedly fills the match-finder window when `read_pos` reaches `read_limit`, then calls the filter-specific encoder. `fill_window()` either copies caller input directly or pulls data through the next filter, zeroes extra comparison bytes, adjusts `read_limit`, and handles flush completion by allowing the encoder to consume all remaining bytes. `lz_encoder_prepare()` validates dictionary and match-finder settings, computes keep-before/after and reserve sizes, selects HC/BT match-finder callbacks, calculates hash/son table sizes, and sets depth defaults. `lz_encoder_init()` allocates buffers/tables, resets positions, initializes hash tables, and seeds preset dictionaries through the skip function.

### State, Persistence, And Dependencies
State lives in `lzma_mf`: sliding input buffer, read/write positions, read-ahead, pending bytes after sync flush, hash/son tables, cyclic position, match limits, action, and depth. Dependencies include `lz_encoder_hash.h`, optional generated hash table, `memcmplen.h`, CRC initialization in small builds, and filter-specific encoder factories.

### Integration Points
LZMA1/LZMA2 encoders call `lzma_lz_encoder_init()` with their own initializer. `lz_encoder_update()` enables filter option updates where the LZ-specific encoder supports them. `set_out_limit` is exposed for block-buffer size limiting when no additional filters are chained.

### Risks
Memory sizing has several integer-overflow and 32-bit constraints; dictionary size is limited to 1.5 GiB. Preset dictionary setup runs through the match finder, so callback selection must already be valid. Sync flush restart relies on `pending` and `read_pos` rewind. Incorrect reserve sizing can cause excessive memmove or insufficient lookahead.

### Test Signals
Tests should cover all enabled match finders, dictionary-size boundaries, preset dictionaries, sync flush with continued input, chained filters, output limits, memory-usage overflow, and fuzzing with tiny input/output buffers.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder.h -->
## sources/compression/xz/src/liblzma/lz/lz_encoder.h

### Purpose
`lz_encoder.h` defines the generic LZ encoder input-window and match-finder API used by LZMA-family encoders.

### Important APIs, Types, And Functions
It defines `IS_ENC_DICT_SIZE_VALID`, `lzma_match`, `lzma_mf`, `lzma_lz_options`, `lzma_lz_encoder`, match-finder helper inlines (`mf_ptr`, `mf_avail`, `mf_unencoded`, `mf_position`, `mf_skip`, `mf_read`), `lzma_lz_encoder_init()`, `lzma_lz_encoder_memusage()`, `lzma_mf_find()`, and HC/BT finder prototypes.

### Control Flow
The inline helpers expose match-finder state transitions to LZMA encoders. `mf_skip()` calls the selected skip callback and increments read-ahead. `mf_read()` copies previously buffered uncompressed bytes for LZMA2 uncompressed chunks. `mf_position()` preserves low alignment bits even after window moves.

### State, Persistence, And Dependencies
`lzma_mf` is the key mutable state: window buffer, history limits, offset normalization base, read/write counters, pending flush bytes, hash and son tables, cyclic metadata, depth, nice length, match max, and current action. The header depends on `common.h`.

### Integration Points
LZMA encoder code uses this API for match discovery and to fall back to uncompressed chunk output. `lz_encoder_mf.c` implements the declared match-finder functions.

### Risks
Most fields are performance-critical and have implicit invariants. `read_ahead` means `read_pos` is not always the next unencoded byte. `cyclic_size` must be dictionary size plus one and below internal limits. Dictionary validation macro limits encoder dictionaries more than the decoder format permits.

### Test Signals
Unit tests around read-ahead accounting, `mf_read()` after incompressible chunks, and each match-finder callback validate this interface indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_hash.h -->
## sources/compression/xz/src/liblzma/lz/lz_encoder_hash.h

### Purpose
`lz_encoder_hash.h` provides hash-table selection and hash calculation macros for LZ match finders.

### Important APIs, Types, And Functions
It selects `hash_table` from `lzma_crc32_table[0]` or hidden `lzma_lz_hash_table`, defines hash table sizes/masks and fixed hash offsets, and defines macros such as `hash_2_calc()`, `hash_3_calc()`, `hash_4_calc()`, and multi-thread-oriented `mt_hash_*` variants.

### Control Flow
The macros compute small rolling hashes from the current input pointer `cur` and `mf->hash_mask`, producing hash indices and shorter-prefix hash values used by HC/BT match finders.

### State, Persistence, And Dependencies
There is no mutable state. The chosen table depends on build flags (`HAVE_SMALL`, `CRC32_GENERIC`, `WORDS_BIGENDIAN`, and `TUKLIB_FAST_UNALIGNED_ACCESS`). It may require `lz_encoder_hash_table.h` to provide a little-endian CRC table.

### Integration Points
`lz_encoder.c` includes this header and conditionally includes the generated table. `lz_encoder_mf.c` uses the macros in every match-finder implementation.

### Risks
Endianness determinism is critical: compressed output must not depend on host byte order. The unused `hash_5_calc()` macro appears malformed but is not compiled unless used; future use would need review.

### Test Signals
Cross-endian or simulated-endian builds, small/non-small builds, and comparing compressed output hashes across platforms validate this layer.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_hash_table.h -->
## sources/compression/xz/src/liblzma/lz/lz_encoder_hash_table.h

### Purpose
`lz_encoder_hash_table.h` provides the hidden 256-entry CRC32-derived lookup table used by LZ encoder hash macros when the normal CRC table is unavailable or unsuitable for deterministic little-endian hashing.

### Important APIs, Types, And Functions
It defines `const uint32_t lzma_lz_hash_table[256]`.

### Control Flow
There is no runtime control flow beyond table reads by hash macros.

### State, Persistence, And Dependencies
The table is static read-only data generated by `crc32_tablegen.c`. It has no dependencies in the file body besides the including translation unit's types.

### Integration Points
Included by `lz_encoder.c` when `LZMA_LZ_HASH_TABLE_IS_NEEDED` is set by `lz_encoder_hash.h`.

### Risks
The table must match the expected CRC polynomial and byte order. Since it is a header containing a definition, it must be included in exactly the intended translation unit to avoid duplicate definitions.

### Test Signals
Build configurations that force this table path and output comparisons against the normal CRC-table path validate correctness.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_hash_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_mf.c -->
## sources/compression/xz/src/liblzma/lz/lz_encoder_mf.c

### Purpose
`lz_encoder_mf.c` implements hash-chain and binary-tree match finders for LZ encoders. These functions discover repeated byte sequences in the sliding input window and provide length-distance candidates to LZMA encoders.

### Important APIs, Types, And Functions
The exported wrapper `lzma_mf_find()` calls the configured finder and extends a longest nice-length match. Implemented find/skip pairs include `lzma_mf_hc3_*`, `lzma_mf_hc4_*`, `lzma_mf_bt2_*`, `lzma_mf_bt3_*`, and `lzma_mf_bt4_*` under feature macros. Internal helpers include `normalize()`, `move_pos()`, `move_pending()`, `hc_find_func()`, `bt_find_func()`, and `bt_skip_func()`.

### Control Flow
Each finder computes hash values at `mf_ptr(mf)`, updates fixed-prefix hash slots, obtains a candidate position, searches either a hash chain or binary tree up to `depth`, and emits matches sorted by increasing length. `lzma_mf_find()` validates matches in debug builds, extends a match that reached `nice_len` up to `match_len_max`, stores the count, and increments read-ahead. Skip functions update hash/tree structures without returning matches. When insufficient input is available during flush, `move_pending()` advances `read_pos` and counts bytes that must later be rehashed. `normalize()` subtracts an offset from all hash/son entries when relative positions approach `UINT32_MAX`.

### State, Persistence, And Dependencies
State is in the caller-owned `lzma_mf`: hash table, son table, cyclic position, offset, read positions, pending count, depth, and action. Dependencies include hash macros and `lzma_memcmplen()` for fast match extension.

### Integration Points
`lz_encoder.c` selects these callbacks from `lzma_lz_options.match_finder`. LZMA optimum parsing depends on the quality and ordering of returned matches.

### Risks
Match-finder code is pointer- and index-heavy. Off-by-one distance handling uses zero-based `dist = delta - 1`, while validation compares against `read_pos`. Binary-tree paths must maintain both child pointers on early termination. Normalization touches potentially uninitialized `son` entries by design, which can confuse dynamic analysis unless documented suppressions are used.

### Test Signals
Tests should compare match outputs against a reference for repeated patterns, random data, low-input flushes, normalization near `UINT32_MAX`, each HC/BT variant, and sanitizer/Valgrind runs around table bounds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lz/lz_encoder_mf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/Makefile.inc -->
## sources/compression/xz/src/liblzma/lzma/Makefile.inc

### Purpose
`lzma/Makefile.inc` lists LZMA-family sources for Automake builds, including shared preset/common files and conditional LZMA1/LZMA2 encoder/decoder sources.

### Important APIs, Types, And Functions
It always includes `lzma_common.h` and `lzma_encoder_presets.c`, distributes `fastpos_tablegen.c`, conditionally includes LZMA1 encoder/decoder files, includes `fastpos_table.c` for non-small LZMA1 encoder builds, and conditionally includes LZMA2 encoder/decoder files.

### Control Flow
Build-time conditionals choose which codec directions and table implementations are compiled.

### State, Persistence, And Dependencies
The file affects build metadata only. It depends on configure-generated `COND_ENCODER_LZMA1`, `COND_DECODER_LZMA1`, `COND_ENCODER_LZMA2`, `COND_DECODER_LZMA2`, and `COND_SMALL`.

### Integration Points
Top-level liblzma build includes this file to assemble LZMA source sets. The LZMA2 files in this subset depend on LZ encoder/decoder layers from `lz/`.

### Risks
The shared `lzma_encoder_presets.c` is included unconditionally despite being encoder-oriented, so build condition assumptions should be verified. Table generation and `COND_SMALL` must stay aligned with `fastpos.h`.

### Test Signals
Build matrix coverage across small/non-small and LZMA1/LZMA2 encoder/decoder toggles validates this file.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/Makefile.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos.h -->
## sources/compression/xz/src/liblzma/lzma/fastpos.h

### Purpose
`fastpos.h` provides fast conversion from LZMA match distances to six-bit distance-slot values, a compact two-bit-style bit-scan encoding used in LZMA distance coding and dictionary-size property coding.

### Important APIs, Types, And Functions
In small builds, `get_dist_slot()` and `get_dist_slot_2()` use `bsr32()`. In normal builds, the hidden `lzma_fastpos` table, `FASTPOS_BITS`, `fastpos_shift()`, `fastpos_limit()`, `fastpos_result()`, `get_dist_slot()`, and optionally `get_dist_slot_2()` provide table-based lookup.

### Control Flow
Small distances are table lookups. Larger distances are shifted down by calibrated amounts before lookup and then adjusted by twice the shift. `get_dist_slot_2()` assumes the distance is at least `FULL_DISTANCES` and uses a different base shift to speed distance coding after fully modeled distances.

### State, Persistence, And Dependencies
There is no mutable state. Normal builds depend on `fastpos_table.c` providing `lzma_fastpos`; small builds depend on `bsr32()`. `FULL_DISTANCES_BITS` is supplied by `lzma_common.h` when the specialized helper is needed.

### Integration Points
LZMA encoders use this for match distance slot coding. LZMA2 property encoding also uses `get_dist_slot()` to encode dictionary size.

### Risks
Slot mapping must exactly match LZMA format rules. Build configuration changes can switch between BSR and table behavior, so both paths must be equivalent. `get_dist_slot_2()` requires its precondition.

### Test Signals
Tests should compare both paths over representative distances, all boundaries shown by the table, dictionary-size property values, and full-distance thresholds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos_table.c -->
## sources/compression/xz/src/liblzma/lzma/fastpos_table.c

### Purpose
`fastpos_table.c` is the generated lookup table backing `fastpos.h` in non-small builds.

### Important APIs, Types, And Functions
It defines `const uint8_t lzma_fastpos[1 << FASTPOS_BITS]`.

### Control Flow
There is no control flow; encoder code indexes the table to map distance prefixes to distance slots.

### State, Persistence, And Dependencies
The table is static read-only data generated by `fastpos_tablegen.c`. It includes `common.h` and `fastpos.h` so dimensions and visibility match the consuming code.

### Integration Points
Linked into liblzma when LZMA1 encoder support is enabled and `COND_SMALL` is false. `fastpos.h` declares the symbol.

### Risks
Generated data must remain synchronized with `FASTPOS_BITS` and the generator. Manual edits could silently alter compressed output. The file is large static data, so small builds intentionally avoid it.

### Test Signals
Regenerating with `fastpos_tablegen.c` and diffing, plus compression output comparisons between table and small/BSR paths, validate this file.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos_tablegen.c -->
## sources/compression/xz/src/liblzma/lzma/fastpos_tablegen.c

### Purpose
`fastpos_tablegen.c` generates the `lzma_fastpos[]` lookup table used by `fastpos_table.c`.

### Important APIs, Types, And Functions
The standalone `main()` includes `fastpos.h`, fills a local `fastpos[1 << FASTPOS_BITS]`, and prints a C source file containing the table.

### Control Flow
The generator seeds slots 0 and 1, then iterates distance-slot values from 2 to `2 * FASTPOS_BITS - 1`. For each slot, it repeats that slot value `1 << ((slot_fast >> 1) - 1)` times, matching the LZMA distance-slot range geometry. It prints SPDX/header text and formats 16 entries per line.

### State, Persistence, And Dependencies
State is local to the generator. It depends on `FASTPOS_BITS` from `fastpos.h` and standard C I/O headers.

### Integration Points
This file is distributed as a maintenance tool and not normally compiled into liblzma. Its output is checked into `fastpos_table.c`.

### Risks
Changing `FASTPOS_BITS` without regenerating the table breaks lookup bounds or semantics. The generator prints source to stdout, so build scripts must redirect output intentionally.

### Test Signals
Run the generator, diff against `fastpos_table.c`, and compare selected generated slots against `get_dist_slot()` expectations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/fastpos_tablegen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_decoder.c -->
## sources/compression/xz/src/liblzma/lzma/lzma2_decoder.c

### Purpose
`lzma2_decoder.c` implements the LZMA2 chunk decoder on top of the generic LZ dictionary decoder and the LZMA decoder core.

### Important APIs, Types, And Functions
Private `lzma_lzma2_coder` tracks chunk parse sequence, embedded `lzma_lz_decoder`, uncompressed/compressed sizes, property/reset requirements, and current LZMA options. Key functions are `lzma2_decode()`, `lzma2_decoder_end()`, `lzma2_decoder_init()`, `lzma_lzma2_decoder_init()`, `lzma_lzma2_decoder_memusage()`, and `lzma_lzma2_props_decode()`.

### Control Flow
The decoder reads a control byte, handles `0x00` end marker, enforces dictionary reset before first chunk, distinguishes LZMA chunks from uncompressed chunks, parses size fields, optionally decodes new properties, resets the LZMA state when required, and either calls the LZMA decoder or copies raw bytes into the dictionary. LZMA chunks validate that the inner decoder consumes exactly the declared compressed size and that uncompressed size constraints are enforced by the inner decoder. Dictionary reset requests are signaled to the generic LZ layer with `dict_reset()`.

### State, Persistence, And Dependencies
State includes sequence, size counters, current properties, and reset flags (`need_properties`, `need_dictionary_reset`). Persistent stream history is in the generic `lzma_dict`. Dependencies include `lz_decoder.h`, `lzma_decoder.h`, and LZMA property helpers.

### Integration Points
Raw/Block decoder filter tables initialize this through `lzma_lz_decoder_init()`. LZMA2 is asserted to be the last filter in a chain. Property decoding is used when parsing filter flags.

### Risks
The control-byte state machine is format-critical. Accepting LZMA chunks before properties or before dictionary reset would permit invalid streams. Size counters are `size_t`, so initialization validates through surrounding code for platform limits. Preset dictionaries bypass the initial dictionary-reset requirement.

### Test Signals
Tests should cover every legal control-byte class, invalid control bytes, missing properties, dictionary reset rules, uncompressed chunks, truncated size fields, compressed-size mismatch, end marker handling, and property values 0 through 40.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_decoder.h -->
## sources/compression/xz/src/liblzma/lzma/lzma2_decoder.h

### Purpose
`lzma2_decoder.h` declares internal LZMA2 decoder entry points for filter registration, memory accounting, and property parsing.

### Important APIs, Types, And Functions
It declares `lzma_lzma2_decoder_init()`, `lzma_lzma2_decoder_memusage()`, and `lzma_lzma2_props_decode()`.

### Control Flow
There is no control flow in the header.

### State, Persistence, And Dependencies
No state is defined. It depends on `common.h`.

### Integration Points
Decoder filter tables include this header when LZMA2 decoder support is enabled.

### Risks
These internal functions must remain aligned with filter registration and property decoder expectations.

### Test Signals
Compile matrix tests and LZMA2 decoder/property tests validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_encoder.c -->
## sources/compression/xz/src/liblzma/lzma/lzma2_encoder.c

### Purpose
`lzma2_encoder.c` implements LZMA2 chunk emission on top of the generic LZ encoder and LZMA encoder core. It decides when to emit compressed chunks, uncompressed chunks, reset markers, properties, and the end marker.

### Important APIs, Types, And Functions
Private `lzma_lzma2_coder` tracks sequence, embedded LZMA encoder, current options, reset/property flags, chunk sizes, copy position, and a header/compressed-data buffer. Key functions are `lzma2_header_lzma()`, `lzma2_header_uncompressed()`, `lzma2_encode()`, `lzma2_encoder_options_update()`, `lzma2_encoder_init()`, `lzma_lzma2_encoder_init()`, `lzma_lzma2_encoder_memusage()`, `lzma_lzma2_props_encode()`, and `lzma_lzma2_block_size()`.

### Control Flow
`lzma2_encode()` starts in `SEQ_INIT`; if no data remains and flushing/finishing is requested, it writes the LZMA2 end marker on finish and returns stream end. Otherwise it resets LZMA state if needed, encodes up to LZMA2 chunk limits into an internal buffer, and checks whether compressed size is smaller than uncompressed size. Incompressible chunks are emitted as uncompressed chunks by copying bytes back from the match-finder history with `mf_read()` and marking that the next chunk needs an LZMA state reset. Compressed chunks get a control byte encoding dictionary/state/property reset class, uncompressed and compressed sizes, and optional LZMA properties, then are copied to output.

### State, Persistence, And Dependencies
State is per-stream chunk sequence, current LZMA properties, reset flags, and internal chunk buffer. It depends on the generic LZ encoder, LZMA encoder core, `fastpos.h`, and LZMA2 constants from the header. Persistent output is emitted through caller buffers.

### Integration Points
`lzma_lzma2_encoder_init()` registers with `lzma_lz_encoder_init()`. Option updates can change only `lc/lp/pb` at chunk boundaries and force new properties plus state reset. Property encoding maps dictionary size to the `.xz` one-byte LZMA2 property. Block size estimation is used by multithreaded encoder defaults.

### Risks
The code must keep enough match-finder history to output incompressible chunks, so initialization adjusts `before_size`. Chunk-size arithmetic and read-ahead handling are subtle. Option updates reject incomplete chunks; callers must flush first. Dictionary-size property rounding must match decoder expectations.

### Test Signals
Tests should cover compressible and incompressible chunks, exact 64 KiB/2 MiB chunk boundaries, finish end marker, sync/full flush behavior through the generic LZ layer, option updates at legal/illegal points, property round trips, and block-size estimation for dictionary boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_encoder.h -->
## sources/compression/xz/src/liblzma/lzma/lzma2_encoder.h

### Purpose
`lzma2_encoder.h` declares internal LZMA2 encoder APIs and chunk-size constants.

### Important APIs, Types, And Functions
It defines `LZMA2_CHUNK_MAX`, `LZMA2_UNCOMPRESSED_MAX`, `LZMA2_HEADER_MAX`, and `LZMA2_HEADER_UNCOMPRESSED`, and declares `lzma_lzma2_encoder_init()`, `lzma_lzma2_encoder_memusage()`, `lzma_lzma2_props_encode()`, and `lzma_lzma2_block_size()`.

### Control Flow
There is no control flow in the header.

### State, Persistence, And Dependencies
No state is defined. It depends on `common.h`.

### Integration Points
LZMA2 encoder implementation and filter registration include this header. Multithreaded stream encoding uses block-size estimation through the declared API.

### Risks
Chunk constants must match the LZMA2 format and the encoder buffer layout. Changing them requires coordinated changes in decoder and tests.

### Test Signals
Boundary tests at chunk and uncompressed-size maxima validate use of these constants.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma2_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_common.h -->
## sources/compression/xz/src/liblzma/lzma/lzma_common.h

### Purpose
`lzma_common.h` defines private constants, state transitions, and probability-table helpers shared by LZMA encoder and decoder implementations.

### Important APIs, Types, And Functions
It defines position-state limits, `is_lclppb_valid()`, the 12-state `lzma_lzma_state` enum, state update macros (`update_literal`, `update_match`, `update_long_rep`, `update_short_rep`), literal coder sizing and selection macros, `literal_init()`, match length constants, distance-state constants, distance-slot ranges, alignment constants, and repeat-distance count.

### Control Flow
The macros encode LZMA's finite-state model: recent literal/match/repetition events update state, and `is_literal_state()` chooses literal coding context. `literal_subcoder()` selects one of many literal probability subcoders from position bits and previous-byte context. `literal_init()` resets all literal probabilities with `bit_reset()`.

### State, Persistence, And Dependencies
The header defines no standalone objects, but it describes the layout and transitions for probability arrays and coder state maintained by LZMA encoder/decoder files. It depends on `common.h` and `range_common.h`.

### Integration Points
LZMA1 and LZMA2 encoder/decoder cores include this header to share format constants and guarantee identical state-machine behavior.

### Risks
These constants are format-defining. Any mismatch between encoder and decoder state updates or length/distance constants breaks compatibility. `literal_mask_calc()` and `literal_subcoder()` rely on `lc + lp <= LZMA_LCLP_MAX`.

### Test Signals
Known-answer LZMA streams, property validation for `lc/lp/pb`, literal probability initialization checks, and distance/length boundary encoding tests validate this shared definition layer.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/lzma/lzma_common.h -->
