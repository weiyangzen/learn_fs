# subset-b-001397 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_mem_input_v.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_mem_input_v.c

Purpose: DCE11 underlay/video memory-input programming for UNP registers. It programs luma and chroma surface addresses, tiling metadata, plane size, rotation, pixel/video format, DVMM PTE behavior, display watermarks, and the `mem_input_funcs` vtable used by the DC plane pipeline.

Important APIs: `dce110_mem_input_v_construct`, `dce_mem_input_v_program_surface_flip_and_addr`, `dce_mem_input_v_program_surface_config`, `dce_mem_input_v_program_pte_vm`, `dce_mem_input_v_program_display_marks`, `dce_mem_input_program_chroma_display_marks`, and `dce_mem_input_v_is_surface_pending`. Helpers split luma/chroma register programming and map tiling/pixel formats to UNP/DVMM fields.

Control flow: construction installs a static function table. Surface setup enables UNP graphics, writes tiling, size/rotation, and format. Flip setup writes pending mode and high-before-low addresses, then caches `request_address`. Pending checks read `UNP_GRPH_UPDATE` and promote `request_address` to `current_address` when hardware clears the pending bit. Watermark programming writes masked A/B sets separately for luma and chroma.

State and persistence: state is mostly hardware register state plus `mem_input` cached addresses. PTE settings and watermarks persist in registers until reprogrammed. Risks include hard-coded request limits, ignored `flip_immediate`, unsupported address types triggering debug breaks, rotation-dependent PTE choices, and L/C register sequencing. Test signals are modeset/flip on video 4:2:0 and graphics planes, rotated planes, watermark changes, stutter disable debug behavior, and flip-pending convergence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_mem_input_v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_mem_input_v.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_mem_input_v.h

Purpose: public declaration for the DCE11 video/underlay memory-input constructor. The header binds the generic `mem_input`/`dce_mem_input` abstractions to the underlay-specific implementation in `dce110_mem_input_v.c`.

Important API: `dce110_mem_input_v_construct(struct dce_mem_input *dce_mi, struct dc_context *ctx)`. It requires `mem_input.h` and `dce/dce_mem_input.h`, so callers must allocate a `struct dce_mem_input` and pass a valid DC context.

Control flow and integration: resource construction code includes this header to initialize a memory-input object with the DCE11 video vtable. The header itself holds no logic or persistent state; state lives in the object and hardware registers after construction.

Risks and test signals: the constructor has no allocation or error return, so caller lifetime and object sizing are the main contract. Build tests should verify the declaration remains synchronized with the implementation and that underlay resources instantiate successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_mem_input_v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_csc_v.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_csc_v.c

Purpose: underlay color-space conversion programming for DCE11 color-management registers. It programs output CSC matrices, input CSC matrices, CSC mode selection, and denormalization/clamp behavior for graphics/video color spaces.

Important APIs: `dce110_opp_v_set_csc_default` and `dce110_opp_v_set_csc_adjustment`. Important data includes `global_color_matrix`, `input_csc_matrix`, `enum csc_color_mode`, and `enum grph_color_adjust_option`. `program_color_matrix_v` double-buffers output CSC register sets A/B, while `program_input_csc` does the same for input CSC.

Control flow: default setup optionally programs a software output matrix based on output color space, always programs input CSC from input color space, selects hardware/predefined/programmed output CSC mode, then sets denormalization based on output color depth. Adjustment setup writes a caller-provided matrix and selects software output CSC mode.

State and dependencies: all state is hardware register state under `COL_MAN_*`, `OUTPUT_CSC_*`, `INPUT_CSC_*`, and `DENORM_CLAMP_CONTROL`. Dependencies are DCE11 register headers, fixed register-field macros, and DC color-space/depth enums. Risks include unsupported SRGB limited underlay output returning false internally, TODO-marked matrix correctness for limited YCbCr, input type hard-coded to 8.4, and lack of validation on caller-provided matrices. Test signals are color-space conformance, limited/full RGB behavior, YCbCr601/709 conversion, and register A/B bank toggling without visible tearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_csc_v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_regamma_v.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_regamma_v.c

Purpose: DCE11 underlay regamma LUT and piecewise-linear gamma programming. It configures gamma regions, powers LUT memories for programming, writes RGB/delta LUT entries, and selects regamma mode.

Important APIs: `dce110_opp_program_regamma_pwl_v`, `dce110_opp_power_on_regamma_lut_v`, and placeholder `dce110_opp_set_regamma_mode_v`. Helpers include `power_on_lut`, `set_bypass_input_gamma`, `regamma_config_regions_and_segments`, and `program_pwl`.

Control flow: PWL programming writes start/end/region descriptors from `pwl_params`, bypasses input gamma, forces gamma memory on, streams `hw_points_num` RGB and delta values through `GAMMA_CORR_LUT_DATA`, sets mode 1, then returns memory control to automatic. Power control toggles input/regamma memory fields in `DCFEV_MEM_PWR_CTRL`.

State and persistence: region descriptors, LUT contents, gamma mode, and memory power fields persist in hardware. Dependencies are `pwl_params`, DCE transform wrappers, and DCE11 color-management registers. Risks include a likely bug in `configure_regamma_mode` building a value but writing zero, the no-op `dce110_opp_set_regamma_mode_v`, bounded but weak memory-power polling, and no guard against oversized `hw_points_num`. Test signals are gamma ramp accuracy, LUT programming under power gating, color-management bypass behavior, and regression checks for mode selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_regamma_v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.c

Purpose: minimal constructor for the DCE11 video/underlay OPP object. It wires an underlay OPP to the generic DCE110 OPP operations for dynamic expansion, formatting, bit-depth reduction, and destroy.

Important API: `dce110_opp_v_construct(struct dce110_opp *opp110, struct dc_context *ctx)`. Its static `opp_funcs` table references `dce110_opp_set_dyn_expansion`, `dce110_opp_destroy`, `dce110_opp_program_fmt`, and `dce110_opp_program_bit_depth_reduction` from the shared DCE OPP implementation.

Control flow and state: construction stores the function table and context in `opp110->base`. No hardware registers are written here; later OPP calls perform the hardware programming. Dependencies include `dce/dce_opp.h`, DC context types, and DCE11 register headers.

Risks and test signals: this file has little logic, so risk is primarily integration mismatch: the underlay path may need different OPP behavior than the generic DCE110 callbacks provide. Build/link tests catch missing symbols; runtime modeset tests catch format and bit-depth callback compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.h

Purpose: public constructor declaration for the DCE11 underlay OPP wrapper.

Important API: `dce110_opp_v_construct(struct dce110_opp *opp110, struct dc_context *ctx)`. The header includes `dc_types.h`, `opp.h`, and `core_types.h`, exposing the object shape needed by resource construction.

Control flow and state: no runtime behavior is implemented here. It exists to allow resource code to instantiate the video OPP and receive a generic `opp` interface through `opp110->base`.

Risks and test signals: the header has no internal guards beyond include guards. The important tests are compilation of users that include it and runtime validation that the constructed OPP vtable is compatible with underlay display paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_opp_v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator.c

Purpose: main DCE11 timing-generator implementation. It validates timings, controls CRTC enable/disable through BIOS callbacks, programs blanking and test patterns, manages vblank/scanout status, supports DRR/static screen controls, global swap lock, triggered reset, VGA disable, vertical interrupts, and CRC.

Important APIs: `dce110_timing_generator_construct`, `dce110_tg_program_timing`, `dce110_timing_generator_program_timing_generator`, `dce110_timing_generator_program_blanking`, `dce110_timing_generator_set_drr`, `dce110_timing_generator_setup_global_swap_lock`, `dce110_timing_generator_enable_reset_trigger`, `dce110_configure_crc`, and `dce110_get_crc`. The static `dce110_tg_funcs` table exports the component contract.

Control flow: construction sets controller id, offsets, BIOS pointer, timing limits, and vtable. Programming either delegates full timing to VBIOS or writes CRTC total/blank registers directly. Wait paths poll vertical blank and counter movement. GSL and reset paths configure DCP/CRTC trigger registers. CRC setup disables before reconfiguration, programs windows, then enables selected CRC engine.

State and dependencies: state includes register offsets, timing limits, controller identity, hardware CRTC/DCP registers, BIOS state, and CRC/test-pattern settings. Risks include busy-wait polling, hard-coded timing thresholds, disabled interlace/3D validation, fragile trigger polarity logic, and register-offset assumptions shared with underlay variants. Test signals include modesets with VBIOS/direct timing paths, vblank waits, DRR changes, synchronized flips, test patterns, vertical interrupt arming, and CRC reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator.h

Purpose: shared DCE timing-generator interface and object definition. It provides sync constants, trigger-source enums, offset storage, the `dce110_timing_generator` container, and declarations reused by DCE60, DCE110 video, and DCE120 implementations.

Important types and APIs: `struct dce110_timing_generator_offsets`, `struct dce110_timing_generator`, `DCE110TG_FROM_TG`, trigger enums, `dce110_timing_generator_construct`, timing validation/programming helpers, blanking/color helpers, DRR/static-screen helpers, sync/reset helpers, CRC helpers, and `dce110_is_two_pixels_per_container`.

Integration: later ASICs reuse the base structure and many functions while swapping vtables. Offsets let one implementation address multiple CRTC/DCP instances. DCE12-specific minimum timing fields are predeclared in the base structure.

Risks and test signals: header changes have wide blast radius because multiple ASIC versions depend on this ABI. Check build coverage across DCE60/DCE80/DCE110/DCE120, and runtime coverage for all function-table entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.c

Purpose: DCE11 underlay/video timing-generator implementation using CRTCV registers. It implements a reduced timing-generator vtable for the underlay pipe.

Important APIs: `dce110_timing_generator_v_construct` and static callbacks for enable/disable, blank/unblank, direct blanking programming, advanced request, colors, vblank counter, waits, and unsupported sync operations. It reuses `dce110_tg_validate_timing`, `dce110_timing_generator_program_timing_generator`, and `dce110_is_two_pixels_per_container`.

Control flow: construction assigns `CONTROLLER_ID_UNDERLAY0`, installs the underlay vtable, and initializes DCE11 timing limits. Program timing either delegates to the shared VBIOS timing routine or writes CRTCV timing, sync, polarity, and interlace registers. Unsupported timing sync/global swap/reset callbacks log errors and return.

State and dependencies: state is mostly CRTCV hardware registers and inherited timing-limit fields. Dependencies include DCE11 register headers and the shared DCE110 timing header. Risks include no `get_position` callback, unsupported sync/reset behavior, direct CRTCV register use without instance offsets, potential typo in early-control writing `mmCRTC_CONTROL`, and limited validation inherited from DCE110. Test signals are underlay modeset, blank/unblank, color programming, vblank waits, and graceful handling when higher layers request unsupported synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.h

Purpose: public constructor declaration for the DCE11 underlay/video timing generator.

Important API: `dce110_timing_generator_v_construct(struct dce110_timing_generator *tg110, struct dc_context *ctx)`. The header depends on the caller having the shared DCE110 timing-generator type visible.

Control flow and state: no local logic. Construction assigns the underlay controller id and underlay callback table in the implementation.

Risks and test signals: because the header omits direct includes for the involved types, include-order dependencies can surface if it is used outside existing resource code. Build tests around resource construction are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_timing_generator_v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.c

Purpose: DCE11 underlay transform/scaler implementation. It programs SCLV viewport, overscan, scaling taps, filter coefficients, ratios/inits, line-buffer configuration, gamut no-op, pixel-storage depth, and exposes underlay OPP CSC/regamma callbacks through `transform_funcs`.

Important APIs: `dce110_transform_v_construct`, `dce110_xfmv_set_scaler`, `dce110_xfmv_power_up_line_buffer`, `dce110_xfmv_set_pixel_storage_depth`, and `dce110_xfmv_reset`. Helpers calculate luma/chroma viewport for 4:2:0, choose 64-phase filters, and program coefficient RAM.

Control flow: scaler setup powers line buffer, calculates viewport, writes overscan, configures taps/modes, programs ratios and filter coefficient memories only when coefficients changed, writes viewport, and flips coefficient memory with `SCL_COEF_UPDATE_COMPLETE`. Pixel-depth setup maps LB depth enums to `LBV_DATA_FORMAT` fields.

State and dependencies: state includes cached filter pointers in `dce_transform`, line-buffer metadata, hardware SCLV/LBV registers, and memory power state around coefficient RAM. Dependencies include filter tables, fixed-point conversion, DCE11 registers, and OPP CSC/regamma functions. Risks include hard-coded init values, coefficient-cache pointer comparison, sparse 4:2:0-only chroma handling, unsupported gamut remap, and polling around power gating. Test signals include scaling quality, 4:2:0 viewport correctness, coefficient updates, depth formats, and visual-confirm overscan adjustments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.h

Purpose: public declarations for the DCE11 underlay transform plus its CSC/regamma helper entry points.

Important APIs and constants: `LB_TOTAL_NUMBER_OF_ENTRIES` is 1712, `LB_BITS_PER_ENTRY` is 144, `dce110_transform_v_construct`, `dce110_opp_v_set_csc_default`, `dce110_opp_v_set_csc_adjustment`, `dce110_opp_program_regamma_pwl_v`, `dce110_opp_power_on_regamma_lut_v`, and `dce110_opp_set_regamma_mode_v`.

Integration: the transform implementation uses this header to share CSC/regamma functions across files, and resource code uses the constructor to create the underlay transform object.

Risks and test signals: the header couples transform and OPP color-management APIs, so signature drift breaks multiple files. Build tests and underlay color/scaler runtime tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce110/dce110_transform_v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/Makefile

Purpose: Kbuild fragment for the DCE112 display controller subdirectory. It adds the DCE112 compressor object to `AMD_DISPLAY_FILES`.

Important variables: `CFLAGS_$(AMDDALPATH)/dc/dce112/dce112_resource.o = -Wno-override-init`, `DCE112 = dce112_compressor.o`, `AMD_DAL_DCE112`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE112)`.

Control flow and integration: when included by the parent AMD display build, the fragment prefixes object paths with `$(AMDDALPATH)/dc/dce112/` and appends them to the global display object list. No runtime state exists.

Risks and test signals: missing objects here silently remove DCE112 compressor support. Build coverage with DCE112 enabled and link checks for compressor symbols are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c

Purpose: DCE11.2 frame-buffer compression and low-power tiling implementation. It powers and configures FBC, enables/disables compression, programs compressed surface address/pitch, configures LPT memory layout, sets invalidation triggers, and constructs/destroys compressor objects.

Important APIs: `dce112_compressor_create`, `dce112_compressor_construct`, `dce112_compressor_destroy`, `dce112_compressor_power_up_fbc`, `dce112_compressor_enable_fbc`, `dce112_compressor_disable_fbc`, `dce112_compressor_program_compressed_surface_address_and_pitch`, `dce112_compressor_program_lpt_control`, `dce112_compressor_enable_lpt`, `dce112_compressor_disable_lpt`, `dce112_compressor_is_fbc_enabled_in_hw`, and `dce112_compressor_set_fbc_invalidation_triggers`.

Control flow: construction initializes support flags, memory/bus properties, and embedded-panel limits from BIOS. Power-up enables FBC engines and default 1:1 minimum compression. Enable verifies support, backend, current state, and panel size; optionally enables LPT; selects source pipe; toggles compression due to a hardware bug; and waits for status. Disable clears compression, state, and LPT. Address programming aligns for LPT and writes high-before-low.

State and dependencies: persistent state spans compressor fields, attached instance, FBC/LPT registers, DCP/DMIF offsets, BIOS panel info, and memory-configuration fields. Risks include constructor ordering where LPT support checks `memory_bus_width` before assigning it, limited polling, only three pipe offsets, invalid memory-config warnings without failure, and reliance on caller-filled DRAM fields. Test signals are FBC enable/disable, LPT on single/multi-channel memory, compressed-surface alignment, panel-size gating, and FBC invalidation after register or memory writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.h

Purpose: public DCE112 compressor type and API declarations for FBC/LPT support.

Important types and APIs: `struct dce112_compressor_reg_offsets`, `struct dce112_compressor`, `TO_DCE112_COMPRESSOR`, lifecycle functions, FBC functions, LPT functions, and hardware state query helpers. It embeds the generic `struct compressor` from `../inc/compressor.h`.

Integration: callers allocate or receive a generic `struct compressor` and use these functions when the ASIC resource path selects the DCE112 implementation. Offset storage tracks the DCP/DMIF pipe currently attached to FBC.

Risks and test signals: API misuse can pass a generic compressor not created by this implementation into `TO_DCE112_COMPRESSOR`. Build tests catch signatures; runtime FBC/LPT tests verify object initialization, state queries, and destroy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/Makefile

Purpose: Kbuild fragment adding the DCE120 timing-generator implementation to AMD display builds.

Important variables: `CFLAGS_$(AMDDALPATH)/dc/dce120/dce120_resource.o = -Wno-override-init`, `DCE120 = dce120_timing_generator.o`, `AMD_DAL_DCE120`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE120)`.

Control flow and integration: the parent build includes this fragment, object names are prefixed with the DCE120 directory, and the resulting object list links into the AMD display module. No runtime state exists.

Risks and test signals: omission would remove DCE120 TG support at link time. Build tests with DCE120 resource code and symbol references to `dce120_timing_generator_construct` are the key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c

Purpose: DCE12/SOC15 timing-generator implementation. It ports DCE110 behavior to SOC15 register access helpers, adds DCE12 timing constraints, and provides a DCE120-specific `timing_generator_funcs` table.

Important APIs: `dce120_timing_generator_construct` plus static callbacks for timing validation, CRTC enable, blanking/color programming, DRR, scanout position, advanced request, test patterns, vertical interrupts, GSL/reset, CRC configure/read, and enable-state queries. It reuses shared DCE110 functions for BIOS timing programming, disable, counter moving, and two-pixels-per-container logic.

Control flow: register writes go through `CRTC_REG_UPDATE*`/`CRTC_REG_SET*` macros over SOC15 offsets. Timing validation first calls DCE110 validation, then checks DCE12 minimum vblank and sync widths. Program timing chooses VBIOS or direct blanking. CRC and test-pattern flows mirror DCE110 with SOC15 accessors.

State and dependencies: state is `dce110_timing_generator` plus SOC15 offsets, DCE12 min constraints, and hardware registers. Dependencies include DCE12 offset/sh-mask headers, `soc15_hw_ip.h`, `vega10_ip_offset.h`, and shared DCE110 timing definitions. Risks include macro definitions for `_4` and `_5` passing `3` as the field count, mixed reuse of DCE110 functions that may read non-SOC15 register addresses, TODOs around reset sources, and direct static-screen side effects in DRR. Test signals are DCE12 modesets, SOC15 register access validation, timing-bound rejection, DRR, sync/reset, test patterns, vertical interrupts, and CRC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.h

Purpose: DCE120 timing-generator constructor declaration.

Important API: `dce120_timing_generator_construct(struct dce110_timing_generator *tg110, struct dc_context *ctx, uint32_t instance, const struct dce110_timing_generator_offsets *offsets)`. It includes the generic timing-generator interface, graphics object ids, and the DCE110 timing-generator base type.

Integration: DCE120 reuses the DCE110 container structure while substituting its SOC15-aware vtable and limits in the implementation.

Risks and test signals: compatibility depends on the shared DCE110 structure retaining fields needed by DCE120. Build coverage and runtime construction of each CRTC instance validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/Makefile

Purpose: Kbuild fragment adding the DCE60 timing-generator implementation to AMD display builds.

Important variables: `CFLAGS_$(AMDDALPATH)/dc/dce60/dce60_resource.o = -Wno-override-init`, `DCE60 = dce60_timing_generator.o`, `AMD_DAL_DCE60`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE60)`.

Control flow and integration: the parent build includes this file, prefixes DCE60 object paths, and appends them to the display object list. Runtime behavior is in the compiled timing-generator object.

Risks and test signals: if not included, DCE60 resource code cannot link its TG constructor. Build tests for DCE60 configurations are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.c

Purpose: DCE6 timing-generator adapter that inherits most DCE110 behavior while handling DCE6 register offsets, DMIF pixel-duration programming, DCE6 advanced-request differences, and limited CRC support.

Important APIs: `dce60_timing_generator_construct`; static `program_timing`, `program_pix_dur`, `dce60_timing_generator_enable_advanced_request`, `dce60_is_tg_enabled`, and `dce60_configure_crc`. Its `dce60_tg_funcs` table mostly points to DCE110 functions with selected overrides.

Control flow: construction stores caller offsets, derived DCE6 CRTC/DCP offsets, shared timing limits, and the DCE60 vtable. Direct timing programming first writes DMIF pixel duration from `pix_clk_100hz`, then delegates to `dce110_tg_program_timing`. Advanced request updates `CRTC_START_LINE_CONTROL` and `CRTC_CONTROL` because DCE6 stores prefetch enable differently and lacks `CRTC_LEGACY_REQUESTOR_EN`.

State and dependencies: state is inherited `dce110_timing_generator` fields plus derived offsets and DCE6 hardware registers. Dependencies are DCE6 register headers and DCE110 timing APIs. Risks include unused loop index in LPT-like offset macros not relevant here, CRC configure returning true without actual CRC registers, derived offsets not used by shared macros consistently, and pixel-duration only programmed on non-VBIOS path. Test signals are DCE6 direct modesets, advanced request behavior, pixel clock changes, enable-state reporting, and CRC API callers tolerating no hardware CRC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.h

Purpose: public constructor declaration for the DCE6 timing-generator adapter.

Important API: `dce60_timing_generator_construct(struct dce110_timing_generator *tg, struct dc_context *ctx, uint32_t instance, const struct dce110_timing_generator_offsets *offsets)`.

Integration: the header documents that DCE6 inherits from DCE11. Resource code passes a DCE110-style object and offsets, and the implementation installs the DCE60 vtable.

Risks and test signals: include-order dependencies are possible because this header references `struct dce110_timing_generator` without including its header. Build coverage through resource construction is the main check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/Makefile

Purpose: Kbuild fragment adding the DCE80 timing-generator implementation to AMD display builds.

Important variables: `CFLAGS_$(AMDDALPATH)/dc/dce80/dce80_resource.o = -Wno-override-init`, `DCE80 = dce80_timing_generator.o`, `AMD_DAL_DCE80`, and `AMD_DISPLAY_FILES += $(AMD_DAL_DCE80)`.

Control flow and integration: included by the parent AMD display make logic, it contributes the DCE80 timing-generator object to the global object list. No runtime state exists in the Makefile.

Risks and test signals: the fragment assumes `dce80_timing_generator.o` exists and is needed by DCE80 resource code. Build/link coverage for DCE80 configurations is the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/Makefile -->
