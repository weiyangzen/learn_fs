# Research: subset-b-001445

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/hw_sequencer.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/hw_sequencer.h

## Purpose

`hw_sequencer.h` is the public hardware sequencing contract for AMD Display Core. It ties high-level DC state transitions to ASIC-specific HWSS implementations through a large `struct hw_sequencer_funcs` vtable and a newer block-sequence layer for batching register actions, including DMUB-assisted fast paths.

## Important APIs, Types, And Functions

Key exported structures include many `*_params` wrappers, `union block_sequence_params`, `enum block_sequence_func`, `struct block_sequence`, `struct block_sequence_state`, and `struct hw_sequencer_funcs`. The vtable covers initialization, context application, plane enable/disable, pipe locking, timing synchronization, stream blanking, bandwidth, infoframes, cursor offload, color programming, VM setup, writeback, clocks, audio, link output, MALL/SubVP/FAMS, power gating, DSC, DCCG, HUBP/DPP/MPC operations, and memory QoS measurement. Helper APIs include `hwss_execute_sequence`, `hwss_build_fast_sequence`, many `hwss_*` executor functions, and many `hwss_add_*` builders that append typed block-sequence steps.

## Control Flow

The traditional path calls function pointers in `dc->hwss` for whole operations such as `apply_ctx_to_hw`, `enable_plane`, `update_dchubp_dpp`, or `pipe_control_lock`. The block-sequence path stores one enum plus a matching params union member per step, then `hwss_execute_sequence` dispatches each step to its `hwss_*` executor. Builders such as `hwss_add_hubp_setup`, `hwss_add_dsc_enable_with_opp`, and `hwss_add_optc_set_odm_combine` encode the operation and arguments without immediately touching hardware.

## State And Persistence Behavior

The header itself has no persistence, but it describes hardware-mutating callbacks. State flows through `struct dc`, `struct dc_state`, `struct pipe_ctx`, resource objects, DMUB command buffers, and per-pipe cached registers. `block_sequence_state` persists a temporary ordered command list and a step count during a commit. Runtime effects include register programming, power and clock state, stream/plane enablement, cursor updates, DWB state, ABM state, MALL/SubVP state, and debug/log snapshots.

## Dependencies And Integration Points

It depends on DC public types, clock source, timing generator, OPP, link encoder, core status, shared HW types, and DSC. It integrates with `core_types.h` through `pipe_ctx`, `dc_state`, resource objects, and the per-context block-sequence arrays. ASIC-specific HWSS files populate `hw_sequencer_funcs` and implement the block executors. DMUB, HUBP, DPP, MPC, HUBBUB, DCCG, DSC, ABM, writeback, and link code are all integration points.

## Risks And Edge Cases

The enum, union, builder functions, and executor dispatch table must remain synchronized. `MAX_HWSS_BLOCK_SEQUENCE_SIZE` scales from enum count times `MAX_PIPES`; missing bounds checks around builders would corrupt a sequence. Many callbacks are optional by ASIC generation, so callers must guard unsupported operations. Pointer-heavy params can outlive their source if sequences are retained too long. Fast DMUB/control-lock paths are sensitive to ordering, pipe topology, SubVP phantom pipes, ODM combines, DSC enablement, and pending register updates.

## Test Signals

Kernel builds catch signature drift and enum/union mismatches. Runtime validation should exercise full commits, surface-only updates, plane enable/disable, DSC/ODM transitions, cursor offload, SubVP/FAMS/MALL paths, writeback enable/disable, ABM, power-gating, and underflow recovery. Useful signals include blank-complete waits, pending-update waits, underflow debug data, visual-confirm colors, hardware-state logs, DMUB command success, and memory QoS readings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/hw_sequencer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/hw_sequencer_private.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/hw_sequencer_private.h

## Purpose

`hw_sequencer_private.h` defines private HWSS state and generation-specific helper callbacks used behind the public sequencer interface. It is the internal companion to `hw_sequencer.h`, concentrating workarounds, power-gating controls, stream/plane helper hooks, and the `struct dce_hwseq` object.

## Important APIs, Types, And Functions

Important types are `enum pipe_gating_control`, `struct dce_hwseq_wa`, `struct hwseq_wa_state`, `struct hwseq_private_funcs`, and `struct dce_hwseq`. Private callbacks cover stream gating, pipe initialization/reset, atomic plane disconnect/disable/power-down, MPCC updates, transfer functions, blanking, stream timing, vupdate interrupts, underflow checks, VGA disable, golden init, root-clock and power-gating controls, DSC power status/control, ODM/writeback programming, HDR multiplier, p-state verification, pipe programming, color LUTs, MALL, DCCG dividers, FIFO resync, controller application, and CM histogram programming.

## Control Flow

Public HWSS callbacks delegate lower-level generation details into `dce_hwseq.funcs`. Several callbacks have paired sequence-producing variants, such as atomic disconnect, blank pixel data, plane power down, update ODM, writeback programming, HDR multiplier, p-state verification, program pipe, and MALL pipe config. Workaround flags in `wa` decide whether specific code paths run, while `wa_state` records whether a workaround is currently applied.

## State And Persistence Behavior

`dce_hwseq` persists for the DC instance and stores register tables, masks/shifts, workaround configuration, current workaround state, private callbacks, and framebuffer/UMA aperture locations. Its effects are hardware state changes and in-memory workaround bookkeeping. There is no disk persistence.

## Dependencies And Integration Points

It includes `dc_types.h` and the public HWSS header. It forward-declares core DC/resource/HW objects to avoid exposing implementation headers. ASIC-specific DCE/DCN sequencer implementations initialize `dce_hwseq`, use `block_sequence_state` from the public header, and consume resources from `core_types.h`.

## Risks And Edge Cases

Workaround flags are hardware-generation-sensitive; applying them on the wrong ASIC can cause blanking, underflow, p-state, or power-gating regressions. Sequence and non-sequence callback variants must remain behaviorally equivalent. `wa_state` contains frame-sensitive state for multi-plane self-refresh transitions, so stale state can incorrectly block self refresh or skip blanking. Power/root-clock controls require strict ordering around DPP/HUBP/DSC use.

## Test Signals

Builds catch callback signature drift. Runtime tests should cover boot init, S0i3/golden init, plane atomic transitions, stream timing enable, ODM changes, MALL/SubVP programming, DSC power gating, p-state allow/disallow, underflow detection, and reset/back-end recovery. Underflow logs, power-gating status, DSC PG status, and visual or blanking artifacts are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/hw_sequencer_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/bw_fixed.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/bw_fixed.h

## Purpose

`bw_fixed.h` defines the fixed-point numeric type used by legacy DCE bandwidth and watermark calculations. It represents values as signed 64-bit integers with 24 fractional bits and provides arithmetic, conversion, comparison, min/max, floor, and ceil helpers.

## Important APIs, Types, And Functions

`struct bw_fixed` wraps `int64_t value`. Constants and macros include `BW_FIXED_BITS_PER_FRACTIONAL_PART`, `BW_FIXED_GET_INTEGER_PART`, `BW_FIXED_MIN_I32`, and `BW_FIXED_MAX_I32`. Inline helpers include `bw_min2`, `bw_max2`, `bw_min3`, `bw_max3`, `bw_int_to_fixed`, `bw_fixed_to_int`, `fixed31_32_to_bw_fixed`, `bw_add`, `bw_sub`, `bw_div`, `bw_mod`, and comparisons. External helpers include `bw_int_to_fixed_nonconst`, `bw_frc_to_fixed`, `bw_mul`, `bw_floor2`, and `bw_ceil2`.

## Control Flow

The header mostly inlines simple operations. `bw_int_to_fixed` uses `__builtin_constant_p` and `BUILD_BUG_ON` to reject out-of-range constant conversions at compile time; non-constant values go to `bw_int_to_fixed_nonconst`. Division delegates to fraction conversion, and modulo uses `div64_u64_rem`.

## State And Persistence Behavior

There is no persistent state. All operations return new `bw_fixed` values or primitive comparisons. State is carried by callers in DCE calculation structures.

## Dependencies And Integration Points

It is consumed by `dce_calcs.h` and other legacy bandwidth code. It expects kernel integer types, `BUILD_BUG_ON`, and `div64_u64_rem` to be available through surrounding includes. It bridges fixed31.32 values with the legacy 24-fractional-bit format.

## Risks And Edge Cases

Addition and subtraction do not check overflow. Multiplication/division behavior depends on external implementations and divisor validity. `bw_mod` casts a signed result storage pointer to `uint64_t *`, so negative inputs or zero divisors are risky. `bw_fixed_to_int` truncates toward the raw arithmetic shift behavior. Compile-time range checks apply only to constants.

## Test Signals

Unit tests should cover integer/fraction conversion, negative values, constant boundary values, floor/ceil significance, multiply/divide precision, modulo, and comparisons. DCE bandwidth golden tests catch practical regressions in watermark and clock decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/bw_fixed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/clock_source.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/clock_source.h

## Purpose

`clock_source.h` defines the display clock-source abstraction for pixel clock generation. It describes PLL inputs, spread-spectrum and de-spread metadata, computed divider settings, and function pointers for programming or querying pixel clock sources.

## Important APIs, Types, And Functions

Important types include `spread_spectrum_data`, `delta_sigma_data`, `pixel_clk_flags`, `csdp_ref_clk_ds_params`, `pixel_clk_params`, `pll_settings`, `calc_pll_clock_source_init_data`, `calc_pll_clock_source`, `clock_source_funcs`, and `clock_source`. Operations include `cs_power_down`, `program_pix_clk`, `get_pix_clk_dividers`, `get_pixel_clk_frequency_100hz`, and `override_dp_pix_clk`.

## Control Flow

Callers populate `pixel_clk_params` from stream timing, signal type, encoder/controller IDs, DP reference clock data, color depth, pixel encoding, and programming flags. A clock-source implementation calculates `pll_settings` and optionally programs the pixel clock for the requested DP/HDMI/LVDS/analog output. Query and override functions support readback and DP-specific clock adjustment.

## State And Persistence Behavior

`clock_source` persists as a resource-pool object with a context, clock-source ID, DP-clock-source flag, and vtable. `pll_settings` is stored in `pipe_ctx` when a pipe is mapped. Hardware state changes occur when `program_pix_clk` or power-down functions run.

## Dependencies And Integration Points

The file includes DC types, graphics object IDs, and BIOS parser types. It integrates with resource allocation, stream/link programming, VBIOS PLL calculations, DCCG/DP DTO setup, and HWSS link-output callbacks. `core_types.h` stores clock sources in `resource_pool` and `pipe_ctx`.

## Risks And Edge Cases

Clock units differ across fields: requested pixel clock is in 100 Hz, requested symbol/DP ref clocks are kHz, and PLL frequencies are also 100 Hz or kHz depending on field. Spread-spectrum percentage divider can be 100 or 1000 and must match firmware interpretation. Wrong encoder/controller IDs can program the wrong PLL path. DP de-spread and on-the-fly tuning are DP-specific and should not leak to non-DP signals.

## Test Signals

Builds catch vtable drift. Runtime tests should validate exact pixel-clock generation for HDMI, DP, eDP, LVDS, and analog paths; spread-spectrum on/off; YCbCr 4:2:0; DP ref-clock de-spread; clock readback; and clock-source power-down. Link training failures and mode timing drift are major practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/clock_source.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/compressor.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/compressor.h

## Purpose

`compressor.h` defines the legacy frame-buffer compression (FBC) abstraction. It tracks compression capabilities, buffer sizing, attached controller instance, memory geometry, and callbacks for enabling, disabling, and programming FBC state.

## Important APIs, Types, And Functions

Important types are `enum fbc_compress_ratio`, `union fbc_physical_address`, `struct compr_addr_and_pitch_params`, `enum fbc_hw_max_resolution_supported`, `struct compressor_funcs`, `struct compressor`, `struct fbc_input_info`, and `struct fbc_requested_compressed_size`. Operations include `power_up_fbc`, `enable_fbc`, `disable_fbc`, `set_fbc_invalidation_triggers`, `surface_address_and_pitch`, and `is_fbc_enabled_in_hw`.

## Control Flow

Callers calculate source view size and compressed-surface needs, allocate or select an FBC buffer, set the compressor surface address/pitch, program invalidation triggers, and enable FBC for a controller instance. Disable paths clear FBC state and can query hardware mapping to determine the active CRTC.

## State And Persistence Behavior

`struct compressor` persists in the DC resource set. It stores attached instance, enable state, option bits, compressed-surface physical address, panel size, memory layout information, allocated/preferred sizes, LPT channel count, and minimum compression ratio. Persistent effects are hardware FBC programming and in-memory resource bookkeeping.

## Dependencies And Integration Points

The header depends on graphics object IDs and BIOS parser interfaces. It integrates with embedded-panel paths, memory allocation, invalidation logic, and older DCE bandwidth/FBC support. It is separate from DCN DCC surface compression handled by HUBP/HUBBUB.

## Risks And Edge Cases

FBC is constrained by fixed maximum resolutions and memory layout. Buffer size alignment and framebuffer-pool requirements must match firmware and hardware expectations. Stale `attached_inst` or `is_enabled` state can map compression to the wrong controller. Dynamic allocation and LPT options have platform-specific constraints.

## Test Signals

Tests should cover enable/disable around mode sets, source-size boundary values, dynamic vs static buffer allocation, invalidation triggers, hardware enabled readback, embedded panel resolutions, and suspend/resume. Visual corruption and stale compressed frames are the key runtime failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/compressor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/core_status.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/core_status.h

## Purpose

`core_status.h` centralizes Display Core status/error codes and string conversion helpers. The enum values identify validation, resource-allocation, bandwidth, link, DSC, cursor, and unexpected failure outcomes.

## Important APIs, Types, And Functions

`enum dc_status` defines `DC_OK`, resource failures for controllers, encoders, clocks, DSC, and link encoders, validation failures for controller/encoder/surface/bandwidth/scaling/DSC/link bandwidth/tunnel bandwidth/cursor support, clock min/max failures, unsupported/value errors, DP training/payload failures, and `DC_ERROR_UNEXPECTED`. Helpers are `dc_status_to_str`, `dc_pixel_encoding_to_str`, and `dc_color_depth_to_str`.

## Control Flow

Display validation and commit functions return `enum dc_status` to short-circuit unsuccessful modes or resource mappings. Diagnostic paths convert status, pixel encoding, and color depth values to strings for logging.

## State And Persistence Behavior

The header has no state. Status values propagate through call stacks and may be recorded in logs or validation results owned by callers.

## Dependencies And Integration Points

It includes `dc_hw_types.h` for pixel-encoding and color-depth enums. It is used by resource validation, HWSS context application, clock programming, link training, DSC allocation, and public DC APIs that need stable status reporting.

## Risks And Edge Cases

Numeric enum values are explicit and may be externally observed in logs or tooling; renumbering is risky. `DC_OK` starts at 1 while `DC_ERROR_UNEXPECTED` is -1, so code must not treat zero as success. New validation failures need string mappings to avoid opaque logs.

## Test Signals

Builds catch missing enum types. Unit/log tests should verify every status maps to a meaningful string and failure paths preserve the precise status. Integration tests should cover bandwidth, DSC, link bandwidth, link training, payload allocation, and clock-limit failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/core_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/core_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/core_types.h

## Purpose

`core_types.h` defines the central internal Display Core resource and state model. It ties streams, planes, pipes, links, bandwidth/DML output, clocks, encoders, writeback, MALL/FAMS, and HWSS block sequences into the `dc_state` object used for validation and commits.

## Important APIs, Types, And Functions

Major types include `resource_funcs`, `resource_pool`, `stream_resource`, `plane_resource`, `link_resource`, `link_config`, `pipe_update_flags`, `pixel_rate_divider`, `p_state_switch_method`, `dsc_padding_params`, `pipe_ctx`, `link_enc_cfg_context`, `resource_context`, DCE/DCN bandwidth outputs, `bw_context`, `dc_dmub_cmd`, `dc_state`, `replay_context`, `dc_bounding_box_max_clk`, and `memory_qos`. `resource_funcs` is the resource-manager vtable for validation, DML pipe population, link encoder assignment, pipe acquisition/release, writeback population, MALL/mcache programming, DSC resource attachment, and encoder switching.

## Control Flow

Validation starts from a prospective `dc_state`, uses `resource_funcs` to acquire resources, populate DML pipe inputs, validate bandwidth/global/planes, assign encoders, and calculate watermarks/DLG. Commit/HWSS paths consume `pipe_ctx` entries, per-pipe update flags, cached DML/RQ/DLG/TTU registers, and block sequences. Reference counting on `dc_state` manages lifetime as current and candidate contexts move through validation and commit.

## State And Persistence Behavior

`dc_state` is the persistent in-memory description of a requested display state: stream arrays, phantom stream/plane arrays, resource context, PowerPlay display config, DML/DML2 bandwidth context, clock manager pointer, pending block sequence, DMUB commands, refcount, performance parameters, and power source. `pipe_ctx` persists per-pipe mappings and cached programming data. `resource_pool` persists hardware objects owned by the DC instance.

## Dependencies And Integration Points

The header includes broad DC, DCE, DCN, DML, DML2, hardware, DMUB, link, audio, DPP, DWB, HUBP, MPC, panel, and power-management headers. It is the integration point between resource management, bandwidth validation, HWSS, link services, color, writeback, mcache/MALL, and clock management.

## Risks And Edge Cases

This is a high-blast-radius header; layout or semantic changes affect nearly every DC subsystem. `pipe_ctx` links (`top_pipe`, `bottom_pipe`, ODM neighbors) must remain consistent during splits/merges. Resource reference counts and acquisition bitmaps can leak or double-assign hardware. Large bandwidth/DML fields must not be stack-copied casually. Phantom/SubVP and mcache/FAMS state adds additional hidden coupling to commit ordering.

## Test Signals

Full AMDGPU DC builds catch type drift. Functional tests should cover multi-stream, MPO, ODM, MPC combine, DSC, writeback, DP HPO, link encoder reassignment, phantom/SubVP, MALL/mcache, cursor, and power-source changes. Resource leak checks, validation status, pipe topology dumps, DML outputs, block sequence counts, and refcount warnings are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/core_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/custom_float.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/custom_float.h

## Purpose

`custom_float.h` declares a helper that converts DC fixed-point values into hardware-specific custom floating-point register encodings. It is used where display hardware exposes non-IEEE float-like fields.

## Important APIs, Types, And Functions

The single API is `convert_to_custom_float_format(struct fixed31_32 value, const struct custom_float_format *format, uint32_t *result)`. Inputs are a fixed31.32 value and a format description; output is the encoded register value.

## Control Flow

Callers provide a value and target format, then the implementation computes sign/exponent/mantissa according to `custom_float_format` and returns success/failure. The header itself has no executable logic.

## State And Persistence Behavior

No state is stored. The only effect is writing the encoded value through `result`. Hardware persistence occurs later when callers write that result to registers.

## Dependencies And Integration Points

It includes `bw_fixed.h`, `hw_shared.h`, and `opp.h`, which provide fixed-point and format definitions. It integrates with OPP/DPP color, scaling, or other programming paths that require custom register encodings.

## Risks And Edge Cases

Encoding is sensitive to rounding, sign handling, exponent limits, zero, saturation, and format bit widths. A mismatched `custom_float_format` can produce valid-looking but wrong register values. Callers must handle a false return and avoid programming uninitialized `result`.

## Test Signals

Unit tests should cover zero, negative values, smallest/largest representable values, rounding boundaries, overflow/saturation, and each hardware format. Visual color/brightness regressions can indicate conversion errors in integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/custom_float.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dce_calcs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dce_calcs.h

## Purpose

`dce_calcs.h` defines the legacy DCE bandwidth and watermark calculation interface. It models DCE IP constants, VBIOS/board memory characteristics, per-mode scratch variables, and output watermarks/clocks using `bw_fixed`.

## Important APIs, Types, And Functions

Key types include `enum bw_calcs_version`, `enum bw_defines`, `struct bw_calcs_dceip`, `struct bw_calcs_vbios`, and `struct bw_calcs_data`. Public functions are `bw_calcs_init(...)` to initialize static DCE/VBIOS inputs and `bw_calcs(...)` to validate a pipe set and fill `struct dce_bw_output`.

## Control Flow

Initialization populates static IP and board parameters from ASIC ID and firmware-derived values. Runtime calculation consumes a DC context, DCE IP data, VBIOS data, current pipe array, and pipe count. It computes scaler, tiling, compression, cursor, urgent latency, stutter, DRAM/NB p-state, request bandwidth, DISPCLK/SCLK/YCLK requirements, and watermarks, returning whether the configuration is supported.

## State And Persistence Behavior

The header defines large temporary calculation state but does not persist data itself. Callers keep initialized DCE/VBIOS inputs and store final values in `dce_bw_output` within `dc_state.bw_ctx`. There is no disk persistence and no direct register programming.

## Dependencies And Integration Points

It depends on `bw_fixed.h` and forward-declared DC/pipe/output types. `core_types.h` embeds DCE output in `union bw_output`. Resource validation and HWSS bandwidth programming consume the resulting clocks, watermarks, and state-change enable flags.

## Risks And Edge Cases

The formulas use many fixed-point divisions and array indexes up to `maximum_number_of_surfaces`. Incorrect pipe counts or unsupported surface combinations can overflow arrays or produce invalid watermarks. Legacy enum constants include negative `notok/na` values mixed with positive symbolic values. Fixed-point precision and rounding determine borderline validation outcomes.

## Test Signals

Golden tests should cover legacy ASIC versions, multi-display sync, underlay formats, FBC/LPT, writeback, rotations, tiling modes, scatter-gather, cursor sizes, compression rates, and p-state/stutter enablement. Integration signals include `dce_bw_output` watermarks, required clocks, validation failure status, and underflow behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dce_calcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dcn_calc_math.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dcn_calc_math.h

## Purpose

`dcn_calc_math.h` declares float math helpers used by early DCN bandwidth calculations. It wraps min/max, floor/ceil, modulo, power, logarithm, and absolute-value operations behind DCN-specific names.

## Important APIs, Types, And Functions

Functions include `dcn_bw_mod`, `dcn_bw_min2`, `dcn_bw_max`, `dcn_bw_max2`, `dcn_bw_floor2`, `dcn_bw_floor`, `dcn_bw_ceil2`, `dcn_bw_ceil`, `dcn_bw_max3`, `dcn_bw_max5`, `dcn_bw_pow`, `dcn_bw_log`, and `dcn_bw_fabs`.

## Control Flow

There is no header control flow beyond declarations. Calculation code calls these helpers while evaluating DCN DML-style formulas and support limits.

## State And Persistence Behavior

No state is stored. All helpers return computed scalar values.

## Dependencies And Integration Points

It integrates with `dcn_calcs.h` implementation files and early DCN bandwidth validation. The helpers are separate from the newer DML inline math used by later display-mode libraries.

## Risks And Edge Cases

Float calculations are sensitive to precision and compiler floating-point behavior. Division-like operations such as modulo/floor by significance must handle zero or invalid significance in implementations. Log/pow domain errors can propagate NaN into validation. `dcn_bw_max` uses unsigned integers while the others use floats.

## Test Signals

Unit tests should cover negative values, zero, non-integer significance, large values, log/pow domains, and max/min tie cases. DCN bandwidth golden tests catch formula-level regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dcn_calc_math.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dcn_calcs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dcn_calcs.h

## Purpose

`dcn_calcs.h` defines early DCN bandwidth, watermark, and mode-support data structures and APIs. It mirrors Display Mode Library concepts for DCN 1.x using float-heavy internal state, SoC/IP bounding boxes, and validation/update helper functions.

## Important APIs, Types, And Functions

Important constants define plane/state counts and DDR4 parameters. `enum dcn_bw_defs` represents voltage states, support flags, swizzle/surface/pixel/output formats, and encoder bpc. `struct dcn_bw_internal_vars` is the large formula workspace. `struct dcn_soc_bounding_box` and `struct dcn_ip_params` define hardware bounds with external defaults `dcn10_soc_defaults` and `dcn10_ip_defaults`. Public functions include `dcn_validate_bandwidth`, `dcn_get_soc_clks`, PPLIB clock update/notify helpers, `dcn_bw_sync_calcs_and_dml`, and `swizzle_mode_to_macro_tile_size`.

## Control Flow

Validation populates `dcn_bw_internal_vars` from `dc_state` pipe data, SoC/IP limits, and PowerPlay clocks, then evaluates bandwidth, DPP/DET/LB sizing, prefetch, urgent/stutter/DRAM-clock watermarks, clock support, DIO support, writeback support, and selected voltage level. PPLIB update functions refresh clock tables and notify firmware of watermark ranges.

## State And Persistence Behavior

`dcn_bw_internal_vars` is embedded in `dc_state`, not stack-allocated. Final outputs flow into `dc_state.bw_ctx.bw.dcn`, including clocks, watermarks, writeback arb params, compbuf/MALL sizes, mcache allocations, and FAMS config in newer code paths. There is no direct register programming in this header.

## Dependencies And Integration Points

It includes `bw_fixed.h` and `dml/display_mode_lib.h`. It integrates with resource validation, clock manager/PPLIB, HUBBUB watermark programming, DML synchronization, and swizzle/tile interpretation used by memory-fetch programming.

## Risks And Edge Cases

The workspace has many fixed-size arrays based on six planes and five states; exceeding those assumptions is unsafe. Float comparisons around support thresholds can change validation at mode boundaries. `dcn_bw_defs` mixes support values, voltage states, formats, and output types in one enum, so assigning the wrong category may compile. Legacy DCN calcs and newer DML/DML2 data must stay synchronized.

## Test Signals

Golden validation should cover DCN10 clocks, DPP split, ODM/DSC capability, DCC, swizzle modes, writeback, GPUVM/PTE, prefetch, p-state/stutter support, and PowerPlay clock-table changes. Runtime signals include watermark ranges, selected clocks, validation status, underflow, and PPLIB notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/dcn_calcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/abm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/abm.h

## Purpose

`abm.h` defines the Ambient Backlight Management hardware/firmware abstraction. It provides callbacks for ABM initialization, level control, pipe binding, PWM backlight programming, pause, configuration loading, and save/restore.

## Important APIs, Types, And Functions

`struct abm` stores context, vtable, and whether DMCU is running. `struct abm_funcs` includes `abm_init`, `set_abm_level`, `set_abm_immediate_disable`, `set_pipe`, `set_backlight_level_pwm`, `get_current_backlight`, `get_target_backlight`, `init_abm_config`, `set_abm_pause`, `save_restore`, and `set_pipe_ex`.

## Control Flow

Display code initializes ABM with current backlight/user level, assigns an OTG/controller and panel instance, loads optional firmware/config data, then changes ABM level or PWM ramp on user/power events. Disable and pause paths stop ABM effects immediately or temporarily for panel/pipe transitions.

## State And Persistence Behavior

The ABM object persists in the resource pool or per-pipe ABM arrays. Firmware/hardware holds current and target backlight state; save/restore preserves panel-specific ABM data through transitions. No on-disk persistence exists.

## Dependencies And Integration Points

It includes `dm_services_types.h` and integrates with HWSS backlight/ABM callbacks, DMCU/DMUB firmware, panel control, eDP paths, and stream resources in `core_types.h`.

## Risks And Edge Cases

Panel instance, OTG/controller ID, and power-sequence instance must match the active stream. ABM calls may depend on DMCU/DMUB firmware running. PWM values use U16.16 fixed-point semantics where 1.0 is max backlight. Save/restore data is opaque and implementation-specific.

## Test Signals

Tests should cover ABM init, level changes, immediate disable, pause/resume, backlight PWM ramps, pipe rebinding, suspend/resume save/restore, and firmware-not-running fallbacks. Visible backlight jumps or stale dimming are key runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/abm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/audio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/audio.h

## Purpose

`audio.h` defines the display audio endpoint abstraction for HDMI/DP audio programming through the Azalia/audio hardware block.

## Important APIs, Types, And Functions

`struct audio_funcs` provides `endpoint_valid`, `hw_init`, `az_enable`, `az_disable`, `az_configure`, `az_disable_hbr_audio`, `wall_dto_setup`, and `destroy`. `struct audio` stores the vtable, DC context, hardware instance, and enabled state.

## Control Flow

Resource code assigns an audio object to a stream. HWSS/link programming initializes and enables Azalia audio, configures it from signal type, CRTC timing, audio info, and DP link info, programs wall DTO using PLL info, disables HBR audio when needed, and disables/destroys the endpoint on teardown.

## State And Persistence Behavior

The audio object persists in the resource pool and tracks whether it is enabled. Hardware retains Azalia and DTO programming until changed or disabled. No disk persistence exists.

## Dependencies And Integration Points

It includes `audio_types.h`. It integrates with stream resources, link encoders, clock/PLL programming, infoframe/audio packet setup, and HWSS `enable_audio_stream`/`disable_audio_stream`.

## Risks And Edge Cases

Audio configuration depends on matching signal type, timing, PLL, and DP link rate/lane data. Endpoint validation must prevent programming unavailable hardware. HBR disable and wall DTO setup are timing-sensitive. `enabled` can become stale if hardware reset occurs outside the audio object.

## Test Signals

Tests should cover HDMI, DP, eDP/no-audio, HBR/non-HBR, link-rate changes, mode changes with audio active, suspend/resume, and endpoint destruction. Runtime signals include audio presence, sample-rate correctness, no underruns/pops, and valid infoframes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/audio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/aux_engine.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/aux_engine.h

## Purpose

`aux_engine.h` defines the AUX/I2C transaction engine abstraction used for DPCD and DDC communication. It models transaction payloads/status, engine types, AUX configuration, read/write command retry context, and engine callbacks.

## Important APIs, Types, And Functions

Important enums are transaction operation, address space, status, engine type, and default I2C speeds. `i2caux_transaction_payload/request`, `aux_config`, `aux_engine`, `read_command_context`, and `write_command_context` carry transaction state. `aux_engine_funcs` includes timeout configuration, acquire/release, configure, channel request/reply submission, reply readback, status query, availability check, high-level request submission, and destruction.

## Control Flow

Clients acquire an engine for a DDC object, configure AUX behavior, submit read/write requests to I2C or DPCD address spaces, process hardware replies, retry timeout/defer/invalid-reply cases through command contexts, then release the engine. Middle-of-transaction handling supports multi-part I2C-over-AUX sequences.

## State And Persistence Behavior

`aux_engine` persists as an AUX resource with instance, DDC binding, context, delay, retry limits, and acquire-reset behavior. Read/write contexts persist only for a transaction and record retry counters, request/reply packets, returned byte, completion, and success flags. Hardware state includes channel ownership and pending AUX transactions.

## Dependencies And Integration Points

It includes `dc_ddc_types.h`. It integrates with DDC services, link detection, EDID reads, DPCD reads/writes, link training, PSR/replay, firmware communication over AUX, and HPD-low policy.

## Risks And Edge Cases

AUX is retry-heavy and failure modes must be distinguished: busy, timeout, protocol error, NACK, incomplete, invalid operation, buffer overflow, and HPD disconnect. Incorrect `middle_of_transaction` or MOT handling can break I2C-over-AUX. Buffer length must stay within AUX limits. Acquiring without release can block link operations.

## Test Signals

Tests should cover EDID reads, DPCD reads/writes, HPD disconnect during AUX, defer storms, NACK, timeouts, channel busy, HPD-low AUX policy, and multi-part I2C transactions. Link training and hotplug reliability are practical integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/aux_engine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr.h

## Purpose

`clk_mgr.h` defines the public Display Core clock-manager abstraction. It owns display clock state, DPM clock-limit/watermark tables, SMU/PMFW interactions, low-power transitions, register dump interfaces, and clock update policy.

## Important APIs, Types, And Functions

Important constants include watermark set IDs and minimum DISPCLK/DPPCLK. Types include ASIC-specific clock register snapshots, `enum clk_type`, `clk_limit_table_entry`, `clk_limit_table`, watermark range structs, `clk_state_registers_and_bypass`, `wm_table`, `clk_bw_params`, `clk_mgr_funcs`, and `clk_mgr`. Public constructors/helpers are `dc_clk_mgr_create`, `dc_destroy_clk_mgr`, `clk_mgr_exit_optimized_pwr_state`, and `clk_mgr_optimize_pwr_state`.

## Control Flow

Validation populates required clocks and watermark ranges. Commit code calls `update_clocks(clk_mgr, context, safe_to_lower)`: with `safe_to_lower == false`, implementations raise clocks needed for safety; with true, they lower clocks after programming is safe. Clock manager functions query DP/DTB refs, set low-power state, dump registers, notify watermark ranges, respond to link-rate changes, and set hard min/max memory clocks through SMU.

## State And Persistence Behavior

`clk_mgr` persists on the DC instance and stores current `dc_clocks`, DP reference clocks, dentist VCO, boot register snapshot, bandwidth params, SMU watermark ranges, and policy flags. Hardware/firmware persistence includes programmed clocks, DPM bounds, PMFW watermark ranges, and low-power state.

## Dependencies And Integration Points

It includes `dc.h` and `dm_pp_smu.h`. It integrates with resource validation, DML/DML2 bandwidth output, PPLIB/SMU, DCCG, clock sources, link-rate changes, idle power optimization, and HWSS clock callbacks.

## Risks And Edge Cases

Clock lowering must be delayed until safe or underflow can occur. Watermark set IDs and latency fields must match PMFW contracts. Units mix kHz, MHz, MT/s, and microseconds. Missing SMU handling must use fallback paths. DC mode softmax and hard min/max memory clock controls can affect system power/performance outside display.

## Test Signals

Tests should cover clock raising/lowering order, SMU-present/absent paths, watermark notification, link-rate changes, DC mode, low-power entry/exit, register dumps, hard min/max memclk, and DPM table parsing. Underflow, clock readback mismatch, and PMFW errors are core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr_internal.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr_internal.h

## Purpose

`clk_mgr_internal.h` defines private clock-manager register macros, internal structures, and helper predicates. It maps ASIC-specific clock registers/fields, stores SMU and DFS-bypass state, and provides low-level helpers used by clock-manager implementations.

## Important APIs, Types, And Functions

Important macros include `TO_CLK_MGR_INTERNAL`, `CLK_SRI`, register-list macros for DCE/DCN generations, mask/shift-list macros, and field-list macros. Types include `clk_mgr_registers`, `clk_mgr_shift`, `clk_mgr_mask`, `enum clock_type`, `state_dependent_clocks`, `clk_mgr_internal`, and `clk_mgr_internal_funcs`. Inline helpers are `should_set_clock`, `should_update_pstate_support`, `khz_to_mhz_ceil`, and `khz_to_mhz_floor`. External helpers count active displays and planes.

## Control Flow

ASIC implementations instantiate register/mask/shift tables through the macros, cast the public manager to `clk_mgr_internal`, and use `should_set_clock` to decide whether to raise or lower clocks in each commit phase. Internal function pointers set DISPCLK/DPREFCLK. Helper counters examine `dc_state` when deriving clock requirements or power policy.

## State And Persistence Behavior

`clk_mgr_internal` extends `clk_mgr` with SMU version, SMU callbacks, DCCG pointer, register tables, max clocks by state, DFS-bypass status, spread-spectrum metadata, xGMI state, current clock states, PHY clock request table, watermark table address, DPM/PME flags, and SMU presence. This state persists for the DC instance.

## Dependencies And Integration Points

It includes the public clock manager, `dc.h`, and `resource.h` for memory type definitions. It integrates tightly with ASIC register headers, SMU/PPLIB, DCCG, link PHY clock requests, DPM tables, and DC logging.

## Risks And Edge Cases

Register-list macros are generation-specific and easy to desynchronize from hardware headers. `should_set_clock` encodes a two-phase safety policy; misuse can lower clocks early. Spread-spectrum and xGMI handling affects DPREFCLK and audio/display clocks. The internal struct is not ABI-stable and should remain private to clock-manager implementations.

## Test Signals

Builds catch missing register symbols and field names for each ASIC. Runtime tests should cover all supported clock-manager generations, DFS bypass, DPREFCLK spread-spectrum, active display/plane counts, safe-to-lower sequencing, PHY clock request updates, and DPM/PMFW interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/clk_mgr_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/cursor_reg_cache.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/cursor_reg_cache.h

## Purpose

`cursor_reg_cache.h` defines packed software mirrors for HUBP and DPP cursor registers. These caches support cursor position/attribute programming and cursor offload paths without repeatedly reconstructing register bitfields.

## Important APIs, Types, And Functions

Important types include `reg_cursor_control_cfg`, `cursor_position_cache_hubp`, `cursor_attribute_cache_hubp`, `cursor_rect`, `reg_cur0_control_cfg`, `cursor_position_cache_dpp`, `cursor_attribute_cache_dpp`, and `cursor_attributes_cfg`. Bitfields cover enable flags, magnification, mode, pitch, lines per chunk, position, hotspot, destination offsets, surface addresses, size, settings, expansion mode, ROM enable, and FP scale/bias.

## Control Flow

HUBP and DPP cursor functions update cache structures alongside hardware programming. Offload/update paths can compare or reuse cached control, position, hotspot, size, address, and scale/bias values while coordinating HUBP memory fetch and DPP composition state.

## State And Persistence Behavior

The caches are embedded in `struct hubp` and `struct dpp`, persisting for the hardware object lifetime. They are software mirrors only; hardware persistence occurs through later register writes.

## Dependencies And Integration Points

The header is included by `hubp.h` and `dpp.h`. It integrates with cursor attribute/position APIs, cursor offload, HUBP surface address programming, DPP cursor matrix/scale programming, and HWSS cursor update functions.

## Risks And Edge Cases

Bitfield layout must match register definitions and compiler assumptions. Cached values can become stale after hardware reset, power gating, or direct register writes outside the cache path. Width-limited fields such as 13-bit destination offset and 16-bit position/size require caller validation.

## Test Signals

Tests should cover cursor enable/disable, movement, hotspot changes, large coordinates, pitch/line-per-chunk modes, FP scale/bias programming, offload abort/commit, power-gate resume, and hardware readback consistency. Visible cursor corruption or lag indicates cache/register mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/cursor_reg_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dccg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dccg.h

## Purpose

`dccg.h` defines the Display Clock Generator abstraction. DCCG controls DPP DTOs, display/DP/audio/DSC/DTB clocks, PHY symbol clocks, pixel-rate dividers, clock gating, root-clock control, and register-state readback.

## Important APIs, Types, And Functions

Key enums include PHYD32 clock source, PHYSYMCLK source, stream clock source, DISPCLK change mode, and pixel-rate divider. Key structs include `dp_dto_params`, `dcn_dccg_reg_state`, `dccg`, `dtbclk_dto_params`, and `dccg_funcs`. The vtable covers DPP DTO update, DCCG ref frequency, FIFO error override, OTG add/drop pixel, init, refclk setup, clock gating, memory low power, HPO DP stream/symclk setup, PHY symclk, DTB/audio DTO, DISPCLK change mode, DSC clock enable/disable, pixel-rate dividers, DIO FIFO resync, DP DTO, DTB source selection, DSC DTO/ref clocks, root gate control, register-state readback, and global fine-grain clock gating.

## Control Flow

HWSS and clock code program DCCG when pipes, links, clocks, DSC, or HPO resources change. DPP clocks are updated per DPP instance. DP/HDMI stream clocks and DTB/audio DTOs are configured from timing/link parameters. DSC clock paths are enabled and referenced before DSC use. Pixel-rate dividers are set for ODM/encoding policies and can be read back.

## State And Persistence Behavior

`struct dccg` persists in the resource pool, tracking context, vtable, per-pipe DPP clock requests, reference DPP clock, and clock-gated state. Hardware retains DCCG register programming until reprogrammed or reset. `dcn_dccg_reg_state` is a diagnostic snapshot.

## Dependencies And Integration Points

It includes DC and shared HW types. It integrates with clock manager, HWSS, timing generators, link encoders, HPO DP encoders, DSC, audio, PHY programming, HUBP/DPP setup, and debug logging.

## Risks And Edge Cases

Clock source selections must match signal type, link encoding, PHY instance, and OTG instance. DTO modulo/phase values are unit-sensitive. Incorrect pixel-rate dividers break timing. Clock gating/root-gate controls can disable active hardware. DSC clock setup must align with slice count and instance.

## Test Signals

Tests should cover DP/HDMI/eDP/HPO link clocks, DSC enable/disable, ODM pixel-rate dividers, audio DTO, DTB clock, DPP clock changes, low-power clock gating, FIFO resync, and register readback. Link training failures, audio drift, blank displays, and underflow are practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dccg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dchubbub.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dchubbub.h

## Purpose

`dchubbub.h` defines the common DCHUBBUB abstraction, the DCN data-fabric request/return and memory-arbitration block shared by pipes. It handles VM context, DCC capability, watermarks, self-refresh/p-state controls, DET/compbuf allocation, MALL, arbiter programming, and performance monitoring.

## Important APIs, Types, And Functions

Important types include DCC control/segment order enums, `dcn_hubbub_wm_set`, `dcn_hubbub_wm`, page-table depth/block-size enums, physical/virtual address configs, `hubbub_addr_config`, state/reg snapshots, latency/urgent params, nested perfmon/qos vtables, `hubbub_funcs`, and `hubbub`. Operations include DCHUB init/update, VM setup, DCC cap/support queries, watermark read/program/init/propagation, self-refresh and p-state controls, DET/compbuf programming, CRB/MALL helpers, arbiter programming, and performance/QoS measurement controls.

## Control Flow

During init, DC programs physical/virtual apertures and DCHUB context. Validation produces watermarks, DET sizes, compbuf sizes, mcache/arbiter data, and DCC decisions. Commit code programs watermarks with safe-to-lower semantics, applies DET/compbuf changes, controls self-refresh/p-state during transitions, and optionally reads performance counters for memory QoS.

## State And Persistence Behavior

`hubbub` persists in the resource pool and stores context plus RIOMMU-active state. Hardware persists VM tables, watermarks, DET/compbuf segmentation, DCHUB arbiter settings, self-refresh/p-state controls, and performance counters. State snapshots expose fault/status and register state for diagnostics.

## Dependencies And Integration Points

It includes DC hardware types and integrates with DML/DML2 bandwidth output, HUBP memory fetch, clock manager watermarks, VM/GART aperture setup, MALL/SubVP, DCC support checks, and HWSS p-state/self-refresh flows.

## Risks And Edge Cases

Watermark lowering must be safe or underflows can occur. VM aperture and default fault addresses are security/reliability-sensitive. DCC support depends on swizzle, plane pitch, pixel format, and bytes per element. DET/compbuf segment allocation must match active pipes and compression needs. Performance counters require correct refclk conversion.

## Test Signals

Tests should cover VM faults, DCC capability by format/swizzle, watermark sets, self-refresh/p-state transitions, DET/compbuf resizing, MALL use, arbiter programming, and perfmon/QoS readings. Signals include underflow, VM fault status, watermark readback, DET config errors, and measured memory latency/bandwidth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dchubbub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dio.h

## Purpose

`dio.h` defines a small Display I/O abstraction for memory power control. It currently exposes an object and vtable to control I2C light-sleep behavior in DIO memory.

## Important APIs, Types, And Functions

`struct dio_funcs` contains `mem_pwr_ctrl(struct dio *dio, bool enable_i2c_light_sleep)`. `struct dio` stores the vtable and DC context.

## Control Flow

Callers invoke `mem_pwr_ctrl` when display I/O memory power policy changes, typically during init, low-power entry/exit, or link/DDC-related transitions.

## State And Persistence Behavior

`dio` persists in the resource pool. Hardware retains the selected memory power state. The header stores no additional state.

## Dependencies And Integration Points

It includes `dc_types.h` and integrates with `resource_pool`, clock/power management, DDC/I2C/AUX paths, and HWSS or resource init code that controls DIO power.

## Risks And Edge Cases

Enabling I2C light sleep while DDC/AUX-like operations need hardware access could cause communication failures. Unsupported ASICs may have a null or minimal DIO implementation. Power sequencing must coordinate with link hotplug and HPD handling.

## Test Signals

Tests should cover display init, suspend/resume, DDC reads with light sleep enabled/disabled, hotplug, and low-power transitions. EDID read failures and link-detection instability are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dmcu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dmcu.h

## Purpose

`dmcu.h` defines the Display Microcontroller Unit abstraction used for firmware-managed display features such as PSR, ABM-related firmware state, EDID/VSDB messaging, PHY locks, and optional secure-display CRC window forwarding.

## Important APIs, Types, And Functions

Important types include `enum dmcu_state`, `struct dmcu_version`, `struct dmcu`, and `struct dmcu_funcs`. Operations include `dmcu_init`, `load_iram`, PSR enable/setup/state/wait-loop accessors, initialization check, PHY lock/unlock, EDID CEA send/ack, AMD VSDB receive, and secure-display CRC window controls when configured.

## Control Flow

Firmware load/init moves the DMCU from unloaded or loaded-uninitialized to running. PSR setup programs link/context data, then enable/disable and state queries control panel self refresh. EDID/VSDB helper calls exchange data through firmware. PHY lock/unlock gates sensitive link/PHY access.

## State And Persistence Behavior

`dmcu` persists as a resource object with context, vtable, state, firmware version, cached wait-loop number, PSP version, and auto-load flag. Firmware state persists in DMCU memory/hardware until reset or reloaded. There is no disk persistence.

## Dependencies And Integration Points

It includes service types and forward-referenced DC link/PSR/rect/mux types. It integrates with ABM, PSR, eDP/panel features, PSP firmware loading, secure display, and HWSS/panel power sequencing.

## Risks And Edge Cases

The state machine requires correct transition checks: some init commands are valid only when firmware is loaded but uninitialized. Firmware version compatibility affects PSR/ABM commands. PHY locks must be released. Optional secure-display callbacks depend on kernel config and mux mapping validity.

## Test Signals

Tests should cover firmware load/init, auto-load, PSR setup/enable/disable/state transitions, wait-loop persistence, EDID/VSDB messaging, PHY lock/unlock error paths, suspend/resume, and secure-display CRC forwarding. Firmware command timeouts and PSR entry/exit failures are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dmcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dpp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dpp.h

## Purpose

`dpp.h` defines the Display Pipe and Plane processing abstraction for DCN. DPP performs per-plane conversion, cursor composition, scaling, color management, LUT/3D LUT programming, gamut remap, HDR multiplier, alpha/keying, histogram, and DPP clock control.

## Important APIs, Types, And Functions

Important types include `defer_reg_writes`, `dpp`, static `dpp_input_csc_matrix`, `dpp_grph_csc_adjustment`, `cnv_color_keyer_params`, `cnv_alpha_2bit_lut`, `dcn_dpp_state`, `dcn_dpp_reg_state`, `CM_bias_params`, and `dpp_funcs`. The vtable covers GAMCOR/pre-degamma/dealpha/bias, state readback, reset, scaler setup, pixel storage depth, optimal taps, gamut remap, CSC default/adjustment, regamma/degamma LUTs, setup/full bypass, cursor attributes/position/matrix/disable, HDR multiplier, DPP clock control, deferred update, blend/shaper/3D LUTs, alpha keyer, histogram control/read, and gamut readback.

## Control Flow

Plane programming sets DPP setup from pixel format, expansion, input CSC, color space, and alpha LUT; then scaler, pixel depth, color pipeline, cursor state, and optional LUTs are programmed. Deferred updates can batch disabling color blocks. Readback functions support debug and color-state logging. Cursor updates use both DPP and HUBP programming.

## State And Persistence Behavior

`dpp` persists per DPP instance in the resource pool. It caches regamma/degamma/shaper params, cursor attributes, deferred-register flags, color-management bypass mode, cursor-offload flag, and cursor register mirrors. Hardware persists DPP registers and LUT RAM until reprogrammed or reset.

## Dependencies And Integration Points

It includes `transform.h` and cursor register cache. It integrates with `plane_resource`, HWSS plane enable/update paths, color management, SPL/scaler data, OPP/MPC blending, HUBP cursor fetch, and DML scaler/timing outputs.

## Risks And Edge Cases

Color pipeline ordering is complex; disabling LUTs or bypassing CM in the wrong order can cause visible color shifts. Static CSC matrices must match hardware coefficient format. Cursor state is split across DPP and HUBP. LUT bank selection, deferred writes, and 3D LUT programming require careful synchronization. Scaler tap selection must obey DPP caps.

## Test Signals

Tests should cover RGB/YUV formats, scaling ratios/taps, rotations via upstream HUBP, degamma/regamma/shaper/blend/3D LUTs, gamut remap, HDR multiplier, cursor movement/offload, alpha keying, histogram, and reset/power transitions. Visual color errors, cursor corruption, and scaler artifacts are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dwb.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dwb.h

## Purpose

`dwb.h` defines the Display Writeback Controller abstraction. DWB captures a display source, optionally scales/converts it, and writes frames through MCIF writeback buffers for capture, composition, or remote/display features.

## Important APIs, Types, And Functions

Important enums cover software version, source selection, pipe IDs, frame capture enable, scaler filter type, boundary mode, output CSC mode, output gamma LUT mode, color volume, and color space. Key structs include HDR metadata, EFC display settings, warmup params, caps, `dwbc`, and `dwbc_funcs`. Operations include capability query, enable/disable/update, enabled/status query, frame capture enable, scaler/stereo/new-content/warmup programming, MCIF buffer line readback, optional output CSC/OGAM, input transfer function, DRR timestamp, and DWB status.

## Control Flow

Resource/HWSS code assigns a DWB pipe and MCIF buffer, configures source OTG or legacy source, programs scaler/color/stereo/warmup/EFC state from `dc_dwb_params`, enables frame capture, and updates or disables the block on stream changes. MCIF line readback and timestamps support synchronization/debug.

## State And Persistence Behavior

`dwbc` persists per writeback block and stores context, instance, MCIF pointer, enable/status fields, selected input source, output black flag, transfer function, output color space, EFC/DRC flags, source plane/OTG metadata, mask ID, MVC config, and last params. Hardware persists DWB and MCIF programming until disabled or reset.

## Dependencies And Integration Points

It includes DAL and DC hardware types and forward-declares `mcif_wb`. It integrates with `resource_pool`, `dc_writeback_info`, HWSS writeback callbacks, MCIF arbitration/buffer programming, DML writeback bandwidth, and stream/OTG resources.

## Risks And Edge Cases

DWB capabilities vary by version and ASIC. Source selection differs between legacy DCE and DCN values. Output color and transfer functions are conditionally compiled for FP support. MCIF buffer overruns, scaler bounds, HDR/EFC metadata, and DRR timestamps require synchronized programming. Cached `params` can become stale after stream topology changes.

## Test Signals

Tests should cover caps, enable/update/disable, each source type, scaler formats, stereo, output black, warmup pattern, OGAM/CSC paths, MCIF buffer overrun readback, DRR timestamp, and writeback under mode changes. Captured-frame correctness and no overruns are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/dwb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/gpio.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/gpio.h

## Purpose

`gpio.h` defines the generic GPIO object wrapper used by Display Core for DDC, HPD, generic, sync, GSL, and other display-related pins. The active function table is disabled in this header, leaving the shared object shape and hardware-container union.

## Important APIs, Types, And Functions

`union gpio_hw_container` can point to DDC, generic, or HPD hardware pin wrappers. `struct gpio` stores the GPIO service, hardware pin, ID, enable/index value, hardware container, mode, and firmware-defined output state. A historical `gpio_funcs` block is present under `#if 0`, documenting creation and offset/ID translation operations.

## Control Flow

GPIO service code creates and manages typed hardware pin objects, then uses `struct gpio` to associate a logical GPIO ID and mode with the underlying pin. VBIOS-sourced GPIOs may carry an initial output state.

## State And Persistence Behavior

`gpio` persists while the service owns the pin. It tracks current logical mode and output state metadata, while hardware pin state persists in registers. No disk persistence exists.

## Dependencies And Integration Points

It includes `gpio_types.h` and integrates with GPIO service, DDC/I2C, HPD detection, generic panel/link controls, VBIOS GPIO translation, and AUX/DDC services.

## Risks And Edge Cases

The union requires consumers to know which hardware wrapper is active. Mode and output state can desynchronize from hardware after reset or external firmware actions. The disabled function table indicates creation/translation logic lives elsewhere; duplication can drift.

## Test Signals

Tests should cover DDC clock/data pins, HPD pins, generic GPIO mode transitions, VBIOS-defined output states, suspend/resume, and hotplug. EDID/HPD failures are the practical integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/gpio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/hubp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/hubp.h

## Purpose

`hubp.h` defines the per-pipe HUBP abstraction, the DCHUB front-end block that fetches plane memory, handles tiling/DCC/VM, cursor fetch, viewport programming, flip/address updates, DML RQ/DLG/TTU registers, MALL/SubVP, and 3D LUT fetch logic.

## Important APIs, Types, And Functions

Important enums include cursor pitch, cursor lines per chunk, HUBP independent block size, and 3D LUT fetch modes/formats/addressing/width/crossbar. `struct hubp` stores vtable, context, request address, instance, runtime OPP/MPCC IDs, cursor state/cache, offload flag, power-gated state, and MALL cursor flag. `surface_flip_registers` mirrors flip/address registers. `hubp_funcs` covers setup/setup2, interdependent setup, DCC control, reset, viewport, flip/address, PTE/VM, aperture/context0, surface config, flip pending, blanking, cursor attributes/position, disconnect, clock/VTG, state/reg readback, underflow, disable/init, DM data, triple buffering, GSL flip control, DML output validation, unbounded requesting, soft reset, interrupts, p-state disallow, MALL/SubVP, surface update lock, extended blank, pipe-read-start wait, mcache, 3D LUT fetch, tiling clear, current read line, and DET config error.

## Control Flow

Plane enable programs surface config, VM/PTE, viewport, RQ/DLG/TTU/DML registers, VTG selection, cursor state, and surface addresses. Flip paths call `hubp_program_surface_flip_and_addr` and then poll pending status or use interrupts. Updates may lock surface registers, adjust MALL/SubVP, reprogram mcache, or validate DML outputs. Disable paths blank, disconnect, reset, or power gate HUBP.

## State And Persistence Behavior

`hubp` persists per hardware pipe and caches request address, runtime routing IDs, cursor attributes/position, cursor register mirrors, cursor rectangle, MALL cursor selection, and power-gated state. Hardware persists memory-fetch, VM, DCC, cursor, flip, blank, and DLG/TTU registers until changed.

## Dependencies And Integration Points

It includes `mem_input.h`, cursor cache, and DML2 DCHUB register/types. It integrates with `pipe_ctx`, HUBBUB, DPP, MPC/OPP, timing generator, DML/DML2 bandwidth output, VM setup, cursor handling, MALL/SubVP, DM data/infoframes, and HWSS block sequences.

## Risks And Edge Cases

Flip/address programming is synchronization-sensitive and must handle immediate vs vblank flips, stereo, TMZ, VMID, meta surfaces, and chroma planes. VM aperture/context and DCC settings must match surface tiling. DML register validation is important because invalid RQ/DLG/TTU values cause underflow. Cursor state is split with DPP. Power-gated state and cached registers must be refreshed after reset.

## Test Signals

Tests should cover surface flips, DCC on/off, VM/PTE, rotations/tiling, viewport changes, cursor movement/offload, triple buffering, GSL flip control, unbounded requesting, SubVP/MALL, mcache, 3D LUT fetch, underflow clear/status, blank/disconnect/reset, and DET config errors. Signals include flip-pending timeouts, underflows, VM faults, current read line, and visual corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/hubp.h -->
