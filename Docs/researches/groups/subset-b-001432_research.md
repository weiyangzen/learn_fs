# subset-b-001432 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h

## Purpose
`dcn10_dpp.h` is the register, field, object, and function contract for the DCN 1.0 display pipe processor. It defines how generated register addresses and masks are gathered into C structs, exposes the `struct dcn10_dpp` hardware object, and declares the color-management, scaler, cursor, conversion, clock, reset, and constructor entry points used by the display core.

## Important APIs, types, and functions
- Register-list macros are the core API surface: `TF_REG_LIST_DCN()`, `TF_REG_LIST_DCN10()`, `TF_REG_LIST_SH_MASK_DCN()`, and `TF_REG_LIST_SH_MASK_DCN10()` enumerate CM, DSCL, CNVC, cursor, and DPP_TOP registers and fields for a pipe instance.
- `TF_REG_FIELD_LIST(type)` expands all shared field names into either `struct dcn_dpp_shift` or `struct dcn_dpp_mask`.
- `DPP_COMMON_REG_VARIABLE_LIST` expands into `struct dcn_dpp_registers`, the register-address table consumed by `REG_*` helpers in implementation files.
- `struct dcn10_dpp` embeds the public `struct dpp` base and stores register tables, cached scaler filter pointers, line-buffer capability fields, the current scaler snapshot, and transfer-function parameters.
- Public prototypes include `dpp1_construct()`, `dpp_read_state()`, `dpp_reset()`, `dpp1_dscl_set_scaler_manual_scale()`, `dpp1_get_optimal_number_of_taps()`, `dpp1_program_input_csc()`, `dpp1_cm_set_gamut_remap()`, regamma/degamma programming helpers, cursor programming helpers, `dpp1_cnv_setup()`, `dpp1_dppclk_control()`, `dpp1_set_hdr_multiplier()`, and `dpp_force_disable_cursor()`.

## Control flow
This header has no executable flow, but it determines the implementation flow by shaping how each DPP instance is constructed and then accessed. ASIC-specific code instantiates static register, shift, and mask tables from these macros, passes them to `dpp1_construct()`, and the implementation accesses hardware by dereferencing `dpp->tf_regs`, `dpp->tf_shift`, and `dpp->tf_mask`. The `TO_DCN10_DPP()` macro downcasts a generic `struct dpp *` from the display core function table back to the DCN10 concrete object.

The declared operation set splits into several pipelines. DSCL functions consume `struct scaler_data`, derive tap and line-buffer settings, and program scaler registers. CM functions consume gamma, CSC, gamut, bias/scale, and HDR multiplier data and program the color-management registers. CNVC and cursor functions program pixel-format conversion, alpha behavior, and cursor registers. Constructor and reset/read-state functions connect those pieces to the generic DPP vtable.

## State and persistence behavior
All state is volatile kernel/hardware state. `struct dcn10_dpp` persists only while the display device is active. It caches the last filter coefficient tables (`filter_h`, `filter_v`, chroma variants) and the last `scl_data` to avoid redundant scaler programming. It also records line-buffer capabilities and a `pwl_data` scratch/cached transfer-function payload. Real display state is persisted in MMIO registers represented by the generated address/field tables; there is no disk or cross-boot persistence.

## Dependencies and integration points
The header depends on the generic display pipe processor interface in `dpp.h`, Linux `container_of`, generated ASIC register naming conventions such as `SRI()` and field macro naming, and DC fixed-point/color/scaler structures included indirectly from display core headers. It is included by DCN10 implementation files and inherited by DCN20/DCN201 headers, so additions here affect later-generation DPP code as well.

## Risks and edge cases
The biggest risk is register-contract drift. The field list is very large and spans DCN10 plus fields later reused by DCN20; a missing or incorrectly named field causes either build failures or incorrect hardware programming through a valid-looking `REG_UPDATE()`. Several fields use `TF2_SF()` to handle naming corner cases, making generated-name consistency important. The embedded object layout also matters because DCN20/DCN201 define similar but not identical objects and cast through generation-specific macros.

## Test signals
Useful validation includes building all DCN ASIC variants that include this header, display bring-up on DCN10 hardware or emulation, register trace comparison for scaler/color/cursor programming, hotplug modeset tests that exercise reset/read-state paths, and static checks that generated register headers still provide every symbol expanded by the macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_cm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_cm.c

## Purpose
`dcn10_dpp_cm.c` implements DCN 1.0 DPP color-management programming. It handles gamut remap, input and output CSC, regamma and degamma piecewise-linear LUTs, input gamma LUT, bias/scale, CM bypass, and HDR multiplier programming through the DCN10 register tables.

## Important APIs, types, and functions
- Gamut APIs are `dpp1_cm_set_gamut_remap()` and `dpp1_cm_get_gamut_remap()`, backed by `program_gamut_remap()` and `read_gamut_remap()`.
- Output CSC APIs are `dpp1_cm_set_output_csc_default()` and `dpp1_cm_set_output_csc_adjustment()`, backed by `dpp1_cm_program_color_matrix()`.
- Regamma APIs include `dpp1_cm_power_on_regamma_lut()`, `dpp1_cm_configure_regamma_lut()`, `dpp1_cm_program_regamma_lut()`, `dpp1_cm_program_regamma_luta_settings()`, and `dpp1_cm_program_regamma_lutb_settings()`.
- Degamma APIs include `dpp1_power_on_degamma_lut()`, `dpp1_set_degamma()`, `dpp1_set_degamma_pwl()`, `dpp1_degamma_ram_select()`, `dpp1_program_degamma_lut()`, and the RAM A/B settings helpers.
- `dpp1_program_input_csc()`, `dpp1_program_bias_and_scale()`, `dpp1_program_input_lut()`, `dpp1_full_bypass()`, and `dpp1_set_hdr_multiplier()` cover the remaining CM integration points.
- The file depends heavily on `cm_helper_program_color_matrices()`, `cm_helper_read_color_matrices()`, `cm_helper_program_xfer_func()`, `convert_float_matrix()`, `convert_hw_matrix()`, and `find_color_matrix()`.

## Control flow
Gamut remap starts by bypassing when the adjustment is not software-controlled. For software matrices it converts twelve fixed-point matrix entries to hardware register values, programs either the main gamut registers or COMA/COMB registers, and then sets `CM_GAMUT_REMAP_MODE`. Readback performs the inverse by reading the active mode and matrix bank, then converting register values back to fixed-point.

Output CSC uses a double-buffer pattern. `dpp1_cm_program_color_matrix()` reads CM debug status index 9 to see which output CSC path is active, programs the alternate OCSC/COMB matrix register bank, then switches `CM_OCSC_MODE`. Input CSC follows the same idea with ICSC/COMA selection in `dpp1_program_input_csc()`, using either a default matrix from `dpp_input_csc_matrix` or a caller-provided `out_csc_color_matrix`.

Regamma and degamma PWL programming split metadata and LUT payload. The settings functions map `struct pwl_params` into per-channel start/slope/end/region registers through `xfer_func_reg`; the payload functions stream red/green/blue base and delta values into LUT data registers. `dpp1_set_degamma_pwl()` detects the currently used RAM, programs the inactive RAM, writes the payload, and flips the selected LUT mode. Input gamma writes a 256-entry LUT into the inactive IGAM RAM and then enables that RAM.

## State and persistence behavior
Runtime state is stored in hardware registers and in the DPP object only indirectly. The file reads hardware status fields to decide which double-buffered bank is active, then writes the inactive bank to avoid visible mid-frame updates. `CM_MEM_PWR_CTRL` controls LUT memory power. `dpp1_program_input_lut()` temporarily powers shared memory, writes the selected IGAM RAM, powers memory back down, and changes `CM_IGAM_LUT_MODE`. There is no durable persistence.

## Dependencies and integration points
The implementation integrates with the generic `struct dpp_funcs` entries declared in `dcn10_dpp.h` and installed by `dcn10_dpp.c`. It depends on `reg_helper.h` register access macros, `dcn10_cm_common.h` color matrices and helper structures, fixed-point conversion helpers, display debug flags, and the display core color types (`dc_gamma`, `pwl_params`, `dpp_grph_csc_adjustment`, `dc_bias_and_scale`).

## Risks and edge cases
Double-buffer selection depends on debug/status register encodings. If those encodings differ across ASIC revisions or masks are wrong, the driver can overwrite the active bank or switch to an unprogrammed bank. Several invalid inputs trigger `BREAK_TO_DEBUGGER()` rather than graceful fallback. `dpp1_program_input_lut()` assumes the gamma object has a suitable number of entries for the 256-entry IGAM path and warns in comments that values beyond 8 bits per channel are truncated. Power-control semantics are subtle: `SHARED_MEM_PWR_DIS` is written with different values depending on whether memory should be accessible or disabled.

## Test signals
Test signals include CSC/gamut matrix programming with readback, rapid color-space changes while scanning out, PWL degamma/regamma transitions between RAM A and RAM B, bypass and hardware sRGB/xvYCC degamma modes, 256-entry input gamma programming, HDR multiplier changes, CM bypass toggling, register traces around memory power transitions, and visual/CRC tests for YCbCr and RGB conversion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_dscl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_dscl.c

## Purpose
`dcn10_dpp_dscl.c` implements the DCN 1.0 DPP scaler and line-buffer programming path. It selects scaler mode based on format and ratios, powers DSCL LUT memory, chooses line-buffer partitioning, programs manual scale ratios and initial phases, loads filter coefficients, and caches scaler state to avoid redundant programming.

## Important APIs, types, and functions
- The primary entry point is `dpp1_dscl_set_scaler_manual_scale()`.
- Public helpers are `dpp1_dscl_calc_lb_num_partitions()` and `dpp1_dscl_is_lb_conf_valid()`.
- Mode and format helpers include `dpp1_dscl_get_pixel_depth_val()`, `dpp1_dscl_is_video_format()`, `dpp1_dscl_is_420_format()`, and `dpp1_dscl_get_dscl_mode()`.
- Filter helpers include `dpp1_dscl_get_filter_coeffs_64p()`, `dpp1_dscl_set_scaler_filter()`, and `dpp1_dscl_set_scl_filter()`.
- Line-buffer helpers include `dpp1_dscl_set_lb()`, `dpp1_dscl_get_lb_depth_bpc()`, and `dpp1_dscl_find_lb_memory_config()`.
- Geometry helpers are `dpp1_dscl_set_manual_ratio_init()` and `dpp1_dscl_set_recout()`.

## Control flow
`dpp1_dscl_set_scaler_manual_scale()` first compares the incoming `scaler_data` to the cached `dpp->scl_data`; if unchanged, it returns immediately. It derives a DSCL mode from scaling ratios, pixel format, `always_scale`, and fixed/float data-processing capability. If low-power DSCL memory is enabled and the mode is not full bypass, it powers the DSCL block on.

The function disables AutoCal, clears boundary mode, programs RECOUT and MPC size, writes `DSCL_MODE`, and exits early for full DSCL bypass. Otherwise it finds a line-buffer memory configuration by testing configs 1, 2, optionally 3 for 4:2:0, and finally config 0 against vertical ratio/tap requirements. It programs the line buffer, returns for 4:4:4 bypass, sets black offsets for RGB or YCbCr, writes manual scale ratios and initial phases, programs tap counts, and finally calls `dpp1_dscl_set_scl_filter()`.

The filter path enables hardcoded 2-tap coefficients when both luma/chroma tap counts qualify, otherwise it fetches 64-phase filter tables for luma and optional chroma. It compares table pointers against cached pointers in `struct dcn10_dpp`; when any table changed, it writes coefficient RAM and toggles `SCL_COEF_RAM_SELECT` to swap RAMs.

## State and persistence behavior
State is volatile and split between MMIO registers and the `struct dcn10_dpp` cache. `dpp->scl_data` records the last programmed scaler request. `filter_h`, `filter_v`, `filter_h_c`, and `filter_v_c` record the last coefficient table pointers. Low-power behavior can defer DSCL disable by setting `dpp->base.deferred_reg_writes.bits.disable_dscl` and `dc->optimized_required` instead of immediately forcing memory power off. No state survives driver unload or reboot.

## Dependencies and integration points
The file depends on `reg_helper.h`, `dcn10_dpp.h`, fixed-point conversion helpers (`dc_fixpt_*`), scaler filter tables (`get_filter_*tap_64p()`), display core debug flags, `struct scaler_data`, `struct line_buffer_params`, pixel-format enums, and `dpp_caps` callbacks. `dcn20_dpp.c` and `dcn201_dpp.c` reuse this DCN10 scaler entry point while providing generation-specific line-buffer partition calculations through their caps.

## Risks and edge cases
Line-buffer calculations rely on hardware-specific memory constants and clamp partitions to 64. Incorrect pixel depth, alpha, 4:2:0, or recout/viewport handling can select an insufficient buffer configuration. Exact zero widths are coerced to one to avoid division by zero. Ratios and taps must be consistent with hardware limits; invalid tap counts trigger debugger breaks in filter selection. The `memcmp()` cache assumes all relevant scaler state is represented deterministically in `struct scaler_data`, including no uninitialized padding.

## Test signals
Useful tests include identity scaling, RGB scaling, YCbCr 4:4:4 scaling, 4:2:0 luma/chroma bypass combinations, high downscale ratios requiring 8 taps, 1-tap and 2-tap paths, sharpness programming, alpha-enabled line-buffer partitioning, low-power DSCL enable/disable flows, and register trace or CRC validation across repeated modesets to confirm cache hits do not skip needed programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn10/dcn10_dpp_dscl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.c

## Purpose
`dcn20_dpp.c` wires the DCN 2.0 DPP object into the generic display core. It implements DCN20-specific state readback, output-buffer power control, pixel-format converter setup, line-buffer partition math, alpha color keyer programming, cursor attribute programming, dummy legacy callbacks, the DCN20 DPP function table, caps, and constructor.

## Important APIs, types, and functions
- Lifecycle/integration APIs are `dpp20_read_state()`, `dpp2_construct()`, and the static `dcn20_dpp_funcs`/`dcn20_dpp_cap`.
- Power and setup APIs include `dpp2_power_on_obuf()` and the static `dpp2_cnv_setup()`.
- Scaler support is provided by `dscl2_calc_lb_num_partitions()` and `dscl2_spl_calc_lb_num_partitions()`, while actual scaler programming reuses `dpp1_dscl_set_scaler_manual_scale()`.
- Pixel/color conversion helpers include `dpp2_cnv_set_alpha_keyer()`, `dpp2_set_cursor_attributes()`, `dpp2_dummy_program_input_lut()`, and `oppn20_dummy_program_regamma_pwl()`.
- The function table binds DCN20 color APIs from `dcn20_dpp_cm.c` such as `dpp2_cm_set_gamut_remap()`, `dpp2_set_degamma_pwl()`, `dpp20_program_blnd_lut()`, `dpp20_program_shaper()`, and `dpp20_program_3dlut()`.

## Control flow
Construction fills the generic DPP base with context, instance, function table, and caps, then stores DCN20 register, shift, and mask tables. It enables all standard line-buffer depths and records the inherited line-buffer entry size/count.

`dpp2_cnv_setup()` configures the converter by clearing bypass, setting expansion mode and fixed format-control defaults, mapping `surface_pixel_format` enums to hardware pixel-format codes, choosing alpha enablement, picking default YCbCr color space for video formats, optionally programming the two-bit alpha LUT, writing `CNVC_SURFACE_PIXEL_FORMAT`, and invoking `dpp2_program_input_csc()` with either caller-provided CSC adjustment or default matrix selection. It disables cursor paths for selected packed/video formats and powers on OBUF/DSCL memory at the end.

`dpp20_read_state()` samples DPP enable, degamma mode, shaper mode, 3D LUT config, and blend gamma status into `struct dcn_dpp_state`. The line-buffer partition functions calculate how many luma/chroma/alpha lines fit for each memory config using DCN20 memory sizes and clamp results to 64.

## State and persistence behavior
State is held in the `struct dcn20_dpp` instance and in MMIO registers. The constructor initializes only in-memory object fields; setup functions program converter, cursor, keyer, power, and color/scaler registers. `dpp20_read_state()` exposes current hardware status for diagnostics or state reconstruction. There is no file-backed persistence.

## Dependencies and integration points
The file depends on `dcn20_dpp.h`, `dcn10_dpp.h` declarations reused through inheritance, `reg_helper.h`, display pixel-format/color enums, scaler structures, DC context debug state, and CM APIs implemented in `dcn20_dpp_cm.c`. It integrates with the display core through `struct dpp_funcs`, and with newer scaler-library paths through `dscl2_spl_calc_lb_num_partitions()`.

## Risks and edge cases
Pixel-format code mapping is hardware-specific and contains many packed/video formats; a wrong mapping produces corrupted scanout or incorrect channel order. For input CSC adjustment, the code copies twelve caller matrix entries but does not pass the custom table in the non-NULL-adjustment branch unless `tbl_entry` is correctly prepared, so this path is sensitive to local initialization and selection rules. Line-buffer math uses DCN20 constants and assumes 6 pixels per memory unit for luma/chroma/alpha. Dummy input LUT and regamma callbacks mean callers must use the DCN20 blend/shaper/3D LUT pipeline instead of legacy hooks.

## Test signals
Validation should cover DCN20 construction, state readback after modeset, all supported RGB/video pixel formats, two-bit alpha LUT programming, cursor disable behavior for 4:2:0 and selected 10-bit formats, OBUF power transitions, alpha color keyer ranges, line-buffer partition choices under scaling, and color pipeline tests that confirm blend/shaper/3D LUT callbacks are invoked instead of dummy legacy callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h

## Purpose
`dcn20_dpp.h` extends the DCN10 DPP contract for DCN 2.0. It adds register and field definitions for blend gamma, shaper LUT, 3D LUT, alpha keying, two-bit alpha LUT, floating conversion controls, OBUF power control, and double-buffered DCN20 CSC/gamut banks, and declares the DCN20 object and exported functions.

## Important APIs, types, and functions
- Register macros include `TF_REG_LIST_DCN20_COMMON()`, `TF_REG_LIST_DCN20_COMMON_UPDATED()`, `TF_REG_LIST_DCN20_COMMON_APPEND()`, and `TF_REG_LIST_DCN20()`.
- Field macros include `TF_REG_LIST_SH_MASK_DCN20_COMMON()`, `TF_REG_LIST_SH_MASK_DCN20_UPDATED()`, `TF_REG_LIST_SH_MASK_DCN20()`, and debug-status macros for DCN20.
- `TF_REG_FIELD_LIST_DCN2_0(type)` extends the DCN10 field list with DCN20-only fields such as blend gamma, shaper, 3D LUT, keyer, alpha LUT, conversion clamps, cursor ROM, and OBUF memory force.
- `struct dcn2_dpp_registers`, `struct dcn2_dpp_shift`, `struct dcn2_dpp_mask`, and `struct dcn20_dpp` define the concrete object contract.
- Enums `dcn20_input_csc_select` and `dcn20_gamut_remap_select` define bypass and A/B bank selections.
- Declared functions cover constructor, state readback, degamma, gamut remap, input CSC, blend LUT, shaper, 3D LUT, alpha keyer, line-buffer partition calculations, cursor attributes, OBUF power, HDR multiplier, and gamut readback.

## Control flow
As a header, this file supplies the static metadata needed by DCN20 implementation files and ASIC resource code. DCN20 register tables are built from the macros, passed into `dpp2_construct()`, and then consumed by `REG_*` helpers. Function declarations are used to populate `dcn20_dpp_funcs` and by DCN201, which reuses much of the same implementation.

The control model encoded here differs from DCN10 in color management: input CSC and gamut remap use A/B banks rather than COMA/COMB naming, while blend gamma, shaper, and 3D LUT get explicit register fields and APIs. Legacy regamma and input LUT hooks remain declared as dummy/no-op helpers in `dcn20_dpp.c`.

## State and persistence behavior
The header describes volatile state only. `struct dcn20_dpp` mirrors DCN10 cache fields for scaler filters and transfer functions, adds `dispclk_r_gate_disable`, and points to DCN20-specific register/shift/mask tables. Persistent state lives only in hardware registers while the device is powered; the software object is rebuilt on driver initialization.

## Dependencies and integration points
The header includes `dcn10/dcn10_dpp.h` and therefore inherits DCN10 register fields, macros, and function declarations. It depends on generated DCN20 register naming, display core structures, and common LUT/CSC/gamma types. It is included by `dcn20_dpp.c`, `dcn20_dpp_cm.c`, and `dcn201_dpp.h`.

## Risks and edge cases
This header has high coupling to generated hardware definitions. The append list adds B-bank CSC/gamut registers, but `struct dcn2_dpp_registers` must include matching fields or implementation code will not compile. Field masks for debug status determine active-bank readback in `dcn20_dpp_cm.c`; incorrect shifts/masks can corrupt double-buffering. Since DCN201 reuses this macro family but defines a narrower register struct, macro reuse must match that ASIC's actual register inventory.

## Test signals
Build coverage across DCN20 and DCN201 is the first signal. Runtime tests should validate every function-table callback that depends on DCN20-only fields: A/B input CSC and gamut updates, blend gamma, shaper, 3D LUT, color keyer, alpha LUT, cursor ROM enable, OBUF power, and state readback fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp_cm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp_cm.c

## Purpose
`dcn20_dpp_cm.c` implements the DCN 2.0 DPP color-management pipeline. It adapts degamma and CSC/gamut programming to DCN20 register status fields, adds blend gamma and shaper LUT programming, and programs the DCN20 3D LUT in either 17x17x17 or 9x9x9 layout with 10-bit or 12-bit channel storage.

## Important APIs, types, and functions
- Degamma APIs are `dpp2_set_degamma_pwl()` and `dpp2_set_degamma()`, backed by `dpp2_degamma_ram_inuse()` and `dpp2_program_degamma_lut()`.
- Gamut APIs are `dpp2_cm_set_gamut_remap()` and `dpp2_cm_get_gamut_remap()`, backed by DCN20 A/B `program_gamut_remap()` and `read_gamut_remap()`.
- Input CSC is handled by `dpp2_program_input_csc()`.
- Blend gamma APIs are `dpp20_program_blnd_lut()`, `dpp20_get_blndgam_current()`, `dpp20_configure_blnd_lut()`, and RAM A/B metadata/payload helpers.
- Shaper APIs are `dpp20_program_shaper()`, `dpp20_get_shaper_current()`, `dpp20_configure_shaper_lut()`, `dpp20_program_shaper_lut()`, and RAM A/B settings helpers.
- 3D LUT APIs are `dpp20_program_3dlut()`, `get3dlut_config()`, `dpp20_set_3dlut_mode()`, `dpp20_select_3dlut_ram()`, `dpp20_select_3dlut_ram_mask()`, `dpp20_set3dlut_ram12()`, and `dpp20_set3dlut_ram10()`.
- `dpp2_set_hdr_multiplier()` writes the DCN20 HDR multiplier field.

## Control flow
Degamma PWL programming is similar to DCN10 but detects the active bank from `CM_DGAM_CONFIG_STATUS` in `CM_DGAM_LUT_WRITE_EN_MASK`. It powers degamma memory through the inherited DCN10 helper, enables the CM block subject to the debug `cm_in_bypass` flag, writes the inactive RAM's transfer-function metadata and LUT payload, then flips selection with `dpp1_degamma_ram_select()`.

Gamut remap and input CSC both use DCN20 debug status index 9 through `IX_REG_GET()`. If bypass is requested they set the mode to zero. Otherwise they read the active A/B selection, program the inactive A or B register bank, and then switch the mode field. Matrix values come from caller adjustments or from `dpp_input_csc_matrix`.

Blend and shaper LUTs follow the same double-buffer model. A NULL parameter disables the block. Otherwise the current config status selects the next RAM, write masks and indices are set, transfer-function region metadata is programmed for that bank, payload values are streamed to data registers, and the mode is switched to RAM A or RAM B. The shaper packs base and delta fields into one 24-bit-ish value per color write.

`dpp20_program_3dlut()` disables on NULL, otherwise selects the inactive 3D LUT RAM, chooses 17-cube or 9-cube data from `tetrahedral_params`, chooses 10-bit packed or 12-bit paired write format, writes four LUT planes by changing the RAM selection mask, and finally enables the selected RAM/size in `CM_3DLUT_MODE`.

## State and persistence behavior
State is volatile and mostly banked in hardware. Current bank/mode status is read from config status fields before programming. LUT payloads, region metadata, and CSC matrices live in MMIO-backed RAM/register banks. No C-level persistent cache is maintained in this file; synchronization relies on hardware status fields and mode switches.

## Dependencies and integration points
The file depends on `dcn20_dpp.h`, inherited DCN10 degamma metadata helpers, `dcn10_cm_common.h`, `reg_helper.h`, fixed-point conversion helpers, `dc_lut_mode`, `pwl_params`, `tetrahedral_params`, and common CSC matrix tables. It supplies most DCN20 color callbacks installed by `dcn20_dpp.c` and reused by `dcn201_dpp.c`.

## Risks and edge cases
Bank switching is sensitive to status encodings: blend/shaper status 1/2 and gamut/ICSC A/B values must match hardware. NULL parameters disable blocks, so callers must avoid accidental NULL during transitions. The 3D LUT 12-bit path writes entries two at a time and indexes `lut[i+1]`; it assumes an even entry count. The 10-bit path packs channels into 30 bits and depends on input values already fitting 10 bits. The `is_color_channel_12bits` argument to `dpp20_set_3dlut_mode()` is unused there, with bit-depth controlled instead by the read/write control register.

## Test signals
Relevant tests include degamma PWL bank flips, gamut/input CSC A/B readback, blend LUT enable/disable and bank alternation, shaper LUT payload/segment programming, 3D LUT 17 and 9 tetrahedral modes, 10-bit and 12-bit channel writes, NULL-to-bypass transitions, HDR multiplier updates, and visual or CRC tests for HDR/color-managed planes across repeated atomic commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn20/dcn20_dpp_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn201/dcn201_dpp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn201/dcn201_dpp.c

## Purpose
`dcn201_dpp.c` implements the DCN 2.0.1 DPP variant. It largely reuses DCN10 scaler/CSC helpers and DCN20 blend/shaper/3D LUT helpers, while providing DCN201-specific converter setup, tap-selection policy, function table, caps, and constructor.

## Important APIs, types, and functions
- The exported constructor is `dpp201_construct()`.
- `dpp201_cnv_setup()` programs pixel-format conversion, default format-control fields, alpha enablement, two-bit alpha LUT, input CSC selection, cursor disable, and OBUF power.
- `dpp201_get_optimal_number_of_taps()` selects scaler tap counts and rejects unsupported scaling cases.
- The static `dcn201_dpp_funcs` table binds the generation to shared callbacks including `dpp20_read_state()`, `dpp1_dscl_set_scaler_manual_scale()`, `dpp1_cm_set_gamut_remap()`, `dpp2_set_degamma_pwl()`, `dpp20_program_blnd_lut()`, `dpp20_program_shaper()`, `dpp20_program_3dlut()`, cursor helpers, and `dpp2_cm_get_gamut_remap()`.
- The static caps object sets float-format DSCL processing and `dscl2_calc_lb_num_partitions()`.

## Control flow
`dpp201_cnv_setup()` starts by writing converter bypass and expansion mode, clears DCN20-style conversion defaults, maps the requested `surface_pixel_format` to a hardware pixel-format code, chooses default YCbCr color space and ICSC enablement for video formats, optionally writes the two-bit alpha LUT, writes pixel format and alpha enable fields, then calls `dpp1_program_input_csc()` with a DCN10-style `dcn10_input_csc_select`. Selected video formats force both cursor paths disabled. Finally it powers on OBUF through the DCN20 helper.

`dpp201_get_optimal_number_of_taps()` rejects some FP16 scaling on fixed-format DSCL caps and max-downscale source-width debug limits. It clamps exact 8.0 ratios down by one fixed-point unit because the hardware cannot program ratio 8 exactly. It fills default luma/chroma taps based on ratio ceilings, forces odd chroma horizontal taps down to the previous even value except tap 1, and reduces taps to 1 for identity ratios unless `debug.always_scale` is set.

Construction initializes the generic base, assigns the DCN201 function table and caps, stores generation-specific register tables, enables 18/24/30 bpp line-buffer depths, and records inherited line-buffer sizing constants.

## State and persistence behavior
State lives in the `struct dcn201_dpp` object and MMIO registers. The constructor sets in-memory pointers and caps. Converter setup writes persistent hardware state for the current mode until the next modeset/reset. Tap selection mutates the caller-provided `struct scaler_data` by filling `scl_data->taps` and adjusting exact-8 ratios. There is no durable persistence beyond runtime hardware state.

## Dependencies and integration points
The file depends on `dcn201_dpp.h`, inherited DCN20 register-field definitions, DCN10 CM/scaler helpers, DCN20 color and OBUF helpers, `reg_helper.h`, and display core pixel-format/scaler/debug types. It is the integration layer that lets DCN201 resource code instantiate a DPP while sharing most DCN10/DCN20 implementation.

## Risks and edge cases
This variant mixes DCN10 and DCN20 color helpers: setup uses `dpp1_program_input_csc()` and `dpp1_cm_set_gamut_remap()`, while the function table exposes DCN20 gamut readback. That split depends on DCN201 register compatibility and can be fragile if A/B bank fields differ. The FP16 scaling rejection condition uses width and height comparisons joined by `&&`; cases where only one dimension scales may bypass the rejection. `dpp201_cnv_setup()` ignores caller-provided `input_csc_color_matrix` adjustments and always passes NULL to `dpp1_program_input_csc()`, unlike DCN20 setup.

## Test signals
Tests should cover DCN201 construction, all pixel-format mappings, two-bit alpha LUT writes, cursor disable for packed/video formats, input CSC defaults for YCbCr formats, tap selection around identity ratios, exact 8.0 ratio clamping, odd chroma horizontal taps, debug `always_scale`, max-downscale rejection, FP16 scaling rejection, and inherited blend/shaper/3D LUT behavior through the function table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn201/dcn201_dpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn201/dcn201_dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn201/dcn201_dpp.h

## Purpose
`dcn201_dpp.h` defines the DCN 2.0.1 DPP object and register contract. It reuses the DCN20 register and field macro sets while providing DCN201-specific struct names, a downcast macro, and the `dpp201_construct()` declaration.

## Important APIs, types, and functions
- `TO_DCN201_DPP()` downcasts a generic `struct dpp *` to `struct dcn201_dpp *`.
- `TF_REG_LIST_DCN201()`, `TF_REG_LIST_SH_MASK_DCN201()`, and `TF_REG_FIELD_LIST_DCN201()` alias the DCN20 macro families.
- `struct dcn201_dpp_shift` and `struct dcn201_dpp_mask` expand DCN20 field lists into DCN201-named field tables.
- `struct dcn201_dpp_registers` uses `DPP_DCN2_REG_VARIABLE_LIST`, which omits the DCN20 append list for B-bank ICSC/gamut registers.
- `struct dcn201_dpp` embeds the generic DPP base, register tables, scaler filter caches, line-buffer capability fields, safe-RAM flag, scaler snapshot, and PWL data.
- `dpp201_construct()` is the constructor consumed by resource code.

## Control flow
The header has no executable control flow. It shapes how DCN201 resource code creates a DPP: generated register tables using the DCN201 macros are passed to `dpp201_construct()`, implementation callbacks downcast through `TO_DCN201_DPP()`, and shared DCN10/DCN20 helpers access registers through the stored tables.

## State and persistence behavior
State is runtime-only. `struct dcn201_dpp` mirrors the cache fields used by DCN10/DCN20 implementations: scaler coefficient table pointers, line-buffer support, last scaler data, and PWL parameters. Hardware state is represented by register addresses and masks supplied at construction and programmed later by implementation callbacks.

## Dependencies and integration points
The header includes `dcn20/dcn20_dpp.h` and inherits its dependency on `dcn10_dpp.h`, display core types, and generated register symbols. It is included by `dcn201_dpp.c` and by ASIC resource files that instantiate DCN201 DPP objects.

## Risks and edge cases
The register struct intentionally does not include `DPP_DCN2_REG_VARIABLE_LIST_CM_APPEND`, yet `dcn201_dpp.c` reuses some DCN20 color functions through the function table. Any callback that expects appended B-bank registers would be unsafe unless DCN201 never exercises that path or compatible symbols are supplied elsewhere. Macro aliasing also means DCN20 field-list changes automatically affect DCN201, which can break builds or subtly expose unsupported fields.

## Test signals
Build tests for DCN201 resource files are essential. Runtime validation should instantiate a DCN201 DPP, run setup/scaler/color function-table callbacks, verify no callback references absent register fields, and compare register traces against DCN201 hardware documentation for converter, cursor, scaler, gamut, degamma, blend, shaper, and 3D LUT paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn201/dcn201_dpp.h -->
