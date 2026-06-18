# subset-b-001381 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/calcs_logger.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/calcs_logger.h

Purpose: provides debug-only bandwidth-calculation tracing helpers for the AMD display core DCE bandwidth model. The header defines static logging functions that dump the contents of `struct bw_calcs_dceip`, `struct bw_calcs_vbios`, and `struct bw_calcs_data` through `DC_LOG_BANDWIDTH_CALCS`, giving developers a full snapshot of hardware capability inputs, VBIOS clock/timing inputs, and intermediate/final bandwidth model state.

Important APIs and functions: `print_bw_calcs_dceip(struct dc_context *ctx, const struct bw_calcs_dceip *dceip)` logs feature flags, pipe counts, DMIF/LB sizes, request limits, scaler efficiencies, and timing constants from the DCE IP description. `print_bw_calcs_vbios(struct dc_context *ctx, const struct bw_calcs_vbios *vbios)` logs memory type, channel topology, SCLK/YCLK/DISPCLK/PHYCLK levels, latency values, scatter-gather enablement, cursor width, compression rate, and blackout timing. `print_bw_calcs_data(struct dc_context *ctx, struct bw_calcs_data *data)` logs the live calculation state, including display counts, tiling and underlay modes, clock levels, scaler ratios, source dimensions, request counts, bandwidth totals, watermarks, stutter metrics, and multidimensional per-surface transfer-time arrays.

Control flow: there is no decision-making beyond sequential logging and fixed-size loops. `print_bw_calcs_data()` first logs scalar fields, then iterates `maximum_number_of_surfaces` for per-pipe arrays, iterates `[maximum_number_of_surfaces][3][8]` for line source transfer timings, iterates `[3][8]` for margin/burst tables, and finally logs six urgent-latency SCLK entries. The only known caller is `dce_calcs.c`, where the three print functions are called when `ctx->dc->debug.bandwidth_calcs_trace` is enabled before `calculate_bandwidth()` runs.

State and persistence: the functions are read-only with respect to the bandwidth structures. Their only side effect is logging through `ctx->logger` via the local `DC_LOGGER` macro. Because the functions are `static` in a header, every translation unit that includes this header gets private copies; currently it is included by the DCE bandwidth calculation implementation. No data is cached or persisted.

Dependencies and integration points: depends on AMD display logging macros, `struct dc_context`, the DCE bandwidth model types, `maximum_number_of_surfaces`, and `bw_fixed_to_int()` from the DCE fixed-point bandwidth arithmetic layer. It is tightly coupled to the exact field layout of `bw_calcs_dceip`, `bw_calcs_vbios`, and `bw_calcs_data`; adding or removing fields in those structures requires updating this header manually if trace completeness matters.

Risks: trace output converts `bw_fixed` values with `bw_fixed_to_int()`, so fractional precision is lost and subtle fixed-point errors may not be visible. The logger has no null checks for `ctx`, `ctx->logger`, or structure pointers, relying on the debug caller to pass valid initialized objects. Because many fields and nested arrays are logged, enabling `bandwidth_calcs_trace` can produce large logs and affect timing-sensitive debugging. The duplicate `memory_type` line in the VBIOS dump is harmless but noisy. Format specifiers are mostly `%d` even for unsigned values, which can make large values appear signed in logs.

Test signals: enable `ctx->dc->debug.bandwidth_calcs_trace` on a DCE path and verify that DCE IP, VBIOS, and data sections appear before bandwidth calculation. Useful validation includes checking that array loop bounds match `bw_calcs_data` array sizes, that new bandwidth fields are represented in logs, that logging does not trigger format warnings, and that trace output remains bounded enough for kernel logs under multi-display configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/calcs_logger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/conversion.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/conversion.c

Purpose: implements small fixed-point conversion helpers used by AMD display color and timing programming paths. Its central job is converting between display core `fixed31_32` arithmetic values and compact hardware register encodings, especially the signed S2D13 matrix format used for color matrices, plus reducing integer ratios.

Important APIs and functions: `fixed_point_to_int_frac()` converts a signed `fixed31_32` value into a packed integer/fraction register representation parameterized by integer and fractional bit counts. `convert_float_matrix()` clamps each matrix entry to the S2D13 range and serializes it to a `uint16_t` register value. `convert_hw_matrix()` converts S2D13 register values back into `fixed31_32` entries using the private `int_frac_to_fixed_point()`. `reduce_fraction()` divides a numerator and denominator by their greatest common divisor found by private `find_gcd()`.

Control flow: `fixed_point_to_int_frac()` floors the absolute integer portion to decide whether the input fits, rounds `arg * 2^fractional_bits` when it does, otherwise saturates to just below `2^integer_bits`, then encodes negative values in the sign bit/value field expected by hardware. `convert_float_matrix()` constructs fixed-point min/max constants for S2D13, clamps every input entry, converts with two integer bits and thirteen fractional bits, and writes the register array. `convert_hw_matrix()` loops over the register array and reconstructs sign and magnitude. `reduce_fraction()` runs Euclid's algorithm and writes reduced outputs.

State and persistence: no persistent state is stored. All helpers are pure transformations except for writes to caller-provided output arrays or output numerator/denominator pointers. They assume callers pass buffers sized for `buffer_size` elements and valid output pointers.

Dependencies and integration points: includes `dm_services.h` and `basics/conversion.h`, and relies on `include/fixed31_32.h` operations such as `dc_fixpt_floor`, `dc_fixpt_round`, `dc_fixpt_mul_int`, `dc_fixpt_clamp`, `dc_fixpt_from_fraction`, `dc_fixpt_recip`, `dc_fixpt_abs`, and `dc_fixpt_neg`. Consumers include DPP, MPC, DWB, and DCE transform color-management code that programs CSC, gamut remap, and temperature matrices. `dc_common.c` also uses `fixed_point_to_int_frac()` for bias/scale register values, and `dc_dmub_srv.c` uses `reduce_fraction()` for SubVP scaling ratios.

Risks: `reduce_fraction()` does not guard `den == 0` or the `num == 0 && den == 0` case; a zero GCD would cause division by zero. `fixed_point_to_int_frac()` uses `1 << (integer_bits + fractional_bits + 1)` and sign-bit shifts into a `uint16_t`, so callers must keep bit counts within the 16-bit register format. The S2D13 comment says `[-3.00...0.9999]`, while the code clamps from `-3` to `+3`; this deserves hardware-spec confirmation. Rounding/saturation behavior affects color accuracy, so small changes can create visible color differences.

Test signals: unit-level tests should cover zero, positive, negative, maximum in-range, out-of-range, and fractional rounding cases for S2D13 conversion. Round-trip tests through `convert_float_matrix()` and `convert_hw_matrix()` should allow expected quantization loss. Ratio tests should cover common reductions and explicitly validate caller behavior when denominator is zero. Integration signals include correct CSC/gamut register programming on DPP/MPC/DWB paths and absence of color regressions after matrix updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/conversion.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/conversion.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/conversion.h

Purpose: declares the display core conversion helper API for fixed-point-to-register packing, matrix conversion, ratio reduction, and integer log2. It is the public contract consumed by color management, hardware sequencing, DMUB support, and other display modules that need consistent fixed-point register encodings.

Important APIs and types: exposes `fixed_point_to_int_frac()`, `convert_float_matrix()`, `convert_hw_matrix()`, and `reduce_fraction()` from `conversion.c`. It also provides `static inline unsigned int log_2(unsigned int num)`, a thin wrapper around the kernel `ilog2()` helper. The API is based on `struct fixed31_32` from `include/fixed31_32.h` and standard integer types.

Control flow: the header itself has no runtime state or complex flow. It provides prototypes and one inline forwarding function. The conversion functions operate on caller-provided buffers and are expected to be linked from `conversion.c`.

State and persistence: no state is declared. The functions are stateless utilities; persistence and lifetime are entirely owned by the caller's input/output arrays and scalar pointers.

Dependencies and integration points: depends on `include/fixed31_32.h` and on the kernel environment providing `ilog2()`. It is included by display color-programming modules such as DPP, MPC, DWB, DCE transform, `dc_common.c`, and DMUB service code. Because it centralizes S2D13 and related packing behavior, changes to prototypes or semantics have broad display-pipeline impact.

Risks: the header does not document valid ranges for `integer_bits`, `fractional_bits`, buffer mutability, or denominator constraints for `reduce_fraction()`, so incorrect callers can trigger overflow, truncation, or divide-by-zero in the implementation. `log_2()` inherits `ilog2()` assumptions; callers must avoid passing zero unless their platform definition explicitly handles it.

Test signals: compile coverage should include every caller that includes the header to catch signature drift. Behavioral tests should target the implementation, while API-level checks should verify that all matrix conversion callers pass the expected S2D13 buffer lengths and that `log_2()` is never invoked with invalid zero input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/conversion.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/custom_float.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/custom_float.c

Purpose: converts `fixed31_32` values into AMD display hardware custom floating-point bitfields. The helper is used by color-management and hardware sequencing code to encode piecewise-linear gamma, shaper, multiplier, and scale values for DCE/DCN registers with configurable mantissa, exponent, and optional sign bits.

Important APIs and functions: the exported `convert_to_custom_float_format(struct fixed31_32 value, const struct custom_float_format *format, uint32_t *result)` orchestrates conversion. Private `build_custom_float()` normalizes the fixed-point value, determines sign, biased exponent, and mantissa. Private `setup_custom_float()` packs mantissa bits, exponent bits, and optional sign into a `uint32_t` result and contains debug-range checks.

Control flow: zero input returns exponent and mantissa zero. Negative input is made positive for magnitude processing and only preserves a negative output if `format->sign` allows it. Values below one are shifted left until normalized; underflow below the exponent bias returns zero. Larger values are shifted right until they fit below the maximum representable mantissa-plus-fraction threshold, then assigned a biased exponent. The mantissa is calculated as `(normalized_value - 1) << mantissa_bits`, floored, and packed into low bits. Exponent bits are packed above the mantissa, and sign is packed above exponent when enabled.

State and persistence: the conversion has no persistent state. It writes a single caller-provided `uint32_t` result and returns `true` for all normal code paths. Debug side effects are limited to `BREAK_TO_DEBUGGER()` when `setup_custom_float()` detects mantissa or exponent bits outside local masks, after which values are clamped to those masks.

Dependencies and integration points: includes `dm_services.h` and `custom_float.h`; the public header lives under `dc/inc` and brings in `bw_fixed.h`, `hw_shared.h`, and `opp.h`, where `struct custom_float_format` is defined. Integration points include DCE110 and DCN10/DCN30/DCN401 color management helpers, DPP/MPC shaper programming, and hardware sequencing multiplier/scale programming. A related SPL namespaced implementation exists under `dc/sspl`, so semantic drift between the two implementations is a maintenance risk.

Risks: the masks in `setup_custom_float()` use `(1 << (bits + 1)) - 1`, which appears wider than the actual loops that pack exactly `mantissa_bits` and `exponenta_bits`; this may hide one-bit overflow in debug checks. The code does not reject invalid `format` values such as zero bit widths or shifts >= 32. Negative values with `format->sign == false` are converted as positive magnitude with no failure, which is acceptable for unsigned hardware formats only if callers prevalidate their domains. The function currently always returns true, so callers that check failure paths mostly protect against future changes rather than current runtime failures.

Test signals: cover zero, underflow, values below one, exactly one, values near mantissa saturation, large values requiring exponent shifts, negative signed formats, and negative unsigned formats. Compare packed bitfields against hardware register specifications for the 6-exponent/12-mantissa formats used by DCN color helpers. Integration tests should validate gamma/shaper programming and any hardware-sequencer multiplier values that rely on this packing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/custom_float.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/dc_common.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/dc_common.c

Purpose: implements small shared display-core helpers for color-space classification, pipe-tree visibility checks, and bias/scale register preparation. These helpers support hardware sequencing decisions in DCN/DCE paths without tying those call sites to repeated switch statements or recursive pipe traversal logic.

Important APIs and functions: `is_rgb_cspace(enum dc_color_space output_color_space)` returns whether an output color space is RGB rather than YCbCr. `is_lower_pipe_tree_visible()`, `is_upper_pipe_tree_visible()`, and `is_pipe_tree_visible()` recursively inspect connected `pipe_ctx` nodes for a visible plane. `build_prescale_params()` fills `struct dc_bias_and_scale` scale values for a plane before DPP programming.

Control flow: `is_rgb_cspace()` uses a switch over known RGB and YCbCr enum values, breaks to debugger on unknown values, and returns false by default. The pipe visibility helpers check the current pipe's `plane_state->visible`, then recurse downward through `bottom_pipe`, upward through `top_pipe`, or both depending on the entry point. `build_prescale_params()` applies coefficient reduction only for valid video formats with input CSC adjustment enabled and a nonzero `coeff_reduction_factor`; it multiplies that factor by `256/255`, packs it with `fixed_point_to_int_frac(..., 2, 13)`, and mirrors the result to red, green, and blue scales. Otherwise it programs default scale `0x2000` for all channels.

State and persistence: no state is owned by this file. Visibility helpers read the current pipe graph and plane states. `build_prescale_params()` writes only the caller-provided `dc_bias_and_scale` output. There is no locking; callers are expected to invoke these helpers while the display state they inspect is stable.

Dependencies and integration points: includes `core_types.h`, `dc_common.h`, and `basics/conversion.h`. `is_rgb_cspace()` is used in DCN10 hardware sequencing for MPO CSC fixes and MPCC blending configuration. `is_pipe_tree_visible()` is used by DCN hardware sequencing to decide blanking behavior for pipe trees. `build_prescale_params()` is called while updating DPP setup and bias/scale registers for a plane.

Risks: the recursive pipe traversal assumes acyclic `top_pipe`/`bottom_pipe` links; a corrupted pipe graph would recurse indefinitely. `is_rgb_cspace()` must be updated when new `dc_color_space` enum values are added, or debug builds will break and release behavior will classify unknown values as non-RGB. `build_prescale_params()` relies on the conversion helper's S2D13 packing behavior and does not clamp or validate unusual coefficient reduction factors locally.

Test signals: enum coverage tests should verify every current `dc_color_space` maps correctly. Pipe-tree tests should cover visibility on current, top, bottom, multi-level, and fully hidden pipe graphs. Prescale tests should cover video and non-video formats, invalid formats, CSC adjustment enabled/disabled, zero and nonzero coefficient reduction, and expected `0x2000` defaults. Integration signals include correct DPP bias/scale programming and MPO blending behavior on RGB versus YCbCr outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/dc_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/dc_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/dc_common.h

Purpose: declares common AMD display-core helper functions implemented by `dc_common.c`. The header exposes color-space classification, pipe-tree visibility checks, and prescale parameter construction to hardware sequencing and other display modules.

Important APIs and types: declares `is_rgb_cspace()`, `is_lower_pipe_tree_visible()`, `is_upper_pipe_tree_visible()`, `is_pipe_tree_visible()`, and `build_prescale_params()`. The declarations depend on `enum dc_color_space`, `struct pipe_ctx`, `struct dc_bias_and_scale`, and `struct dc_plane_state` from `core_types.h`.

Control flow: this header has no executable logic. It defines the public interface used by callers that need the implementation in `dc_common.c`.

State and persistence: no state is declared or persisted. The functions operate on caller-owned display state and output structures.

Dependencies and integration points: includes `core_types.h`, which makes it part of the internal display core type graph. It is included by hardware sequencing modules such as DCN10 paths that need RGB/YCbCr classification, pipe blanking visibility checks, and DPP bias/scale setup.

Risks: because the header exposes recursive visibility helpers on raw `pipe_ctx` pointers, callers must pass valid pipe nodes from a stable display state. Signature changes would ripple into hardware sequencing code. Documentation of expected pointer nullability and pipe graph assumptions is minimal, so misuse depends on code review and integration tests.

Test signals: compile all hardware sequencing users after any signature or type change. Runtime validation should come from the `dc_common.c` behavior tests: color-space enum coverage, pipe graph traversal coverage, and prescale register value checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/dc_common.h -->
