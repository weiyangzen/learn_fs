# Group Research: group_55_9front_sources_os_plan9_9front_sys_src_cmd_audio_mp3dec_synth_c_sourc_6dad9ad00cbf

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/synth.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/synth.c

This file is libmad's MPEG audio synthesis stage. It converts decoded subband samples from `struct mad_frame` into fixed-point PCM samples stored in `struct mad_synth.pcm`.

Key responsibilities:
- Initializes and resets synthesis state with `mad_synth_init()` and `mad_synth_mute()`.
- Implements a fixed-point 32-point DCT in `dct32()`.
- Maintains a 16-phase polyphase synthesis filter history in `synth->filter`.
- Applies the synthesis window coefficients from included `D.dat`.
- Emits either full-rate 32 samples per subband sample or half-rate 16 samples when `MAD_OPTION_HALFSAMPLERATE` is set.
- Updates `pcm.samplerate`, `pcm.channels`, `pcm.length`, and the rolling `phase`.

Important functions:
- `mad_synth_init(struct mad_synth *synth)`: clears filter history, sets phase to zero, and clears PCM metadata.
- `mad_synth_mute(struct mad_synth *synth)`: zeros all per-channel filterbank history entries.
- `dct32(...)`: static, optimized DCT used by both synthesis paths.
- `synth_full(...)`: full-frequency PCM synthesis.
- `synth_half(...)`: half-frequency PCM synthesis that emits only every other output sample position.
- `mad_synth_frame(...)`: public entry point for one decoded frame.

Dependencies and integration:
- Includes `global.h`, `fixed.h`, `frame.h`, and `synth.h`.
- Depends on libmad fixed-point arithmetic helpers/macros such as `mad_f_mul`, `MAD_F_ML0`, `MAD_F_MLA`, `MAD_F_MLZ`, and `MAD_F()`.
- Uses `MAD_NCHANNELS()` and `MAD_NSBSAMPLES()` from frame/header logic.
- The `D` coefficient table is compiled by including `D.dat` into a static `D[17][32]`.

Control flow:
- `mad_synth_frame()` derives channel count and subband sample count from the frame header.
- It sets PCM output metadata, chooses `synth_full` or `synth_half`, invokes the selected synthesis routine, then advances phase by the number of subband samples modulo 16.
- Each synthesis routine loops channels, then subband sample slots, performs `dct32()`, and applies synthesis-window multiply-accumulate patterns into PCM output.

Notable implementation details:
- Optional `OPT_SSO` shifts reduce fixed-point multiply cost at some accuracy cost.
- `FPM_DEFAULT` enables `OPT_SSO` automatically because the comment says avoiding SSO loses both performance and accuracy for that mode.
- `OPT_DCTO` can use `MAD_F_MLX` for a DCT speed path when available.
- The DCT is manually unrolled and uses many temporaries for speed.
- Half-rate synthesis still runs the DCT and filterbank update but writes a reduced PCM sequence.

Risks and edge cases:
- The code assumes fixed array dimensions from `struct mad_synth` and `struct mad_frame`; malformed upstream frame metadata would be dangerous if invariants are broken.
- Many arithmetic paths rely on compile-time fixed-point macro consistency; `OPT_SSO` explicitly requires `MAD_F_FRACBITS == 28`.
- The synthesis loops are performance-sensitive and hard to audit because the filterbank arithmetic is heavily unrolled.
- No direct filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/synth.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/synth.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/synth.h

This header declares libmad's PCM output and synthesis-state API.

Key declarations:
- `struct mad_pcm`: samplerate, channel count, per-channel sample count, and fixed-point PCM samples `[2][1152]`.
- `struct mad_synth`: polyphase filterbank history, current phase, and embedded `struct mad_pcm`.
- Channel selector enums for single-channel, dual-channel, and stereo output.
- Public functions `mad_synth_init()`, `mad_synth_mute()`, and `mad_synth_frame()`.
- `mad_synth_finish(synth)` is a no-op macro.

Dependencies and integration:
- Includes `fixed.h` for `mad_fixed_t`.
- Includes `frame.h` for `struct mad_frame`.
- Implemented by `synth.c`.
- Consumed by decoder front ends that need PCM output after frame decoding.

Data model:
- `samples[2][1152]` matches MPEG Layer III's maximum PCM samples per channel per frame.
- `filter[2][2][2][16][8]` stores the channel, even/odd, phase parity, synthesis slot, and vector state needed by the polyphase filterbank.

Risks and edge cases:
- The header exposes fixed-size arrays, so callers must respect `pcm.channels` and `pcm.length` rather than assuming every slot is valid.
- The finish macro means there is no dynamic resource cleanup for this object.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/synth.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/timer.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/timer.h

This header declares libmad's rational timer type and timer utility API.

Key declarations:
- `mad_timer_t`: signed whole seconds plus an unsigned fractional part.
- `mad_timer_zero`: external zero constant.
- `MAD_TIMER_RESOLUTION`: `352800000UL`, chosen to be divisible by common audio/video timing rates.
- `enum mad_units`: units for hours, minutes, seconds, metric fractions, audio sample rates, video frame rates, CD frames, and drop-frame-like rates.
- Timer operations for reset, compare, sign, negate, absolute value, set, add, multiply, count, fraction extraction, and formatting.

Dependencies and integration:
- This is a public libmad utility header. Implementations are outside this file.
- Audio rates listed include 8 kHz through 48 kHz, matching MPEG samplerates and common PCM rates.
- The API can represent playback durations, sample counts, and time strings for decoder applications.

Risks and edge cases:
- Negative enum values are used for aggregate units and drop-frame variants, so callers must pass valid enum values to the implementation.
- The fractional resolution is large but still integer-based; overflow behavior depends on implementation code not present here.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/timer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/version.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/version.c

This file defines libmad version/build metadata strings.

Key exports:
- `mad_version`: `"MPEG Audio Decoder " MAD_VERSION`.
- `mad_copyright`: copyright year plus author.
- `mad_author`: author and email.
- `mad_build`: concatenated compile-time feature string.

Dependencies and integration:
- Includes `global.h` and `version.h`.
- The strings declared here are exported by `version.h`.
- Build metadata is selected by preprocessor defines such as `DEBUG`, `NDEBUG`, `EXPERIMENTAL`, fixed-point implementation flags, assembly optimization flags, and optimization-mode flags.

Notable behavior:
- `mad_build` is a compile-time string literal assembled from enabled flags.
- `OPT_DCTO` is checked but commented as never defined here, because it is local to synthesis compilation conditions.

Risks and edge cases:
- Build metadata only reflects macros visible while compiling this translation unit; flags local to other files may not appear.
- No runtime logic or filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/version.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/version.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/version.h

This header defines libmad's static version constants and declares exported metadata strings.

Key definitions:
- Version components: major `0`, minor `15`, patch `1`, extra `" (beta)"`.
- `MAD_VERSION`: stringized combined version.
- `MAD_PUBLISHYEAR`: `"2000-2004"`.
- `MAD_AUTHOR`: `"Underbit Technologies, Inc."`.
- `MAD_EMAIL`: `"info@underbit.com"`.

Exports:
- `mad_version`
- `mad_copyright`
- `mad_author`
- `mad_build`

Integration:
- Implemented by `version.c`.
- Included by code that reports decoder version/build information.

Risks:
- Version metadata is compile-time static.
- No logic, allocation, or I/O is present.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3dec/version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/VbrTag.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/VbrTag.c

This file implements Xing-style VBR tagging for the LAME-derived MP3 encoder.

Key responsibilities:
- Maintains a compressed seek table as frames are encoded.
- Detects and parses existing Xing VBR headers.
- Reserves a dummy first MP3 frame for the eventual VBR header.
- Rewrites that reserved frame at the end with final frame count, byte count, TOC, quality scale, and LAME version string.
- Handles ID3v2-at-start offset when rewriting the VBR tag.

Important functions:
- `addVbr(VBR_seek_info_t *v, int bitrate)`: accumulates bitrate samples into a bounded bag, thinning entries when full.
- `Xing_seek_table(...)`: converts the accumulated bag into 100 TOC seek entries.
- `AddVbrFrame(lame_global_flags *gfp)`: initializes and updates `gfc->VBR_seek_table`, increments `nVbrNumFrames`.
- `CreateI4(...)` and `ExtractI4(...)`: big-endian 32-bit encoding/decoding helpers.
- `CheckVbrTag(unsigned char *buf)`: checks only for Xing marker at the MPEG-header-derived offset.
- `GetVbrTag(VBRTAGDATA *pTagData, unsigned char *buf)`: parses Xing flags, frames, bytes, TOC, VBR scale, samplerate, and header size.
- `InitVbrTag(lame_global_flags *gfp)`: reserves a dummy header frame by writing dummy bytes into the bitstream.
- `PutVbrTag(lame_global_flags *gfp, FILE *fpStream, int nVbrScale)`: seeks back and writes final VBR header bytes.

Dependencies and integration:
- Includes `machine.h`, `VbrTag.h`, `version.h`, and `bitstream.h`.
- Uses `bitrate_table`, `samplerate_table`, and `BitrateIndex()`.
- Uses `add_dummy_byte()` to reserve bytes in the encoder bitstream.
- `lame.c` calls `InitVbrTag()` during initialization, `AddVbrFrame()` after frames, and `PutVbrTag()` through `lame_mp3_tags_fid()`.

Data flow:
- During encoding, frame bitrates are recorded in `gfc->VBR_seek_table`.
- At finalization, the output file is inspected for an optional ID3v2 tag, the first real frame's MPEG header fields are used as a template, and a Xing frame is written at the correct offset.
- The TOC entries approximate byte positions as `toc[i] / 256 * total_bytes`.

Risks and edge cases:
- `AddVbrFrame()` allocates a 400-entry seek bag and reports failure but otherwise leaves VBR tagging degraded.
- `PutVbrTag()` requires a seekable `FILE *`; it returns `-1` when the file is empty or no VBR frames were recorded.
- Several `fread()` and `fseek()` calls are not strongly checked.
- `assert()` checks enforce header frame sizing; disabled assertions could hide bad sizing assumptions.
- `VbrTag.h` declares `SeekPoint()`, but this file does not define it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/VbrTag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/VbrTag.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/VbrTag.h

This header declares the Xing VBR tag interface and parsed-tag structure.

Key definitions:
- Xing flag bits: `FRAMES_FLAG`, `BYTES_FLAG`, `TOC_FLAG`, and `VBR_SCALE_FLAG`.
- `NUMTOCENTRIES`: 100.
- `FRAMES_AND_BYTES`: convenience mask.
- `VBRTAGDATA`: parsed VBR header fields including MPEG id, samplerate, flags, frame count, byte count, VBR scale, TOC, and header size.

Exported functions:
- `CheckVbrTag()`
- `GetVbrTag()`
- `SeekPoint()`
- `InitVbrTag()`
- `PutVbrTag()`
- `AddVbrFrame()`

Dependencies and integration:
- Includes `lame.h`.
- Implemented primarily by `VbrTag.c`.
- Used by encoder initialization/finalization and possibly MP3 input parsing.

Risks and edge cases:
- The comment says `toc` may be `NULL`, but the struct contains an inline array, not a pointer; that comment appears stale.
- `SeekPoint()` is declared here but not implemented in the paired file read in this group.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/VbrTag.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/bitstream.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/bitstream.c

This file implements MP3 bitstream assembly for the LAME-derived encoder.

Key responsibilities:
- Writes individual bits and bytes into the encoder output buffer.
- Delays and inserts MPEG frame headers/side information at scheduled bit positions.
- Encodes MPEG Layer III side information with optional CRC.
- Huffman-encodes quantized spectral coefficients and count1 regions.
- Writes scalefactors for MPEG-1 and MPEG-2/LSF layouts.
- Drains reservoir/ancillary bits and flushes the stream.
- Copies completed bytes to caller-owned output buffers.

Important functions:
- `putheader_bits()`: copies a queued frame header into the bitstream.
- `putbits2()`: writes bits while honoring pending header insertion timing.
- `putbits_noheaders()`: writes bits while ignoring header insertion, used for dummy bytes/tags.
- `drain_into_ancillary()`: writes stuffing bits, beginning with `LAME` and version text where space allows.
- `writeheader()` and `CRC_writeheader()`: write header fields and update CRC.
- `encodeSideInfo2()`: serializes MPEG header and side information for MPEG-1 or MPEG-2.
- `HuffmanCode()`, `Huffmancodebits()`, `ShortHuffmancodebits()`, `LongHuffmancodebits()`: emit Huffman-coded spectral pairs.
- `writeMainData()`: writes scalefactors and Huffman data for all granules/channels.
- `format_bitstream()`: combines ancillary pre-drain, side info, main data, post-drain, reservoir accounting, and overflow protection.
- `flush_bitstream()`: pads enough bits to write all pending headers and complete the last frame.
- `add_dummy_byte()`: writes a raw byte and shifts all queued header timings.
- `copy_buffer()`: copies buffered bytes out and resets byte position.
- `init_bit_stream_w()`: allocates and initializes `gfc->bs`.

Dependencies and integration:
- Includes `tables.h`, `bitstream.h`, `quantize.h`, `quantize_pvt.h`, and `version.h`.
- Depends on `III_side_info_t`, `III_scalefac_t`, Huffman table `ht`, bitrate/frame-size helpers, and LAME internal flags.
- Called from `encoder.c` after quantization and from `lame.c` during initialization/flushing.
- `id3tag.c` and `VbrTag.c` use `add_dummy_byte()` to inject metadata bytes into the bitstream.

Notable state:
- `Bit_stream_struc` fields: buffer pointer, byte index, bit index, and total bit count.
- Header ring buffer fields in `gfc->header[]`, controlled by `h_ptr` and `w_ptr`.
- `l3_side->main_data_begin` and `gfc->ResvSize` must remain consistent.

Risks and edge cases:
- Many assertions verify bitcount invariants; in non-assert builds mismatches may only log through `ERRORF`.
- `init_bit_stream_w()` does not check `malloc()` failure.
- `copy_buffer()` returns `-1` if caller buffer is too small, but callers must propagate that correctly.
- The file mutates `table_select` values of 14 to 16 before writing side info.
- `bs->totbit` is reset after exceeding one billion bits to avoid overflow, adjusting queued header timings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/bitstream.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/bitstream.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/bitstream.h

This header declares the MP3 bitstream output interface.

Exports:
- `format_bitstream()`: encode one frame's side info and main data into the output bitstream.
- `flush_bitstream()`: pad and flush pending MP3 frame data.
- `add_dummy_byte()`: append a raw byte while adjusting queued header timing.
- `copy_buffer()`: copy completed bytes to a caller buffer and reset bitstream byte position.
- `init_bit_stream_w()`: allocate and initialize write-side bitstream state.
- `main_CRC_init()`: declared but implemented as an empty function in `bitstream.c`.

Dependencies:
- Includes `util.h`, which provides LAME internal structures and `III_scalefac_t`.

Integration:
- Used by `encoder.c`, `lame.c`, `VbrTag.c`, and `id3tag.c`.
- This is a central boundary between frame encoding and byte-oriented output.

Risks:
- The API exposes raw buffer sizes and requires callers to handle negative return codes from `copy_buffer()`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/bitstream.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/brhist.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/brhist.h

This header declares bitrate histogram display support and console I/O state.

Exports:
- `brhist_init()`
- `brhist_disp()`
- `brhist_disp_total()`
- `brhist_jump_back()`
- Global `Console_IO`

Data structures:
- `Console_IO_t` stores reporting streams, optional Windows console handle, display dimensions, terminal-control strings, and a console buffer.

Dependencies and integration:
- Includes `lame.h`.
- Includes `<windows.h>` on Windows non-Cygwin builds.
- Function implementations are outside this group.
- Used by command-line reporting/progress UI rather than core encoding.

Risks:
- Exposes a mutable global `Console_IO`.
- Terminal-control behavior is platform-dependent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/brhist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/encoder.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/encoder.c

This file orchestrates encoding of one MP3 frame.

Key responsibilities:
- Initializes per-frame encoder state on first use.
- Applies padding policy.
- Runs psychoacoustic analysis or fallback block defaults.
- Adjusts ATH for low-volume content.
- Runs MDCT/polyphase analysis and short-block reordering.
- Chooses LR vs MS stereo coding.
- Selects quantization loop according to CBR/VBR/ABR mode.
- Writes encoded frame data to the bitstream.
- Updates VBR frame accounting and analysis/statistics output.

Important functions:
- `adjust_ATH(lame_global_flags *gfp, FLOAT8 tot_ener[2][4])`: dynamically lowers/raises ATH adjustment based on frame energy and VBR mode.
- `lame_encode_mp3_frame(...)`: main one-frame encoding function.

Dependencies and integration:
- Includes `lame.h`, `util.h`, `newmdct.h`, `psymodel.h`, `quantize.h`, `quantize_pvt.h`, `bitstream.h`, and `VbrTag.h`.
- Calls psychoacoustic functions `L3psycho_anal()` or `L3psycho_anal_ns()`.
- Calls `mdct_sub48()` and `freorder()`.
- Calls quantization functions `iteration_loop()`, `VBR_quantize()`, `VBR_iteration_loop()`, or `ABR_iteration_loop()`.
- Calls `format_bitstream()` and `copy_buffer()` through bitstream code.
- Calls `AddVbrFrame()` when VBR tagging is enabled.

Control flow:
- On first frame, initializes padding state, primes MDCT/filterbank with zero-prefixed samples, calls `iteration_init()`, and configures ATH decay.
- For each frame, computes padding, obtains masking/energy data, sets block types and window-switch flags, runs MDCT, optionally computes MS stereo, writes analyzer data, quantizes, formats the bitstream, copies output, updates stats, and returns byte count.

Notable behavior:
- `force_ms` overrides automatic MS decisions.
- Automatic MS uses both MS energy ratios and perceptual entropy comparison.
- nspsytune mode applies a 19-tap FIR smoothing/normalization over perceptual entropy before quantization in CBR/ABR.
- The function uses stack arrays for MDCT coefficients, quantized coefficients, masking ratios, and scalefactors except on old Macintosh builds.

Risks and edge cases:
- Many invariants are asserted: buffer size, FFT offset, MDCT/filterbank sample availability, and bit accounting.
- The first-frame initialization mutates persistent `gfc` state and assumes valid `mf_size`.
- Some math paths use integer sums from floating-point perceptual entropy values.
- `mp3count` can be negative if downstream buffer copying fails.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/encoder.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/encoder.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/encoder.h

This header defines core encoder constants and declares the one-frame MP3 encode function.

Key constants:
- Delay constants: `ENCDELAY`, `MDCTDELAY`, `FFTOFFSET`, `DECDELAY`.
- MPEG analysis dimensions: `SBLIMIT`, `CBANDS`, `SBPSY_l`, `SBPSY_s`, `SBMAX_l`, `SBMAX_s`.
- FFT dimensions: `BLKSIZE`, `HBLKSIZE`, `BLKSIZE_s`, `HBLKSIZE_s`.
- Block types: `NORM_TYPE`, `START_TYPE`, `SHORT_TYPE`, `STOP_TYPE`.
- Stereo mode extension constants: `MPG_MD_LR_LR`, `MPG_MD_LR_I`, `MPG_MD_MS_LR`, `MPG_MD_MS_I`.

Export:
- `lame_encode_mp3_frame(...)`

Dependencies and integration:
- Includes `machine.h` and `lame.h`.
- Used throughout encoder, psychoacoustic, FFT, MDCT, and analysis code.
- Delay constants are critical for frame buffering in `lame.c` and `encoder.c`.

Risks:
- Changing delay or FFT constants affects buffer sizing and alignment across many modules.
- Comments document historical uncertainty around exact encoder/decoder delay; code relies on the chosen constants.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/encoder.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/fft.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/fft.c

This file implements FFT/FHT routines used by the psychoacoustic model.

Key responsibilities:
- Provides an in-place Fast Hartley Transform implementation unless `USE_FFT3DN` redirects to `fht_3DN`.
- Performs windowed long and short transforms over encoder PCM buffers.
- Initializes long and short analysis windows.

Important functions:
- `fht(FLOAT *fz, int n)`: static Hartley transform using precomputed trig values.
- `fft_short(lame_internal_flags *gfc, FLOAT x_real[3][BLKSIZE_s], int chn, const sample_t *buffer[2])`: computes three short-window transforms.
- `fft_long(lame_internal_flags *gfc, FLOAT x[BLKSIZE], int chn, const sample_t *buffer[2])`: computes one long-window transform.
- `init_fft(lame_internal_flags *gfc)`: fills Blackman long window and Hann-style short window.

Dependencies and integration:
- Includes `util.h` and `fft.h`.
- Uses window arrays stored in `lame_internal_flags`.
- Called by psychoacoustic analysis code outside this group.

Notable implementation details:
- Uses a 256-entry bit-reversal table.
- Macro families (`ml*`, `ms*`) combine window lookup and PCM buffer access for speed.
- Long window uses Blackman coefficients.
- Short window stores only half-window coefficients.

Risks and edge cases:
- The file's header comments mention patent/licensing history around FHT/trig algorithms.
- Assumes buffer offsets supplied by caller are valid for 1024- and 256-point windows.
- Heavy macro arithmetic makes indexing correctness important and non-obvious.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/fft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/fft.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/fft.h

This header declares FFT analysis functions for the encoder.

Exports:
- `fft_long()`
- `fft_short()`
- `init_fft()`

Dependencies:
- Includes `encoder.h` for `BLKSIZE`, `BLKSIZE_s`, `sample_t`, `FLOAT`, and LAME structures.

Integration:
- Used by psychoacoustic model code to transform time-domain samples into frequency-domain energy data.
- `init_fft()` must be called during encoder initialization before analysis windows are used.

Risks:
- Function prototypes depend on fixed compile-time block sizes.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/fft.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/get_audio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/get_audio.c

This file implements input audio opening, decoding, PCM reading, simple decoding-to-WAV, and fallback WAV/AIFF/raw parsers for the LAME-derived command.

Key responsibilities:
- Opens input and output files.
- Reads PCM, MP3, or Ogg samples into encoder frame buffers.
- Converts interleaved PCM into left/right channel arrays.
- Handles byte swapping and 8-bit-to-16-bit sample expansion.
- Writes simple WAV headers for decode mode.
- Supports libsndfile-based input when `LIBSNDFILE` is enabled.
- Provides fallback WAV/AIFF/raw header parsing when libsndfile is unavailable.
- Provides mpglib-based MP3 header probing and frame decoding when `HAVE_MPGLIB` is enabled.

Important globals:
- `count_samples_carefully`
- `pcmbitwidth`
- `mp3input_data`
- `num_samples_read`
- `musicin`

Important functions:
- `fskip()`: forward skip helper that falls back to read/discard for pipes.
- `init_outfile()`: opens stdout or binary output file.
- `init_infile()` / `close_infile()`: manage global input file.
- `SwapBytesInWords()`: byte-swaps 16-bit samples, optimized for 32- or 64-bit unsigned long.
- `get_audio()`: reads one encoder frame's worth of samples into `[2][1152]`.
- `read_samples_ogg()` and `read_samples_mp3()`: decode compressed input through optional decoders.
- `WriteWaveHeader()`: writes a PCM WAV header.
- `lame_decoder()`: simple decode loop from compressed/raw input to WAV PCM output.
- `OpenSndFile()` / `CloseSndFile()`: format-specific open/close.
- Fallback-only `parse_wave_header()`, `parse_aiff_header()`, `parse_file_header()`.
- mpglib-only `lame_decode_initfile()` and `lame_decode_fromfile()`.

Dependencies and integration:
- Includes `lame.h`, `main.h`, `get_audio.h`, `portableio.h`, `timestatus.h`, and `lametime.h`.
- Optional dependencies: libsndfile, mpglib, Vorbis.
- Uses global command-line state such as `input_format`, `swapbytes`, and `silent`.
- The encoder front end calls `init_infile()`, repeatedly calls `get_audio()`, then `close_infile()`.

Control flow:
- `get_audio()` determines how many samples to read, optionally clamps to known sample count, dispatches by `input_format`, and returns samples per channel.
- PCM default path reads interleaved samples and deinterleaves mono/stereo into the two-channel output buffer.
- Compressed paths call decoder wrappers and verify channel count and samplerate have not changed.
- Decode mode writes WAV data while skipping known decoder/encoder delay for MPEG formats.

Fallback parser behavior:
- WAV parsing looks for `RIFF`, `WAVE`, `fmt `, and `data` chunks, supports PCM only, and sets channels, samplerate, bit width, and sample count.
- AIFF parsing looks for `FORM`, `AIFF`, `COMM`, and `SSND`, validates PCM-like constraints, and sets corresponding LAME fields.
- Raw fallback rewinds to byte zero if header detection fails.

Risks and edge cases:
- Uses process-global input state, so it is not reentrant.
- Many fatal input errors call `exit()`, which is command-line friendly but not library friendly.
- Some format strings use `%ud` for channel values, which is suspicious C formatting.
- mpglib decode reads fixed 100-byte chunks and treats short reads as errors/end.
- `fskip()` prints directly to stderr on unsupported seek cases.
- No direct filesystem implementation logic; file I/O is ordinary audio command input/output.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/get_audio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/get_audio.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/get_audio.h

This header declares audio input helpers and fallback audio container structures.

Key definitions:
- `sound_file_format`: enum for unknown, raw, WAVE, AIFF, MPEG Layer I/II/III, and Ogg.
- `blockAlign`: AIFF sound-data offset/block-size pair.
- `IFF_AIFF`: fallback AIFF metadata structure.

Exports:
- `init_outfile()`
- `init_infile()`
- `close_infile()`
- `get_audio()`
- `lame_decoder()`
- `SwapBytesInWords()`

Conditional declarations:
- If `LIBSNDFILE` is enabled, includes `sndfile.h`.
- Otherwise includes `portableio.h` and declares older AIFF/WAV helper prototypes.

Integration:
- Used by command-line encode/decode front ends.
- Implemented by `get_audio.c`.

Risks:
- Header exposes legacy fallback prototypes that are not all implemented in `get_audio.c`, suggesting compatibility remnants.
- API relies on global state configured outside the header.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/get_audio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/id3tag.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/id3tag.c

This file implements ID3v1 and simple ID3v2 tag writing for the LAME-derived encoder.

Key responsibilities:
- Maintains standard ID3 genre names and an alphabetical genre listing map.
- Stores user-provided title, artist, album, year, comment, track, and genre in `gfc->tag_spec`.
- Controls whether ID3v1, ID3v2, padding, or spacing is used.
- Writes ID3v2.3 text/comment frames into the bitstream.
- Writes ID3v1/1.1 fixed-size trailing tags into the bitstream.

Important functions:
- `id3tag_genre_list(...)`: iterates genres in alphabetical order through a callback.
- `id3tag_init(...)`: clears tag state and sets unknown genre.
- `id3tag_add_v2()`, `id3tag_v1_only()`, `id3tag_v2_only()`, `id3tag_space_v1()`, `id3tag_pad_v2()`: set policy flags.
- `id3tag_set_title()`, `id3tag_set_artist()`, `id3tag_set_album()`, `id3tag_set_year()`, `id3tag_set_comment()`, `id3tag_set_track()`, `id3tag_set_genre()`: populate metadata.
- `id3tag_write_v2()`: builds and writes an ID3v2.3 tag.
- `id3tag_write_v1()`: builds and writes a 128-byte ID3v1 tag.

Dependencies and integration:
- Includes `lame.h`, `id3tag.h`, `util.h`, and `bitstream.h`.
- Uses `add_dummy_byte()` to insert tag bytes into the encoder's bitstream.
- `lame.c` writes ID3v2 before the Xing VBR header and ID3v1 during flush.

ID3v2 behavior:
- Writes `ID3` header version 2.3.0.
- Uses ISO-8859-1 text encoding byte `0`.
- Supports frames `TIT2`, `TPE1`, `TALB`, `TYER`, `COMM`, `TRCK`, and `TCON`.
- Adds optional 128-byte padding.
- Does not perform unsynchronization.

ID3v1 behavior:
- Writes `TAG`, 30-byte title/artist/album, 4-byte year, comment, optional track byte, and genre byte.
- Uses zero padding or space padding depending on flag.
- Uses ID3v1.1 track convention when a track is set.

Risks and edge cases:
- Stores string pointers, not copies, so caller-provided strings must remain valid until tags are written.
- `local_strcasecmp()` calls `tolower()` on `char` values without an explicit unsigned cast.
- ID3v2 tag size is encoded as synchsafe 28-bit, but the code does not guard against extremely large total tag sizes.
- Genre name list includes historical Winamp spellings, including offensive legacy genre names.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/id3tag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/id3tag.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/id3tag.h

This header declares private ID3 tag state and write functions.

Key structure:
- `struct id3tag_spec`: flags plus pointers/values for title, artist, album, year, comment, track, and genre.

Exports:
- `id3tag_write_v2(lame_global_flags *gfp)`
- `id3tag_write_v1(lame_global_flags *gfp)`

Dependencies:
- Includes `lame.h`.

Integration:
- `lame_internal_flags` embeds or references this tag specification.
- Implemented by `id3tag.c`.
- Tag setter functions are not declared here, likely exposed from another public LAME header.

Risks:
- The structure is labeled private but visible in the header.
- String fields are non-owning `const char *` pointers.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/id3tag.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/l3side.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/l3side.h

This header defines MPEG Layer III side-information and scalefactor data structures.

Key typedefs:
- `D576`, `I576`: 576-sample coefficient arrays.
- `D192_3`, `I192_3`: short-block grouped arrays.
- `scalefac_struct`: long and short scalefactor band boundaries.
- `III_psy_xmin`: long/short psychoacoustic threshold or energy arrays.
- `III_psy_ratio`: threshold and energy pair.
- `gr_info`: per-granule/channel side-info fields.
- `III_side_info_t`: frame-level Layer III side info.
- `III_scalefac_t`: encoded long/short scalefactors.

Dependencies and integration:
- Includes `encoder.h` and `machine.h`.
- Used by psychoacoustic, quantization, and bitstream code.
- `bitstream.c` serializes `III_side_info_t` and `III_scalefac_t`.
- `encoder.c` mutates block type, window flags, and stereo mode decisions.

Notable fields:
- `gr_info` contains MPEG fields such as `part2_3_length`, `big_values`, `global_gain`, `scalefac_compress`, `block_type`, region counts, Huffman table selectors, and LSF partition data.
- `III_side_info_t` includes reservoir fields `main_data_begin`, `resvDrain_pre`, and `resvDrain_post`.

Risks:
- Structures are tightly coupled to MPEG Layer III bitstream layout.
- Integer dimensions assume maximum two granules and two channels.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/l3side.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame-analysis.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame-analysis.h

This header defines data captured for LAME's MP3 frame analyzer/plotting support.

Key constants:
- `READ_AHEAD`
- `MAXMPGLAG`
- `NUMBACK`
- `NUMPINFO`

Main structure:
- `plotting_data`: large per-frame analysis snapshot containing PCM data, MDCT data, decoded comparison data, MS ratios, energy, thresholds, scalefactors, quantization metadata, noise metrics, block types, frame header properties, bit counts, and reservoir data.

Export:
- `extern plotting_data *pinfo`

Dependencies:
- Includes `encoder.h` for block sizes and constants.

Integration:
- `encoder.c` writes analysis data into `gfc->pinfo`.
- Intended for GTK plotting/frame-analyzer tooling rather than normal encoding output.

Risks:
- Large structure with many fixed-size arrays.
- Global `pinfo` suggests non-reentrant analyzer state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame-analysis.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame.c

This file implements the central LAME encoder initialization, public encode-buffer API, flush/finalization, tag rewrite hook, and bitrate/statistics accessors.

Key responsibilities:
- Computes derived encoder parameters from user-facing `lame_global_flags`.
- Selects bitrate, samplerate, MPEG version, frame size, compression ratio, channel mode, and filters.
- Initializes internal feature flags, CPU feature flags, bitstream state, scalefactor bands, side-info length, ATH/nspsytune behavior, and VBR limits.
- Provides public encode APIs for sample_t, short, float, long, and interleaved short input.
- Handles buffering, resampling, optional stereo-to-mono mixing, frame feeding, and output byte accumulation.
- Flushes encoder delay/padding, writes trailing ID3v1 tags, and closes/free internal state.
- Rewrites Xing VBR tag into a seekable file after encoding.
- Provides bitrate and stereo-mode histograms.

Important initialization functions:
- `lame_init_params_ppflt_lowpass()`: computes polyphase lowpass band amplitudes.
- `lame_init_params_ppflt()`: computes lowpass/highpass transition bands and amplitudes.
- `optimum_bandwidth()`: estimates default lowpass/highpass based on bitrate, samplerate, and channel mode.
- `optimum_samplefreq()`: suggests output samplerate from lowpass/input constraints.
- `lame_init_qval()`: maps quality level to psy model, quantization, noise shaping, and Huffman-search flags.
- `lame_init_params()`: full derived-parameter initialization.
- `lame_init()` and `lame_init_old()`: allocate and default global/internal flags.

Important encode/finalize functions:
- `lame_print_config()`: reports version, CPU features, resampling, filters, and free-format warnings.
- `lame_encode_frame()`: dispatches to MP3 or optional Ogg frame encoder.
- `lame_encode_buffer_sample_t()`: main buffered encode path with resampling/fill-buffer integration.
- `lame_encode_buffer()`, `lame_encode_buffer_float()`, `lame_encode_buffer_long()`: type-converting wrappers.
- `lame_encode_buffer_interleaved()`: deinterleaves stereo short samples and encodes.
- `lame_encode()`: legacy 2x1152-frame API.
- `lame_encode_flush()`: feeds zero padding until internal samples are encoded, then flushes bitstream and writes ID3v1.
- `lame_close()`: frees internal state and possibly the `lame_global_flags`.
- `lame_encode_finish()`: flushes then closes.
- `lame_mp3_tags_fid()`: rewrites final Xing VBR tag through `PutVbrTag()`.

Statistics functions:
- `lame_bitrate_hist()`
- `lame_bitrate_kbps()`
- `lame_stereo_mode_hist()`
- `lame_bitrate_stereo_mode_hist()`

Dependencies and integration:
- Includes `lame-analysis.h`, `lame.h`, `util.h`, `bitstream.h`, `version.h`, `tables.h`, `quantize_pvt.h`, and `VbrTag.h`.
- Calls CPU feature probes, `init_bit_stream_w()`, `id3tag_write_v2()`, `InitVbrTag()`, `fill_buffer()`, `lame_encode_mp3_frame()`, `flush_bitstream()`, `id3tag_write_v1()`, `copy_buffer()`, `freegfc()`, and VBR tag rewriting.
- Optional Ogg/Vorbis and architecture-specific code is gated by preprocessor flags.

Initialization control flow:
- Establishes internal pointer and report callbacks.
- Detects CPU features and allocates ATH state.
- Determines input/output channel counts and disables MS for mono.
- Resolves bitrate/compression ratio/output samplerate.
- Sets MP3 frame size from MPEG version granule count.
- Estimates VBR compression ratio or CBR compression ratio.
- Chooses default stereo mode if not set.
- Computes default/user-driven lowpass and highpass filters.
- Maps samplerate/bitrate to MPEG table indexes.
- Disables VBR tags for CBR, Ogg, analysis, or pinfo modes.
- Initializes bitstream, scalefactor bands, side-info length, ID3v2, optional initial VBR header, MPEG flags, frame estimate, nspsytune, VBR/ATH behavior, and qval flags.

Encoding data flow:
- `lame_encode_buffer_sample_t()` fills internal `mfbuf` from caller input via `fill_buffer()`.
- Once enough samples are buffered for FFT and MDCT/filterbank requirements, it calls `lame_encode_frame()`.
- After a frame is encoded, it shifts old samples out of `mfbuf` by `gfp->framesize`.
- Wrapper APIs allocate temporary `sample_t` buffers and delegate to the sample_t path.

Risks and edge cases:
- Several allocation failure paths in buffer wrappers return `-2` without freeing the other buffer if only one allocation succeeded.
- `init_bit_stream_w()` allocation failure is not handled here.
- API is stateful and guarded by `gfc->Class_ID`; misuse before `lame_init_params()` returns `-3`.
- Many settings are silently adjusted, such as VBR disabled at high fixed bitrate, quality clamping, mode defaults, and samplerate decisions.
- `lame_encode_flush()` mutates `mf_samples_to_encode` while also calling encode paths that mutate it.
- VBR tag rewriting requires a seekable `FILE *`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame.c -->