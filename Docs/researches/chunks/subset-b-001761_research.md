# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 24895-27447

## Scope And Purpose

This chunk is part of the generated DCN 3.0.2 shift/mask register header for the AMD display driver. It contains C preprocessor constants only: each hardware register field has a `__SHIFT` value and a matching `_MASK` value. Driver code uses these constants to build register field tables for typed register access helpers such as `REG_UPDATE`, `REG_GET`, `REG_READ`, and wait/update macros in the DC display stack.

The slice covers 2,127 macro definitions in the middle of the file: 1,065 shift constants and 1,062 masks. It begins with the tail field for `OPP_PIPE_CRC0_OPP_PIPE_CRC_RESULT2`, then defines repeated instance blocks for OPP/FMT/DPG/OPPBUF/OPP pipe CRC instances 1 through 4, OPP top and DSCRM blocks, a DC perfmon block, ODM input blocks 0 through 4, all of OTG0 timing-generator field masks, and the beginning of OTG1 timing-generator field masks through `OTG1_OTG_VERT_SYNC_CONTROL`.

## Register Blocks Covered

The chunk is organized by generated `addressBlock` comments and register comments:

- `dce_dc_opp_fmt1_dispdec` through `dce_dc_opp_fmt4_dispdec`: formatter controls for OPP instances 1-4. These define clamping lower/upper bounds per RGB component, dynamic expansion, pixel encoding, subsampling, dither/truncation/FRC fields, dither seeds, clamp color format, side-by-side stereo width, 4:2:0 memory power controls, and 4:2:2 left-edge extra-pixel control.
- `dce_dc_opp_dpg1_dispdec` through `dce_dc_opp_dpg4_dispdec`: display pattern generator controls. Fields include `DPG_EN`, mode, dynamic range, bit depth, horizontal/vertical resolution, ramp increments, active dimensions, test colors, segment offsets, and double-buffer pending status.
- `dce_dc_opp_oppbuf1_dispdec` through `dce_dc_opp_oppbuf4_dispdec`: OPP buffer controls. Fields describe active width, display segmentation, overlap pixels, pixel repetition, 3D dummy data and v-active spacing, padded pixels, and double-buffer pending status.
- `dce_dc_opp_opp_pipe1_dispdec` through `dce_dc_opp_opp_pipe4_dispdec`: OPP pipe clock and digital bypass fields.
- `dce_dc_opp_opp_pipe_crc1_dispdec` through `dce_dc_opp_opp_pipe_crc4_dispdec`: OPP pipe CRC control, masks, and result registers for alpha/red, green/blue, and C-channel results.
- `dce_dc_opp_opp_top_dispdec`: top-level OPP clock gating and ABM selector fields, including ABM0-4 clock-on status bits.
- `dce_dc_opp_dscrm0_dispdec` through `dce_dc_opp_dscrm4_dispdec`: DSC remapper forward configuration, including enable, OPP pipe source select, double-buffer pending, and enable-status bits.
- `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec`: DC perfmon counter control, counter state, perfmon control, count-value interrupt/ack/status bits, and low/high counter value fields for `DC_PERFMON16`.
- `dce_dc_optc_odm0_dispdec` through `dce_dc_optc_odm4_dispdec`: ODM/OPTC input controls for soft reset, underflow status/clear/interrupts, segment source selection, DSC data format, bytes-per-pixel, segment/slice width, input clock gating, memory select, and spare register storage.
- `dce_dc_optc_otg0_dispdec`: a full OTG0 timing-generator block, including horizontal/vertical totals, blank/sync ranges, trigger A/B controls, flow control, stereo/interlace state, status counters, update locks, double-buffer status, blank color, vertical interrupts, CRC windows/data/control, static-screen detection, 3D structure, global-sync-lock controls, master update, dynamic refresh rate fields, DSC start position, pipe update status, and spare registers.
- `dce_dc_optc_otg1_dispdec`: the start of the equivalent OTG1 block through vertical sync control.

## Important APIs, Types, And Functions

This header does not declare C functions or structs, but its macros become fields in several DC hardware abstraction structs:

- `struct dcn20_opp_shift` and `struct dcn20_opp_mask` in `display/dc/opp/dcn20/dcn20_opp.h` are populated in DCN302 by `OPP_MASK_SH_LIST_DCN20(__SHIFT)` and `OPP_MASK_SH_LIST_DCN20(_MASK)`.
- `struct dcn20_opp_registers` receives the matching register addresses from `OPP_REG_LIST_DCN30(id)` in `display/dc/resource/dcn302/dcn302_resource.c`.
- `struct dcn_optc_shift` and `struct dcn_optc_mask` are populated by `OPTC_COMMON_MASK_SH_LIST_DCN30(__SHIFT)` and `OPTC_COMMON_MASK_SH_LIST_DCN30(_MASK)`.
- `struct dcn_optc_registers` receives the matching OTG/ODM addresses from `OPTC_COMMON_REG_LIST_DCN3_0(id)`.

The concrete construction path for DCN 3.0.2 is in `dcn302_resource.c`:

- `dcn302_opp_create()` allocates `struct dcn20_opp`, then calls `dcn20_opp_construct(opp, ctx, inst, &opp_regs[inst], &opp_shift, &opp_mask)`.
- `dcn302_timing_generator_create()` allocates `struct optc`, attaches `&optc_regs[instance]`, `&optc_shift`, and `&optc_mask`, then calls `dcn30_timing_generator_init()`.
- The resource constructor creates up to five OPP objects and five timing generator objects, matching the 0-4 instance coverage represented by this chunk and neighboring chunks.

The OPP macros from this chunk support operations in `dcn10_opp.c`, `dcn20_opp.c`, and related helpers: bit-depth truncation, spatial/temporal dithering, pixel encoding, chroma subsampling, 4:2:2 edge handling, display test pattern generation, and OPP CRC state capture. The OPTC/OTG/ODM macros support timing-generator programming in `dcn10_optc.c`, `dcn30_optc.c`, and later inherited code paths: mode timing, vertical interrupts, underflow clear/readout, update-lock and double-buffer synchronization, CRC capture, dynamic refresh rate, global sync lock, and ODM segment routing.

## Control Flow And Data Flow

There is no runtime control flow in this header. The generated data flow is:

1. The DCN302 resource file includes `dcn_3_0_2_offset.h` and this `dcn_3_0_2_sh_mask.h`.
2. Register-list macros from subsystem headers expand symbolic register names into ASIC-specific addresses.
3. Mask/shift-list macros expand symbolic field names into the `__SHIFT` and `_MASK` constants defined here.
4. Constructors store those addresses, shifts, and masks into per-block register tables.
5. Runtime DC code calls register helper macros. Those helpers use the field shift and mask tables to insert or extract field values without hard-coded bit arithmetic at each call site.

For example, an OPP formatter update such as a pixel encoding or dither-mode write depends on `FMTn_FMT_CONTROL__...` and `FMTn_FMT_BIT_DEPTH_CONTROL__...` definitions. An OPTC underflow query or clear depends on `ODMn_OPTC_INPUT_GLOBAL_CONTROL__OPTC_UNDERFLOW_OCCURRED_STATUS` and `__OPTC_UNDERFLOW_CLEAR`. Timing programming depends on OTG total/blank/sync masks, while CRC capture depends on OTG and OPP CRC control/result masks.

## State And Persistence Behavior

The macros themselves are compile-time constants and hold no software state. The state they describe is hardware state persisted in display engine registers until overwritten by driver programming, display engine reset, power gating, or ASIC reset.

Important state classes represented in this chunk include:

- Double-buffer and update synchronization state: `FMT_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `DPG_DOUBLE_BUFFER_PENDING`, `OPPBUF_DOUBLE_BUFFER_PENDING`, `DSCRM_DSC_DOUBLE_BUFFER_REG_UPDATE_PENDING`, `OPTC_DOUBLE_BUFFER_PENDING`, `OTG_UPDATE_PENDING`, and several OTG pending subfields.
- Interrupt/status/ack state: ODM underflow status/clear fields, OTG vertical interrupt status/clear fields, OTG vtotal event status/ack fields, perfmon counter interrupt status/ack fields, and trigger/force-count/force-vsync occurrence fields.
- Timing state: OTG horizontal and vertical counters, frame/VF/HV counters, nominal vertical position, dynamic refresh rate bounds, update windows, keepout windows, and global-sync status.
- CRC and readback state: OPP pipe CRC results, OTG CRC result data and windows, CRC masks, pixel data readback registers, and CRC one-shot pending indicators.
- Power/clock state: OPP pipe clock enable/on bits, FMT 4:2:0 memory power fields, OPP top ABM clock-on fields, ODM input clock enable/on/gate-disable bits, and OTG clock busy/enable/on/gate-disable fields.

## Dependencies And Integration Points

This chunk depends on the generated offset header having matching register address names. It also depends on the display subsystem field-list macros selecting the correct instance-0 field names when building reusable shift/mask tables. For OPP and OPTC, the resource code builds one shared shift/mask table from instance-0-style field names and separate per-instance address tables. Therefore the bit layouts must be identical across instances 0-4; this chunk provides the instance 1-4 evidence for that layout.

Primary integration points:

- `display/dc/resource/dcn302/dcn302_resource.c` includes the header and binds its constants into DCN302 resource objects.
- `display/dc/opp/dcn20/dcn20_opp.h` and inherited `dcn10_opp` code define and consume OPP formatter, DPG, OPPBUF, and CRC field tables.
- `display/dc/optc/dcn30/dcn30_optc.h` defines the OPTC/OTG/ODM register and field lists used by DCN302 timing generators.
- `display/dc/optc/dcn10/dcn10_optc.c`, `display/dc/optc/dcn30/dcn30_optc.c`, and inherited OPTC functions consume the tables for underflow handling, timing setup, trigger handling, CRC, and status reads.
- Diagnostic/debug structures in `display/dc/dc.h` name many of the same fields for register-state capture, especially formatter, OPP CRC, and OPTC underflow fields.

## Risks And Edge Cases

- Generated macro drift is high impact. If a shift/mask value is wrong but still compiles, the driver may silently program the wrong hardware bit, causing display corruption, black screen, underflow storms, CRC mismatch, broken stereo/interlace behavior, or incorrect power/clock handling.
- Instance consistency matters. Shared shift/mask structs are based on common field layouts while addresses vary per instance. Any real ASIC layout difference between OPP/ODM/OTG instances would not be represented safely by this pattern.
- Double-buffer pending and update-lock masks are synchronization critical. Incorrect masks around `OTG_DOUBLE_BUFFER_CONTROL`, `OPTC_DOUBLE_BUFFER_PENDING`, formatter pending fields, or DSCRM pending fields can make the driver believe an update has latched when hardware is still pending, or wait forever on the wrong bit.
- Status-clear fields are often write-one-to-clear. Incorrect masks for ODM underflow clear, OTG interrupt clear, perfmon ack, trigger clear, or vtotal ack fields can lose events or leave stale interrupt state asserted.
- CRC fields are used for validation and diagnostics. Wrong CRC control/result masks may make automated display CRC tests fail even when output is correct, or hide real output corruption.
- The chunk boundary splits logical content: it starts with the last field of OPP pipe CRC0 result2 from the previous block and ends in the middle of OTG1 vertical sync control. The final per-file merge must combine adjacent chunks before drawing whole-file conclusions.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display integration signals:

- Build coverage for `amd/display` with DCN302 enabled should catch missing or renamed macro fields in `OPP_MASK_SH_LIST_DCN20`, `OPTC_COMMON_MASK_SH_LIST_DCN30`, and `dcn302_resource.c` table initialization.
- Display mode-set tests on DCN302-class hardware should exercise OTG totals, blanking, sync polarity, `OTG_MASTER_EN`, update-lock behavior, and ODM source/width configuration.
- Underflow tests and logs should verify `OPTC_UNDERFLOW_OCCURRED_STATUS` and `OPTC_UNDERFLOW_CLEAR` read/clear the expected ODM input state.
- Dithering, truncation, YCbCr 4:2:2/4:2:0, and pixel-encoding tests should validate the FMT fields in `FMT_CONTROL`, `FMT_BIT_DEPTH_CONTROL`, `FMT_CLAMP_CNTL`, and `FMT_422_CONTROL`.
- DisplayPort compliance or KMS CRC tests can exercise OPP pipe CRC and OTG CRC windows/data fields.
- Test pattern paths through `opp2_set_disp_pattern_generator()`, `opp2_program_dpg_dimensions()`, `opp2_dpg_set_blank_color()`, and `opp2_dpg_is_pending()` can validate DPG and OPPBUF masks.
- Dynamic refresh rate, PSR/static-screen, stereo/interlace, and global-sync-lock tests should cover the OTG0 fields for vtotal min/max/mid, static-screen control, stereo control/status, interlace control/status, and GSL status/control.
