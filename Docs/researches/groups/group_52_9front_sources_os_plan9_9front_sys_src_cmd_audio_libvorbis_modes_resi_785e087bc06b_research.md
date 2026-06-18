# Group Research: group_52_9front_sources_os_plan9_9front_sys_src_cmd_audio_libvorbis_modes_resi_785e087bc06b

Scope: `Docs/research_subset_a.md`, specifically the listed 9front `sys/src/cmd/audio/libvorbis` residue/setup tables, psychoacoustic/residue/codebook/FFT implementations, and Vorbis public headers. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44.h

Static residue template header for 32/44.1/48 kHz stereo-coupled Vorbis encoder modes.

Important contents:
- Includes `vorbis/codec.h`, `backends.h`, and `books/coupled/res_books_stereo.h`.
- Defines three `vorbis_info_residue0` profiles: `_residue_44_low`, `_residue_44_mid`, and `_residue_44_high`, with progressively broader partition/class metrics.
- Defines many `static_bookblock` tables for quality slots `-1` through `9`, split into stereo and stereo-mid variants at low qualities, then higher-rate coupled residue books.
- Defines paired short/long `vorbis_residue_template` arrays `_res_44s_n1` through `_res_44s_9`.
- Exports `_mapres_template_44_stereo`, mapping quality indexes to `_map_nominal` plus the corresponding residue template.

Integration points:
- Included by `setup_44.h`.
- Uses codebooks generated under `books/coupled/`.
- Consumed by encoder setup assembly code through `ve_setup_data_template` mappings.

Risk and review signals:
- Pure static table data; correctness depends on table alignment with included codebooks and mapping expectations.
- Sentinel-like class metric values such as `999`/`157` are tuning data, not bounds checks.
- Any edits can silently alter bitrate/quality behavior across 44.1/48 kHz stereo encodes.

Filesystem relevance:
- No filesystem logic. This is vendored audio codec encoder configuration data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44p51.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44p51.h

Static residue and mapping template header for 44.1/48 kHz 5.1 Vorbis encoder modes.

Important contents:
- Includes `books/coupled/res_books_51.h`.
- Defines multichannel residue profiles `_residue_44p_lo`, `_residue_44p`, `_residue_44p_hi`, and `_residue_44p_lfe`.
- Defines main-channel residue bookblocks `_resbook_44p_n1` through `_resbook_44p_9`.
- Defines separate LFE bookblocks `_resbook_44p_ln1` through `_resbook_44p_l9`.
- Defines `_map_nominal_51` with coupling steps `{2,4,1,3}` and `_map_nominal_51u` with coupling disabled.
- Defines `_res_44p51_n1` through `_res_44p51_9`; each quality has short, long, and LFE residue templates.
- Exports `_mapres_template_44_51`, switching from coupled mappings at lower quality to uncoupled mappings for qualities 5 through 9.

Integration points:
- Included by `setup_44p51.h`.
- Uses 5.1-specific codebooks and LFE-specific residue coding.
- Depends on Vorbis mapping/residue setup structures from `backends.h`.

Risk and review signals:
- This file is entirely static codec tuning data, but table mismatch can affect 5.1 channel coding, especially LFE.
- Qualities 7-9 reuse `_huff_book__44p6_lfe` and `_resbook_44p_l6` for LFE, which appears intentional tuning reuse.
- Mapping arrays assume six channels and specific Vorbis 5.1 channel layout semantics.

Filesystem relevance:
- No filesystem logic. It is multichannel audio encoder setup data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44p51.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44u.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44u.h

Static residue template header for 32/44.1/48 kHz uncoupled Vorbis modes.

Important contents:
- Includes `books/uncoupled/res_books_uncoupled.h`.
- Defines `_residue_44_low_un`, `_residue_44_mid_un`, and `_residue_44_hi_un` residue profiles for uncoupled channels.
- Defines `_map_nominal_u`, a one-submap mapping with no channel coupling.
- Defines uncoupled static bookblocks `_resbook_44u_n1` through `_resbook_44u_9`.
- Defines short/long `vorbis_residue_template` arrays `_res_44u_n1` through `_res_44u_9`.
- Exports `_mapres_template_44_uncoupled`, mapping quality indexes to `_map_nominal_u`.

Integration points:
- Included by `setup_44u.h` and reused indirectly by `setup_32.h` for uncoupled 32 kHz modes.
- Shares psychoacoustic and floor setup with 44 kHz modes while selecting uncoupled residue books.

Risk and review signals:
- Static table data only; wrong partition metrics or book pointers would alter encoder output or fail setup.
- The uncoupled mapping intentionally disables stereo coupling, trading compression efficiency for independent channels.
- Book names vary slightly (`_44u8_p...` vs `_44u8__...` style), so mechanical edits are error-prone.

Filesystem relevance:
- No filesystem logic. It is Vorbis encoder table configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_44u.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_8.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_8.h

Static residue templates for 8/11 kHz Vorbis encoder modes.

Important contents:
- Includes `vorbis/codec.h` and `backends.h`; it relies on residue profiles and mappings defined by earlier included headers.
- Defines stereo bookblocks `_resbook_8s_0` and `_resbook_8s_1`.
- Defines stereo residue templates `_res_8s_0` and `_res_8s_1`, both using `_residue_44_mid`.
- Exports `_mapres_template_8_stereo`.
- Defines uncoupled bookblocks `_resbook_8u_0` and `_resbook_8u_1`.
- Defines uncoupled templates `_res_8u_0` and `_res_8u_1`, using `_residue_44_low_un` and `_residue_44_mid_un`.
- Exports `_mapres_template_8_uncoupled`.

Integration points:
- Included by `setup_8.h`; `setup_11.h` reuses the same 8 kHz residue templates for 11 kHz.
- Depends on `_map_nominal`, `_map_nominal_u`, and residue profile symbols defined in other mode headers.

Risk and review signals:
- Header inclusion order matters because several referenced symbols are not defined locally.
- This low-rate configuration has only two quality classes, so quality interpolation is coarse.
- All content is static encoder tuning data.

Filesystem relevance:
- No filesystem logic. This is audio codec setup data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_8.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_11.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_11.h

Top-level encoder setup template for 11 kHz Vorbis modes.

Important contents:
- Includes `psych_11.h`.
- Defines fixed block size `{512,512}` for both short and long paths.
- Defines floor mapping `_floor_mapping_11a` selecting floor index 6.
- Defines stereo bitrate mapping `{8000,13000,44000}` and uncoupled mapping `{12000,20000,50000}`.
- Defines quality mapping `{-0.1,0.0,1.0}`.
- Defines `ve_setup_11_stereo` and `ve_setup_11_uncoupled`.

Integration points:
- Reuses many 8 kHz tables: `_psy_noiseguards_8`, `_psy_compand_8`, `_noise_start_8`, `_noise_part_8`, `_global_mapping_8`, `_psy_stereo_modes_8`, and `_mapres_template_8_*`.
- Uses 11 kHz-specific tone, noise bias, lowpass, and threshold tables.

Risk and review signals:
- Static setup data only.
- Stereo uses coupling indicator `2`; uncoupled uses `-1`.
- Low-rate setup uses one floor mapping set and fixed block sizes, so changes have broad effect across all 11 kHz qualities.

Filesystem relevance:
- No filesystem logic. It is Vorbis encoder preset configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_11.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_16.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_16.h

Top-level encoder setup template for 16 kHz Vorbis modes.

Important contents:
- Includes `psych_16.h` and `residue_16.h`.
- Defines short block sizes `{1024,512,512}` and long block sizes `{1024,1024,1024}`.
- Defines two floor mapping arrays: `_floor_mapping_16a` and `_floor_mapping_16b`.
- Defines stereo and uncoupled bitrate mappings with four points.
- Defines `_global_mapping_16`, `quality_mapping_16`, and `_psy_compand_16_mapping`.
- Defines `ve_setup_16_stereo` and `ve_setup_16_uncoupled`.

Integration points:
- Uses 16 kHz psychoacoustic tables for tone, noise, ATH, lowpass, and stereo modes.
- Uses `_mapres_template_16_stereo` and `_mapres_template_16_uncoupled`.
- Reuses `_psy_compand_8` with 16 kHz compand mappings.

Risk and review signals:
- Static setup only; data shape must match `ve_setup_data_template`.
- Quality mapping has four points, not the 12-point 44 kHz scheme.
- Floor mapping count is `2`; callers must not select a third mapping.

Filesystem relevance:
- No filesystem logic. This is audio encoder setup data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_16.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_22.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_22.h

Top-level encoder setup template for 22 kHz modes, built mostly from 16 kHz tables with 22 kHz rate/lowpass adjustments.

Important contents:
- Defines `rate_mapping_22` and `rate_mapping_22_uncoupled`.
- Defines `_psy_lowpass_22`.
- Defines `ve_setup_22_stereo` and `ve_setup_22_uncoupled`.

Integration points:
- Reuses 16 kHz block sizes, floor mappings, quality mapping, companding, noise guards, noise bias, ATH, stereo modes, and residue templates.
- Expects `setup_16.h`-provided symbols to be in scope before this header is used.
- Uses `_mapres_template_16_stereo` and `_mapres_template_16_uncoupled`.

Risk and review signals:
- Header dependency order matters; it does not include `setup_16.h` itself.
- Static tuning data only.
- Lowpass values `{9.5,11,30,99}` define the major 22 kHz-specific behavior.

Filesystem relevance:
- No filesystem logic. It is Vorbis encoder preset data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_22.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_32.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_32.h

Top-level encoder setup template for 32 kHz modes, reusing 44 kHz psychoacoustic/residue infrastructure with 32 kHz rate mappings.

Important contents:
- Defines 12-point stereo and uncoupled bitrate mappings.
- Defines `_psy_lowpass_32` with lower lowpass values at lower quality and `99` for high quality.
- Defines `ve_setup_32_stereo` and `ve_setup_32_uncoupled`.

Integration points:
- Relies on 44 kHz symbols such as `quality_mapping_44`, `blocksize_short_44`, `blocksize_long_44`, `_psy_tone_masteratt_44`, `_floor_mapping_44`, and `_mapres_template_44_*`.
- Stereo uses `_psy_stereo_modes_44`; uncoupled passes `NULL` for stereo modes.
- Uses the same floor books/floors as 44 kHz.

Risk and review signals:
- Header inclusion order matters because it assumes 44 kHz setup symbols are already available.
- Static setup data only.
- Uncoupled rate mapping is substantially higher than stereo mapping at low qualities.

Filesystem relevance:
- No filesystem logic. This is audio encoder setup configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44.h

Primary top-level setup template for 44.1/48 kHz stereo Vorbis modes.

Important contents:
- Includes `modes/floor_all.h`, `modes/residue_44.h`, and `modes/psych_44.h`.
- Defines 12-point stereo bitrate mapping and 12-point quality mapping from `-0.1` to `1.0`.
- Defines 11 short and long block sizes for quality slots.
- Defines short/long companding mappings and `_global_mapping_44`.
- Defines three floor mapping arrays `_floor_mapping_44a`, `_floor_mapping_44b`, `_floor_mapping_44c`.
- Defines `ve_setup_44_stereo`.

Integration points:
- Base setup reused by `setup_32.h`, `setup_44p51.h`, `setup_44u.h`, and `setup_X.h`.
- Binds 44 kHz psychoacoustic tables, floor tables, and coupled residue templates.
- Supplies shared symbols such as `quality_mapping_44`, block sizes, and floor mappings.

Risk and review signals:
- This is a central static table; changes can affect several other setup headers.
- `rate_mapping_44_stereo` ends at `250001`, likely to avoid boundary ambiguity.
- Floor mapping arrays have 11 entries while quality mapping has 12 entries; this matches existing libvorbis setup conventions but is easy to misuse.

Filesystem relevance:
- No filesystem logic. It is encoder preset data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44p51.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44p51.h

Top-level setup template for 44.1/48 kHz 5.1 surround Vorbis modes.

Important contents:
- Includes `modes/residue_44p51.h`.
- Defines 12-point `rate_mapping_44p51`.
- Defines `ve_setup_44_51` for six-channel encoding.

Integration points:
- Reuses shared 44 kHz quality mapping, block sizes, psychoacoustic tables, floor books, floors, and floor mappings.
- Uses `_mapres_template_44_51` from `residue_44p51.h`.
- Sets channel/coupling mode field to `6`, matching 5.1 setup expectations.
- Uses floor mapping count `3`, unlike stereo/uncoupled 44 kHz setup count `2`.

Risk and review signals:
- Static setup data only.
- Inclusion order matters because many 44 kHz symbols are assumed from `setup_44.h`.
- Bitrate mapping is much lower per quality point than stereo because values are setup-selection hints, not total transparent quality guarantees.

Filesystem relevance:
- No filesystem logic. It is surround audio encoder preset data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44p51.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44u.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44u.h

Top-level setup template for 44.1/48 kHz uncoupled Vorbis modes.

Important contents:
- Includes `modes/residue_44u.h`.
- Defines 12-point `rate_mapping_44_un`.
- Defines `ve_setup_44_uncoupled`.

Integration points:
- Reuses shared 44 kHz block sizes, quality mapping, psychoacoustic tables, floor books, floors, and floor mappings.
- Uses `_mapres_template_44_uncoupled`.
- Sets coupling/channel mode field to `-1`, marking uncoupled behavior.

Risk and review signals:
- Static setup data only.
- Inclusion order matters because common 44 kHz symbols are not defined here.
- Uses `_psy_stereo_modes_44` despite uncoupled residue; this appears inherited setup behavior and should be treated cautiously if refactoring.

Filesystem relevance:
- No filesystem logic. It is audio encoder setup data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_44u.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_8.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_8.h

Top-level encoder setup template for 8 kHz Vorbis modes.

Important contents:
- Includes `psych_8.h` and `residue_8.h`.
- Defines fixed block size `{512,512}`.
- Defines one floor mapping selecting floor index 6.
- Defines stereo bitrate mapping `{6000,9000,32000}` and uncoupled mapping `{8000,14000,42000}`.
- Defines quality mapping `{-0.1,0.0,1.0}`.
- Defines `_psy_compand_8_mapping` and `_global_mapping_8`.
- Defines `ve_setup_8_stereo` and `ve_setup_8_uncoupled`.

Integration points:
- Uses 8 kHz psychoacoustic, noise, lowpass, ATH, stereo mode, floor, and residue templates.
- Provides base tables reused by `setup_11.h` and `setup_X.h`.

Risk and review signals:
- Static setup data only.
- Only three quality points and fixed block sizes, so tuning changes are broad.
- Stereo and uncoupled modes differ mainly in rate mapping, coupling field, and residue mapping template.

Filesystem relevance:
- No filesystem logic. It is low-rate audio encoder configuration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_8.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_X.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_X.h

Catch-all quality-only setup templates used when bitrate mapping should be disabled.

Important contents:
- Defines `rate_mapping_X`, a 12-entry array of `-1` values.
- Defines `ve_setup_X_stereo` and `ve_setup_X_uncoupled` using 44 kHz-style setup data and no bitrate hints.
- Defines `ve_setup_XX_stereo` and `ve_setup_XX_uncoupled` using 8 kHz-style setup data and no bitrate hints.

Integration points:
- Reuses 44 kHz symbols for `ve_setup_X_*`.
- Reuses 8 kHz symbols for `ve_setup_XX_*`.
- Intended for quality modes only, as documented in the file header.

Risk and review signals:
- Static setup data only.
- Header inclusion order matters for all referenced 44 kHz and 8 kHz symbols.
- `rate_mapping_X` uses 12 entries even for the 8 kHz setup, which only consumes the first quality-count entries.
- `ve_setup_X_uncoupled` passes `NULL` for stereo modes, while `ve_setup_XX_uncoupled` uses `_psy_stereo_modes_8`.

Filesystem relevance:
- No filesystem logic. It is encoder setup fallback data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/setup_X.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/os.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/os.h

Platform abstraction header for libvorbis math, inline, allocation, and float-to-int helpers.

Important contents:
- Includes optional `config.h`, `<math.h>`, `<ogg/os_types.h>`, and `misc.h`.
- Defines `STIN`, fallback `M_PI`, `FAST_HYPOT`, `min`, and `max`.
- Provides fallback `rint()` definitions for platforms lacking it.
- Handles `alloca`/memory header portability.
- Defines optimized `vorbis_ftoi()` and FPU control helpers for i386 GCC, 32-bit MSVC, and SSE2-capable x86_64.
- Provides a portable fallback `vorbis_ftoi()` using `floor(f+.5)`.

Integration points:
- Included by many libvorbis implementation files: psychoacoustics, scales, FFT, synthesis, codebooks, residue, etc.
- The FPU helpers affect quantization and integer rounding behavior in codec paths.

Risk and review signals:
- Cross-platform code includes Windows, Symbian, DJGPP, GCC inline asm, and SSE2 intrinsics; some paths are irrelevant to Plan 9 builds but retained in vendored code.
- `min`/`max` macros evaluate arguments multiple times.
- FPU rounding behavior can affect bit-exact encoding decisions.

Filesystem relevance:
- No filesystem logic. This is codec portability glue.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/os.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psy.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psy.c

Vorbis psychoacoustic analysis implementation, excluding pre-echo envelope handling.

Important routines:
- `_vp_global_look()` and `_vp_global_free()` allocate/free global psychoacoustic lookups.
- `_vi_gpsy_free()` and `_vi_psy_free()` free setup structures.
- `setup_tone_curves()` builds tone masking curves from ATH and tonemask tables.
- `_vp_psy_init()` initializes per-block psychoacoustic lookups: ATH, Bark windows, octave maps, tone curves, and noise offsets.
- `_vp_psy_clear()` releases lookup allocations.
- `_vp_noisemask()` computes hybrid Bark-domain noise masks with companding.
- `_vp_tonemask()` computes tone masks using seed curves and ATH floor.
- `_vp_offset_and_mix()` combines tone/noise masks and applies AoTuV MDCT compensation.
- `_vp_ampmax_decay()` decays amplitude max over time.
- `_vp_couple_quantize_normalize()` performs noise normalization, quantization, and stereo/multichannel coupling.

Important data:
- `stereo_threshholds` and `stereo_threshholds_limited` drive coupling thresholds.
- `FLOOR1_fromdB_LOOKUP` converts floor dB indexes to linear scale.
- Internal helpers implement seed curve propagation, Bark noise regression, lossless flags, and noise normalization.

Integration points:
- Declared by `psy.h`.
- Used by encoder mapping/floor/residue paths.
- Depends on `masking.h`, `smallft.h`, `scales.h`, `codec_internal.h`, and setup tables.

Risk and review signals:
- Allocation-heavy hot paths use `malloc()` without explicit failure checks.
- Coupling/normalization code is numerically sensitive and affects bitstream quality.
- Several comments document AoTuV tuning behavior; changes need audio regression coverage.
- Static lookup duplicates floor1 dB conversion logic for encode-side coupling.

Filesystem relevance:
- No filesystem logic. This is audio psychoacoustic encode logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psy.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psy.h

Header for Vorbis psychoacoustic setup and lookup structures.

Important contents:
- Defines psychoacoustic constants: `EHMER_MAX`, `P_BANDS`, `P_LEVELS`, `P_NOISECURVES`, and `NOISE_COMPAND_LEVELS`.
- Defines `vorbis_info_psy`, containing block flag, ATH tuning, tone mask settings, noise mask settings, companding, max curve dB, and normalization controls.
- Defines `vorbis_info_psy_global`, containing octave resolution, envelope thresholds, amplitude decay, coupling controls, and sliding lowpass settings.
- Defines `vorbis_look_psy_global` and `vorbis_look_psy` runtime lookup structures.
- Declares psychoacoustic lifecycle, masking, amplitude decay, and coupling/quantization routines.

Integration points:
- Included by `codec_internal.h`, `psy.c`, and encoder paths.
- Depends on `smallft.h`, `backends.h`, and `envelope.h`.
- Couples setup-table data to runtime encoder analysis.

Risk and review signals:
- Raw pointer ownership is manual; callers must pair init/clear functions.
- Constants fix array dimensions used by many static setup tables.
- Struct layout is private to this vendored libvorbis tree but broad within the codec.

Filesystem relevance:
- No filesystem logic. It is audio encoder analysis API/state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psytune.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psytune.c

Dead/reference utility for running PCM audio through psychoacoustic processing without full encoding.

Important contents:
- File comment explicitly says it is dead code retained for documentation/reference and should not be compiled.
- Defines local psychoacoustic setup structures, partition/coupling tuning, floor setup, mapping info, and codec setup.
- `analysis()` optionally writes vectors to MATLAB-style `.m` files.
- `main()` reads a WAV-like stream from stdin, skips/copies a 44-byte header, processes overlapping stereo frames, runs FFT/MDCT, computes psychoacoustic masks, applies floor/residue/coupling analysis, reconstructs samples, and writes PCM-like output.
- Uses historical helper names such as `_vp_compute_mask`, `_vp_remove_floor`, `_vp_partition_prequant`, and `_vp_couple`.

Integration points:
- Includes many libvorbis internals: `codec_internal.h`, `psy.h`, `mdct.h`, `smallft.h`, `window.h`, `lpc.h`, `lsp.h`, `masking.h`, and `registry.h`.
- Useful as a tuning/reference artifact, not as a live build unit.

Risk and review signals:
- Should not be compiled; it likely does not match current interfaces.
- Uses unchecked I/O, `alloca`-style assumptions through codec helpers, and simplified WAV handling.
- Retained constants may document older tuning intent but should not be treated as authoritative runtime behavior.

Filesystem relevance:
- No filesystem implementation. It performs simple stdin/stdout test I/O for audio tuning.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/psytune.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/registry.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/registry.c

Backend registry implementation for Vorbis floor, residue, and mapping backends.

Important contents:
- Declares external backend bundles: `floor0_exportbundle`, `floor1_exportbundle`, `residue0_exportbundle`, `residue1_exportbundle`, `residue2_exportbundle`, and `mapping0_exportbundle`.
- Defines `_floor_P` with floor0 and floor1.
- Defines `_residue_P` with residue0, residue1, and residue2.
- Defines `_mapping_P` with mapping0.

Integration points:
- Used by setup/header parsing and synthesis/analysis dispatch.
- Bounds for these arrays are declared in `registry.h`.
- `info.c`, `synthesis.c`, and backend setup code index these arrays after validating backend IDs.

Risk and review signals:
- Minimal static dispatch table.
- Adding backend types requires synchronized updates to `registry.h` bounds and setup/header validation.
- Incorrect ordering would break bitstream backend IDs.

Filesystem relevance:
- No filesystem logic. It is codec backend dispatch registration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/registry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/registry.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/registry.h

Header declaring Vorbis backend registry bounds and arrays.

Important contents:
- Defines backend-count constants:
  - `VI_TRANSFORMB 1`
  - `VI_WINDOWB 1`
  - `VI_TIMEB 1`
  - `VI_FLOORB 2`
  - `VI_RESB 3`
  - `VI_MAPB 1`
- Declares `_floor_P`, `_residue_P`, and `_mapping_P`.

Integration points:
- Included by setup/header code and backend dispatch users.
- Constants are used to validate backend type numbers during Vorbis setup-header parsing.

Risk and review signals:
- Constants must match actual arrays in `registry.c`.
- Any new backend requires coordinated changes in validation and implementation.

Filesystem relevance:
- No filesystem logic. It is codec backend registry metadata.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/registry.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/res0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/res0.c

Implementation of Vorbis residue backends 0, 1, and 2.

Important routines:
- `res0_free_info()` and `res0_free_look()` release residue setup/lookups.
- `res0_pack()` serializes residue setup fields and second-stage cascades.
- `res0_unpack()` parses residue setup, validates book indexes/maptypes, and checks phrasebook partition geometry.
- `res0_look()` builds runtime partbook pointers and decode maps.
- `local_book_besterror()` selects nearest encode codebook entry for integer vectors.
- `_01class()` and `_2class()` classify residue partitions for type 0/1 and type 2 coding.
- `_01forward()` encodes partition words and residue values.
- `_01inverse()` decodes type 0/1 residue data.
- `res0_inverse()`, `res1_*()`, and `res2_*()` expose backend-specific encode/decode behavior.
- `residue0_exportbundle`, `residue1_exportbundle`, and `residue2_exportbundle` register backend hooks.

Integration points:
- Uses `codebook.c` decode/encode APIs and setup from `codec_internal.h`.
- Called via `_residue_P` registry from mapping backends.
- Training/debug code can emit `.vqd` files when compile-time flags are enabled.

Risk and review signals:
- Decode treats truncated packets as “stop working” and returns success-like `0`, matching libvorbis robustness behavior.
- Setup unpack has important range checks for codebook indexes and phrasebook sizing.
- Several allocation paths do not explicitly handle allocation failure.
- Type 2 interleaves channels into one vector, so channel count and `pcmend` arithmetic are security-sensitive.

Filesystem relevance:
- No filesystem logic. Optional training modes write files, but normal code is audio bitstream residue coding.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/res0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/scales.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/scales.h

Inline scale conversion helpers for Vorbis psychoacoustic and codec math.

Important contents:
- Defines `unitnorm()` using float bit manipulation when `VORBIS_IEEE_FLOAT32` is enabled.
- Defines `todB()` fast dB approximation using IEEE float exponent/mantissa bits.
- Defines fallback `unitnorm()`, `todB()`, and `todB_nn()` for non-IEEE builds.
- Defines `fromdB()`.
- Defines Bark, Mel, and octave conversion macros: `toBARK`, `fromBARK`, `toMEL`, `fromMEL`, `toOC`, and `fromOC`.

Integration points:
- Included by psychoacoustic, floor, LSP, codebook, and tuning utilities.
- Depends on `os.h` for platform details and Ogg integer types.

Risk and review signals:
- Fast `todB()` assumes IEEE 32-bit float layout.
- Macros evaluate arguments directly; avoid side-effect expressions.
- Scale approximations are part of codec tuning behavior and should not be “simplified” casually.

Filesystem relevance:
- No filesystem logic. It is audio/math helper code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/scales.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/sharedbook.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/sharedbook.c

Shared Vorbis codebook helper implementation for codeword generation, float packing, quantization maps, and encode/decode initialization.

Important routines:
- `ov_ilog()` returns integer bit width.
- `_float32_pack()` and `_float32_unpack()` convert Vorbis non-IEEE packed float representation.
- `_make_words()` builds canonical Huffman codewords from length lists, including sparse and single-entry cases.
- `_book_maptype1_quantvals()` computes maptype-1 quantization value count with integer verification.
- `_book_unquantize()` expands maptype 1/2 quant lists into floating value lists.
- `vorbis_staticbook_destroy()` frees heap-allocated static codebooks.
- `vorbis_book_clear()` frees runtime codebook lookup fields.
- `vorbis_book_init_encode()` initializes encode-side codebook fields.
- `vorbis_book_init_decode()` builds sorted bit-reversed decode lookup structures and first-level decode tables.
- `vorbis_book_codeword()` and `vorbis_book_codelen()` expose encode-side codeword metadata.

Integration points:
- Used by `codebook.c`, `info.c`, residue/floor setup, and static book initialization.
- Depends on `codebook.h`, `scales.h`, `ogg/ogg.h`, and `os.h`.

Risk and review signals:
- `_make_words()` rejects overpopulated and most underpopulated Huffman trees; this is security-critical for setup parsing.
- `_float32_pack()` notes it does not guard under/overflow.
- Decode initialization has several heap allocations without explicit failure handling.
- Correctness is bitstream-critical; floating-point changes can affect compatibility.

Filesystem relevance:
- No filesystem logic. It is codec codebook infrastructure.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/sharedbook.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/smallft.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/smallft.c

Small unnormalized real FFT implementation used by Vorbis analysis.

Important routines:
- `drfti1()` and `fdrffti()` factor transform size and build trigonometric/split caches.
- Forward radix helpers: `dradf2()`, `dradf4()`, and `dradfg()`.
- `drftf1()` performs forward real FFT dispatch over factor stages.
- Backward radix helpers: `dradb2()`, `dradb3()`, `dradb4()`, and `dradbg()`.
- `drftb1()` performs backward real FFT dispatch.
- Public API:
  - `drft_forward()`
  - `drft_backward()`
  - `drft_init()`
  - `drft_clear()`

Behavior:
- Derived from OggSquish/NetLib-style FFT code, cut down for Vorbis.
- Supports factorized sizes and uses mixed radix routines.
- Transform packing is documented as FORTRAN-style real FFT packing.

Integration points:
- Declared by `smallft.h`.
- Used by psychoacoustic/envelope analysis and tuning tools.
- Allocates lookup caches using `_ogg_calloc()`.

Risk and review signals:
- Index-heavy numerical code; off-by-one changes are high risk.
- `drft_init()` does not check allocation failure.
- The implementation is unnormalized; callers must handle scaling.
- Input sizes are assumed to be codec-controlled block sizes.

Filesystem relevance:
- No filesystem logic. This is audio transform math.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/smallft.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/smallft.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/smallft.h

Header for the small real FFT implementation.

Important contents:
- Defines `drft_lookup`, containing transform size, trig cache, and split/factor cache.
- Declares:
  - `drft_forward()`
  - `drft_backward()`
  - `drft_init()`
  - `drft_clear()`

Integration points:
- Included by `psy.h`, `psy.c`, `psytune.c`, and other analysis code.
- Depends on `vorbis/codec.h`.

Risk and review signals:
- Lookup owns heap buffers initialized by `drft_init()` and released by `drft_clear()`.
- No inline logic; behavior is in `smallft.c`.

Filesystem relevance:
- No filesystem logic. It is transform API declaration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/smallft.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/synthesis.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/synthesis.c

Single-packet Vorbis PCM synthesis and packet blocksize helper implementation.

Important routines:
- `vorbis_synthesis()` validates decoder state, initializes packet bit reader, checks audio packet flag, reads mode/window flags, allocates block PCM storage, and dispatches mapping inverse.
- `vorbis_synthesis_trackonly()` parses packet mode/window/granule metadata without decoding PCM, useful for fast-forward tracking.
- `vorbis_packet_blocksize()` returns the decoded packet block size after reading the packet mode.
- `vorbis_synthesis_halfrate()` toggles half-rate decode mode if block size permits.
- `vorbis_synthesis_halfrate_p()` reports half-rate state.

Integration points:
- Uses `codec_internal.h`, `registry.h`, and `_mapping_P`.
- Relies on setup-header validation to make mode mapping/type indexes safe.
- Called from public libvorbis decode APIs declared in `vorbis/codec.h`.

Risk and review signals:
- `vorbis_synthesis()` has explicit null-state checks and returns `OV_EBADPACKET` for invalid decoder state.
- `vorbis_synthesis_trackonly()` assumes valid `vb`, `vd`, and backend state more directly than `vorbis_synthesis()`.
- Packet parsing rejects non-audio packets and invalid modes.
- PCM allocation uses block-local allocator.

Filesystem relevance:
- No filesystem logic. It decodes audio packets already supplied by container code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/synthesis.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/tone.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/tone.c

Small standalone tone generator utility.

Important contents:
- Parses command-line arguments as `<frequency_Hz>[,<amplitude>]`.
- Allocates frequency/amplitude arrays with `alloca()`.
- Generates 10 seconds of 44.1 kHz stereo 16-bit little-endian PCM to stdout.
- Sums sine waves, rounds with `rint()`, clips to signed 16-bit range, and writes duplicate left/right samples.
- `usage()` prints syntax and exits.

Integration points:
- Not tied into libvorbis internals; uses only C library math/stdio/string/stdlib.
- Useful for generating simple test tones.

Risk and review signals:
- Uses `alloca()` without including an explicit alloca header in this file.
- Writes raw PCM, not WAV with headers.
- No argument validation beyond `atof()` conversion.
- Long argument lists can consume stack.

Filesystem relevance:
- No filesystem implementation. It writes generated audio bytes to stdout.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/tone.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/codec.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/codec.h

Public libvorbis codec API header adapted for 9front.

Important contents:
- Contains Plan 9 pragma: `#pragma lib "/sys/src/cmd/audio/libvorbis/libvorbis.a$O"`.
- Defines public structs:
  - `vorbis_info`
  - `vorbis_dsp_state`
  - `vorbis_block`
  - `alloc_chain`
  - `vorbis_comment`
- Declares general info/comment/block/DSP lifecycle APIs.
- Declares analysis/encoding packet APIs.
- Declares synthesis/decoding APIs.
- Declares half-rate decode APIs.
- Defines Vorbis error codes such as `OV_EOF`, `OV_HOLE`, `OV_EBADHEADER`, `OV_ENOTAUDIO`, and `OV_EBADPACKET`.

Integration points:
- Included by nearly all libvorbis source files and public consumers.
- Depends on `<ogg/ogg.h>`.
- `codec_setup` and `backend_state` are opaque public pointers to private internal structures.

Risk and review signals:
- This is public API/ABI surface; struct layout changes affect applications.
- Comment query APIs return owned internal pointers.
- Error code values are API-visible compatibility constants.
- Plan 9 pragma is local build integration.

Filesystem relevance:
- No filesystem logic. It is codec public API declaration.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/codec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/vorbisenc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/vorbisenc.h

Public libvorbisenc setup API header for encoder configuration.

Important contents:
- Declares one-step and staged encoder setup APIs:
  - `vorbis_encode_init()`
  - `vorbis_encode_setup_managed()`
  - `vorbis_encode_setup_vbr()`
  - `vorbis_encode_init_vbr()`
  - `vorbis_encode_setup_init()`
  - `vorbis_encode_ctl()`
- Defines deprecated `ovectl_ratemanage_arg`.
- Defines current `ovectl_ratemanage2_arg`.
- Defines `vorbis_encode_ctl()` request codes for bitrate management, lowpass, impulse block bias, and coupling controls.
- Retains deprecated rate-management request codes for compatibility.

Integration points:
- Includes `codec.h`.
- Implemented by libvorbis encoder setup code elsewhere in the tree.
- Applications use it before analysis APIs to populate `vorbis_info`.

Risk and review signals:
- Public API header; request-code values and struct fields are compatibility surface.
- Documentation states valid ranges and sequencing requirements; implementations must enforce them.
- Several comments preserve deprecated API behavior, which should remain stable for old callers.

Filesystem relevance:
- No filesystem logic. It declares audio encoder setup APIs.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/vorbisenc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/vorbisfile.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/vorbisfile.h

Public libvorbisfile convenience API header for stdio/callback-based Ogg Vorbis opening, seeking, and decoding.

Important contents:
- Defines `ov_callbacks` with read, seek, close, and tell function pointers.
- Provides static callback presets unless `OV_EXCLUDE_STATIC_CALLBACKS` is defined:
  - `OV_CALLBACKS_DEFAULT`
  - `OV_CALLBACKS_NOCLOSE`
  - `OV_CALLBACKS_STREAMONLY`
  - `OV_CALLBACKS_STREAMONLY_NOCLOSE`
- Defines ready-state constants `NOTOPEN`, `PARTOPEN`, `OPENED`, `STREAMSET`, and `INITSET`.
- Defines `OggVorbis_File`, holding datasource, seek/index metadata, Ogg sync/stream state, Vorbis info/comment arrays, decode state, tracking counters, and callbacks.
- Declares open/test/clear, bitrate/stream info, raw/PCM/time seeking and telling, info/comment access, float/integer read APIs, crosslap, and half-rate APIs.

Integration points:
- Includes `<stdio.h>` and `codec.h`.
- Wraps Ogg container state plus Vorbis decoder state.
- Callback design allows stdio or custom data sources.

Risk and review signals:
- Static callback objects in a header intentionally create one copy per including translation unit.
- `_ov_header_fseek_wrap()` has platform-specific large-file seek handling.
- `OggVorbis_File` is public ABI and includes overloaded `pcmlengths` for binary compatibility.
- Callback implementations must return stdio-compatible values, especially `-1` for unseekable seek callbacks.

Filesystem relevance:
- Filesystem-adjacent only as an audio file convenience API: it opens/seeks/reads streams through stdio or callbacks, but it is not filesystem implementation code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/vorbis/vorbisfile.h -->