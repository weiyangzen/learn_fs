# Group Research: group_45_9front_sources_os_plan9_9front_sys_src_cmd_audio_libFLAC_lpc_c_source_7732db723b42

Scope checked against `Docs/research_subset_a.md`: all files are inside `sources/os/plan9/9front`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/lpc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/lpc.c

## Role

`lpc.c` implements libFLAC linear predictive coding support for FLAC encoding and decoding. It covers windowing, autocorrelation, Levinson-Durbin LPC coefficient generation, QLP coefficient quantization, residual generation, signal restoration, residual bit-depth estimation, and best-order selection.

This is codec math code rather than filesystem code, but it is part of the 9front Plan 9 audio command source tree.

## Major Functions

- `FLAC__lpc_window_data*()` multiplies 32-bit or 64-bit sample input by a floating-point analysis window. Partial variants handle shifted partition windows.
- `FLAC__lpc_compute_autocorrelation()` computes autocorrelation for requested lags using a locality-oriented loop.
- `FLAC__lpc_compute_lp_coefficients()` derives LPC coefficients and error terms from autocorrelation, stopping early if prediction error reaches zero.
- `FLAC__lpc_quantize_coefficients()` scales floating-point LPC coefficients into signed integer QLP coefficients, with shift-limit handling and clipping.
- `FLAC__lpc_compute_residual_from_qlp_coefficients*()` computes encoded residuals from input samples and QLP predictors.
- `FLAC__lpc_compute_residual_from_qlp_coefficients_limit_residual*()` validates residuals fit in signed 32-bit range and are not `INT32_MIN`.
- `FLAC__lpc_restore_signal*()` reconstructs decoded samples from residuals and predictor history.
- `FLAC__lpc_max_prediction_before_shift_bps()` and `FLAC__lpc_max_residual_bps()` estimate predictor and residual bit widths.
- `FLAC__lpc_compute_expected_bits_per_residual_sample*()` and `FLAC__lpc_compute_best_order()` estimate coding cost and select the best LPC order.

## Plan 9 / Portability Notes

The file has a Plan 9-specific compatibility branch defining `_copysign()` and `lround()` when `Plan9` is defined. Floating-point LPC analysis is excluded under `FLAC__INTEGER_ONLY_LIBRARY`, but residual restore and bit-depth helpers remain available.

## Important Implementation Details

The hot residual and restore paths use hand-unrolled branches for LPC orders up to 12, then a fallthrough `switch` for orders up to 32. These functions intentionally index `data[i-order]` and similar negative offsets from the current data pointer; callers must pass a pointer positioned after warm-up samples.

There are normal and wide paths. Normal paths accumulate in `FLAC__int32`; wide paths use `FLAC__int64`. The limit-residual variants are safer for encoder decisions because they reject residuals outside the legal 32-bit range before storing.

Coefficient quantization can return `0` for success, `1` if a negative shift is too small to represent, and `2` if all coefficients are zero. A rare negative shift is handled by scaling coefficients down and then forcing shift to zero, because FLAC decoder-side LPC shifts cannot be negative.

## Risks / Edge Cases

- The performance paths rely heavily on signed integer overflow behavior in audio math. Fuzzing builds can suppress signed-overflow sanitizer for restore functions.
- The unrolled loops require `order > 0` and `order <= 32`; these are asserted, not fully runtime-validated in release builds.
- Residual and restore callers must preserve enough predictor history before the `data` pointer.
- `FLAC__lpc_max_prediction_before_shift_bps()` sums `abs(qlp_coeff[i])` into `FLAC__int32`; extremely large coefficient sets would be risky, though FLAC coefficient precision normally bounds this.

## Dependencies

Uses `FLAC/assert.h`, `FLAC/format.h`, `private/bitmath.h`, `private/lpc.h`, `private/macros.h`, and `share/compat.h`. The file depends on libFLAC numeric typedefs and format constants such as `FLAC__MAX_LPC_ORDER`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/lpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/md5.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/md5.c

## Role

`md5.c` implements MD5 accumulation for libFLAC. FLAC uses MD5 as an audio stream integrity checksum, not as a security primitive. The file combines a public-domain MD5 transform with FLAC-specific formatting that converts decoded PCM sample arrays into the canonical little-endian byte stream before updating the digest.

## Major Functions

- `FLAC__MD5Transform()` is the core 64-step MD5 block transform over four 32-bit state words.
- `byteSwap()` and `byteSwapX16()` are big-endian helpers; on little-endian builds they compile to no-ops.
- `FLAC__MD5Update()` appends arbitrary bytes to the MD5 context, buffering partial 64-byte blocks.
- `FLAC__MD5Init()` initializes MD5 state and clears the reusable internal sample buffer.
- `FLAC__MD5Final()` pads the message, appends bit length, writes the 16-byte digest, frees the internal buffer, and zeroes the context.
- `format_input_()` interleaves per-channel FLAC integer samples into little-endian bytes for 1-, 2-, 3-, and 4-byte sample widths.
- `FLAC__MD5Accumulate()` sizes or grows the internal buffer, formats samples, and feeds them to `FLAC__MD5Update()`.

## Important Implementation Details

`format_input_()` special-cases common channel/sample-width combinations: 1, 2, 4, 6, and 8 channels for 1-, 2-, and 4-byte samples, plus common 3-byte mono/stereo cases. Other combinations fall back to general nested loops.

For 2- and 4-byte samples, it writes through `FLAC__int16 *` and `FLAC__int32 *` aliases and applies `H2LE_16` / `H2LE_32`. For 3-byte samples it writes bytes manually by shifting the signed 32-bit sample.

`FLAC__MD5Accumulate()` checks multiplication overflow before using the computed total size for allocation behavior. The initial `bytes_needed` expression is computed before the checks, but because it is `size_t`, wraparound is defined and the checked path returns `false` before the wrapped value is used for buffer growth.

## Risks / Edge Cases

- `bytes_per_sample` values outside 1..4 cause `format_input_()` to do nothing, but `FLAC__MD5Accumulate()` will still update MD5 with whatever is in the buffer. The caller is expected to supply valid FLAC sample sizes.
- The internal buffer is reused and only reallocated when capacity is too small. Failed `safe_realloc_()` is followed by `safe_malloc_()`, preserving a fallback allocation attempt.
- MD5 length tracking uses two 32-bit byte counters and writes a 64-bit bit length at finalization, matching MD5 expectations.
- `FLAC__MD5Final()` frees `ctx->internal_buf.p8` and zeroes the full context, so the context must be reinitialized before reuse.

## Dependencies

Uses `private/md5.h` for the context layout, `share/alloc.h` for safe allocation helpers, `share/compat.h`, and `share/endswap.h` for endian conversions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/md5.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/memory.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/memory.c

## Role

`memory.c` provides libFLAC allocation helpers for aligned arrays and one local safe multiplication allocator. It centralizes the pattern where callers keep both the original malloc pointer for `free()` and an aligned alias for SIMD-friendly access.

## Major Functions

- `FLAC__memory_alloc_aligned()` allocates raw memory and returns both the base allocation and an aligned address through an out parameter.
- `FLAC__memory_alloc_aligned_int32_array()`
- `FLAC__memory_alloc_aligned_uint32_array()`
- `FLAC__memory_alloc_aligned_int64_array()`
- `FLAC__memory_alloc_aligned_uint64_array()`
- `FLAC__memory_alloc_aligned_unsigned_array()`
- `FLAC__memory_alloc_aligned_real_array()` when not building `FLAC__INTEGER_ONLY_LIBRARY`
- `safe_malloc_mul_2op_p()` allocates `size1 * size2` with overflow checking and converts zero-size requests into `malloc(1)`.

## Important Implementation Details

If `FLAC__ALIGN_MALLOC_DATA` is defined, `FLAC__memory_alloc_aligned()` overallocates by 31 bytes and rounds the returned alias up to a 32-byte boundary. Otherwise, the aligned pointer is simply the base pointer.

Each typed array allocator checks `elements > SIZE_MAX / sizeof(*pu)` before multiplying. It allocates a new buffer first, then frees the previous `*unaligned_pointer` only after the new allocation succeeds. This avoids losing the old allocation on failure.

The functions use small unions to store `void *` and typed pointers, avoiding C99 strict-aliasing problems when receiving the aligned address through a `void **`.

## Risks / Edge Cases

- The API requires `unaligned_pointer` and `aligned_pointer` to be distinct, non-null output locations. These are asserted, not handled in release builds.
- `elements > 0` is asserted. Zero-length array allocation is not a supported caller contract for the typed aligned array helpers.
- Callers must free the unaligned/base pointer, not the aligned alias.
- `safe_malloc_mul_2op_p()` differs from direct `malloc(0)` by always allocating at least one byte when either operand is zero, following the local FLAC convention.

## Dependencies

Uses `private/memory.h`, `FLAC/assert.h`, `share/compat.h`, and `share/alloc.h`. It depends on libFLAC typedefs for fixed-width integer and real sample types.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/metadata_iterators.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/metadata_iterators.c

## Role

`metadata_iterators.c` implements libFLAC metadata access and mutation APIs. It has three layers: level 0 convenience getters, level 1 simple file iterator operations, and level 2 in-memory metadata chains plus chain iterators. It reads, writes, inserts, deletes, pads, and rewrites FLAC metadata blocks.

## Level 0: Convenience Getters

`get_one_metadata_block_()` creates a stream decoder, disables MD5 checking, asks for one metadata type, and clones the matching metadata block from the decoder callback. Public wrappers expose `FLAC__metadata_get_streaminfo()`, `FLAC__metadata_get_tags()`, `FLAC__metadata_get_cuesheet()`, and `FLAC__metadata_get_picture()`.

`FLAC__metadata_get_picture()` scans picture blocks with the simple iterator and selects the largest matching image by area, using depth as a tie-breaker.

## Level 1: Simple Iterator

`FLAC__Metadata_SimpleIterator` owns a `FILE *`, filename, optional temp path prefix, saved file stats, current block offset, first STREAMINFO offset, current block header fields, and a small offset stack for push/pop navigation.

Important operations:

- `FLAC__metadata_simple_iterator_init()` opens a file read-write when possible, otherwise read-only, finds the FLAC signature, and verifies the first metadata block is STREAMINFO.
- `next()` and `prev()` traverse metadata blocks by seeking over block lengths.
- `get_block()` allocates a `FLAC__StreamMetadata`, reads current block data, then seeks back to the block data start.
- `set_block()`, `insert_block_after()`, and `delete_block()` either write in place, split or consume padding, or rewrite the whole file through a temp file.
- `rewrite_whole_file_()` copies prefix, writes replacement or inserted metadata, copies postfix, fixes `is_last` flags when needed, renames the temp file over the original, and re-primes the iterator.

STREAMINFO replacement is constrained: replacing STREAMINFO with a different type, or inserting STREAMINFO, is rejected.

## Level 2: Chains

`FLAC__Metadata_Chain` stores metadata blocks as a doubly linked list of `FLAC__Metadata_Node`. Chain reading supports native FLAC by parsing metadata directly and Ogg FLAC by using a stream decoder callback path. Ogg chain writing is explicitly unsupported.

Important chain operations:

- `chain_read_cb_()` parses all metadata blocks into nodes and records first/last offsets and initial chain length.
- `chain_prepare_for_write_()` adjusts padding to avoid a whole-file rewrite when possible, adds or trims terminal padding, and rejects non-padding metadata blocks that exceed FLAC’s 24-bit metadata length field.
- `FLAC__metadata_chain_check_if_tempfile_needed()` mirrors the write-preparation sizing logic without mutating the chain.
- `FLAC__metadata_chain_write()` writes metadata in place if length is unchanged; otherwise it rewrites via temp file.
- Callback write APIs enforce correct use: in-place callback write must not need a temp file, while temp-file callback write must need one.
- `FLAC__metadata_chain_sort_padding()` moves padding blocks to the end, then merges adjacent padding.

`FLAC__Metadata_Iterator` navigates and mutates the in-memory chain. It cannot delete or insert before the first STREAMINFO block, and it rejects insertion of STREAMINFO elsewhere.

## Metadata Parsing and Serialization

The file implements local big-endian and little-endian pack/unpack helpers. It reads and writes all standard FLAC metadata types:

- STREAMINFO
- PADDING
- APPLICATION
- SEEKTABLE
- VORBIS_COMMENT
- CUESHEET
- PICTURE
- UNKNOWN/opaque blocks

Vorbis comment lengths are little-endian; most FLAC structure fields are big-endian. Padding is skipped on read and emitted as zero-filled blocks on write. Unknown blocks are preserved as opaque bytes.

The FLAC signature scanner skips an optional ID3v2 tag before checking for `fLaC`.

## File Rewrite and Platform Behavior

Temp files default to `<filename>.metadata_edit`. `transport_tempfile_()` closes the temp file and renames it over the original, with Windows-specific unlink-before-rename handling. Comments note that `tempfile_path_prefix` support is incomplete because cross-filesystem movement would require copy rather than rename.

`get_file_stats_()` and `set_file_stats_()` preserve mode and times, and on non-Windows-like builds attempt owner/group restoration via `chown()`. File I/O is routed through compatibility wrappers such as `flac_fopen`, `flac_rename`, `flac_unlink`, `flac_stat`, `flac_chmod`, and `flac_utime`.

## Risks / Edge Cases

- `write_metadata_block_stationary_with_padding_()` returns `FLAC__METADATA_SIMPLE_ITERATOR_STATUS_MEMORY_ALLOCATION_ERROR` from a `FLAC__bool` function when padding allocation fails, without setting iterator status. Since that enum value is nonzero, this can be misread as success and should be verified against upstream or tested.
- `read_metadata_block_data_application_cb_()` reads the 4-byte application ID before checking whether `block_length` is at least 4.
- Vorbis comment parsing is intentionally lenient: malformed lengths can cause the parser to skip remaining bytes and still return OK after preserving partial data.
- Ogg FLAC chain offsets are marked as wrong placeholders, and write-back for Ogg FLAC returns internal error.
- The temp-file replacement path is rename-based and not crash-atomic in the stronger transactional sense.
- Many invariants rely on assertions: valid initialized iterators, non-null callbacks, STREAMINFO first, sane block sizes, and small push depth.

## Dependencies

Uses `private/metadata.h`, `FLAC/stream_decoder.h`, `FLAC/assert.h`, `share/alloc.h`, `share/compat.h`, `share/macros.h`, `share/safe_str.h`, `private/macros.h`, and `private/memory.h`. It aliases `safe_malloc_mul_2op_` to `safe_malloc_mul_2op_p` from `memory.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/metadata_iterators.c -->