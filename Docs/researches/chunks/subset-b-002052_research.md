# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_0_offset.h lines 5275-7886

## Purpose

This chunk is generated DCN 3.5 display register offset data for the AMDGPU display stack. It defines `reg...` address offsets and matching `reg..._BASE_IDX` selectors used to build absolute MMIO addresses as `ctx->dcn_reg_offsets[BASE_IDX] + reg...`. The range is not executable code; it is a hardware-address contract consumed by DC resource construction, IRQ setup, GPIO/DDC/HPD translation, AUX engines, DMUB register lookup, and low-level display block programming.

The requested line range begins in the middle of `dce_dc_dpp2_dispdec_cnvc_cfg_dispdec` and ends in the middle of `dce_dc_dio_dp_aux4_dispdec`. Inside the complete requested range, the major covered blocks are DPP pipe 2/3 color, cursor, scaler, and perfmon registers; OPP/FMT/DPG/OPPBUF/CRC/DSCRM blocks for output pipes 0-3; OPTC/ODM/OTG timing-generator blocks 0-3; DIO I2C, misc link, HPD, perfmon, and DP AUX blocks 0-4.

## Important Macros and Register Groups

- DPP2/DPP3 conversion and color path: `regCNVC_CFG2_*` partial at the start, `regCNVC_CUR2_*`, `regDSCL2_*`, `regCM2_*`, `regDPP_TOP3_*`, `regCNVC_CFG3_*`, `regCNVC_CUR3_*`, `regDSCL3_*`, and `regCM3_*`. These provide offsets for pixel format, alpha/keying, pre-CSC, cursor color/control, scaler coefficient RAM and ratios, line-buffer controls, memory power controls, color matrices, gamut remap, 3D LUT, degamma/regamma, gamma correction, bias/scale, and debug index/data registers.
- DPP perfmon: `regDC_PERFMON13_*` for DPP2 and `regDC_PERFMON14_*` for DPP3. Each block has counter control/state, monitor control, current-value, high, and low counter registers.
- OPP pipe instances 0-3: `regFMT{0..3}_*`, `regDPG{0..3}_*`, `regOPPBUF{0..3}_*`, `regOPP_PIPE{0..3}_OPP_PIPE_CONTROL`, and `regOPP_PIPE_CRC{0..3}_*`. These cover output formatter clamp/dynamic-expansion/bit-depth/pixel-encoding/422 controls, DisplayPort generator controls, OPP buffering, pipe enable/control, and CRC capture/result registers.
- Shared OPP and DSC-remap support: `regOPP_TOP_CLK_CONTROL`, `regOPP_ABM_CONTROL`, `regDSCRM{0..3}_DSCRM_DSC_FORWARD_CONFIG`, and `regDC_PERFMON16_*`.
- ODM and OTG timing-generator instances 0-3: `regODM{0..3}_OPTC_INPUT_*` and large `regOTG{0..3}_*` groups. The OTG groups define timing totals and blank/sync windows, dynamic refresh rate min/max/control registers, vertical interrupt positions, trigger controls, CRC windows/results, GSL synchronization, stereo/3D controls, clock controls, status/readback, DSC start, and spare/debug registers.
- OPTC misc and perfmon: `regGSL_SOURCE_SELECT`, `regODM_MEM_PWR_CTRL`, `regOPTC_CLOCK_CONTROL`, `regOPTC_INPUT_CLOCK_CONTROL`, `regOPTC_DATA_SOURCE_SELECT`, `regOPTC_SEG{0,1}_SRC_SEL`, `regOPTC_DATA_FORMAT_CONTROL`, `regOPTC_MISC_SPARE_REGISTER`, and `regDC_PERFMON17_*`.
- DIO DDC/I2C: `regDC_I2C_*` defines software/hardware I2C control, arbitration, data, setup/speed, transaction, status, mask, DDC EDID timing, pin select, and interrupt registers.
- DIO link/misc and HPD: `regDIO_DCN_STATUS`, `regDIO_MEM_PWR_CTRL`, `regDIO_LINK*_CNTL`, and `regHPD{0..4}_DC_HPD_*` define display link status/control and hotplug detect status, interrupt control, control, fast training, and toggle filter offsets.
- DIO perfmon and AUX: `regDC_PERFMON18_*` plus `regDP_AUX{0..4}_AUX_*`. AUX instances define AUX channel control, software control/status/data, link-service status/data, DPHY TX/RX control/status, GTC sync control/status, and PHY wake control. `DP_AUX4` is partial in this chunk; its remaining offsets continue after line 7886.

Every defined register normally appears as a pair: the offset macro and a `_BASE_IDX` macro. In this chunk almost all `_BASE_IDX` values are `2`, tying these display blocks to DCN base segment 2; the explicit address-block comments also show per-instance local base spacing such as OPP `0x0/0x168/0x2d0/0x438`, OTG `0x0/0x200/0x400/0x600`, HPD `0x0/0x20/...`, and AUX `0x0/0x70/...`.

## Integration Points

The primary consumer pattern is the DCN register initializer macros in `display/dc/resource/dcn35` and `display/dc/resource/dcn351`. Their `SRI`, `SRII`, `SRI_ARR`, and related macros expand token-pasted names such as `regOTG2_OTG_V_TOTAL_BASE_IDX` and `regOTG2_OTG_V_TOTAL` into absolute offsets. `dcn351_resource_construct()` then creates HUBP, DPP, OPP, timing generator, AUX, I2C, DSC, ABM, and related resources using static register tables built from these macros.

IRQ setup also depends on these names. `display/dc/irq/dcn351/irq_service_dcn351.c` uses `SRI(reg_name, block, id)` to derive HPD, vblank, vline, page-flip, and other interrupt register addresses. For this chunk, the `HPD{0..4}` and `OTG{0..3}` offsets are the relevant pieces for connector hotplug and timing interrupt routing.

DMUB code uses the same offset/header convention. `display/dmub/src/dmub_dcn35.c` includes `dcn_3_5_0_offset.h` and `dcn_3_5_0_sh_mask.h`, then expands register offsets with `REG_OFFSET_EXP(reg_name) = BASE(reg..._BASE_IDX) + reg...`. The generic `dmub_reg.h` helpers (`REG_READ`, `REG_WRITE`, `REG_UPDATE`, `REG_GET`) operate on the initialized offsets and field masks.

The offset header must stay synchronized with `dcn_3_5_0_sh_mask.h` and the register-list macros in resource headers. Offset macros define where a register lives; sh/mask macros define how fields inside that register are manipulated. A name mismatch between the two usually becomes a compile-time failure in token-pasted macros, while a wrong numeric offset can compile but program the wrong hardware register.

## Control Flow and State Behavior

This file has no runtime control flow, no functions, and no in-memory state of its own. Its state effect is indirect: at driver initialization, resource constructors fold these constants into per-block register tables. Later display operations mutate hardware state through those tables, including scaler programming, color matrices and LUTs, output formatting, timing generator setup, DRR updates, CRC capture, HPD interrupt ack/mask state, DDC transactions, AUX transactions, clock/power controls, and perf counters.

Persistence is hardware-resident only. Values written through the offsets persist in display hardware registers until reset, power gating, suspend/resume reinitialization, mode-set reprogramming, or another driver path overwrites them. The header itself contributes no saved state, serialization, or recovery logic.

## Dependencies

- AMDGPU DCN 3.5 base-offset discovery via `dc_context::dcn_reg_offsets`.
- `dcn_3_5_0_sh_mask.h` for field shifts and masks corresponding to the registers named here.
- DC resource macros and constructors in `display/dc/resource/dcn35` and `display/dc/resource/dcn351`.
- IRQ service macros in `display/dc/irq/dcn351`.
- DMUB register helper macros in `display/dmub/src/dmub_reg.h` and DCN 3.5 DMUB initialization in `dmub_dcn35.c`.
- Hardware-generation naming conventions: `reg<block><instance>_<register>` plus `reg..._BASE_IDX`.

## Risks

- Numeric offset drift is high impact. A wrong offset may silently program an unrelated display register, causing blank displays, bad color conversion, scaler artifacts, broken VRR/DRR timing, AUX/DDC failures, missed HPD events, CRC test failures, or power-management regressions.
- Instance spacing must remain exact. OPP, OTG, HPD, and AUX blocks are repeated with regular-looking but hardware-defined strides; copying an offset from the wrong instance can route programming to another pipe or connector.
- Partial chunks should not be interpreted as complete hardware blocks. `CNVC_CFG2` starts before line 5275 and `DP_AUX4` continues after line 7886.
- `_BASE_IDX` mismatches are especially dangerous on SoCs with runtime-populated base arrays. Most macros here use segment `2`; an incorrect segment could move accesses to a completely different IP aperture.
- Generated headers are brittle under manual edits. Token-pasted consumers require exact macro spelling, so renames or omissions can break builds. Incorrect but present macros can evade compile-time detection.

## Test Signals

- Compile coverage for DCN 3.5/3.5.1 resource, IRQ, GPIO, AUX, and DMUB objects is the first signal; token-pasted macro use catches missing or misspelled offsets.
- Boot and probe on DCN 3.5-class hardware should create all DPPs, OPPs, timing generators, AUX engines, and I2C engines without `failed to create ...` errors from resource construction.
- Display mode-set tests across all four timing generators should verify stable scanout, correct H/V timing, vblank/vline interrupts, DRR/VRR behavior, and no timing-generator register-access faults.
- Connector tests should cover HPD plug/unplug and HPD RX IRQ behavior on all exposed HPD instances.
- DDC/AUX tests should read EDID and perform DisplayPort AUX transactions across all physical links, including AUX instance 4 whose block crosses the chunk boundary.
- Visual validation should include color-management and scaler paths: cursor rendering, CSC/gamut/regamma/3D LUT behavior, scaling ratios/taps, output formatter depth/encoding, and CRC capture/readback.
- Perfmon/debug smoke tests can validate the `DC_PERFMON13/14/16/17/18` offsets by enabling counters and observing sane counter progression.
