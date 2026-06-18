# Research Group subset-b-001461

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_easf_filters.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_easf_filters.c

Purpose: this file is the Enhanced Adaptive Scaling Filter (EASF) coefficient and register-parameter table provider for the AMD Display Core SPL scaler path. Most of the file is static, generated coefficient data for 3-, 4-, and 6-tap 64-phase LanczosEd filters at ratio bands 0.3 through 1.0. It keeps both S1.10 tables and preconverted S1.12 tables; the normal public coefficient API returns S1.12 data, while the `_s1_10` API returns the original quantization.

Important APIs and control flow: `spl_dscl_get_easf_filter_coeffs_64p()` dispatches by tap count to 3/4/6 tap helpers and chooses a coefficient table by comparing `struct spl_fixed31_32 ratio.value` against 3/10, 4/10, ..., 9/10 thresholds. Unsupported tap counts call `SPL_BREAK_TO_DEBUGGER()` and return `NULL`. `spl_set_filters_data()` is the integration point used by `dc_spl.c`; it selects EASF or legacy scaler filter pointers for luma/chroma and horizontal/vertical axes. When EASF is enabled it uses `data->recip_ratios`; otherwise it uses `data->ratios`, matching the comment that newer coefficients are based on output/input while old coefficients are input/output.

State and persistence: there is no runtime ownership, allocation, or persistent mutable state. Outputs are pointers into static read-only coefficient arrays and computed register values from static lookup tables. `dscl_prog_data` is mutated by `spl_set_filters_data()` only by assigning filter pointer fields.

Dependencies and integration: the file depends on `spl_debug.h`, fixed-point helpers through `dc_spl_types.h`, legacy filter selection in `dc_spl_scl_filters.h`, and common S1.10 conversion definitions in `dc_spl_filters.h`. Register lookup helpers feed EASF programming in `dc_spl.c` for BF3 modes, reducer gains, ring gains, and 3-tap tilt parameters.

Risks: ratio boundary behavior is strict `<`, so exact thresholds select the next higher table. Invalid tap counts are debug assertions, not recoverable errors. The lookup tables use a `{-1, -1, ...}` sentinel and assume entries are ordered by ascending threshold. The file contains duplicate quantization families, so table regeneration must keep S1.10 and S1.12 tables synchronized. Test signals should cover each tap count, exact threshold ratios, below-0.3 and above-1.0 fallback behavior, `spl_set_filters_data()` axis enable combinations, and register lookup defaults for unsupported taps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_easf_filters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_easf_filters.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_easf_filters.h

Purpose: this header declares the public EASF scaler-filter interface and the small lookup-row type used by the EASF implementation. It is the contract between SPL scaler calculation code and the generated EASF coefficient/register tables in `dc_spl_scl_easf_filters.c`.

Important APIs and types: `struct scale_ratio_to_reg_value_lookup` stores a rational threshold (`numer`/`denom`) and the register value selected for ratios below that threshold; negative numerator rows are used by the implementation as a sentinel/default. `spl_set_filters_data()` populates `struct dscl_prog_data` filter pointers from `struct spl_scaler_data`, taking independent vertical and horizontal EASF enable flags. The `spl_get_*` functions expose EASF register values for BF3 mode, reducer gains, ring gains, and 3-tap tilt controls. `spl_dscl_get_easf_filter_coeffs_64p()` and `_s1_10()` expose coefficient tables for supported tap counts.

Control flow and state: the header has no executable state, but it defines a pull-based API: scaler setup computes ratios/taps, then calls these functions to obtain register-ready values or coefficient-array pointers. All state is held by caller-owned `spl_scaler_data` and `dscl_prog_data`.

Dependencies and integration: it includes `dc_spl_types.h`, so users inherit SPL fixed-point, scaler, and hardware-programming data structures. The symbols are wrapped in `SPL_NAMESPACE`, allowing optional compile-time prefixing. Primary consumers are SPL scaler parameter programming paths such as `dc_spl.c`; the implementation also coordinates with legacy `dc_spl_scl_filters`.

Risks and tests: callers must pass only supported tap counts for coefficient APIs, because invalid combinations assert in the implementation. Ratio values must use the same fixed31_32 convention expected by the generated tables. Tests should compile this header with namespace prefixing on/off, check all declarations match the implementation, and exercise 3-, 4-, and 6-tap EASF paths plus unsupported tap defensive behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_easf_filters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_filters.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_filters.c

Purpose: this file provides the legacy/non-EASF DSCL scaler coefficient tables and the public selector `spl_dscl_get_filter_coeffs_64p()`. The data covers 2 through 8 taps, 64 phases represented as 33 stored symmetric phases, and several ModifiedLanczos ratio bands.

Important APIs and control flow: static arrays such as `filter_3tap_64p_upscale`, `filter_3tap_64p_116`, `filter_3tap_64p_149`, and `filter_3tap_64p_183` repeat for 3 through 8 taps. Selection helpers choose an upscale table when `ratio < 1`, then downscale bands split at `4/3` and `5/3`, with the final table used for larger ratios. `spl_get_filter_2tap_64p()` always returns the 2-tap table. `spl_dscl_get_filter_coeffs_64p()` dispatches by tap count, returns `NULL` for one tap, and asserts for impossible tap counts.

State and persistence: the implementation is stateless. It returns pointers to static const tables and does not allocate, copy, or retain caller data. Runtime behavior depends only on the `taps` integer and the raw `value` field in `struct spl_fixed31_32`.

Dependencies and integration: it depends on `spl_debug.h` for assertions and `dc_spl_scl_filters.h` for the public prototype. It is used indirectly by `spl_set_filters_data()` when EASF is disabled, and directly by scaler programming code that needs raw DSCL coefficient pointers. The fixed-point comparison thresholds depend on `spl_fixpt_from_fraction()`.

Risks and tests: threshold equality selects the higher ratio band because all comparisons are strict `<`. Invalid tap counts are treated as programming bugs rather than soft failures. Array lengths must remain `33 * taps`; a malformed generated table would corrupt hardware programming downstream. Test signals should validate the dispatch matrix for taps 1-8, exact 1.0/4:3/5:3 boundaries, pointer identity for each selected table, and coefficient sum/format expectations for representative phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_filters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_filters.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_filters.h

Purpose: this header exposes the legacy DSCL 64-phase scaler coefficient selector. It is intentionally narrow: callers provide a tap count and fixed-point scale ratio and receive a pointer to a static coefficient table.

Important API: `spl_dscl_get_filter_coeffs_64p(int taps, struct spl_fixed31_32 ratio)` returns `const uint16_t *`. The tap count determines table width, and the ratio determines which precomputed ModifiedLanczos band the implementation uses. The symbol is wrapped in `SPL_NAMESPACE`, making it compatible with SPL prefixing.

Control flow and state: the header defines no state. Control is delegated entirely to `dc_spl_scl_filters.c`; callers must not assume ownership of the returned pointer. A `NULL` result is meaningful for one-tap/bypass-style operation in the implementation.

Dependencies and integration: it includes `dc_spl_types.h`, which provides `struct spl_fixed31_32` and the SPL namespace macro through included OS types. It is included by EASF selection code as the fallback path and by scaler programming code that emits raw DSCL filter pointers.

Risks and tests: this API has no output length parameter, so consumers must know that tables are stored as `33 * taps` entries. Invalid taps assert in the implementation, so tests should cover valid tap values and the `taps == 1` `NULL` behavior. Build tests should also confirm declarations remain synchronized with the implementation when `SPL_PFX_` is defined.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_scl_filters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_types.h

Purpose: this header is the central SPL data model for scaler calculation and hardware programming. It defines geometry, ratios, taps, input policy, output register payloads, EASF/iSharp register fields, callbacks, and debug knobs used by AMD Display Core scaler code.

Important types: simple geometry and scaler primitives include `spl_size`, `spl_rect`, `spl_ratios`, `spl_inits`, `spl_taps`, and `spl_scaler_data`. Hardware-facing outputs are concentrated in `dscl_prog_data`, which contains recout, MPC size, DSCL mode, black color, ratios, init values, taps, raw filter pointers, EASF register fields, iSharp registers, blur-scale filters, and `sharpness_level`. Public calculation boundaries are `spl_in`, `spl_out`, and `spl_scratch`. Policy enums cover pixel formats, 3D view mode, rotation, color space, transfer functions, chroma cositing, sharpness behavior, and linear-light scaling preference.

Control flow and state: the header itself has no functions, but it describes the state flow used by SPL. Callers provide `spl_in` basic input/output properties and policy flags; SPL fills `spl_scratch.scl_data`; final hardware-ready results are written through `spl_out.dscl_prog_data`. Pointers inside `dscl_prog_data` refer to static coefficient tables supplied by filter modules.

Dependencies and integration: it includes debug, OS type, fixed-point, and custom-float helpers. It is consumed broadly by `dc_spl.c`, filter selection modules, iSharp support, and any hardware sequencer code translating `dscl_prog_data` to registers.

Risks and tests: this is a wide ABI-style header; field ordering and meaning matter to every scaler path. Many fields are raw register values with no local validation, so tests should verify SPL fills all relevant fields for RGB/YUV, 4:2:0 chroma, rotations, scaling/bypass modes, EASF/iSharp enable policies, fullscreen/HDR policy, and ODM/MPC slicing. Pointer lifetime assumptions for coefficient arrays should be checked by integration tests rather than unit-only coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_custom_float.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_custom_float.c

Purpose: this file converts SPL fixed31_32 values into a caller-specified compact custom floating-point bit layout. It is used by scaler programming paths that need register encodings with configurable mantissa, exponent, and optional sign bits.

Important functions and control flow: `spl_convert_to_custom_float_format()` is the public entry point. It calls `spl_build_custom_float()` to normalize a fixed-point value, derive sign, mantissa, and exponent, then calls `spl_setup_custom_float()` to pack fields into a `uint32_t`. Zero returns all fields zero. Negative values are converted to magnitude and only preserve negativity if the format supports `sign`. Values below one are left-shifted until normalized, with underflow producing zero exponent/mantissa. Large values are right-shifted until they fit below the maximum mantissa range. Packing copies mantissa bits first, exponent bits after them, and sign after exponent.

State and persistence: there is no static mutable state and no allocation. The function mutates only caller-provided out parameters and returns `true` even for clamped/underflow-style cases.

Dependencies and integration: it depends on `spl_debug.h`, `spl_custom_float.h`, and fixed-point arithmetic helpers (`spl_fixpt_*`). `dc_spl.c` uses it for EASF matrix coefficient register fields.

Risks and tests: the format fields drive shifts such as `1 << (bits + 1)`, so invalid or oversized bit counts can overflow C integer shifts. Verification masks assert and clamp if mantissa/exponent exceed masks, but the API does not report these as failures. Negative input with `format->sign == false` silently becomes nonnegative. Tests should cover zero, positive/negative values, underflow below exponent range, high values requiring exponent growth, no-sign formats, maximum mantissa/exponent boundaries, and exact bit packing for known fixed-point inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_custom_float.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_custom_float.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_custom_float.h

Purpose: this header declares the custom-float conversion API used by SPL register programming. It lets callers describe a compact floating-point format rather than hard-coding one register encoding into the math helper.

Important types and API: `struct spl_custom_float_format` contains `mantissa_bits`, `exponenta_bits`, and `sign`. `struct spl_custom_float_value` mirrors the decomposed result fields plus packed `value`, but the implementation's public API currently returns only the packed `uint32_t`. `spl_convert_to_custom_float_format()` accepts a fixed31_32 value, a format descriptor, and a result pointer.

Control flow and state: the header defines no state. Callers own the format descriptor and result storage; the implementation computes a one-shot conversion.

Dependencies and integration: it includes `spl_os_types.h` for kernel integer/bool types and namespace macros, and `spl_fixpt31_32.h` for the input value type. It is included by `dc_spl_types.h`, so the conversion API is available throughout SPL. Main integration is EASF matrix or coefficient-like register programming where custom exponent/mantissa encodings are required.

Risks and tests: there is no validation contract for legal bit widths in the header, so callers must avoid formats that produce invalid shifts or exceed the 32-bit result field. The misspelled `exponenta` field is part of the API and must be kept consistent. Tests should validate header/implementation agreement, namespace prefixing, and representative packed encodings for each hardware format that uses this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_custom_float.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_debug.h

Purpose: this header centralizes SPL assertion and debugger-break macros for kernel builds. It maps SPL internal invariants to Linux `WARN_ON()` behavior and, when KGDB is configured, can trigger `kgdb_breakpoint()` for critical assertions.

Important macros: `SPL_ASSERT_CRITICAL(expr)` warns on failed expressions and conditionally breaks into KGDB. `SPL_ASSERT(expr)` maps to critical assertions only when `CONFIG_DEBUG_KERNEL_DC` is enabled; otherwise it is a plain `WARN_ON(!(expr))`. `SPL_BREAK_TO_DEBUGGER()` is implemented as `SPL_ASSERT(0)`.

Control flow and state: there is no persistent state. Failed assertions affect control only through warnings and optional debugger breakpoints; most callers continue executing unless the debugger stops the system. Many scaler helpers use these macros for impossible tap counts, overflow checks, and packing validation.

Dependencies and integration: this file assumes Linux warning/debug symbols are available through including contexts; `spl_os_types.h` includes Linux kernel headers and also includes this header. It is used by fixed-point math, custom float packing, and filter selectors.

Risks and tests: because assertions are warnings in non-debug builds, callers must not rely on them for input sanitization. Code paths often return fallback values after `SPL_BREAK_TO_DEBUGGER()`, so invalid inputs can still propagate `NULL` or clamped values. Build tests should cover configurations with and without KGDB and `CONFIG_DEBUG_KERNEL_DC`. Runtime tests should include invalid-input paths only in controlled debug environments to avoid unexpected breakpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_fixpt31_32.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_fixpt31_32.c

Purpose: this file implements SPL fixed31_32 arithmetic for scaler calculations. The format is signed 1.31.32: one sign bit, 31 integer bits, and 32 fractional bits. It supplies fraction construction, multiplication, square, reciprocal, sinc/sin/cos, exp/log, hardware-format conversions, and reconstruction from packed integer/fraction fields.

Important functions and control flow: `spl_fixpt_from_fraction()` performs integer division plus bit-by-bit fractional generation and LSB rounding. `spl_fixpt_mul()` and `spl_fixpt_sqr()` split integer/fractional parts to avoid full 128-bit math. `spl_fixpt_sinc()` normalizes large arguments by multiples of two pi, then uses a polynomial recurrence; `spl_fixpt_sin()` multiplies by sinc. `spl_fixpt_cos()` uses a similar recurrence but notes missing argument normalization. `spl_fixpt_exp()` reduces by ln(2) and evaluates a Taylor series for the residual. `spl_fixpt_log()` iterates using exp until a fixed error threshold. Hardware conversion helpers pack/truncate values into u4.19, u3.19, u2.19, u0.19, clamped u0.14/u0.10, and s4.19.

State and persistence: no mutable state is stored. Constants for two pi and ln(2) are static const. All functions return values by copy.

Dependencies and integration: it depends on `spl_fixpt31_32.h`, Linux division wrappers from `spl_os_types.h`, and SPL assertions. It underpins scaler ratio math, filter threshold comparisons, EASF register lookup, and custom float conversion.

Risks and tests: division by zero is not guarded in reciprocal/fraction paths. Several comments document limited valid domains for trig/exp/log; `cos()` lacks normalization and `log()` assumes positive input. Overflow behavior is assertion-based, so release builds may warn but continue. Tests should compare fixed-point results against high-precision references for ratio construction, multiplication rounding, boundary conversions, negative values, clamp minima, and documented invalid domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_fixpt31_32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_fixpt31_32.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_fixpt31_32.h

Purpose: this header defines the fixed31_32 numeric type and most inline arithmetic/comparison helpers used throughout SPL. It documents the signed 31-integer/32-fraction fixed-point representation and exposes non-inline math implemented in `spl_fixpt31_32.c`.

Important APIs and types: `struct spl_fixed31_32` wraps a signed 64-bit `value`. Constants include zero, epsilon, half, and one. Inline helpers cover construction from int, negation, absolute value, relational comparisons, min/max/clamp, shifts, add/subtract with overflow assertions, multiplication/division by int, fixed division, power, floor/round/ceil, and truncation. External functions cover fraction construction, multiply/square, reciprocal, sinc/sin/cos, exp/log, hardware packing (`u4d19`, `u3d19`, `u2d19`, `u0d19`, clamped u0 formats, `s4d19`), and reconstruction from packed fields.

Control flow and state: most inline functions are pure value transforms. Overflow and invalid assumptions call `SPL_ASSERT`, which may only warn depending on build configuration. No dynamic state is stored.

Dependencies and integration: it includes `spl_debug.h` and `spl_os_types.h` for assertions, integer types, division helpers, and `SPL_NAMESPACE`. It is included by `dc_spl_types.h`, filter headers, EASF lookup code, and custom-float conversion.

Risks and tests: the header redefines `LLONG_MIN/MAX` defensively, which can interact with compiler/system definitions. Shift helpers depend on sane shift counts and valid ranges. Some documented math functions have restricted domains but the declarations do not encode those constraints. Tests should compile both with and without existing `LLONG_*` definitions, validate inline overflow assertions, and compare all public conversions and rounding helpers with expected bit patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_fixpt31_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_os_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_os_types.h

Purpose: this header is the Linux-kernel adaptation layer for SPL common code. It imports kernel types/utilities, wraps division helpers under SPL names, defines simple utility macros, and supplies the `SPL_NAMESPACE` symbol-prefix mechanism.

Important APIs and macros: wrappers include `spl_div_u64_rem()`, `spl_div_u64()`, `spl_div64_u64()`, `spl_div64_u64_rem()`, and `spl_div64_s64()`. `spl_swap()` uses `typeof` to swap two lvalues. `spl_min()` is defined if absent. Namespace macros define `SPL_PFX_` defaulting to empty and use token-pasting through `SPL_EXPAND2`, `SPL_EXPAND`, and `SPL_NAMESPACE(symbol)`.

Control flow and state: all functions are static inline wrappers with no stored state. The namespace macro changes symbol names at compile time only.

Dependencies and integration: it includes `spl_debug.h` plus Linux kernel headers for slab, KGDB, kref, types, delay, and mm. Fixed-point math depends on the division wrappers; every public SPL API uses `SPL_NAMESPACE` for optional prefixing.

Risks and tests: this file ties SPL to Linux kernel build context; it is not freestanding C. `spl_swap()` evaluates lvalues through a temporary but still requires compatible assignment types. `spl_min()` lacks type-safety and can double-evaluate arguments. Namespace prefixing must be consistent across all SPL translation units. Tests should include kernel-build compilation, namespace-prefixed builds, division edge cases, and macro hygiene checks for arguments with side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/spl_os_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/dmub_srv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/dmub_srv.h

Purpose: this header defines the standalone DMUB service interface for AMD display DMCUB microcontroller management. It covers service creation, firmware memory layout, hardware initialization/reset, framebuffer and register inbox command submission, GPINT/inbox/outbox communication, diagnostics, power-state tracking, and firmware metadata extraction. The file explicitly states that the interface is not thread-safe and must be synchronized by callers.

Important types: enums describe status codes, ASIC families, DMUB cache windows, notification types, DPIA bandwidth statuses, memory access mode, power state, and inbox command interface. Memory/layout structs include `dmub_region`, `dmub_window`, `dmub_fb`, region/memory params, region/fb info, SoC FB info, and hardware-init params. Runtime state is in `struct dmub_srv`, which stores ASIC/config flags, firmware/shared-state pointers, framebuffer regions, hardware callback tables, inbox/outbox ring buffers, feature caps, power state, diagnostics, and pre-OS info. `dmub_srv_base_funcs` and `dmub_srv_hw_funcs` are the platform/hardware callback surfaces. `dmub_notification` is the normalized outbox notification payload.

Control flow and persistence: the documented sequence is create, query support, calculate regions, initialize hardware, queue/execute commands, wait for idle/pending/free space, and destroy/reset as needed. `dmub_srv` persists software state across calls; hardware and firmware state are managed through callback functions and mailbox/ring-buffer state.

Dependencies and integration: it includes `inc/dmub_cmd.h` and `dc/dc_types.h`. Display manager code creates the service, DC wraps it in `dc_dmub_srv`, and stat code consumes notifications.

Risks and tests: synchronization is caller-owned. Hardware callbacks may be ASIC-specific and partially unsupported. Timeouts, D3 power state, queue fullness, and mailbox desynchronization must be handled by callers. Tests should cover initialization sequences per ASIC, memory alignment/size calculations, command queue full/timeout behavior, GPINT and inbox0 ACK paths, D3 rejection, diagnostic capture after failures, and firmware metadata parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/dmub_srv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/dmub_srv_stat.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/dmub_srv_stat.h

Purpose: this header declares the lock-light DMUB status/notification interface. It exists because some notification polling paths are called without DAL and DC locks and therefore must touch only state dedicated to that purpose.

Important API: `dmub_srv_stat_get_notification(struct dmub_srv *dmub, struct dmub_notification *notify)` retrieves and normalizes a DMUB outbox notification. The implementation lives in `dmub/src/dmub_srv_stat.c`. `struct dmub_notification` and status codes come from `dmub_srv.h`.

Control flow and state: callers pass an existing `dmub_srv` and an output notification buffer. The comment in `dmub_srv.h` notes that `outbox1_rb` is accessed without locks and is intended only for this stat function. That makes this API a constrained side path into DMUB service state rather than a general service operation.

Dependencies and integration: it includes `dmub_srv.h`. `dc/core/dc_stat.c` calls this API, and ASIC-specific DMUB files provide outbox read/write helpers that are documented as callable only by this notification path.

Risks and tests: because the API is used without broad locks, it must avoid modifying unrelated DMUB state and must tolerate concurrent display-core activity. Races around outbox ring pointers, pending notifications, and hardware-ready interrupt status are the main risk. Tests should cover no-data, AUX reply, HPD, HPD IRQ, set-config reply, DPIA notifications, fused I/O, pending-notification chaining, and concurrent polling with normal DMUB command submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/dmub_srv_stat.h -->
