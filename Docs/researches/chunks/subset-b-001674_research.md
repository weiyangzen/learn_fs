# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 44391-46846

## Scope

This chunk is a generated AMD DCN 2.1.0 register shift/mask header slice. It exports preprocessor constants only: `REGISTER__FIELD__SHIFT` values and `REGISTER__FIELD_MASK` values used by AMDGPU display register helpers to pack and extract MMIO fields. There are no C functions, structs, enums, or local algorithms in this range.

The slice contains 2,139 `#define` entries: 1,069 shift constants and 1,070 mask constants across 267 register names. It starts at the tail of `DSCCIF0_DSCCIF_CONFIG1` with `PIC_WIDTH` and `PIC_HEIGHT` masks, covers complete generated field sets for DSC/DSCC instances 0 through 3, includes most of instance 4, and ends inside `DSCC4_DSCC_B_CR_SQUARED_ERROR_UPPER`. It also includes DC perfmon instances 19 through 22.

Major hardware domains represented here are:

- `DSC_TOP1` through `DSC_TOP4` top-level Display Stream Compression clock/debug controls.
- `DSCCIF0` through `DSCCIF4` DSC input interface fields for underflow recovery/status/interrupt enable, pixel format, bits per component, picture width, and picture height.
- `DSCC0` through `DSCC4` DSC compressor core fields for slice geometry, initial chunk handling, rate-control buffer model, PPS programming, interrupt/status, memory power, error counters, fullness readbacks, and debug-bus rotation.
- `DC_PERFMON19` through `DC_PERFMON22` performance counter fields for event selection, run/stop control, counter state, interrupt control/status/ack, counter values, high/low reads, and selection control.

## Purpose

The purpose of this chunk is to map DCN 2.1 display-compression and performance-monitor register fields to exact bit positions. Runtime display code uses these generated constants through register-table macros instead of hard-coding numeric shifts and masks.

The DSC portions support programming VESA Display Stream Compression encoder state. The field families map the input interface and compressor core configuration needed for compressed DisplayPort/eDP output: input pixel format, color depth, picture and slice dimensions, slice counts, bits per pixel, chunk size, initial transmit/decode delays, scale intervals, BPG offsets, initial/final offsets, flatness QP bounds, rate-control thresholds, all 15 rate-control range parameter sets, and compressor memory-power controls.

The perfmon portions expose hardware diagnostics around the same DC display fabric. They are repeated generated instances, each with counter event selectors, clear/load/run bits, active/counter state, interrupt threshold/status/ack fields, and high/low counter data.

## Important API Surface

The public surface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important DSC top and input-interface constants include:

- `DSC_TOP<n>_DSC_TOP_CONTROL__DSC_CLOCK_EN`, `DSC_DISPCLK_R_GATE_DIS`, and `DSC_DSCCLK_R_GATE_DIS` for clock enable and clock-gating behavior.
- `DSC_TOP<n>_DSC_DEBUG_CONTROL__DSC_DBG_EN` and `DSC_TEST_CLOCK_MUX_SEL` for debug routing.
- `DSCCIF<n>_DSCCIF_CONFIG0__INPUT_INTERFACE_UNDERFLOW_RECOVERY_EN`, `INPUT_INTERFACE_UNDERFLOW_OCCURRED_INT_EN`, `INPUT_INTERFACE_UNDERFLOW_OCCURRED_STATUS`, `INPUT_PIXEL_FORMAT`, and `BITS_PER_COMPONENT`.
- `DSCCIF<n>_DSCCIF_CONFIG1__PIC_WIDTH` and `PIC_HEIGHT`.

Important DSCC compressor core constants include:

- `DSCC<n>_DSCC_CONFIG0__ICH_RESET_AT_END_OF_LINE`, `NUMBER_OF_SLICES_PER_LINE`, `ALTERNATE_ICH_ENCODING_EN`, and `NUMBER_OF_SLICES_IN_VERTICAL_DIRECTION`.
- `DSCC<n>_DSCC_CONFIG1__DSCC_RATE_CONTROL_BUFFER_MODEL_SIZE` and `DSCC_DISABLE_ICH`.
- `DSCC<n>_DSCC_STATUS__DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING`.
- `DSCC<n>_DSCC_INTERRUPT_CONTROL_STATUS__DSCC_RATE_BUFFER[0-3]_{OVERFLOW,UNDERFLOW}_OCCURRED` and matching interrupt-enable fields, plus `DSCC_RATE_CONTROL_BUFFER_MODEL[0-3]_OVERFLOW_OCCURRED` and interrupt-enable fields.
- `DSCC<n>_DSCC_PPS_CONFIG0` through `DSCC_PPS_CONFIG22`, which carry the generated register form of the DSC picture parameter set and rate-control parameters.
- `DSCC<n>_DSCC_MEM_POWER_CONTROL__DSCC_DEFAULT_MEM_LOW_POWER_STATE`, `DSCC_MEM_PWR_FORCE`, `DSCC_MEM_PWR_DIS`, `DSCC_MEM_PWR_STATE`, and native-422 memory-power fields.
- Error and diagnostic readback fields such as `DSCC_R_Y_SQUARED_ERROR_*`, `DSCC_G_CB_SQUARED_ERROR_*`, `DSCC_B_CR_SQUARED_ERROR_*`, `DSCC_MAX_ABS_ERROR*`, rate-buffer maximum-fullness fields, rate-control-buffer maximum-fullness fields, and `DSCC_TEST_DEBUG_BUS_ROTATE`.

Important perfmon constants include:

- `DC_PERFMON19` through `DC_PERFMON22` `PERFCOUNTER_CNTL`, `PERFCOUNTER_CNTL2`, `PERFCOUNTER_STATE`, `PERFMON_CNTL`, `PERFMON_CNTL2`, `PERFMON_CVALUE_INT_MISC`, `PERFMON_CVALUE_LOW`, `PERFMON_HI`, and `PERFMON_LOW` fields.

The main consumer pattern is in `display/dc/dsc/dcn20/dcn20_dsc.h`, where `DSC_REG_LIST_DCN20(id)` builds per-instance DSC register tables and `DSC_REG_LIST_SH_MASK_DCN20(__SHIFT)` / `_MASK` build `dcn20_dsc_shift` and `dcn20_dsc_mask` tables. `display/dc/resource/dcn21/dcn21_resource.c` instantiates those tables for DCN 2.1 DSC instances and passes them to `dsc2_construct`.

## Control Flow

There is no local control flow in this header. Runtime behavior is supplied by AMD display code that pairs these field constants with offsets from `dcn_2_1_0_offset.h`.

A typical DSC flow is:

1. DCN21 resource construction includes `dcn_2_1_0_offset.h` and this shift/mask header.
2. `dcn21_resource.c` expands `DSC_REG_LIST_DCN20(id)` into `dcn20_dsc_registers` for DSC instances 0 through 5 and expands `DSC_REG_LIST_SH_MASK_DCN20` into common shift and mask tables.
3. `dsc2_construct` stores those register, shift, and mask tables in each `dcn20_dsc` object.
4. `dsc2_validate_stream` and `dsc_prepare_config` compute valid DSC register values from `dsc_config`, DRM DSC PPS data, rate-control parameters, slice counts, pixel format, and ODM requirements.
5. `dsc_write_to_registers` uses `REG_SET`, `REG_SET_2`, `REG_SET_3`, `REG_SET_4`, `REG_SET_5`, and similar helpers to program `DSCCIF_CONFIG*`, `DSCC_CONFIG*`, `DSCC_INTERRUPT_CONTROL_STATUS`, and the full `DSCC_PPS_CONFIG0-22` set.
6. `dsc2_enable`, `dsc2_disable`, and `dsc2_disconnect` toggle `DSC_TOP_CONTROL.DSC_CLOCK_EN` and DSCRM forwarding state, while `dsc2_read_state` and `dsc2_read_reg_state` read back selected DSC fields for logging and diagnostics.

Perfmon control flow is similarly external: diagnostic or debug code selects events, clears or loads counters, enables counting, reads high/low counter values, and acknowledges counter interrupts using the generated perfmon fields.

## State And Persistence Behavior

The file stores no software state. It describes hardware state in memory-mapped DCN display registers, which persists until rewritten, reset, power-gated, or changed by hardware.

State represented by this chunk includes:

- DSC top-level clock/debug state per compressor instance.
- DSCCIF input format and image-size state, including underflow recovery, sticky underflow status, and underflow interrupt enable.
- DSCC compressor slice topology, ICH reset behavior, alternate ICH encoding, and rate-control buffer-model sizing.
- The active DSC PPS register image: DSC version, PPS ID, line buffer depth, bits per component, bits per pixel, RGB/YCbCr/native mode flags, block prediction, chunk size, picture/slice dimensions, transmit/decode delays, scale intervals, line and slice BPG offsets, initial/final offsets, flatness limits, rate-control model size, target offsets, 14 buffer thresholds, and 15 QP/BPG range parameter triplets.
- Compressor status and error state: double-buffer update pending, rate-buffer overflow/underflow, RC model overflow, squared-error accumulators, maximum absolute error, maximum fullness levels, and debug-bus rotation selection.
- Compressor memory-power force/disable/default/status fields, including separate native-422 memory power fields.
- Perfmon counter configuration, run state, interrupt state, and counter value state for four generated perfmon instances.

Several fields are sticky status or interrupt bits, several are live readbacks, and several are latched programming values. The header does not encode access permissions, write-one-to-clear semantics, valid value ranges, update-lock requirements, or timing restrictions; callers must enforce those rules.

## Dependencies And Integration Points

This chunk is tightly coupled to the matching DCN 2.1 register offset header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_offset.h`. Offsets identify the MMIO registers, while this file identifies the bit fields inside those registers.

Direct integration points visible in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn21/dcn21_resource.c`, which includes this header, builds `dsc_regs`, `dsc_shift`, and `dsc_mask`, constructs DCN21 DSC objects, and creates six DSC register-table entries.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h`, whose `DSC_REG_LIST_DCN20` and `DSC_REG_LIST_SH_MASK_DCN20` macros name the fields defined here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.c`, which validates DSC streams, computes DSC PPS and rate-control parameters, writes DSCCIF/DSCC/PPS fields, toggles DSC enable state, waits for disconnect/update-pending behavior, and reads back selected DSC state.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn21.c`, which includes the same DCN 2.1 shift/mask header for DMUB common register field tables, although this specific chunk's DSC fields are not the main DMUB surface.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn21/irq_service_dcn21.c`, which also includes this header for DCN21 interrupt register field metadata.
- DRM DSC helpers and types, especially `<drm/display/drm_dsc.h>` and `<drm/display/drm_dsc_helper.h>`, plus local DSC helpers under `display/dc/dsc/` such as `dscc_types.h` and `rc_calc.h`.

The repeated generated instance layout is part of the contract. The chunk shows complete field sets for instances 0-3 and most of instance 4, while `dcn21_resource.c` expects six DSC instances. Adjacent chunks must be merged to cover the tail of `DSCC4` and all of `DSCC5`.

## Risks And Edge Cases

- A wrong shift or mask silently programs the wrong hardware bits while C still compiles. The highest-risk fields here are PPS dimensions, bits per pixel/component, slice width/height, slice count, chunk size, rate-control thresholds/ranges, native 420/422 flags, and interrupt enable/status fields.
- DSC programming is protocol-visible. Bad constants can produce corrupted compressed output, link training or stream validation failures, DP/eDP sink decode errors, black screens, underflow, or visual artifacts that only reproduce for DSC-enabled modes.
- `DSCCIF_CONFIG0` and `DSCC_PPS_CONFIG0` both carry bits-per-component style fields and use generated duplicate-field workarounds in `dcn20_dsc.h`. Misnaming or mismatching those macros can put color depth into the wrong register table field.
- The 14 buffer thresholds and 15 rate-control range entries are dense repeated fields spread across `PPS_CONFIG12-22`. Off-by-one, mask-width, or range-order mistakes can pass compile tests but break rate-control behavior under specific bpp, slice, or pixel-format combinations.
- Interrupt status and interrupt-enable fields share `DSCC_INTERRUPT_CONTROL_STATUS`. Incorrect read/modify/write handling or stale masks can miss rate-buffer overflow/underflow events, fail to enable RC model overflow interrupts, or accidentally preserve/clear sticky status.
- Instance-copy errors are easy because `DSCC0` through `DSCC4`, `DSCCIF0` through `DSCCIF4`, and `DSC_TOP1` through `DSC_TOP4` are near-duplicates. A bad instance suffix may affect only a particular display pipe, ODM configuration, or multi-monitor topology.
- Memory-power fields affect compressor SRAM availability. Incorrect `DSCC_MEM_POWER_CONTROL` masks can leave DSC memory powered down while active, block power savings, or report the wrong power state.
- Chunk boundaries are artificial. This range begins after the `DSCCIF0_DSCCIF_CONFIG1` shift definitions and ends before the complete DSCC4 diagnostic set; whole-file reconciliation must combine neighboring chunks before judging completeness.

## Test Signals

Useful validation signals for this chunk include:

- A full AMDGPU display build with DCN21 enabled, covering `dcn21_resource.c`, `dcn20_dsc.c`, DMUB DCN21 code, and DCN21 IRQ code that include `dcn_2_1_0_sh_mask.h`.
- Static generated-header checks against AMD's DCN 2.1 register database and the companion `dcn_2_1_0_offset.h`, verifying that each `__SHIFT` has the expected `_MASK`, field masks do not overlap unintentionally, and repeated DSC instances remain consistent where hardware requires consistency.
- DSC modeset tests for DisplayPort/eDP streams with DSC enabled across different bits per component, RGB/YCbCr 4:4:4, simple 4:2:2, native 4:2:2, native 4:2:0, multiple bpp values, and multiple horizontal/vertical slice counts.
- High-resolution and ODM/multi-DSC tests that exercise multiple compressor instances, especially instances 0-5 as constructed by DCN21 resource code.
- PPS pack/readback comparisons: compare the packed DRM DSC PPS and computed `dsc_reg_values` with hardware readback from `dsc2_read_state` and selected `DSCC_PPS_CONFIG*` registers.
- Underflow and overflow diagnostics that deliberately stress bandwidth or invalid timing and verify DSCCIF underflow status, DSCC rate-buffer overflow/underflow status, RC model overflow status, and corresponding interrupt-enable behavior.
- Suspend/resume, runtime power management, and DSC enable/disable/disconnect tests that verify `DSC_CLOCK_EN`, DSCRM forwarding state, `DSCC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, and DSCC memory-power status converge correctly.
- Perfmon smoke tests that select DC perf events on instances 19-22, run counters, read high/low values, and validate interrupt threshold/status/ack fields.

Regression symptoms from bad constants include DSC stream enable failures, black or corrupted display only on compressed modes, sink-side DSC decode errors, underflow/overflow interrupts, bad bpp or color-depth programming, incorrect slice/chunk sizing, stuck disconnect/update-pending waits, missing power savings, or impossible perf counter values.

## Cross-Chunk Notes

This is a chunk of a generated hardware register layout contract, not a standalone module. The final per-file report should merge it with adjacent `dcn_2_1_0_sh_mask.h` chunks to cover the complete DCN 2.1 field map, including the preceding `DSCCIF0_DSCCIF_CONFIG1` shifts, the remainder of `DSCC4`, and the complete `DSCC5` instance that DCN21 resource construction expects.
