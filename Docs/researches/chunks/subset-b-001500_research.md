# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h lines 3029-6046

## Purpose

This chunk is the large middle section of AMD's generated DCE 10.0 register address header. It defines C preprocessor constants for display-engine register addresses; it is not executable driver logic. The macros are consumed by DCE 10.0 AMDGPU and Display Core code to read, write, or compute per-pipe/per-link MMIO addresses.

The range starts in the middle of the display controller pipe, or DCP, color-management block and runs through the legacy VGA register aliases. It covers:

- DCP pipe instances 0-5 for gamut remap, dithering, cursor registers, display LUT access, CRC/debug, graphic/overlay stereo flip, hardware rotation, XDMA underflow detection, regamma, and alpha control.
- Digital encoder instances 0-6 for front-end/output clock/test/FIFO controls, HDMI registers, AFMT audio and InfoFrame registers, TMDS/LVDS controls, and indirect `ixTMDS_DEBUG*` entries.
- The DMCU microcontroller register block, including firmware, RAM, interrupt, mailbox, DPRX, and performance-monitor registers.
- DisplayPort link, video, PHY, secondary-data, multi-stream, and front-end control registers replicated across DP0-DP6, plus AUX channel registers replicated across AUX0-AUX5 and indirect `ixDP_AUX_DEBUG_*` entries.
- DVO, frame-buffer compression, formatter, line-buffer, multi-view pipeline, scaler, color-management, uniphy graphics-plane, CRC/debug, and legacy VGA/VGA-indexed register address definitions.

This header chunk supplies addresses only. Bit-level field names, masks, and shifts are defined in the companion DCE 10.0 mask header, while runtime sequencing lives in AMDGPU and DC source files.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this chunk. The important interface is the generated macro namespace:

- `mm...` macros name direct MMIO register offsets, for example `mmREGAMMA_CONTROL`, `mmDIG0_DIG_FE_CNTL`, `mmDP0_DP_DPHY_CNTL`, `mmDP_AUX0_AUX_CONTROL`, `mmLB0_LB_DATA_FORMAT`, `mmSCL0_SCL_MODE`, `mmUNP_GRPH_ENABLE`, and `mmVGA_RENDER_CONTROL`.
- Instance-specific macros map the same logical register to per-pipe or per-link addresses. DCP, LB, and SCL display pipes use the repeating base pattern `0x1a..`, `0x1c..`, `0x1e..`, `0x40..`, `0x42..`, and `0x44..` for instances 0-5. Digital encoder and DP macros replicate across DIG/DP instances 0-6, and AUX macros replicate across AUX instances 0-5.
- Unqualified aliases such as `mmCUR_CONTROL`, `mmDC_LUT_CONTROL`, `mmREGAMMA_CONTROL`, `mmDP_LINK_CNTL`, and `mmSCL_MODE` generally point at instance 0. Consumers commonly add a pipe or CRTC offset, or select an instance-specific macro, to address other blocks.
- `ix...` macros define indexed debug/register-space selectors rather than ordinary direct MMIO offsets. This range includes `ixTMDS_DEBUG1..13`, `ixDP_AUX_DEBUG_A..Q`, `ixFMT_DEBUG0..2`, `ixMVP_DEBUG_12..17`, VGA sequencer/CRT/graphics/attribute indexes, and `ixVGADCC_DBG_DCCIF_C`.

Important macro families in this range include:

- DCP color and cursor: `mmGAMUT_REMAP_*`, `mmDCP_SPATIAL_DITHER_CNTL`, `mmDCP_RANDOM_SEEDS`, `mmCUR_*`, `mmDC_LUT_*`, `mmDCP_CRC_*`, `mmREGAMMA_*`, `mmALPHA_CONTROL`, and their `mmDCP0_...` through `mmDCP5_...` aliases.
- Digital encoder and audio: `mmDIG*_DIG_*`, `mmDIG*_HDMI_*`, `mmDIG*_AFMT_*`, `mmDIG*_TMDS_*`, and `mmDIG*_LVDS_DATA_CNTL`.
- DMCU: `mmDMCU_CTRL`, `mmDMCU_STATUS`, `mmDMCU_PC_START`, firmware control/version/checksum registers, RAM/ERAM/IRAM access registers, interrupt registers, `mmMASTER_COMM_*`, `mmSLAVE_COMM_*`, and `mmDMCU_PERFMON_*`.
- DisplayPort and AUX: `mmDP*_DP_LINK_CNTL`, `mmDP*_DP_PIXEL_FORMAT`, `mmDP*_DP_MSA_*`, `mmDP*_DP_VID_*`, `mmDP*_DP_DPHY_*`, `mmDP*_DP_SEC_*`, `mmDP*_DP_MSE_*`, `mmDP*_DP_TEST_*`, `mmDP_AUX*_AUX_*`, and `ixDP_AUX_DEBUG_*`.
- Output formatting and scanout: `mmFMT*_*`, `mmLB*_*`, `mmSCL*_*`, `mmSCLV_*`, `mmCOL_MAN_*`, `mmINPUT_CSC_*`, `mmOUTPUT_CSC_*`, `mmGAMMA_CORR_*`, and `mmUNP_GRPH_*`.
- Legacy and compatibility registers: VGA generic, sequencer, CRT, graphics, attribute, render/source/control/status/debug, and per-display `mmD1VGA_CONTROL` through `mmD6VGA_CONTROL` macros.

## Control Flow

This header has no control flow. It contributes compile-time constants used by runtime code that performs register access. Typical consumers use these addresses with helpers such as `RREG32`, `WREG32`, `dm_read_reg`, `dm_write_reg`, `REG_SET_FIELD`, and `set_reg_field_value`.

Observed integration examples in this tree include:

- `amdgpu/dce_v10_0.c` programs display color state by writing `mmDC_LUT_30_COLOR + amdgpu_crtc->crtc_offset`, then disabling degamma/gamut/regamma/CSC through `mmDEGAMMA_CONTROL`, `mmGAMUT_REMAP_CONTROL`, `mmREGAMMA_CONTROL`, `mmOUTPUT_CSC_CONTROL`, and `mmDENORM_CONTROL` with the CRTC offset.
- `amdgpu/dce_v10_0.c`, `amdgpu/vi.c`, `amdgpu/gmc_v8_0.c`, and related ASIC paths use `mmVGA_RENDER_CONTROL` and `mmVGA_HDP_CONTROL` to disable or restore VGA aperture/render behavior during display and memory-controller setup.
- `display/dc/dce110/dce110_mem_input_v.c` reads and writes `mmUNP_GRPH_ENABLE` to enable the uniphy graphics path for the DCE 11-style vertical memory-input block, whose address layout overlaps this DCE 10.0 header.
- Power-management and BACO files include this header for DCE 10.0-era display and low-power transition tables.

The effective control flow is therefore outside the header: select the right ASIC/generation header, select the right instance macro or add the correct per-CRTC offset, combine the address with the matching mask/shift header, then perform ordered MMIO reads/writes according to the hardware programming sequence.

## State And Persistence Behavior

The header itself is stateless. It does not allocate memory, perform I/O, maintain locks, or persist data.

The addressed registers represent persistent hardware state in the display engine until changed by driver code, firmware, mode-setting, hotplug handling, suspend/resume, BACO, display reset, or full GPU reset. State represented by this range includes:

- per-pipe color pipeline state: gamut remap coefficients, spatial dither settings, LUT contents and offsets, regamma piecewise-linear regions, input/output CSC coefficients, prescale values, denorm clamp ranges, gamma correction LUTs, and alpha/cursor behavior;
- cursor and overlay state: cursor surface addresses, size, position, hot spot, palette colors, update control, stereo control, overlay secondary surface addresses, and stereo flip controls;
- display-link state: digital encoder frontend routing, HDMI packet/audio state, AFMT InfoFrames and IEC-60958 state, TMDS/LVDS controls, DP link/MSA/video/PHY/secondary-data/MST controls, and AUX transaction control/status/debug registers;
- memory and plane state: line-buffer format, vblank/vline/interrupt/keyer/buffer/debug state, scaler coefficients and viewport/overscan state, MVP state, and uniphy graphics surface addresses/pitch/window/update/in-use/interrupt state;
- diagnostic state: CRC current/last registers, debug index/data registers, DMCU firmware/RAM/performance counters, frame-buffer compression debug/status registers, formatter debug, and VGA readback/debug registers.

Because these are raw addresses, they do not express read-only versus writable behavior, shadowing rules, double-buffering, update latches, or required vblank timing. Callers must supply the correct sequencing and synchronization.

## Dependencies And Integration Points

The immediate dependency is the C preprocessor and the generated AMD ASIC register naming contract. Practically, these address macros must match the DCE 10.0 hardware register specification and companion mask/shift files, especially `dce_10_0_sh_mask.h`.

Known include/integration points in this source tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v8_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_vi.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/fiji_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/tonga_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/*_smumgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_common.h`

The same logical register families appear in adjacent DCE headers such as DCE 8.0, 11.0, 11.2, and 12.0 offset headers, but addresses differ for some generations. Code that shares helpers across ASICs must include the matching generation header and must not assume a DCE 10.0 address is valid for DCE 8, DCE 11, DCE 12, or DCN.

## Risks And Edge Cases

The primary risk is silent misaddressing. These macros are untyped integers, so using a DCP1 register with a DCP0 offset, mixing DIG and DP instances, using an `ix...` indexed selector as direct MMIO, or applying a DCE 10.0 address on a different generation can compile cleanly while touching the wrong hardware register.

Instance aliases need careful handling. Unqualified macros often name instance 0, while many runtime paths add `amdgpu_crtc->crtc_offset` or use an instance-specific macro. Double-applying an offset to an instance-specific macro, or forgetting the offset for an unqualified macro, can target the wrong display pipe.

Display programming has timing and latch hazards not visible in this file. LUT, regamma, CSC, scaler, line-buffer, cursor, and surface-address updates may need vblank coordination, update-register writes, lock/unlock ordering, or atomic modeset sequencing. The header gives no hints about those constraints.

Some ranges expose disruptive controls. DP PHY, AUX, HDMI/AFMT, DMCU RAM/control, FBC, scaler, uniphy surface-address, and VGA aperture/render registers can affect link training, hotplug/AUX transactions, audio packets, firmware behavior, scanout addresses, or legacy VGA decode if written incorrectly.

The chunk begins at line 3029 in the middle of `GAMUT_REMAP_C21_C22`: the generic `mmGAMUT_REMAP_C21_C22` alias is in the previous chunk while the DCP0-DCP5 instance aliases are here. The chunk ends at line 6046 after `ixVGADCC_DBG_DCCIF_C`, before the BPHY PLL and PHY register addresses in the next chunk. Final file-level research should reconcile both boundaries.

## Test Signals

Useful validation signals include:

- Build coverage for DCE 10.0/VI display, GMC, GFX, BACO, and SMU translation units that include `dce_10_0_d.h`; missing or renamed macros should fail compilation.
- Generated-header checks comparing every address in this chunk against the DCE 10.0 register source data and against `dce_10_0_sh_mask.h` field definitions.
- Static checks for `ix...` versus `mm...` access style, ensuring indexed debug selectors are not passed to direct MMIO helpers by mistake.
- Static review of pipe/link instance arithmetic, especially unqualified DCP/LB/SCL/FMT/DP/AUX aliases plus runtime offsets versus already instance-qualified macros.
- Display modeset tests on DCE 10.0 hardware covering boot console handoff, CRTC enable/disable, cursor movement, gamma/LUT updates, color-management disable paths, scaler/viewport changes, overlay/uniphy paths, and suspend/resume.
- Link tests for HDMI, DVI/TMDS/LVDS where present, DP link training, DP MST, AUX transactions, hotplug, audio InfoFrame/AFMT programming, and secondary-data packet behavior.
- VGA handoff and aperture tests verifying that `mmVGA_RENDER_CONTROL`, `mmVGA_HDP_CONTROL`, and per-display VGA controls preserve expected boot/display behavior and do not leave legacy VGA decode enabled unexpectedly.
- Diagnostic tests for CRC, FBC status/debug, DMCU firmware/RAM access, formatter debug, and scaler/line-buffer debug paths when those features are available.

## Cross-Chunk Notes

This is chunk 2 of 3 for `dce_10_0_d.h`. The final per-file report should merge it with chunk 1, which contains the include guard and earlier DCE/DCP base addresses through the first half of gamut remap, and chunk 3, which continues with BPHY PLL/PHY, high-level display clock, audio, and remaining DCE 10.0 address definitions.
