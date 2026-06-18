# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 32772-35325

## Purpose

This chunk is a generated DCN 4.2 ASIC register field-definition section for AMD display hardware. It contains C preprocessor constants only: `__SHIFT` values and `_MASK` values for MMIO bitfields. The constants are consumed by the AMD Display Core register helper layer to compose, update, poll, and decode register fields without hard-coding bit positions in functional code.

The covered range spans output-pixel-processor and timing-generator register blocks. It starts in the middle of the `dce_dc_opp_dpg1_dispdec` definitions, continues through OPP/FMT/DPG instances 1-3, OPP top-level and DSC-remap forwarding fields, then covers ODM0-ODM3 input controls and OTG0/OTG1 timing-generator controls through `OTG1_OTG_STATIC_SCREEN_CONTROL`.

## Contents and Important Definitions

The chunk contains 2,120 `#define` entries grouped by commented register names and 25 address blocks:

- `dce_dc_opp_oppbuf1_dispdec`, `dce_dc_opp_opp_pipe1_dispdec`, `dce_dc_opp_opp_pipe_crc1_dispdec`: output buffer, OPP pipe clock/bypass, and pipe CRC controls for OPP instance 1.
- `dce_dc_opp_fmt2_dispdec`, `dce_dc_opp_dpg2_dispdec`, `dce_dc_opp_oppbuf2_dispdec`, `dce_dc_opp_opp_pipe2_dispdec`, `dce_dc_opp_opp_pipe_crc2_dispdec`: formatter, display pattern generator, output buffer, pipe control, and OPP CRC fields for OPP/FMT/DPG instance 2.
- `dce_dc_opp_fmt3_dispdec`, `dce_dc_opp_dpg3_dispdec`, `dce_dc_opp_oppbuf3_dispdec`, `dce_dc_opp_opp_pipe3_dispdec`, `dce_dc_opp_opp_pipe_crc3_dispdec`: equivalent field layout for instance 3.
- `dce_dc_opp_opp_top_dispdec`: top-level OPP clock and ABM control fields.
- `dce_dc_opp_dscrm0_dispdec` through `dce_dc_opp_dscrm3_dispdec`: DSC remap forwarding configuration, including `DSCRM_DSC_FORWARD_EN`, `DSCRM_DSC_OPP_PIPE_SOURCE`, and forward-enable status.
- `dce_dc_opp_opp_dcperfmon_dc_perfmon_dispdec`: DC perfmon counter control, value, high/low, state, and overflow-style control fields.
- `dce_dc_optc_odm0_dispdec` through `dce_dc_optc_odm3_dispdec`: ODM/OPTC input global control, underflow status/clear, segment source selection, data format, DSC byte count, width, clock, memory, and spare fields.
- `dce_dc_optc_otg0_dispdec` and `dce_dc_optc_otg1_dispdec`: OTG timing, trigger, stereo, status, interrupt, update-lock, CRC, static-screen, dynamic refresh-rate, global sync, p-state, encryption, and spare fields. The chunk ends at the static-screen control masks for OTG1.

Important repeated field families are:

- `FMTx_FMT_BIT_DEPTH_CONTROL`: truncation, spatial dither, temporal dither, RGB/frame/high-pass randomization, FRC selectors, and temporal reset/level fields.
- `FMTx_FMT_CONTROL`: pixel encoding, 4:2:0 or 4:2:2 subsampling control, stereo sync override, CbCr reduction bypass, and double-buffer pending status.
- `DPGx_DPG_*`: display-pattern-generator enable/mode, dynamic range, bit depth, dimensions, colors, segment offset, ramp increments, and double-buffer pending.
- `OPPBUFx_OPPBUF_*`: active width, display segmentation, overlap pixels, pixel repetition, 3D dummy data/vertical active spaces, padded segment pixels, and double-buffer pending.
- `OPP_PIPE_CRCx_*`: OPP pipe CRC enable, continuous/one-shot state, stereo/interlace modes, source/pixel select, mask, and result registers.
- `ODMx_OPTC_*`: ODM input segmentation and source selection, DSC formatting, segment widths, input clocks, underflow/RSMU underflow status and clear bits, and memory selection/status.
- `OTGx_OTG_*`: full timing generator control surface for horizontal/vertical totals, blank/sync windows, triggers, count/status snapshots, interrupts, double-buffering, CRC windows/results/readbacks, static-screen detection, GSL/global update lock, DRR, and p-state-related control.

## APIs, Types, and Integration Points

This header does not define functions or types. Its "API" is the macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The functional driver code maps these generated macros into typed shift/mask tables. In `drivers/gpu/drm/amd/display/dc/resource/dcn42/dcn42_resource.c`, DCN42 constructs static tables such as `opp_shift`, `opp_mask`, `dsc_shift`, `dsc_mask`, `optc_shift`, and `optc_mask` using list macros. The register addresses come from companion offset headers, while this file supplies the bit layout.

Key consumers include:

- OPP construction: `dcn42_opp_create()` initializes four OPP register tables and passes `opp_regs[inst]`, `opp_shift`, and `opp_mask` into `dcn20_opp_construct()`. The relevant list macros include `OPP_MASK_SH_LIST_DCN20(__SHIFT)` and `OPP_MASK_SH_LIST_DCN20(_MASK)`, which depend on this header's `FMT0/DPG0/OPPBUF0` field macros as canonical layout definitions. The chunk also supplies instance 1-3 equivalents for per-instance direct register tables.
- OPP programming: `dcn10_opp.c`, `dcn20_opp.c`, and related OPP code use `REG_UPDATE_*`, `REG_READ`, and state-dump paths for `FMT_BIT_DEPTH_CONTROL`, `FMT_CONTROL`, `OPPBUF_CONTROL`, `DPG_*`, and `OPP_PIPE_CRC_CONTROL`.
- DSC forwarding: `dcn401_dsc.h` and `dcn401_dsc.c` consume `DSCRM0_DSCRM_DSC_FORWARD_CONFIG` field shifts/masks for enable, OPP pipe source selection, and enable status. Functional paths use `REG_GET_2`, `REG_UPDATE_2`, `REG_UPDATE`, and `REG_WAIT` around `DSCRM_DSC_FORWARD_CONFIG`.
- OPTC/timing generation: `dcn42_optc.h` maps many `OTG0_*` and `ODM0_*` fields into `dcn_optc_shift` and `dcn_optc_mask`. Runtime code uses those tables for timing programming, static-screen events, CRC capture, underflow handling, ODM segmentation, global update locks, GSL synchronization, DRR, and p-state windows.
- DMUB, IRQ, GPIO, clock manager, and resource files include `dcn_4_2_0_sh_mask.h` alongside `dcn_4_2_0_offset.h` when they need DCN42 register-field access.

## Control Flow

There is no executable control flow in this chunk. Runtime flow is indirect:

1. DCN42 resource construction includes this header and builds static shift/mask tables from generated macros.
2. Hardware block constructors receive register-address tables plus these shift/mask tables.
3. Register helper macros such as `REG_UPDATE`, `REG_UPDATE_2`, `REG_UPDATE_3`, `REG_SET_2`, `REG_GET`, `REG_GET_2`, `REG_READ`, and `REG_WAIT` use the per-block tables to modify or inspect the intended bitfields.
4. Hardware state changes occur through MMIO writes to the registers described here; readback/status fields report hardware state back to the driver.

Because field layout is selected at compile time, a bad shift or mask produces deterministic but hardware-specific misprogramming rather than a local C runtime failure.

## State and Persistence Behavior

The definitions are compile-time constants and have no in-memory state by themselves. They describe persistent hardware-visible state in DCN registers:

- Double-buffer pending bits appear in DPG, OPPBUF, FMT, ODM, OTG, and DRR-related controls and are used to determine when staged updates have latched.
- Status fields report clock-on, underflow, CRC pending/results, static-screen status, stereo eye/frame count, force-count events, interrupt status, and update-lock status.
- Control fields persist in hardware registers until changed by the driver, reset, or power-gated hardware state transitions.
- Readback fields for OTG CRC windows provide a hardware-latched view of programmed CRC window coordinates.

The generated constants also shape debug and state collection. For example, OPP and OPTC read-reg-state paths read raw registers whose bit meanings are defined here.

## Dependencies

This chunk depends on the broader AMD DC register-generation scheme:

- Companion register address definitions in `dcn_4_2_0_offset.h`.
- Register helper macros and block-specific structures in AMD Display Core, especially OPP, DSC, and OPTC headers.
- Consistent generated naming across instances. Many table macros use instance 0 field layouts as the canonical shift/mask source because corresponding instance registers are expected to share the same bit layout.
- Hardware documentation or generation inputs that guarantee the numeric shifts/masks match DCN 4.2 silicon.

## Risks and Maintenance Hazards

- Shift/mask drift is high impact. If a generated bit position differs from the actual DCN 4.2 register layout, the driver may write neighboring fields, leave requested fields unchanged, or misread status.
- Instance symmetry is assumed by consumer macros. The chunk shows instance-specific definitions for OPP/FMT/DPG/ODM/OTG blocks, while many consumer tables use instance 0 macros as the shared layout. Any future asymmetric instance layout would require consumer-list changes, not only generated definitions.
- Double-buffer and pending fields are timing-sensitive. Misdefined pending bits can cause waits to time out, updates to be applied too early, or state validation to report false readiness.
- CRC fields are used for display validation and debug. Incorrect CRC masks, window fields, or result fields can silently invalidate CRC-based diagnostics.
- Underflow clear/status fields are operationally important. Incorrect ODM/OPTC underflow masks can hide real display underflow or clear the wrong interrupt/status bit.
- This line range starts mid-register for `DPG1_DPG_DIMENSIONS`; the corresponding active-height shift/mask and active-width shift are immediately before the chunk. Merge-lane research should join this with the adjacent chunk to avoid treating `DPG1_DPG_DIMENSIONS` as incomplete at file level.

## Test and Validation Signals

Useful signals for changes touching this generated section include:

- Build coverage for DCN42 display code, because unresolved or renamed macros should fail at compile time in `dcn42_resource.c`, `dcn42_optc.h`, OPP headers, DSC headers, DMUB, IRQ, GPIO, and clock/resource paths.
- Display bring-up on DCN 4.2 hardware with multiple pipes, especially OPP instances 1-3 and ODM split/merge paths.
- Modeset and hotplug tests that exercise OTG timing programming, update locks, vertical interrupts, DRR, and p-state windows.
- CRC validation paths, including OTG CRC window programming/readback and OPP pipe CRC result reads.
- DSC enable/disable and DSC-forwarding tests that cover `DSCRM_DSC_FORWARD_CONFIG` enable, source selection, and status waits.
- Underflow injection or stress tests that verify ODM/OPTC underflow status, clear, and interrupt fields.
- Static-screen detection tests that verify `OTG_STATIC_SCREEN_CONTROL` event mask/frame count programming and status/interrupt behavior.
