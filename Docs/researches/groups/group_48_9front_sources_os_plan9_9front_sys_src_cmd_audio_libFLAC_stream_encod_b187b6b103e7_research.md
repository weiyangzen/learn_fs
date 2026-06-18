# Group Research: group_48_9front_sources_os_plan9_9front_sys_src_cmd_audio_libFLAC_stream_encod_b187b6b103e7

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All three listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_encoder.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_encoder.c

## Purpose

This is the main libFLAC stream encoder implementation vendored under 9front's audio command tree. It owns the public `FLAC__StreamEncoder` lifecycle, configuration API, input buffering, frame/subframe model selection, Rice entropy parameter selection, optional verify decoding, file/callback output, Ogg-FLAC wrapping, and final metadata backpatching.

The file is codec infrastructure rather than filesystem code, but it is in subset A through the included `sources/os/plan9/9front` source tree.

## Main Structures and State

- `verify_input_fifo` stores original PCM samples used by the verify decoder path.
- `verify_output` exposes the just-encoded bytes to the internal verification decoder.
- `EncoderStateHint` distinguishes magic, metadata, and audio phases for verify handling.
- `compression_levels_` maps FLAC compression levels 0-8 to mid/side settings, LPC order, Rice partition bounds, and apodization presets.
- `FLAC__StreamEncoderPrivate` is the central private state:
  - input sample buffers for independent channels, mid/side channels, and 33-bit side data for 32-bit stereo;
  - optional floating-point LPC windows and windowed signal buffers;
  - residual workspaces, subframe workspaces, partitioned-Rice workspaces, and best-subframe indexes;
  - bitwriter, STREAMINFO scratch metadata, seektable pointer, current sample/frame counters, MD5 context, CPU dispatch data, and optimized function pointers;
  - callbacks for stream/file/Ogg output and metadata/progress reporting;
  - verification decoder state and mismatch statistics;
  - unaligned allocation pointers for freeing aligned buffers.

## Public API Surface

The file defines the encoder object lifecycle:

- `FLAC__stream_encoder_new()` allocates the public object, protected state, private state, and bitwriter; initializes defaults and Rice-content workspaces.
- `FLAC__stream_encoder_delete()` marks deletion, calls finish, deletes verify decoder if present, clears Rice workspaces, deletes the bitwriter, and frees state.
- `FLAC__stream_encoder_finish()` flushes a partial final frame, finalizes MD5, backpatches metadata when seekable, finishes verification, closes file handles, frees buffers, resets defaults, and returns success/failure.

Initialization entry points share internal setup:

- `FLAC__stream_encoder_init_stream()` initializes callback-based native FLAC output.
- `FLAC__stream_encoder_init_ogg_stream()` initializes callback-based Ogg-FLAC output.
- `FLAC__stream_encoder_init_FILE()` and `FLAC__stream_encoder_init_ogg_FILE()` initialize already-open `FILE *` output.
- `FLAC__stream_encoder_init_file()` and `FLAC__stream_encoder_init_ogg_file()` open a filename or use stdout.

Configuration setters are accepted only while uninitialized. They cover Ogg serial number, verify, streamable subset, MD5, channels, bits per sample, sample rate, compression level, blocksize, mid/side, loose mid/side, apodization, LPC order, QLP precision/search, escape coding, exhaustive model search, residual partition order bounds, Rice search distance, total sample estimate, metadata, minimum bitrate limiting, and internal test/fuzzing disables for instruction sets and subframe types.

Getters expose current encoder state, verify decoder state/error stats, and all major configuration fields.

## Initialization Behavior

`init_stream_internal_()` performs most setup:

- Rejects already-initialized encoders and unsupported Ogg builds.
- Validates callback combinations, channel count, bits per sample, sample rate, blocksize, LPC order, QLP precision, streamable subset constraints, residual partition bounds, and user metadata legality.
- Reorders Ogg Vorbis comment metadata when needed.
- Tracks the first SEEKTABLE metadata block for later seekpoint backpatching.
- Initializes input/workspace pointers, loose mid/side scheduling, sample/frame counters, CPU information, and optimized function pointers.
- Installs architecture-specific LPC/fixed/residual helpers when available and not disabled.
- Allocates encoder buffers via `resize_buffers_()`.
- Initializes the output bitwriter.
- If verification is enabled, allocates a FIFO and initializes an internal stream decoder using local callbacks.
- Writes the FLAC stream sync, STREAMINFO, an empty Vorbis comment if the caller did not supply one, and caller metadata blocks.
- Records `audio_offset` through the tell callback when possible, then switches verify state to audio.

## Input Processing

Two input paths feed blocks:

- `FLAC__stream_encoder_process()` accepts planar per-channel buffers.
- `FLAC__stream_encoder_process_interleaved()` accepts interleaved PCM.

Both paths:

- Require encoder state `FLAC__STREAM_ENCODER_OK`.
- Validate sample values against the configured bits-per-sample range.
- Buffer samples until `blocksize + OVERREAD_` samples are available.
- Keep exactly one overread sample so non-final frames can be emitted while final-frame status is deferred to `finish()`.
- Append original samples to verify FIFO when verification is enabled.
- Compute mid/side samples when enabled; for 32-bit source samples the side channel may need 33-bit storage.
- Call `process_frame_()` for each full non-final block, then move the overread sample to the front of buffers.

## Frame and Subframe Encoding

`process_frame_()`:

- Accumulates the raw signal into MD5 when enabled.
- Calls `process_subframes_()` to build the frame header and subframes.
- Byte-aligns the frame, appends CRC-16, writes the bitbuffer, then updates frame/sample counters and STREAMINFO total sample count.

`process_subframes_()`:

- Computes legal Rice partition order bounds for the current block.
- Builds a `FLAC__FrameHeader`.
- Decides whether to test independent, mid/side, or both channel assignments. Loose mid/side periodically re-evaluates both, then reuses the previous winning style for several frames.
- Detects wasted low bits per channel and right-shifts signals in place.
- Encodes independent and/or mid-side subframe candidates through `process_subframe_()`.
- Chooses the smallest channel assignment among independent, left-side, right-side, and mid-side unless loose mode restricts the choice.
- Emits the frame header with `FLAC__frame_add_header()` and writes selected subframes with `add_subframe_()`.

`process_subframe_()` chooses the best subframe representation:

- Starts with verbatim as the baseline unless disabled.
- Detects constant subframes.
- Evaluates fixed predictors, either a guessed best order or all orders when exhaustive search is enabled.
- In floating-point builds, evaluates LPC predictors across configured apodization windows and optional QLP precision search.
- Supports subdivided Tukey apodization by iterating full, partial, and punchout-style windows.
- Falls back to verbatim if all other enabled paths fail or are disabled.

Subframe evaluators build candidate subframe structures and estimate bit costs:

- `evaluate_constant_subframe_()`
- `evaluate_fixed_subframe_()`
- `evaluate_lpc_subframe_()` when not integer-only
- `evaluate_verbatim_subframe_()`

## Rice Partition Selection

`find_best_partition_order_()`:

- Limits partition order by blocksize and predictor order.
- Precomputes absolute residual sums for all candidate partition orders.
- Optionally precomputes raw-bit escape sizes.
- Tests partition orders from max down to min with `set_partitioned_rice_()`.
- Copies the winning Rice parameters/raw bits into the selected entropy coding method.
- Promotes to `PARTITIONED_RICE2` if any parameter needs the extended range.

`precompute_partition_info_sums_()` computes max-order partition absolute residual sums and merges them into lower-order sums. It chooses 32-bit or 64-bit accumulation based on expected magnitude.

`precompute_partition_info_escapes_()` computes raw residual bit widths for escape-coded partitions and merges max widths for lower orders.

`set_partitioned_rice_()` estimates the Rice parameter from partition residual magnitude, optionally searches nearby parameters if compiled in, optionally chooses escape coding, and returns the estimated coded bit count.

## Output, Metadata, and Verification

`write_bitbuffer_()` obtains the bitwriter buffer, optionally feeds it to the verification decoder, calls `write_frame_()`, releases/clears the bitwriter, and updates min/max frame sizes.

`write_frame_()`:

- Uses tell callbacks to record output positions.
- Captures STREAMINFO and SEEKTABLE offsets while writing metadata.
- Fills seektable entries as audio frames pass target samples.
- Wraps writes through the Ogg encoder aspect when encoding Ogg-FLAC.
- Calls the client write callback and updates bytes/samples/frame counters.

`update_metadata_()` backpatches native FLAC output after encoding by seeking to STREAMINFO fields for MD5, total samples, min/max frame sizes, and then writing sorted seektable entries.

`update_ogg_metadata_()` performs equivalent Ogg-FLAC backpatching by reading/modifying/writing Ogg pages through helper routines.

Verification uses an internal decoder:

- `append_to_verify_fifo_()` and `append_to_verify_fifo_interleaved_()` store source PCM.
- `verify_read_callback_()` feeds encoded bytes to the decoder, with a special magic-string path for stream sync.
- `verify_write_callback_()` compares decoded PCM against the FIFO and records exact mismatch location and expected/got values.
- `verify_error_callback_()` maps decoder errors onto encoder state.

File callbacks provide `FILE *` read/seek/tell/write support and progress reporting. `get_binary_stdout_()` handles binary stdout mode on platforms requiring it.

## Error Handling and Portability Notes

The code is defensive but stateful. Most failures map to `encoder->protected_->state`, including allocation, client callback, framing, verification, Ogg, and I/O errors. Many internal invariants are enforced with `FLAC__ASSERT`, while public-facing checks return false or init status values.

Portability is handled through compile-time guards for Ogg, integer-only builds, assembly/intrinsics, Windows buffering/binary mode, Valgrind testing, and CPU-specific optimized function dispatch.

## Key Dependencies

This file depends heavily on libFLAC internals:

- `private/bitwriter.h` for bitstream construction.
- `private/format.h` and public `FLAC/format.h` constants for frame/metadata layout.
- `private/fixed.h`, `private/lpc.h`, and `private/window.h` for prediction.
- `private/md5.h` for STREAMINFO MD5.
- `private/cpu.h` for runtime dispatch.
- `private/stream_encoder_framing.h` for metadata/frame/subframe serialization.
- Optional Ogg helper/mapping headers.

## Research Notes

This file is the behavioral center of the encoder. The framing helper writes syntax, and the window helper computes LPC analysis windows, but this file decides when and how to use them. The highest-risk areas for maintenance are the block overread protocol, mutable wasted-bit shifting, 32-bit versus 33-bit side-channel paths, metadata offset backpatching, and conditional optimized function dispatch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_encoder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_encoder_framing.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_encoder_framing.c

## Purpose

This file serializes FLAC metadata blocks, frame headers, and subframes into a `FLAC__BitWriter`. It is the low-level syntax writer used by `stream_encoder.c` after that file has selected metadata, frame parameters, channel assignments, subframe types, predictor data, and entropy parameters.

## Metadata Serialization

`FLAC__add_metadata_block()` writes a complete FLAC metadata block:

- Writes the `is_last` flag, metadata type, and metadata length.
- Adjusts Vorbis comment length to substitute the library vendor string.
- Serializes all known block types:
  - STREAMINFO: block sizes, frame sizes, sample rate, channels, bits per sample, total samples, MD5.
  - PADDING: zero bytes.
  - APPLICATION: application ID plus payload.
  - SEEKTABLE: sample number, stream offset, and frame sample count per point.
  - VORBIS_COMMENT: vendor string and user comments in little-endian length-prefixed form.
  - CUESHEET: catalog, lead-in, CD flag, tracks, ISRCs, and indices.
  - PICTURE: type, MIME, description, dimensions, color info, and image bytes.
  - Unknown metadata: raw payload bytes.
- Ensures output remains byte-aligned.

The STREAMINFO total sample field is written as zero if it exceeds the field width.

## Frame Header Serialization

`FLAC__frame_add_header()` writes a FLAC frame header:

- Writes sync code, reserved bit, and blocking strategy.
- Encodes blocksize using standard FLAC hints when possible, or writes extra 8/16-bit blocksize fields for uncommon sizes.
- Encodes sample rate using standard hints, or extra 8/16-bit sample-rate fields for custom rates.
- Encodes channel assignment: independent, left-side, right-side, or mid-side.
- Encodes bits per sample, reserved zero pad, and frame/sample number as UTF-8 integer.
- Appends the frame-header CRC-8.

The caller is responsible for giving a valid `FLAC__FrameHeader`; this function asserts invariants and returns false on bitwriter failure.

## Subframe Serialization

The file provides one writer per subframe type:

- `FLAC__subframe_add_constant()` writes subframe type, optional wasted-bits unary count, and the constant sample value.
- `FLAC__subframe_add_fixed()` writes type/order, wasted bits, warmup samples, entropy coding method, and fixed residual.
- `FLAC__subframe_add_lpc()` writes type/order, wasted bits, warmup samples, QLP precision, quantization shift, QLP coefficients, entropy coding method, and LPC residual.
- `FLAC__subframe_add_verbatim()` writes type, wasted bits, and raw samples, supporting both 32-bit and 33-bit verbatim data paths.

All subframe writers return `false` on any bitwriter write failure.

## Entropy Coding Helpers

`add_entropy_coding_method_()` writes the entropy method type and partition order for partitioned Rice or Rice2. Other types assert as unsupported.

`add_residual_partitioned_rice_()` writes partitioned residual data:

- Selects Rice parameter field width and escape value depending on normal Rice versus Rice2.
- For partition order 0, writes a single parameter and encodes all residuals, or writes escape raw bits.
- For higher partition orders, iterates partitions, subtracting predictor warmup samples from partition 0, then writes either Rice-coded residual blocks or raw escape-coded residuals.
- Uses `FLAC__bitwriter_write_rice_signed_block()` for normal Rice coding and raw signed integer writes for escape partitions.

## Key Dependencies

- `private/stream_encoder_framing.h` for exported framing declarations.
- `private/crc.h` and bitwriter CRC support for frame header CRC.
- `FLAC/assert.h`, `share/compat.h`, and public format constants/macros.

## Research Notes

This file does not choose compression models; it faithfully serializes structures prepared by `stream_encoder.c`. The main correctness sensitivities are exact FLAC field widths, byte alignment, Vorbis-comment vendor length adjustment, partition-0 predictor-order handling, and Rice versus Rice2 escape parameter widths.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/stream_encoder_framing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/window.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/window.c

## Purpose

This file computes floating-point apodization windows for LPC analysis in the FLAC encoder. It is compiled only when `FLAC__INTEGER_ONLY_LIBRARY` is not defined. `stream_encoder.c` allocates and fills these windows during buffer resize, then applies them before LPC autocorrelation.

## Window Functions

The file implements these window generators:

- `FLAC__window_bartlett()`: triangular Bartlett window with separate odd/even handling.
- `FLAC__window_bartlett_hann()`: Bartlett-Hann blend using absolute center distance and cosine taper.
- `FLAC__window_blackman()`: standard Blackman coefficients.
- `FLAC__window_blackman_harris_4term_92db_sidelobe()`: 4-term Blackman-Harris window.
- `FLAC__window_connes()`: squared parabolic Connes window.
- `FLAC__window_flattop()`: flat-top cosine-series window.
- `FLAC__window_gauss()`: Gaussian window with validated standard deviation; invalid or NaN values recurse to a default.
- `FLAC__window_hamming()`: Hamming window.
- `FLAC__window_hann()`: Hann window.
- `FLAC__window_kaiser_bessel()`: Kaiser-Bessel-derived cosine approximation.
- `FLAC__window_nuttall()`: Nuttall cosine-series window.
- `FLAC__window_rectangle()`: all ones.
- `FLAC__window_triangle()`: triangular window using `L + 1` denominator.
- `FLAC__window_tukey()`: rectangle/Hann hybrids with parameter validation and NaN fallback.
- `FLAC__window_partial_tukey()`: zero outside a selected `[start, end)` region, Tukey-tapered inside.
- `FLAC__window_punchout_tukey()`: inverse-style Tukey with a zeroed middle region and tapered kept regions.
- `FLAC__window_welch()`: parabolic Welch window.

## Parameter Handling

Several parameterized windows guard invalid values:

- Gaussian `stddev` must be `0 < stddev <= 0.5`; invalid values fall back to `0.25`.
- Tukey `p <= 0` becomes rectangular; `p >= 1` becomes Hann; NaN-like invalid values fall back to `0.5`.
- Partial and punchout Tukey clamp invalid `p` by recursively using `0.05`, `0.95`, or `0.5`.

Most functions assume a positive length `L` supplied by the encoder. They compute `N = L - 1` where needed and fill exactly `L` entries.

## Key Dependencies

- `<math.h>` for `cosf`, `fabsf`, `exp`, and `M_PI`.
- `FLAC/format.h` and `private/window.h` for FLAC types and declarations.
- `share/compat.h` for portability.
- MSVC warning pragmas suppress float conversion warnings around the implementation.

## Relationship to Encoder

`stream_encoder.c` parses apodization names such as `tukey(5e-1)`, `subdivide_tukey(2)`, `partial_tukey(...)`, and `punchout_tukey(...)`. During buffer allocation or blocksize changes, it calls these functions to precompute windows. LPC analysis then multiplies integer samples by the selected window before autocorrelation and coefficient search.

## Research Notes

This file is mathematically simple and self-contained. Its correctness depends on matching libFLAC's expected window formulas and edge behavior. Parameter validation is intentionally local so malformed apodization specifications do not propagate NaN-heavy windows into LPC analysis.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/window.c -->