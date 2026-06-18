# Group Research: group_54_9front_sources_os_plan9_9front_sys_src_cmd_audio_mp3dec_bit_c_sources_4eb5a1027ecf

Source-read status: complete for every listed file in `sources/os/plan9/9front/sys/src/cmd/audio/mp3dec`. This group is an embedded libmad-based MP3 decoder/player adapted for Plan 9/9front, with fixed-point MPEG audio decode code plus a small Plan 9 `main.c` frontend that pipes decoded samples through `/bin/audio/pcmconv`.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/bit.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/bit.c

This file implements libmad's low-level bitstream reader and CRC helper. It owns `mad_bit_init`, `mad_bit_length`, `mad_bit_nextbyte`, `mad_bit_skip`, `mad_bit_read`, and `mad_bit_crc`. The central abstraction is `struct mad_bitptr`, which tracks a byte pointer, cached byte value, and remaining bits in the current byte.

The implementation reads UIMSBF bit fields of arbitrary length, advances byte/bit state, supports skipping ahead, and computes MPEG CRC-16 using the ISO/IEC 11172-3 generator polynomial `0x8005`. The CRC table is static lookup data used by frame and layer decoders to validate protected MPEG frames. `mad_bit_write` is present only in a disabled `#if 0` block, while `bit.h` still declares it.

In the decoder pipeline, this file is foundational: `frame.c`, `layer12.c`, `layer3.c`, and `stream.c` all depend on bit-exact reading. The code assumes callers have already ensured enough guard bytes in the stream buffer; most overrun protection happens at the stream/frame/layer level rather than inside `mad_bit_read`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/bit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/bit.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/bit.h

This header defines the bit-reader interface for the MP3 decoder. `struct mad_bitptr` contains `byte`, `cache`, and `left`, representing the current byte address, cached byte contents, and number of unread bits left in that byte.

It declares initialization, length calculation between two bit pointers, next-byte discovery, skip/read/write operations, and CRC calculation. `mad_bit_finish` is a no-op macro because the bit pointer owns no dynamic memory. `mad_bit_bitsleft` exposes the `left` field directly for performance-sensitive code, especially Layer III Huffman decoding.

The header is included throughout the decode stack: stream synchronization initializes bit pointers; frame header parsing reads bit fields; Layer I/II sample parsing and Layer III side-info/Huffman parsing use it heavily. `mad_bit_write` is declared but not compiled in `bit.c`, so external users should not rely on it unless they also enable/provide that implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/bit.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/decoder.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/decoder.c

This file implements libmad's callback-driven decoder orchestration. `mad_decoder_init` records client callbacks for input, header, filter, output, error, and message handling. `mad_decoder_run` allocates the synchronous state bundle (`mad_stream`, `mad_frame`, `mad_synth`) and dispatches to synchronous decoding, or to an optional asynchronous mode when `USE_ASYNC` is compiled in.

The synchronous loop repeatedly asks the input callback for data, decodes headers and frames, runs an optional filter, synthesizes PCM via `mad_synth_frame`, and delivers PCM to the output callback. Recoverable errors are routed through either a user callback or `error_default`, which ignores CRC errors and mutes repeated bad CRC frames. Nonrecoverable errors break the loop.

The async path, guarded by `USE_ASYNC`, uses pipes, `fork`, and simple length-prefixed messages between parent and child. In this 9front player, `main.c` runs only `MAD_DECODER_MODE_SYNC`, so the active path is the callback loop around `stream.c`, `frame.c`, layer decoders, and synthesis.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/decoder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/decoder.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/decoder.h

This header defines the public decoder control API. It declares `enum mad_decoder_mode` for sync/async operation, `enum mad_flow` for callback control (`CONTINUE`, `STOP`, `BREAK`, `IGNORE`), and `struct mad_decoder`, which stores options, async pipe/process metadata, synchronous decode state, callback data, and callback function pointers.

The callback surface is the key contract: clients provide input data, may inspect headers, may filter decoded frames, consume PCM, handle errors, and optionally exchange messages with an async decoder. `mad_decoder_options` is a macro that writes option flags into the decoder before running.

Within this group, `main.c` uses this API as a small MP3 player: input reads stdin, header handles seeking, output writes converted PCM, and error skips tags/reports decode errors. This header depends on `stream.h`, `frame.h`, and `synth.h` because the callback signatures expose those structures.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/decoder.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/fixed.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/fixed.c

This file provides C helper routines for libmad fixed-point arithmetic. `mad_f_abs` returns the absolute value of a fixed-point integer. `mad_f_div` performs fixed-point division using integer quotient/remainder expansion, rounding, sign correction, and overflow guarding against the fixed-point representable range.

The decoder uses a 28-fraction-bit fixed-point format defined in `fixed.h`, so division must produce values scaled into the same representation. `mad_f_div` first computes an integer quotient, then iteratively shifts remainder bits into the fractional field until either all fraction bits are generated or the remainder reaches zero. It rounds based on the final remainder.

Most multiplication is macro/assembly driven in `fixed.h`; this file contains the few arithmetic routines that are easier or more portable as functions. Correctness here affects requantization, synthesis math, and Layer I/II scaling wherever division or absolute value is required.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/fixed.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/fixed.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/fixed.h

This header defines libmad's fixed-point numeric model for the 9front build. It uses Plan 9 integer types (`u32int`, `vlong`) and defines `mad_fixed_t` as 32-bit signed fixed point with `MAD_F_FRACBITS == 28`. The representable range is approximately -8.0 to +8.0, with `MAD_F_ONE` as `0x10000000`.

The header provides conversion, integer/fraction extraction, add/subtract, and multiplication/scaling macros. It includes multiple architecture-specific multiplication implementations, including Intel inline assembly, ARM, MIPS, SPARC, PowerPC, 64-bit, and portable fallback paths. The active path depends on compile-time `FPM_*` and optimization flags. If neither an FPM mode nor fallback is selected, preprocessing fails.

Layer decoders and synthesis code rely on these macros for every scaling, requantization, IMDCT, windowing, and stereo operation. This file is performance-critical and assumes compiler support for the selected inline assembly/macros. It declares `mad_f_abs` and `mad_f_div`, implemented in `fixed.c`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/fixed.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/frame.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/frame.c

This file decodes MPEG audio frame headers, chooses the layer decoder, and manages frame-level state. It defines bitrate and sample-rate lookup tables, maps layers I/II/III to `mad_layer_I`, `mad_layer_II`, and `mad_layer_III`, and implements initialization/cleanup for `mad_header` and `mad_frame`.

`decode_header` parses sync, MPEG version flags including unofficial MPEG 2.5, layer, CRC protection, bitrate index, sample rate, padding, private bit, mode, mode extension, copyright/original flags, and emphasis. `mad_header_decode` handles stream sync, skip requests, free-format bitrate detection, next-frame length calculation, buffer-length validation, and incomplete-header marking. `free_bitrate` scans for the next compatible frame to infer free-format rate.

`mad_frame_decode` ensures a header exists, dispatches to the appropriate layer decoder, and records ancillary data boundaries for non-Layer III frames. `mad_frame_mute` zeroes all subband samples and any Layer III overlap buffer. This file is the bridge between byte stream management and actual MPEG layer decoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/frame.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/frame.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/frame.h

This header defines MPEG frame/header types and constants. It declares `enum mad_layer`, `enum mad_mode`, and `enum mad_emphasis`, plus `struct mad_header` for parsed metadata and `struct mad_frame` for decoded subband samples and Layer III overlap state.

Important macros include `MAD_NCHANNELS`, which maps single-channel mode to one channel and all other modes to two, and `MAD_NSBSAMPLES`, which returns 12, 18, or 36 subband sample groups depending on layer and LSF status. The flags enum records protection, padding, stereo mode features, free format, LSF, multichannel extension, MPEG 2.5, and incomplete-header status. Private bit constants separate header private data from Layer III private bits.

The public API initializes/finishes headers and frames, decodes a header, decodes a full frame, and mutes a frame. It depends on `fixed.h` and `stream.h`, and is consumed by the decoder orchestrator, layer decoders, and the Plan 9 frontend's header callback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/frame.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/global.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/global.h

This is the small global portability/configuration header for the 9front libmad copy. It includes Plan 9 system headers `<u.h>` and `<libc.h>`, replacing the broader autoconf/platform headers used by upstream libmad in many builds.

It also enforces that `OPT_SPEED` and `OPT_ACCURACY` are mutually exclusive, and implicitly enables `OPT_SSO` when `OPT_SPEED` is selected. Those flags affect arithmetic and synthesis optimization choices in fixed-point code and other libmad modules.

This file is included by most implementation files before local decoder headers. Its role is not algorithmic; it establishes the Plan 9 compilation environment and shared compile-time feature rules. Because it uses Plan 9 headers directly, this source tree is adapted for 9front rather than a generic portable libmad checkout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/global.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/huffman.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/huffman.c

This file is static Layer III Huffman lookup data derived from ISO/IEC 11172-3 Table B.7. It defines quad tables `hufftabA` and `hufftabB` for count1 regions and pair tables `hufftab0`, `hufftab1`, `hufftab2`, `hufftab3`, `hufftab5`, `hufftab6`, `hufftab7`, `hufftab8`, `hufftab9`, `hufftab10`, `hufftab11`, `hufftab12`, `hufftab13`, `hufftab15`, `hufftab16`, and `hufftab24`.

The table entries use local `PTR` and `V` macros to represent either intermediate lookup nodes or final decoded symbols with Huffman length metadata. The layout supports decoding up to four Huffman bits at a time, with occasional secondary lookups through offsets. At the end, `mad_huff_quad_table[2]` exposes the two quad tables, and `mad_huff_pair_table[32]` maps MPEG table-select indices to table pointers, `linbits`, and starting lookup widths. Unused table-select values are represented with null entries.

There is no executable decode routine here; `layer3.c` consumes these tables in `III_huffdecode`. The correctness and shape of this data directly determine Layer III spectral coefficient decoding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/huffman.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/huffman.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/huffman.h

This header defines the data structures used by Layer III Huffman decoding. `struct huffquad` stores either an intermediate pointer (`bits`, `offset`) or a final quadruple value (`v`, `w`, `x`, `y`, `hlen`). `struct huffpair` is the equivalent for decoded pair values (`x`, `y`, `hlen`). Each entry has a `final` byte indicating whether the lookup is terminal.

`struct hufftable` wraps a pair table pointer with the table's `linbits` and `startbits`, allowing Layer III code to select the correct lookup behavior for each MPEG Huffman table number. The header exports `mad_huff_quad_table` and `mad_huff_pair_table`, both defined in `huffman.c`.

This header has no functions; it is a compact ABI between table data and `layer3.c`'s `III_huffdecode`. The design favors fast table-driven decoding over bit-by-bit tree traversal.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/huffman.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer12.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer12.c

This file implements MPEG Layer I and Layer II frame decoding. It includes scalefactor data from `sf_table.dat`, Layer I linear scaling constants, Layer II subband quantization tables, bit-allocation tables, offset tables, and quantization classes from `qc_table.dat`.

For Layer I, `I_sample` reads and requantizes a sample, while `mad_layer_I` parses bit allocations, validates CRC when enabled, reads scalefactors, handles joint stereo bounds, and fills `frame->sbsample` for 12 sample groups. For Layer II, `II_samples` handles grouped and ungrouped quantized samples, and `mad_layer_II` selects the appropriate allocation table based on MPEG version, bitrate/channel mode, and sample rate. It decodes allocations, scalefactor selection info, CRC, scalefactors, sample groups, and zero-fills unused subbands.

The output is subband-domain fixed-point data consumed later by synthesis. Error reporting uses `stream->error` values such as bad CRC, bad bit allocation, bad mode, and bad scalefactor. This file is self-contained for Layers I/II and shares only common bit, stream, frame, and fixed-point helpers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer12.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer12.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer12.h

This header exposes the Layer I and Layer II decoder entry points: `mad_layer_I` and `mad_layer_II`. Both take a `struct mad_stream *` and `struct mad_frame *`, reading compressed frame data from the stream and filling the frame's subband sample array.

It includes `stream.h` and `frame.h` because those structures are part of the function signature. `frame.c` uses this header to populate its layer dispatch table, mapping MPEG header layer values to the correct decoder implementation.

There are no data definitions or helper declarations here. Internal Layer I/II lookup tables and helper routines stay private in `layer12.c`, keeping the public surface narrow.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer12.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer3.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer3.c

This is the main MPEG Layer III decoder. It parses side information, manages the bit reservoir, decodes scalefactors and Huffman data, requantizes spectral coefficients, applies joint stereo, performs reorder/alias reduction/IMDCT/overlap-add, and writes subband samples into `frame->sbsample`.

The file defines Layer III side-info structures, MPEG-1 and LSF scalefactor tables, scalefactor-band widths for MPEG-1/2/2.5 sample rates, requantization lookup data from `rq_table.dat`, powers and stereo/alias/IMDCT/window constants, and many static decode helpers. `III_sideinfo` parses granule/channel metadata and validates big-values, block type, and scfsi constraints. `III_scalefactors` and `III_scalefactors_lsf` decode scalefactors. `III_huffdecode` uses `huffman.c` tables, applies linbits/sign bits, caches requantized values, and detects overrun/part length errors.

`III_decode` orchestrates per-granule channel processing, stereo transforms, reordering, alias reduction, IMDCT, overlap, zero-subband handling, and frequency inversion. `mad_layer_III` allocates dynamic main-data and overlap buffers, validates side-info length, checks CRC, handles private bits, computes current/next main-data regions, decodes, marks ancillary bits, and preserves reservoir bytes for future frames. This is the highest-risk and most performance-sensitive file in the group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer3.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer3.h

This header exposes the single Layer III frame decoder entry point, `mad_layer_III(struct mad_stream *, struct mad_frame *)`. It includes `stream.h` and `frame.h` for the function signature.

`frame.c` uses this declaration in its decoder dispatch table, allowing generic frame decoding to call the Layer III implementation after parsing a frame header. All Layer III internals, including side-info structures, Huffman decode helpers, IMDCT helpers, and lookup tables, remain private in `layer3.c`.

The header is intentionally minimal. Its only role is to connect the shared frame pipeline to the large Layer III implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/layer3.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/mad.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/mad.h

This is an aggregated public libmad header. It combines version definitions, fixed-point arithmetic declarations/macros, bit pointer APIs, timer declarations, stream declarations, frame declarations, synthesis declarations, and decoder declarations into one include file. `main.c` includes this single header instead of including each subsystem header separately.

It identifies libmad version `0.15.1 (beta)`, defines fixed-point types and architecture-specific multiplication paths, declares `struct mad_bitptr`, `mad_timer_t`, `struct mad_stream`, `struct mad_header`, `struct mad_frame`, `struct mad_pcm`, `struct mad_synth`, and `struct mad_decoder`, plus their public functions and control macros. It also hardcodes `FPM_INTEL` and size macros near the top, making this copy configuration-specific.

Compared with the separate local headers, `mad.h` includes timer and synth public declarations not otherwise in this file list. It is the frontend-facing API surface for the Plan 9 player and mirrors upstream libmad's consolidated include model.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/mad.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/main.c

This file is the Plan 9 command frontend: a simple MP3 player derived from libmad's `minimad.c`. It reads compressed MP3 data from standard input, decodes it synchronously with libmad callbacks, and writes fixed-point PCM samples to `/bin/audio/pcmconv` for conversion/playback.

The `input` callback preserves leftover bytes from `stream->next_frame`, reads more stdin data into a static 32 KiB buffer, updates `offset`, and calls `mad_stream_buffer`. The `header` callback implements `-s` seeking by counting decoded sample positions and ignoring frames until the target time is reached. The `output` callback starts or restarts `pcmconv` when sample rate/channel count changes, formats samples as signed fixed-point interleaved little-endian-ish bytes, clips to `[-MAD_F_ONE, MAD_F_ONE)`, and writes to the converter pipe.

The `error` callback skips ID3v1 `TAG` and ID3v2 `ID3` metadata on lost sync and optionally logs decode errors with `-d`. `main` parses `-d` and `-s`, initializes callbacks, runs sync decode, waits for `pcmconv`, and exits.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/stream.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/stream.c

This file implements stream buffer state management and error string conversion. `mad_stream_init` clears buffer pointers, skip length, sync/free-rate state, frame pointers, bit pointers, ancillary data, Layer III main-data reservoir pointer/length, options, and error status. `mad_stream_finish` frees the Layer III main-data buffer if allocated.

`mad_stream_buffer` installs a caller-owned input buffer, sets `bufend`, initializes current/next frame pointers, marks sync as available, and initializes the bit pointer. `mad_stream_skip` accumulates byte skip requests used by header decode and metadata skipping. `mad_stream_sync` scans from the current bit pointer's next byte until it finds an MPEG sync pattern (`0xff` followed by high `0xe0` bits), requiring the guard-byte margin before declaring success.

`mad_stream_errorstr` maps every `enum mad_error` value to a human-readable string used by `main.c` debug logging. This file does not read from file descriptors itself; it only manages memory ranges supplied by the input callback.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/stream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/stream.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/stream.h

This header defines the stream-level input and error model. Constants include `MAD_BUFFER_GUARD` for safe bit reads past frame data and `MAD_BUFFER_MDLEN` for the Layer III main-data reservoir size. `enum mad_error` classifies buffer, allocation, sync/header, CRC, Layer I/II, and Layer III decode failures; `MAD_RECOVERABLE` treats errors with high-byte category bits as recoverable.

`struct mad_stream` tracks caller-provided input buffer bounds, deferred skip length, sync state, inferred free bitrate, current/next frame pointers, primary bit pointer, ancillary-data pointer/length, Layer III reservoir buffer/length, decode options, and current error code. Options include ignoring CRC and half-sample-rate generation, with some channel-selection options disabled.

The public functions initialize/finish a stream, set a buffer, request a skip, search for sync, and stringify errors. This structure is shared across the full decoder pipeline and is mutated by input callbacks, frame parsing, layer decoders, and error handlers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/stream.h -->