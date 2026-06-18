# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_1_0_sh_mask.h lines 24867-27467

## Scope

This chunk is part of the generated AMD DCN 2.1.0 ASIC register shift/mask header. It covers lines 24867-27467 and exports preprocessor constants for display register fields. The slice contains 2,118 `#define` entries: 1,059 `__SHIFT` constants and 1,059 `_MASK` constants. It has no C functions, structs, enums, or executable control flow; the API is the generated macro namespace consumed by AMDGPU display register access helpers.

The chunk starts in the tail of `MPC_OUT3` output CSC coefficient fields and ends inside the beginning of the `OTG0` timing generator interrupt/status fields. Whole-file reconciliation should merge this with adjacent chunks for complete MPC and OTG coverage.

## Purpose

The purpose of this chunk is to map DCN 2.1 output/display-pipe hardware fields to exact bit positions and bit masks. Runtime display code can then use symbolic field names through register helper macros instead of literal bit constants.

Major hardware domains represented here are:

- `MPC_OUT3` output color-space-conversion coefficient registers for MPC output instance 3, including A/B coefficient banks.
- `DC_PERFMON15` and OPP-side `DC_PERFMON4` performance monitor counter control, state, count, compare-value, interrupt, run-enable, and clock fields.
- `BL1_PWM_*` and `DC_ABM1_*` backlight and ambient/backlight modulation fields, including PWM levels, ABM control, histogram/luma statistics, ACE coefficients, sample rates, histogram result bins, and master lock.
- Repeated OPP instance groups `FMT0` through `FMT5`, `DPG0` through `DPG5`, `OPPBUF0` through `OPPBUF5`, `OPP_PIPE0` through `OPP_PIPE5`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5`.
- OPP top-level memory power status/control fields and `DSCRM0` through `DSCRM5` DSC rate-control/average-rate fields.
- `ODM0` through `ODM5` OPTC input blocks for ODM segmentation, DSC mode, bytes-per-pixel, segment/slice width, input clock gating, memory selection, soft reset, underflow, and double-buffer state.
- The first `OTG0` timing generator fields for horizontal/vertical total, blanking, sync, dynamic refresh-rate vertical-total control, and vertical-total/vsync interrupt status.

## Important API Surface

The exported naming convention is:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Important families in this chunk include:

- `MPC_OUT3_CSC_C*_A/B__MPC_OCSC_*` for 16-bit packed output CSC matrix coefficients.
- `DC_PERFMON15_PERFCOUNTER_CNTL`, `DC_PERFMON15_PERFCOUNTER_CNTL2`, `DC_PERFMON15_PERFCOUNTER_STATE`, `DC_PERFMON15_PERFMON_CNTL`, and `DC_PERFMON15_PERFMON_CVALUE_INT_MISC` for selecting performance events, count modes, hardware stop/count-off conditions, active state, interrupt status/ack, and 48-bit count-value halves.
- `BL1_PWM_*` fields for ambient light level, user/target/current/final/minimum duty-cycle levels, ABM enable and gradient/scale control, sample-rate updates, and group register locking.
- `DC_ABM1_CNTL`, `DC_ABM1_IPCSC_COEFF_SEL`, `DC_ABM1_ACE_*`, `DC_ABM1_HG_*`, and `DC_ABM1_LS_*` for adaptive backlight modulation setup and histogram/luma-stat readback.
- `FMTn_FMT_CONTROL`, `FMTn_FMT_BIT_DEPTH_CONTROL`, `FMTn_FMT_CLAMP_*`, `FMTn_FMT_DITHER_RAND_*`, `FMTn_FMT_MAP420_MEMORY_CONTROL`, and `FMTn_FMT_422_CONTROL` for OPP pixel encoding, subsampling, truncation, temporal/spatial dithering, clamp limits, random seeds, 4:2:0 memory power, and 4:2:2 edge handling.
- `DPGn_DPG_CONTROL`, `DPGn_DPG_RAMP_CONTROL`, `DPGn_DPG_DIMENSIONS`, `DPGn_DPG_COLOUR_*`, and `DPGn_DPG_STATUS` for display pattern generator mode, dimensions, colors, ramp parameters, segment offset, and double-buffer status.
- `OPPBUFn_OPPBUF_CONTROL` and `OPPBUFn_OPPBUF_3D_PARAMETERS_*` for active width, display segmentation, overlap/repetition, padded pixels, stereo/3D active-space sizes, dummy data, and double-buffer pending state.
- `OPP_PIPE_CRCn_OPP_PIPE_CRC_CONTROL`, `*_MASK`, and `*_RESULT*` for OPP CRC enable/mode/source selection, one-shot pending, masks, and component results.
- `ODM*_OPTC_INPUT_GLOBAL_CONTROL`, `ODM*_OPTC_DATA_SOURCE_SELECT`, `ODM*_OPTC_DATA_FORMAT_CONTROL`, `ODM*_OPTC_BYTES_PER_PIXEL`, `ODM*_OPTC_WIDTH_CONTROL`, and `ODM*_OPTC_INPUT_CLOCK_CONTROL` for ODM input routing, DSC, segmentation, clocks, soft reset, underflow, and update-pending status.
- `OTG0_OTG_H_*`, `OTG0_OTG_V_TOTAL*`, `OTG0_OTG_V_TOTAL_CONTROL`, `OTG0_OTG_V_TOTAL_INT_STATUS`, and the start of `OTG0_OTG_VSYNC_NOM_INT_STATUS` for timing programming and dynamic refresh-rate/event interrupt handling.

These constants are normally referenced indirectly through AMD display register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SF`, `OPP_SF`, and generated field-list tables. The header must be paired with the matching DCN 2.1.0 register offset header.

## Control Flow

There is no local control flow in this generated header. Runtime behavior is imposed by callers:

- OPP constructors bind `FMT`, `DPG`, `OPPBUF`, `OPP_PIPE`, and `OPP_PIPE_CRC` offsets, masks, and shifts into per-instance register tables.
- Display pipe programming writes `FMTn` fields when setting pixel encoding, subsampling, clamp, truncation, dithering, and memory power behavior.
- Pattern generator code writes `DPGn` fields and waits on double-buffer status when producing test patterns.
- CRC capture paths program `OPP_PIPE_CRCn` control/mask fields, then read component result registers for validation or diagnostics.
- ABM/backlight code programs `BL1_PWM_*` and `DC_ABM1_*` fields and reads histogram/luma result fields to drive panel brightness decisions.
- ODM/OPTC code writes `ODM*_OPTC_*` fields for output-merger segmentation and DSC routing, while monitoring soft reset, underflow, clock, and double-buffer state.
- Timing-generator code writes `OTG0` horizontal/vertical timing and dynamic refresh-rate fields, then handles vertical-total or vsync interrupt status/ack/mask fields.
- Perfmon code programs event selection, counting modes, count-off conditions, run-enable/stop sources, and interrupt acknowledgement using the `DC_PERFMON*` fields.

Ordering, locking, and polling are external contracts. For example, callers must not update packed FMT/ODM/OTG fields mid-frame without the relevant double-buffer/update semantics, and interrupt status/ack bits must be handled with hardware-prescribed write patterns.

## State and Persistence

The file stores no software state. Its macros describe memory-mapped display hardware state that persists in GPU registers while the blocks are powered:

- MPC CSC coefficients persist as active output color conversion state.
- FMT fields persist as active output formatting, dither, clamp, subsampling, and memory-power state for each OPP instance.
- DPG and OPPBUF fields persist as test-pattern, segmentation, stereo, and output-buffer state.
- OPP CRC state persists as capture configuration and latched result values.
- BL/ABM fields persist as backlight control, image-statistics, histogram, and adaptive contrast/backlight state.
- ODM fields persist as OPTC input routing, segment width, DSC slice/bytes-per-pixel, clock, memory selection, underflow, and pending-update state.
- OTG fields persist as timing-generator configuration and sticky/event interrupt state.
- Perfmon fields persist as counter configuration, live counter values, active state, and sticky interrupt bits.

Incorrect constants can leave display hardware programmed incorrectly until a modeset, block reinitialization, power transition, or GPU reset restores known values.

## Dependencies and Integration Points

This chunk depends on the generated DCN 2.1.0 offset header and on the AMD display register-access macro framework that token-pastes register and field names into `__SHIFT` and `_MASK` symbols.

Key integration points include:

- DCN 2.1 display bring-up paths selected through the DC resource, clock manager, GPIO, and DMUB code. `dmub_dcn21.c`, DCN21 GPIO factory/translate code, and related DCN21 modules include `dcn/dcn_2_1_0_sh_mask.h`.
- OPP code in `drivers/gpu/drm/amd/display/dc/opp/`, especially DCN10/DCN20-style field lists and helpers that use `FMT0_*`, `DPG0_*`, `OPPBUF0_*`, and `OPP_PIPE_CRC0_*` symbols as the base instance and instantiate per-OPP register tables.
- ABM/backlight code such as `drivers/gpu/drm/amd/display/dc/dce/dmub_abm_lcd.c`, which writes `DC_ABM1_*` setup fields and reads/statistically consumes histogram/luma fields.
- OPTC timing and ODM code in `drivers/gpu/drm/amd/display/dc/optc/`, which uses `OTG0_*` and `ODM0_OPTC_*` masks for timing, dynamic refresh-rate, DSC, segmentation, underflow, and clock/pending status.
- Performance-monitor and diagnostic paths that consume `DC_PERFMON*` fields for event selection, counters, and interrupt management.
- Cross-generation generated headers (`dcn_2_0_*`, `dcn_3_*`, and later) with similar names but potentially different field availability, mask widths, or reserved-bit layout.

## Risks

- A wrong shift or mask silently writes the wrong hardware bit. Highest-risk fields here include interrupt ack/status bits, double-buffer pending bits, clock enable/status, soft reset, underflow clear/status, OTG timing, ODM DSC/segment routing, and FMT dither/clamp/subsampling controls.
- Instance drift is likely because `FMT`, `DPG`, `OPPBUF`, `OPP_PIPE`, `OPP_PIPE_CRC`, `DSCRM`, and `ODM` families repeat from 0 through 5. A copy/paste or generation mismatch may only break a specific pipe.
- Packed 16-bit coefficient/result fields are common in MPC, FMT clamp/seed, DPG colors, CRC results, and OTG timing. Swapping high/low fields or using the wrong half of a packed register can create visual corruption without compile-time errors.
- Status and clear/ack bits share registers with enable, mask, type, and control bits in perfmon, ODM underflow, OTG interrupts, and CRC paths. Careless read-modify-write sequences can lose events or acknowledge sticky status unexpectedly.
- Timing and segment-width masks are narrow. Overflow in OTG totals, ODM segment/slice widths, DPG dimensions, OPPBUF active width, or side-by-side stereo width can manifest only on particular modes or DSC/ODM topologies.
- ABM histogram and luma-stat result fields are readback-heavy. Wrong masks may bias adaptive backlight decisions rather than causing an obvious failure.
- Generated headers are rarely unit-tested directly; many regressions surface only through full driver builds, static register-database comparisons, or hardware display behavior.

## Test Signals

Useful validation signals for changes to this chunk are:

- AMDGPU display build coverage for DCN 2.1 and neighboring DCN20 code paths, catching missing/renamed macros in OPP, ABM, OPTC/ODM, GPIO, DMUB, and timing code.
- Static comparison against the vendor register database and the matching DCN 2.1.0 offset header, verifying every `__SHIFT` has the intended `_MASK` and that repeated instance families are consistent where hardware requires them.
- Multi-display and multi-pipe runtime tests that exercise OPP instances 0-5, including format changes, RGB/YUV subsampling, clamp/dither configuration, 4:2:0 memory power, OPPBUF segmentation, and OPP CRC readback.
- ABM/backlight tests that cover PWM level programming, ABM enable/disable, histogram/luma result reads, sample-rate updates, and lock behavior.
- ODM/DSC tests with split output, DSC enabled, varying slice/segment widths, underflow detection/clear, input clock gating, and memory selection.
- OTG timing tests covering modesets, dynamic refresh-rate vertical-total min/max/mid behavior, vsync/vtotal interrupts, and interrupt mask/ack behavior.
- Perfmon diagnostics that select events, run counters under different enable/stop modes, read low/high count values, and verify interrupt status/ack handling.

## Chunk Notes

This chunk is generated register metadata, not functional logic. Its research value is identifying which hardware surfaces are covered and where mask/shift errors would propagate: OPP formatting and diagnostics, ABM/backlight statistics, ODM/DSC routing, output timing, performance counters, and repeated per-pipe register families. The final merged file report should combine this with adjacent chunks for full `dcn_2_1_0_sh_mask.h` coverage.
