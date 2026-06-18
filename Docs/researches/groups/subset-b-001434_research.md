# Research: subset-b-001434

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dc_dsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dc_dsc.c

## Purpose

`dc_dsc.c` is the shared AMD Display Core Display Stream Compression policy and negotiation layer. It parses sink DSC DPCD capability blocks, derives encoder capabilities from the active DSC object and clock/resource limits, intersects source and sink capabilities, selects slice geometry and target bits-per-pixel, and computes bandwidth ranges used by link validation.

## Important APIs, Types, And Functions

Public entry points include `dc_bandwidth_in_kbps_from_timing`, `dc_dsc_parse_dsc_dpcd`, `dc_dsc_compute_bandwidth_range`, `dc_dsc_compute_config`, `dc_dsc_stream_bandwidth_in_kbps`, `dc_dsc_stream_bandwidth_overhead_in_kbps`, `dc_dsc_get_policy_for_timing`, the policy setter functions, and `dc_dsc_get_default_config_option`. Internal helpers convert DPCD encodings for buffer size, line-buffer depth, throughput, and BPP increment; build multi-DSC slice caps; intersect `struct dsc_dec_dpcd_caps` with `struct dsc_enc_caps`; choose slice counts; and compute target BPP from a link bandwidth budget.

## Control Flow

DSC setup flows from sink DPCD parsing to encoder cap collection to `setup_dsc_config`. `setup_dsc_config` rejects unsupported branch line width, missing DSC support, incompatible color format/depth, throughput limits, invalid slice divisibility, and impossible slice height. It then applies policy defaults and debug/options overrides, chooses horizontal/vertical slice counts, optionally computes target BPP from bandwidth, and fills `struct dc_dsc_config`.

## State And Persistence Behavior

There is no disk persistence. The file owns process-global DSC policy toggles: max target BPP limit, enable-when-not-needed, DSC stream overhead disable, and 128b/132b overhead disable. It mutates caller-provided capability/range/config structures and relies on `dc->debug`, `dc->clk_mgr`, and `dc->res_pool` for runtime policy.

## Dependencies And Integration Points

It integrates with DRM DP/DSC helpers, AMD fixed-point math, clock manager, resource pool, `struct display_stream_compressor` function tables, link encoding policy, and DC timing/color enums. Link validation and stream commit code consume its bandwidth/config outputs before hardware DSC programming.

## Risks And Test Signals

Risks include global policy side effects, zero or malformed timing totals causing bad math, slice count loops depending on valid caps, and debug overrides broadening sink BPP increment behavior. Tests should cover DPCD parsing, RGB/YUV420/YUV422 policy, eDP max BPP, branch throughput/line-width limits, forced ODM slice overrides, 128b/132b and DSC overhead math, and failure cleanup that zeroes `dc_dsc_config`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dc_dsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.c

## Purpose

`dcn20_dsc.c` is the DCN2.0 hardware backend for DSC encoders. It implements the `struct dsc_funcs` table, translates validated DC DSC configuration into DRM PPS and DSCC register values, writes the DSC/DSCC/DSCCIF/DSCRM registers, exposes state reads, and controls enable, disable, disconnect, and PPS packing.

## Important APIs, Types, And Functions

Key functions are `dsc2_construct`, `dsc2_get_enc_caps`, `dsc2_read_state`, `dsc2_read_reg_state`, `dsc2_validate_stream`, `dsc2_set_config`, `dsc2_get_packed_pps`, `dsc2_enable`, `dsc2_disable`, `dsc2_disconnect`, `dsc2_wait_disconnect_pending_clear`, `dsc_prepare_config`, `dsc_override_rc_params`, `dsc_init_reg_values`, and `dsc_update_from_dsc_parameters`. Conversion helpers map DC pixel encoding and color depth to DSC-specific enums.

## Control Flow

Construction installs DCN20 function pointers and register metadata. Configuration calls `dsc_prepare_config`, which validates slice counts, version, picture size, line-buffer depth, and BPP, initializes defaults, maps pixel format, computes slice width/height, derives PPS BPP encoding, calculates RC parameters through `calc_rc_params`, applies optional RC overrides, runs `dscc_compute_dsc_parameters`, then updates register values and OPTC-facing slice/bytes-per-pixel data. `dsc2_set_config` logs and writes every PPS/rate-control register. Enable sets `DSC_CLOCK_EN` and DSCRM forwarding to the selected OPP pipe after checking for conflicting existing routing.

## State And Persistence Behavior

State is in hardware registers plus `struct dcn20_dsc::reg_vals`. No on-disk persistence exists. Enable/disable and disconnect alter DSCRM forwarding and top clock enable; `dsc2_wait_disconnect_pending_clear` polls the double-buffer update pending bit.

## Dependencies And Integration Points

The file depends on `reg_helper`, `dcn20_dsc.h`, `dscc_types.h`, `rc_calc.h`, and DRM DSC PPS packing. It is called through the DSC function table by HWSS/stream programming and feeds OPTC DSC config through `struct dsc_optc_config`.

## Risks And Test Signals

Risk centers on register field mismatches, unsupported picture widths over 5184, invalid slice divisibility, RC calculation availability under `CONFIG_DRM_AMD_DC_FP`, and conflicting OPP pipe enable attempts. Tests should validate PPS packing, register write field values for RGB/simple422/native422/native420, enable/disable/disconnect sequencing, state readback, and RC override propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h

## Purpose

`dcn20_dsc.h` defines the DCN2.0 DSC hardware abstraction: register lists, shift/mask field lists, register address containers, encoded pixel formats, cached register values, the `struct dcn20_dsc` object, and exported helper prototypes shared by later DSC generations.

## Important APIs, Types, And Functions

Important definitions include `TO_DCN20_DSC`, `DSC_REG_LIST_DCN20`, `DSC_REG_LIST_SH_MASK_DCN20`, `DSC_FIELD_LIST_DCN20`, `struct dcn20_dsc_registers`, `struct dcn20_dsc_shift`, `struct dcn20_dsc_mask`, `enum dsc_pixel_format`, `struct dsc_reg_values`, and `struct dcn20_dsc`. It declares all DCN20 implementation functions plus shared helpers such as `dsc_prepare_config`, `dsc_log_pps`, `dsc_override_rc_params`, and format/depth converters.

## Control Flow

This header does not execute logic, but it drives generated-style register access. Source files include it, instantiate ASIC-specific register tables from the macros, and use the shift/mask structs through `REG_SET`, `REG_UPDATE`, and `REG_GET`. Later generations cast or extend the DCN20 field list to reuse common DSC programming code.

## State And Persistence Behavior

The only state it defines is in-memory and hardware-facing: cached `dsc_reg_values`, register address tables, field masks/shifts, and the base DSC object. Persistence is limited to programmed MMIO state owned by the hardware backend.

## Dependencies And Integration Points

It depends on `dsc.h`, `dscc_types.h`, and DRM DSC types. It is integrated by DCN20 resource construction, DCN35 reuse/extension, and shared DSC preparation code. Any change to register field lists must match ASIC register headers.

## Risks And Test Signals

Risks include field-list drift, duplicate field-name handling through `DSC2_SF`, missing fields needed by later code, and ABI-like coupling between `struct dsc_reg_values` and register writers. Build coverage is the primary signal; hardware tests should verify register definitions for PPS, interrupt, memory power, DSCCIF, and DSCRM forwarding fields across ASIC variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.c

## Purpose

`dcn35_dsc.c` adapts the DCN20 DSC implementation for DCN3.5 hardware. It reuses most DCN20 DSC behavior, adds DCN35-specific construction and function table wiring, resets DSCC memory power controls during enable, exposes FGCg control, and reports single-encoder capabilities based on the maximum DSCCLK.

## Important APIs, Types, And Functions

The file exports `dsc35_construct` and `dsc35_set_fgcg`; internally it defines `dsc35_enable` and `dsc35_get_single_enc_caps`. The DCN35 `dsc_funcs` table delegates state reads, validation, config, PPS packing, disable, disconnect, and disconnect wait to DCN20 helpers while using DCN35 enable and single-encoder cap logic.

## Control Flow

Construction stores DC context, instance, function table, DCN20-compatible register pointers, DCN35 shift/mask pointers cast to DCN20 base types, and the max image width. Enable first clears `DSCC_MEM_PWR_FORCE` and `DSCC_MEM_PWR_DIS` because idle exit can leave DSCC memory shut down, then follows DCN20 enable checks and writes clock/forwarding state. FGCg programming toggles `DSC_FGCG_REP_DIS` opposite the requested enable flag.

## State And Persistence Behavior

State lives in the base `struct dcn20_dsc`, the hardware registers, and the function table. The file mutates DSCC memory power control, top clock enable, DSCRM forwarding, and FGCg disable state; no disk persistence exists.

## Dependencies And Integration Points

It depends on `dcn35_dsc.h`, `reg_helper`, and the DCN20 DSC shared implementation. The resource pool creates DCN35 DSC objects but higher-level policy still reaches them through `struct display_stream_compressor` and `struct dsc_funcs`.

## Risks And Test Signals

Risks include unsafe casts if DCN35 field structs stop preserving DCN20 layout, memory power reset behavior interacting with power management, and DSCCLK-derived throughput needing valid clock manager data. Tests should cover enable after idle/power-gated states, FGCg toggling, config reuse from DCN20, and cap scaling from max DSCCLK.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.h

## Purpose

`dcn35_dsc.h` defines the DCN3.5 DSC register-field extension over DCN20. It adds the fine-grain clock-gating repeat disable field and declares DCN35 constructor and FGCg control APIs.

## Important APIs, Types, And Functions

Key definitions are `DSC_REG_LIST_SH_MASK_DCN35`, `DSC_FIELD_LIST_DCN35`, `struct dcn35_dsc_shift`, `struct dcn35_dsc_mask`, `dsc35_construct`, and `dsc35_set_fgcg`.

## Control Flow

The header itself has no runtime control flow. It expands DCN20 shift/mask lists with `DSC_FGCG_REP_DIS`, allowing `dcn35_dsc.c` to reuse DCN20 register structures and function implementations while reaching the additional DCN35 field through typed casts.

## State And Persistence Behavior

It defines only static register metadata layout. Runtime state is held by `struct dcn20_dsc` and the hardware registers. The added FGCg field persists only as programmed MMIO state.

## Dependencies And Integration Points

It includes `dcn20/dcn20_dsc.h` and is consumed by DCN35 resource construction and power/clock-gating paths. Register macro expansion must match the ASIC register generated headers.

## Risks And Test Signals

Risks include structure layout mismatch with DCN20 field lists and missing generated register definitions for `DSC_FGCG_REP_DIS`. Build tests catch most declaration drift; runtime tests should verify FGCg enable/disable does not disturb existing DSC fields or DSC config programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn35/dcn35_dsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.c

## Purpose

`dcn401_dsc.c` is the DCN4.01 DSC hardware backend. It mirrors the DCN20 preparation model but uses a DCN401-specific register map, interrupt-control layout, state readback, forwarding-status wait, and object type. It still relies on shared DSC config/PPS/RC helpers.

## Important APIs, Types, And Functions

The file exports `dsc401_construct`, `dsc401_read_state`, `dsc401_validate_stream`, `dsc401_set_config`, `dsc401_enable`, `dsc401_disable`, `dsc401_disconnect`, `dsc401_wait_disconnect_pending_clear`, and `dsc401_set_fgcg`. It also defines `dsc401_get_single_enc_caps` and a private `dsc_write_to_registers`.

## Control Flow

Construction installs `dcn401_dsc_funcs`. Validation and set-config call the shared `dsc_prepare_config`; set-config then writes DCN401 registers. The writer programs debug, DSCCIF input format/BPC, slice count and ICH fields, RC buffer model size, DCN401 interrupt-control register 0, PPS config registers 0-22, and range parameters. Enable/disable manage `DSC_CLOCK_EN` and DSCRM forwarding. Disconnect clears forwarding; wait polls `DSCRM_DSC_FORWARD_EN_STATUS` rather than the older pending bit.

## State And Persistence Behavior

Runtime state is in `struct dcn401_dsc::reg_vals` and MMIO registers. `dsc401_read_state` fills additional fields in `struct dcn_dsc_state`, including block prediction, line buffer depth, version minor, RC buffer size, and simple422 state.

## Dependencies And Integration Points

The file depends on `dcn401_dsc.h`, `reg_helper`, DRM DSC helpers, `dscc_types.h`, and `rc_calc.h`. Higher-level DC code sees it through `display_stream_compressor` function pointers; packed PPS generation reuses `dsc2_get_packed_pps`.

## Risks And Test Signals

Risks include divergent DCN401 register names versus DCN20, under-programming DSCCIF size fields that are commented out here, status-poll semantic changes, and shared `dsc2_read_reg_state` compatibility. Tests should cover config register programming, disconnect wait completion, enhanced readback fields, FGCg toggling, and compare packed PPS with register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.h

## Purpose

`dcn401_dsc.h` defines the DCN4.01 DSC register abstraction, including the DCN401 register list, shift/mask list, interrupt status/control fields, memory power registers, output/rate-buffer fullness fields, object type, and exported backend functions.

## Important APIs, Types, And Functions

Important definitions include `TO_DCN401_DSC`, `DSC_REG_LIST_SH_MASK_DCN401`, `struct dcn401_dsc_registers`, `DSC_FIELD_LIST_DCN401`, `struct dcn401_dsc_shift`, `struct dcn401_dsc_mask`, `struct dcn401_dsc`, and declarations for all `dsc401_*` functions.

## Control Flow

This header has no executable flow. Its macro lists allow ASIC-specific resource files to create register tables consumed by `dcn401_dsc.c`. The field list reuses `DSC_FIELD_LIST_DCN20` and appends DCN401-specific interrupt, FGCg, fullness, and buffer status fields.

## State And Persistence Behavior

The header defines in-memory metadata and object layout. Runtime persistence is only hardware register state plus cached `dsc_reg_values` inside `struct dcn401_dsc`.

## Dependencies And Integration Points

It includes `dsc.h`, `dscc_types.h`, `dcn20_dsc.h`, and DRM DSC definitions. It integrates with resource construction, register helper macros, and shared DSC preparation code.

## Risks And Test Signals

Risks include field-list duplication with DCN20 causing missing or stale declarations, register map drift for DCN401 interrupt/memory power fields, and accidentally using DCN20-only register-state helpers against incompatible addresses. Build coverage and register programming tests are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn401/dcn401_dsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dsc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dsc.h

## Purpose

`dsc.h` is the Display Core internal DSC interface header. It defines external configuration input, OPTC output configuration, hardware readback structs, encoder capability structures, and the generation-specific DSC function table.

## Important APIs, Types, And Functions

Important types include `struct dsc_config`, `struct dsc_optc_config`, `struct dcn_dsc_state`, `struct dcn_dsc_reg_state`, `union dsc_enc_slice_caps`, `struct dsc_enc_caps`, and `struct dsc_funcs`. The function table covers capability query, state readback, validation, hardware config, PPS packing, enable/disable/disconnect, disconnect wait, single-encoder cap query, and FGCg control.

## Control Flow

The header has no implementation flow. It defines the polymorphic contract consumed by shared policy code and HWSS wrappers: policy computes `dc_dsc_cfg`, generation backends validate/program hardware, and timing generator/OPTC code consumes `dsc_optc_config`.

## State And Persistence Behavior

`dsc_config` is transient input. `dcn_dsc_state` and `dcn_dsc_reg_state` are readback snapshots. Persistent effects occur only when a backend function table writes hardware registers.

## Dependencies And Integration Points

The file intentionally includes only `dc_dsc.h`, `dc_hw_types.h`, and `dc_types.h` to avoid breaking EDID utility users. It is included by DSC backends and DC code that treats DSC blocks generically.

## Risks And Test Signals

Risks include expanding includes and breaking utility builds, changing function-table contracts without updating all generations, or misinterpreting fixed-point units such as bytes-per-pixel u3.28. Build all DSC generations and exercise HWSS DSC wrappers to catch contract drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dscc_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dscc_types.h

## Purpose

`dscc_types.h` defines the small DSC calculation interface between AMD DC register-preparation code and DRM DSC PPS structures. It adds hardware-programming data that is not part of the raw PPS.

## Important APIs, Types, And Functions

It defines `NUM_BUF_RANGES` when absent, `struct dsc_pps_rc_range`, `struct dsc_parameters`, forward-declares `struct rc_params`, and declares `dscc_compute_dsc_parameters`.

## Control Flow

There is no runtime flow in the header. Callers build a DRM `drm_dsc_config`, calculate `struct rc_params`, call `dscc_compute_dsc_parameters`, and receive a possibly adjusted PPS plus `bytes_per_pixel` and RC buffer model size for register programming.

## State And Persistence Behavior

All state is caller-owned stack or heap data. The interface has no persistent storage and no hardware side effects by itself.

## Dependencies And Integration Points

It depends on `<drm/display/drm_dsc.h>` and is used by DCN DSC backends after `calc_rc_params`. The returned `struct dsc_parameters` feeds `dsc_update_from_dsc_parameters` and OPTC configuration.

## Risks And Test Signals

Risks include ABI mismatch with DRM DSC config fields, incorrect `NUM_BUF_RANGES`, and callers misreading the nonzero return from `dscc_compute_dsc_parameters` as success. Tests should validate RC threshold/range propagation, bytes-per-pixel units, and error paths for invalid PPS values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dscc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc.c

## Purpose

`rc_calc.c` is a thin non-FPU wrapper around the AMD DSC rate-control calculator. It maps DRM DSC PPS fields to the internal FPU calculator enums and invokes `_do_calc_rc_params` inside the DC floating-point guard.

## Important APIs, Types, And Functions

The only exported function is `calc_rc_params(struct rc_params *rc, const struct drm_dsc_config *pps)`. It chooses `enum colour_mode`, `enum bits_per_comp`, BPP, slice width/height, native422/native420 flag, and DSC version minor.

## Control Flow

When `CONFIG_DRM_AMD_DC_FP` is defined, the function derives mode from `convert_rgb`, `simple_422`, `native_422`, and `native_420`; maps 8/10/other BPC to 8/10/12; enters `DC_FP_START`; calls `_do_calc_rc_params`; and exits with `DC_FP_END`. Without FP support the function is effectively empty.

## State And Persistence Behavior

It only mutates the caller-provided `rc_params`. No persistent state and no hardware access exist.

## Dependencies And Integration Points

It depends on `rc_calc.h`, which includes `dml/dsc/rc_calc_fpu.h`. `dsc_prepare_config` uses it before optional RC override and DSCC parameter computation.

## Risks And Test Signals

Risks include the misspelled local `is_navite_422_or_420` being harmless but confusing, non-8/10 BPC collapsing to 12, and empty behavior when FP support is disabled. Tests should compare calculated RC parameters for RGB, simple422, native422, native420, 8/10/12bpc, and DSC 1.1/1.2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc.h

## Purpose

`rc_calc.h` exposes the DSC rate-control calculation wrapper to DSC hardware backends while hiding the FPU implementation behind `dml/dsc/rc_calc_fpu.h`.

## Important APIs, Types, And Functions

It declares `calc_rc_params(struct rc_params *rc, const struct drm_dsc_config *pps)` and brings in `struct rc_params` plus calculator enums through the FPU header.

## Control Flow

The header has no control flow. It defines the compile-time dependency that allows `dcn20_dsc.c` and other DSC code to call the wrapper without directly invoking FPU internals.

## State And Persistence Behavior

No state is defined here. All mutation occurs in the implementation through the caller-supplied `rc_params`.

## Dependencies And Integration Points

It depends directly on the DML DSC FPU calculator. Integration is limited but important: register preparation cannot compute full PPS/RC values without this API when FP support is enabled.

## Risks And Test Signals

Risks include exposing FPU-only declarations to non-FPU build contexts and mismatched `rc_params` definitions. Kernel build matrix coverage with and without `CONFIG_DRM_AMD_DC_FP` is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc_dpi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc_dpi.c

## Purpose

`rc_calc_dpi.c` implements the DSCC parameter computation declared in `dscc_types.h`. It combines an input DRM DSC PPS with AMD RC parameters, calls the DRM DSC helper to finish RC/PPS derivation, and returns register-facing DSC parameters such as bytes-per-pixel and RC buffer model size.

## Important APIs, Types, And Functions

The exported function is `dscc_compute_dsc_parameters`. Private helpers are `copy_pps_fields`, which copies the subset of `struct drm_dsc_config` fields this path preserves, and `copy_rc_to_cfg`, which maps `struct rc_params` into DRM PPS RC fields.

## Control Flow

`dscc_compute_dsc_parameters` starts by copying the input PPS into `dsc_params->pps`, computes `initial_scale_value` from RC model size and initial fullness offset, copies the PPS into a temporary `drm_dsc_config`, overlays RC fields, chooses mux word size from bits-per-component, calls `drm_dsc_compute_rc_parameters`, computes `bytes_per_pixel` in u3.28 format by rounding `slice_chunk_size / slice_width`, copies the computed PPS back, and stores `rc_bits` as the register RC buffer model size.

## State And Persistence Behavior

All data is temporary or caller-owned. It has no static state, no register access, and no persistence.

## Dependencies And Integration Points

It depends on DRM DSC helpers, `dscc_types.h`, and `rc_calc.h` for `struct rc_params`. DCN DSC backends call it from `dsc_prepare_config` after `calc_rc_params` has filled RC values.

## Risks And Test Signals

Risks include division by `rc_model_size - initial_fullness_offset`, truncating 8-bit signed BPG offsets to 6-bit fields, array size assumptions around `QP_SET_SIZE`, mux word size thresholds, and callers treating a nonzero DRM helper return as success. Tests should validate computed PPS, bytes-per-pixel rounding, RC buffer model size, threshold/range propagation, and error handling for invalid PPS/RC inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/rc_calc_dpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/Makefile

## Purpose

`dc/dwb/Makefile` selects Display Writeback block objects for AMD Display Core builds. It adds DCN30 and DCN35 DWB source files to `AMD_DISPLAY_FILES` when floating-point display core support is enabled.

## Important APIs, Types, And Functions

The file defines `DWB_DCN30`, `AMD_DAL_DWB_DCN30`, `DWB_DCN35`, and `AMD_DAL_DWB_DCN35`, appending each expanded path under `$(AMDDALPATH)/dc/dwb/...` to `AMD_DISPLAY_FILES`.

## Control Flow

Build inclusion is gated by `ifdef CONFIG_DRM_AMD_DC_FP`. DCN30 builds `dcn30_dwb.o` and `dcn30_dwb_cm.o`; DCN35 builds `dcn35_dwb.o`.

## State And Persistence Behavior

This is build metadata only. It mutates make variables during compilation and has no runtime state.

## Dependencies And Integration Points

It depends on top-level AMD display Makefile variables and Kconfig. DWB color-management code depends on FP paths, explaining the gate.

## Risks And Test Signals

Risks include missing objects when new DWB generations are added, stale path prefixes, and accidental exclusion in non-FP configurations. Build tests with `CONFIG_DRM_AMD_DC_FP=y` should confirm DWB symbols link.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_cm_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_cm_common.h

## Purpose

`dcn30_cm_common.h` extends DCN10 color-management helper register descriptions for DCN3 transfer function programming. It supports DWB OGAM curve programming with additional region start base and offset fields.

## Important APIs, Types, And Functions

It defines `TF_HELPER_REG_FIELD_LIST_DCN3`, `struct DCN3_xfer_func_shift`, `struct DCN3_xfer_func_mask`, `struct dcn3_xfer_func_reg`, and declares `cm_helper_program_gamcor_xfer_func`, `cm3_helper_translate_curve_to_hw_format`, `cm3_helper_convert_to_custom_float`, and `is_rgb_equal`.

## Control Flow

The header has no execution. DWB color-management code populates a `dcn3_xfer_func_reg` with RAM A/B register addresses and shift/mask fields, then passes it to common helpers that program piecewise-linear transfer functions.

## State And Persistence Behavior

It defines register mapping containers only. Runtime state is in caller-owned `pwl_params` and hardware OGAM registers.

## Dependencies And Integration Points

It includes `dcn10/dcn10_cm_common.h` and is consumed by `dcn30_dwb_cm.c`. The helpers bridge DWB-specific register maps to shared color-management algorithms.

## Risks And Test Signals

Risks include mismatch between helper field expectations and DWB register mapping, especially region start/base/offset fields. Tests should verify OGAM LUT programming for equal RGB and per-channel curves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_cm_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.c

## Purpose

`dcn30_dwb.c` implements the DCN3.0 Display Writeback Controller lifecycle and function table. It reports capabilities, configures frame capture source/cropping/stereo/rate, enables and disables capture, updates color processing, and checks hardware enable state.

## Important APIs, Types, And Functions

Key functions are `dwb3_get_caps`, `dwb3_config_fc`, `dwb3_enable`, `dwb3_disable`, `dwb3_set_fc_enable`, `dwb3_update`, `dwb3_is_enabled`, `dwb3_set_stereo`, `dwb3_set_new_content`, `dwb3_set_denorm`, and `dcn30_dwbc_construct`. The function table also exposes OGAM transfer function programming through `dwb3_ogam_set_input_transfer_func`.

## Control Flow

Enable turns on DWB, programs FC source/crop/capture rate/stereo, programs HDR multiplier, gamut remap, OGAM transfer function, output denorm, enables frame capture, and sets first pixel delay. Update preserves any pre-existing DWB update lock; if unlocked, it locks, reprograms FC/color/denorm, then unlocks. Disable clears FC capture and DWB enable. `set_fc_enable` similarly preserves caller lock state while toggling capture.

## State And Persistence Behavior

State lives in DWB registers. The code mutates clock/enable, frame-capture, crop window, source size, stereo, new-content, output format/denorm/min/max, and update lock registers. It keeps no private persistent software state.

## Dependencies And Integration Points

It depends on `reg_helper`, `resource.h`, `dwb.h`, and `dcn30_dwb.h`. It integrates with higher-level writeback resource code through `struct dwbc_funcs` and with color-management helpers in `dcn30_dwb_cm.c`.

## Risks And Test Signals

Risks include update-lock imbalance, programming color paths while capture is active, unsupported output formats skipping denorm, and capability reporting assuming two pipes and one adapter. Tests should cover enable/update/disable, crop on/off, stereo on/off, lock-preserving update, `is_enabled` readback, and capture with color transforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.h

## Purpose

`dcn30_dwb.h` defines the DCN3.0 Display Writeback Controller register map, field map, object layout, and exported operations. It covers DWB top registers, scaler registers, CRC/backpressure/host-read control, output control, gamut remap, and OGAM RAM A/B programming fields.

## Important APIs, Types, And Functions

Important definitions include `TO_DCN30_DWBC`, `DWBC_COMMON_REG_LIST_DCN30`, `DWBC_COMMON_MASK_SH_LIST_DCN30`, `DWBC_REG_FIELD_LIST_DCN3_0`, `struct dcn30_dwbc_registers`, `struct dcn30_dwbc_mask`, `struct dcn30_dwbc_shift`, `struct dcn30_dwbc`, and declarations for DWB lifecycle, FC, denorm, HDR multiplier, gamut remap, and OGAM transfer function APIs.

## Control Flow

The header supplies macro-expanded register tables and typed shift/mask structs. Implementation files use these through `REG`, `FN`, and `REG_UPDATE` helpers. There is no runtime flow in the header itself.

## State And Persistence Behavior

It defines the `struct dcn30_dwbc` software object holding base `dwbc`, register table, shifts, and masks. Runtime state is hardware register state; no durable storage is defined.

## Dependencies And Integration Points

It is consumed by DCN30 DWB implementation, DCN35 extension, and generated ASIC resource files. It also defines register fields needed by DWB color management for LUT/gamut programming.

## Risks And Test Signals

Risks include macro/list drift, huge field lists hiding missing declarations, and incorrect register ordering causing writes to wrong blocks. Build coverage plus register-level write/read tests for FC, output control, gamut remap, and OGAM RAM A/B are critical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb_cm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb_cm.c

## Purpose

`dcn30_dwb_cm.c` implements DWB color-processing programming for DCN3.0: OGAM transfer functions, gamut remap matrices, and HDR multiplier. It translates DC color parameters into DWB register writes.

## Important APIs, Types, And Functions

Public functions are `dwb3_ogam_set_input_transfer_func`, `dwb3_set_gamut_remap`, and `dwb3_program_hdr_mult`. Private helpers map OGAM register fields, program RAM A/B region settings, determine current OGAM RAM, configure LUT writes, write PWL LUT data, program LUT selection, and program gamut remap coefficient banks.

## Control Flow

OGAM programming allocates `pwl_params`, converts the transfer function with `cm_helper_translate_curve_to_hw_format`, selects the inactive RAM bank based on current mode, writes region metadata and LUT samples, then switches `DWB_OGAM_SELECT`. Equal RGB curves use a single write mask; non-equal curves program red, green, and blue separately. Gamut remap bypasses unless software adjustment is requested, converts a 3x4 matrix to register values, and ping-pongs between remap A and B coefficient banks.

## State And Persistence Behavior

Software state is temporary allocation only. Hardware state includes OGAM mode/select/LUT contents, region metadata, gamut remap coefficient banks/mode, and HDR multiplier.

## Dependencies And Integration Points

It depends on `fixed31_32`, conversion helpers, `dwb.h`, `dcn30_dwb.h`, `dcn30_cm_common.h`, and DCN10 color helpers. It is called from DWB enable/update paths.

## Risks And Test Signals

Risks include allocation failure silently skipping OGAM, inactive-bank selection errors, LUT point count assumptions, equal-RGB optimization masking channel bugs, and bypassing non-software gamut adjustments. Tests should cover null transfer functions, PWL curves, RGB-equal and per-channel curves, gamut ping-pong, HDR multiplier writes, and update while capture is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn35/dcn35_dwb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn35/dcn35_dwb.c

## Purpose

`dcn35_dwb.c` adapts the DCN30 Display Writeback Controller for DCN3.5. It delegates construction to the DCN30 constructor with extended shift/mask structs and adds fine-grain clock-gating control.

## Important APIs, Types, And Functions

The exported functions are `dcn35_dwbc_construct` and `dcn35_dwbc_set_fgcg`. The file defines DCN35-specific `FN` access casting but otherwise reuses the DCN30 DWB implementation.

## Control Flow

Construction calls `dcn30_dwbc_construct`, casting DCN35 shift/mask tables to DCN30-compatible base types. FGCg control updates `DWB_FGCG_REP_DIS` to the inverse of the requested enable flag.

## State And Persistence Behavior

No private software state is added. Runtime effects are the inherited DWB object initialization and the DWB enable-clock-control register field for FGCg.

## Dependencies And Integration Points

It depends on `reg_helper` and `dcn35_dwb.h`. Resource construction uses this adapter when instantiating DCN35 DWB blocks while higher-level DWB code continues through `dwbc_funcs`.

## Risks And Test Signals

Risks include layout assumptions in casted shift/mask structs and FGCg toggling interfering with enable state. Build and runtime tests should verify inherited DCN30 operations plus FGCg enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn35/dcn35_dwb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn35/dcn35_dwb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn35/dcn35_dwb.h

## Purpose

`dcn35_dwb.h` defines the DCN3.5 DWB extension over DCN30. It adds the FGCg repeat-disable field to the DWB register field list and declares construction/FGCg APIs.

## Important APIs, Types, And Functions

Key definitions are `DWBC_COMMON_MASK_SH_LIST_DCN35`, `DWBC_REG_FIELD_LIST_DCN3_5`, `struct dcn35_dwbc_mask`, `struct dcn35_dwbc_shift`, `dcn35_dwbc_construct`, and `dcn35_dwbc_set_fgcg`.

## Control Flow

The header has no execution flow. It extends the macro-expanded DCN30 field set with `DWB_FGCG_REP_DIS` so DCN35 source can reuse the base DWB object and programming code.

## State And Persistence Behavior

It defines metadata only. Runtime state persists in hardware registers and inherited `struct dcn30_dwbc`.

## Dependencies And Integration Points

It includes `resource.h`, `dwb.h`, and `dcn30/dcn30_dwb.h`. It is consumed by DCN35 DWB construction and clock-gating code.

## Risks And Test Signals

Risks include field-list layout mismatch and missing register definitions on some ASIC headers. Build coverage and FGCg register toggling tests are sufficient for this small adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn35/dcn35_dwb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/Makefile

## Purpose

`dc/gpio/Makefile` assembles AMD Display Core GPIO support. It adds common GPIO service/base/pin/translate objects and generation-specific hardware factory/translate objects for DCE and DCN families.

## Important APIs, Types, And Functions

It defines common `GPIO`, `AMD_DAL_GPIO`, and per-generation variables for DCE60, DCE80, DCE110, DCE120, DCN10, DCN20, DCN21, DCN30, DCN315, DCN32, DCN401, and DCN42. Each generation appends paths to `AMD_DISPLAY_FILES`; DCE60 is gated by `CONFIG_DRM_AMD_DC_SI`.

## Control Flow

This is make-time flow only. The common GPIO objects are always appended, SI-era DCE60 objects are conditional, and later generations are unconditionally added under the AMD display build.

## State And Persistence Behavior

It changes build variables only. No runtime state exists.

## Dependencies And Integration Points

It depends on `AMDDALPATH`, `AMD_DISPLAY_FILES`, and Kconfig. It integrates GPIO hardware factories and translators with the overall AMDGPU DC build.

## Risks And Test Signals

Risks include stale generation lists, duplicate or missing object inclusion, and copyright/date churn. Build tests across supported ASIC Kconfigs should catch unresolved factory/translator symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.c

## Purpose

`hw_factory_dce110.c` builds the DCE11.0 GPIO hardware factory. It defines HPD and DDC register tables, shift/mask tables, pin register binding callbacks, and factory function pointers/pin counts.

## Important APIs, Types, And Functions

Important elements are HPD register arrays from `HPD_REG_LIST`, DDC data/clock register arrays, `hpd_shift`, `hpd_mask`, `ddc_shift`, `ddc_mask`, `define_ddc_registers`, `define_hpd_registers`, the `hw_factory_funcs` table, and `dal_hw_factory_dce110_init`.

## Control Flow

Initialization fills `factory->number_of_pins` for DDC data/clock, generic, HPD, GPIO pad, VIP pad, sync, and GSL, then assigns factory funcs. DDC binding switches on `pin->id` to select data or clock register arrays by encoder index and sets base GPIO register pointers. HPD binding sets HPD register/shifts/masks and base GPIO regs.

## State And Persistence Behavior

State is written into the caller-provided `struct hw_factory` and individual `hw_gpio_pin`/`hw_ddc`/`hw_hpd` objects. Hardware registers are not programmed here; this file only binds metadata.

## Dependencies And Integration Points

It depends on DCE11 generated register headers, `reg_helper`, shared GPIO factory/pin classes, and HPD/DDC register macro headers. GPIO service code calls this to instantiate generation-specific pins.

## Risks And Test Signals

Risks include array index assumptions for eight DDC pins and six HPD pins, missing generic pin init despite nonzero generic count, and critical assertion on unsupported DDC pin IDs. Tests should create DDC data/clock and HPD pins for all valid indices and verify register pointers and pin counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.h

## Purpose

`hw_factory_dce110.h` declares the DCE11.0 GPIO hardware factory initializer.

## Important APIs, Types, And Functions

The only API is `dal_hw_factory_dce110_init(struct hw_factory *factory)`.

## Control Flow

The header has no runtime logic. Consumers include it to call the initializer during GPIO service/resource setup for DCE11-class hardware.

## State And Persistence Behavior

It defines no state. The implementation initializes caller-owned `struct hw_factory` data.

## Dependencies And Integration Points

The declaration depends on `struct hw_factory` being visible to the including translation unit. It connects generation-specific DCE110 factory setup to shared GPIO factory code.

## Risks And Test Signals

Risks are limited to missing forward declarations in include order or signature drift with the implementation. Build coverage catches these; runtime GPIO factory tests should verify the implementation-populated function table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce110/hw_factory_dce110.h -->
