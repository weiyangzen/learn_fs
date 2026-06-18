# subset-b-001452 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h

## Purpose
`dcn42_mpc.h` is the DCN 4.2 Multiple Plane/Pixel Combiner register-contract header. It extends the DCN 4.01 MPC definitions with the register lists, field masks, shift structures, and public function prototypes needed to program MPCC blending, output color-space conversion, output gamma, movable color-management blocks, and the newer RMCM shaper/3D LUT/gamut-remap path.

## Important APIs, types, and functions
The key type is `struct dcn42_mpc`, which embeds `struct mpc` and stores MPCC use tracking, MPCC/RMU counts, and pointers to register, shift, and mask tables. `struct dcn42_mpc_registers`, `struct dcn42_mpc_shift`, and `struct dcn42_mpc_mask` are generated from large macro lists. Construction and MPCC setup are declared through `dcn42_mpc_construct()` and `mpc42_init_mpcc()`. RMCM programming APIs include shaper LUT programming/configuration, 3D LUT power and fast-load selection, LUT read/write control, LUT mode, 3D LUT size, fast-load bias/scale, bit-depth programming, and `mpc42_set_fl_config()`. State/readback hooks include `mpc42_read_mpcc_state()` and `mpc42_update_blending()`.

## Control flow
This header has no executable control flow, but it defines the metadata consumed by the DCN42 MPC implementation. Driver initialization supplies register arrays and field metadata to `dcn42_mpc_construct()`. Runtime MPC operations use the macros to resolve per-instance MPCC, MCM, OCSC, OGAM, DWB mux, flow-control, and RMCM registers before issuing `REG_*` helper writes. The RMCM functions form a typical sequence of powering memory, programming shaper/3D LUT region parameters and LUT data, selecting banks, enabling fast load, and enabling the active LUT mode.

## State and persistence behavior
All state is volatile display-driver and hardware-register state. The header describes software-side fields such as `mpcc_in_use_mask`, `num_mpcc`, and `num_rmu`, plus hardware register addresses and bitfields. It persists nothing across driver unload, suspend, or reboot; correctness depends on initialization and mode-set paths repopulating hardware state.

## Dependencies and integration points
The file depends on `dcn401/dcn401_mpc.h`, the AMD DC register macro system (`SF`, `SRII`, `MPC_REG_*`), `struct dc_context`, `struct mpcc`, `struct pwl_params`, `struct pwl_result_data`, color-management LUT types, and common MPC/MPCC abstractions. It integrates with resource construction, color-management programming, plane blending, display writeback muxing, and DCN42-specific fast 3D LUT load paths.

## Risks and edge cases
Most risk is hardware ABI drift: field names, instance arrays, and mask/shift declarations must match generated register headers. The repeated RAMA/RAMB region lists and MCM/RMCM field blocks are easy to desynchronize. `MAX_MPCC`-sized arrays assume the implementation never indexes beyond hardware MPCC count. Fast-load status/underflow fields require careful sequencing so partial 3D LUT updates do not become visible. The TODO in the RMCM register list notes possible missing 3D LUT registers.

## Test signals
Useful signals include DCN42 build coverage, display bring-up with multiple planes, MPCC blend and background-color tests, output CSC/OGAM/MCM/RMCM color-management validation, RMCM shaper and 3D LUT programming with both banks, fast-load completion and underflow checks, DWB mux validation, and suspend/resume or hotplug mode-set tests that force reconstruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mpc/dcn42/dcn42_mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/Makefile

## Purpose
This Kbuild fragment adds AMD DC output pixel processor implementations to `AMD_DISPLAY_FILES` when `CONFIG_DRM_AMD_DC_FP` is enabled. It covers DCN10, DCN20, and DCN35 OPP generations.

## Important APIs, types, and functions
The file has no C APIs. Its important build variables are `OPP_DCN10`, `AMD_DAL_OPP_DCN10`, `OPP_DCN20`, `AMD_DAL_OPP_DCN20`, `OPP_DCN35`, and `AMD_DAL_OPP_DCN35`, each mapping generation-local object names to paths under `$(AMDDALPATH)/dc/opp/...`.

## Control flow
Kbuild evaluates the block only under `ifdef CONFIG_DRM_AMD_DC_FP`. Each object list is prefixed with its source directory and appended to `AMD_DISPLAY_FILES`, which is later consumed by the parent AMD display build.

## State and persistence behavior
There is no runtime state. The file only controls compile-time object selection.

## Dependencies and integration points
It depends on the kernel build system, `CONFIG_DRM_AMD_DC_FP`, `AMDDALPATH`, and the presence of `dcn10_opp.o`, `dcn20_opp.o`, and `dcn35_opp.o`. It integrates the OPP implementation layer into the larger DC object set.

## Risks and edge cases
If a generation object is renamed, moved, or added without updating this file, that OPP implementation will not link. The file intentionally gates floating-point DC code; build configurations without `CONFIG_DRM_AMD_DC_FP` omit these objects.

## Test signals
Build tests with AMD DC FP enabled should compile and link the three OPP object files. Missing-object, disabled-config, and incremental-build coverage are the relevant validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.c

## Purpose
`dcn10_opp.c` implements the DCN1.0 output pixel processor. It programs FMT bit-depth reduction, spatial dithering, clamping, pixel encoding, dynamic expansion, stereo OPP buffer parameters, pipe clock control, and basic register-state readback.

## Important APIs, types, and functions
Public functions wired into `struct opp_funcs` are `opp1_set_dyn_expansion()`, `opp1_program_fmt()`, `opp1_program_bit_depth_reduction()`, `opp1_program_stereo()`, `opp1_pipe_clock_control()`, `opp1_destroy()`, and `opp1_read_reg_state()`. Internal helpers include `opp1_set_truncation()`, `opp1_set_spatial_dither()`, `opp1_set_pixel_encoding()`, `opp1_set_clamping()`, and `opp1_program_clamping_and_pixel_encoding()`. `dcn10_opp_construct()` binds context, instance, register tables, masks, shifts, and the function table.

## Control flow
`opp1_program_fmt()` optionally releases 4:2:0 map memory from forced power mode, then programs bit-depth reduction before clamping and pixel encoding because dithering depends on the CRTC source selection. Bit-depth reduction first writes truncation controls, then disables old dither state, configures frame-random counters and seeds, and enables requested spatial-dither fields. Pixel encoding maps RGB/YCbCr444 to 4:4:4, YCbCr422 to subsampling mode 2, and YCbCr420 to pixel encoding 2 with CbCr bit reduction bypass, unless the debug option forces 1-tap chroma subsampling. Dynamic expansion only enables 8-to-12 or 10-to-12 expansion for HDMI, DP, MST, and virtual signals when `opp->dyn_expansion` permits it.

## State and persistence behavior
The implementation stores no durable state. `struct dcn10_opp` keeps pointers to immutable register metadata and a base `output_pixel_processor`. Runtime state is hardware register state in FMT, OPPBUF, and OPP_PIPE blocks. `opp1_destroy()` frees the allocated OPP object.

## Dependencies and integration points
The file depends on AMD DC core types, `dm_services`, `reg_helper`, OPP interface types from `opp.h`, color/depth/timing enums, and debug flags under `dc->debug`. It is constructed by resource code and called by pipe/mode programming code before data reaches OPTC/stream encoder blocks.

## Risks and edge cases
Dither programming has depth-specific frame-counter settings and silently returns for unsupported depth. Clamping has an unimplemented programmable case. Stereo active width subtracts `h_border_right` twice, which may be intentional or legacy but is a maintenance risk. Dynamic expansion is signal-type gated. Debug-forced 1-tap chroma subsampling can override normal 4:2:2/4:2:0 setup.

## Test signals
Mode-set tests across RGB, YCbCr444, YCbCr422, and YCbCr420; 6/8/10/12 bpc output; dither/truncation enable combinations; debug forced chroma subsampling; dynamic-expansion signal coverage; stereo timing formats; and register readback through `opp_read_reg_state()` are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h

## Purpose
`dcn10_opp.h` defines the DCN1.0 OPP private structure, register-list macros, field mask/shift lists, and function prototypes used by `dcn10_opp.c` and later OPP generations.

## Important APIs, types, and functions
Key macros are `TO_DCN10_OPP()`, `OPP_SF()`, `OPP_REG_LIST_DCN()`, `OPP_REG_LIST_DCN10()`, `OPP_COMMON_REG_VARIABLE_LIST`, `OPP_MASK_SH_LIST_DCN()`, `OPP_MASK_SH_LIST_DCN10()`, and `OPP_DCN10_REG_FIELD_LIST()`. Types include `struct dcn10_opp_registers`, `struct dcn10_opp_shift`, `struct dcn10_opp_mask`, and `struct dcn10_opp`. Prototypes expose construction, format programming, bit-depth reduction, stereo, pipe clock control, destruction, and register readback.

## Control flow
The header has no executable flow. It supplies the generated register metadata consumed by register-helper macros in the C file. Later headers include it to inherit common FMT/OPPBUF/OPP_PIPE definitions.

## State and persistence behavior
`struct dcn10_opp` carries runtime object identity, register metadata, and `is_write_to_ram_a_safe`; persistent display state lives in hardware registers programmed through the C implementation.

## Dependencies and integration points
It depends on `opp.h`, AMD register naming macros such as `SRI`, and shared DC color/timing structures referenced by function prototypes. It integrates with DC resource factories and later OPP generations.

## Risks and edge cases
Register field macros must match hardware-generated register definitions. `OPP_COMMON_REG_VARIABLE_LIST` includes `OPP_PIPE_CRC_CONTROL` although DCN10 function code mostly reads it for diagnostics. Fields for OPPBUF segmentation are declared even when generation-specific behavior is minimal.

## Test signals
Compile coverage across DCN10 and derived generations, successful register-table initialization, and mode-set paths that touch every declared FMT/OPPBUF/OPP_PIPE field are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn10/dcn10_opp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.c

## Purpose
`dcn20_opp.c` extends the DCN10 OPP implementation with DCN2.0 display pattern generator support, DPG blank-color helpers, DPG pending/blanked status checks, 4:2:2 left-edge extra-pixel programming, and expanded register readback.

## Important APIs, types, and functions
DCN20-specific functions include `opp2_set_disp_pattern_generator()`, `opp2_program_dpg_dimensions()`, `opp2_dpg_set_blank_color()`, `opp2_dpg_is_blanked()`, `opp2_dpg_is_pending()`, `opp2_program_left_edge_extra_pixel()`, `opp2_get_left_edge_extra_pixel_count()`, `opp2_read_reg_state()`, and `dcn20_opp_construct()`. The function table reuses DCN10 format, dynamic-expansion, stereo, pipe-clock, and destroy functions.

## Control flow
Pattern programming starts by translating requested color depth to DPG bit-depth, then writes active dimensions and offset. Color-square modes choose VESA/CEA dynamic range and RGB/YCbCr601/YCbCr709 mode. Bar modes scale 16-bit white/black source colors to the requested bpc, left-align the data in DPG color registers, and enable vertical or horizontal bars. Color-ramp mode computes ramp increments from source and destination bpc. Video mode disables DPG state, and solid-color mode programs both color slots to the supplied blank color before enabling a horizontal-bar generator. Left-edge extra-pixel programming writes one extra pixel only for non-primary 4:2:2/4:2:0 paths when 1-tap subsampling is not forced.

## State and persistence behavior
State is hardware-resident in DPG, FMT_422, OPPBUF, OPP_PIPE, and DSCRM registers. `struct dcn20_opp` stores register metadata and inherits the OPP base; there is no persistent state outside runtime memory and register programming.

## Dependencies and integration points
The file depends on DCN10 OPP helpers, DPG register definitions, `controller_dp_test_pattern`, `controller_dp_color_space`, `dc_color_depth`, `tg_color`, and debug flags under the DC context. It integrates with link training/test-pattern flows, blanking flows, and chroma-subsampling pipe programming.

## Risks and edge cases
DPG color values must be left-aligned to the hardware format; wrong shifts cause visibly incorrect patterns. `opp2_dpg_is_blanked()` checks DPG enable and double-buffer pending rather than color content. Left-edge extra-pixel behavior depends on primary/secondary pipe roles and debug overrides. Solid color uses horizontal bars with identical colors, so accidental mismatched color slots would show a pattern.

## Test signals
DP test-pattern compliance for color squares, CEA color squares, bars, ramps, video mode, and solid color; DPG pending/blanked polling; 4:2:2 and 4:2:0 secondary-pipe chroma tests; and readback of `DSCRM_DSC_FORWARD_CONFIG` and FMT/DPG registers provide useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h

## Purpose
`dcn20_opp.h` defines DCN2.0 OPP register metadata and prototypes, extending DCN10 with DPG, FMT_422 left-edge, OPPBUF_CONTROL1, and DSC forward-state readback support.

## Important APIs, types, and functions
Important macros include `TO_DCN20_OPP()`, `OPP_DPG_REG_LIST()`, `OPP_REG_LIST_DCN20()`, `OPP_REG_VARIABLE_LIST_DCN2_0`, `OPP_DPG_MASK_SH_LIST()`, `OPP_MASK_SH_LIST_DCN20()`, and `OPP_DCN20_REG_FIELD_LIST()`. Types are `struct dcn20_opp_registers`, `struct dcn20_opp_shift`, `struct dcn20_opp_mask`, and `struct dcn20_opp`. Prototypes expose DPG programming/status, blank color, left-edge pixel programming, source count, register readback, and construction.

## Control flow
The header itself has no control flow. It expands register tables consumed by DCN20 implementation functions and by later generations such as DCN35.

## State and persistence behavior
The `dcn20_opp` object stores the base OPP, register metadata, and `is_write_to_ram_a_safe`. Display state is transient hardware register state.

## Dependencies and integration points
It includes `dcn10/dcn10_opp.h` and relies on AMD DC register macros and OPP interface types. It is the inheritance point for DCN35 OPP and an integration surface for DPG users.

## Risks and edge cases
DPG register fields must remain aligned with hardware headers. The DPG status field is double-buffer pending, not a full pattern-state audit. Derived generations must cast compatible register and mask/shift layouts.

## Test signals
Build coverage for DCN20 and DCN35, DPG pattern programming tests, FMT_422 left-edge tests, and register readback coverage validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn20/dcn20_opp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.c

## Purpose
`dcn35_opp.c` is a thin DCN3.5 OPP specialization. It reuses DCN20 construction and behavior while adding fine-grain clock-gating control and expanded register-state readback for ABM.

## Important APIs, types, and functions
The exported functions are `dcn35_opp_construct()`, `dcn35_opp_set_fgcg()`, and `dcn35_opp_read_reg_state()`. The file casts DCN35 register/shift/mask structures to DCN20-compatible structures for construction, then uses DCN35-specific register access macros for the additional fields.

## Control flow
Construction delegates directly to `dcn20_opp_construct()`. Fine-grain clock gating writes `OPP_FGCG_REP_DIS` in `OPP_TOP_CLK_CONTROL` with the inverse of the requested enable flag. Register-state readback reads DPG, FMT, ABM, pipe control, pipe CRC, OPPBUF, and DSC forward configuration.

## State and persistence behavior
No durable state is introduced. The extra state is hardware register state in `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`.

## Dependencies and integration points
The file depends on `dcn35_opp.h`, DCN20 OPP layout compatibility, `reg_helper`, and `struct dcn_opp_reg_state`. It integrates with power-management/clock-gating code and diagnostics that inspect ABM and OPP state.

## Risks and edge cases
The construction cast assumes DCN35 register, shift, and mask layouts begin with the DCN20 fields in the same order. Misuse of `enable` in `dcn35_opp_set_fgcg()` would invert clock-gating behavior. Readback assumes all registers are valid for the DCN35 instance.

## Test signals
DCN35 build and boot, FGC G enable/disable register checks, display mode-set with inherited DCN20 paths, ABM state readback, and power-gating regression tests are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.h

## Purpose
`dcn35_opp.h` declares the DCN3.5 OPP register extension over DCN20, adding top clock-control and ABM-control registers plus the fine-grain clock-gating field.

## Important APIs, types, and functions
Key macros are `OPP_REG_VARIABLE_LIST_DCN3_5`, `OPP_MASK_SH_LIST_DCN35()`, and `OPP_DCN35_REG_FIELD_LIST()`. Types are `struct dcn35_opp_registers`, `struct dcn35_opp_shift`, and `struct dcn35_opp_mask`. Prototypes expose `dcn35_opp_construct()`, `dcn35_opp_set_fgcg()`, and `dcn35_opp_read_reg_state()`.

## Control flow
The header has no executable control flow. It defines a layout compatible with DCN20 plus DCN35 additions, enabling the C file to delegate most behavior to DCN20.

## State and persistence behavior
Runtime state is stored in OPP hardware registers. The header itself only describes register addresses and field masks.

## Dependencies and integration points
It includes `dcn20/dcn20_opp.h` and integrates with DCN35 resource construction, clock-gating policy, ABM diagnostics, and the common OPP function interface.

## Risks and edge cases
The anonymous struct in `OPP_DCN35_REG_FIELD_LIST()` must remain compatible with how the implementation casts to DCN20 metadata. Missing DCN35-specific mask fields would make FGC G programming a no-op or corrupt another field.

## Test signals
Compile coverage, DCN35 register-table initialization, FGC G toggling, and OPP readback validation are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/opp/dcn35/dcn35_opp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/Makefile

## Purpose
This Kbuild fragment adds AMD DC output timing controller implementations to `AMD_DISPLAY_FILES` when `CONFIG_DRM_AMD_DC_FP` is enabled. It covers DCN10, DCN20, DCN201, DCN30, DCN301, DCN31, DCN314, DCN32, DCN35, DCN401, and DCN42.

## Important APIs, types, and functions
There are no runtime APIs. Important variables are the per-generation object lists, such as `OPTC_DCN10`, `OPTC_DCN20`, `OPTC_DCN201`, `OPTC_DCN30`, `OPTC_DCN301`, through `OPTC_DCN42`, and their `AMD_DAL_OPTC_*` path-prefixed forms.

## Control flow
When the config symbol is set, each object list is prefixed with `$(AMDDALPATH)/dc/optc/<generation>/` and appended to the global AMD display file list. Parent Kbuild logic later compiles and links the selected objects.

## State and persistence behavior
The file has build-time state only and no runtime persistence.

## Dependencies and integration points
It depends on Kbuild, `CONFIG_DRM_AMD_DC_FP`, `AMDDALPATH`, and the generation directories. It integrates timing-generator support into the AMD display core.

## Risks and edge cases
The file must be kept in sync with available generation directories and Kconfig expectations. Adding a new OPTC generation without appending it here prevents it from linking; retaining a removed object breaks builds.

## Test signals
Builds with AMD DC FP enabled should compile every listed generation object. Configuration coverage with the symbol disabled should omit them cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.c

## Purpose
`dcn10_optc.c` implements the base DCN timing generator/OPTC behavior. It programs mode timing, global sync, VTG parameters, CRTC enable/disable, blanking, clocks, update locks, reset triggers, dynamic refresh rate, test patterns, stereo, CRC, underflow handling, and hardware state readback.

## Important APIs, types, and functions
Major APIs include `optc1_program_timing()`, `optc1_program_global_sync()`, vertical interrupt setup functions, `optc1_enable_crtc()`, `optc1_disable_crtc()`, `optc1_enable_optc_clock()`, `optc1_set_blank()`, `optc1_validate_timing()`, lock/unlock helpers, reset-trigger helpers, `optc1_set_drr()`, `optc1_set_vtotal_min_max()`, `optc1_get_crtc_scanoutpos()`, stereo helpers, `optc1_read_otg_state()`, `optc1_get_hw_timing()`, CRC configure/read helpers, `optc1_is_two_pixels_per_container()`, and `dcn10_timing_generator_init()`.

## Control flow
Mode programming copies and patches timing to enforce front-porch minimums, writes H/V totals, sync widths, blank start/end, sync polarities, interlace state, VTG state, global sync, data format, and horizontal timing division for 4:2:0 or ODM-like cases. Enable selects the OPTC source, enables VTG, and turns on OTG master enable through a register sequence. Disable clears master enable, disables VTG, and waits for OTG not busy. DRR writes mid/min/max totals and selectors, then configures manual trigger. CRC configuration validates that the timing generator is enabled, programs windows per engine, and enables continuous or one-shot CRC.

## State and persistence behavior
`struct optc` stores cached timing parameters such as vready/vstartup/vupdate and original patched timing, plus capability bounds initialized from masks. Hardware state is in OTG, VTG, OPTC input, CRC, and trigger registers. There is no durable persistence.

## Dependencies and integration points
The file depends on `reg_helper`, `dcn10_optc.h`, `dc.h`, tracing, timing-generator interfaces, DC timing/color enums, and register sequence helpers. It is the base function-table provider reused by DCN20, DCN201, DCN30, and DCN301.

## Risks and edge cases
Timing arithmetic is sensitive to off-by-one hardware conventions. Interlace validation is blocked even though some programming paths contain interlace handling. `vstartup_start == 0` triggers debugger break. Underflow is cleared during unblank as a test workaround, which can hide transient events. CRC is unavailable while the CRTC is disabled. Manual trigger and reset-trigger programming depends on correct source pipe and edge polarity.

## Test signals
Mode validation and programming across common timings, DP/HDMI/eDP signals, 4:2:0 and DSC 4:2:2 native timing division, CRTC enable/disable and blank/unblank, vblank counter/scanout position, DRR min/max/mid updates, CRC window capture, stereo modes, reset synchronization, and underflow clear/readback are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.h

## Purpose
`dcn10_optc.h` is the central OPTC register metadata header. It defines common DCN timing-generator register lists, register variable storage, mask/shift lists, field-list macros, and the `dcn_optc_registers`, `dcn_optc_shift`, and `dcn_optc_mask` structures used across many generations.

## Important APIs, types, and functions
Important macros include `DCN10TG_FROM_TG()`, `TG_COMMON_REG_LIST_DCN()`, `TG_COMMON_REG_LIST_DCN1_0()`, `OPTC_REG_VARIABLE_LIST_DCN`, `OPTC_REG_VARIABLE_LIST_DCN42`, `TG_COMMON_MASK_SH_LIST_DCN()`, `TG_COMMON_MASK_SH_LIST_DCN1_0()`, `TG_REG_FIELD_LIST_DCN1_0()`, and `TG_REG_FIELD_LIST()`. It also defines extension field-list macros for DCN2.0, DCN3.2, DCN3.5, DCN3.6, DCN401, and DCN42. The only function prototype is `dcn10_timing_generator_init()`.

## Control flow
The header has no executable control flow. It enables the C files to use generic `REG_*` helpers over generation-specific address and bitfield tables. Later generation headers reuse or extend these macros rather than redefining the full OTG/OPTC contract.

## State and persistence behavior
The structures hold register addresses, shifts, and masks in kernel memory. The hardware state they describe is volatile timing-generator state. No persistent storage is involved.

## Dependencies and integration points
It includes `optc.h` and depends on AMD register macro conventions (`SRI`, `SR`, `SF`). It integrates with all OPTC generation implementations and resource-construction code that instantiates register tables.

## Risks and edge cases
The header is broad and generation-spanning, so field mismatches can break many targets. There is a duplicated `OTG_DISABLE_STEREOSYNC_OUTPUT_FOR_DP` mask entry. DCN42 fields are present alongside older-generation structures, requiring careful initialization. Empty generation macros such as `V_TOTAL_REGS(type)` are extension hooks and can be mistaken for omissions.

## Test signals
Compile coverage across all OPTC generations, register-table initialization tests, mode-set smoke tests on multiple ASIC generations, CRC/readback coverage, and static checks for missing mask/shift fields provide validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn10/dcn10_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.c

## Purpose
`dcn20_optc.c` extends the base DCN10 timing generator with DCN2.0 capabilities: segmented OPTC source selection, ODM combine/bypass, DSC configuration/status, global swap lock support, DWB source selection, vblank alignment, triple buffering, double-buffer lock programming, manual trigger updates, CRC stream-mode configuration, and last-used DRR vtotal readback.

## Important APIs, types, and functions
Key functions are `optc2_enable_crtc()`, `optc2_set_gsl()`, `optc2_set_gsl_source_select()`, `optc2_set_dsc_config()`, `optc2_get_dsc_status()`, `optc2_set_odm_bypass()`, `optc2_set_odm_combine()`, `optc2_get_optc_source()`, `optc2_set_dwb_source()`, `optc2_align_vblanks()`, `optc2_triplebuffer_lock()`, `optc2_triplebuffer_unlock()`, `optc2_lock_doublebuffer_enable()`, `optc2_lock_doublebuffer_disable()`, `optc2_setup_manual_trigger()`, `optc2_program_manual_trigger()`, `optc2_configure_crc()`, `optc2_get_last_used_drr_vtotal()`, and `dcn20_timing_generator_init()`.

## Control flow
Enable selects `OPTC_SEG0_SRC_SEL`, enables VTG, and turns on OTG master enable. ODM bypass routes one OPP segment and sets H timing division based on two-pixels-per-container formats. ODM combine asserts two OPPs, derives a non-overlapping memory mask from OPP ids, sets segment sources/width, forces divide-by-two timing, and records `opp_count`. GSL functions assign OTGs to groups and select ready sources. Vblank alignment temporarily disables a slave OTG, locks it to the master, computes an X/Y unlock point from pixel clocks and totals, starts the slave at the calculated phase, then restores lock ownership. Manual trigger uses TRIGA and DMCUB-friendly min/max selectors.

## State and persistence behavior
State is held in OTG/OPTC registers and in `optc1->opp_count` for ODM width and lock calculations. There is no nonvolatile persistence.

## Dependencies and integration points
The file depends on DCN10 OPTC helpers, DCN20 register fields, `dc.h`, division helpers, GSL/ODM/DSC/DWB timing-generator interfaces, and CRC parameter structures. It integrates with multi-OPP wide-display composition, DSC stream formatting, DWB routing, and multi-display synchronization.

## Risks and edge cases
ODM combine assumes exactly two OPPs and reserves memory based on OPP ids. Vblank alignment uses integer math and direct master/slave register switching, so wrong clock inputs can misphase displays. Double-buffer lock positions subtract fixed pixel margins from blank start and depend on `opp_count`. `get_optc_source()` works around VBIOS not updating segment count by checking `SEG1 == 0xf`.

## Test signals
ODM bypass/combine modes, DSC enable/disable and CRC with DSC/ODM modes, GSL master/slave synchronization, DWB source selection, triple-buffer lock/unlock, double-buffer lock timing, manual trigger DRR, last-used DRR readback, and multi-display vblank alignment tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.h

## Purpose
`dcn20_optc.h` defines the DCN2.0 OPTC register additions and function prototypes. It extends DCN10 with global control, GSL windows, vupdate keepout, DSC start, CRC mode, ODM data format/width/memory, DWB source, manual flow control, DRR status, and pipe update status.

## Important APIs, types, and functions
Important macros are `TG_COMMON_REG_LIST_DCN2_0()` and `TG_COMMON_MASK_SH_LIST_DCN2_0()`. Prototypes expose DCN20 initialization, CRTC enable, GSL programming, DSC configuration/status, ODM bypass/combine/source readback, triplebuffer and doublebuffer locks, manual trigger setup/programming, CRC configuration, and last-used DRR vtotal readback.

## Control flow
The header has no executable control flow. It describes the extra register fields needed by `dcn20_optc.c` and later users.

## State and persistence behavior
The register and bitfield tables are runtime metadata. Hardware state is volatile OTG/OPTC state.

## Dependencies and integration points
It includes `dcn10/dcn10_optc.h` and integrates with DCN20 timing-generator construction, ODM, DSC, DWB, GSL, DRR, and CRC flows.

## Risks and edge cases
The header must stay synchronized with generated register names. DWB source fields include both DWB0 and DWB1; incorrect field mapping misroutes writeback. The mask list adds pipe-update and vupdate-keepout fields used for locking, so omissions can lead to unsafe update timing.

## Test signals
Compile coverage, register-table instantiation, ODM/DSC/GSL/DWB mode tests, and lock/update-pending tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn20/dcn20_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn201/dcn201_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn201/dcn201_optc.c

## Purpose
`dcn201_optc.c` provides a DCN2.0.1 timing-generator function table. It largely reuses DCN10/DCN20 behavior but customizes timing validation, triplebuffer locking, OPTC source readback, and minimum timing limits for the DCN201 hardware subset.

## Important APIs, types, and functions
Key local helpers are `optc201_triplebuffer_lock()`, `optc201_triplebuffer_unlock()`, `optc201_validate_timing()`, and `optc201_get_optc_source()`. `dcn201_timing_generator_init()` installs the function table and capability limits. The table reuses DCN10 timing/blanking/DRR/CRC helpers and DCN20 enable, DSC, manual-trigger, and CRC-mode helpers.

## Control flow
Triplebuffer lock selects the instance in `OTG_GLOBAL_CONTROL0`, enables vupdate keepout, asserts master update lock, and waits for lock status. Unlock clears the lock and disables keepout. Validation mirrors DCN10 checks but does not block interlace explicitly; it verifies supported 3D formats, max totals, min blanking, and sync widths. Source readback returns only `OPTC_SEG0_SRC_SEL` and sets source count to one.

## State and persistence behavior
State is volatile OTG/OPTC register state plus `struct optc` min/max capability values initialized at construction. No persistent state exists.

## Dependencies and integration points
The file depends on `dcn201_optc.h`, DCN10 and DCN20 helper functions, register helpers, and timing-generator interfaces. It integrates with DCN201 resource construction where full DCN20 ODM/DWB behavior is not exposed.

## Risks and edge cases
Minimum HSync width is initialized to 8 here, unlike DCN20/DCN30 values of 4. The source readback intentionally reports one source and ignores `src_opp_id_1`; callers expecting ODM combine state must use a different generation path. Triplebuffer lock register selection differs from DCN30.

## Test signals
DCN201 mode validation around hsync width, interlace-like timings, triplebuffer lock/unlock, DSC setup, CRC, DRR, and source readback should be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn201/dcn201_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn201/dcn201_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn201/dcn201_optc.h

## Purpose
`dcn201_optc.h` declares the DCN2.0.1 OPTC register list and mask/shift additions. It is a smaller DCN20-derived contract for hardware that exposes selected global-control, GSL, vupdate keepout, DSC, ODM, width, and DWB source fields.

## Important APIs, types, and functions
Key macros are `TG_COMMON_REG_LIST_DCN201()` and `TG_COMMON_MASK_SH_LIST_DCN201()`. The only prototype is `dcn201_timing_generator_init()`.

## Control flow
The header has no executable flow. It supplies register metadata for `dcn201_optc.c`.

## State and persistence behavior
Only volatile register metadata is described; no persistent state is defined.

## Dependencies and integration points
It includes `dcn20/dcn20_optc.h` and integrates with DCN201 timing-generator construction and shared DCN10/DCN20 helper code.

## Risks and edge cases
The mask list repeats `OPTC_DWB1_SOURCE_SELECT` and omits some DCN20 fields such as `OPTC_NUM_OF_INPUT_SEGMENT`, matching the reduced implementation. Callers must not assume full DCN20 ODM source readback.

## Test signals
Compile coverage, DCN201 register-table initialization, DSC/width programming, DWB source references, and triplebuffer behavior validate the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn201/dcn201_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.c

## Purpose
`dcn30_optc.c` specializes OPTC behavior for DCN3.0. It updates lock-register programming, supports expanded ODM combine up to four OPPs, extended blank-color registers, DRR trigger-window/change-limit controls, output mux selection, pending-status queries, and optional DMUB-mediated DRR min/max updates.

## Important APIs, types, and functions
Important functions are `optc3_triplebuffer_lock()`, `optc3_lock_doublebuffer_enable()`, `optc3_lock_doublebuffer_disable()`, `optc3_lock()`, `optc3_set_out_mux()`, `optc3_program_blank_color()`, `optc3_set_drr_trigger_window()`, `optc3_set_vtotal_change_limit()`, `optc3_set_dsc_config()`, `optc3_set_odm_bypass()`, `optc3_set_odm_combine()`, `optc3_get_optc_double_buffer_pending()`, `optc3_get_otg_update_pending()`, `optc3_get_pipe_update_pending()`, `optc3_wait_drr_doublebuffer_pending_clear()`, `optc3_set_vtotal_min_max()`, `optc3_tg_init()`, and `dcn30_timing_generator_init()`.

## Control flow
DCN30 locks select the OTG instance through `OTG_GLOBAL_CONTROL2`, program keepout, and trace lock state. Double-buffer locking computes start/end X/Y windows from current blank starts and fixed offsets, programs DIG update location, enables global update lock, and sets vupdate keepout. ODM bypass clears segments 1-3 and sets H timing division with `OTG_H_TIMING_DIV_MODE`. ODM combine accepts two or four OPPs, computes memory masks, programs segment selectors, segment width, and timing division as `opp_cnt - 1`. DRR min/max writes can be redirected through `dc_dmub_srv_drr_update_cmd()` when DMUB mclk switching is active and FAMS is enabled.

## State and persistence behavior
State is volatile register state plus `optc1->opp_count`. DMUB-mediated DRR updates also depend on runtime DC capability/debug state, but no persistent storage is used.

## Dependencies and integration points
The file depends on DCN10 and DCN20 helpers, `dcn30_optc.h`, `dc_dmub_srv`, DML/DCN30 headers, tracing, ODM/DSC/DRR interfaces, and DC debug/capability flags. It integrates with wide-display ODM, DMUB refresh-rate control, update-lock sequencing, DSC, CRC, and diagnostics.

## Risks and edge cases
Fixed lock-window offsets assume sufficient blanking; small blank intervals can underflow the programmed coordinates. Four-OPP combine memory masks are derived from OPP ids and must avoid overlap. DMUB DRR update behavior diverges from direct register writes, so debug flags change hardware programming path. `triplebuffer_unlock` reuses the DCN20 implementation while lock is DCN30-specific.

## Test signals
Two- and four-way ODM combine, ODM bypass with 4:2:0/DSC 4:2:2 native formats, lock/double-buffer update timing, blank color with extended high bits, DMUB and non-DMUB DRR paths, pending-status readback, DSC config, and output mux tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.h

## Purpose
`dcn30_optc.h` defines DCN3.0 OPTC register lists, mask/shift fields, and prototypes. It refactors DCN3 base register metadata around new global-control lock fields, extended blank color, DTO, DRR trigger/change registers, four-segment ODM selection, and update-pending status fields.

## Important APIs, types, and functions
Important macros include `OPTC_COMMON_REG_LIST_DCN3_BASE()`, `OPTC_COMMON_REG_LIST_DCN3_0()`, `OPTC_COMMON_MASK_SH_LIST_DCN3_BASE()`, `OPTC_COMMON_MASK_SH_LIST_DCN3_0()`, and `OPTC_COMMON_MASK_SH_LIST_DCN30()`. Prototypes expose DCN30 initialization, output mux, locks, DRR trigger/change controls, triplebuffer lock, blank color, DSC config, ODM bypass/combine, DRR pending wait, TG init, vtotal min/max, and update-pending queries.

## Control flow
The header has no runtime flow. It gives `dcn30_optc.c` register coverage for the DCN3 lock model, ODM segment routing, and DRR/pipe-update status.

## State and persistence behavior
It defines volatile register metadata only. Runtime state is in `struct optc` and hardware registers.

## Dependencies and integration points
It includes `dcn20/dcn20_optc.h` and integrates with DCN30 timing-generator resource construction, ODM, DSC, DRR, lock, CRC, GSL, and pending-status paths.

## Risks and edge cases
The header declares `optc3_set_timing_db_mode()` but this file set does not provide a matching non-static implementation in `dcn30_optc.c`, so users must avoid relying on that symbol unless implemented elsewhere. DCN3.0 has both `OTG_H_TIMING_DIV_BY2` and `OTG_H_TIMING_DIV_MODE` variants in mask macros, requiring correct generation selection.

## Test signals
Compile/link coverage, register-table initialization, ODM four-segment programming, lock-window programming, DRR trigger/change, pending-status reads, and DSC/CRC mode tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn30/dcn30_optc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn301/dcn301_optc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn301/dcn301_optc.c

## Purpose
`dcn301_optc.c` provides a DCN3.0.1 timing-generator function table. It reuses most DCN30 behavior but changes DRR disable behavior and manual-trigger setup.

## Important APIs, types, and functions
The DCN301-specific functions are `optc301_set_drr()`, `optc301_setup_manual_trigger()`, and `dcn301_timing_generator_init()`. The function table reuses DCN10 timing/blanking/stereo/CRC helpers, DCN20 enable/GSL/manual trigger programming, and DCN30 locks, blank color, ODM, DSC, pending-status, DMUB-aware vtotal min/max, and DRR trigger controls.

## Control flow
When DRR parameters contain valid min/max totals, `optc301_set_drr()` programs optional mid total, calls the function-table vtotal min/max hook, enables min/max selectors, clears lock/mask bits, and sets up manual trigger. When DRR is disabled or parameters are invalid, it clears min/max selectors and force-lock state, then writes vtotal min/max to zero through the active hook. Manual trigger setup programs TRIGA source 21 for the current pipe without the extra min/max selector workaround used by DCN20.

## State and persistence behavior
State is volatile OTG/OPTC register state plus the inherited `struct optc` fields. No persistent state exists.

## Dependencies and integration points
The file depends on DCN10, DCN20, and DCN30 helper implementations, `dcn301_optc.h`, DMUB service headers, DML/DCN30 headers, and tracing. It integrates with DCN301 resource construction and DRR/FAMS behavior.

## Risks and edge cases
The function table is named `dcn30_tg_funcs`, which is harmless but can confuse maintenance. DRR disable explicitly zeros min/max, which differs from DCN10/DCN30 and must match hardware expectations. Manual trigger setup omits DCN20's min/max selector workaround.

## Test signals
DRR enable/disable transitions, invalid DRR params, manual trigger behavior, DMUB and direct vtotal update paths, ODM combine/bypass, lock timing, and normal mode-set/CRC tests should be covered on DCN301 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn301/dcn301_optc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn301/dcn301_optc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn301/dcn301_optc.h

## Purpose
`dcn301_optc.h` declares the DCN3.0.1 timing-generator initialization and the two DCN301-specific helper functions for manual trigger setup and DRR programming.

## Important APIs, types, and functions
The public prototypes are `dcn301_timing_generator_init()`, `optc301_setup_manual_trigger()`, and `optc301_set_drr()`.

## Control flow
There is no executable flow. The header exposes DCN301 overrides while including both DCN20 and DCN30 OPTC contracts.

## State and persistence behavior
No state is defined. Runtime state is controlled by the implementation through hardware registers.

## Dependencies and integration points
It includes `dcn20/dcn20_optc.h` and `dcn30/dcn30_optc.h`, making DCN301 a small specialization of the DCN30 function set with DCN20 helper compatibility.

## Risks and edge cases
The header intentionally adds no new register-list macros. Any DCN301-specific register differences must be handled by the included DCN30/DCN20 metadata or resource tables.

## Test signals
Compile coverage and runtime tests of the DCN301 DRR/manual-trigger overrides validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/optc/dcn301/dcn301_optc.h -->
