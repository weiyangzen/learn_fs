# Group Research: group_51_9front_sources_os_plan9_9front_sys_src_cmd_audio_libvorbis_codec_inte_5441a0d7fb76

Scope: `Docs/research_subset_a.md`, specifically the bundled 9front `sys/src/cmd/audio/libvorbis` codec internals and mode tables listed in this work item. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/codec_internal.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/codec_internal.h

Internal libvorbis codec state header. It defines private encoder/decoder structures and declares floor1 encode-side helpers shared across backend files.

Important contents:
- Defines block-type constants, `PACKETBLOBS`, and `vorbis_block_internal`, which stores delayed PCM, maximum amplitude, block type, and bitrate-managed packet blobs.
- Defines internal opaque aliases for floor, residue, and transform lookups.
- Defines `vorbis_info_mode`, the packed mode description containing block flag, window type, transform type, and mapping index.
- Defines `private_state`, the runtime codec backend state hanging off `vorbis_dsp_state`: envelope lookup, window cache, MDCT/FFT lookups, floor/residue/psychoacoustic lookups, temporary header packet storage, bitrate manager state, and sample count.
- Defines `codec_setup_info`, the central setup structure containing block sizes, modes, mappings, floor/residue/codebook descriptors, full runtime codebooks, psychoacoustic setup, bitrate manager info, high-level encoder setup, and decode halfrate flag.
- Defines `vorbis_look_floor1`, the floor1 lookup structure used by `floor1.c` and declared encode-side helpers.

Integration points:
- Included widely by libvorbis internals such as `info.c`, `mapping0.c`, `envelope.c`, `floor0.c`, and `floor1.c`.
- `info.c` allocates and clears `codec_setup_info`.
- `block.c` and mapping/floor/residue backends consume `private_state` and setup arrays.
- `floor1_fit()`, `floor1_interpolate_fit()`, and `floor1_encode()` are declared here for encoder use from `mapping0.c`.

Risk and review signals:
- This is a private ABI within the vendored libvorbis tree; field layout changes affect many C files.
- Array sizes are fixed by Vorbis limits: 64 modes/maps/floors/residues, 256 books, and 4 psychoacoustic configs.
- Many pointers are owned elsewhere; cleanup correctness depends on `vorbis_info_clear()` and backend-specific free hooks.

Filesystem relevance:
- No filesystem logic. This is vendored audio codec internal state under 9front audio command sources.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/codec_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/envelope.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/envelope.c

PCM envelope analysis implementation used by the Vorbis encoder to detect pre-echo/post-echo regions and guide block switching.

Important routines:
- `_ve_envelope_init()` initializes a 128-sample MDCT, sine-squared MDCT window, seven fixed envelope bands, per-channel filter state, and mark storage.
- `_ve_envelope_clear()` releases MDCT, band windows, filter state, and mark storage.
- `_ve_amp()` transforms a small PCM window, derives smoothed band amplitudes, tracks near-DC energy, compares recent max/min deltas against psychoacoustic pre/postecho thresholds, and returns trigger flags.
- `_ve_envelope_search()` scans buffered PCM in `searchstep` increments, grows mark storage as needed, updates pre/postecho marks, tracks stretch penalty, and reports whether enough unmarked/marked data exists for block decision.
- `_ve_envelope_mark()` checks whether the current Vorbis block overlaps an envelope trigger.
- `_ve_envelope_shift()` shifts mark/cursor state when PCM history is consumed.

Behavior:
- Uses seven hard-coded analysis bands and short MDCT windows rather than full psychoacoustic masking.
- Maintains a moving near-DC accumulator to avoid low-frequency leakage driving false triggers.
- Marks windows around both rising and falling amplitude deltas, with stretch logic to reduce repeated impulse sensitivity.

Integration points:
- Uses thresholds from `codec_setup_info.psy_g_param`.
- Uses `mdct.c`, `scales.h`, and `envelope.h`.
- Called from encoder block selection paths via `private_state->ve`.

Risk and review signals:
- `_ve_amp()` uses plain `malloc()` per analyzed channel/window and does not check allocation failure.
- Mark storage is dynamically reallocated to match PCM progress; malformed state or incorrect shift values could corrupt envelope timing.
- Trigger behavior is tuning-sensitive and should be regression-tested with impulses, fades, silence, and low-energy noise.

Filesystem relevance:
- No filesystem logic. It is audio encoder analysis code in the 9front libvorbis vendor subtree.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/envelope.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/envelope.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/envelope.h

Header for Vorbis PCM envelope analysis state and operations.

Important contents:
- Defines analysis constants: `VE_PRE`, `VE_WIN`, `VE_POST`, `VE_AMP`, `VE_BANDS`, `VE_NEARDC`, and stretch bounds.
- Defines `envelope_filter_state`, holding per-band amplitude ring buffer and near-DC accumulator state.
- Defines `envelope_band`, holding band begin/end indexes, a weighting window, and normalization total.
- Defines `envelope_lookup`, the full runtime envelope analyzer state: channel count, window/search sizes, MDCT lookup/window, bands, per-channel filters, stretch, mark array, storage size, current offset, current mark, and cursor.
- Declares init, clear, search, shift, and mark functions implemented in `envelope.c`.

Integration points:
- Included by `codec_internal.h` and `envelope.c`.
- Depends on `mdct.h`.

Risk and review signals:
- The structs expose raw pointers and counters; callers must initialize with `_ve_envelope_init()` and clear with `_ve_envelope_clear()`.
- Mark/cursor values are sample-position state and must stay synchronized with PCM buffer shifting.

Filesystem relevance:
- No filesystem logic; this is codec analysis state.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/envelope.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/floor0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/floor0.c

Vorbis floor backend 0 implementation. Floor0 reconstructs a spectral envelope from line spectral pairs decoded from codebooks.

Important routines:
- `floor0_free_info()` and `floor0_free_look()` release floor0 setup and lookup state.
- `floor0_unpack()` reads floor0 setup from an Ogg bitpack buffer: order, rate, Bark map size, amplitude bit fields, amplitude dB range, and codebook list. It validates book indexes and rejects maptype-0 books.
- `floor0_map_lazy_init()` lazily builds linear-frequency to Bark-scale maps per block size.
- `floor0_look()` creates the runtime lookup containing order, Bark map length, and lazy linear maps.
- `floor0_inverse1()` decodes amplitude and LSP vector values from the packet, cumulatively reconstructing LSP coefficients.
- `floor0_inverse2()` maps the LSP envelope to a spectral curve with `vorbis_lsp_to_curve()`, or clears output when no floor is present.
- `floor0_exportbundle` exposes the backend hooks to the registry.

Integration points:
- Uses `lpc.h`, `lsp.h`, `codebook.h`, `scales.h`, and Vorbis backend registry types.
- Called by setup-header unpack through `_floor_P`.
- Decode-time mapping uses `inverse1` and `inverse2` through `mapping0.c`.

Risk and review signals:
- Uses `_vorbis_block_alloc()` for packet-local LSP memory.
- Lazy map initialization assumes `look->linearmap` is valid and block sizes are already validated.
- Floor0 is decode-oriented here; export bundle has no pack hook.

Filesystem relevance:
- No filesystem logic. It is Vorbis audio decode backend code.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/floor0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/floor1.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/floor1.c

Vorbis floor backend 1 implementation, including setup serialization, decode reconstruction, and encoder curve fitting.

Important routines:
- `floor1_pack()` writes partitions, class definitions, subclass books, multiplier, and post list.
- `floor1_unpack()` reads and validates floor1 setup, including class/subbook indexes, post count bounds, and duplicate post positions.
- `floor1_look()` precomputes sorted post indexes, reverse indexes, quantization range, and low/high prediction neighbors.
- `render_point()`, `render_line()`, and `render_line0()` perform integer line interpolation and floor curve rendering.
- `accumulate_fit()`, `fit_line()`, and `inspect_error()` build weighted least-squares fits against log MDCT/masking curves for encoder floor approximation.
- `floor1_fit()` greedily splits floor segments where interpolation exceeds error bounds, producing post values for encoding.
- `floor1_interpolate_fit()` creates intermediate bitrate-managed floor fits.
- `floor1_encode()` quantizes posts, writes prediction residuals through codebooks, and renders an integer mask.
- `floor1_inverse1()` decodes floor post values and unwraps prediction residuals.
- `floor1_inverse2()` renders the decoded floor envelope into the spectral output.
- `floor1_exportbundle` registers pack/unpack/look/free/inverse hooks.

Important data:
- `FLOOR1_fromdB_LOOKUP[256]` converts quantized floor dB values to linear multipliers.
- `lsfit_acc` stores weighted sums for line fitting.

Integration points:
- `mapping0_forward()` directly calls `floor1_fit()`, interpolation, and `floor1_encode()` for encoder work.
- `mapping0_inverse()` calls floor backend hooks to recover envelope curves before MDCT inverse.
- `info.c` uses the backend registry to pack/unpack floor setup.

Risk and review signals:
- Contains an `exit(1)` in `floor1_fit()` if internal fit state reaches an impossible neighbor case; this is hostile in library-style code.
- Many codec bounds are explicitly checked during unpack, especially post counts and codebook indexes.
- Encoder fit quality is tuning-sensitive; tests should cover zero floors, duplicate/invalid postlists, malformed packet EOF, and managed bitrate floor interpolation.
- Decode clamps rendered floor lookup indexes to `[0,255]`.

Filesystem relevance:
- No filesystem logic. This is Vorbis spectral envelope codec logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/floor1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/highlevel.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/highlevel.h

Header defining high-level encoder setup structures used by Vorbis encoder setup code.

Important contents:
- `highlevel_byblocktype` stores per-block-type tone mask, tone peak limit, noise bias, and noise companding settings.
- `highlevel_encode_setup` stores user-facing/derived encoder configuration: selected setup, base quality, impulse noise tuning, managed bitrate parameters, block/noise/coupling toggles, stereo point, lowpass, ATH controls, amplitude tracking, trigger setting, and per-block settings.

Integration points:
- Included by `codec_internal.h`.
- Stored as `codec_setup_info.hi`, primarily for `vorbisenc.c` setup flow.

Risk and review signals:
- Declaration-only header; no runtime logic or validation.
- Values are redundant with expanded codec setup and must be synchronized by encoder setup code.

Filesystem relevance:
- No filesystem logic. It is encoder configuration data modeling.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/highlevel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/info.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/info.c

Vorbis info/comment/header management implementation. It owns public `vorbis_info` lifecycle, Vorbis comment helpers, header packet parsing, and header packet generation.

Important routines:
- Comment API: `vorbis_comment_init()`, `vorbis_comment_add()`, `vorbis_comment_add_tag()`, `vorbis_comment_query()`, `vorbis_comment_query_count()`, and `vorbis_comment_clear()`.
- Info lifecycle: `vorbis_info_init()`, `vorbis_info_clear()`, and `vorbis_info_blocksize()`.
- Header unpacking: `_vorbis_unpack_info()`, `_vorbis_unpack_comment()`, and `_vorbis_unpack_books()` read the three Vorbis header packet types and validate stream structure.
- Header detection: `vorbis_synthesis_idheader()` checks for an initial Vorbis identification header.
- Main header input: `vorbis_synthesis_headerin()` dispatches identification, comment, and setup headers in correct order.
- Header packing: `_vorbis_pack_info()`, `_vorbis_pack_comment()`, `_vorbis_pack_books()`, `vorbis_commentheader_out()`, and `vorbis_analysis_headerout()`.
- Utility: `vorbis_granule_time()` converts granule positions to seconds; `vorbis_version_string()` returns the general vendor string.

Validation behavior:
- Identification header enforces version 0, positive channels/rate, short block size at least 64, long block size not smaller than short, and maximum long block size 8192.
- Comment unpack checks vendor/comment lengths against packet storage before allocating strings.
- Setup unpack validates codebooks, time backend IDs, floor/residue/mapping backend IDs, mode window/transform types, and mapping indexes.
- On malformed setup, `vorbis_info_clear()` is called to release partial allocations.

Integration points:
- Uses `codec_internal.h`, `codebook.h`, `registry.h`, `window.h`, `psy.h`, `misc.h`, and Ogg bitpacking.
- Backend registries `_floor_P`, `_residue_P`, and `_mapping_P` supply pack/unpack/free hooks.
- Encoding header packets are stored in `private_state` fields `header`, `header1`, and `header2`.

Risk and review signals:
- Some allocation paths do not explicitly handle `_ogg_malloc()`/`_ogg_calloc()` failure.
- `vorbis_comment_query()` returns an interior pointer into owned comment storage, not a copy.
- Cleanup depends on backend type arrays being trustworthy after successful range checking; comments note aborted unpack cases.
- Fuzzing should target truncated headers, large comment counts/lengths, invalid backend indexes, repeated setup headers, and invalid packet ordering.

Filesystem relevance:
- No filesystem implementation. This is stream metadata/header parsing for audio packets.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup.c

Lookup-table helper implementation for cosine, inverse-square-root, exponent scaling, and dB-to-linear conversions.

Important routines:
- Under `FLOAT_LOOKUP`:
  - `vorbis_coslook()` interpolates cosine over `[0, PI]`.
  - `vorbis_invsqlook()` interpolates `1/sqrt(p)` for `.5 <= p < 1`.
  - `vorbis_invsq2explook()` returns exponent correction values.
  - `vorbis_fromdBlook()` converts dB values in roughly `[-140, 0]` to linear multipliers.
- Under `INT_LOOKUP`:
  - `vorbis_invsqlook_i()` performs fixed/integer-style inverse-square-root scaling.
  - `vorbis_fromdBlook_i()` converts fixed-format dB to linear float.
  - `vorbis_coslook_i()` returns fixed-format cosine.

Integration points:
- Uses generated tables from `lookup_data.h`.
- `lsp.c` can include `lookup.c` directly when optimized lookup modes are enabled, though this local build undefines those modes in `lsp.c`.

Risk and review signals:
- Functions assume inputs are in documented domains; out-of-domain indexes can overrun lookup arrays.
- Conditional compilation means active symbols depend on `FLOAT_LOOKUP`/`INT_LOOKUP`.
- `vorbis_fromdBlook()` clamps outside-table values to `1.f` or `0.f`.

Filesystem relevance:
- No filesystem logic. This is numeric support for codec math.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup.h

Declaration header for optional lookup-table math helpers.

Important contents:
- Declares float lookup helpers when `FLOAT_LOOKUP` is defined.
- Declares integer lookup helpers when `INT_LOOKUP` is defined.

Integration points:
- Included by `lookup.c` and `lsp.c`.

Risk and review signals:
- The header has `#ifndef _V_LOOKUP_H_` but does not define `_V_LOOKUP_H_`, so it does not actually prevent repeated inclusion.
- No implementation is present; available declarations depend entirely on compile-time lookup mode macros.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup_data.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup_data.h

Generated static lookup table header produced by `lookups.pl`.

Important contents:
- Under `FLOAT_LOOKUP`, defines:
  - `COS_LOOKUP` with 129 cosine samples.
  - `INVSQ_LOOKUP` with 33 inverse-square-root samples.
  - `INVSQ2EXP_LOOKUP` for exponent correction from -32 to 32.
  - `FROMdB_LOOKUP` and `FROMdB2_LOOKUP` for dB conversion.
- Under `INT_LOOKUP`, defines:
  - `INVSQ_LOOKUP_I` fixed-point inverse-square-root table.
  - `COS_LOOKUP_I` fixed-point cosine table.
- Also defines shared dB lookup sizes/shifts/masks.

Integration points:
- Included by `lookup.c`.
- Generated by `lookups.pl`; comments say to edit the generator rather than this file.

Risk and review signals:
- Like `lookup.h`, it has an `#ifndef _V_LOOKUP_DATA_H_` without a matching `#define`, so repeated inclusion is not guarded.
- The tables are compile-time constants and depend on exact macro definitions used by interpolation code.
- Out-of-range callers in `lookup.c` can index beyond these tables unless they clamp first.

Filesystem relevance:
- No filesystem logic. It is generated numeric codec data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookup_data.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookups.pl -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookups.pl

Perl generator for `lookup_data.h`.

Important behavior:
- Prints the libvorbis lookup-data header prologue.
- Generates float cosine, inverse-square-root, exponent, and dB conversion tables.
- Generates integer inverse-square-root and cosine tables for `INT_LOOKUP`.
- Uses fixed table sizes and shifts matching `lookup.c`: cosine size 128, inverse-square-root size 32, exponent range -32..32, dB table sizes/shifts, integer lookup shifts 10 and 9.

Integration points:
- Source of truth for generated lookup tables in `lookup_data.h`.
- Not used at runtime.

Risk and review signals:
- Generated header from this script differs slightly from the checked-in header style, including older copyright text and non-`const` declarations in the generator output.
- The generated guard also lacks a `#define`, matching the checked-in file’s ineffective guard.
- Re-running the script could cause formatting and constness churn.

Filesystem relevance:
- No filesystem logic. It is a build-time/codegen helper for audio math tables.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lookups.pl -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lpc.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lpc.c

Low-level LPC routines for linear predictive coding support.

Important routines:
- `vorbis_lpc_from_data()` computes autocorrelation coefficients from time-domain data, runs Levinson-Durbin recursion to derive LPC coefficients, applies slight damping, writes float coefficients, and returns residual/error energy.
- `vorbis_lpc_predict()` predicts output samples from LPC coefficients and optional prime history.

Implementation notes:
- Autocorrelation and LPC coefficient accumulation use `double` for depth.
- The LPC error floor uses an epsilon based on signal energy.
- The code preserves separate Degener/Bormann copyright notice for derived autocorrelation/LPC logic.

Integration points:
- Declared in `lpc.h`.
- Included by floor and mapping code; floor0 uses LPC/LSP concepts for spectral envelope work.

Risk and review signals:
- Uses plain `malloc()` for temporary arrays and does not check allocation failure.
- `vorbis_lpc_predict()` allocates `m+n` samples for work storage.
- Input sizes/order must be sensible; no defensive validation is performed in these helpers.

Filesystem relevance:
- No filesystem logic. This is audio signal-processing math.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lpc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lpc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lpc.h

Declaration header for low-level LPC helpers.

Important contents:
- Declares `vorbis_lpc_from_data()` for LPC coefficient estimation.
- Declares `vorbis_lpc_predict()` for sample prediction from coefficients.
- Includes `vorbis/codec.h`.

Integration points:
- Used by `lpc.c`, `floor0.c`, and `mapping0.c`.

Risk and review signals:
- Header only; callers must satisfy buffer and length requirements expected by `lpc.c`.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lpc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lsp.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lsp.c

LSP/LSF conversion implementation used for Vorbis floor0 spectral envelope reconstruction and LPC-to-LSP conversion.

Important routines:
- `vorbis_lsp_to_curve()` converts LSP values into a spectral floor curve. In this file both `FLOAT_LOOKUP` and `INT_LOOKUP` are explicitly undefined, so the active implementation is the simple non-optimized floating-point path.
- `cheby()` converts polynomial coefficients to Chebyshev form.
- `Laguerre_With_Deflation()` finds real roots with Laguerre iteration and deflation.
- `Newton_Raphson()` polishes roots after Laguerre.
- `vorbis_lpc_to_lsp()` converts LPC coefficients into LSP coefficients by forming symmetric/antisymmetric polynomials, finding roots, sorting them, and applying `acos()`.

Inactive code:
- Optimized float lookup and integer lookup implementations of `vorbis_lsp_to_curve()` are present under disabled macros and can include `lookup.c` directly.

Integration points:
- Declared in `lsp.h`.
- `floor0.c` calls `vorbis_lsp_to_curve()`.
- Uses `lookup.h` only for disabled optimized paths.

Risk and review signals:
- Several temporary arrays use plain `malloc()` without allocation checks.
- `Laguerre_With_Deflation()` mutates the `defl` pointer before calling `free(defl)`, which is suspicious because freeing an advanced pointer would be invalid if executed after pointer increment. This should be reviewed carefully.
- Root-finding failure returns `-1` for bad/complex roots, and `vorbis_lpc_to_lsp()` propagates failure.
- `vorbis_lsp_to_curve()` mutates the input `lsp` array as a documented side effect.

Filesystem relevance:
- No filesystem logic. It is audio codec math.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lsp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lsp.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lsp.h

Declaration header for LSP/LSF conversion routines.

Important contents:
- Declares `vorbis_lpc_to_lsp()`.
- Declares `vorbis_lsp_to_curve()`.

Integration points:
- Used by `lsp.c` and `floor0.c`.

Risk and review signals:
- Header only; callers must account for `vorbis_lsp_to_curve()` modifying the LSP input buffer.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/lsp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mapping0.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mapping0.c

Vorbis channel mapping backend 0 implementation. It wires floor, residue, psychoacoustic analysis, coupling, quantization, and MDCT together for encode and decode.

Important routines:
- `mapping0_free_info()` releases mapping setup.
- `mapping0_pack()` writes submapping, coupling, channel mux, floor submap, and residue submap setup fields.
- `mapping0_unpack()` reads and validates mapping setup, including channel count, coupling pairs, reserved bits, submap indexes, floor indexes, and residue indexes.
- `mapping0_forward()` is the main encode path:
  - windows PCM,
  - runs MDCT and FFT,
  - computes log spectral data,
  - builds noise and tone masks,
  - fits floor1 curves,
  - creates bitrate-managed floor variants across `PACKETBLOBS`,
  - writes packet mode/window flags,
  - encodes floors,
  - performs psychoacoustic coupling/quantization/normalization,
  - classifies and encodes residue by submap.
- `mapping0_inverse()` is the main decode path:
  - decodes floor memo per channel,
  - marks nonzero channels,
  - decodes residue bundles,
  - reverses channel coupling,
  - applies floor curves,
  - runs inverse MDCT.
- `mapping0_exportbundle` registers pack/unpack/free/forward/inverse hooks.

Integration points:
- Uses `codec_internal.h`, `window.h`, `registry.h`, `psy.h`, `mdct.h`, `envelope.h`, `lpc.h`, `lsp.h`, and `scales.h`.
- Directly assumes encode-side floor backend is floor1; it returns `-1` if configured floor type is not 1.
- Calls residue backend class/forward/inverse hooks from `_residue_P`.

Risk and review signals:
- Allocates several temporary arrays with plain `malloc()` and no allocation checks.
- Encode mode selection uses `int modenumber=vb->W`, assuming setup mode ordering matches short/long block choice.
- Coupling decode mutates channel spectral vectors in reverse coupling order and depends on validated coupling pairs.
- The disabled analysis block contains a duplicate floor dB table for debugging only.
- Good tests should include mono/stereo/multichannel mappings, coupling edge cases, zero floor channels, managed bitrate blobs, and malformed mapping headers.

Filesystem relevance:
- No filesystem logic. It is the central Vorbis audio packet mapping backend.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mapping0.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/masking.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/masking.h

Static psychoacoustic masking data for Vorbis tone and absolute-threshold calculations.

Important contents:
- Defines `MAX_ATH` and `ATH[]`, a detailed absolute threshold of hearing table.
- Defines `EHMER_OFFSET`, `EHMER_MAX`, and a large `tonemasks[P_BANDS][6][EHMER_MAX]` table.
- Tone mask data covers frequency bands from low bass through 16 kHz, with masking curves for multiple tone levels and offsets.
- Uses `-999` sentinel-style values for inactive/out-of-range curve regions.

Integration points:
- Included by psychoacoustic code, not directly by the files in this group.
- Depends on `P_BANDS` and related psychoacoustic types/macros from `psy.h`.

Risk and review signals:
- This is calibration data; changes affect encoder quality and bitrate behavior, not parser safety.
- Table dimensions must remain consistent with psychoacoustic code expectations.
- No executable logic is present.

Filesystem relevance:
- No filesystem logic. It is static audio psychoacoustic tuning data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/masking.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mdct.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mdct.c

Normalized modified discrete cosine transform implementation for Vorbis power-of-two block sizes.

Important routines:
- `mdct_init()` allocates trigonometric and bit-reversal lookup tables, computes log2 block size, and stores scaling.
- `mdct_clear()` releases lookup allocations.
- Internal butterfly routines implement 8-, 16-, 32-, first-stage, and generic-stage MDCT butterflies.
- `mdct_bitreverse()` performs bit-reversal and final pre/post rotations.
- `mdct_backward()` runs inverse MDCT from spectral input to time-domain output.
- `mdct_forward()` runs forward MDCT from time-domain input to spectral output, using temporary work storage.

Implementation notes:
- Supports optional integerized transform through macros in `mdct.h`, but default is float.
- The module intentionally excludes window generation/application; callers handle windowing.
- Forward transform allocates a full-size temporary work buffer per call.

Integration points:
- Used by `envelope.c` for short envelope MDCT.
- Used by `mapping0.c` for encode/decode transform.
- Lookup objects are stored in `private_state->transform` and `envelope_lookup.mdct`.

Risk and review signals:
- `mdct_init()` and `mdct_forward()` use allocation without checking failure.
- Assumes power-of-two length at least 64 as validated by Vorbis header/setup paths.
- Transform correctness is sensitive to lookup generation, bit reversal, and block size.

Filesystem relevance:
- No filesystem logic. It is audio transform math.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mdct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mdct.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mdct.h

Header for MDCT lookup state and transform prototypes.

Important contents:
- Optional `MDCT_INTEGERIZED` macro branch defines integer data types, trig constants, conversion, multiply-normalization, and halving macros.
- Default branch defines float data/register types and float constants.
- Defines `mdct_lookup` with block size, log2 size, trig table, bit-reversal table, and scale.
- Declares `mdct_init()`, `mdct_clear()`, `mdct_forward()`, and `mdct_backward()`.

Integration points:
- Included by `mdct.c`, `envelope.h`, and transform users.

Risk and review signals:
- Integerized path is commented as potentially rough/noisy and is disabled by default.
- Header exposes implementation macros that affect ABI/behavior of `mdct_lookup`.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/mdct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/misc.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/misc.h

Miscellaneous internal declarations and debug allocation macro overrides.

Important contents:
- Declares `_vorbis_block_alloc()` and `_vorbis_block_ripcord()` for per-block scratch allocation.
- Declares `ov_ilog()` for integer bit-width calculation.
- Under `ANALYSIS`, declares analysis output helpers.
- Under `DEBUG_MALLOC`, declares debug allocation/free hooks and redefines `_ogg_malloc`, `_ogg_calloc`, `_ogg_realloc`, and `_ogg_free` unless building `misc.c`.

Integration points:
- Included by many libvorbis internals for block allocation, bit utility, and debug allocation support.

Risk and review signals:
- Debug macro replacement affects allocation call sites globally in translation units including this header.
- Header name guard is `_V_RANDOM_H_`, which is semantically odd for a miscellaneous header but still functions as a guard.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/misc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/floor_all.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/floor_all.h

Static floor1 setup presets and floor codebook lists used by Vorbis encoder modes.

Important contents:
- Includes public codec types, backend types, and generated floor codebooks.
- Defines arrays of floor codebook pointers for multiple floor geometries: `128x4`, `256x4`, `128x7`, `256x7`, `128x11`, `128x17`, `256x4low`, `1024x27`, `2048x27`, `512x17`, and LFE `Xx0`.
- Defines `_floor_books[11]`, mapping floor preset index to its book pointer array.
- Defines `_floor[11]`, an array of `vorbis_info_floor1` structures specifying partitions, classes, dimensions, subclasses, subbooks, multiplier, post lists, and fit/error parameters.

Integration points:
- Used by encoder setup code to instantiate floor backends for different sample-rate/quality modes.
- Depends on generated Huffman books from `books/floor/floor_books.h`.

Risk and review signals:
- Static table only; no runtime validation here.
- Post lists and class/subbook references must remain consistent with corresponding codebook arrays.
- LFE floor preset has only edge posts and no books.

Filesystem relevance:
- No filesystem logic. It is static Vorbis encoder setup data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/floor_all.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_11.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_11.h

Static psychoacoustic tuning tables for 11 kHz Vorbis encoding modes.

Important contents:
- `_psy_lowpass_11[3]` defines lowpass targets.
- `_psy_tone_masteratt_11[3]` defines tone master attenuation.
- `_vp_tonemask_adj_11[3]` defines tone-mask adjustment blocks.
- `_psy_noisebias_11[3]` defines low/mid/high noise bias curves across frequency bands.
- `_noise_thresh_11[3]` defines noise thresholds.

Integration points:
- Included by encoder mode setup code for low-sample-rate configurations.
- Uses types such as `att3`, `vp_adjblock`, and `noise3` from the mode/psychoacoustic setup headers.

Risk and review signals:
- Table-only file; changes affect encoder quality and bitrate allocation.
- Several high-frequency entries use `99` sentinel-style values because 11 kHz mode cannot use full 16 kHz-band tuning.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_11.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_16.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_16.h

Static psychoacoustic tuning tables for 16 kHz Vorbis encoding modes.

Important contents:
- `_psy_stereo_modes_16[4]` defines stereo coupling behavior by base quality.
- `_psy_lowpass_16[4]` defines lowpass targets.
- `_psy_tone_masteratt_16[4]` and `_vp_tonemask_adj_16[4]` define tone masking controls.
- `_psy_noisebias_16_short[4]`, `_psy_noisebias_16_impulse[4]`, and `_psy_noisebias_16[4]` define block-type-specific noise bias curves.
- `_psy_noiseguards_16[4]` defines noise guard parameters.
- `_noise_thresh_16[4]`, `_noise_start_16`, `_noise_part_16`, `_psy_ath_floater_16`, and `_psy_ath_abs_16` define noise normalization and ATH controls.

Integration points:
- Used by encoder setup paths targeting 16 kHz and nearby low-rate audio.

Risk and review signals:
- Static tuning only; no executable logic.
- Arrays have different lengths by purpose, so setup code must index with the correct mode family.
- `9999`/`99` values act as disabled/out-of-range sentinels.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_16.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_44.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_44.h

Large static psychoacoustic tuning header for 44.1/48 kHz Vorbis encoding.

Important contents:
- `_psy_global_44[5]` defines global preecho trigger settings, postecho thresholds, stretch penalty, and minimum energy for quality tiers.
- `_psy_compand_44[6]` defines noise compander lookup blocks for short/long and low/mid/high quality modes.
- `_vp_tonemask_adj_longblock[12]` and `_vp_tonemask_adj_otherblock[12]` define tonal masking adjustment curves.
- `_psy_noisebias_trans[12]`, `_psy_noisebias_long[12]`, `_psy_noisebias_impulse[12]`, and `_psy_noisebias_padding[12]` define noise bias curves by block type and quality.
- `_psy_noiseguards_44[4]`, `_psy_tone_suppress[12]`, `_psy_tone_0dB[12]`, and `_psy_noise_suppress[12]` define guard/suppression behavior.
- `_psy_info_template` provides a default `vorbis_info_psy` structure.
- `_psy_ath_floater[12]` and `_psy_ath_abs[12]` define ATH tuning.
- `_psy_stereo_modes_44[12]` maps quality tiers to stereo coupling points.
- `_psy_tone_masteratt_44[12]`, `_psy_lowpass_44[12]`, noise start/partition arrays, and noise thresholds define high-level quality-dependent tuning.

Integration points:
- Consumed by encoder mode setup code for full-band 44.1/48 kHz presets.
- Values influence `mapping0_forward()` indirectly through psychoacoustic lookups and global settings.

Risk and review signals:
- Static tuning dominates encoder quality; changes require audio regression tests, not just compile tests.
- Contains historical commented-out alternative tunings and sentinel values such as `99` and `9999`.
- There are visually suspicious initializer fragments like `-7  -3` without a comma in some adjustment blocks; this is valid C tokenization as arithmetic subtraction but should be treated carefully if editing.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_44.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_8.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_8.h

Static psychoacoustic tuning tables for 8 kHz Vorbis encoding.

Important contents:
- `_psy_tone_masteratt_8[3]` and `_vp_tonemask_adj_8[3]` define tone masking controls.
- `_psy_noisebias_8[3]` defines noise bias curves.
- `_psy_stereo_modes_8[3]` defines low-sample-rate stereo coupling behavior.
- `_psy_noiseguards_8[2]` defines noise guard parameters.
- `_psy_compand_8[2]` defines companding tables.
- `_psy_lowpass_8[3]`, `_noise_start_8`, `_noise_part_8`, `_psy_ath_floater_8`, and `_psy_ath_abs_8` define lowpass, noise normalization, and ATH controls.

Integration points:
- Used by encoder mode setup for 8 kHz audio.

Risk and review signals:
- Static table-only file.
- High frequency bands use `99` sentinels because 8 kHz audio has limited bandwidth.
- Array lengths differ by category, so setup code must use correct indexes.

Filesystem relevance:
- No filesystem logic.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/psych_8.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_16.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_16.h

Static residue backend templates for 16/22 kHz Vorbis modes.

Important contents:
- Defines stereo residue book blocks `_resbook_16s_0`, `_resbook_16s_1`, and `_resbook_16s_2`.
- Defines stereo residue templates `_res_16s_0`, `_res_16s_1`, and `_res_16s_2`, referencing residue type/config presets, phrase books, and partition books.
- Defines `_mapres_template_16_stereo[3]`, tying nominal mapping templates to the stereo residue templates.
- Defines uncoupled residue book blocks `_resbook_16u_0`, `_resbook_16u_1`, and `_resbook_16u_2`.
- Defines uncoupled residue templates `_res_16u_0`, `_res_16u_1`, and `_res_16u_2`.
- Defines `_mapres_template_16_uncoupled[3]`.

Integration points:
- Consumed by encoder setup code for 16/22 kHz residue/mapping selection.
- References generated codebooks such as `_16c*_...` and `_16u*_...`, plus residue presets like `_residue_44_mid` and mapping presets like `_map_nominal`.

Risk and review signals:
- Static setup only; correctness depends on all referenced generated books and residue presets existing and matching expected dimensions.
- Template type values select coupled vs uncoupled residue behavior, so accidental edits can alter stereo coding behavior.

Filesystem relevance:
- No filesystem logic. It is static Vorbis residue encoding setup data.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/modes/residue_16.h -->