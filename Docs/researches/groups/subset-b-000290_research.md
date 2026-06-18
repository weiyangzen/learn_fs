# Research group subset-b-000290

Grouped research for liblzma common files under `sources/compression/xz/src/liblzma/common`. Each file section is source-tree aligned and bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/file_info.c -->
# sources/compression/xz/src/liblzma/common/file_info.c

Purpose: Implements `lzma_file_info_decoder()`, a seek-aware decoder that reads `.xz` container metadata without decompressing Blocks and returns a combined `lzma_index`. It walks the file from both ends: it first verifies the first Stream Header, then scans backward from the end to parse Stream Padding, Stream Footers, Index fields, and matching Stream Headers for all concatenated Streams.

Important APIs and types: `lzma_file_info_coder` owns the state machine, file position tracking, `lzma_next_coder index_decoder`, temporary backward-read buffer, decoded per-Stream index, accumulated `combined_index`, destination index pointer, external `seek_pos`, memory limit, and cached `lzma_stream_flags`. Public entry is `lzma_file_info_decoder()`, backed by internal `lzma_file_info_decoder_init()`, `file_info_decode()`, `file_info_decoder_memconfig()`, and `file_info_decoder_end()`.

Control flow: `SEQ_MAGIC_BYTES` reads and validates the first Stream Header and file size constraints. `SEQ_PADDING_SEEK` and `SEQ_PADDING_DECODE` use `reverse_seek()` and `get_padding_size()` to locate trailing Stream Padding. `SEQ_FOOTER` decodes the Stream Footer and Backward Size. `SEQ_INDEX_INIT` initializes the Index decoder with a remaining memory budget, and `SEQ_INDEX_DECODE` decodes exactly the Backward Size. `SEQ_HEADER_DECODE` and `SEQ_HEADER_COMPARE` validate Header/Footer flag consistency, attach flags and padding to the index, concatenate it with earlier Streams, then either finish or continue backward.

State and persistence: `file_cur_pos` and `file_target_pos` are the core invariants; all input consumption updates them so `seek_to_pos()` can decide whether to adjust `*in_pos` internally or return `LZMA_SEEK_NEEDED` via `strm->seek_pos`. `this_index` is transient until a Stream is validated; `combined_index` owns the progressively concatenated result and is transferred to `*dest_index` only on `LZMA_STREAM_END`.

Dependencies and integration: Depends on `index_decoder.h`, Stream Header/Footer decoders, `lzma_index_*` aggregation APIs, VLI limits, and the liblzma `lzma_next_coder` interface. It integrates with applications that can seek and with liblzma memory limit APIs through `memconfig`.

Risks: Position arithmetic is security-sensitive; malformed Backward Size, odd file size, non-multiple-of-four Stream Padding, or inconsistent Header/Footer flags must produce `LZMA_DATA_ERROR`. Memory accounting is subtle because multiple temporary Indexes can use more memory than the final combined index. The function intentionally hides interior `LZMA_FORMAT_ERROR` as data corruption after the first header. Tests should cover tiny files, whole-file single-buffer operation, external seek paths, multi-Stream padding, corrupt Backward Size, low memory limits, and changing the memory limit during `SEQ_INDEX_DECODE`.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/file_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_buffer_decoder.c -->
# sources/compression/xz/src/liblzma/common/filter_buffer_decoder.c

Purpose: Provides `lzma_raw_buffer_decode()`, the single-call buffer-to-buffer API for raw filter chains. It wraps the streaming raw decoder and normalizes completion and partial-buffer failures for callers that want all work done in one call.

Important APIs: The only public function validates input/output pointers and positions, initializes a temporary `lzma_next_coder` with `lzma_raw_decoder_init()`, runs it with `LZMA_FINISH`, and always releases it with `lzma_next_end()`.

Control flow and state: The function snapshots `in_pos` and `out_pos` before decoding. `LZMA_STREAM_END` is translated to `LZMA_OK`. If the decoder returns `LZMA_OK`, the wrapper distinguishes truncated input from too-small output; in the ambiguous case where both input and output end together, it probes one extra output byte through the same decoder.

Dependencies and integration: Depends on `filter_decoder.h` and the raw coder chain builder in `filter_common.c`. It is used by higher-level APIs and tests that need raw decoding without owning a persistent `lzma_stream`.

Risks and tests: Error rollback is the key contract: on any non-success result, both positions must be restored. Tests should include invalid pointers, unsupported filter chains, truncated input, undersized output, exact output size, and the ambiguous all-input/all-output case.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_buffer_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_buffer_encoder.c -->
# sources/compression/xz/src/liblzma/common/filter_buffer_encoder.c

Purpose: Implements `lzma_raw_buffer_encode()`, the single-call raw encoder wrapper for an already-specified filter chain.

Important APIs: The function validates buffer arguments, initializes a temporary raw encoder with `lzma_raw_encoder_init()`, runs the coder with `LZMA_FINISH`, frees it, and maps `LZMA_STREAM_END` to `LZMA_OK`.

Control flow and state: It keeps a local `in_pos` and snapshots `out_pos`. On successful stream end it leaves the new output position visible. On `LZMA_OK`, the output buffer was too small and becomes `LZMA_BUF_ERROR`; all other errors preserve the original output position.

Dependencies and integration: Depends on `filter_encoder.h`, the raw filter chain init path, and downstream filter encoders such as LZMA, BCJ, and Delta. It is commonly exercised by raw filter tests and higher-level single-shot wrappers.

Risks and tests: The main risks are accepting invalid `NULL`/size combinations and failing to roll back `out_pos` on errors. Tests should cover empty input, exact output capacity, undersized output, invalid chains, and custom allocator failures.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_buffer_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_common.c -->
# sources/compression/xz/src/liblzma/common/filter_common.c

Purpose: Centralizes common filter-chain behavior shared by raw encoder and decoder paths: feature metadata, option copying/freeing, chain validation, chain initialization, and memory usage estimation.

Important APIs and data: The compile-time `features[]` table maps filter IDs to option structure sizes and chain-placement rules (`non_last_ok`, `last_ok`, `changes_size`). Public/internal functions include `lzma_filters_copy()`, `lzma_filters_free()`, `lzma_validate_chain()`, `lzma_raw_coder_init()`, and `lzma_raw_coder_memusage()`.

Control flow: `lzma_filters_copy()` copies to a temporary array first so `real_dest` is unchanged on failure. `lzma_validate_chain()` enforces one to four filters, known IDs, legal non-last/last placement, and at most three size-changing filters. `lzma_raw_coder_init()` uses a caller-provided `coder_find()` table; encoders reverse chain order before calling `lzma_next_filter_init()`, while decoders preserve order. `lzma_raw_coder_memusage()` validates the chain, sums per-filter memory usage, uses 1 KiB for simple filters without a callback, and adds `LZMA_MEMUSAGE_BASE`.

State and persistence: The module owns no persistent global state beyond static feature metadata. It allocates filter option copies on demand and relies on callers to release them with `lzma_filters_free()`.

Dependencies and integration: Included by filter encoder/decoder ID tables, Block Header parsing, stream decoders, and raw APIs. Compile-time `HAVE_ENCODER_*`/`HAVE_DECODER_*` macros determine which filters appear valid.

Risks and tests: Chain validation controls API safety and file-format correctness. Tests should cover unsupported IDs, missing terminators, invalid last filters, too many filters, many size-changing filters, option copy rollback, allocator failures, and encoder order reversal.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_common.h -->
# sources/compression/xz/src/liblzma/common/filter_common.h

Purpose: Internal header defining the common ABI prefix for encoder and decoder filter tables and declaring shared raw-filter helper functions.

Important APIs/types: `lzma_filter_coder` contains the common leading fields `id`, `init`, and `memusage`. `lzma_filter_find` is a function pointer returning that common view for a filter ID. Declarations cover `lzma_validate_chain()`, `lzma_raw_coder_init()`, and `lzma_raw_coder_memusage()`.

Control flow and state: The header has no runtime state. Its main design point is structural compatibility: encoder and decoder table structs begin with identical fields so `filter_common.c` can initialize and measure either side through the same interface.

Dependencies and integration: Includes `common.h` and is consumed by `filter_common.c`, `filter_encoder.c`, and `filter_decoder.c`.

Risks and tests: Adding fields before the common prefix in encoder or decoder structs would break casts used by `coder_find()`. Compile-time review and raw encoder/decoder init tests are the main signals.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_decoder.c -->
# sources/compression/xz/src/liblzma/common/filter_decoder.c

Purpose: Maps Filter IDs to decoder-specific functions and exposes raw decoder initialization, support checks, memory usage, and property decoding.

Important APIs/data: The `decoders[]` table is built from compile-time macros and maps LZMA1/LZMA1EXT, LZMA2, BCJ filters, and Delta to init, memory, and properties-decode callbacks. Public functions include `lzma_filter_decoder_is_supported()`, `lzma_raw_decoder()`, `lzma_raw_decoder_memusage()`, and `lzma_properties_decode()`. Internal `lzma_raw_decoder_init()` feeds `filter_common.c`.

Control flow: `decoder_find()` scans the table. `lzma_raw_decoder_init()` delegates chain validation and initialization to `lzma_raw_coder_init()` with decoder order preserved. `lzma_properties_decode()` initializes `filter->options` to NULL for safe cleanup, rejects unknown IDs, accepts empty properties when no decode callback exists, and otherwise lets the filter-specific decoder allocate options.

State and dependencies: Static table only; no persistent runtime state. Depends on filter-specific headers for LZMA, LZMA2, simple BCJ, and Delta decoders.

Risks and tests: Compile-time feature combinations affect supported IDs. Tests should cover unsupported-but-valid IDs, invalid properties sizes, `options` cleanup behavior, memory usage for chains with simple filters, and raw decoding action support (`LZMA_RUN`, `LZMA_FINISH`).
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_decoder.h -->
# sources/compression/xz/src/liblzma/common/filter_decoder.h

Purpose: Internal declaration header for raw decoder chain initialization.

Important API: Declares `lzma_raw_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, const lzma_filter *options)`.

Control flow/state: No runtime behavior; it exposes the initializer used by stream, block, and buffer wrappers while public API entry points remain in `filter_decoder.c`.

Dependencies/integration: Includes `common.h` for `lzma_next_coder`, allocator, and filter definitions. Used by raw buffer decoding and stream/block decode paths.

Risks/tests: Header risk is primarily API drift between declaration and implementation. Build coverage and raw decoder initialization tests catch regressions.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_encoder.c -->
# sources/compression/xz/src/liblzma/common/filter_encoder.c

Purpose: Maps Filter IDs to encoder-specific functions and exposes raw encoder initialization, support checks, memory usage, property encoding, and multithreaded block-size hints.

Important APIs/data: `encoders[]` maps supported filter IDs to init, memory usage, optional block-size, property-size, fixed property-size, and property-encode callbacks. Public APIs include `lzma_filter_encoder_is_supported()`, `lzma_filters_update()`, `lzma_raw_encoder()`, `lzma_raw_encoder_memusage()`, `lzma_mt_block_size()`, `lzma_properties_size()`, and `lzma_properties_encode()`. Internal `lzma_raw_encoder_init()` delegates to common chain initialization.

Control flow: Raw encoder init validates through `filter_common.c` and reverses the filter order for efficient encoding. `lzma_filters_update()` validates a new filter chain, builds a reversed copy, and calls the active coder update callback. `lzma_mt_block_size()` returns the maximum filter-specific block-size recommendation or `UINT64_MAX` when no hint is available. Property helpers distinguish unsupported valid IDs from programming errors and handle fixed-size versus callback-sized properties.

State/dependencies: Static table only. Depends on LZMA, LZMA2, simple BCJ, and Delta encoder modules. Public stream state is installed through `lzma_next_strm_init()` with `LZMA_RUN`, `LZMA_SYNC_FLUSH`, and `LZMA_FINISH`.

Risks/tests: Table accuracy is central. Tests should cover compile-time feature combinations, update callbacks with reversed chains, property size/encode failures, unsupported IDs, invalid options, and LZMA2 block-size hints for threaded encoding.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_encoder.h -->
# sources/compression/xz/src/liblzma/common/filter_encoder.h

Purpose: Internal declaration header for raw encoder chain initialization.

Important API: Declares `lzma_raw_encoder_init(lzma_next_coder *next, const lzma_allocator *allocator, const lzma_filter *filters)`.

Control flow/state: The header has no runtime state. It lets buffer, block, stream, and MicroLZMA-style code initialize encoder chains without going through public `lzma_stream` setup.

Dependencies/integration: Includes `common.h`; implemented in `filter_encoder.c`.

Risks/tests: API drift is the main concern. Build tests and raw encoder tests validate the declaration remains synchronized.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_flags_decoder.c -->
# sources/compression/xz/src/liblzma/common/filter_flags_decoder.c

Purpose: Decodes an on-wire `.xz` Filter Flags field into an `lzma_filter` with allocated filter-specific options.

Important API: `lzma_filter_flags_decode(lzma_filter *filter, const lzma_allocator *allocator, const uint8_t *in, size_t *in_pos, size_t in_size)`.

Control flow: Initializes `filter->options` to NULL for safe cleanup, decodes Filter ID as VLI, rejects reserved IDs, decodes properties size as VLI, checks that enough input remains, and delegates option decoding to `lzma_properties_decode()`. It advances `*in_pos` past the property bytes even if the property decoder returns an error from filter-specific validation.

State/dependencies: Stateless beyond `filter` output. Depends on VLI decoding and decoder property tables in `filter_decoder.c`.

Risks/tests: Important malformed cases are reserved IDs, truncated VLI, properties size larger than remaining input, unsupported filter ID, and properties that allocate then fail. Tests should assert `filter->options` remains safe to free.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_flags_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_flags_encoder.c -->
# sources/compression/xz/src/liblzma/common/filter_flags_encoder.c

Purpose: Encodes and sizes the on-wire `.xz` Filter Flags field for a single filter.

Important APIs: `lzma_filter_flags_size()` computes encoded ID VLI size plus properties-size VLI plus properties bytes. `lzma_filter_flags_encode()` emits the same fields into caller-provided output.

Control flow: Both functions reject reserved Filter IDs as programming errors. Encoding writes Filter ID, obtains and writes properties size, verifies output capacity for fixed properties bytes, calls `lzma_properties_encode()`, and advances `*out_pos`.

State/dependencies: Stateless. Depends on encoder property table functions from `filter_encoder.c` and VLI encoding.

Risks/tests: Output capacity mismatch returns `LZMA_PROG_ERROR` because callers are expected to size the field first. Tests should cover reserved IDs, unsupported IDs in size calculation, zero-size properties, variable-size simple properties, and exact buffer boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/filter_flags_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/hardware_cputhreads.c -->
# sources/compression/xz/src/liblzma/common/hardware_cputhreads.c

Purpose: Exposes `lzma_cputhreads()`, a public wrapper returning available CPU thread/core count.

Important APIs: Public `lzma_cputhreads()` calls `tuklib_cpucores()`. On Linux symbol-version builds, compatibility aliases provide `lzma_cputhreads@XZ_5.2.2` and default `lzma_cputhreads@@XZ_5.2`.

Control flow/state: No persistent state. It is a thin visibility and ABI wrapper around the tuklib platform implementation.

Dependencies/integration: Includes `common.h` and `tuklib_cpucores.h`. Used by applications and liblzma helpers to choose default thread counts.

Risks/tests: ABI symbol versioning is the risk on affected Linux builds. Tests should confirm nonzero or documented platform fallback behavior and symbol exports in compatibility builds.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/hardware_cputhreads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/hardware_physmem.c -->
# sources/compression/xz/src/liblzma/common/hardware_physmem.c

Purpose: Exposes `lzma_physmem()`, a public wrapper returning total physical memory.

Important API: `lzma_physmem()` calls `tuklib_physmem()` and returns its `uint64_t` result.

Control flow/state: Stateless wrapper. The local comment notes this avoids symbol visibility complications in tuklib modules.

Dependencies/integration: Includes `common.h` and `tuklib_physmem.h`. Used by applications and threaded presets to choose memory limits.

Risks/tests: Platform-specific tuklib behavior is the main uncertainty. Tests should check the API returns a plausible value or documented fallback across supported OSes.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/hardware_physmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index.c -->
# sources/compression/xz/src/liblzma/common/index.c

Purpose: Implements the in-memory `.xz` Index and Stream metadata model, including append, concatenate, duplicate, size/memory queries, stream flags/padding, and iteration/location APIs.

Important APIs/types: Internal structures include `index_tree_node`, `index_tree`, `index_record`, `index_group`, `index_stream`, and `struct lzma_index_s`. Public APIs include `lzma_index_init/end/prealloc`, `lzma_index_memusage/memused`, block/stream/size queries, `lzma_index_stream_flags()`, `lzma_index_stream_padding()`, `lzma_index_append()`, `lzma_index_cat()`, `lzma_index_dup()`, `lzma_index_iter_init/rewind/next/locate()`, and internal `lzma_index_padding_size()`.

Control flow: Streams and groups are appended sequentially into AVL-like trees optimized for monotonic insert order. Record groups store cumulative uncompressed sums and cumulative padded compressed sums, enabling binary search by uncompressed offset. `lzma_index_append()` validates unpadded/uncompressed sizes, file size bounds, Index Backward Size bounds, allocates groups using `prealloc`, and updates both Stream and global totals. `lzma_index_cat()` validates combined limits, may shrink the final underfilled group, moves Stream nodes from source to destination with adjusted base offsets, updates check masks, and frees only the source base object. Iterators maintain internal pointers carefully so they do not hold a pointer to a group that `lzma_index_cat()` may reallocate.

State and persistence: `lzma_index` persists totals, tree roots, preallocation preference, and check masks. Each `index_stream` carries base offsets, numbering, record tree, stream flags, and Stream Padding. Records persist cumulative Block size data rather than raw per-Block starts.

Dependencies/integration: Depends on `index.h`, `stream_flags_common.h`, VLI helpers, allocation wrappers, and public `lzma_index_iter` layout. It is the shared metadata object used by Index encoder/decoder, file info decoding, stream buffer encoding, and applications.

Risks/tests: Overflow checks and iterator stability are the main risks. Tests should cover empty Streams, zero-size Blocks, many Records crossing group boundaries, concatenated Streams with padding, duplicate/cat interactions, locating offsets around empty Blocks, maximum VLI boundaries, and the fixed `lzma_index_prealloc(0)` behavior preventing later buffer overflow after decoding an empty Index.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index.h -->
# sources/compression/xz/src/liblzma/common/index.h

Purpose: Internal/test-facing header for Index constants and helper functions without pulling in the full `common.h` dependency tree.

Important APIs/macros: Defines `UNPADDED_SIZE_MIN`, `UNPADDED_SIZE_MAX`, `INDEX_INDICATOR`, declares `lzma_index_padding_size()` and `lzma_index_prealloc()`, and defines inline helpers `vli_ceil4()`, `index_size_unpadded()`, `index_size()`, and `index_stream_size()`.

Control flow/state: No runtime state. Helpers encode `.xz` Index layout rules: Index Indicator, record count, record list, CRC32, four-byte padding, and Stream Header/Footer overhead.

Dependencies/integration: This header intentionally assumes `lzma.h` or `common.h` was included first so include-order problems fail consistently. It is used by internal common files and tests.

Risks/tests: Size arithmetic must stay aligned with the `.xz` specification and encoder/decoder CRC/padding logic. Tests should assert known Index sizes, padding sizes, and VLI boundary behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_decoder.c -->
# sources/compression/xz/src/liblzma/common/index_decoder.c

Purpose: Implements streaming and single-call decoding of the `.xz` Index field into an `lzma_index`.

Important APIs/types: `lzma_index_coder` tracks sequence, memory limit, target index, output pointer, remaining record count, current VLI fields, VLI position, and CRC32. APIs include internal `lzma_index_decoder_init()`, public `lzma_index_decoder()`, and public `lzma_index_buffer_decode()`.

Control flow: The state machine reads `INDEX_INDICATOR`, VLI record count, memory usage check, repeated Unpadded and Uncompressed sizes, Index Padding, and little-endian CRC32. It preallocates record storage after count is known and updates CRC incrementally across calls. On stream completion it transfers ownership by assigning `*index_ptr` and nulling `coder->index`.

State and persistence: Before success, the decoder owns the in-progress `lzma_index` and frees it on reset/end/error. `memconfig` reports `lzma_index_memusage(1, coder->count)` and can raise/lower the limit if current known usage fits.

Dependencies/integration: Depends on `index_decoder.h`, `index.h`, `check.h`, VLI decode, and `lzma_index_append()`. `file_info.c` uses this decoder for reverse metadata parsing.

Risks/tests: Single-call decode restores `*in_pos` and frees partial Index on error, and reports required memory through `*memlimit` on `LZMA_MEMLIMIT_ERROR`. Tests should cover bad indicator, truncated VLI, count over memlimit, invalid Unpadded Size, bad padding, bad CRC, zero-record Index, and fuzzing-mode CRC bypass behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_decoder.h -->
# sources/compression/xz/src/liblzma/common/index_decoder.h

Purpose: Internal declaration header for the Index streaming decoder initializer.

Important API: Declares `lzma_index_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, lzma_index **i, uint64_t memlimit)`.

Control flow/state: No runtime state. The initializer plugs Index decoding into the liblzma `lzma_next_coder` pipeline and is wrapped by public stream and buffer APIs.

Dependencies/integration: Includes `common.h` and `index.h`. Used by `file_info.c` and `index_decoder.c`.

Risks/tests: Build/API synchronization and correct ownership contract for `lzma_index **i` are the relevant checks.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_encoder.c -->
# sources/compression/xz/src/liblzma/common/index_encoder.c

Purpose: Implements streaming and single-call encoding of an `lzma_index` into the `.xz` Index field.

Important APIs/types: `lzma_index_coder` tracks sequence, source Index, `lzma_index_iter`, VLI position, and CRC32. APIs include internal `lzma_index_encoder_init()`, public `lzma_index_encoder()`, and public `lzma_index_buffer_encode()`.

Control flow: The encoder emits Index Indicator, record count, each Block's Unpadded Size and Uncompressed Size from `lzma_index_iter_next()`, padding bytes from `lzma_index_padding_size()`, and CRC32. CRC is updated once per call over bytes produced before the CRC field.

State and persistence: Streaming state persists sequence, iterator, VLI position, and CRC across calls. The input `lzma_index` is borrowed, not owned, so callers must keep it alive while the coder runs.

Dependencies/integration: Depends on `index_encoder.h`, `index.h`, `check.h`, VLI encoding, and iterator APIs from `index.c`. Used by stream buffer encoding and public Index encoding.

Risks/tests: `lzma_index_buffer_encode()` preflights `lzma_index_size(i)` and restores output position on unexpected failure. Tests should cover empty Index, multi-record Index, exact buffer sizing, undersized output, CRC bytes, and streaming calls that split in the middle of VLIs and CRC.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_encoder.h -->
# sources/compression/xz/src/liblzma/common/index_encoder.h

Purpose: Internal declaration header for Index encoder initialization.

Important API: Declares `lzma_index_encoder_init(lzma_next_coder *next, const lzma_allocator *allocator, const lzma_index *i)`.

Control flow/state: No runtime state. Exposes the streaming Index encoder to stream/block container code while keeping public wrappers in `index_encoder.c`.

Dependencies/integration: Includes `common.h`; implemented by `index_encoder.c`.

Risks/tests: Declaration drift is caught by build and Index encode tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_hash.c -->
# sources/compression/xz/src/liblzma/common/index_hash.c

Purpose: Validates an `.xz` Index against Block sizes observed while decoding, without building a full `lzma_index`.

Important APIs/types: `lzma_index_hash_info` tracks padded Block size sum, uncompressed sum, record count, index-list byte size, and an integrity check state over size pairs. `struct lzma_index_hash_s` holds separate `blocks` and `records` info plus decode sequence, remaining count, current VLI fields, VLI position, and CRC32. APIs include `lzma_index_hash_init/end/size/append/decode()`.

Control flow: Callers append each decoded Block with `lzma_index_hash_append()`, which updates sums and hashes and validates global limits. `lzma_index_hash_decode()` then parses Index Indicator, count, records, padding, and CRC. It checks record count equality, ensures decoded record sums never exceed observed Block sums, compares final sums and best-check hashes, then verifies CRC32.

State and persistence: The object persists between Block decoding and Index decoding. Once `lzma_index_hash_decode()` starts, its sequence leaves `SEQ_BLOCK`, and further append calls are programming errors.

Dependencies/integration: Depends on `index.h`, `check.h`, VLI decode, CRC32, and `LZMA_CHECK_BEST`. Used by single-threaded and multithreaded Stream decoders to verify Index integrity with O(1) memory.

Risks/tests: Hashing raw `lzma_vli` arrays means producer and verifier run in the same library ABI, not an interchange format. Tests should cover count mismatch, size mismatch, padding mismatch, CRC failure, zero Blocks, append overflows, invalid unpadded sizes, and incremental Index input boundaries.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/index_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/lzip_decoder.c -->
# sources/compression/xz/src/liblzma/common/lzip_decoder.c

Purpose: Implements `.lz`/lzip member decoding on top of the LZMA1 decoder, including lzip header parsing, CRC32/data/member-size footer validation, concatenated member handling, and memory-limit reporting.

Important APIs/types: `lzma_lzip_coder` stores sequence, version, CRC32, uncompressed and member sizes, memory limits, flags, header/footer position, footer buffer, LZMA options, and nested LZMA decoder. Public `lzma_lzip_decoder()` wraps internal `lzma_lzip_decoder_init()`.

Control flow: `SEQ_ID_STRING` matches `LZIP`. `SEQ_VERSION` accepts versions 0 and 1 and optionally reports `LZMA_GET_CHECK`. `SEQ_DICT_SIZE` decodes the lzip dictionary-size byte into LZMA options with fixed lc/lp/pb. `SEQ_CODER_INIT` checks memory and initializes LZMA1. `SEQ_LZMA_STREAM` forwards data to the nested decoder while updating CRC and observed sizes. `SEQ_MEMBER_FOOTER` validates CRC32, data size, and version-1 member size, then either ends or loops for concatenated members.

State and persistence: Per-member CRC and sizes reset after magic bytes. Concatenated mode uses `first_member` to report non-lzip trailing data as `LZMA_STREAM_END` only after at least one valid member.

Dependencies/integration: Depends on `lzip_decoder.h`, LZMA decoder internals, CRC helpers, and supported liblzma flags (`TELL_ANY_CHECK`, `IGNORE_CHECK`, `CONCATENATED`). It is a format adapter separate from `.xz` stream parsing.

Risks/tests: Trailing-data semantics can discard 1-3 matching magic-prefix bytes after the first member because the API cannot rewind across calls. Tests should cover v0/v1 footers, invalid magic, unsupported version, dictionary byte bounds, CRC and size mismatch, concatenated members, trailing non-lzip data, `IGNORE_CHECK`, and memlimit retry.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/lzip_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/lzip_decoder.h -->
# sources/compression/xz/src/liblzma/common/lzip_decoder.h

Purpose: Internal declaration header for lzip decoder initialization.

Important API: Declares `lzma_lzip_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, uint64_t memlimit, uint32_t flags)`.

Control flow/state: No runtime state; the initializer is used by public lzip decoder setup and generic auto-decoding paths.

Dependencies/integration: Includes `common.h` and is implemented by `lzip_decoder.c`.

Risks/tests: Header drift and flag contract mismatches are caught by build and lzip decode tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/lzip_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/memcmplen.h -->
# sources/compression/xz/src/liblzma/common/memcmplen.h

Purpose: Provides `lzma_memcmplen()`, an inline optimized routine for finding the length of the common prefix between two buffers, starting from a known matching length.

Important APIs/macros: `lzma_memcmplen(buf1, buf2, len, limit)` returns a value in `[len, limit]`. `LZMA_MEMCMPLEN_EXTRA` is defined per implementation path to document how many bytes may be read beyond `limit`.

Control flow: The implementation chooses at compile time between 64-bit unaligned word comparison, SSE2 movemask comparison, generic 32-bit little-endian/big-endian unaligned comparison, and a portable byte loop. Fast paths use ctz/clz or bit scans to locate the first differing byte and clamp to `limit`.

State and dependencies: Header-only, no persistent state. Depends on `common.h`, endian read helpers, compiler intrinsics, `TUKLIB_FAST_UNALIGNED_ACCESS`, and optional `<immintrin.h>`/`<intrin.h>`.

Risks/tests: Callers must provide initialized extra bytes according to `LZMA_MEMCMPLEN_EXTRA`, otherwise fast paths may trip memory sanitizers or fault on invalid padding. Tests should cover equal buffers, first-byte mismatch, mismatches around word boundaries, big/little endian paths where possible, exact limit, nonzero initial `len`, and ASan/Valgrind with required extra padding.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/memcmplen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/microlzma_decoder.c -->
# sources/compression/xz/src/liblzma/common/microlzma_decoder.c

Purpose: Decodes the MicroLZMA format, a compact LZMA1-based stream format with a negated properties byte and externally supplied compressed and uncompressed sizes.

Important APIs/types: `lzma_microlzma_coder` stores nested LZMA decoder, remaining compressed size, remaining/untrusted uncompressed size, dictionary size, exact-size mode, and whether properties have been decoded. Public `lzma_microlzma_decoder()` wraps internal init.

Control flow: Before initializing LZMA, the decoder limits input by remaining `comp_size` and, when uncompressed size is not exact, limits output by remaining `uncomp_size`. It reads one properties byte, negates it, decodes lc/lp/pb, configures LZMA1EXT with exact size when known, initializes the nested decoder, and feeds a dummy leading zero byte expected by the LZMA decoder. Subsequent calls forward to LZMA and update remaining sizes. Exact-size mode requires stream end exactly when compressed bytes are exhausted; inexact mode forbids LZMA EOPM and returns `LZMA_STREAM_END` when the requested output amount has been produced.

State/dependencies: Depends on LZMA decoder internals and LZ decoder size-extension helpers. State persists nested decoder progress and size counters across calls.

Risks/tests: Exact and inexact modes have different end conditions. Tests should cover missing properties byte, invalid properties, compressed-size leftovers, too-small compressed size, inexact output limit, unexpected EOPM, oversized `uncomp_size`, and dummy-byte initialization.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/microlzma_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/microlzma_encoder.c -->
# sources/compression/xz/src/liblzma/common/microlzma_encoder.c

Purpose: Encodes input into MicroLZMA format using LZMA1 and overwriting the first output byte with the bitwise-negated LZMA properties byte.

Important APIs/types: `lzma_microlzma_coder` stores nested LZMA encoder and encoded properties byte. Public `lzma_microlzma_encoder()` supports only `LZMA_FINISH`.

Control flow: Init encodes lc/lp/pb properties from `lzma_options_lzma`, initializes an LZMA1 encoder, and stores the properties. Encoding asks the nested encoder's `set_out_limit()` how many uncompressed bytes fit in the available compressed output, runs the encoder to `LZMA_STREAM_END`, writes `~props` at the first byte of this MicroLZMA chunk, and rewinds `*in_pos` to the number of bytes actually encoded according to `uncomp_size`.

State/dependencies: Depends on LZMA encoder internals and the nested coder's `set_out_limit` capability. It borrows caller options during init and persists only nested encoder state plus properties.

Risks/tests: The nested LZMA encoder may read ahead beyond bytes that fit; correcting `*in_pos` is a critical contract. Tests should cover invalid options, too-small output for `set_out_limit`, multiple calls, exact output boundaries, and property-byte negation.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/microlzma_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/outqueue.c -->
# sources/compression/xz/src/liblzma/common/outqueue.c

Purpose: Implements `lzma_outq`, a FIFO of output buffers with a same-size cache for multithreaded encoding/decoding.

Important APIs: `lzma_outq_memusage()`, `lzma_outq_init()`, `lzma_outq_end()`, `lzma_outq_clear_cache()`, `lzma_outq_clear_cache2()`, `lzma_outq_prealloc_buf()`, `lzma_outq_get_buf()`, `lzma_outq_is_readable()`, `lzma_outq_read()`, and `lzma_outq_enable_partial_output()`.

Control flow: The queue allows up to `2 * threads` allocated buffers to keep workers busy when completion order differs from output order. `lzma_outq_prealloc_buf()` ensures `lzma_outq_get_buf()` cannot fail. Finished head buffers are moved to cache by `move_head_to_cache()`, and cache is cleared when sizes differ. `lzma_outq_read()` copies from the head buffer, returns the buffer's `finish_ret` when fully consumed, and optionally reports Block size metadata.

State/persistence: `lzma_outq` persists linked-list head/tail, read offset, cache list, allocated/in-use memory counters, buffer counts, and buffer limit. Each `lzma_outbuf` persists worker pointer, output positions, finish status, finish return, and Block size metadata.

Dependencies/integration: Used by `stream_decoder_mt.c` and multithreaded encoder code. Relies on caller-held mutexes for fields documented as shared between worker and main threads.

Risks/tests: The implementation does not enforce locking; races are prevented by callers. Tests should cover memory accounting, cache retention by size, reading partial and finished buffers, non-`LZMA_STREAM_END` finish errors, thread limits, and clearing caches under changing block sizes.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/outqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/outqueue.h -->
# sources/compression/xz/src/liblzma/common/outqueue.h

Purpose: Declares the output queue structures and functions used by multithreaded liblzma coders.

Important APIs/types: `lzma_outbuf` is a flexible-array output buffer with worker pointer, allocation size, produced/consumed positions, finish state, finish return, and Block size metadata. `lzma_outq` stores active FIFO, cache, memory counters, and buffer limits. Inline helpers are `lzma_outq_has_buf()`, `lzma_outq_is_empty()`, and `lzma_outq_outbuf_memusage()`.

Control flow/state: The header documents which fields require mutex protection. `pos`, `decoder_in_pos`, and `finished` are shared between worker and main threads. `finish_ret` must not be `LZMA_OK` for a finished buffer because it signals completion/error when the head is drained.

Dependencies/integration: Includes `common.h` and is implemented by `outqueue.c`. Used by multithreaded stream decoder and encoder components.

Risks/tests: The contract depends on caller discipline around mutexes and on buffer-size overflow checks before `lzma_outq_outbuf_memusage()`. Tests should include thread sanitizer coverage in users of the queue and assertion coverage for invalid finish states.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/outqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_buffer_decoder.c -->
# sources/compression/xz/src/liblzma/common/stream_buffer_decoder.c

Purpose: Provides `lzma_stream_buffer_decode()`, a single-call `.xz` Stream decoder wrapper.

Important API: Validates input/output pointers and positions, rejects `LZMA_TELL_ANY_CHECK` for buffer mode, initializes `lzma_stream_decoder_init()`, runs it with `LZMA_FINISH`, translates `LZMA_STREAM_END` to `LZMA_OK`, reports required memory on memlimit failure, rolls back positions on errors, and frees the decoder.

Control flow/state: Uses local `lzma_next_coder stream_decoder`. On `LZMA_OK` from the streaming decoder, it distinguishes truncated input from too-small output: if all input was consumed, the stream is considered truncated; otherwise output space was too small.

Dependencies/integration: Depends on `stream_decoder.h` and the normal `.xz` stream decoder state machine.

Risks/tests: Position rollback and `memlimit` output are important. Tests should cover exact decode, truncated stream, undersized output, unsupported flags, memlimit too low then retry, and zero-length input/output combinations.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_buffer_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_buffer_encoder.c -->
# sources/compression/xz/src/liblzma/common/stream_buffer_encoder.c

Purpose: Implements single-call `.xz` Stream encoding and a bound calculation for caller output buffers.

Important APIs/macros: `lzma_stream_buffer_bound()` returns worst-case output size for one Block plus Stream Header, Index, and Footer. `lzma_stream_buffer_encode()` writes a Stream Header, optional Block, Index, and Stream Footer.

Control flow: The bound uses `lzma_block_buffer_bound()` plus `HEADERS_BOUND`. Encoding validates filters/check/buffers, rejects unsupported checks, reserves Footer space, writes Stream Header, encodes one Block only if input is nonempty, builds an `lzma_index`, appends the Block record when present, encodes the Index, sets `stream_flags.backward_size`, writes Footer, and only then updates `*out_pos_ptr`.

State/dependencies: Uses a local `lzma_stream_flags`, `lzma_block`, and temporary `lzma_index`. Depends on Block buffer encoding, Index APIs, and Stream Header/Footer encoding.

Risks/tests: Empty input produces an empty Index with no Block. Tests should cover empty streams, unsupported checks, small output buffers at each phase, size-bound overflow, exact bound, and failure before `*out_pos_ptr` is committed.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_buffer_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder.c -->
# sources/compression/xz/src/liblzma/common/stream_decoder.c

Purpose: Implements the single-threaded `.xz` Stream decoder state machine.

Important APIs/types: `lzma_stream_coder` owns sequence, nested Block decoder, `lzma_block` options, Stream Flags, `lzma_index_hash`, memory limit/usage, check reporting flags, concatenation flags, buffer position, and a shared header buffer. Public `lzma_stream_decoder()` wraps internal `lzma_stream_decoder_init()`.

Control flow: `SEQ_STREAM_HEADER` reads and validates the Header, reports check notifications if requested, and sets Block check type. `SEQ_BLOCK_HEADER` distinguishes Index Indicator from Block Header and collects full Block Header. `SEQ_BLOCK_INIT` decodes filter options, applies ignore-check, calculates raw decoder memory, enforces memlimit, initializes the Block decoder, and frees temporary filter options. `SEQ_BLOCK_RUN` forwards data/output to the Block decoder and appends observed size pairs to `lzma_index_hash`. `SEQ_INDEX` decodes and verifies Index hash. `SEQ_STREAM_FOOTER` verifies Backward Size and Stream Flags. `SEQ_STREAM_PADDING` handles concatenated Streams and four-byte padding alignment.

State and persistence: The nested Block decoder and Index hash persist across calls. `memusage` is updated only after a valid filter chain is known, so `lzma_memusage()` does not expose `UINT64_MAX` from bad options. `first_stream` converts bad magic in later Streams from format error to data error.

Dependencies/integration: Depends on Block decoder, filter decoder memory usage, Stream Header/Footer helpers, `index_hash.c`, and `lzma_next_coder` callbacks (`end`, `get_check`, `memconfig`).

Risks/tests: Error classification, memlimit retry at `SEQ_BLOCK_INIT`, Index/hash verification, and concatenated padding are critical. Tests should cover all check-reporting flags, unknown filters, low memlimit, unsupported checks, corrupt Block/Header/Footer/Index, concatenated Streams with padding, and `LZMA_FINISH` behavior.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder.h -->
# sources/compression/xz/src/liblzma/common/stream_decoder.h

Purpose: Internal declaration header for `.xz` Stream decoder initialization.

Important API: Declares `lzma_stream_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, uint64_t memlimit, uint32_t flags)`.

Control flow/state: No runtime state. The initializer is used by the public stream decoder API, stream buffer decoder, auto decoders, and related wrappers.

Dependencies/integration: Includes `common.h`; implemented by `stream_decoder.c`.

Risks/tests: Flag contract and declaration synchronization are tested through stream decoder builds and API tests.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder_mt.c -->
# sources/compression/xz/src/liblzma/common/stream_decoder_mt.c

Purpose: Implements multithreaded `.xz` Stream decoding, parallelizing Blocks when Block Header sizes make that safe, while preserving ordered output and exact `.xz` validation semantics.

Important APIs/types: `worker_thread` owns worker state, input buffer, input/output progress, nested Block decoder, copied Block options, filter memory usage, output buffer pointer, mutex/condition, and thread ID. `struct lzma_stream_coder` owns the main sequence, direct-mode decoder, shared Block options/filter buffer, Stream Flags, Index hash, timeout, error fields, thread pool, `lzma_outq`, memory limits/counters, progress counters, flags, and header buffer. Public API is `lzma_stream_decoder_mt()`, backed by `stream_decoder_mt_init()`.

Control flow: The main state machine reads Stream Header and Block Headers like the single-threaded decoder. After Block Header decode, `SEQ_BLOCK_INIT` computes filter memory and decides between threaded mode and direct mode. Threaded mode requires known compressed and uncompressed sizes small enough for `size_t`, enough `memlimit_threading`, a free output queue slot, and a worker. `SEQ_BLOCK_THR_INIT` allocates/cache-trims memory, gets a worker, initializes a thread-local Block decoder, allocates full compressed Block input and full uncompressed output buffers, starts the worker, and enables partial output from the oldest buffer. `SEQ_BLOCK_THR_RUN` feeds the full Block body to the worker while draining ordered output. Direct mode drains all queued worker output, tears down threads, and decodes the Block synchronously for unknown/huge sizes or insufficient thread memory. Index and Footer verification are serialized after all queued output is flushed.

Worker behavior: `worker_decoder()` waits for `THR_RUN`, decodes input in 16 KiB chunks, optionally publishes partial output progress under the main mutex, marks its output buffer finished with success or error, updates global progress, and returns itself to the free-thread stack on success. `threads_stop()` asks workers to stop after unrecoverable errors; `threads_end()` signals exit and joins all initialized threads.

State and persistence: Memory is tracked separately for direct mode, active workers, cached worker filter state, output queue allocations, and the next Block. `memlimit_stop` is the hard limit; `memlimit_threading` can force fallback to direct mode. `pending_error` lets non-fail-fast mode deliver all output before an error location. `get_progress` combines main-thread and per-worker progress under locks.

Dependencies/integration: Depends on Block decoder, Stream Header/Footer helpers, `index_hash.c`, `outqueue.c`, liblzma thread abstraction, and the public `lzma_mt` options structure. Supports `LZMA_RUN` and `LZMA_FINISH`, timeouts, concatenated Streams, check reporting flags, ignore-check, and fail-fast.

Risks/tests: This file has the highest concurrency risk in the subset: lock ordering, partial-output publication, memory counter correctness, worker error propagation, timeout behavior, and direct/threaded transitions. Tests should cover known-size threaded Blocks, unknown-size direct fallback, memlimit forcing direct mode or hard failure, output-order preservation when later Blocks finish first, worker errors with and without `LZMA_FAIL_FAST`, truncated input under `LZMA_FINISH`, timeout returns, progress reporting, concatenated Streams, and thread teardown/reinit across decoder reuse.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/liblzma/common/stream_decoder_mt.c -->
