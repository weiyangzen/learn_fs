# Research Report: subset-b-001398

This grouped report covers AMD display-controller source files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/`. Each section preserves the source path and is delimited for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.c

## Purpose
Implements the DCE 8.0 timing-generator specialization by reusing the DCE 11 timing-generator core and overriding the timing-programming and advanced-request behavior needed by older DCE8 CRTC/DMIF hardware. It wires an instance-specific `timing_generator_funcs` table into `struct dce110_timing_generator`.

## Important APIs, Types, And Functions
The local `enum black_color_format` is defined but unused in this file. `reg_offsets[]` maps DCE8 CRTC and DCP instance register offsets for six controllers. `program_pix_dur()` computes and writes the DMIF pixel duration from `pix_clk_100hz`. `dce80_timing_generator_program_timing()` optionally programs pixel duration, then delegates mode programming to `dce110_tg_program_timing()`. `dce80_timing_generator_enable_advanced_request()` toggles legacy requestor mode and prefetch/start-line fields based on vertical sync plus front porch. `dce80_timing_generator_construct()` initializes base fields, offsets, vblank limits, porch minima, BIOS pointer, and the DCE8 function table.

## Control Flow
Construction stores caller-provided offsets, selects derived offsets from `reg_offsets[instance]`, assigns `dce80_tg_funcs`, and defines timing limits. During timing programming, VBIOS-owned modes skip `program_pix_dur()`, while driver-owned modes update `DMIF_PG0_DPG_PIPE_ARBITRATION_CONTROL1.PIXEL_DURATION` before forwarding to the DCE110 implementation. Advanced request programming reads `CRTC_START_LINE_CONTROL`, sets `CRTC_LEGACY_REQUESTOR_EN`, selects advanced start-line position `3` with prefetch disabled for very short vertical blanking, otherwise position `4` with prefetch enabled, and forces progressive/interlace early start flags.

## State And Persistence
Persistent state is hardware register state and fields inside the provided `dce110_timing_generator` object. The file does not allocate memory or persist software state beyond function pointers, offsets, and timing limits. Register writes persist until later display mode programming or CRTC reset.

## Dependencies And Integration Points
Depends on DCE8 register definitions, `dm_services` register accessors, DCE110 timing-generator helpers, BIOS pointers from `dc_context`, and the common `timing_generator` interface. It integrates into resource construction for DCE8 display pipes and exposes behavior through the `timing_generator_funcs` vtable.

## Risks
`reg_offsets[instance]` assumes a valid instance index; invalid resource construction could index beyond the six-entry table. `program_pix_dur()` divides by pixel clock and silently skips zero clocks; callers must not rely on register refresh when pixel clock is zero. Advanced-request heuristics depend on vblank geometry and can affect underrun/prefetch behavior on edge timings.

## Test Signals
Useful signals are successful mode set on all DCE8 CRTCs, no DMIF arbitration underflows, correct `PIXEL_DURATION` register values for non-VBIOS mode programming, and regression tests around very small `v_sync_width + v_front_porch` timings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.h

## Purpose
Declares the DCE8 timing-generator constructor and documents that the implementation inherits from the DCE11 timing-generator structure and behavior.

## Important APIs, Types, And Functions
Exports `dce80_timing_generator_construct(struct dce110_timing_generator *tg, struct dc_context *ctx, uint32_t instance, const struct dce110_timing_generator_offsets *offsets)`. The header includes `timing_generator.h` and `grph_object_id.h`, relying on the DCE110 type being visible through surrounding include chains.

## Control Flow
The header has no executable control flow. Its constructor declaration is the entry point resource builders use to initialize a DCE8 timing-generator instance.

## State And Persistence
No state is defined here. The constructor populates caller-owned state in the `.c` implementation.

## Dependencies And Integration Points
Used by DCE8 resource code and included by `dce80_timing_generator.c`. It binds DCE8 code to the common timing-generator API and the DCE110-compatible implementation structure.

## Risks
The header accepts a DCE110 concrete object for DCE8 behavior, so changes to DCE110 structure layout or offset contracts can affect DCE8. Missing direct include of `dce110_timing_generator.h` would be fragile if include order changes.

## Test Signals
Compile coverage is the main signal: resource files must be able to include this header and construct timing generators without incomplete-type errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/Makefile

## Purpose
Adds the DCN1.0 display-core objects for input pixel processing, hardware-state debug dumping, and common color-management helpers to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN10 = dcn10_ipp.o dcn10_hw_sequencer_debug.o dcn10_cm_common.o`, wraps it into `AMD_DAL_DCN10` with `$(AMDDALPATH)/dc/dcn10/`, and appends to `AMD_DISPLAY_FILES`.

## Control Flow
There is no runtime flow. Build flow expands object names to source-tree paths and includes them in the aggregate AMD display object list.

## State And Persistence
No runtime state. Build state is represented by make variables.

## Dependencies And Integration Points
This file integrates the DCN10 subdirectory into the parent AMDGPU display make system. Other DCN10 files may be referenced from later-generation code, but only these three objects are compiled from this local Makefile.

## Risks
Omitting a required object from this list causes unresolved symbols or disabled functionality. Adding objects here without matching source files breaks builds. Because `dcn10_dwb.c` exists but is not listed here, its compilation is controlled elsewhere or intentionally excluded for this snapshot.

## Test Signals
Kernel/module build should show these object files compiled and linked through `AMD_DISPLAY_FILES`; missing-symbol failures around `dcn10_ipp_construct`, `dcn10_get_hw_state`, or color helper functions indicate build-list drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_cm_common.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_cm_common.c

## Purpose
Provides shared DCN1 color-management helpers for programming color matrices and transfer-function LUT region metadata. It converts software transfer-function samples into the fixed/custom-float formats consumed by DCN hardware.

## Important APIs, Types, And Functions
`cm_helper_program_color_matrices()` writes paired CSC matrix coefficients across a contiguous register range. `cm_helper_read_color_matrices()` reads the same layout back. `cm_helper_program_xfer_func()` programs start/end points and per-region LUT offsets/segment counts into transfer-function registers. `cm_helper_convert_to_custom_float()` converts corner points and optional PWL base/delta values into hardware custom-float or fixed-point fields. `cm_helper_translate_curve_to_hw_format()` builds regamma/shaper PWL parameters from `dc_transfer_func`. `cm_helper_translate_curve_to_degamma_hw_format()` builds the degamma-specific 12-region format.

## Control Flow
Matrix helpers linearly walk register pairs from `csc_c11_c12` through `csc_c33_c34`. Transfer-function programming writes three color channels of start controls, start slopes, end controls, and then walks `region_start..region_end` two regions per hardware register. Translation first rejects null or bypass transfer functions, clears `pwl_params`, chooses region distribution based on transfer-function type, samples `output_tf->tf_pts`, appends a duplicate terminal point for delta math, computes corner points and slopes, fills `arr_curve_points`, computes deltas, optionally clamps fixed-point values for shaper LUTs, then converts to custom float.

## State And Persistence
The helpers mutate caller-provided `struct pwl_params` and write hardware registers through `REG_SET*` macros. No heap allocation or static mutable state is used. The programmed register state persists in DPP/OPP color blocks until replaced by later color programming.

## Dependencies And Integration Points
Depends on `dc.h`, `reg_helper.h`, `dcn10_dpp.h`, `custom_float.h`, fixed-point helpers, logger macros, and the transfer-function data model. Integrated by DPP/OPP code that needs common LUT and matrix register programming.

## Risks
Boundary math is sensitive: `TRANSFER_FUNC_POINTS`, `MAX_LOW_POINT`, and `NUMBER_SW_SEGMENTS` must stay consistent with table sizes. `seg_distr[k] != -1` compares unsigned values against `-1`; it works as all-bits-one but is easy to misread. Failed custom-float conversion triggers debug breaks and returns false, so callers must handle translation failure. Fixed-point mode warns when delta precision is lost.

## Test Signals
Signals include correct LUT programming for PQ, gamma 2.2, sRGB-like curves, and degamma paths; no out-of-bounds log errors; stable color output under regamma/de-gamma changes; and readback matching matrix values written by `cm_helper_program_color_matrices()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_cm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_cm_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_cm_common.h

## Purpose
Defines register descriptor structures and function prototypes for DCN1 color-management helper code.

## Important APIs, Types, And Functions
Macros `TF_HELPER_REG_FIELD_LIST`, `TF_HELPER_REG_LIST`, and `TF_CM_REG_FIELD_LIST` generate shift/mask/register fields. Types include `xfer_func_shift`, `xfer_func_mask`, `xfer_func_reg`, `cm_color_matrix_shift`, `cm_color_matrix_mask`, and `color_matrices_reg`. Prototypes expose matrix programming/readback, transfer-function programming, software-to-hardware curve translation, degamma translation, and custom-float conversion.

## Control Flow
No executable flow. The macro-generated structures define the shape used by register-specific DPP/OPP code when calling helpers.

## State And Persistence
No runtime state; all structures are caller-owned constant register maps or temporary descriptors.

## Dependencies And Integration Points
Consumed by `dcn10_cm_common.c` and display block implementations that populate register lists. It is part of the shared color-management contract for DCN1 and later code that reuses DCN1 helpers.

## Risks
Field names must match the `REG_SET*` calls in the implementation. The misspelled `exp_resion_start_segment` is part of the ABI between macros and code and must not be “fixed” without updating all users. Header lacks explicit type includes for several structs used in prototypes, relying on include order.

## Test Signals
Compile-time field resolution is the primary signal. Runtime color tests validate that generated register descriptors match the expected hardware fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_cm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_dwb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_dwb.c

## Purpose
Implements the DCN1 display writeback controller base behavior: capability reporting, simple enable/disable, and object construction.

## Important APIs, Types, And Functions
`dwb1_get_caps()` fills `struct dwb_caps` for DCN1.0, reporting two pipes, DWB support, WBSCL support, and no OGAM/OCSC. `dwb1_enable()` disables first, disables writeback clock/memory gating, then sets `WB_ENABLE`. `dwb1_disable()` disables capture and WB, soft-resets the block, and re-enables power gating. `dcn10_dwbc_funcs` publishes these functions. `dcn10_dwbc_construct()` stores context, instance, function table, register map, shifts, and masks.

## Control Flow
Enable calls the vtable `disable()` first to reset the block, programs `WB_EC_CONFIG` gating-disable fields, and enables WB. Disable turns off `CNV_FRAME_CAPTURE_EN`, clears `WB_ENABLE`, pulses `WB_SOFT_RESET`, then restores gating fields. Construction is straight-line assignment.

## State And Persistence
Persistent state is hardware register state for the writeback and converter blocks, plus the function pointer and register-map pointers held in `struct dcn10_dwbc`. No dynamic allocation is performed.

## Dependencies And Integration Points
Depends on `reg_helper`, `resource`, the common `dwb` interface, and `dcn10_dwb.h` register definitions. It integrates through the `dwbc_funcs` interface used by display writeback resource code.

## Risks
Enable ignores detailed `dc_dwb_params`; DCN1 writeback configuration is minimal here. Calling enable while external users expect existing CNV state will reset it via `disable()`. Power-gating field behavior is hardware-specific and can affect hangs or idle power if wrong.

## Test Signals
Check `get_caps` values, successful enable/disable register readback, absence of WB soft-reset hangs, and writeback capture smoke tests on DCN1 hardware where this object is wired in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_dwb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_dwb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_dwb.h

## Purpose
Defines DCN1 display writeback register lists, field lists, and the concrete `dcn10_dwbc` object layout.

## Important APIs, Types, And Functions
Register macros such as `DWBC_COMMON_REG_LIST_DCN1_0` enumerate CNV and MCIF_WB registers for enable, mode, buffer addresses, arbitration, pstate, watermark, warmup, and buffer sizes. `DWBC_COMMON_MASK_SH_LIST_DCN1_0` and `DWBC_REG_FIELD_LIST` define field shift/mask members. Types include `dcn10_dwbc_registers`, `dcn10_dwbc_mask`, `dcn10_dwbc_shift`, and `dcn10_dwbc`. The constructor prototype is `dcn10_dwbc_construct()`.

## Control Flow
No executable flow. The macros are expanded by resource code to create register maps and by implementation code through `REG()`/`FN()` accessors.

## State And Persistence
The concrete object stores a common `struct dwbc` plus immutable register, shift, and mask pointers. Actual persistent state is in hardware registers named by the maps.

## Dependencies And Integration Points
Requires DCN register-address macros (`SRI`, `SF`, base-index macros) from surrounding AMD display headers. Used by `dcn10_dwb.c` and shared by later writeback implementations that extend DCN1 fields.

## Risks
The register map is large and tightly coupled to generated ASIC headers. Field-list drift causes incorrect writes. Some fields in `DWBC_REG_FIELD_LIST` are not present in the DCN1 common mask list, so users must ensure masks are valid before optional field use.

## Test Signals
Compile-time macro expansion across supported ASIC headers, successful register programming in DWB enable/disable paths, and hardware writeback buffer manager state changes are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_dwb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_hw_sequencer_debug.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_hw_sequencer_debug.c

## Purpose
Formats DCN1 hardware state into CSV-like diagnostic text and clears selected underflow status bits. It is a debug support file for hardware-sequencer diagnostics.

## Important APIs, Types, And Functions
`snprintf_count()` wraps `vsnprintf()` and returns the number of characters actually consumed from a bounded buffer. State dump helpers cover hubbub watermarks, hubp surfaces and underflows, RQ, DLG, TTU, color-management state, MPCC state, OTG timing, and clocks. `dcn10_clear_status_bits()` clears HUBP and OPTC underflows according to a mask. `dcn10_get_hw_state()` dispatches selected dump helpers by bitmask and writes into a caller buffer.

## Control Flow
Each dump helper writes a header, loops over resource-pool instances, skips inactive/blanked blocks where appropriate, queries block-specific read-state callbacks, formats fields, and advances the output pointer by `snprintf_count()` results. `dcn10_get_hw_state()` defaults mask `0` to all low 16 bits, then calls helpers in fixed order while `remaining_buf_size > 0`. Underflow clearing reads current states and clears only enabled/non-blank blocks.

## State And Persistence
The file reads live hardware/resource state and writes only the caller-provided text buffer, except for underflow-clear functions that mutate hardware status bits. It does not persist software state.

## Dependencies And Integration Points
Depends on many display block interfaces: hubbub, hubp, DPP, MPC, timing generator, OPP/IPP includes, DCN10 hubbub/hubp structures, clock manager state, and logger infrastructure. It integrates with debugfs or diagnostic paths that request current hardware state.

## Risks
Buffer accounting assumes `remaining_buffer` remains valid; subtracting when already tiny can underflow if callers pass `bufSize == 0`, though dispatch checks before most helper calls. State arrays are indexed by resource counts and `current_state->res_ctx.pipe_ctx[i]`, so mismatched counts could report wrong pixel clocks. Diagnostics can expose address bits unless invariant-only mode is selected.

## Test Signals
Exercise `dcn10_get_hw_state()` with small and large buffers, all mask bits, invariant-only mode, active and blank pipes, and underflow clear requests. Expected output should remain parseable CSV and not overflow the provided buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_hw_sequencer_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_hw_sequencer_debug.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_hw_sequencer_debug.h

## Purpose
Declares public DCN1 hardware-state debug helpers.

## Important APIs, Types, And Functions
Exports `dcn10_clear_status_bits()` and `dcn10_get_hw_state()`. It also declares `dcn10_log_hw_state()`, which is not implemented in the paired source file in this subset and may be implemented conditionally or in another snapshot. It forward-declares `struct dc` and includes `core_types.h`.

## Control Flow
No executable flow. Consumers call the declared functions from debug or hardware-sequencer code paths.

## State And Persistence
No state in the header. Implementations read diagnostic state and may clear hardware underflow flags.

## Dependencies And Integration Points
This header is the interface between debugfs/logging callers and DCN10 debug implementation.

## Risks
Prototype drift, especially for `dcn10_log_hw_state()`, can cause link failures if a caller references a declaration that is not built. Mask semantics are documented only in implementation comments, not in typed enums.

## Test Signals
Build/link coverage for all declared functions and smoke tests of debug state collection through the user-facing diagnostic interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_hw_sequencer_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.c

## Purpose
Implements constructors and destructor for the DCN input pixel processor object.

## Important APIs, Types, And Functions
`dcn10_ipp_destroy()` frees the containing `struct dcn10_ipp` and nulls the caller pointer. `dcn10_ipp_funcs` and `dcn20_ipp_funcs` currently publish only `ipp_destroy`. `dcn10_ipp_construct()` and `dcn20_ipp_construct()` initialize context, instance, function table, and register/shift/mask pointers.

## Control Flow
Construction is straight-line assignment. Destruction converts the base `input_pixel_processor` pointer back to `dcn10_ipp`, frees it with `kfree`, and clears the original pointer.

## State And Persistence
Software state consists of the base object, register maps, and cursor attributes stored in `struct dcn10_ipp`. No hardware register writes happen in this implementation file.

## Dependencies And Integration Points
Depends on `dm_services`, `dcn10_ipp.h`, `reg_helper`, and the common `ipp` interface. Integrated by resource pools that allocate IPP objects for DCN1/DCN2-style pipes.

## Risks
The destructor assumes the object was heap-allocated as `struct dcn10_ipp`; using it on embedded/static instances would be invalid. DCN10 and DCN20 function tables are identical here, so generation-specific behavior must live elsewhere.

## Test Signals
Resource construction/destruction tests, leak checks during device teardown, and compile-time validation of IPP function-table compatibility are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.h

## Purpose
Defines the DCN IPP register-map macros and concrete IPP structure used by DCN1/DCN2/DCN201 resource code.

## Important APIs, Types, And Functions
Macros `IPP_REG_LIST_DCN`, `IPP_REG_LIST_DCN10`, `IPP_REG_LIST_DCN20`, and `IPP_REG_LIST_DCN201` enumerate CNVC format and cursor registers with generation-specific naming differences. Mask/shift macros define fields for surface format, bypass/alpha/format expansion, legacy cursor color/control, cursor address/size/control/position/hotspot, destination offsets, and optional `OUTPUT_FP`. Types include `dcn10_ipp_registers`, shift/mask structs, and `struct dcn10_ipp`. Constructors for DCN10 and DCN20 are declared.

## Control Flow
No runtime flow. Macro expansion creates register maps consumed by resource constructors and IPP functions.

## State And Persistence
`struct dcn10_ipp` stores a common `input_pixel_processor`, register descriptors, and cached cursor attributes. Hardware state is represented by the cursor and CNVC registers listed here.

## Dependencies And Integration Points
Includes `ipp.h` and relies on AMD-generated register macros like `SRI` and `IPP_SF`. It bridges resource-specific register tables to the common IPP interface.

## Risks
Generation-specific spelling differences matter: DCN10 uses `CURSOR_SETTINS` while DCN20 uses `CURSOR_SETTINGS`, and DCN201 drops HUBPREQ cursor settings. Incorrect macro selection causes wrong register addresses. Manually defined cursor magnify shift/mask must match ASIC headers.

## Test Signals
Cursor enable/move tests, format-control programming tests, and build coverage for all generation-specific register-list macros detect drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn10/dcn10_ipp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/Makefile

## Purpose
Adds DCN2.0 VMID and display writeback objects to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN20 = dcn20_vmid.o dcn20_dwb.o dcn20_dwb_scl.o`, expands it to `AMD_DAL_DCN20`, and appends it to `AMD_DISPLAY_FILES`.

## Control Flow
Build-only flow: object names are path-prefixed and included in the aggregate object list.

## State And Persistence
No runtime state. Make variables persist only during build evaluation.

## Dependencies And Integration Points
Connects DCN20 VMID/page-table setup, writeback controller, and writeback scaler code into the parent display build system.

## Risks
The writeback implementation depends on scaler helper symbols from `dcn20_dwb_scl.o`; removing either object causes link failures. Adding DCN20 source files without updating this list can silently omit functionality.

## Test Signals
Module build should compile these three objects and resolve `dcn20_vmid_setup`, `dcn20_dwbc_construct`, `dwb_program_horz_scalar`, and `dwb_program_vert_scalar`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.c

## Purpose
Implements DCN2.0 display writeback controller behavior, including converter configuration, enable/disable, update, scaler programming dispatch, stereo/new-content controls, and warmup control.

## Important APIs, Types, And Functions
`dwb2_get_caps()` reports one DCN2 writeback pipe with DWB support but no OGAM/OCSC and `support_wbscl = false` despite scaler programming paths. `dwb2_config_dwb_cnv()` programs source size, optional crop window, capture rate, and output BPC. `dwb2_enable()` validates no luma scaling, enables WB, programs CNV/scaler, enables frame capture, and disables warmup. `dwb2_update()` handles locked/unlocked CNV updates. Exported helpers include `dwb2_disable()`, `dwb2_is_enabled()`, `dwb2_set_stereo()`, `dwb2_set_new_content()`, and `dwb2_set_scaler()`.

## Control Flow
Enable/update both reject source dimensions that differ from destination dimensions, allowing only chroma/subsampling behavior. Update checks `CNV_UPDATE_LOCK`; if not already locked it locks, programs CNV and scaler, then unlocks. Scaler programming sets WBSCL mode/depth, destination size, rounding, clamp, outside-pixel strategy, selects cropped or full source size, calls horizontal and vertical scaler helpers, then toggles coefficient RAM if the hardware exposes the select mask.

## State And Persistence
Persistent state is DWB/CNV/WBSCL hardware registers, including frame capture enable, crop windows, scaler coefficient RAM, stereo/new-content bits, and warmup mode. The `dcn20_dwbc` object stores register descriptor pointers and function table.

## Dependencies And Integration Points
Depends on `dcn20_dwb.h`, common `dwb` params, `resource`, `reg_helper`, and the scalar functions in `dcn20_dwb_scl.c`. Integrated through `dwbc_funcs` used by capture/writeback flows.

## Risks
The dimension check forbids luma scaling, so callers must understand DCN2 limitations. `support_wbscl = false` can conflict with the presence of scaler code if capability consumers interpret it strictly. Update lock ownership is subtle: if caller pre-locks, this function leaves unlock responsibility to caller. Coefficient RAM toggle only occurs if mask is nonzero.

## Test Signals
Enable, update, disable, and `is_enabled` register readback; crop/no-crop capture tests; stereo bit programming; update while pre-locked vs unlocked; and invalid luma-scaling rejection are important test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.h

## Purpose
Defines DCN2 writeback controller register maps, field maps, concrete object layout, and exported helper prototypes.

## Important APIs, Types, And Functions
`DWBC_COMMON_REG_LIST_DCN2_0` lists CNV, WBSCL, debug, CRC, coefficient RAM, clamp, warmup, and soft-reset registers. `DWBC_COMMON_MASK_SH_LIST_DCN2_0` and `DWBC_REG_FIELD_LIST_DCN2_0` define fields used by DWB/CNV/WBSCL operations. Types include `dcn20_dwbc_registers`, `dcn20_dwbc_mask`, `dcn20_dwbc_shift`, and `dcn20_dwbc`. Prototypes expose constructor, DWB controls, CNV/scaler setup, and the horizontal/vertical scaler programming functions.

## Control Flow
No executable flow. The header creates the structural contract that `dcn20_dwb.c` and `dcn20_dwb_scl.c` use for register accesses.

## State And Persistence
`struct dcn20_dwbc` stores the base `dwbc` and constant register descriptor pointers. Runtime state is held in hardware registers defined by the macros.

## Dependencies And Integration Points
Relies on DWB-specific register-address macros such as `SRI2_DWB` and `SF_DWB`, plus common DWB parameter types. Used by DCN2 resource code and possibly later generations that reuse DCN20 writeback functions.

## Risks
Large macro lists make field drift likely when ASIC headers change. Optional coefficient-RAM fields are included in the field list and must be valid for callers that test/use them. Function prototypes expose scaler helpers that assume valid tap counts and dimensions.

## Test Signals
Compile coverage across ASIC register headers, writeback scaler programming tests, and register dumps confirming mask/shift alignment with hardware fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb_scl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb_scl.c

## Purpose
Programs DCN2 writeback scaler ratios, phases, tap counts, and coefficient RAM for horizontal and vertical luma/chroma scaling.

## Important APIs, Types, And Functions
The file contains static 16-phase coefficient tables for 3 through 12 taps, with variants for upscale, ratios below 4/3, below 5/3, and higher downscale. `wbscl_get_filter_*tap_16p()` selects the table for a tap count and fixed-point ratio. `wbscl_get_filter_coeffs_16p()` dispatches by tap count and supports 2-tap through `get_filter_2tap_16p()` and 1-tap with no coefficients. `wbscl_set_scaler_filter()` writes coefficient RAM by phase and tap pair. Exported `dwb_program_horz_scalar()` and `dwb_program_vert_scalar()` compute ratios, taps, phases, and load coefficient sets.

## Control Flow
Horizontal and vertical programming compute `src/dest` fixed-point ratios, convert ratios to hardware U3.19-left-shifted format with an all-ones special case at floor 8, program tap counts as `taps - 1`, compute luma and chroma initial phases, split signed phase into integer and fractional fields, program init registers, choose luma/chroma filter tables, and write coefficient RAM. Vertical chroma phase adds a quarter-pixel offset only for co-sited subsampling.

## State And Persistence
The coefficient tables are static read-only data. Hardware state persists in WBSCL scale-ratio, tap-control, init-phase, and coefficient RAM registers. No software state is retained.

## Dependencies And Integration Points
Depends on `fixed31_32.h`, common DWB scaling params, `dcn20_dwb.h`, and `reg_helper`. Called by `dwb2_set_scaler()` from DCN2 writeback enable/update flows.

## Risks
Tap values outside 1..12 trigger debugger break in coefficient dispatch. Zero destination dimensions would divide by zero through fixed-point helpers. Chroma filter selection passes `dc_fixpt_from_int(h_ratio_luma * 2)`/`v_ratio_luma * 2`, which uses the encoded register ratio rather than the original fixed ratio and is sensitive to overflow/semantic assumptions. Coefficient arrays encode signed coefficients as unsigned 14-bit style values, so accidental reinterpretation would break filtering.

## Test Signals
Validate register programming for tap counts 1..12, upscale and downscale threshold ratios, co-sited vs non-co-sited vertical subsampling, zero/invalid dimensions rejection at higher layers, coefficient RAM writes, and capture quality/resampling correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_dwb_scl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.c

## Purpose
Programs DCN2 VMID page-table context registers for display GPUVM access and waits for hardware acknowledgement.

## Important APIs, Types, And Functions
`dcn20_vmid_setup()` writes start/end logical page numbers, page-table depth and block size, high page-directory address, then low page-directory address last. `dcn20_wait_for_vmid_ready()` polls `PAGE_TABLE_BASE_ADDR_LO32` until bit 0 becomes set, with a 10000 iteration limit and 5 microsecond delay.

## Control Flow
Setup writes start and end address high/low fields, control fields, base high, base low, then calls the wait helper. The wait helper repeatedly reads `VM_CONTEXT0_PAGE_DIRECTORY_ENTRY_LO32`; success returns immediately, timeout logs a warning and asserts.

## State And Persistence
Persistent state is the VM context hardware register set for the VMID. No software state is retained except descriptor pointers in `struct dcn20_vmid`.

## Dependencies And Integration Points
Depends on Linux `udelay`, `dcn20_vmid.h`, `reg_helper`, and logger/assert infrastructure. It integrates with DCN memory hub/display VM setup before surfaces or writeback clients use GPU virtual addresses.

## Risks
Programming order is critical: hardware requires the low base register last. Timeout constants are marked TODO and may be too long or short for some ASICs. The ready check uses bit 0 of the full field rather than `REG_WAIT` on a named field.

## Test Signals
VMID setup should complete without timeout, page-table register readback should match config values, GPUVM-backed scanout/writeback should work, and fault logs should remain clean under VM context updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.h

## Purpose
Defines DCN2 VMID register lists, field lists, concrete VMID descriptor, and the setup API.

## Important APIs, Types, And Functions
`DCN20_VMID_REG_LIST(id)` enumerates `CNTL`, page-table base high/low, start high/low, and end high/low registers. `DCN20_VMID_MASK_SH_LIST` and `DCN20_VMID_REG_FIELD_LIST` define depth, block size, page-directory entry, and logical page-number fields. `struct dcn20_vmid` stores context, register map, shifts, and masks. `dcn20_vmid_setup()` is declared.

## Control Flow
No runtime flow in the header. It supplies the register contract consumed by the `.c` setup implementation and resource code.

## State And Persistence
The descriptor holds pointers to register metadata. VM page-table state lives in hardware registers.

## Dependencies And Integration Points
Includes `vmid.h` for common VMID register and config types. Resource builders use these macros to instantiate VMID register tables.

## Risks
Field names all use VM_CONTEXT0 naming even when macro parameter selects other instances; this follows generated register naming but is easy to misuse. Any mismatch in high/low address field width corrupts GPUVM address ranges.

## Test Signals
Compile-time macro expansion, VMID setup readback, GPUVM memory access tests, and absence of VM faults after context programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/Makefile

## Purpose
Adds DCN2.0.1 MPC, OPP, and link encoder objects to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN201 = dcn201_mpc.o dcn201_opp.o dcn201_link_encoder.o`, creates `AMD_DAL_DCN201`, and appends it to `AMD_DISPLAY_FILES`.

## Control Flow
Build-time object-list expansion only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrates the DCN201-specific compositor, output pixel processor, and link encoder implementations into the parent display build.

## Risks
Missing any of these objects causes resource construction or function-table symbol failures for DCN201 ASICs. The directory is small and reuses DCN20 code heavily, so build-list mistakes may not be obvious until hardware-specific configs are built.

## Test Signals
Kernel/module build for DCN201 targets should include all three objects and resolve their constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.c

## Purpose
Implements the DCN2.0.1 link encoder constructor and small USB-C/DP-alt-mode capability overrides on top of DCN10/DCN20 link-encoder behavior.

## Important APIs, Types, And Functions
`dcn201_link_encoder_get_max_link_cap()` calls the DCN10 max-cap helper, then limits lane count to two on USB-C combo PHY when DP alt-mode state indicates no DP4. `dcn201_link_encoder_is_in_alt_mode()` reads `RDPCS_PHY_DPALT_DISABLE` and returns true when alt mode is enabled. `dcn201_link_enc_funcs` mostly delegates to DCN10/DCN20 helpers, adding FEC support and DCN201 alt-mode/max-cap functions. `dcn201_link_encoder_construct()` initializes the encoder, reads VBIOS capability info, maps transmitters A/B to DIG engines, and applies debug HDMI 2.0 disable.

## Control Flow
Construction initializes base fields from `encoder_init_data`, assigns function table and register maps, sets supported output signals, maps only UNIPHY A/B to preferred DIG engines, defaults HDMI 6G on, queries VBIOS capabilities, copies HBR2/HBR3/HDMI/USB-C feature flags, logs on failure, then applies debug override. Capability query path reads DP alt-mode register fields after base capability calculation and clamps lanes when needed.

## State And Persistence
Persistent software state is the initialized `link_encoder` object fields and feature flags. Hardware state is read but not written by the DCN201-specific helpers in this file.

## Dependencies And Integration Points
Depends on DCN20 link-encoder structures, DCN10 link helpers, VBIOS capability callbacks, GPIO/HPD data, register helper macros, and stream encoder contracts. Integrated by DCN201 resource construction and link training paths.

## Risks
Only transmitters A and B are accepted; other transmitters assert and become unknown. Lane clamping depends on exact `RDPCSTX_PHY_CNTL2` bit semantics. VBIOS capability failure leaves defaults, which may overstate HDMI 6G until debug disables it.

## Test Signals
USB-C alt-mode lane-count tests, VBIOS capability read success/failure paths, HPD and link training on UNIPHY A/B, FEC readiness tests, and HDMI 2.0 debug override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.h

## Purpose
Declares the DCN201 link encoder constructor and extends DPCS register/mask lists for DCN201 PHY and DP alt-mode fields.

## Important APIs, Types, And Functions
`DPCS_DCN201_MASK_SH_LIST` extends common DPCS masks with raw-lane override, DP alt-disable/DP4, per-lane pstate/MPLL, lane width/rate, and ref clock fields. `DPCS_DCN201_REG_LIST` extends common DCN2 DPCS registers with raw-lane indexed override registers. `dcn201_link_encoder_construct()` is the exported constructor.

## Control Flow
No executable flow. Register macros are expanded by resource code and consumed by the `.c` implementation and inherited helpers.

## State And Persistence
No state in the header. The register lists describe hardware state relevant to link PHY programming.

## Dependencies And Integration Points
Includes `dcn20/dcn20_link_encoder.h` and reuses DPCS/DCN2 link encoder macro infrastructure. Used by DCN201 resource code.

## Risks
The register/mask list must stay aligned with both DCN201 ASIC headers and inherited DCN20 helper expectations. Incorrect DP alt-mode fields can cause bad USB-C link-cap reporting.

## Test Signals
Compile coverage of macro expansion, DP-alt-mode detection, lane-cap reporting, and link training with DCN201 registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_mpc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_mpc.c

## Purpose
Implements the DCN201 multiple-pipe combiner object by reusing DCN1/DCN2 MPC helpers and adding output rate/flow-control programming.

## Important APIs, Types, And Functions
`mpc201_set_out_rate_control()` programs `MPC_OUT_RATE_CONTROL_DISABLE`, `MPC_OUT_RATE_CONTROL`, and optional flow-control mode/counts on the output mux register indexed by OPP. `mpc201_init_mpcc()` initializes each software MPCC node to defaults. `dcn201_mpc_funcs` delegates plane insertion/removal, blending, denorm, output CSC/gamma, memory power, background color, and MPCC state operations to MPC1/MPC2 helpers, with DCN201 rate control. `dcn201_mpc_construct()` initializes the object and MPCC array.

## Control Flow
Construction sets context, function table, register descriptors, zeroes in-use mask, stores `num_mpcc`, and initializes all `MAX_MPCC` MPCC nodes. Rate-control calls update mux fields and conditionally writes flow-control fields only when a `flow_control` pointer is provided.

## State And Persistence
Software state includes `mpcc_in_use_mask`, `num_mpcc`, the MPCC array inside the base object, and register descriptor pointers. Hardware state persists in MPC output mux registers and inherited MPC registers.

## Dependencies And Integration Points
Depends on `dcn201_mpc.h`, `reg_helper`, and inherited DCN20 MPC helper functions. Integrated into the resource pool as the compositor for DCN201 display pipes.

## Risks
`opp_id` is used directly as `MUX[opp_id]`; callers must pass a valid output index. All `MAX_MPCC` entries are initialized even if `num_mpcc` is smaller, so later allocation code must respect `num_mpcc`. Flow-control values are unvalidated here.

## Test Signals
Plane composition, MPCC allocation/free, output CSC/gamma, rate-control toggling, DWB flow control, and register readback of mux fields are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_mpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_mpc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_mpc.h

## Purpose
Defines the DCN201 MPC register-field extensions, concrete MPC structure, and constructor prototype.

## Important APIs, Types, And Functions
Macros reuse DCN2.0 MPC register lists and add fields for `MPC_OUT_RATE_CONTROL`, disable, flow-control mode, and two flow-control counts. Types include `dcn201_mpc_registers`, `dcn201_mpc_shift`, `dcn201_mpc_mask`, and `dcn201_mpc`. `TO_DCN201_MPC()` converts the base object to the concrete object.

## Control Flow
No executable flow. Macro expansion controls which fields inherited MPC helpers and DCN201-specific rate control can access.

## State And Persistence
The concrete object extends `struct mpc` with MPCC usage tracking, MPCC count, and register descriptors. Hardware state is in MPC registers.

## Dependencies And Integration Points
Includes `dcn20/dcn20_mpc.h` and is used by `dcn201_mpc.c` and DCN201 resource construction.

## Risks
Field-list concatenation must include proper separators; a missing semicolon in macro expansion would break generated structs. Flow-control fields must match the hardware mux register layout.

## Test Signals
Compile-time structure generation plus runtime tests of rate control, flow control, MPCC state reading, and plane composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_mpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_opp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_opp.c

## Purpose
Constructs the DCN201 output pixel processor and assigns an OPP function table largely inherited from OPP1/OPP2 helpers.

## Important APIs, Types, And Functions
`dcn201_opp_funcs` maps dynamic expansion, format programming, bit-depth reduction, stereo, pipe clock control, display pattern generator, DPG dimensions/status, blank color, left-edge extra pixel, and destroy operations to inherited functions. `dcn201_opp_construct()` initializes context, instance, function table, register map, shift map, and mask map.

## Control Flow
Construction is straight-line assignment. Runtime operations are handled by the inherited function pointers rather than local logic.

## State And Persistence
Software state is the initialized `dcn201_opp` object. Runtime hardware state is programmed by inherited OPP helpers using the stored register descriptors.

## Dependencies And Integration Points
Depends on `dm_services`, `dcn201_opp.h`, `reg_helper`, and inherited DCN10/DCN20 OPP helpers. Integrated by DCN201 resource construction for pipe output processing.

## Risks
Because all behavior delegates to inherited functions, register-list compatibility is critical. Any DCN201 hardware difference not represented by the register/mask maps can produce incorrect formatting or DPG behavior.

## Test Signals
Mode-set output formatting, bit-depth reduction, stereo, DPG pattern generation, blanking, and left-edge extra-pixel tests on DCN201 are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_opp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_opp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_opp.h

## Purpose
Defines the DCN201 output pixel processor register map, concrete object, and constructor.

## Important APIs, Types, And Functions
`OPP_REG_LIST_DCN201` combines DCN10 OPP registers, DPG registers, and `FMT_422_CONTROL`. `OPP_MASK_SH_LIST_DCN201` and `OPP_DCN201_REG_FIELD_LIST` reuse DCN20 fields. Types include `dcn201_opp_shift`, `dcn201_opp_mask`, `dcn201_opp_registers`, and `dcn201_opp`. `TO_DCN201_OPP()` converts from base object.

## Control Flow
No executable flow. The header supplies register descriptors for inherited OPP helper functions.

## State And Persistence
`struct dcn201_opp` stores the common output pixel processor, descriptors, and `is_write_to_ram_a_safe`. Hardware state is represented by OPP/FMT/DPG registers.

## Dependencies And Integration Points
Includes `dcn20/dcn20_opp.h`, and is used by DCN201 OPP implementation and resource construction.

## Risks
Reusing DCN20 mask fields with DCN201 register lists assumes exact compatibility. The `is_write_to_ram_a_safe` field is present but not initialized in the constructor in this subset, so users must not assume a default unless zero-initialized allocation is guaranteed.

## Test Signals
Compile-time macro expansion, OPP format programming, DPG operation, and register readback for FMT_422 and inherited OPP fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn201/dcn201_opp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/Makefile

## Purpose
Adds the DCN2.1 link encoder object to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN21 = dcn21_link_encoder.o`, expands it to `AMD_DAL_DCN21`, and appends to `AMD_DISPLAY_FILES`.

## Control Flow
Build-time object-list expansion only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects the DCN2.1 link encoder implementation to the parent display build.

## Risks
If omitted, DCN2.1 resource construction will miss the link encoder constructor and function-table implementation.

## Test Signals
Build coverage for DCN2.1 ASIC configs and link-time resolution of `dcn21_link_encoder_construct`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.c

## Purpose
Implements the DCN2.1 link encoder, including Renoir-style PHY acquisition/release, MPLL configuration for DP rates when avoiding VBIOS execution tables, and construction of a DCN2.1-specific link function table.

## Important APIs, Types, And Functions
`dcn21_mpll_cfg_ref[]` stores reference MPLL settings for RBR, HBR, HBR2, and HBR3. `update_cfg_data()` selects the MPLL config for a requested link rate and enables all four lanes. `dcn21_link_encoder_acquire_phy()` handles USB-C DP-alt-mode acknowledgement and enables the DP reference clock. `dcn21_link_encoder_release_phy()` releases alt-mode ack and disables ref clock. `dcn21_link_encoder_enable_dp_output()` and MST variant wrap PHY acquisition around inherited enable paths. `dcn21_link_encoder_disable_output()` releases PHY for DP signals. The constructor initializes fields, transmitter-to-DIG mapping A through G, and VBIOS feature flags.

## Control Flow
DP output enable first acquires PHY. If VBIOS exec tables are allowed, it delegates to DCN10 enable. If debug avoids VBIOS exec tables, it fills local PHY sequence config, calls `enc1_configure_encoder()`, and sets up DP output. MST enable delegates after PHY acquisition. Disable delegates to DCN10 and releases PHY for DP signals. Construction populates base identity, output signal mask, register maps, preferred engine by transmitter, default HDMI 6G, VBIOS caps, and debug overrides.

## State And Persistence
Software state includes the base link encoder and `phy_seq_cfg`. Hardware state includes DP-alt disable acknowledgement, DP reference clock enable, and inherited link/PHY programming. Feature flags persist in the encoder object.

## Dependencies And Integration Points
Depends on DCN20 link encoder headers, DCN10 link helpers, VBIOS callbacks, GPIO/HPD data, Linux delay, stream encoder functions, and debug flags. Used by DCN2.1 resource/link-training paths.

## Risks
PHY acquisition can return without release if `update_cfg_data()` fails after reference clock enable in the avoid-VBIOS path. Lane mapping is marked TODO and currently enables all lanes. USB-C alt-mode handshake depends on `RDPCS_PHY_DPALT_DISABLE` semantics and fixed 40 microsecond delay. Unsupported link rates return false and abort enable.

## Test Signals
DP SST/MST link training at RBR/HBR/HBR2/HBR3, USB-C alt-mode plug/unplug, avoid-VBIOS-exec-table debug mode, reference-clock enable/disable readback, and failure-path cleanup tests are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h

## Purpose
Defines the DCN2.1 link encoder structure, register/mask extensions, and public constructor/DP-enable prototypes.

## Important APIs, Types, And Functions
`struct dcn21_link_encoder` embeds `struct dcn10_link_encoder` and adds `struct dpcssys_phy_seq_cfg`. `DPCS_DCN21_MASK_SH_LIST` extends DCN2 masks with fuse, DP-alt, vreg, EQ, DCO, and soft-reset fields. `DPCS_DCN21_REG_LIST` adds PHY control and DMCU DP-alt block registers. `LINK_ENCODER_MASK_SH_LIST_DCN21` extends link encoder masks and adds xbar/fuse/scratch registers. Exports `dcn21_link_encoder_enable_dp_output()` and constructor.

## Control Flow
No executable flow. Macros provide register descriptors for the implementation and inherited link helpers.

## State And Persistence
The concrete structure persists link encoder state plus PHY sequence configuration. Hardware state is represented by the listed PHY and link registers.

## Dependencies And Integration Points
Includes `dcn20/dcn20_link_encoder.h` and participates in DCN2.1 resource construction and link training.

## Risks
Macro `LINK_ENCODER_MASK_SH_LIST_DCN21(mask_sh)` references `id` inside the body for `SRI(...)` entries even though the macro signature has no `id`; this relies on expansion context or may be a latent macro bug. PHY field compatibility with inherited DCN20 helpers is critical.

## Test Signals
Compile all macro users, instantiate DCN2.1 link encoders, and run DP/HDMI link training, USB-C alt-mode, and PHY fuse/EQ programming tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn21/dcn21_link_encoder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/Makefile

## Purpose
Adds selected DCN3.0 objects to the AMD display build.

## Important APIs, Types, And Functions
Defines `DCN30 := dcn30_vpg.o dcn30_afmt.o dcn30_cm_common.o dcn30_mmhubbub.o`, wraps with `AMD_DAL_DCN30`, and appends to `AMD_DISPLAY_FILES`.

## Control Flow
Build-time object-list expansion only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrates video packet generator, audio formatter, color-management helpers, and MMHUBBUB/MCIF writeback memory client into the display build.

## Risks
The report set does not include `dcn30_vpg.c`, but the build list does; missing or stale source for that object would fail builds. Omitting `dcn30_cm_common.o` or `dcn30_mmhubbub.o` breaks symbols used by DCN3 resource code.

## Test Signals
Kernel/module build for DCN3 configs, link-time resolution of AFMT/CM/MMHUBBUB symbols, and object inclusion in `AMD_DISPLAY_FILES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.c

## Purpose
Implements DCN3 audio formatter setup for HDMI and DisplayPort audio packet generation, stream audio mapping, mute/power behavior, and infoframe update.

## Important APIs, Types, And Functions
`afmt3_setup_hdmi_audio()` powers on the block and programs IEC 60958 channel status defaults and channel numbers. `speakers_to_channels()` maps `audio_speaker_flags` to CEA channel allocation bits. `afmt3_se_audio_setup()` selects the audio source instance and writes channel allocation. `afmt3_audio_mute_control()` powers down/up conditionally and toggles audio sample transmission. `afmt3_audio_info_immediate_update()` forces double-buffered audio infoframe update. `afmt3_setup_dp_audio()` programs DP audio packet defaults. `afmt3_construct()` initializes the object and function table.

## Control Flow
HDMI/DP setup optionally powers on through function pointers, then writes packet-control and 60958/infoframe registers. Stream setup asserts and null-checks `audio_info`, maps speakers to channels, selects audio source, enables channels, and clears forced memory power-off if no poweron callback exists. Mute powers down before disabling packets and powers on before enabling packets.

## State And Persistence
Hardware state persists in AFMT packet, source, channel-status, infoframe, and memory-power registers. Software state is the initialized `dcn30_afmt` object and optional power callbacks in the base function table.

## Dependencies And Integration Points
Depends on `dc_bios_types`, `hw_shared`, `dcn30_afmt.h`, and `reg_helper`. It integrates with stream encoder/audio setup paths for HDMI and DP on DCN3.

## Risks
`audio_info == NULL` is asserted then tolerated by return, so release builds silently skip setup. Power callback ordering matters for mute/unmute. Channel mapping logic encodes speaker exclusivity rules and can produce wrong CEA allocation if flags are inconsistent.

## Test Signals
HDMI and DP audio playback, channel allocation for stereo/5.1/7.1 layouts, mute/unmute power transitions, infoframe update readback, and no audio packet transmission while muted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.h

## Purpose
Defines the DCN3 audio formatter register maps, function table interface, base/concrete object structures, and public setup functions.

## Important APIs, Types, And Functions
`AFMT_DCN3_REG_LIST` lists infoframe, VBI/audio packet, audio source, 60958 status, and memory-power registers. `DCN3_AFMT_MASK_SH_LIST` and `AFMT_DCN3_REG_FIELD_LIST` define fields for audio info update, source select, channel enable, 60958 update/layout/channel numbers/clock accuracy, sample send, and memory power force. `struct afmt_funcs` contains setup, mute, update, DP setup, and power callbacks. `struct afmt` is the base, `struct dcn30_afmt` stores register descriptors, and setup/constructor prototypes are exported.

## Control Flow
No executable flow; callers invoke function pointers or exported setup helpers.

## State And Persistence
The base object stores context, instance, and function table. The concrete object stores register descriptors. Hardware state is in AFMT registers.

## Dependencies And Integration Points
The header is used by `dcn30_afmt.c` and stream/audio resource code. It assumes common audio types such as `audio_info` and `audio_speaker_flags` are visible through including translation units.

## Risks
Power callbacks are optional, so implementations must guard them. Adding AFMT fields requires synchronized updates to register, shift, and mask lists. Header-defined base `struct afmt` becomes an ABI-like contract for all AFMT users.

## Test Signals
Compile-time structure/function compatibility, HDMI/DP audio setup, power callback invocation, and register readbacks for source select/channel enable/sample send.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_afmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_cm_common.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_cm_common.c

## Purpose
Provides DCN3 color-management helper logic for gamcor transfer-function programming and DCN3-specific software-curve translation, including 257-point behavior for non-shaper LUTs.

## Important APIs, Types, And Functions
`cm_helper_program_gamcor_xfer_func()` writes gamcor start controls, start slopes, end base/slope/end controls, and region metadata. `cm3_helper_translate_curve_to_hw_format()` converts `dc_transfer_func` samples into `pwl_params` for DCN3 hardware. `cm3_helper_convert_to_custom_float()` converts corner points and PWL base values to custom float or fixed point. `is_rgb_equal()` checks if all programmed RGB register values are equal across a PWL array.

## Control Flow
Translation rejects null/bypass inputs, clears params, chooses 32-region distribution for PQ, gamma 2.2, and HLG or compact 13-segment distribution otherwise, computes total hardware points, adjusts point count for fixed-point shaper LUTs, samples `tf_pts`, writes terminal duplicates, computes corner points and slopes, fills region offsets/segment counts, computes fixed-point deltas only in shaper mode, converts to custom float, and returns success/failure. Programming walks region registers two curve regions per register after writing per-channel start/end controls.

## State And Persistence
The helpers mutate caller-provided `pwl_params` and program hardware registers. There is no static mutable state. DCN3 register state persists until later color updates.

## Dependencies And Integration Points
Depends on `dcn30_dpp.h`, `dcn30_cm_common.h`, `custom_float`, fixed-point conversion helpers, and logger macros. Integrated by DCN3 DPP/OPP color programming paths.

## Risks
DCN3 point-count behavior differs from DCN1: non-fixpoint paths use 257 points because there are no separate slope registers. Off-by-one errors around `hw_points`, `hw_points + 1`, and terminal duplicates can corrupt LUT output. HLG is treated like PQ/gamma22 for region distribution. Fixed-point precision loss is logged as error.

## Test Signals
Regamma/gamcor tests for PQ, gamma 2.2, HLG, and SDR curves; shaper-LUT fixed-point tests; RGB equality checks; boundary coverage for `TRANSFER_FUNC_POINTS`; and visual/colorimetric validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_cm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_mmhubbub.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_mmhubbub.c

## Purpose
Implements DCN3 MMHUBBUB/MCIF writeback memory-client setup for warmup, writeback buffer addresses/sizes/pitch, arbitration, watermarks, pstate timing, and construction.

## Important APIs, Types, And Functions
`MCIF_ADDR()` and `MCIF_ADDR_HIGH()` convert 64-bit addresses into low/high register encodings. `mmhubbub3_warmup_mcif()` programs warmup base/region/increment, enables warmup interrupt, waits for completion, acknowledges, and disables warmup. `mmhubbub3_config_mcif_buf()` programs four luma/chroma buffer addresses, high address parts, buffer sizes, address fence enable, and pitches. `mmhubbub3_config_mcif_arb()` programs time per pixel, four urgent watermarks, four pstate watermarks, DRAM speed change duration, max scaled time, slice lines, and arbitration slice. `dcn30_mmhubbub_funcs` reuses DCN2 enable/disable/IRQ/dump helpers and DCN3-specific config functions. `dcn30_mmhubbub_construct()` initializes object fields.

## Control Flow
Warmup shifts address/region/increment by five bits, writes base and control registers, waits on `MMHUBBUB_WARMUP_SW_INT_STATUS`, acknowledges, then disables. Buffer config writes Y/C addresses for all four buffers, computes size from pitch shifted by eight times destination height, enables address fence, and writes pitch fields. Arbitration config selects watermark masks before writing each watermark bank, writes pstate masks similarly, then programs QoS and slice/arbitration fields.

## State And Persistence
Persistent hardware state is MCIF_WB buffer manager registers, buffer address/status registers, watermark and pstate registers, warmup control/status, and QoS/arbitration registers. Software state is the `dcn30_mmhubbub` descriptor.

## Dependencies And Integration Points
Depends on `mcif_wb.h`, `dcn30_mmhubbub.h`, DCN2 MMHUBBUB helper functions, and `reg_helper`. Integrated with DCN3 writeback and memory hub paths for frame dumping/capture.

## Risks
Address encoding masks to 40 bits plus high bits above 40; address format must match hardware. Pitches and sizes assume 256-byte alignment and shift by eight. `slice_lines - 1` underflows if zero. Warmup waits with fixed polling parameters and comments out VMID programming, which may matter for virtualized/protected memory cases.

## Test Signals
Writeback buffer address readback, four-buffer capture/fence behavior, warmup completion/timeout, watermark selection correctness, pstate transition stability, and MCIF dump-frame output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_mmhubbub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_mmhubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_mmhubbub.h

## Purpose
Defines DCN3 MCIF writeback/MMHUBBUB register lists, field lists, concrete object layout, and constructor prototype.

## Important APIs, Types, And Functions
`MCIF_WB_COMMON_REG_LIST_DCN3_0` extends DCN2 MCIF writeback registers with high address registers, buffer resolutions, MMHUBBUB memory power/warmup registers, and DRAM speed change duration. `MCIF_WB_COMMON_REG_LIST_DCN30` defines DCN30-specific uninstanced register names. `MCIF_WB_COMMON_MASK_SH_LIST_DCN3_0` and `MCIF_WB_COMMON_MASK_SH_LIST_DCN30` define buffer manager status/control, buffer status, watermarks, QoS, high address, resolution, warmup, and pstate fields. Types include register, mask, shift, and `dcn30_mmhubbub` structures.

## Control Flow
No executable flow. Macro expansion creates descriptor tables used by MMHUBBUB implementation and inherited DCN2 helpers.

## State And Persistence
`struct dcn30_mmhubbub` stores the base `mcif_wb` and descriptor pointers. Hardware state is represented by the many MCIF_WB/MMHUBBUB registers listed here.

## Dependencies And Integration Points
Includes `dcn20/dcn20_mmhubbub.h`, reusing DCN2 field lists and adding DCN3 fields. Used by DCN3 resource construction and `dcn30_mmhubbub.c`.

## Risks
There are two register/mask-list variants for DCN3.0 and DCN30 naming; choosing the wrong one can address wrong registers. Macro list size increases risk of omitted high-address or status fields. Warmup VMID field exists in the header but is not programmed in the implementation.

## Test Signals
Compile all macro variants, MCIF writeback capture with high addresses, warmup register readback, buffer status/overrun reporting, and pstate/watermark behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_mmhubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_opp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_opp.h

## Purpose
Defines the DCN3 OPP register-list macro for resource code that needs DCN30 output pixel processor registers.

## Important APIs, Types, And Functions
`OPP_REG_LIST_DCN30(id)` combines DCN10 OPP registers, DPG registers, and `FMT_422_CONTROL`, matching the DCN201-style OPP register set for DCN3.

## Control Flow
No executable flow.

## State And Persistence
No software state. The macro describes hardware register addresses to be stored in generated OPP register descriptor structures elsewhere.

## Dependencies And Integration Points
Includes `dcn20/dcn20_opp.h` for inherited OPP register macros. Used by DCN30 resource construction or OPP implementation code outside this subset.

## Risks
The header only provides a register list and no constructor or type definitions, so consumers must combine it with inherited DCN20 OPP structures. Any DCN30-specific OPP fields beyond this list must be added elsewhere.

## Test Signals
Compile-time macro expansion in DCN30 resource code and runtime OPP format/DPG/FMT_422 register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn30/dcn30_opp.h -->
