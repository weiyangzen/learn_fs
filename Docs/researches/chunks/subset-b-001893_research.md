# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h lines 7704-10281

## Scope

This chunk is a middle slice of the generated DCN 3.1.6 register offset header `dcn_3_1_6_offset.h`. It contains C preprocessor constants only: `reg*` address offsets, matching `reg*_BASE_IDX` segment selectors, and address-block comments. There are no C functions, structs, enums, branches, allocations, or software-owned data structures in this range.

The slice starts on the `_BASE_IDX` macro for the preceding `regMPC_OUT1_CSC_C33_C34_B` definition, then covers MPC output CSC tail registers, the MPC RMU shaper/3D LUT blocks, four ABM/OPP instances, OPP formatter and CRC surfaces, ODM input blocks, four OTG timing generators, miscellaneous OPTC/OPP registers, five HPD blocks, DP0/DIG0 link-encoder registers, and the beginning of DP1. It ends at `regDP1_DP_SEC_FRAMING2` before that register's `_BASE_IDX`, so both boundaries depend on neighboring chunks for complete macro pairs.

## Purpose And Hardware Surface

The purpose of this header range is to provide the address side of the AMDGPU Display Core hardware ABI for DCN 3.1.6. Driver code and DMUB register tables use these macros with the companion `dcn_3_1_6_sh_mask.h` field definitions to calculate MMIO addresses and field encodings without embedding raw offsets at call sites.

Major hardware areas represented here:

- MPC output color-space conversion and output CSC debug registers. The chunk finishes `MPC_OUT2` and `MPC_OUT3` CSC mode/matrix coefficient A/B registers and exposes `MPC_OCSC_TEST_DEBUG_INDEX/DATA`.
- `dce_dc_mpc_mpc_rmu_dispdec` registers. Two RMU instances provide shaper LUT programming, RAM A/B start/end/region tables, 3D LUT index/data windows, 30-bit data, read/write control, output normalization, and RGB output offsets.
- `dce_dc_opp_abm[0-3]_dispdec` registers. Four ABM blocks define PWM levels, ABM control, IPCSC coefficient selection, ACE slopes/thresholds, histogram/luma statistics readback, sample-rate controls, histogram bin metadata/results, and backlight master locks.
- OPP per-pipe output blocks for instances 0-3: display pattern generator (`DPG`), formatter (`FMT`), OPP buffer (`OPPBUF`), pipe control, and pipe CRC registers.
- DSC forwarding/control surfaces: `DSCRM0..2_DSCRM_DSC_FORWARD_CONFIG`, `OPP_TOP_CLK_CONTROL`, `OPP_ABM_CONTROL`, and `DC_PERFMON16_*`.
- ODM and OTG blocks. `ODM0..3` select OPTC input source/format/width/clock/memory settings. `OTG0..3` define timing, trigger, status, snapshot, interrupt, update-lock, CRC, static-screen, 3D, GSL, DRR, DTO, DSC start-position, pipe-update, and spare registers.
- Miscellaneous OPTC/OPP registers: `DWB_SOURCE_SELECT`, `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_*`, `OPTC_MISC_SPARE_REGISTER`, and `DC_PERFMON17_*`.
- DIO hotplug and link encoder blocks. `HPD0..4` expose interrupt status/control, control, and toggle filtering. `DP0` and the beginning of `DP1` cover DisplayPort link/video/DPHY/secondary-data/audio/info/GSP controls, and `DIG0` covers DIG front/back-end, HDMI, AFMT, TMDS, CRC, test-pattern, FIFO, and force-disable registers.

## Important Definitions

The exported API is the generated macro convention:

- `reg<NAME>` is the DCN 3.1.6 register offset.
- `reg<NAME>_BASE_IDX` selects the base segment used by `BASE(reg<NAME>_BASE_IDX)`.
- Address comments such as `// addressBlock: dce_dc_optc_otg0_dispdec` identify the hardware block whose registers follow.
- Runtime code normally computes an MMIO address as `BASE(regFOO_BASE_IDX) + regFOO`, as shown by `REG_OFFSET_EXP` in `display/dmub/src/dmub_dcn316.c`.

Important register families in this chunk:

- `regMPC_OUT2_CSC_*` and `regMPC_OUT3_CSC_*` provide output CSC mode and packed matrix coefficient addresses for two MPC outputs. Each output has A and B coefficient banks for rows `C11_C12` through `C33_C34`.
- `regMPC_RMU_CONTROL`, `regMPC_RMU_MEM_PWR_CTRL`, `regMPC_RMU0_*`, and `regMPC_RMU1_*` describe RMU control, memory power, two shaper LUTs, dual RAM region tables, and two 3D LUT programming windows from offsets `0x0680` through `0x0701`, all in base index 3.
- `regABM0_*` through `regABM3_*` repeat the same 60-register ABM layout at offsets `0x0e7a..0x0eb6`, `0x0ebb..0x0ef7`, `0x0efc..0x0f38`, and `0x0f3d..0x0f79`. The repeated stride maps independent ABM/OPP instances.
- `regDPG[0-3]_*`, `regFMT[0-3]_*`, `regOPPBUF[0-3]_*`, `regOPP_PIPE[0-3]_OPP_PIPE_CONTROL`, and `regOPP_PIPE_CRC[0-3]_*` repeat per-output-pipe control, formatting, buffering, test pattern, and CRC capture surfaces in base index 2.
- `regODM[0-3]_OPTC_*` define OPTC input-side global control, data source, data format, bytes per pixel, width, input clock, memory config, and spare registers.
- `regOTG[0-3]_OTG_*` are the largest group in this chunk. Each OTG instance has 105 registers covering horizontal/vertical totals, blank/sync timing, variable refresh totals, trigger controls, flow/stereo/interlace state, counters, snapshots, vertical interrupts, CRC windows/results/masks, static-screen detection, global sync, GSL, DRR, M/N DTO, request control, DSC start position, and pipe update status.
- `regHPD[0-4]_DC_HPD_*` provide five hotplug-detect interrupt/control/filter register sets.
- `regDP0_DP_*` includes DP link control, pixel format, MSA metadata, video timing/N/M, DPHY training/scrambling/CRC, secondary-data/audio/MSE/SST/MST controls, GTC sync, ALPM, and GSP controls. `regDIG0_*` maps the paired digital encoder/HDMI/TMDS block. The chunk then starts the equivalent `regDP1_DP_*` block at base address `0x400`.

## Control Flow And State Behavior

This header has no executable control flow. Runtime behavior appears only when Display Core, DMUB, or lower register helpers expand these macros into MMIO reads and writes.

A typical path is:

1. DCN316 support selects `dmub_srv_dcn316_regs`.
2. The register table expands names through `REG_OFFSET_EXP(reg_name)`.
3. `REG_OFFSET_EXP` uses the offset and base index from this header to calculate a physical register address.
4. Field packing/extraction comes from the companion `dcn_3_1_6_sh_mask.h` header.
5. Hardware latches, reports, clears, or samples the corresponding display state.

The state represented here is hardware state rather than persistent software state:

- Persistent configuration includes CSC matrices, RMU shaper/3D LUT contents, ABM PWM/user/target levels, ACE and histogram setup, formatter clamp/dither/420/422 controls, OPP buffer and pipe controls, ODM input routing, OTG timing totals, interrupt positions, update locks, global sync, DRR, DP link/stream configuration, HDMI/AFMT/TMDS setup, and HPD filtering.
- Volatile readback/status includes ABM current/final levels and histogram/luma results, OPP/OTG CRC results, OTG counters and positions, snapshot/status registers, perfmon counters, HPD interrupt/status bits, DP DPHY CRC/training/status, HDMI status, DIG FIFO status, and GSP double-buffer status.
- Side-effecting or sequencing-sensitive registers include LUT index/data windows, RMU/ABM memory power controls, ABM lock registers, OTG update/master locks, interrupt/status controls, counter resets, manual triggers, HPD interrupt acknowledge/control paths, DPHY training controls, DP secondary-data enables, and HDMI/AFMT packet controls.

The sequencing rules are not encoded in the offsets. Callers must still obey display power gating, clock availability, vblank/update-lock timing, double-buffering rules, link-training state, audio packet timing, HPD interrupt ordering, and instance ownership.

## Dependencies And Integration Points

This chunk depends on the companion field-layout header `dcn_3_1_6_sh_mask.h`; offsets from this file are useful only when paired with masks and shifts for the same register revision. It also depends on the base segment constants used by `BASE()` in DCN316 code. In `display/dmub/src/dmub_dcn316.c`, those base constants are `DCN_BASE__INST0_SEG0` through `DCN_BASE__INST0_SEG5`, and `REG_OFFSET_EXP` combines `BASE_IDX` plus offset to populate `dmub_srv_dcn316_regs`.

Known integration points include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which directly includes `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h` and builds the DCN316 DMUB register table.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_srv.c`, which selects `dmub_srv_dcn316_regs` for `DMUB_ASIC_DCN316`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c`, which maps the ASIC to `DMUB_ASIC_DCN316` and names the `amdgpu/dcn_3_1_6_dmcub.bin` firmware.
- DCN316 resource, clock-manager, link-encoder, timing-generator, ABM/backlight, audio/HDMI, HPD interrupt, and diagnostics code that uses generated register lists or DMUB table entries to program these hardware blocks indirectly.
- Cross-revision generated headers in the same `asic_reg/dcn` directory. Similar blocks exist for other DCN revisions, but the exact offsets, instance count, and base-index mapping must remain DCN 3.1.6-specific.

Because this file is generated, missing or misspelled macros often fail at compile time in register-list expansions. Wrong numeric offsets or base indices can compile cleanly and instead misdirect live MMIO accesses.

## Risks And Maintenance Notes

- Numeric drift from the authoritative DCN 3.1.6 register database is the main risk. A wrong offset can program a valid but unrelated register, especially in dense repeated OTG/OPP/DP blocks.
- Base-index drift is as dangerous as offset drift. Most MPC/RMU/ABM registers in this chunk use base index 3, while OPP/OPTC/DIO blocks use base index 2. Copying an offset without its matching `_BASE_IDX` changes the calculated MMIO segment.
- This chunk starts and ends on incomplete macro pairs. The merge lane should join it with adjacent chunks before making whole-file claims about `regMPC_OUT1_CSC_C33_C34_B` or `regDP1_DP_SEC_FRAMING2`.
- Repeated instance names are easy to confuse. `ABM0..3`, `DPG0..3`, `FMT0..3`, `OPPBUF0..3`, `OPP_PIPE_CRC0..3`, `ODM0..3`, `OTG0..3`, `HPD0..4`, and `DP0/DP1` use similar register names with shifted offsets.
- Timing-generator registers affect active display timing. Incorrect `OTG_*` totals, locks, trigger controls, vertical interrupt positions, or DRR ranges can cause blanking, underrun-like symptoms, missed vblank events, or broken variable refresh behavior.
- LUT and histogram programming registers are index/data style surfaces. Callers must sequence index, data, write-enable/readback, and lock registers correctly; offsets alone do not protect against stale or partial updates.
- HPD and link-encoder registers interact with external displays. Wrong HPD interrupt or DP training offsets can break hotplug detection, link training, MST/SST setup, secondary-data packets, audio, or ALPM/GSP behavior.
- HDMI/AFMT/TMDS registers are adjacent to DIG front/back-end controls. Mistaking packet-control, ACR, generic-packet, TMDS, or DIG disable addresses can create display audio or signaling failures that are hard to attribute to an offset error.
- OPP and OTG CRC registers are diagnostic but are also used for validation. Incorrect offsets may produce false CRC mismatches or mask real display corruption.

## Test Signals

Useful validation signals for changes touching this chunk include:

- Full AMDGPU Display Core build with DCN316 enabled. This catches missing macro names, malformed generated definitions, and broken include dependencies.
- Regeneration or static diff against the authoritative DCN 3.1.6 register source, checking both `reg*` offsets and `reg*_BASE_IDX` values.
- Cross-revision comparison against neighboring DCN offset headers for blocks expected to be layout-compatible, while confirming DCN316-specific deltas are intentional.
- Boot/runtime testing on DCN 3.1.6 hardware with DMUB enabled, verifying that `dmub_srv_dcn316_regs` initializes and basic display bring-up succeeds.
- Display timing tests across multiple pipes: mode set, vblank interrupt delivery, variable refresh/DRR behavior, GSL/global sync if available, OTG update-lock behavior, and CRC readback sanity.
- Backlight/ABM tests: PWM level changes, ABM enable/disable, histogram/luma readback, no stuck ABM locks or update-pending state, and stable brightness transitions.
- Color pipeline tests: CSC updates, RMU shaper/3D LUT programming, formatter dither/clamp/420/422 behavior, and visual or CRC confirmation that only intended pipes are affected.
- Hotplug/link tests for HPD0-4 and DP0/DP1: connect/disconnect interrupts, DP link training, MST/SST streams, secondary-data packets, audio infoframes/ACR, HDMI/TMDS output, and ALPM/GSP behavior where supported.
- Register dumps before and after representative operations. Calculated addresses should land in the expected base segment and adjacent instance offsets should not change unexpectedly.

## Open Questions For Merge

- Earlier chunks are needed to describe the beginning of the MPC OUT CSC table and the complete header-level include guard/license context.
- Later chunks are needed to finish `regDP1_DP_SEC_FRAMING2_BASE_IDX` and the remaining DP/DIG/HDMI/audio blocks for other link instances.
- This chunk documents register addresses only. The final merged report should connect these addresses to actual register-list consumers and field semantics from `dcn_3_1_6_sh_mask.h` without inferring bit-level behavior from offsets alone.
