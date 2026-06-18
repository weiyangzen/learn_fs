# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_1_0_sh_mask.h lines 17516-20046

## Purpose

This chunk is part of the generated DCN 1.0 register shift/mask header for AMD display hardware. It does not implement executable logic; it defines field positions and bit masks used by the display driver register helper macros to read, write, and compose MMIO values safely for DCN 1.0 display blocks.

The assigned range starts at the tail of the `DSCL3` scaler definitions and then covers several display pipeline register blocks:

- `DSCL3` scaler/output-buffer tail fields for black offset, update state, autocalibration, overscan, OTG blanking, recout/MPC sizing, line-buffer format, line-buffer memory partitioning, memory power control/status, and OBUF control.
- `CM3` color-management fields for input/output color matrices, input degamma, degamma/regamma RAM programming, gamut remap, output CSC, bias/scale, HDR multiplier, clamps, denorm, output dither, random seeds, and CM memory power state.
- `DC_PERFMON15` and `DC_PERFMON16` display performance monitor fields.
- `MPCC0` through `MPCC3` composition fields and the common MPC configuration block for clock gating, soft reset, CRC, output muxing, stall grace, and vupdate locks.
- The beginning of `ABM0` and `ABM1` adaptive backlight management definitions, including PWM levels, ABM enable/control, ACE curve parameters, histogram/luma-stat control, sample rates, histogram bins/results, and update/read locks.

The practical purpose is to provide the bitfield metadata consumed by `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, `SF`, `SR`, and related AMD display register-list macros. For this header, correctness of every shift/mask pair is the interface contract.

## Important APIs, Types, And Functions

This header exports preprocessor constants, not functions or C types. The important "APIs" are the generated macro names:

- `*_SHIFT` constants, such as `CM3_CM_DGAM_CONTROL__CM_DGAM_LUT_MODE__SHIFT`, specify the low bit of a hardware field.
- `*_MASK` constants, such as `MPCC0_MPCC_CONTROL__MPCC_GLOBAL_ALPHA_MASK`, specify the full bitmask for that field in its 32-bit MMIO register.
- Address-block comments, such as `// addressBlock: dce_dc_dpp3_dispdec_cm_dispdec`, group the register fields by hardware block and instance.
- `DSCL3_*` fields describe the DPP3 scaler and output-buffer tail.
- `CM3_*` fields describe color-management hardware attached to DPP3.
- `DC_PERFMON15_*` and `DC_PERFMON16_*` fields describe performance counter programming and readout registers for DPP3 and MPC performance-monitor instances.
- `MPCC[0-3]_*` and `MPC_*` fields describe multi-plane composition and composition-wide configuration.
- `ABM0_*` and `ABM1_*` fields describe OPP adaptive backlight/PWM and histogram/luma-stat units.

The main consumers are the AMD display register helper layers under `drivers/gpu/drm/amd/display/dc/`. For example, `dcn10_dpp.c`, `dcn10_dpp_cm.c`, `dcn10_dpp_dscl.c`, `dcn10_cm_common.c`, and `dcn10_mpc.h` build register tables and use these masks through the `TF_SF`, `SF`, `SRI`, `SRII`, `REG_SET_*`, `REG_UPDATE_*`, and `REG_GET_*` macros.

## Control Flow

There is no runtime control flow in this header. The effective control flow appears in the generated macro expansion path:

1. DCN-specific code declares register address arrays and mask/shift tables using macros such as `SF(MPCC0_MPCC_CONTROL, MPCC_MODE, mask_sh)` or transfer-function variants for CM and DSCL fields.
2. Those macros resolve to the matching `__SHIFT` and `_MASK` constants from this file.
3. Runtime driver code calls register helpers such as `REG_SET`, `REG_SET_2`, `REG_UPDATE`, `REG_UPDATE_7`, `REG_GET`, or `REG_WAIT`.
4. The helpers use the stored mask/shift data to clear, insert, extract, or poll bitfields in 32-bit MMIO register values.

The driver-level flows represented by this chunk include:

- Scaler programming: DSCL code writes sizing, overscan, line-buffer, black-offset, and memory-power fields while setting up DPP scaling paths.
- Color pipeline programming: DPP color-management code selects gamut-remap, input/output CSC, degamma/regamma LUT mode, RAM A/B bank selection, region segmentation, and LUT data writes.
- MPC composition programming: MPC code binds DPP outputs into MPCC slots, selects top/bottom inputs, programs alpha blending/global alpha/gain, sets backgrounds, and monitors MPCC busy/stall/exception state.
- Diagnostics and validation: CRC and perfmon fields let driver/debug paths select sources, start one-shot or continuous CRCs, program event counters, read counter values, and acknowledge interrupt/status bits.
- Backlight/statistics: ABM fields program PWM levels, adaptive-brightness controls, histogram/luma-stat collection, sample-rate counters, and status/readback locks.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. Its constants describe persistent hardware state in DCN MMIO registers. Writes performed using these masks persist in the display engine until another MMIO write, a display block reset, GPU reset, power-gating transition, or firmware/driver reinitialization changes the same registers.

Important state surfaces described by this range include:

- DSCL3 update state, line-buffer memory partitioning, memory-power control/status, OBUF mode, and scaler black-offset/overscan/blanking values.
- CM3 LUT mode, LUT index/data, RAM A/B region setup, gamut and CSC coefficient matrices, range clamps, dither enable/mode/depth, random seeds, and CM memory-power state.
- MPCC link state, alpha/composition modes, update-lock selection/status, background color, idle/busy indicators, stall interrupt/ack/mask, and MPCC input-check exception flags.
- MPC-wide soft reset bits, CRC source/control/result state, output mux selections, vupdate lock bits for address/config/cursor update groups, and stall grace-window duration.
- ABM0/ABM1 PWM duty/target/current values, ACE curves/thresholds, histogram/luma-stat result registers, sample-rate counters, missed-frame/read-progress bits, and lock/update-pending controls.

Several fields are explicitly lock- or latch-oriented. `*_REG_LOCK`, `*_UPDATE_PENDING`, `*_UPDATE_AT_FRAME_START`, `*_READBACK_DB_REG_VALUE_EN`, `*_IGNORE_MASTER_LOCK_EN`, `MPC_CRC_UPDATE_LOCK`, and vupdate lock fields indicate that writes may be double-buffered, frame-start-latched, or blocked by higher-level display update locking. Driver code must respect those semantics when programming live pipes.

## Dependencies

This file depends on the generated ASIC register naming convention used across the AMDGPU display stack. It is normally paired with the matching DCN 1.0 offset header, which provides register addresses, while this file provides field extraction and insertion metadata.

The key dependencies are:

- `drivers/gpu/drm/amd/display/dc/inc/reg_helper.h`, which defines the generic register access helpers that combine register addresses with these field masks and shifts.
- DCN 1.0 DPP/CM code under `drivers/gpu/drm/amd/display/dc/dpp/dcn10/`, which consumes `DSCL3_*` and `CM3_*` fields for scaler and color-management programming.
- DCN CM helper code under `drivers/gpu/drm/amd/display/dc/dcn10/`, which uses mask/shift tables for CSC and piecewise-linear gamma region programming.
- MPC code under `drivers/gpu/drm/amd/display/dc/mpc/dcn10/`, which consumes `MPCC0_*`-derived masks for all MPCC instances because repeated instances share the same field layout.
- Interrupt source definitions under `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h`, which map ABM and MPC perfmon status bits to display interrupt sources.
- DC color, plane, and stream state structures that select which gamut, CSC, gamma, scaler, composition, CRC, or ABM programming path the register helpers execute.

The generated field layout also depends on hardware-family stability: code often uses instance-zero field masks for multiple instances (`MPCC0` masks for MPCC arrays, CM0/CM3 family layouts, and repeated perfmon schemas). A mismatch between instance field layout and the chosen mask table would corrupt unrelated bits.

## Integration Points

This chunk integrates with several DCN 1.0 display subsystems:

- DPP scaler and line buffer: `dcn10_dpp_dscl.c` uses DSCL fields such as `SCL_BLACK_OFFSET`, `DSCL_MEM_PWR_CTRL`, and `DSCL_MEM_PWR_STATUS` while setting scaler state, memory power, and format-dependent offsets.
- DPP color management: `dcn10_dpp.c` and `dcn10_dpp_cm.c` read/write CM fields for input gamma, degamma, regamma, gamut remap, output CSC, and LUT RAM programming. The coefficient fields are integrated through common CSC helper structures.
- Common CM helpers: `dcn10_cm_common.c` receives register IDs plus shift/mask structures and writes packed CSC coefficients and PWL gamma-region registers. This chunk supplies many of the packed field definitions those helpers need.
- MPC/MPCC composition: `dcn10_mpc.h` and later MPC implementations use the MPCC field definitions to program top/bottom DPP selection, OPP routing, alpha blending, stereo/field mode, update locks, background color, and status checking.
- Diagnostics and debug paths: MPC CRC fields and perfmon fields are used to validate composition output, monitor hardware events, count display block events, and acknowledge counter interrupts.
- ABM/DMCU integration: ABM0/ABM1 fields correspond to adaptive backlight management and stats interrupts. The interrupt-source header maps histogram-ready, luma-stat-ready, and backlight-update events for both ABM instances.

The chunk starts in the middle of the `DSCL3_SCL_VERT_FILTER_INIT_BOT_C` register group and ends in the middle of the `ABM1` block. The per-file merge should join this research with adjacent chunks for the full DSCL3 scaler context before line 17516 and the remainder of ABM1 after line 20046.

## Risks And Edge Cases

- Off-by-one field definitions are high-impact. A wrong shift or mask can silently write the wrong hardware bits, causing bad color, bad scaling, composition corruption, missed interrupts, display underflow, stuck update locks, or unusable backlight control.
- Many registers pack two or more signed/fixed-point fields into one 32-bit value, especially CSC coefficients, LUT region endpoints, offsets, clamps, alpha/gain, and PWM/sample-rate fields. Callers must pass values preformatted for the hardware field width.
- The chunk contains repeated layouts for RAM A/B, MPCC0-3, DC_PERFMON15/16, and ABM0/1. Repetition makes generated-copy errors possible and makes reviews dependent on comparing corresponding instances for field consistency.
- Several fields are status/ack or write-one-style control surfaces, such as stall interrupts, perfcounter interrupts, missed-frame clears, and update-pending/read-progress bits. Treating them as ordinary persistent configuration fields can clear events or leave stale status.
- Update-lock fields require correct sequencing with vertical update/frame-start boundaries. Programming locked or double-buffered fields without checking pending/status bits can delay changes or apply partial state.
- Memory power fields for DSCL and CM interact with register access. Polling `*_MEM_PWR_STATUS` and sequencing force/disable fields incorrectly can produce timeouts or writes to unavailable memories.
- CRC and perfmon fields are diagnostic but can still affect interrupt behavior. Enabling counter/CRC interrupts without an ACK path can generate persistent display interrupts.
- ABM histogram and luma-stat result registers are hardware-produced data. Result reads must account for ready/read-progress/missed-frame bits and should not assume software owns the update cadence.

## Test Signals

Useful validation signals for code depending on this chunk include:

- Build-time coverage: compile DCN 1.0 display code that includes the generated offset and sh/mask headers, especially DPP, CM, DSCL, MPC, and ABM paths.
- Register helper sanity: check that `SF`/`TF_SF` entries resolve to the intended `__SHIFT` and `_MASK` fields and that no field name typo selects the wrong register family.
- Display functional tests: exercise scaling, underscan/overscan, YCbCr/RGB formats, line-buffer partitioning, and plane updates that use DSCL3 fields.
- Color tests: run degamma/regamma/gamut/CSC paths, verify LUT programming and RAM A/B selection, and compare CRC or visual output for known color transforms.
- Composition tests: enable multiple planes/cursors and alpha blending, then verify MPCC routing, background, global alpha/gain, and idle/busy/status behavior.
- CRC/perfmon diagnostics: program MPC CRC one-shot/continuous modes and perfmon counters, read high/low values, and confirm interrupt status/ack bits clear as expected.
- ABM tests: vary ambient/user/backlight levels, enable ABM, collect histogram/luma-stat results, and confirm ready/update interrupts map to the expected ABM0/ABM1 sources.
- Power-management tests: enter/exit display memory power states and confirm `DSCL_MEM_PWR_STATUS`, `CM_MEM_PWR_STATUS`, and OBUF memory state fields are polled and restored correctly.
