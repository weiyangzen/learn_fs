# Group Research: group_57_9front_sources_os_plan9_9front_sys_src_cmd_audio_mp3enc_psymodel_c_so_48a9255ab91a

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/plan9/9front`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/psymodel.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/psymodel.c

This file implements LAME's Layer III psychoacoustic model for the 9front-imported `mp3enc` tree. It computes masking thresholds, perceptual entropy, block switching decisions, and mid/side stereo guidance from PCM windows and FFT energy.

Key responsibilities:
- Lazily initializes psychoacoustic state and FFT tables through `psymodel_init()` and `init_fft()`.
- Provides two analysis paths:
  - `L3psycho_anal()`: older ISO/GPSYCHO-style analysis using unpredictability and tonality from long/short FFTs.
  - `L3psycho_anal_ns()`: nspsytune-style analysis using spectral peak tonality, high-pass attack detection, additive masking, and extra mid/side fixes.
- Computes long- and short-block energy/masking data into `III_psy_ratio` structures.
- Maintains a one-granule delay: current analysis is saved in `gfc`, while previous-granule ratios, perceptual entropy, and block types are returned to the encoder.
- Determines block types (`NORM_TYPE`, `START_TYPE`, `SHORT_TYPE`, `STOP_TYPE`) from attack/PE history.
- Computes mid/side masking thresholds and `ms_ratio`/`ms_ratio_next` signals for joint stereo decisions.
- Builds Bark-scale partition bands, scalefactor-band mappings, spreading functions, ATH partition values, demasking thresholds, and temporal masking decay in `L3para_read()`.
- Initializes persistent history buffers, old block types, unpredictability limits, spreading-function index ranges, and nspsytune state in `psymodel_init()`.

Important functions:
- `L3psycho_anal(...)`: full classic psychoacoustic analyzer.
- `mask_add(...)`: nspsytune additive simultaneous masking combiner.
- `L3psycho_anal_ns(...)`: nspsytune psychoacoustic analyzer with attack/pre-echo controls.
- `s3_func(FLOAT8 bark)`: Bark-domain spreading function.
- `L3para_read(...)`: derives psychoacoustic partition/scalefactor mapping and spreading tables from samplerate.
- `psymodel_init(lame_global_flags *gfp)`: initializes all persistent psychoacoustic model state.

Control/data flow:
- The encoder calls this file from `encoder.c` before MDCT/quantization.
- Input PCM buffers are transformed through `fft_long()` and `fft_short()` for left/right channels; joint stereo creates mid/side FFT spectra from those results.
- Per-line FFT energies are grouped into critical-band partitions.
- Thresholds are convolved with `s3_l`/`s3_s` spreading functions.
- Partition data is remapped to MPEG scalefactor bands using `bu_*`, `bo_*`, `w1_*`, and `w2_*` tables.
- Results populate `gfc->en[]`, `gfc->thm[]`, `gfc->pe[]`, `gfc->tot_ener[]`, `gfc->blocktype_old[]`, and optional `pinfo` analysis fields.
- Returned `masking_ratio` and `masking_MS_ratio` feed quantization threshold calculation in `quantize_pvt.c`.

Notable behavior:
- Classic mode estimates unpredictability for low spectral lines from long FFT history and for higher lines from short FFTs.
- nspsytune mode applies an fs/4 high-pass FIR for attack detection over 12 sub-short blocks.
- nspsytune applies short-block pre-echo attenuation based on current and previous attack positions.
- `no_short_blocks` forces long-block decisions.
- Joint stereo generally forces both channels to share block type unless `allow_diff_short` is enabled and MS stereo is not used.
- `safejoint` reduces the nspsytune MS masking relaxation from `NS_MSFIX` to a stricter value.
- `analysis` mode fills plotting/diagnostic arrays.

Dependencies:
- Includes `util.h`, `encoder.h`, `psymodel.h`, `l3side.h`, `tables.h`, and `fft.h`.
- Relies on internal fields in `lame_internal_flags`, especially psychoacoustic history arrays defined in `util.h`.
- Uses ATH and scalefactor-band data initialized elsewhere in the encoder setup.

Risks and edge cases:
- This file is heavily stateful; first-call initialization and one-granule delayed returns must stay synchronized with encoder buffering.
- `energy` is treated as a 4-channel array in the implementation, while `psymodel.h` declares the parameter as `FLOAT8 ener[2]`; C array decay hides this ABI-wise but the declaration is misleading.
- Several static/local arrays assume maximum channel count including derived M/S channels.
- Assertions guard partition counts and block-type invariants but may disappear in non-debug builds.
- The nspsytune path uses hard-coded regression coefficients and attack thresholds; behavior is sensitive to samplerate and encoder quality settings.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/psymodel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/psymodel.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/psymodel.h

This header declares the psychoacoustic analysis API used by the frame encoder.

Exports:
- `L3psycho_anal(...)`: classic psychoacoustic analysis.
- `L3psycho_anal_ns(...)`: nspsytune psychoacoustic analysis.
- `psymodel_init(lame_global_flags *gfp)`: initializes psychoacoustic internal state.

Dependencies:
- Includes `l3side.h` for `III_psy_ratio`, `lame_global_flags`, `sample_t`, and numeric typedefs.

Integration:
- Included by `encoder.c` to choose and call the psychoacoustic model before quantization.
- Implemented by `psymodel.c`.

Risks and edge cases:
- The `ener` parameter is declared as `FLOAT8 ener[2]`, but `psymodel.c` accepts and writes a 4-element energy array for L/R/M/S channels. Because C array bounds in parameters decay to pointers, this compiles, but the declaration under-documents the required storage.
- The first parameter is named `gfc` in declarations but is actually a `lame_global_flags *`; this is cosmetic but confusing because `gfc` usually means `lame_internal_flags *`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/psymodel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize.c

This file implements the main Layer III quantization loops for CBR, VBR, and ABR encoding. It takes MDCT coefficients plus psychoacoustic masking ratios and produces quantized spectral coefficients, scalefactors, Huffman-side information, bitrate selection, and reservoir updates.

Key responsibilities:
- Initializes per-granule/channel quantization state with `init_outer_loop()`.
- Searches global gain and quantizer step sizes via `bin_search_StepSize()` and `inner_loop()`.
- Runs the outer noise-shaping/scalefactor amplification loop with `outer_loop()`.
- Chooses better quantization candidates through configurable `quant_compare()` policies.
- Adjusts scalefactor scale, subblock gain, and per-band amplification through helper loops.
- Implements final post-quantization steps in `iteration_finish()`: scalefactor storage optimization, optional Huffman-region optimization, reservoir accounting, and coefficient sign restoration.
- Provides three public frame quantizers:
  - `iteration_loop()` for CBR.
  - `VBR_iteration_loop()` for VBR.
  - `ABR_iteration_loop()` for average bitrate mode.

Important internal functions:
- `init_outer_loop(...)`: resets `gr_info`, clears scalefactors, computes `xrpow = |xr|^(3/4)`, and detects digital silence.
- `bin_search_StepSize(...)`: finds an initial global gain that approaches a bit target.
- `inner_loop(...)`: raises global gain until Huffman bits fit a max bit budget.
- `loop_break(...)`: detects whether every scalefactor band has already been amplified.
- `quant_compare(...)`: compares noise metrics under `experimentalX` modes.
- `amp_scalefac_bands(...)`: amplifies bands whose noise exceeds the trigger.
- `inc_scalefac_scale(...)`: converts scalefactors to doubled step size where possible.
- `inc_subblock_gain(...)`: tries to reduce oversized short-block scalefactors by raising subblock gain.
- `balance_noise(...)`: coordinates scalefactor amplification and bitcount validity checks.
- `outer_loop(...)`: main noise-shaping iteration.
- `VBR_encode_granule(...)`: binary-searches a good per-granule bit count for acceptable VBR noise.
- `get_framebits(...)`, `calc_min_bits(...)`, `calc_max_bits(...)`, `VBR_prepare(...)`: VBR bit budget setup.
- `calc_target_bits(...)`: ABR target bit calculation.

Public functions:
- `iteration_loop(...)`
- `VBR_iteration_loop(...)`
- `ABR_iteration_loop(...)`
- `bin_search_StepSize(...)`
- `inner_loop(...)`

Control/data flow:
- The encoder passes `xr`, `ratio`, `pe`, and M/S energy ratios into one of the public loops.
- Each granule/channel initializes `cod_info`, `scalefac`, and `xrpow`.
- `calc_xmin()` from `quantize_pvt.c` converts psychoacoustic thresholds into allowed distortion.
- `outer_loop()` repeatedly quantizes, counts bits, measures distortion, and amplifies scalefactor bands until quality or loop-stop criteria are met.
- `count_bits()` and Huffman helpers in `takehiro.c` calculate coding length and table selections.
- `best_scalefac_store()` and `best_huffman_divide()` refine side-info storage after final quantization.
- Reservoir functions assign and reconcile available bits.

VBR behavior:
- `VBR_prepare()` optionally converts LR to MS coefficients, computes quality-dependent masking lower factors, detects analog silence, and computes min/max bit budgets.
- `VBR_iteration_loop()` first estimates needed bits, chooses the smallest bitrate that can hold them, and may retry with relaxed thresholds or repartitioned budgets.
- `vbr_mtrh` delegates per-granule quantization to `VBR_noise_shaping2()` from `vbrquantize.c`.

ABR behavior:
- `calc_target_bits()` starts from target average bitrate, adds bits based on perceptual entropy, caps by max frame capacity, and reduces side-channel allocation in MS mode.
- `ABR_iteration_loop()` then selects the lowest allowed bitrate index capable of holding the final frame.

CBR behavior:
- `iteration_loop()` asks reservoir code for target/extra bits, allocates based on PE, optionally converts LR to MS, and quantizes each granule/channel within the current frame budget.

Dependencies:
- Includes `util.h`, `l3side.h`, `quantize.h`, `reservoir.h`, `quantize_pvt.h`, and `lame-analysis.h`.
- Uses MPEG bitrate tables from `tables.c` through headers.
- Depends heavily on `lame_internal_flags` state: bitrate index, mode granules, side info, noise-shaping flags, VBR bounds, scalefactor bands, and reservoir size.

Risks and edge cases:
- Quantization loops depend on many mutable globals in `gfc`; retry paths must restore `cod_info`, `scalefac`, and `xrpow` carefully.
- `inc_subblock_gain()` computes `width = scalefac_band.s[sfb] - scalefac_band.s[sfb+1]`, which is negative for normal ascending scalefactor bands; that makes its later loop inert and looks like a latent bug or old-code typo.
- `bin_search_StepSize()` mutates `gfc->CurrentStep` using a heuristic that depends on prior frames.
- Several bit budgets are bounded by hard constants such as `MAX_BITS`, `LARGE_BITS`, and magic PE thresholds.
- VBR loops can retry while relaxing thresholds if used bits exceed frame capacity; correctness depends on convergence and valid bitrate bounds.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize.h

This header declares the public quantization entry points used by the frame encoder and VBR modules.

Exports:
- `iteration_loop(...)`: CBR frame quantization.
- `VBR_iteration_loop(...)`: VBR quantization/bitrate selection.
- `ABR_iteration_loop(...)`: ABR quantization/bitrate selection.
- `VBR_quantize(...)`: alternate VBR quantizer implemented elsewhere.
- `VBR_noise_shaping2(...)`: per-granule VBR noise-shaping helper used by `vbr_mtrh`.

Dependencies:
- Includes `util.h`, which provides `lame_global_flags`, `FLOAT8`, `III_psy_ratio`, `III_scalefac_t`, and related encoder types.

Integration:
- Included by `encoder.c` and quantization-related modules.
- The declarations route all frame-level MDCT/psychoacoustic output into quantized `l3_enc` coefficients and scalefactors.

Risks and edge cases:
- The header exposes large fixed-size array contracts such as `[2][2][576]`; callers must preserve granule/channel/coefficient layout exactly.
- `VBR_quantize()` and `VBR_noise_shaping2()` are declared here but not implemented in `quantize.c`, so link completeness depends on the companion VBR source.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize_pvt.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize_pvt.c

This file provides shared private quantization data and helper routines: scalefactor-band tables, ATH computation, allowed-distortion computation, noise measurement, plotting data, and nonlinear quantizer lookup initialization.

Key responsibilities:
- Defines MPEG scalefactor partition tables:
  - `slen1_tab`, `slen2_tab`
  - `nr_of_sfb_block`
  - `pretab`
  - `sfBandIndex`
- Initializes quantization lookup tables:
  - `pow43`
  - `adj43`
  - `adj43asm`
  - `pow20`
  - `ipow20`
- Computes ATH per scalefactor band through `ATHmdct()` and `compute_ath()`.
- Converts L/R MDCT coefficients to M/S with `ms_convert()`.
- Allocates CBR target bits from perceptual entropy and reservoir availability via `on_pe()`.
- Reduces side-channel bit allocation in M/S stereo via `reduce_side()`.
- Converts psychoacoustic ratios into allowed quantization noise with `calc_xmin()`.
- Computes actual quantization noise and aggregate metrics with `calc_noise()`.
- Updates optional analysis/plotting structures through `set_pinfo()` and `set_frame_pinfo()`.
- Implements `quantize_xrpow()` and `quantize_xrpow_ISO()` for nonlinear quantization of `|xr|^(3/4)`.

Important functions:
- `iteration_init(lame_global_flags *gfp)`: one-time setup for ATH arrays, quantizer tables, and Huffman table chooser.
- `ATHmdct(...)`: converts ATH formula output into MDCT energy-domain threshold.
- `compute_ath(...)`: finds minimum ATH per long/short scalefactor band.
- `ms_convert(...)`: coefficient-domain M/S transform.
- `on_pe(...)`: target-bit allocation based on perceptual entropy.
- `reduce_side(...)`: shifts bits from side to mid channel based on side/mid energy ratio.
- `calc_xmin(...)`: computes `l3_xmin` masking thresholds per scalefactor band.
- `penalties(...)`: nonlinear noise penalty used in Klemm noise metric.
- `calc_noise(...)`: compares quantized reconstruction against original MDCT coefficients.
- `set_frame_pinfo(...)`: fills analysis fields after quantization.
- `quantize_xrpow(...)`: default quantizer using adjustment tables.
- `quantize_xrpow_ISO(...)`: ISO-style quantizer.

Control/data flow:
- `iteration_init()` is called before quantization begins and calls `huffman_init()` from `takehiro.c`.
- `quantize.c` calls `calc_xmin()` before `outer_loop()` and `calc_noise()` during noise shaping.
- `takehiro.c` calls `quantize_xrpow()` or `quantize_xrpow_ISO()` through `count_bits()`.
- Analysis mode uses `set_frame_pinfo()` after final signs and scalefactors are known.

Notable behavior:
- ATH scaling differs for nspsytune (`NSATHSCALE`) versus older model.
- `noATH` forces ATH thresholds down to near zero.
- `calc_xmin()` applies nspsytune bass/alto/treble shaping and optional temporal masking.
- For high-quality CBR/ABR nspsytune paths, `calc_xmin()` can aggressively lower thresholds by multiplying by `0.001`.
- There is optional `TAKEHIRO_IEEE754_HACK` code for faster float-to-int quantization; the default path uses portable casts and adjustment tables.

Dependencies:
- Includes `util.h`, `lame-analysis.h`, `tables.h`, `reservoir.h`, and `quantize_pvt.h`.
- Uses `ATHformula()` and internal ATH/scalefactor-band state from `lame_internal_flags`.

Risks and edge cases:
- Lookup arrays require quantized values to stay below `PRECALC_SIZE`; `count_bits()` checks against `IXMAX_VAL` before quantization.
- `compute_ath()` is declared in the header with `ATH_s[SBPSY_l]`, while short-block ATH arrays conceptually use `SBPSY_s`; the C ABI is unaffected but the declaration is misleading.
- `calc_noise()` assumes positive `l3_xmin` thresholds; extremely small thresholds can produce huge noise ratios.
- Optional IEEE754 hack is architecture-sensitive and disabled unless explicitly compiled.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize_pvt.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize_pvt.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize_pvt.h

This private header exposes quantization internals shared by `quantize.c`, `quantize_pvt.c`, `takehiro.c`, and related encoder modules.

Key definitions:
- `IXMAX_VAL`: maximum allowed quantized coefficient plus linbits margin.
- `PRECALC_SIZE`: quantizer lookup table size.
- `Q_MAX`: size for `pow20`/`ipow20` global gain tables.
- `LARGE_BITS`: sentinel bit count for impossible encodings.
- `calc_noise_result`: aggregate quantization-noise metrics.

Exported data:
- MPEG scalefactor tables: `nr_of_sfb_block`, `pretab`, `slen1_tab`, `slen2_tab`, `sfBandIndex`.
- Quantizer tables: `pow43`, `adj43`, `adj43asm`, `pow20`, `ipow20`.

Exported functions:
- ATH and M/S helpers: `compute_ath()`, `ms_convert()`.
- Bit allocation: `on_pe()`, `reduce_side()`.
- Quantization search: `bin_search_StepSize()`, `inner_loop()`, `iteration_init()`.
- Noise and thresholds: `calc_xmin()`, `calc_noise()`, `set_frame_pinfo()`.
- Quantizer kernels: `quantize_xrpow()`, `quantize_xrpow_ISO()`.
- Huffman/scalefactor helpers from `takehiro.c`: `count_bits()`, `best_huffman_divide()`, `best_scalefac_store()`, `scale_bitcount()`, `scale_bitcount_lsf()`, `huffman_init()`.

Dependencies:
- Includes `l3side.h` for side-info, scalefactor, and psychoacoustic types.

Risks and edge cases:
- This header deliberately exposes mutable global lookup arrays; initialization order via `iteration_init()` matters.
- Several functions accept large fixed-size arrays by pointer; dimension mismatches will not be caught by C.
- The `compute_ath()` short-array bound is misleading (`SBPSY_l`) even though the implementation iterates short bands separately.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/quantize_pvt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/reservoir.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/reservoir.c

This file manages the MP3 Layer III bit reservoir. It calculates frame capacity, distributes reservoir bits to granules, tracks surplus/deficit after quantization, and schedules stuffing/drain bits.

Key responsibilities:
- Computes the maximum reservoir size allowed for the current MPEG version, frame length, strict ISO mode, and `disable_reservoir`.
- Reports available frame bits at the beginning of a frame through `ResvFrameBegin()`.
- Computes target and extra bits for a granule through `ResvMaxBits()`.
- Updates reservoir size after each granule with `ResvAdjust()`.
- Byte-aligns and drains surplus bits at frame end with `ResvFrameEnd()`.

Important functions:
- `ResvFrameBegin(lame_global_flags *gfp, III_side_info_t *l3_side, int mean_bits, int frameLength)`: sets `gfc->ResvMax`, clears pre-drain, updates pinfo, and returns full frame bit capacity.
- `ResvMaxBits(...)`: returns base `targ_bits` and allowed `extra_bits` from the reservoir.
- `ResvAdjust(...)`: adds unused bits or subtracts overuse after quantization.
- `ResvFrameEnd(...)`: drains stuffing bits to keep reservoir byte-aligned and within max.

Control/data flow:
- `quantize.c` calls `ResvFrameBegin()` before allocation, `ResvMaxBits()` for CBR PE-based targets, `ResvAdjust()` after each final granule/channel, and `ResvFrameEnd()` after the frame.
- Bitstream formatting later uses `l3_side->resvDrain_pre`, `resvDrain_post`, and `main_data_begin`.

Notable behavior:
- MPEG-1 reservoir limit is `8*511`; MPEG-2 uses `8*255`.
- Strict ISO max frame buffer is `8*960`; non-strict allows `8*2047`.
- If the reservoir is almost full, target bits are increased to burn surplus; otherwise, CBR can reserve about 10 percent of mean bits to build reservoir.
- The active code drains all stuffing into current-frame ancillary data. The alternate `NEW_DRAIN` path is disabled because the file defines `NEW_DRAINXX`, not `NEW_DRAIN`.

Risks and edge cases:
- Reservoir accounting is integer/bit exact; any mismatch with bitstream formatter can corrupt `main_data_begin`.
- `ResvAdjust()` does not use its `l3_side` argument.
- The disabled `NEW_DRAIN` path suggests historical uncertainty around pre/post drain behavior.
- Assertions require byte-aligned `ResvMax` and overage values.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/reservoir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/reservoir.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/reservoir.h

This header declares the MP3 bit reservoir API.

Exports:
- `ResvFrameBegin(...)`
- `ResvMaxBits(...)`
- `ResvAdjust(...)`
- `ResvFrameEnd(...)`

Dependencies:
- Relies on types from headers included before it, especially `lame_global_flags`, `lame_internal_flags`, `III_side_info_t`, and `gr_info`.

Integration:
- Included by quantization modules to allocate and reconcile per-frame/per-granule bit budgets.
- Implemented by `reservoir.c`.

Risks and edge cases:
- The header does not include the type-defining headers it needs, so include order matters.
- `ResvMaxBits()` names its fourth pointer `max_bits` in the declaration, while the implementation uses it as `extra_bits`; this is a documentation/API clarity mismatch.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/reservoir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/set_get.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/set_get.c

This file contains part of the `lame_global_flags` setter/getter API plus many forward declarations for additional public settings.

Implemented setters/getters:
- Input stream:
  - `lame_set_num_samples()`, `lame_get_num_samples()`
  - `lame_set_in_samplerate()`, `lame_get_in_samplerate()`
  - `lame_set_num_channels()`, `lame_get_num_channels()`
  - `lame_set_scale()`, `lame_get_scale()`
  - `lame_set_out_samplerate()`, `lame_get_out_samplerate()`
- General controls:
  - `lame_set_analysis()`, `lame_get_analysis()`
  - `lame_set_bWriteVbrTag()`, `lame_get_bWriteVbrTag()`
  - `lame_set_disable_waveheader()`, `lame_get_disable_waveheader()`
  - `lame_set_decode_only()`, `lame_get_decode_only()`
  - `lame_set_ogg()`, `lame_get_ogg()`
  - `lame_set_quality()`, `lame_get_quality()`
  - `lame_set_mode()`, `lame_get_mode()`
  - `lame_set_mode_automs()`, `lame_get_mode_automs()`
- Message callback setters:
  - `lame_set_errorf()`
  - `lame_set_debugf()`
  - `lame_set_msgf()`

Declared but not implemented in this file:
- Many settings for force-MS, free-format, bitrate/compression ratio, frame flags, reservoir, experimental options, VBR controls, filters, ATH options, psychoacoustic flags, and internal read-only values.

Validation behavior:
- Boolean-like fields generally reject values outside `0..1`.
- `lame_set_num_channels()` rejects zero and values above two.
- `lame_set_mode()` rejects modes outside the `MPEG_mode` enum range.
- Getter assertions document expected normalized values.

Dependencies:
- Includes `lame.h` for public encoder structures and enums.

Integration:
- Intended as the public C API layer for configuring `lame_global_flags`.
- The implemented functions directly mutate fields in `lame_global_flags`; derived validation and adjustment happen later in `lame_init_params()`.

Risks and edge cases:
- Large portions of this `.c` file are only prototypes, not implementations. If matching implementations are absent elsewhere, the public API is incomplete.
- Many setters perform minimal validation and allow values later clamped or interpreted by initialization.
- Assertions in getters catch invalid state only when assertions are enabled.
- Callback setters store raw function pointers without null checks, which may be intentional for disabling callbacks.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/set_get.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tables.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tables.c

This file defines static MPEG Layer III Huffman and MPEG version tables used by bit counting, bitstream writing, and parameter initialization.

Key responsibilities:
- Defines Huffman codeword tables `t1HB` through `t33HB`.
- Defines Huffman code-length tables `t1l` through `t33l`.
- Defines the public `ht[HTN]` array of `struct huffcodetab` entries.
- Defines packed bit-count helper tables:
  - `largetbl` for comparing table 16 and 24 style choices.
  - `table23` for comparing Huffman tables 2 and 3.
  - `table56` for comparing Huffman tables 5 and 6.
- Defines MPEG bitrate/samplerate/version/header constants:
  - `bitrate_table`
  - `samplerate_table`
  - `version_string`
  - `header_word`

Integration:
- `takehiro.c` uses `ht`, `t32l`, `t33l`, `largetbl`, `table23`, and `table56` for Huffman table selection and bit counting.
- Encoder initialization and bitstream formatting use bitrate/samplerate/header constants.

Dependencies:
- Includes `util.h` and `tables.h`.

Notable behavior:
- The `ht` table maps table numbers `0..33`, with unused entries represented by null table pointers or length-only entries.
- Tables 16 through 23 share the same code table with increasing `linmax`.
- Tables 24 through 31 share another large-value table family.
- Count1 tables 32 and 33 encode quadruples.

Risks and edge cases:
- These constants encode MPEG spec data; any table corruption changes bitstream validity.
- Some generated helper tables pack two candidate bit counts into one `unsigned int` for fast comparison, so endian-independent arithmetic assumptions matter only at integer value level, not byte layout.
- The file comment says `end of tables.h` at the end, but this is harmless stale text.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tables.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tables.h

This header declares MPEG Layer III table structures and public table symbols.

Key definitions:
- `type1_t`, `type2_t`, `type34_t`, `type5_t`: older psychoacoustic table record types.
- `HTN`: Huffman table count, set to 34.
- `struct huffcodetab`: Huffman table descriptor with `xlen`, `linmax`, code table, and code-length table.

Exports:
- `table5[6]`: declared but not defined in `tables.c`; likely legacy/unused in this import.
- `ht[HTN]`
- `t32l[]`, `t33l[]`
- `largetbl[16*16]`
- `table23[3*3]`
- `table56[4*4]`

Dependencies:
- Includes `machine.h` for `size_t` and platform definitions.

Integration:
- Used by `takehiro.c` for Huffman bit counting.
- Used by `tables.c` to define the exported table data.

Risks and edge cases:
- `bitrate_table`, `samplerate_table`, `version_string`, and `header_word` are defined in `tables.c` but are not declared here; other declarations likely live in another common header.
- `table5` is declared here but absent from the read `tables.c`, suggesting dead legacy API or another definition elsewhere.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tables.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/takehiro.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/takehiro.c

This file implements MP3 Huffman table selection, quantized coefficient bit counting, scalefactor-storage optimization, and Huffman-region refinement.

Key responsibilities:
- Chooses optimal Huffman tables for quantized coefficient regions.
- Counts bits for big-values and count1 regions.
- Sets `big_values`, `count1`, `table_select[]`, `region0_count`, `region1_count`, and `count1table_select` in `gr_info`.
- Recalculates better region divisions after quantization.
- Applies `scfsi` sharing between MPEG-1 granules where legal.
- Optimizes scalefactor storage (`scalefac_scale`, `preflag`, `scalefac_compress`, `part2_length`).
- Initializes per-bigvalue scalefactor-region lookup tables in `huffman_init()`.

Important functions:
- `ix_max(...)`: maximum quantized coefficient in a region.
- `count_bit_ESC(...)`: bit count for escape-code Huffman tables.
- `count_bit_noESC(...)`, `count_bit_noESC_from2(...)`, `count_bit_noESC_from3(...)`: fast bit counts for non-escape table families.
- `choose_table_nonMMX(...)`: selects best Huffman table for a coefficient pair region.
- `count_bits_long(...)`: counts bits for a complete granule/channel and fills Huffman side-info fields.
- `count_bits(...)`: quantizes `xrpow`, checks `IXMAX_VAL`, and calls `count_bits_long()`.
- `best_huffman_divide(...)`: tries alternative region divisions and count1 boundaries.
- `scfsi_calc(...)`: marks reusable long-block scalefactor bands in MPEG-1 second granule.
- `best_scalefac_store(...)`: removes scalefactors from zero bands, optionally halves scalefactors via `scalefac_scale`, applies `scfsi`, and updates part2 length.
- `scale_bitcount(...)`: MPEG-1 scalefactor bit count and compress selection.
- `scale_bitcount_lsf(...)`: MPEG-2/2.5 LSF scalefactor bit count and compress selection.
- `huffman_init(...)`: selects MMX/non-MMX table chooser and precomputes `bv_scf`.

Control/data flow:
- `quantize.c` calls `count_bits()` repeatedly during global-gain and outer noise-shaping loops.
- After final quantization, `quantize.c` calls `best_scalefac_store()` and optionally `best_huffman_divide()`.
- `iteration_init()` in `quantize_pvt.c` calls `huffman_init()` once during quantization setup.

Notable behavior:
- The table chooser has hard-coded knowledge of MPEG Huffman table families.
- Quantized coefficients beyond `IXMAX_VAL` cause `count_bits()` to return `LARGE_BITS`.
- Short-block MPEG-2 Huffman division optimization is explicitly skipped.
- `best_scalefac_store()` can set second-granule scalefactors to `-1` to indicate `scfsi` reuse.
- `scale_bitcount_lsf()` reverse-engineers MPEG-2 scalefactor compression partitioning and sets `slen[]`.

Dependencies:
- Includes `util.h`, `l3side.h`, `tables.h`, and `quantize_pvt.h`.
- Uses lookup tables from `tables.c` and quantizer kernels from `quantize_pvt.c`.

Risks and edge cases:
- This file is bitstream-critical; incorrect region counts or table choices produce invalid MP3 frames.
- Several optimizations depend on MPEG version, block type, and scalefactor-band boundaries.
- The MMX path is conditional and requires an external `choose_table_MMX()` symbol if enabled.
- Some assertions around region counts are commented out, so unusual boundary cases rely on later clamping.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/takehiro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/timestatus.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/timestatus.c

This file implements command-line progress reporting for encoding and decoding.

Key responsibilities:
- Tracks elapsed real time and CPU time for encoding.
- Estimates total encode time and ETA from current frame progress.
- Computes encode speed relative to realtime playback.
- Prints one-line updating progress status to `stderr`.
- Optionally integrates bitrate histogram display when `BRHIST` is enabled.
- Prints decoder progress for MP3 input frames.

Important functions:
- `ts_calc_times(...)`: computes estimated total time and speed index.
- `ts_time_decompose(...)`: formats seconds as `mm:ss`, `hh:mm:ss`, or large-hour text.
- `timestatus(...)`: main encoding progress renderer.
- `timestatus_finish()`: emits final newline.
- `timestatus_klemm(...)`: throttled public progress updater controlled by `silent` and `update_interval`.
- `decoder_progress(...)`: prints decoder frame number, total frames, bitrate, and joint-stereo mode transition hints.
- `decoder_progress_finish(...)`: emits decoder final newline.

Dependencies:
- Includes `lame.h`, `main.h`, `lametime.h`, and `timestatus.h`.
- Uses `GetRealTime()` and `GetCPUTime()` from `lametime.c`.
- Uses global UI controls such as `silent`, `update_interval`, and optional `brhist`.

Notable behavior:
- `timestatus()` uses static state for start times and an initialization workaround.
- Progress output is carriage-return based and intended for interactive terminals.
- Speed display is in `x` realtime units by default.
- `decoder_progress()` keeps static previous joint-stereo mode extension state to show transitions.

Risks and edge cases:
- Uses static state, so multiple concurrent encodes in the same process would share progress timing.
- `ts_calc_times()` asserts samplerate is 8000..48000.
- ETA is computed as unsigned subtraction after casting; if estimates go backward, display can be odd.
- Output is hard-wired to `stderr`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/timestatus.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/timestatus.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/timestatus.h

This header declares progress-reporting APIs for encoder and decoder command-line status.

Exports:
- `timestatus_klemm(const lame_global_flags *gfp)`
- `timestatus(int samp_rate, int frameNum, int totalframes, int framesize)`
- `timestatus_finish(void)`
- `decoder_progress(const lame_global_flags *gfp, const mp3data_struct *)`
- `decoder_progress_finish(const lame_global_flags *gfp)`

Dependencies:
- Requires `lame_global_flags` and `mp3data_struct` to be declared before inclusion.

Integration:
- Used by command-line encoding/decoding paths to display progress.
- Implemented by `timestatus.c`.

Risks and edge cases:
- Does not include `lame.h`, so include order matters.
- The decoder finish function accepts `gfp` but the implementation does not use it.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/timestatus.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tools.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tools.c

This file contains only a comment block describing intended scope for context-free LAME helper functions.

Content:
- States that this module should contain simple LAME functions that do not use `gfc` or `gfp`.
- States that functions here should not call non-local functions other than libc.
- Directs other utilities to `util.c`.

Exports:
- None.

Integration:
- No executable code is present.
- Likely a placeholder for future standalone helper functions.

Risks and edge cases:
- Empty compilation unit apart from comments; depending on build system/compiler, this is harmless but contributes no symbols.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tools.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tools.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tools.h

This file is empty.

Exports:
- None.

Integration:
- No include guard, declarations, comments, or dependencies.
- May exist as a placeholder for the empty `tools.c` module.

Risks and edge cases:
- Including it has no effect.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/tools.h -->