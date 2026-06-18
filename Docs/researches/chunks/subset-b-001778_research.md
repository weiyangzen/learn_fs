# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_offset.h lines 2681-5260

## Scope

This chunk is a generated DCN 3.0.3 register-offset slice from `dcn_3_0_3_offset.h`. It contains only C preprocessor definitions and address-block comments. There are no functions, structs, enums, local variables, or executable branches in the range. Its job is to expose the MMIO offset map for AMDGPU Display Core code that programs DCN 3.0.3 display pipelines.

The range begins inside the DPP0 color-management block at `mmCM0_CM_GAMCOR_LUT_CONTROL` and ends at `mmDIG1_HDMI_ACR_STATUS_1`. It covers 2,409 `#define mm...` lines: 1,205 register-offset macros and 1,204 matching `_BASE_IDX` macros inside the requested line range. The apparent one-macro imbalance is a chunk-boundary artifact: line 5260 contains `mmDIG1_HDMI_ACR_STATUS_1`, while its `mmDIG1_HDMI_ACR_STATUS_1_BASE_IDX` companion appears on line 5261, outside this work item.

## Purpose And Hardware Surface

The macros in this chunk provide register addresses for the DCN 3.0.3 display datapath. Driver code combines each register offset with a base segment selected by the corresponding `_BASE_IDX` macro. In the DCN303 resource code, helper macros such as `SR`, `SRI`, `SRII`, and `SRI2` expand names like `mmCM1_CM_CONTROL_BASE_IDX` and `mmCM1_CM_CONTROL` into absolute register addresses through `BASE(mm..._BASE_IDX) + mm...`. Companion field definitions in `dcn_3_0_3_sh_mask.h` provide the bit-level `_SHIFT` and `_MASK` values.

Major hardware areas represented in this slice:

- DPP0 color management tail: gamma-correction LUT control, RAM A/B piecewise gamma segment start/end/slope/base/offset/region registers, blend gamma, HDR multiplier, memory power, dealpha, coefficient format, shaper LUTs, 3D LUT, and debug index/data registers.
- DPP0 performance monitor: `DC_PERFMON7_*` counter control, state, interrupt/misc, and counter-value readout registers.
- DPP1 pipeline frontend: DPP top control/soft reset/CRC/host read, CNVC pixel format and pre-CSC/pre-degamma/pre-alpha controls, cursor color/control, DSCL scaler/filter/viewport/output sizing/memory-power controls, CM color-management registers mirroring the DPP0 color pipeline, and `DC_PERFMON8_*`.
- OPP0 and OPP1 output processing: formatter clamp, dynamic expansion, bit-depth/dither, side-by-side stereo, 4:2:0 and 4:2:2 controls; display pattern generator controls/status; OPP buffer controls; pipe controls; per-pipe CRC controls/results; common OPP clock and ABM control; DSC forward-config registers for two DSCRM instances; and `DC_PERFMON9_*`.
- OPTC timing/output controls: ODM0/ODM1 input/data format/bytes-per-pixel/width/memory registers, OTG0 and OTG1 timing generator registers, global sync and update-lock controls, vertical interrupt controls, CRC windows/data, dynamic refresh rate controls, DSC start position, pipe-update status, DWB/GSL source select, OPTC memory power, and `DC_PERFMON10_*`.
- DIO/link side registers: DDC/I2C control/arbitration/transactions/data/EDID detect, DIO scratch and power/clock/reset/generic interrupt registers, HPD0/HPD1 status/control/filter/fast-train registers, `DC_PERFMON11_*`, AUX0/AUX1 control/status/data/DPHY/GTC/wake registers, DIG0/DIG1 VPG generic packet and info packet windows, AFMT audio/infoframe/CRC/status/memory-power registers, DME control/memory control, DIG/HDMI packet/audio/ACR/test/CRC/frontend registers, and DP0 transport/link/secondary-data-packet/MST/MSA/MSO/DSC/ALPM/GSP registers.

## Important Definitions

The important API is the macro naming contract, not a callable function interface:

- `mm<REGISTER>` gives the generated register offset within the ASIC's display register space.
- `mm<REGISTER>_BASE_IDX` gives the DCN base segment index used by generated address helpers. In this range the value is consistently `2` for all complete pairs, matching the DCN display segment selected by the including code.
- `// addressBlock: ...` and `// base address: ...` comments document hardware grouping and instance base offsets. They are consumed by humans and generation/reconciliation tools, not by the C compiler.

Representative definition families:

- `mmCM0_*` and `mmCM1_*` define color-management state for DPP instances 0 and 1. The CM families include post-CSC and gamut-remap matrix registers, gamma correction LUT index/data/control, RAM A/B region programming, blend gamma, shaper LUT, 3D LUT, and memory-power/status registers.
- `mmCNVC_CFG1_*`, `mmCNVC_CUR1_*`, and `mmDSCL1_*` define DPP1 input conversion, cursor, and scaler control offsets. These are used when DC builds the DPP1 register table in `dcn303_resource.c`.
- `mmFMT0_*`, `mmFMT1_*`, `mmDPG*`, `mmOPPBUF*`, `mmOPP_PIPE*`, and `mmOPP_PIPE_CRC*` define the output pixel processor surface for two output pipes.
- `mmODM*` and `mmOTG*` define timing-generator and output-data-mapping state for two timing generators. OTG registers include timing totals/blanks/syncs, vertical totals, frame and position counters, update locks, interrupt positions, CRC programming/readout, static-screen and 3D structure state, global sync, DRR, and DSC integration.
- `mmDC_I2C_*`, `mmHPD*`, `mmDP_AUX*`, `mmDIG*`, `mmVPG*`, `mmAFMT*`, `mmDME*`, and `mmDP0_*` define link-side control for DDC/I2C, hotplug, AUX transactions, stream encoding, HDMI/DP packet generation, audio formatting, and DisplayPort transport.
- `mmDC_PERFMON7_*` through `mmDC_PERFMON11_*` define repeated display performance-monitor blocks associated with DPP, OPP, OPTC, and DIO blocks.

## Control Flow And State Behavior

There is no local control flow in this header. Runtime behavior is created by other driver layers that expand these macros into register tables and then perform MMIO read/modify/write operations through AMD Display Core helpers.

The typical flow is:

1. DCN303 initialization includes this header and `dcn_3_0_3_sh_mask.h`.
2. Resource constructors build per-block register tables with macros such as `DPP_REG_LIST_DCN30`, `OPP_REG_LIST_DCN30`, `OPTC_COMMON_REG_LIST_DCN3_0`, `AUX_COMMON_REG_LIST0`, `SE_DCN3_REG_LIST`, `VPG_DCN3_REG_LIST`, `AFMT_DCN3_REG_LIST`, and `I2C_HW_ENGINE_COMMON_REG_LIST`.
3. Block constructors store the resulting addresses in typed register structs for DPPs, OPPs, timing generators, stream encoders, VPG/AFMT, AUX, I2C, HPD, DIO, and related blocks.
4. Runtime display code programs those hardware blocks while setting modes, enabling planes, applying color transforms, setting cursors, training links, sending AUX/I2C transactions, generating HDMI/DP packets, servicing interrupts, or reading CRC/perfmon/debug state.

State represented by this chunk is hardware-backed:

- CM/CNVC/DSCL/DPP registers persist per-plane color conversion, cursor, scaling, memory-power, CRC, and debug state until updated, reset, or power-gated.
- OPP/FMT/DPG/OPPBUF/CRC registers persist output format, dithering/clamping, pattern generation, output buffer, and output CRC state.
- ODM/OTG registers persist timing, update-lock, global sync, dynamic refresh, CRC, DSC, interrupt-position, and pipe-update state for the timing generator.
- DIO/I2C/AUX/HPD/DIG/DP/VPG/AFMT/DME registers persist link-side configuration and expose volatile status for hotplug, AUX/I2C progress, FIFO/CRC/status, audio packet state, DP transport state, and packet-transmission status.
- Perfmon registers persist counter configuration and expose volatile counter values and interrupt status.

The header does not enforce sequencing. Callers must still respect hardware ordering such as locking updates before timing changes, programming scaler/color blocks before enabling a pipe, waiting for AUX/I2C completion, acknowledging or masking HPD/interrupt state appropriately, and avoiding live link/stream packet changes outside safe update windows.

## Dependencies And Integration Points

This offset slice is integrated through several DCN303 paths:

- `display/dc/resource/dcn303/dcn303_resource.c` includes `dcn_3_0_3_offset.h` and uses helper macros to build register tables for DIO, VPG, AFMT, audio, stream encoders, DPPs, OPPs, OPTCs, AUX engines, I2C engines, link encoders, MCIF writeback, MMHUBBUB, MPC, DSC, and hardware sequencing.
- `display/dc/irq/dcn303/irq_service_dcn303.c` includes the same offset and mask headers. It uses generated register names through `SRI` and `IRQ_REG_ENTRY` to describe HPD, vblank, vline, flip, and vupdate interrupt enable/status/ack registers. This chunk directly includes HPD0/HPD1 and OTG0/OTG1 offsets that participate in those tables.
- `display/dmub/src/dmub_dcn303.c` includes this header for common DMUB register offset construction. The DMCUB registers themselves are outside this particular line range, but the integration pattern is the same generated-offset plus generated-mask model.
- Common block headers such as `dcn30_dpp.h`, `dce_opp.h`, `dcn10/dcn10_optc.h`, `dcn20/dcn20_optc.h`, `dce_aux.h`, and `dce_stream_encoder.h` define the register-list macros that expand against this file's `mm...` names.
- Companion generated headers are required: `dcn_3_0_3_sh_mask.h` supplies field masks/shifts, and IP segment headers such as `sienna_cichlid_ip_offset.h` supply the base address macros used by `BASE(mm..._BASE_IDX)`.

The chunk is source-tree-aligned with a DCN303 resource capability of two timing generators, two OPPs, two video planes, two audio instances, two stream encoders, two DDC engines, one DWB, and two DSC instances. That matches the instance coverage visible here for DPP0/DPP1, OPP0/OPP1, OTG0/OTG1, HPD0/HPD1, AUX0/AUX1, DIG0/DIG1, VPG0/VPG1, AFMT0/AFMT1, and DME0/DME1.

## Risks And Maintenance Notes

- Generated-header drift is the primary risk. A wrong offset or stale `_BASE_IDX` value can make otherwise-correct display code write the wrong MMIO register.
- Instance naming is dense and repetitive. Confusing `CM0` with `CM1`, `OTG0` with `OTG1`, `DIG0` with `DIG1`, `HPD0` with `HPD1`, or `AUX0` with `AUX1` can route programming to the wrong pipe or connector.
- Many register families are mirrored but not always contiguous. Code should rely on generated names and register-list macros, not arithmetic assumptions between instances.
- The requested chunk begins and ends mid-block. It starts after earlier DPP0 CM setup definitions and ends before the `mmDIG1_HDMI_ACR_STATUS_1_BASE_IDX` line and later DIG1 registers. Merge/reconciliation should treat this as chunk slicing, not as missing definitions in the source file.
- Several registers control memory power, resets, update locks, CRC/test modes, and link transaction state. Misprogramming these can cause blank displays, stuck AUX/I2C transactions, bad hotplug behavior, link-training failures, incorrect CRC validation, or color/scaler corruption.
- Perfmon and debug registers are low-level diagnostic surfaces. Incorrect use can perturb performance counters or read misleading status if counters are not stopped/sampled in the expected sequence.
- Because these are preprocessor macros, there is no type safety. A register offset from this header can be accidentally paired with a mask or shift from a different register and still compile in generic helper code.

## Test Signals

Useful validation signals are compile-time expansion, register-table sanity, and hardware/display smoke coverage:

- Build AMDGPU DC with DCN303 enabled. This proves the register-list macros in resource, IRQ, stream encoder, DPP, OPP, OPTC, AUX, I2C, HPD, VPG, AFMT, and audio code still resolve every referenced `mm...` symbol.
- Static generated-header checks should verify each complete in-range `mm<REGISTER>` definition has a matching `_BASE_IDX` definition and that all referenced names also have matching field definitions in `dcn_3_0_3_sh_mask.h`.
- Mode-set and page-flip smoke tests should exercise DPP color/scaler setup, OPP formatter setup, OTG timing, update locks, vblank/vline/vupdate, and pipe-update status.
- Color-management tests should apply gamma, degamma, gamut remap, shaper LUT, blend gamma, 3D LUT, CSC, HDR multiplier, and cursor color paths on both available DPP instances.
- Link tests should cover HPD0/HPD1 plug/unplug, DDC/I2C EDID reads, AUX0/AUX1 transactions, DP link training, DP MSA/MST/secondary packet paths, HDMI generic/info/audio/ACR packet programming, and AFMT audio state.
- CRC and diagnostic tests should read DPP, OPP pipe, DIG output, and OTG CRC paths, plus display perfmon counters `DC_PERFMON7` through `DC_PERFMON11`.
- Power-management tests should exercise CM, DSCL, OBUF, OPTC/ODM, DIO, VPG, AFMT, and DME memory-power controls across suspend/resume and display on/off transitions.

## Chunk-Specific Summary

Lines 2681-5260 define a broad DCN 3.0.3 MMIO offset surface for the display pipeline from DPP color/scaler blocks through OPP, OPTC, DIO, AUX/I2C/HPD, stream encoder, HDMI/DP transport, VPG, AFMT, and DME blocks. The slice is not executable code; it is a generated hardware ABI used by AMDGPU Display Core register-table construction. Correctness depends on exact offset/base-index values, consistent instance naming, and matching field masks in the companion sh/mask header.
