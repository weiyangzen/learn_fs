# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h lines 7719-10374

## Scope

This chunk is a generated AMD DCN 3.0 register-offset header segment. It contains preprocessor register address macros, not executable C logic. The range starts in the middle of the DPP5 color-management block at `mmCM5_CM_BLNDGAM_RAMA_END_CNTL1_G` and ends mid-way through the DIO DisplayPort AUX2 block at `mmDP_AUX2_AUX_GTC_SYNC_ERROR_CONTROL_BASE_IDX`.

The chunk defines 2,396 macros: 1,198 `mm...` register-offset macros and 1,198 matching `..._BASE_IDX` macros. Every visible register offset has a paired base-index macro, and all visible `_BASE_IDX` values are `2`, meaning consumers combine each register offset with segment 2 of the DCN base table.

## Purpose

The purpose of this header region is to provide ASIC-specific symbolic addresses for DCN 3.0 display hardware. These symbols let the AMDGPU display stack build register tables for:

- DPP5 color management and gamma/shaper/3D LUT programming.
- DPP5 DC performance counters.
- Six OPP output-pixel-processing instances, including FMT, DPG, OPPBUF, OPP pipe control, and OPP pipe CRC blocks.
- OPP top-level controls, DSC remap forwarding, and OPP performance counters.
- Six ODM input instances and six OTG timing-generator instances.
- OPTC miscellaneous and performance counter registers.
- DIO I2C/DDC, DIO scratch/power/clock/interrupt registers, six HPD instances, DIO performance counters, and the first three DP AUX register groups, with the third group truncated by the chunk boundary.

The macros are consumed by DC, DMUB, IRQ, GPIO, resource, DIO, OPP, and OPTC code through register-list and bitfield-list macros. They form the numeric address layer beneath typed structures such as OPP, OPTC, AUX, HPD, and IRQ services.

## Important Macro Families

### DPP5 Color Management

Lines 7719-7984 finish the DPP5 `CM5` register set. They cover blend gamma RAM A/B control and region registers, HDR multiplier, color-management memory power control/status, dealpha and coefficient format, shaper offset/scale/LUT access, shaper RAM A/B region programming, 3D LUT mode/index/data/read-write controls, output normalization and offsets, and test debug index/data registers.

These names match color-management helper patterns used elsewhere in the display code, where generated `REG(...)` values are assigned into gamma/shaper/LUT register tables. The visible chunk only covers instance 5; earlier chunks should contain `CM0` through `CM4` and the beginning of `CM5`.

### DC Performance Counters

The chunk contains three performance monitor groups:

- `DC_PERFMON17_*` for DPP5 performance counting.
- `DC_PERFMON18_*` for OPP performance counting.
- `DC_PERFMON20_*` for DIO performance counting.

Each group contains counter control, secondary control, state, monitor control, current-value, high, and low result registers. These offsets are used by generic DC perf counter code to select hardware blocks and read accumulated values.

### OPP/FMT/DPG/OPPBUF/CRC Instances

Lines 8007-8498 define six repeated OPP instance groups using base addresses `0x0`, `0x168`, `0x2d0`, `0x438`, `0x5a0`, and `0x708`.

For each instance `0` through `5`, the chunk provides:

- `FMTn_*` registers for clamp components, dynamic expansion, format control, bit-depth control, dither random seeds, clamp control, side-by-side stereo, 4:2:0 memory control, and 4:2:2 control.
- `DPGn_*` registers for display pattern generator control, ramp control, dimensions, color channels, offset segment, and status.
- `OPPBUFn_*` registers for OPP buffer control and 3D parameters.
- `OPP_PIPEn_OPP_PIPE_CONTROL`.
- `OPP_PIPE_CRCn_*` control, mask, and three result registers.

These definitions are integration-critical for output formatting, dithering, test-pattern generation, output-buffer behavior, CRC validation, and pipe-level status/control.

### OPP Top, DSCRM, ODM, and OTG

The OPP top block exposes `OPP_TOP_CLK_CONTROL` and `OPP_ABM_CONTROL`, followed by `DSCRM0` through `DSCRM5` DSC-forwarding configuration registers. These are routing/forwarding controls around the output processor and display stream compression path.

The ODM input blocks, `ODM0` through `ODM5`, each define global control, source select, data format, bytes-per-pixel, width, input clock, memory config, and spare registers. Their base addresses advance by `0x40`. These symbols support output data merger configuration, especially multi-pipe or high-bandwidth display modes.

The OTG blocks, `OTG0` through `OTG5`, are the largest portion of the chunk. Each repeated instance covers horizontal and vertical totals, blanking, sync, trigger controls, force-count, flow, stereo, control, blanking, interlace, readback, status, counters, snapshot, interrupts, update locks, double buffering, master enable, blank color, CRC windows/results, static-screen detection, 3D structure, global sync lock, manual triggers, DRR timing, DTO constants, request control, DSC start position, pipe update status, and spare registers.

These are timing-generator registers. Display mode programming, vblank/vertical interrupt scheduling, dynamic refresh-rate changes, stereo/interlace handling, CRC capture, and global-sync coordination all depend on these offsets being correct.

### DIO, HPD, I2C/DDC, and AUX

The DIO portion begins at line 10047. It defines:

- `DC_I2C_*` control, arbitration, interrupt, software status, six DDC hardware status registers, six DDC speed/setup pairs, transaction slots, data, EDID detection, and read-request interrupt.
- `DIO_*` scratch registers, memory power controls/status, clock controls, power-management control, generic interrupt message/clear, and `DIG_SOFT_RESET`.
- `HPD0` through `HPD5` interrupt status/control, HPD control, fast-train control, and toggle filter controls, with instance base addresses stepping by `0x20`.
- `DP_AUX0`, `DP_AUX1`, and the start of `DP_AUX2` AUX-control groups, including software/low-speed data and status, arbitration, interrupt control, DPHY TX/RX controls and status, GTC sync controls/status, and PHY wake control where the full instance is visible.

The chunk ends before completing `DP_AUX2`; later chunks should contain the rest of AUX2 plus additional AUX instances if present.

## APIs, Types, and Functions

This header segment declares no C functions, structs, enums, or storage. Its API surface is preprocessor-only:

- `mm<block>_<register>` expands to a register offset.
- `mm<block>_<register>_BASE_IDX` expands to the DCN base segment index used with the offset.
- Consumers commonly transform these through macros such as `REG_OFFSET(reg_name)`, `REG(reg)`, `BASE(...)`, `OPP_SF(...)`, `AUX_SF(...)`, `LE_SF(...)`, and `SF(...)`.

Observed in-tree integration examples include:

- `dmub/src/dmub_dcn30.c` and `dmub/src/dmub_dcn302.c` include this header and use `REG_OFFSET_EXP`/`BASE_INNER` to build DMUB register offsets.
- `dc/irq/dcn30/irq_service_dcn30.c`, `dc/gpio/dcn30/*`, `dc/resource/dcn30/dcn30_resource.c`, and `dc/clk_mgr/dcn30/dcn30_clk_mgr.c` include this header directly for DCN 3.0 register programming.
- `dc/opp/dcn10/dcn10_opp.h` references fields under registers such as `FMT0_FMT_CONTROL`.
- `dc/optc/dcn30/dcn30_optc.h` references OTG timing registers such as `OTG0_OTG_H_TOTAL`.
- `dc/dce/dce_aux.h` and `dc/dio/dcn10/dcn10_link_encoder.h` reference AUX and HPD fields under registers such as `DP_AUX0_AUX_CONTROL` and `HPD0_DC_HPD_INT_STATUS`.

## Control Flow

There is no runtime control flow in this chunk. Runtime behavior emerges when driver code expands these macros into register tables and then calls MMIO read/write helpers. The effective flow is:

1. A DCN 3.0 source file includes this offset header and the matching shift/mask header.
2. Register-list macros instantiate per-block register address tables.
3. Hardware object constructors attach those tables to block-specific objects such as OPP, OPTC, AUX, HPD, IRQ, GPIO, and DMUB interfaces.
4. Mode-setting, link training, hotplug, color-management, CRC, perfmon, or interrupt code reads or writes the computed MMIO addresses.

Because the header is generated and flat, the important control-flow invariant is compile-time naming consistency: the same symbolic register names must exist in offset, shift, and mask headers and must match the register-table macros expected by consumers.

## State and Persistence Behavior

The macros themselves are stateless and create no persistence. They describe persistent hardware register locations whose values live in the GPU display engine until changed by driver writes, hardware state machines, reset, power gating, or suspend/resume transitions.

Important hardware state represented by this chunk includes:

- DPP5 color LUT/gamma/shaper/3D LUT state.
- OPP format, dithering, clamp, buffer, CRC, and pattern-generator state.
- OTG mode timing, vertical interrupt, CRC, global sync, DRR, and update-lock state.
- ODM input routing/format/clock/memory configuration.
- DIO I2C transaction state, HPD sense/interrupt state, AUX transaction/PHY/GTC sync state, and DIO power/clock state.
- Performance counter configuration and accumulated counter values.

Driver suspend/resume, display mode transitions, link retraining, HPD handling, and color pipeline updates must restore or reprogram these hardware registers through higher-level DC code. The header only provides addresses for that work.

## Dependencies

This chunk depends on the rest of the generated DCN 3.0 ASIC register set:

- Earlier/later chunks of `dcn_3_0_0_offset.h` for other blocks, full include guards, and complete macro coverage.
- Matching `dcn_3_0_0_sh_mask.h` or related generated shift/mask headers for bit positions and masks.
- DCN base-address definitions such as `DCN_BASE__INST0_SEG2` and `BASE(...)` macros in consumers.
- Register access abstractions in AMDGPU DC and DMUB code.
- Hardware documentation or generation inputs that guarantee the numeric offsets match the ASIC.

All visible `_BASE_IDX` values are `2`, so any consumer using these macros must provide a valid base segment 2. A mismatch between base segment values and these offsets would shift every register access in this chunk to the wrong address range.

## Integration Points

Key integration points by subsystem:

- DPP/color: gamma, blend gamma, shaper, 3D LUT, HDR multiplier, and color-memory power control programming.
- OPP/output: FMT output format controls, dithering, clamp, 420/422 behavior, DPG test patterns, OPPBUF, OPP pipe control, and OPP CRC readback.
- OPTC/OTG: timing programming, vblank interrupts, update locks, global sync, DRR, CRC windows, snapshots, stereo/interlace state, and DSC timing alignment.
- ODM: multi-pipe output-merger input routing, format, width, and memory configuration.
- DIO/link: DDC/I2C EDID access, HPD interrupt/sense handling, AUX transactions, link encoder reset/fast training, and DIO clock/power controls.
- Perfmon: DC performance counter selection and readback for DPP, OPP, and DIO blocks.
- DMUB: firmware-side or DMUB-mediated register offset tables for DCN 3.0/3.0.2 paths that include this offset header.

## Risks and Failure Modes

- Incorrect numeric offsets can silently write the wrong hardware register, causing display corruption, failed modesets, broken link training, missed hotplug interrupts, bogus CRCs, or hangs.
- Missing or mismatched `_BASE_IDX` macros break `BASE(mm..._BASE_IDX) + mm...` expansion or send accesses to the wrong segment.
- Instance repetition creates copy/paste or generator risks: one bad stride among `FMTn`, `OTGn`, `HPDn`, or `DP_AUXn` instances could affect only a subset of pipes/connectors and be hard to detect.
- This chunk starts and ends mid-block. The first visible `CM5` macros require earlier chunk context for the start of the DPP5 color-management block, and `DP_AUX2` requires later chunk context for full AUX2 coverage.
- Field definitions are not present here. A correct offset with an incorrect shift/mask definition in the companion header can still corrupt register programming.
- Some register names are shared conceptually across DCN generations but not always at the same offset. Cross-generation reuse must include the correct generated header for the active ASIC family.
- Power-gated or clock-gated blocks such as DPP/OPP/DIO can reject or lose register accesses unless higher-level code sequences power and clocks correctly before using these offsets.

## Test Signals

Useful validation signals for this chunk include:

- Build-time success for DCN 3.0 and DCN 3.0.2 display code that includes `dcn_3_0_0_offset.h`; missing macro names should fail compilation in register-list initializers.
- Static generated-header checks that every `mm...` register macro in this range has exactly one matching `_BASE_IDX`, and that visible base indices are expected for DCN segment 2.
- Display modeset smoke tests across all six pipes to exercise `OTG0` through `OTG5`, `FMT0` through `FMT5`, and `OPP_PIPE_CRC0` through `OPP_PIPE_CRC5` address tables.
- CRC tests using OPP pipe CRC and OTG CRC registers to confirm readback changes with known test patterns.
- Hotplug and HPD interrupt tests across six connectors where available, checking `HPD0` through `HPD5` sense and interrupt behavior.
- DDC/EDID and DisplayPort AUX transaction tests covering `DC_I2C_*`, `DP_AUX0`, `DP_AUX1`, and, after later chunk completion, full `DP_AUX2` and remaining AUX instances.
- Color pipeline tests that program DPP5 blend gamma, shaper LUT, and 3D LUT state and compare output CRCs or visual/colorimetry results.
- Suspend/resume and power-gating tests that verify DPP/OPP/OTG/DIO register state is restored through higher-level DC programming.

## Cross-Chunk Notes

This is only one chunk of a larger generated header. The final per-file research report should merge this with adjacent chunks to recover:

- Header-level include guards and generation provenance.
- Earlier DCN base segment and register-block definitions.
- The full DPP5 block start before line 7719.
- The remainder of `DP_AUX2` and any later DIO/AUX/link-encoder blocks after line 10374.
- Whole-file comparisons against companion shift/mask headers and DCN 3.0 resource table construction.
