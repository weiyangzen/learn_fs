# subset-b-001433 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c

## Purpose
`dcn30_dpp.c` implements the DCN 3.0 display pipe processor behavior for AMD Display Core. It wires the DPP function table to register-programming routines for format conversion, post-CSC, pre-degamma ROM selection, cursor attributes, scaler tap selection, blend/shaper/3D LUT programming, deferred memory power-down, state readback, and DPP construction.

## Important APIs, types, and functions
- `dpp3_construct()` initializes `struct dcn3_dpp` with DC context, instance, register tables, function table, and caps.
- `dpp30_read_state()` and `dpp30_read_reg_state()` read live DPP enable, color pipeline, scaler, MPC, and control registers into debug state structures.
- `dpp3_cnv_setup()` maps `enum surface_pixel_format` and expansion/CSC inputs into CNVC format, alpha, 2-bit alpha LUT, dealpha/re-alpha, and post-CSC registers.
- `dpp3_program_post_csc()` programs either the ICSC or COMA post-CSC matrix bank, using local hardcoded color-space matrices or caller-provided matrix entries.
- `dpp3_set_pre_degam()`, `dpp3_set_cursor_attributes()`, and `dpp3_get_optimal_number_of_taps()` cover pre-degamma ROM mode, cursor format/degamma state, and adaptive scaler tap selection.
- Local helpers program double-buffered blend gamma LUTs, shaper LUTs, and tetrahedral 3D LUTs while managing CM memory low-power state.
- `dcn30_dpp_funcs` is the integration surface consumed by DC resource construction and hardware sequencing.

## Control flow
Construction is straightforward: `dpp3_construct()` stores register descriptors and exposes `dcn30_dpp_funcs` plus `dcn30_dpp_cap`. Runtime programming usually starts through function-table callbacks. Plane setup enters `dpp3_cnv_setup()`, which resets format-control defaults, selects a hardware pixel format code, programs alpha behavior, optionally writes 2-bit alpha LUT values, disables pre-dealpha/re-alpha, and then calls `dpp3_program_post_csc()` with bypass or ICSC selection.

Post-CSC uses double-buffering. If bypass is requested it clears `CM_POST_CSC_MODE`; otherwise it chooses built-in matrix coefficients or caller coefficients, reads `CM_POST_CSC_MODE_CURRENT`, selects the alternate ICSC/COMA register bank, programs matrix registers through `cm_helper_program_color_matrices()`, and switches `CM_POST_CSC_MODE`.

The color LUT paths follow the same pattern. `dpp3_program_blnd_lut()`, `dpp3_program_shaper()`, and `dpp3_program_3dlut()` bypass and schedule memory power-down on NULL parameters. With valid parameters, they power the target memory, choose the alternate RAM bank, program region/control registers plus LUT data, and update mode/select registers so hardware latches the new bank. `dpp3_deferred_update()` later completes power-down requests only after hardware reports the bypass state on vupdate.

Scaler tap selection in `dpp3_get_optimal_number_of_taps()` derives defaults from scaling ratios, clamps chroma horizontal taps to supported values, checks debug max-downscale limits, calculates line-buffer partitions through DPP caps, clamps vertical taps to partition-derived limits, and collapses identity axes to one tap unless `always_scale` is set.

## State and persistence behavior
This file maintains only runtime software and hardware state. Software state lives in `struct dpp` and `struct dcn3_dpp`: cached function/cap pointers, register tables, cursor attribute snapshots, deferred low-power bits, scaler cache fields, and LUT/filter pointers. Persistent effects are register writes to DPP/CNVC/CM/DSCL blocks; there is no disk or cross-boot persistence. Low-power behavior is stateful across frames through `deferred_reg_writes` and `ctx->dc->optimized_required`, because memory shutdown is postponed until the bypass mode has latched.

## Dependencies and integration points
The implementation depends on Display Core base types, `reg_helper` register macros, `dcn30_dpp.h` register tables, `dcn30_cm_common.h` matrix/gamma helpers, fixed-point helpers, DC debug/cap flags, and common DPP functions from DCN1/DCN2. It integrates upward through `struct dpp_funcs`, and downward through ASIC-specific register offsets/masks supplied by resource construction.

## Risks and edge cases
The highest-risk areas are register bank selection and latch timing for post-CSC, blend LUT, shaper, and 3D LUT. Incorrect current-mode reads or select writes can update the bank currently scanned out. LUT data paths assume valid nonzero `params->hw_points_num` and correctly sized tetrahedral arrays. `dpp3_set3dlut_ram12()` writes entries in pairs and assumes an even entry count. Low-power paths rely on debug flags and mode-current checks; stale `deferred_reg_writes` can assert if a LUT is re-enabled before the bypass latch. Format setup has many hardware magic pixel codes, and YCrCb video formats disable cursors on DCN30 while related newer code does not. Tap selection must match line-buffer partition math or the scaler can underflow.

## Test signals
Useful signals include DC bring-up on DCN30 hardware, plane format tests across RGB, FP16, RGBE, and YUV 4:2:0 variants; CSC adjustment and color-space bypass tests; cursor format and degamma tests; identity/upscale/downscale scaler validation with debug `always_scale`; blend/shaper/3D LUT programming with RAM A/B flips; low-power memory enable/disable coverage; register readback through debug state; and visual CRC tests for gamma, CSC, cursor, and scaler output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h

## Purpose
`dcn30_dpp.h` is the private DCN 3.0 DPP interface and register map definition. It extends DCN2 DPP register fields with DCN3 color-management, CNVC, DSCL, cursor, low-power, and LUT registers, defines `struct dcn3_dpp`, and declares the DCN3 DPP programming functions implemented across `dcn30_dpp.c` and `dcn30_dpp_cm.c`.

## Important APIs, types, and functions
- `TO_DCN30_DPP()` casts a base `struct dpp` to `struct dcn3_dpp`.
- `DPP_REG_LIST_DCN30_COMMON()`, `DPP_REG_LIST_DCN30()`, `DPP_REG_LIST_SH_MASK_DCN30_COMMON()`, `DPP_REG_LIST_SH_MASK_DCN30_UPDATED()`, and `DPP_REG_LIST_SH_MASK_DCN30()` are macro inventories consumed by ASIC resource register table generation.
- `DPP_REG_FIELD_LIST_DCN3()` defines the shift/mask field set used by `struct dcn3_dpp_shift` and `struct dcn3_dpp_mask`.
- `DPP_DCN3_REG_VARIABLE_LIST_COMMON` and `struct dcn3_dpp_registers` define register-offset storage.
- `struct dcn3_dpp` embeds `struct dpp` and stores register tables, cached scaler filter pointers, line-buffer capabilities, scaler data, and PWL data.
- Public prototypes include construction, GAMCOR, CM dealpha/bias/gamut remap, pre-degamma, cursor attributes, post-CSC, state readback, and tap-selection helpers.

## Control flow
The header has no executable runtime flow. Its macros are expanded by generated/static register table definitions for each ASIC instance. C files use the resulting offset/shift/mask structures through `REG()`, `FN()`, and `REG_*` helpers to program hardware. Function prototypes define the callable surface that generational DPP constructors reuse in DCN32, DCN35, DCN401, and DCN42.

## State and persistence behavior
The header defines runtime state shape only. `struct dcn3_dpp` persists cached filter pointers and last scaler/PWL data in memory for the lifetime of a DPP object. Register offset, shift, and mask structures are read-only tables supplied by ASIC-specific resource code. There is no persistent storage outside kernel memory and hardware registers.

## Dependencies and integration points
The header depends on `dcn20/dcn20_dpp.h` for base DCN2 fields and types. It is included by DCN30 implementation files and by later generation headers that reuse DCN3 structures. The register-list macros must align with generated register headers and the ASIC resource files that instantiate register tables.

## Risks and edge cases
Macro-maintained hardware maps are brittle: duplicate entries, missing fields, or mismatched field names produce incorrect register writes or compile failures depending on where the mismatch appears. The file includes repeated register/field entries such as `CM_GAMCOR_LUT_INDEX` and duplicate cursor control fields, which may be intentional compatibility baggage but increase maintenance risk. `struct dcn3_dpp` is reused by later generations, so adding fields or changing type assumptions can affect DCN32/DCN35 code.

## Test signals
Build coverage across ASIC configurations is the primary signal for macro/table correctness. Runtime validation should include DPP construction, register writes for every callback in `dcn30_dpp.c` and `dcn30_dpp_cm.c`, debug readback, and later-generation builds that include this header through DCN32/DCN35/DCN401/DCN42.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp_cm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp_cm.c

## Purpose
`dcn30_dpp_cm.c` implements the DCN3 DPP color-management functions that are separate from the main DPP file: CM bypass control, gamma-correction programmable LUT programming, CM dealpha/bias, HDR multiplier, and gamut-remap set/get.

## Important APIs, types, and functions
- `dpp3_program_gamcor_lut()` is the exported programmable gamma correction path for `dpp_funcs.dpp_program_gamcor_lut`.
- `dpp3_program_cm_dealpha()` and `dpp3_program_cm_bias()` program simple CM blending/bias registers.
- `dpp3_set_hdr_multiplier()` writes `CM_HDR_MULT_COEF`.
- `dpp3_cm_set_gamut_remap()` and `dpp3_cm_get_gamut_remap()` convert between DC fixed-point gamut matrices and hardware matrix registers.
- Local helpers include `dpp3_enable_cm_block()`, `dpp30_get_gamcor_current()`, `dpp3_program_gammcor_lut()`, `dpp3_power_on_gamcor_lut()`, `dpp3_gamcor_reg_field()`, `dpp3_configure_gamcor_lut()`, `program_gamut_remap()`, and `read_gamut_remap()`.

## Control flow
Gamma programming begins by enabling the CM block unless debug forces bypass. A NULL PWL parameter bypasses GAMCOR and schedules or performs memory power-down. A valid PWL parameter powers GAMCOR memory, sets programmable RAM mode, reads the currently active RAM bank, chooses the alternate bank, configures LUT host selection, selects the correct RAM A/B region and slope registers, fills `struct dcn3_xfer_func_reg` shift/mask metadata, calls `cm_helper_program_gamcor_xfer_func()`, writes LUT base values channel-by-channel or once if RGB values are equal, and finally updates `CM_GAMCOR_SELECT`.

Gamut remap accepts only software matrices. Non-software adjustment types bypass the block. Software matrices are converted to 12 hardware register values, the current active coefficient set is read, the alternate A/B set is selected, matrix registers are programmed through `cm_helper_program_color_matrices()`, and `CM_GAMUT_REMAP_MODE` is updated. Readback mirrors this by reading the current mode, reading the active matrix bank if not bypassed, and converting hardware matrix values back to `fixed31_32`.

## State and persistence behavior
State is transient and register-backed. GAMCOR RAM bank selection and gamut-remap coefficient set are maintained by hardware mode/current registers. The low-power path uses `dpp_base->deferred_reg_writes.bits.disable_gamcor` and `ctx->dc->optimized_required` to defer memory shutdown until a safe update point. No file or firmware persistence exists.

## Dependencies and integration points
The file depends on `dcn30_dpp.h`, `dcn30_cm_common.h`, conversion helpers, `reg_helper`, and Display Core color structures. It is wired into `dcn30_dpp_funcs` and reused by later DPP constructors unless a later generation explicitly removes the callback. It also relies on DC debug flags such as `cm_in_bypass`, `enable_mem_low_power.bits.cm`, and DC caps such as `ips_v2_support`.

## Risks and edge cases
GAMCOR programming is sensitive to bank selection, region register mapping, and low-power sequencing. `params` must contain valid PWL point counts and curve metadata; the LUT writer indexes `rgb[num - 1]`. The function name `dpp3_program_gammcor_lut()` has a typo but is local. Gamut remap assumes only two coefficient sets and always alternates based on current mode; unexpected hardware modes fall back to set A. Color matrix conversion precision and signedness are important for visual correctness.

## Test signals
Relevant validation includes gamma LUT updates with RAM A/B alternation, NULL gamma bypass and low-power defer tests, CM bypass debug mode, HDR multiplier programming, gamut-remap set/get round trips, visual CRC/colorimeter validation for color temperature matrices, and resume/retrain scenarios where current-mode registers must still reflect software expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn30/dcn30_dpp_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn32/dcn32_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn32/dcn32_dpp.c

## Purpose
`dcn32_dpp.c` adapts the DCN3 DPP implementation for DCN 3.2. It keeps most DCN30 callbacks, removes DPP-local BLNDGAM/shaper/3D LUT programming because those blocks moved out of the DPP, and replaces line-buffer partition calculations with DCN32-specific memory sizing.

## Important APIs, types, and functions
- `dpp32_construct()` initializes a `struct dcn3_dpp` with DCN32 function and cap tables.
- `dscl32_calc_lb_num_partitions()` computes luma/chroma line-buffer partition counts for `struct scaler_data`.
- `dscl32_spl_calc_lb_num_partitions()` performs the same calculation for SPL scaler data.
- `dcn32_dpp_funcs` inherits DCN30 GAMCOR, post-CSC/CNVC setup, pre-degamma, cursor, gamut remap, CM bias/dealpha, tap selection, readback, and DPP clock callbacks, but sets blend LUT, shaper LUT, and 3D LUT callbacks to NULL.
- `dcn32_dpp_cap` advertises floating DSCL processing, max 31 line-buffer partitions, and the DCN32 partition calculator.

## Control flow
Construction stores base context/instance, installs `dcn32_dpp_funcs`, installs `dcn32_dpp_cap`, and records DCN3 register tables. The partition calculators choose the lesser of viewport and recout width for luma/chroma, guard zero widths as one, compute memory line sizes by dividing by six with ceiling, choose memory capacities based on `enum lb_memory_config`, account for full-active non-scaling cases with larger effective memory, include alpha memory as a luma limiter when enabled, and cap output counts at 32.

## State and persistence behavior
This file does not create new persistent state. It populates existing `struct dcn3_dpp` fields and provides stateless calculations. Runtime state remains in the DPP object, DC debug/cap flags, and hardware registers programmed by inherited callbacks.

## Dependencies and integration points
The file includes DC core types, register helpers, `dcn32_dpp.h`, DCN30 color helpers, and conversion helpers. It integrates with DC resource construction through `dpp32_construct()`, and with scaler/tap logic because `dpp3_get_optimal_number_of_taps()` calls the cap-supplied line-buffer partition function.

## Risks and edge cases
The partition constants are hardware-specific magic values; incorrect values or caps can produce unsupported tap choices. The 32 cap coexists with `max_lb_partitions = 31`, so callers must preserve the intended off-by-one hardware interpretation. Removing BLNDGAM/shaper/3D LUT callbacks means higher-level code must route those operations to MPCC or tolerate NULL callbacks. Zero-dimension guards avoid division by zero but can hide invalid scaler input.

## Test signals
Build and boot on DCN32 ASICs, scaler validation for RGB and 4:2:0 formats, alpha-enabled line-buffer cases, SPL and non-SPL partition parity, callback NULL handling for moved color blocks, and visual tests for inherited GAMCOR/CSC/cursor paths are the important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn32/dcn32_dpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn32/dcn32_dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn32/dcn32_dpp.h

## Purpose
`dcn32_dpp.h` is the small public/private header for DCN32 DPP construction and SPL line-buffer partition calculation. It reuses the DCN20 and DCN30 DPP type/register model rather than defining a new DPP structure.

## Important APIs, types, and functions
- `dpp32_construct()` constructs a DCN32 DPP instance using `struct dcn3_dpp` and DCN3 register tables.
- `dscl32_spl_calc_lb_num_partitions()` exposes the SPL scaler-data variant of the line-buffer partition calculator.

## Control flow
There is no executable flow in the header. It provides prototypes used by resource construction and scaler code.

## State and persistence behavior
No state is stored here. DCN32 instances use `struct dcn3_dpp` from `dcn30_dpp.h`; partition calculations are stateless.

## Dependencies and integration points
The header depends on `dcn20/dcn20_dpp.h` and `dcn30/dcn30_dpp.h`. It is included by DCN32 implementation and later code, including DCN401, that reuses the SPL partition helper pattern.

## Risks and edge cases
Because DCN32 intentionally reuses DCN3 structures, prototype changes ripple to later generations. The header does not define a `TO_DCN32_DPP()` cast, so callers must know that `struct dcn3_dpp` remains the concrete type.

## Test signals
Compile coverage for DCN32 resource construction and callers of `dscl32_spl_calc_lb_num_partitions()` is the main signal, supplemented by runtime scaler tests from the implementation file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn32/dcn32_dpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.c

## Purpose
`dcn35_dpp.c` adapts DCN32 DPP behavior for DCN 3.5. It adds DPP clock-control handling for DISPCLK_R gate workarounds, programs FCNV bias/scale registers, exposes an FGCg control helper, and installs a DCN35-specific function table.

## Important APIs, types, and functions
- `dpp35_dppclk_control()` enables/disables DPP clocking, optionally programming `DPPCLK_RATE_CONTROL` or `DISPCLK_R_GATE_DISABLE`.
- `dpp35_program_bias_and_scale_fcnv()` writes FCNV floating-point bias/scale registers or resets them to default bias 0 and scale `0x1F000`.
- `dpp35_construct()` delegates most construction to `dpp32_construct()`, swaps in `dcn35_dpp_funcs`, and enables a cursor-memory workaround on early ASIC revisions.
- `dpp35_set_fgcg()` controls fine-grain clock gating replication disable through `DPP_FGCG_REP_DIS`.
- `dcn35_dpp_funcs` inherits DCN32/DCN30 behavior while enabling bias/scale and the DCN35 DPP clock callback.

## Control flow
Construction first calls `dpp32_construct()` with casts from DCN35 shift/mask structures to DCN3 base structures. It then replaces the function table and, when `hw_internal_rev < 0x40`, sets `dispclk_r_gate_disable` so later clock-enable calls program the workaround. Clock control writes `DPP_CONTROL` differently depending on whether the register table exposes `DPPCLK_RATE_CONTROL` and whether the workaround flag is set. Bias/scale programming branches on `bias_and_scale_valid` to either write caller values or restore neutral defaults.

## State and persistence behavior
The only new software state is `dpp->dispclk_r_gate_disable`, stored in the reused `struct dcn3_dpp`. Hardware state is DPP control, FCNV bias/scale, and FGCg control registers. There is no persistent storage beyond runtime registers and object fields.

## Dependencies and integration points
The file depends on `dcn35_dpp.h`, DCN32 construction, inherited DCN30 CM/CNVC helpers, and DCN20-style register fields via casts. It integrates with resource construction through `dpp35_construct()` and with clock/power sequencing through the `dpp_dppclk_control` callback.

## Risks and edge cases
The shift/mask casts require `struct dcn35_dpp_shift` and mask layout to embed the DCN3 field list compatibly. Clock control has nested conditional logic without braces in some branches, so maintenance changes can easily alter behavior. The early-revision workaround is keyed only on `hw_internal_rev < 0x40`; incorrect ASIC revision reporting can leave cursor memory stuck or unnecessarily disable gating. FCNV defaults must match hardware neutral scale.

## Test signals
Signals include DCN35 build coverage, DPP enable/disable with and without `DPPCLK_RATE_CONTROL`, early and later ASIC revision coverage for `DISPCLK_R_GATE_DISABLE`, FCNV bias/scale visual tests, FGCg toggling tests, and inherited DPP format/scaler/color tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.h

## Purpose
`dcn35_dpp.h` defines DCN35-specific DPP register field additions and prototypes. It layers on DCN32/DCN30 definitions and adds FGCg and DISPCLK gate fields needed by the DCN35 implementation.

## Important APIs, types, and functions
- `DPP_REG_LIST_SH_MASK_DCN35()` extends the DCN30 common shift/mask list with `DPP_FGCG_REP_DIS` and `DISPCLK_R_GATE_DISABLE`.
- `DPP_REG_FIELD_LIST_DCN35()` embeds the DCN3 field list and adds `DPP_FGCG_REP_DIS`.
- `struct dcn35_dpp_shift` and `struct dcn35_dpp_mask` are the DCN35 field-table types.
- Prototypes cover `dpp35_dppclk_control()`, `dpp35_construct()`, `dpp35_set_fgcg()`, and `dpp35_program_bias_and_scale_fcnv()`.

## Control flow
The header contains no executable control flow. Its macro expansions produce register field tables, and its prototypes connect resource construction and DPP function-table callbacks to `dcn35_dpp.c`.

## State and persistence behavior
No state is stored here. It defines table layouts and function signatures for runtime state held in DPP objects and hardware registers.

## Dependencies and integration points
The header depends on `dcn32/dcn32_dpp.h` and therefore on DCN30 structures. ASIC resource files must instantiate compatible shift/mask tables when using `dpp35_construct()`.

## Risks and edge cases
`DPP_REG_LIST_SH_MASK_DCN35()` lists `DPP_FGCG_REP_DIS` twice, which may be harmless but can obscure generated table intent. `DPP_REG_FIELD_LIST_DCN35()` only adds `DPP_FGCG_REP_DIS`, while `dpp35_dppclk_control()` also references `DISPCLK_R_GATE_DISABLE` through inherited masks; table-generation correctness is essential. The closing comment names `__DCN35_DPP_H` without trailing underscores, which is cosmetic but inconsistent.

## Test signals
Compile tests for DCN35 register table generation, `dpp35_construct()` callers, and function-table linkage are the primary signals, with runtime DPP clock and FGCg tests from the C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn35/dcn35_dpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.c

## Purpose
`dcn401_dpp.c` defines the DCN 4.0.1 DPP constructor, function table, basic state readback, CNVC plane setup, and 64-partition line-buffer calculators. It reuses much of DCN30/DCN35 color and cursor behavior while replacing scaler programming with the DCN401 DSCL implementation.

## Important APIs, types, and functions
- `dpp401_construct()` initializes `struct dcn401_dpp` with DCN401 register tables, function table, and caps.
- `dpp401_read_state()` currently reports only `DPP_CLOCK_ENABLE` and leaves DCN4 detailed state as TODO.
- `dpp401_dpp_setup()` programs CNVC format, alpha, 2-bit alpha LUT, pre-dealpha/re-alpha, and post-CSC selection.
- `dscl401_calc_lb_num_partitions()` and `dscl401_spl_calc_lb_num_partitions()` compute line-buffer partitions for classic and SPL scaler data, capped at 64.
- `dcn401_dpp_funcs` wires DCN401 to `dpp401_dscl_set_scaler_manual_scale()`, DCN401 cursor callbacks, DCN35 bias/scale, DCN30 GAMCOR/pre-degamma/CM bias, and cursor matrix setup.

## Control flow
Plane setup mirrors DCN30: reset format conversion defaults, map `surface_pixel_format` to hardware pixel format IDs, derive default color space and ICSC select for video formats, optionally write 2-bit alpha LUT, program alpha/dealpha/re-alpha controls, and invoke `dpp3_program_post_csc()` with either provided adjustment matrix or default matrix. Unlike DCN30, it does not force-disable cursor for YCrCb 4:2:0 formats.

Construction stores context, instance, function/cap pointers, and register table pointers. Line-buffer partition calculators use the same memory constants as DCN32 but cap luma/chroma partitions to 64, reflecting larger DCN401 capacity. The function table intentionally leaves gamut remap, full bypass, BLNDGAM, shaper, and 3D LUT callbacks NULL, while adding cursor matrix support.

## State and persistence behavior
State is runtime-only in `struct dcn401_dpp`, inherited `struct dpp` fields, cached scaler data, and hardware registers. The line-buffer calculators are stateless. Detailed DPP state readback is incomplete for DCN4, so software cannot currently persist or reconstruct the full color/scaler state through `dpp401_read_state()`.

## Dependencies and integration points
The file depends on DC core types, `dcn401_dpp.h`, DCN30 color helpers, DCN32 partition patterns, and DCN35 bias/scale helpers. It integrates with DC resource construction via `dpp401_construct()`, with scaler programming via `dcn401_dpp_dscl.c`, and with cursor matrix/attributes via `dcn401_dpp_cm.c`.

## Risks and edge cases
The DCN4 read-state TODO reduces diagnostics and may break tooling expecting parity with DCN30 readback. `dpp401_dpp_setup()` calls DCN30 post-CSC helper with DCN401 register tables, so field compatibility is critical. NULL callbacks for gamut remap/full bypass/color LUTs require higher-level code to check capability before calling. The partition cap checks use `> 64` despite caps advertising `max_lb_partitions = 63`, preserving hardware convention but creating off-by-one maintenance risk.

## Test signals
Key signals include DCN401 build and display bring-up, format coverage for RGB/YUV/FP16/RGBE, post-CSC adjustment tests, cursor matrix path tests, scaler partition/tap tests for 64-partition cases, NULL callback tolerance in DC color-management paths, and debug readback coverage demonstrating the current limited state read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.h

## Purpose
`dcn401_dpp.h` defines the DCN401 DPP register map, field map, concrete DPP structure, scaler mode enum, and cross-file prototypes. It extends DCN3 definitions with DCN4 cursor matrix, EASF, iSharp, luma keyer, line-buffer power, and extra scaler-init fields.

## Important APIs, types, and functions
- `TO_DCN401_DPP()` casts a base DPP to `struct dcn401_dpp`.
- `DPP_REG_LIST_SH_MASK_DCN401_COMMON()` enumerates DCN401 register field mappings for CM, CNVC, cursor, DSCL, EASF, iSharp, and scaler init.
- `DPP_REG_FIELD_LIST_DCN401()` extends the DCN3 field list with cursor matrix, EASF horizontal/vertical, scaler color matrix, iSharp, luma keyer, and related low-power fields.
- `DPP_REG_VARIABLE_LIST_DCN401`, `struct dcn401_dpp_registers`, `struct dcn401_dpp_shift`, and `struct dcn401_dpp_mask` define register offset and field tables.
- `struct dcn401_dpp` embeds `struct dpp`, register tables, filter cache pointers, line-buffer properties, `struct scaler_data`, and `struct pwl_params`.
- `enum dcn401_dscl_mode_sel` defines hardware scaler modes for 444 bypass/RGB/YCbCr, 420 combined/luma/chroma bypass, and full DSCL bypass.
- Prototypes expose construction, DPP setup, scaler manual programming, cursor callbacks, line-buffer calculators, read state, and cursor matrix setup.

## Control flow
There is no executable flow in the header. Its macros expand into ASIC register tables used by `dcn401_dpp.c`, `dcn401_dpp_cm.c`, `dcn401_dpp_dscl.c`, and DCN42 code. The enum and prototypes establish contracts used by scaler mode selection and DPP function-table callbacks.

## State and persistence behavior
The header defines runtime state shape only. `struct dcn401_dpp` caches the last scaler data and filter pointers so `dcn401_dpp_dscl.c` can skip redundant programming and detect filter updates. Register tables are static configuration. There is no durable persistence.

## Dependencies and integration points
The header depends on DCN20, DCN30, and DCN32 DPP headers. It is included by DCN401 implementation files and by DCN42, which extends it. ASIC resource files must provide register offsets, shifts, and masks matching the field list.

## Risks and edge cases
This is a large macro map with many hardware-specific fields. Missing or duplicated field entries can silently target wrong registers if generated tables remain type-compatible. DCN42 includes this header and extends the field list, so any incompatible structural change affects newer code. The register struct contains both `ALPHA_2BIT_LUT` through the common list and `ALPHA_2BIT_LUT01/23`, requiring generation code to select the correct fields for each ASIC. The enum values must match hardware `DSCL_MODE` encodings.

## Test signals
Compile coverage across DCN401 and DCN42 ASIC table instantiations, DPP construction, cursor matrix programming, EASF/iSharp scaler programming, SPL and non-SPL scaler paths, and register read/write tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp_cm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp_cm.c

## Purpose
`dcn401_dpp_cm.c` implements DCN401-specific cursor color-management helpers. It programs cursor attributes, cursor enable state, optional cursor FP bias/scale, and a cursor CSC matrix block, though the public cursor matrix entry currently forces bypass.

## Important APIs, types, and functions
- `dpp401_set_cursor_attributes()` programs cursor mode, expansion, ROM degamma enable, monochrome colors, and mirrors state into `dpp_base->att`.
- `dpp401_set_cursor_position()` only toggles cursor enable state for DPP-side cursor control and mirrors it into `pos`/`att` snapshots.
- `dpp401_set_optional_cursor_attributes()` programs G/Y and RB/CRCB cursor FP scale/bias register pairs and records them in software state.
- `dpp401_set_cursor_matrix()` is the public function-table callback for cursor matrix setup; it currently ignores caller inputs and forces bypass through `COLOR_SPACE_UNKNOWN`.
- Local `dpp401_program_cursor_csc()` can program cursor matrix set A or B from color-space tables or caller entries and switch `CUR0_MATRIX_MODE`.

## Control flow
Cursor attribute programming determines whether cursor ROM degamma is required from the cursor color format and attribute flags, writes `CURSOR0_CONTROL` unless cursor offload is active, writes monochrome cursor colors when needed, and updates software attribute shadow fields. Position programming reduces to enable/disable: if the desired enable bit differs from the cached state, it writes `CUR0_ENABLE` unless offloaded, then updates cached position/attribute bits.

Optional attributes program two register pairs so G/Y and RB/CRCB channels share the provided bias and scale. The local cursor CSC helper bypasses non-YCbCr color spaces, otherwise selects a built-in matrix or supplied table, alternates matrix set A/B based on `CUR0_MATRIX_MODE_CURRENT`, writes matrix registers with `cm_helper_program_color_matrices()`, and selects the new set. The public `dpp401_set_cursor_matrix()` currently bypasses this logic unconditionally.

## State and persistence behavior
State is mirrored in `dpp_base->att` and `dpp_base->pos` for cursor controls and in hardware cursor/CM registers. Cursor offload suppresses direct register writes but still updates software shadows. There is no persistence outside runtime kernel memory and registers.

## Dependencies and integration points
The file depends on `dcn401_dpp.h`, register helpers, DC color/cursor types, `dcn10_cm_common.h` matrix tables, and conversion helpers. Its callbacks are wired by `dcn401_dpp.c` and reused by DCN42.

## Risks and edge cases
`dpp401_set_cursor_matrix()` currently discards caller color space and matrix inputs, so cursor CSC is always bypassed despite local support for matrix programming. That may be intentional pending cursor matrix information, but it is a functional limitation. Cursor offload paths rely on software shadow updates remaining consistent with offloaded hardware state. Matrix programming assumes register set A/B fields and shifts are compatible with `color_matrices_reg` using only C11/C12 shift metadata.

## Test signals
Cursor tests should cover all cursor formats, ROM degamma flag behavior, mono cursor colors, cursor enable transitions with and without offload, optional FP scale/bias, YCbCr cursor CSC expectations, and regression tests documenting that `dpp401_set_cursor_matrix()` currently forces bypass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp_dscl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp_dscl.c

## Purpose
`dcn401_dpp_dscl.c` is the DCN401 scaler implementation. It programs DSCL line-buffer configuration, scale ratios and initial phases, recout/MPC geometry, coefficient RAMs, scaler mode, EASF sharpening/filter blocks, iSharp, blur/scale coefficients, and scaler memory power control.

## Important APIs, types, and functions
- `dpp401_dscl_set_scaler_manual_scale()` is the exported scaler programming entry used by the DCN401/42 DPP function table.
- `dpp401_dscl_get_dscl_mode()` maps scaler ratios and pixel format to `enum dcn401_dscl_mode_sel`.
- `dpp401_power_on_dscl()` handles DSCL LUT memory power state and deferred low-power shutdown.
- `dpp401_dscl_set_lb()`, `dpp401_dscl_find_lb_memory_config()`, and `dpp401_dscl_is_lb_conf_valid()` configure line-buffer memory and validate tap/partition needs.
- `dpp401_dscl_get_filter_coeffs_64p()`, `dpp401_dscl_set_scaler_filter()`, and `dpp401_dscl_set_scl_filter()` select and program 64-phase scaler filter coefficients.
- `dpp401_dscl_set_manual_ratio_init()` writes scale ratios and filter initial phases, using SPL precomputed values when enabled.
- `dpp401_dscl_program_easf()`, `_easf_v()`, `_easf_h()`, and `_disable_easf()` program or disable edge adaptive scaler functions.
- `dpp401_dscl_program_isharp()` and `dpp401_dscl_set_isharp_filter()` program iSharp mode, noise detection, LBA PWL, delta LUT, soft clip, and blur/scale coefficient filters.

## Control flow
The main entry first compares the new `scaler_data` with the cached copy and returns if unchanged. If iSharp is enabled and only the sharpness level changed, it writes only the iSharp 1D delta LUT, updates the cached sharpness/LUT, and returns if the whole structure now matches. Otherwise it caches the full scaler data, optionally replaces computed geometry/mode/taps with SPL-provided programmed data, powers on DSCL memory when needed, disables AutoCal, clears boundary mode, programs recout and MPC size, and writes `DSCL_MODE`.

If DSCL is fully bypassed, it may schedule memory power-down and returns. For active modes it chooses the smallest line-buffer memory config satisfying vertical tap and ratio requirements, programs line-buffer format/memory control, handles 444 bypass as a special case for EASF disable/iSharp-only programming, writes black offsets for YCbCr versus RGB, writes manual ratios and init phases, writes tap counts, programs iSharp, programs scaler filter coefficients with possible coefficient-RAM toggle, and finally programs EASF when `prefer_easf` is enabled.

Filter programming obtains SPL-provided filters when SPL is enabled and not disabled; otherwise it selects built-in 64-phase filters based on taps and ratios. It uses hardware hardcoded 2-tap coefficients when both luma and chroma taps are two, otherwise it detects changed filter pointers or forced updates, writes luma/chroma coefficient RAMs, caches pointers, reads current coefficient RAM select, and flips to the alternate coefficient RAM.

## State and persistence behavior
`struct dcn401_dpp` caches the last `struct scaler_data` and filter pointers to avoid redundant register programming and to detect coefficient updates. Hardware state persists in DSCL, EASF, iSharp, line-buffer, coefficient RAM, recout, and MPC registers until reprogrammed. Low-power state is coordinated through DC debug flags, `ctx->dc->optimized_required`, and `deferred_reg_writes.bits.disable_dscl`. There is no durable storage.

## Dependencies and integration points
The file depends on DC fixed-point conversion, scaler data structures, filter-table providers such as `get_filter_8tap_64p()`, DC config/debug flags (`use_spl`, `disable_spl`, `prefer_easf`, `always_scale`, `enable_mem_low_power.bits.dscl`), DC caps (`ips_v2_support`), and the DCN401 register/field tables. It integrates through `dpp401_dscl_set_scaler_manual_scale()` in DCN401/DCN42 function tables and through line-buffer partition caps from `dcn401_dpp.c`.

## Risks and edge cases
The early `memcmp()` cache depends on `struct scaler_data` being fully initialized and stable; padding or transient pointers can cause missed or redundant programming. The sharpness-only fast path copies `ISHARP_LUT_TABLE_SIZE` entries and assumes `isharp_delta` storage is valid. Filter pointer caching treats pointer identity as coefficient identity for built-in filters and SPL-provided filters, which can miss in-place updates unless `force_coeffs_update` is set. The iSharp 1D LUT skip condition appears inverted in `dpp401_dscl_program_isharp()` (`if (!program_isharp_1dlut)` writes the LUT), so sharpness-only paths need careful validation. Many register writes consume SPL `dscl_prog_data` directly; invalid SPL data can program unsupported modes, taps, or PWL values. Power transitions use longer waits for IPS v2 and deferred shutdown for low-power debug, so sequencing bugs can leave memories in light sleep during coefficient writes.

## Test signals
Scaler validation should cover identity, RGB/YCbCr 444, 420 luma-only/chroma-only/full scaling, FP16 fixed-format bypass, SPL and non-SPL paths, all tap counts 1-8, 2-tap hardcoded coefficient paths, coefficient RAM flips, line-buffer config selection under high downscale ratios, EASF enabled/disabled and 1:1 behavior, iSharp enabled/disabled and sharpness-only updates, blur/scale coefficient updates, memory low-power transitions, and visual CRC/quality tests for scaling and sharpening.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn401/dcn401_dpp_dscl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.c

## Purpose
`dcn42_dpp.c` adapts DCN401 DPP behavior for DCN 4.2 and adds CM histogram control/readback support. It also updates DPP setup for DCN42 alpha LUT register layout and color-space CSC selection.

## Important APIs, types, and functions
- `dpp42_construct()` initializes `struct dcn42_dpp` with DCN42 register tables, function table, and caps.
- `dpp42_dpp_cm_hist_control()` programs CM histogram tap point, channel enables, source selections, channel crossbars, format, read channel mask, and RGB-to-luma coefficients.
- `dpp42_dpp_cm_hist_read()` locks ready histogram buffers, reads 256 bins for enabled channels, accumulates into `struct cm_hist`, and unlocks.
- `dpp42_dpp_setup()` programs CNVC format/alpha and post-CSC similar to DCN401, but writes split `ALPHA_2BIT_LUT01/23` registers and only uses ICSC for YCbCr or higher color-space values.
- `get_hist_rgb_luma_coefs()` chooses BT.709 or BT.2020 fixed-point luma coefficients.
- `dcn42_dpp_funcs` combines DCN401 scaler/cursor functions, DCN35 clock/bias-scale functions, DCN30 GAMCOR/CM helpers, and new histogram callbacks.

## Control flow
Histogram control writes ten fields in `CM_HIST_CNTL`. If source 2 is RGB-to-luma, it writes BT.2020 luma coefficients for 2020 RGB color spaces and BT.709 coefficients otherwise; if not, it writes pass-through green/Y coefficients. Histogram read validates the output pointer, reads the configured channel mask, checks buffer A/B ready status, locks the histogram block, resets index to zero, iterates 256 bins, reads one register per enabled channel per bin, accumulates into the caller's histogram arrays, unlocks, and returns whether data was read.

DPP setup follows the standard CNVC path: reset format controls, map surface format to pixel format/alpha defaults, derive color space, program split 2-bit alpha LUT registers for 10-bit formats, set pixel format and alpha, clear pre-dealpha/re-alpha, and call `dpp3_program_post_csc()` with caller matrix or defaults. Its adjustment path bypasses CSC for RGB-like color spaces and selects ICSC for YCbCr color spaces.

Construction stores context, instance, function/cap pointers, and DCN42 register tables. Caps advertise floating DSCL processing, 63 max line-buffer partitions, and the DCN401 partition calculator.

## State and persistence behavior
Histogram output accumulates into caller-owned `struct cm_hist`; the function does not clear bins before adding. Hardware histogram buffers, lock state, and ready status are register-backed. DPP setup and scaler/cursor state remains runtime-only in `struct dcn42_dpp`, inherited DPP shadows, and hardware registers.

## Dependencies and integration points
The file depends on `dcn42_dpp.h`, DCN401 DPP and scaler functions, DCN35 clock/bias-scale functions, DCN30 CM helpers, register helpers, and DC color/histogram structures. It integrates upward through histogram callbacks in `struct dpp_funcs` and downward through DCN42-specific histogram registers.

## Risks and edge cases
Histogram read uses logical OR of ready statuses and does not distinguish which hardware buffer is ready. It accumulates rather than assigns, so callers must clear `cm_hist` when they need per-read samples. Lock/unlock sequencing is critical to avoid reading changing bins. `dpp42_dpp_setup()` casts the base DPP to `struct dcn401_dpp` even though construction uses `struct dcn42_dpp`; this relies on identical leading layout for base/register pointers and is a maintenance hazard. The split alpha LUT registers differ from DCN401, so wrong register tables will corrupt alpha programming.

## Test signals
Validation should include DCN42 bring-up, histogram enable/read for each channel mask and tap point, RGB-to-luma coefficients for BT.709 versus BT.2020, repeated histogram reads with known accumulation behavior, CNVC format coverage including 2-bit alpha formats, post-CSC adjustment for RGB and YCbCr inputs, inherited scaler/cursor tests, and register-table layout tests for the DCN401 cast assumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.h

## Purpose
`dcn42_dpp.h` extends the DCN401 DPP register and field map for DCN42. It adds CM histogram registers/fields, split 2-bit alpha LUT register variables, and the concrete `struct dcn42_dpp` plus constructor prototype.

## Important APIs, types, and functions
- `TO_DCN42_DPP()` casts a base DPP to `struct dcn42_dpp`.
- `DPP_REG_LIST_SH_MASK_DCN42_COMMON()` is the DCN42 field-map macro, largely extending DCN401 with histogram fields and DCN42 register names.
- `DPP_REG_FIELD_LIST_DCN42()` appends histogram control/status/data/scale/bias/coefficient fields to the DCN401 field list.
- `DPP_REG_VARIABLE_LIST_DCN42` adds `ALPHA_2BIT_LUT01`, `ALPHA_2BIT_LUT23`, and CM histogram registers to the DCN401 variable list.
- `struct dcn42_dpp_registers`, `struct dcn42_dpp_shift`, `struct dcn42_dpp_mask`, and `struct dcn42_dpp` define the DCN42 table and object layouts.
- `dpp42_construct()` is the constructor consumed by resource code.

## Control flow
The header has no executable flow. Its macros generate register table shape, while the struct definitions and constructor prototype are consumed by `dcn42_dpp.c` and ASIC resource construction.

## State and persistence behavior
`struct dcn42_dpp` mirrors `struct dcn401_dpp` in layout style: it stores base DPP, register tables, cached filter pointers, line-buffer properties, scaler data, and PWL data. Histogram state itself is hardware-register-backed and caller-buffer-backed, not stored in the DPP object. No durable persistence exists.

## Dependencies and integration points
The header depends on `dcn401/dcn401_dpp.h` and therefore inherits DCN401/DCN30/DCN32 types. It integrates with DCN42 resource files that instantiate register lists and with DPP histogram callbacks implemented in `dcn42_dpp.c`.

## Risks and edge cases
The macro is very large and inherits all DCN401 map fragility while adding histogram fields. It duplicates some field entries such as `CM_HIST_DATA`, and also includes both DCN401 and DCN42 alpha LUT naming. `dcn42_dpp.c` relies on structural compatibility with `struct dcn401_dpp` in at least one cast, so changing field order in `struct dcn42_dpp` can break runtime register access. Histogram field masks must match hardware bin read sequencing.

## Test signals
Compile coverage for DCN42 ASIC register tables, DPP construction, histogram callback linkage, alpha LUT programming, inherited DCN401 scaler/cursor paths, and runtime histogram read/control tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/Makefile

## Purpose
This Makefile contributes Display Stream Compression sources to `AMD_DISPLAY_FILES` for the AMD Display Core build. It conditionally includes DCN generation-specific DSC implementations when floating-point DC support is enabled and always includes common DSC rate-control/calculation files.

## Important APIs, types, and functions
- Under `CONFIG_DRM_AMD_DC_FP`, `DSC_DCN20`, `DSC_DCN35`, and `DSC_DCN401` list generation-specific objects: `dcn20_dsc.o`, `dcn35_dsc.o`, and `dcn401_dsc.o`.
- `DSC` lists common objects: `dc_dsc.o`, `rc_calc.o`, and `rc_calc_dpi.o`.
- `AMD_DISPLAY_FILES += $(addprefix $(AMDDALPATH)/dc/dsc/..., ...)` appends all selected objects to the driver build.

## Control flow
Kbuild evaluates the conditional. If `CONFIG_DRM_AMD_DC_FP` is set, it appends DCN20/DCN35/DCN401 DSC implementation objects from their subdirectories. Regardless of that option, it appends common DSC objects under `dc/dsc/`.

## State and persistence behavior
The file has build-time state only through make variables. It does not create runtime state or persistence.

## Dependencies and integration points
It depends on the AMD Display Core Kbuild variable convention (`AMD_DISPLAY_FILES`, `AMDDALPATH`) and the `CONFIG_DRM_AMD_DC_FP` configuration symbol. It integrates DSC object files into the larger amdgpu display driver link.

## Risks and edge cases
Renaming or moving DSC source files without updating this Makefile will cause missing-object build failures. Generation-specific DSC is omitted when floating-point DC support is disabled, so references to those symbols must be similarly conditional. The `DSC_DCN401 +=` assignment is append-style even though it is first use; harmless, but different from the `=` style used for DCN20/DCN35.

## Test signals
Build tests with `CONFIG_DRM_AMD_DC_FP=y` and disabled should verify that the correct object sets are included and that common DSC objects always link. Generation-specific DSC feature tests should cover DCN20, DCN35, and DCN401 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/Makefile -->
