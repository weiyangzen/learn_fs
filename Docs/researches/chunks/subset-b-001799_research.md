# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_offset.h lines 7671-10248

## Scope

This chunk is a generated AMD DCN 3.1.2 register-offset header slice. It contains no executable C logic, types, functions, storage objects, includes, allocation paths, or runtime branches. Its exported surface is 2,386 preprocessor definitions: 1,193 `reg...` register-offset macros and 1,193 paired `reg..._BASE_IDX` macros. The range spans 2,578 source lines and 48 generated `addressBlock` sections.

The chunk begins at the final `MPC_RMU0_3DLUT_OUT_OFFSET_B` offset pair, covers the full `MPC_RMU1` shaper/3DLUT offset group, four ABM/backlight instances, four OPP/DPG/FMT/OPPBUF/OPP pipe groups, ODM and OTG timing groups for instances 0-3, OPTC miscellaneous/perfmon registers, HPD instances 0-4, DP link instances 0-1, DIG/HDMI/TMDS instance 0, and most of DIG instance 1 through `DIG1_TMDS_CTL0_1_GEN_CNTL`. The next source line after this chunk continues `DIG1`.

Although the repository path includes `ceph-client`, this header is AMDGPU display-controller hardware metadata, not distributed filesystem code.

## Purpose

The purpose of this range is to map symbolic DCN 3.1.2 display register names to hardware offsets and base-index selectors. Runtime driver code should not hard-code these numeric offsets; it builds register tables from names such as `regOTG1_OTG_H_TOTAL` and `regDP0_DP_LINK_CNTL`, then combines each offset with its matching `reg..._BASE_IDX` through register helper macros.

The covered hardware areas are:

- MPC/RMU color-management registers for shaper LUT and 3D LUT programming.
- ABM/backlight registers for PWM levels, ambient/user/target/current brightness, adaptive brightness processing, ACE controls, luma/histogram sampling, grouped locks, and master locks.
- OPP output-pixel-processor blocks, including DPG, FMT, OPP buffer, pipe, pipe CRC, DSC rate-match, top-level OPP, and OPP perfmon registers.
- ODM and OTG/OPTC timing-generator blocks for display timing, vblank/vsync, vertical interrupts, update locks, CRC windows/results, stereo, trigger, global sync lock, DRR, DTO, DSC start position, and pipe-update status.
- HPD hotplug-detect registers for five physical connectors.
- DP and DIG encoder/link registers for DisplayPort link training, MSA/MST/MSO/DSC/secondary packets/audio, HDMI packets/audio clock regeneration, AFMT, TMDS, CRC, test patterns, and FIFO/status handling.

## Important APIs, Types, And Macros

There are no callable APIs in this chunk. The API surface is the generated macro namespace:

- `regREGISTER`: register offset within a hardware register aperture.
- `regREGISTER_BASE_IDX`: base-address segment selector for that register.
- `// addressBlock: ...` and `// base address: ...`: generated grouping comments that document the owning hardware block and replicated instance base.

Important macro families in this chunk:

- `regMPC_RMU1_SHAPER_*` and `regMPC_RMU1_3DLUT_*`: shaper control, per-channel offsets/scales, LUT index/data/write-enable mask, RAM A/B start/end controls, 34 region pairs for each RAM bank, 3D LUT mode/index/data/30-bit data, read/write control, output normalization, and RGB output offsets. The chunk also includes the final offset pair for `MPC_RMU0_3DLUT_OUT_OFFSET_B`.
- `regABM[0-3]_*`: repeated ABM/backlight layout with BL1 PWM level/duty-cycle controls, `DC_ABM1_*` control/ACE/histogram/luma/statistics/sample-rate/readback registers, panel mask, backlight current/target/final fractional registers, and master lock.
- `regDPG[0-3]_*`, `regFMT[0-3]_*`, `regOPPBUF[0-3]_*`, `regOPP[0-3]_*`, and `regOPP_PIPE_CRC[0-3]_*`: per-OPP data-path, formatter, buffer, and CRC offsets used by OPP register-list macros.
- `regDSCRM[0-2]_*`, `regOPP_*`, `regDWB_*`, and `regDC_PERFMON17_*`: DSC rate-match memory-power state, OPP memory power/reset/top controls, DWB clock control, and OPP/OPTC performance-counter offsets.
- `regODM[0-3]_*` and `regOTG[0-3]_*`: output data merger memory power/control and full per-OTG timing-generator offsets for timing totals, sync/blank windows, trigger controls, counters, status, update locks, interrupts, CRC windows/results, global sync, DRR, DTO, DSC, and pipe update status.
- `regHPD[0-4]_*`: hotplug interrupt status/control, HPD control, fast-train control, and toggle filter control.
- `regDP[0-1]_*`: DisplayPort link, video, DPHY, secondary packet/audio, MSE/SAT, MSA timing, MSO, DSC, DB, VBID, metadata, ALPM, GSP, and status offsets.
- `regDIG0_*` and `regDIG1_*`: digital front/back-end, output CRC, patterns, HDMI metadata/audio/infoframe/generic packets, HDMI ACR, AFMT, TMDS, and FIFO/status offsets. `DIG1` continues after this chunk.

## Control Flow

This header chunk has no runtime control flow. Runtime use is indirect:

1. DCN31-specific code includes `dcn_3_1_2_offset.h` with the matching `dcn_3_1_2_sh_mask.h` and ASIC base definitions.
2. Register-list macros paste symbolic names into offset lookups, pairing `reg...` with `reg..._BASE_IDX`.
3. Component-specific register tables are constructed for ABM, OPP, OTG, HPD, stream encoders, AUX/link encoders, DMUB, IRQ handling, and related DC blocks.
4. Runtime code uses helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, and `REG_GET` against those tables to program timing, link, audio/packet, backlight, color-management, and interrupt state.

Ordering and side-effect rules are not represented here. Higher-level display, link, DMUB, IRQ, power, and mode-setting code must still sequence clocks, resets, power gates, update locks, LUT programming, HPD debounce, DP training, HDMI packet setup, ABM locks, and interrupt acknowledgements correctly.

## State And Persistence Behavior

The file stores no software state and persists nothing. It describes addresses of MMIO-backed GPU display hardware state.

The represented hardware state includes:

- RMU shaper/3DLUT LUT RAM contents, index/data portals, bank/region descriptors, and output normalization/offset state.
- ABM PWM brightness state, target/current/final levels, ambient/user inputs, ACE coefficients, histogram/luma samples, grouped lock state, panel mask, and master lock state.
- OPP formatter, buffer, pipe CRC, DSC rate-match, memory-power, reset, and performance-monitor state.
- OTG/OPTC timing totals, sync/blank windows, counters, interrupts, update-lock state, CRC state, global sync lock windows, DRR range/change/window state, DTO constants, DSC start position, and pipe-update status.
- HPD interrupt/status/filter/fast-train state.
- DP/DIG link, training, stream, packet, audio, MST/MSO, DSC, HDMI, TMDS, AFMT, CRC, FIFO, and metadata state.

Some of these registers are normal read/write controls, while others are status, readback, sticky interrupt, clear/ack, self-clearing, indexed data, or lock registers. The offset macros do not encode access type, reset value, field width, or side effects; callers need the matching shift/mask header and hardware programming model.

## Dependencies And Integration Points

Primary generated dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h` supplies field shift/mask metadata for these offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/yellow_carp/yellow_carp_offset.h` supplies the ASIC base segment definitions used with `reg..._BASE_IDX`.

Observed direct include sites for the DCN 3.1.2 offset/mask pair:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn31/irq_service_dcn31.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn31.c`

Important integration patterns:

- `dcn31_resource.c` builds `abm_regs`, `vpg_regs`, `afmt_regs`, `stream_enc_regs`, `opp_regs`, `aux_engine_regs`, and DWB/HPD/link-related register tables from generated register-list macros. The ABM, OPP, HPD, DP/DIG, and timing names in this chunk feed those tables.
- `dmub_dcn31.c` defines `REG_OFFSET_EXP(reg_name)` as `BASE(reg##reg_name##_BASE_IDX) + reg##reg_name`, then expands DMUB register tables from this generated namespace.
- `irq_service_dcn31.c` includes this header with the matching masks so IRQ code can map and program interrupt/status registers for HPD, OTG/vblank/vline/vupdate, page flips, and DMUB outbox events.
- DC helper headers and common block implementations consume these offsets through register-list macros for OPP (`OPP_REG_LIST_DCN30`), ABM (`ABM_MASK_SH_LIST_DCN30` paired with ABM register lists), HPD (`HPD_REG_LIST`), stream encoders, AFMT/VPG, and DIO/link encoder logic.

## Risks And Edge Cases

- Offset metadata is hardware ABI. A wrong numeric offset or `_BASE_IDX` compiles cleanly but can redirect reads/writes to the wrong register or IP segment, causing blank displays, bad timing, corrupt color, bad brightness, link-training failure, audio/packet regressions, interrupt storms, or resume failures.
- The chunk starts and ends inside logical groups. It begins with only the final `MPC_RMU0_3DLUT_OUT_OFFSET_B` pair, and it ends before the last `DIG1` TMDS/version/force-disable offsets. Whole-file conclusions must merge adjacent chunks.
- Repeated register families are copy-sensitive. ABM0-3, OPP0-3, ODM0-3, OTG0-3, HPD0-4, DP0-1, and DIG0-1 differ largely by instance number and base offset; an instance drift can break only multi-display, connector-specific, or higher-pipe configurations.
- LUT and indexed data registers are stateful. Incorrect RMU shaper/3DLUT offsets can corrupt color only when HDR, gamma, shaper, or 3D LUT paths are exercised.
- ABM registers combine backlight control, histogram readback, ACE curves, update locks, and firmware-managed behavior. Incorrect offsets can produce brightness jumps, flicker, stuck locks, bad histogram data, or suspend/resume divergence.
- OTG and DP/DIG blocks contain timing, interrupt, and packet registers with strict sequencing requirements. Address correctness alone does not protect update-lock, vblank, DP training, MST/MSO allocation, DSC, secondary packet, HDMI ACR, or TMDS programming order.
- HPD and interrupt status/control registers may have sticky or write-one-to-clear behavior. Treating them as ordinary storage can lose events or leave interrupts asserted.
- Some offsets in this file use base index `3` for display/MMIO-style blocks, while DIO DP/DIG/HPD blocks use base index `2`. Pairing an offset with the wrong base-index selector is as damaging as a wrong offset.

## Test Signals

Useful validation combines compile-time checks, generated-header comparison, and hardware exercise:

- Build AMDGPU/DC with DCN31 enabled. Missing or renamed macros should fail while expanding resource, DMUB, IRQ, OPP, ABM, HPD, DP/DIG, and timing-generator register lists.
- Mechanically verify that every non-`_BASE_IDX` `reg...` macro in lines 7671-10248 has an immediately matching `reg..._BASE_IDX` macro. This chunk has a balanced 1,193/1,193 split.
- Diff the chunk against AMD's authoritative DCN 3.1.2 register database and adjacent DCN versions where layouts should be compatible.
- Exercise RMU color paths with shaper LUT and 3D LUT programming, HDR/gamma transitions, modesets, plane updates, and suspend/resume.
- Exercise ABM/backlight on eDP panels: user brightness changes, ABM level changes, ambient-level input, PWM fraction/current/target/final readback, histogram/ACE readback, panel-mask selection, lock/unlock paths, and resume restoration.
- Exercise OPP/OTG paths with multi-pipe and multi-display modesets, vblank/vline/vupdate IRQs, update locks, DRR/VRR changes, CRC capture, stereo/interlace where supported, DSC start position, and pipe-update status.
- Exercise HPD and DP/DIG paths: hotplug/unplug, HPD debounce, DP link training and retraining, MST/SAT/MSO, DSC over DP, ALPM/GSP where supported, HDMI modes, HDMI audio/ACR, infoframes/generic packets, AFMT, TMDS, and output CRC/test-pattern paths.
- Monitor kernel logs and display diagnostics for DMUB timeouts, IRQ storms, missed HPD events, blank display, bad timings, page-flip timeout, underflow, bad color, audio loss, malformed infoframes, brightness flicker, and resume regressions.

## Cross-Chunk Notes

The previous chunk is required for complete `MPC_RMU0` coverage. The next chunk is required for the rest of `DIG1` and the following `DP2` register block. The final per-file research document should reconcile this chunk with neighboring chunks before making claims about complete RMU, DIG, DP, or DCN 3.1.2 offset-header coverage.
