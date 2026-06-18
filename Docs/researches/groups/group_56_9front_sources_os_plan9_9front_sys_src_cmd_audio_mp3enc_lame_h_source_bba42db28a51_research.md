# Group Research: 9front mp3enc LAME frontend headers and support sources

Scope verified against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame.h

## Scope
Public LAME API header for the bundled `mp3enc` encoder/decoder interface. It defines user-visible configuration, encoder lifecycle calls, encode/decode entry points, ID3 tag functions, and exported MPEG lookup tables.

## APIs and Data
Defines `vbr_mode`, `MPEG_mode`, `lame_global_flags`, and alias `lame_t`. `lame_global_flags` includes input description, output controls, VBR settings, filters, psychoacoustic tuning, reporting callbacks, visible internal counters, and VBR tag bookkeeping. API coverage includes `lame_init`, parameter setters/getters, `lame_init_params`, version getters, `lame_encode_buffer*`, `lame_encode_flush`, `lame_close`, obsolete `lame_encode_finish`, mpglib-backed decode calls, ID3 tag setters, and `bitrate_table`/`samplerate_table`.

## Dependencies
Requires `stdio.h` and `stdarg.h`; C++ callers get `extern "C"`. Optional declarations are gated by `KLEMM_44`.

## Risks and Notes
The public struct exposes many internal fields and comments warn callers not to modify some of them. Several APIs are obsolete or conditionally available. Decode APIs depend on mpglib being compiled in. `LAME_MAXMP3BUFFER` is marked obsolete but still used by the frontend.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lame.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lameerror.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lameerror.h

## Scope
Small shared enum of LAME/frontend error codes.

## APIs and Data
Defines `lame_errorcodes_t` with success aliases `LAME_OKAY`/`LAME_NOERROR`, generic `-1`, LAME-specific negative codes beginning at `-10`, and frontend I/O/file-size codes beginning at `-80`.

## Dependencies
No includes and no include guard.

## Risks and Notes
The comment says values begin at `-10` to avoid older `-1` through `-4` return conventions, but `LAME_GENERICERROR` still uses `-1`. Lack of guard can be harmless for enum-only inclusion but is fragile.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lameerror.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lametime.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lametime.c

## Scope
Time and file utility implementation for the LAME frontend.

## APIs and Behavior
`GetCPUTime()` returns process CPU time via `clock() / CLOCKS_PER_SEC`. `GetRealTime()` returns wall time from `gettimeofday()` and asserts on failure. `lame_set_stream_binary_mode()` is a no-op returning 0, matching Unix/Plan 9 stream semantics. `lame_get_file_size()` returns `stat().st_size` or `-1`.

## Dependencies
Uses standard/POSIX headers: `time.h`, `sys/time.h`, `sys/types.h`, `sys/stat.h`, plus `lametime.h`.

## Risks and Notes
`GetRealTime()` uses `assert(0)` for an OS error path. Binary mode is intentionally ignored here, unlike DOS/Windows ports.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lametime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lametime.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lametime.h

## Scope
Header for time/file utility helpers.

## APIs
Declares `GetCPUTime`, `GetRealTime`, `lame_set_stream_binary_mode`, and `lame_get_file_size`.

## Dependencies
Includes `sys/types.h` and `lame.h`, mainly for `FILE` and `off_t`.

## Risks and Notes
Simple guarded header; the binary-mode function is platform-dependent in implementation.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/lametime.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/machine.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/machine.h

## Scope
Machine/compiler compatibility layer for LAME internals.

## APIs and Data
Provides fallback C library declarations/macros, math includes, `POW20`/`IPOW20` lookup macros, inline portability definitions, `FLOAT`, `FLOAT8`, `sample_t`, and `stereo_t`.

## Dependencies
Includes `stdio.h`, `memory.h`, `math.h`, `ctype.h`, optional `errno.h`/`fcntl.h`, and system stat/type headers. Handles several legacy compiler/platform branches.

## Risks and Notes
`POW20`/`IPOW20` assume global tables exist elsewhere. Uses old portability branches and C++-style comments in places. `FLOAT8=float` is explicitly warned as breaking resampling and VBR code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/machine.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/main.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/main.c

## Scope
Command-line frontend for encoding audio to MP3, with optional decode mode.

## Entry Points
`parse_args_from_string()` tokenizes `LAMEOPT` by spaces and passes synthetic argv to `parse_args()`. `main()` initializes LAME, parses environment and command-line options, opens input/output, initializes encoder parameters, loops through input audio, encodes with `lame_encode_buffer`, writes MP3 bytes, flushes, writes VBR tags, closes LAME/output, and closes input.

## Control Flow
Input and output paths are initialized as `"-"`, so this 9front frontend is stream-oriented by default. Decode mode calls `lame_decoder()` with either user-specified MP3 delay or encoder delay. Encode mode reads 1152-sample channel buffers via `get_audio()`, optionally updates status/histogram displays, encodes, writes output, then flushes and finishes status.

## Dependencies
Uses `lame.h`, `brhist.h`, `parse.h`, `main.h`, `get_audio.h`, and `timestatus.h`.

## Risks and Notes
`parse_args_from_string()` is explicitly “quick & dirty”: it splits only on spaces, has a fixed 128-argument array, and does not handle quoting. Several status `fprintf` branches are disabled with `if (0)`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/main.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/main.h

## Scope
Shared frontend globals and small utility macros for `main.c` and `parse.c`.

## APIs and Data
Includes `get_audio.h`, defines `MAX_NAME_SIZE`, declares globals `input_format`, `swapbytes`, `silent`, `brhist`, `mp3_delay`, `mp3_delay_set`, and `update_interval`. Defines `Min`, `Max`, and `MAX_U_32_NUM`.

## Dependencies
Depends on `sound_file_format` from `get_audio.h`.

## Risks and Notes
The header comment calls the global sharing “ugly”; `parse.c` owns the definitions. There is no include guard.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/main.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/memory.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/memory.h

## Scope
Minimal compatibility shim.

## Content
Includes `<string.h>` and `<stdlib.h>`.

## Risks and Notes
No include guard. Exists to satisfy older code expecting `memory.h`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/memory.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/mpglib_interface.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/mpglib_interface.c

## Scope
Conditional wrapper exposing LAME decode APIs over mpglib/mpg123 internals.

## APIs and Behavior
Compiled only under `HAVE_MPGLIB`. Maintains global `MPSTR mp` decoder state. `lame_decode_init()` calls `InitMP3`. `lame_decode1_headers()` decodes at most one frame, fills `mp3data_struct` from parsed headers, computes bitrate from frame size or bitrate table, handles Xing frame count, and deinterleaves mpglib output into left/right PCM arrays. `lame_decode1`, `lame_decode_headers`, and `lame_decode` layer simpler interfaces over that core routine.

## Dependencies
Requires mpglib `interface.h`, `lame.h`, mpg123 tables/state such as `freqs` and `tabsel_123`.

## Risks and Notes
Uses static output buffer `char out[8192]` and global decoder state, so the interface is not reentrant. Several impossible states use `assert(0)`. Header fields are zeroed only partially; callers should not assume untouched fields are reset unless set by this path.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/mpglib_interface.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/newmdct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/newmdct.c

## Scope
Layer III subband analysis, MDCT transform, filtering, and alias-reduction implementation.

## Data and Algorithms
Defines analysis window constants, MDCT windows for normal/start/short/stop block types, short-block trig tables, alias reduction constants, and subband output ordering. `window_subband()` applies the overlapping analysis window and fast cosine-style reduction. `mdct_short()` transforms three short windows. `mdct_long()` transforms long blocks. `mdct_sub48()` drives 48 subband samples per granule/channel, applies highpass/lowpass transition-band gains, chooses block type including mixed-block handling, zeros filtered bands, performs MDCT, and applies alias-reduction butterflies for non-short blocks.

## Dependencies
Includes `util.h`, `l3side.h`, and `newmdct.h`; uses LAME internal fields such as `l3_side`, `sb_sample`, `channels_out`, `mode_gr`, filter bands, and amplitude tables.

## Risks and Notes
Performance-critical, table-heavy DSP code with pointer arithmetic and negative indexes relative to working buffers. Correctness depends on upstream buffer layout and constants such as `SBLIMIT`, `SHORT_TYPE`, and block-type definitions.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/newmdct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/newmdct.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/newmdct.h

## Scope
Header for the MDCT/subband transform implementation.

## API
Declares `mdct_sub48(lame_internal_flags *gfc, const sample_t *w0, const sample_t *w1, FLOAT8 mdct_freq[2][2][576])`.

## Dependencies
Requires prior declarations of `lame_internal_flags`, `sample_t`, and `FLOAT8`, typically through internal LAME headers.

## Risks and Notes
Guarded header, but not self-contained.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/newmdct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/parse.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/parse.c

## Scope
Command-line parsing, usage/help text, presets, file-type detection, and frontend global option state.

## APIs and Behavior
Defines globals declared in `main.h`. Help functions print version, license, usage, short help, long help, bitrate tables, and preset information. Presets map names like `phone`, `fm`, `hifi`, `cd`, and `studio` to resampling, filters, block behavior, mode, CBR, and VBR ranges. `parse_args()` handles GNU-style long options and compact short options, mutating `lame_global_flags`, ID3 state, input format, silence/status settings, byte swapping, decoder delay, and frontend VBR histogram behavior.

## Control Flow
Long options include input type, Ogg/Vorbis, presets, decode, ATH/noise-shaping controls, ID3 fields, filters, ABR/VBR, nspsytune controls, verbosity, version/license/help, and display interval. Short options cover mode, VBR quality, sample rate, bitrate min/max, raw input, byte swap, CRC, mono conversion, filters, experimental toggles, emphasis, copyright/original bits, and help. After parsing, this 9front version forces `silent = 1` and disables VBR tag writing, reflecting stdin/stdout behavior.

## Dependencies
Uses `lame.h`, `brhist.h`, `parse.h`, `main.h`, and `get_audio.h`; calls many LAME setters and ID3 APIs.

## Risks and Notes
Parsing mostly uses `atoi`/`atof` with limited validation. `local_strcasecmp()` passes plain `char` to `tolower`, which can be undefined for negative signed chars. `presets_setup()` accepts prefix matches, so ambiguous prefixes can select the first matching preset. `parse_args()` resets globals on every call, relevant because `main.c` calls it once for `LAMEOPT` and once for argv.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/parse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/parse.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/parse.h

## Scope
Prototypes for parser/help functions.

## APIs
Declares `print_license`, `usage`, `short_help`, `long_help`, and `display_bitrates`.

## Dependencies
Requires `lame_global_flags` and `FILE` declarations from included context.

## Risks and Notes
No include guard and not self-contained.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/parse.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/pcm.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/pcm.c

## Scope
Experimental generalized PCM input, demultiplexing, scalar, and resampling implementation, compiled only under `KLEMM_44`.

## APIs and Behavior
When enabled, provides `octetstream_open/resize/close`, a generic `lame_encode_pcm()` path, `lame_encode_pcm_flush()`, compatibility wrappers for `lame_encode_buffer`, `lame_encode_buffer_interleaved`, and `lame_encode_flush`, scalar dot-product implementations, scalar dispatch selection by CPU features, `unround_samplefrequency()`, `resample_open()`, `resample_close()`, and `resample_buffer()`.

## Data and Algorithms
Contains u-law and A-law conversion tables, endian-aware demux functions for 8/16/24/32-bit integer PCM and 32/64/80-bit float PCM, demux metadata indexed by PCM type bitfields, channel conversion by averaging or duplication, optional resampling through FIR tables, amplification/fade handling, frame buffering, and encoder dispatch to Layer I/II/III, MPEG-plus, AAC, or Ogg paths when compiled.

## Dependencies
Includes `bitstream.h` and `id3tag.h` outside the compile gate, and under `KLEMM_44` includes `pcm.h` plus math/stdio/memory/system headers. Uses many internal fields from `lame_t`.

## Risks and Notes
Most code is inactive unless `KLEMM_44` is defined. Active code has debug tracing and writes `pcm_data.txt` in `lame_encode_frame()`. Several allocation results are unchecked, some error paths leak allocated buffers, and the implementation depends on internal `lame_t` layout not visible in this file.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/pcm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/pcm.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/pcm.h

## Scope
Interface and constants for the generalized PCM/resampling layer.

## APIs and Data
Defines encoder delay/resampling constants, object IDs, floating typedefs, scalar function pointer types, data direction annotation macros, PCM layout flags (`LAME_INTERLEAVED`, `LAME_CHAINED`, `LAME_INDIRECT`), endian flags, PCM sample type flags, and channel-count flags. Declares scalar function pointers and possible i387/3DNow/SIMD/plain implementations, resampler lifecycle functions, `init_scalar_functions`, `unround_samplefrequency`, and `lame_encode_ogg_frame`.

## Dependencies
Includes `limits.h`, `lame.h`, and `util.h`.

## Risks and Notes
Defines `inline` as `__inline`, which can affect includers. The header assumes `CHAR_BIT == 8` and emits preprocessor diagnostics otherwise. Many declared optimized scalar implementations are platform/build dependent.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/pcm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/portableio.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/portableio.c

## Scope
Endian-independent file I/O helpers for integer and extended floating-point values, originally from Apple/Slaney/Turkowski code.

## APIs and Behavior
Implements `ReadByte`, 16/24/32-bit low-high and high-low readers, 8/16/32-bit writers, byte-block read/write with optional byte reversal, `ConvertFromIeeeExtended`, and `ReadIeeeExtendedHighLow`. Some alternate implementations are compiled under `KLEMM_36`.

## Dependencies
Uses `stdio.h`, `math.h` or `ymath.h`, and `portableio.h`.

## Risks and Notes
The file’s own comments call out portability flaws: assumes 8-bit chars, does not handle EOF robustly, assumes 32-bit-or-larger `int`, and lacks write error checks. Several functions mask `getc()` without checking EOF first. `portableio.h` declares more IEEE float/double read/write APIs than this file visibly implements.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/portableio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/portableio.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/portableio.h

## Scope
Header for portable endian/file I/O routines.

## APIs
Declares byte, 16/24/32-bit integer, raw byte, swapped byte, IEEE float/double, and IEEE extended read/write helpers. Defines C/C++ linkage macro `CLINK`, `Read32BitsLowHigh(f)` as `Read32Bits(f)`, and `WriteString(f,s)` as an `fwrite` wrapper.

## Dependencies
Includes `stdio.h`.

## Risks and Notes
The header exposes APIs whose implementations may be absent or compiled elsewhere. `WriteString` uses `strlen` but this header does not include `string.h`, so includers must provide it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/portableio.h -->