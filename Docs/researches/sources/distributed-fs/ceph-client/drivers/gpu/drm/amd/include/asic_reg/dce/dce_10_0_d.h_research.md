# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001499`: lines 1-3028, `Docs/researches/chunks/subset-b-001499_research.md`
- `subset-b-001500`: lines 3029-6046, `Docs/researches/chunks/subset-b-001500_research.md`
- `subset-b-001501`: lines 6047-7358, `Docs/researches/chunks/subset-b-001501_research.md`

## Chunk Research

### subset-b-001499: lines 1-3028

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h

Chunk: `subset-b-001499`
Covered source range: lines 1-3028 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h`

## Purpose

This chunk is the first part of AMD's generated DCE 10.0 register address header. It is not executable driver logic; it provides preprocessor constants that map human-readable register names to MMIO or indexed-register addresses for DCE10-era display hardware.

The covered range starts at the license and include guard, then defines 3003 register constants. Most are `mm*` direct MMIO-style addresses, with a small number of `ix*` indexed debug selectors. The major hardware areas represented here are:

- display controller power gating and pipe power-gating status;
- backlight PWM and Adaptive Backlight Management, or ABM, histogram/luma registers;
- CRTC timing generator registers replicated across CRTC0 through CRTC6;
- DAC, display performance counters, display clock generator, pixel PLL, and clock debug registers;
- DMIF, MCIF, DCI, RBBMIF, and pipe memory-interface/arbitration registers;
- DCIO, UNIPHY, GPIO/DDC/HPD, backlight, power sequence, and display PHY reserve ranges;
- the beginning of DCP graphics plane and color-processing registers replicated across DCP0 through DCP5.

The chunk ends at `mmGAMUT_REMAP_C21_C22` on line 3028, in the middle of the DCP color-management address block. Later gamut-remap, gamma, cursor, line-buffer, scaler, and related DCE10 register addresses are expected in the next chunk for this source file.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or runtime APIs in this range. The interface is entirely macro constants inside `#ifndef DCE_10_0_D_H`.

The naming contract is:

- `mmREGISTER_NAME` is a direct register offset used with AMDGPU MMIO helpers such as `RREG32`, `WREG32`, and DC register macros.
- `mmBLOCKn_REGISTER_NAME` names the same logical register for a specific repeated hardware instance, such as `mmCRTC3_CRTC_CONTROL` or `mmDCP5_GRPH_ENABLE`.
- `ixREGISTER_NAME` is an indexed register selector used through an index/data access path rather than as a direct MMIO address.
- A base, unnumbered macro often aliases instance 0. For example, `mmCRTC_CONTROL` and `mmCRTC0_CRTC_CONTROL` both resolve to `0x1b9c`; `mmGRPH_CONTROL` and `mmDCP0_GRPH_CONTROL` both resolve to `0x1a01`.

Important macro families in this chunk include:

- `mmPIPE0..5_PG_*`, `mmDC_IP_REQUEST_CNTL`, `mmDC_PGFSM_*`, and `mmDCPG_TEST_DEBUG_*`: display pipe power-gating configuration, enable, status, and debug access.
- `mmBL1_PWM_*`, `mmDC_ABM1_*`, and `mmABM_TEST_DEBUG_*`: backlight PWM levels, ABM control, ambient/user/target/current duty data, luma statistics, histogram bins/results, overscan value, and ABM debug access.
- `mmCRTC_*` plus `mmCRTC0..6_*`: timing-generator clocking, horizontal/vertical totals, blanking, sync A/B, trigger, stereo, AV sync, control/blank/interlace/status, snapshots, update locks, test pattern, MVP, interrupts, CRC windows/results, external timing sync, static-screen, and global swap-lock/GSL support.
- `mmDAC_*`: analog DAC enable/source, CRC, sync tristate, autodetect, forced output, power-down, comparator, FIFO, DFT, and debug registers.
- `mmPERFCOUNTER*`, `mmPERFMON*`, and `mmDC_PERFMON*`: display performance counter control/state and counter pair addresses.
- `mmREFCLK_CNTL`, `mmDPREFCLK_CNTL`, `mmDCCG_*`, `mmDENTIST_DISPCLK_CNTL`, `mmCPLL_*`, and `mmPLL_*`: display clock generator control, DP reference clock selection, clock gating/debug, symclk/pixclk/dpclk controls, CPLL and PLL macro reserved ranges.
- `mmDMIF_*`, `mmPIPE0..7_ARBITRATION_CONTROL3`, `mmPIPE0..7_MAX_REQUESTS`, `mmMCIF_*`, `mmDCI_*`, `mmRBBMIF_*`, and indexed `ixDMIF_*`/`ixIDDCCIF*`: display memory interface, memory client interface, arbitration, VMID, low-power tiling, request limits, timeout/status, and debug selector registers.
- `mmDC_*`, `mmUNIPHYA..G_*`, `mmUNIPHY_IMPCAL_*`, `mmAUXP_IMPCAL`, `mmAUXN_IMPCAL`, `mmDCIO_*`, `mmDC_GPIO_*`, `mmLVTMA_PWRSEQ_*`, and `mmBL_PWM_*`: physical display I/O, UNIPHY link/channel mux, impedance calibration, AUX pads, GPIO/DDC/HPD/power-sequence pads, backlight PWM, generic debug, and DCIO soft reset/test debug.
- `mmUNIPHY_MACRO_CNTL_RESERVED*`, `mmDCRX_PHY_MACRO_CNTL_RESERVED*`, and `mmDPHY_MACRO_CNTL_RESERVED*`: reserved PHY macro address ranges. They still matter because low-level bring-up tables and golden-register sequences may write reserved or undocumented addresses for specific ASIC steppings.
- `mmGRPH_*`, `mmDCP0..5_GRPH_*`, `mmOVL_*`, `mmPRESCALE_*`, `mmINPUT_*`, `mmOUTPUT_*`, `mmCOMM_MATRIX*`, `mmDENORM_*`, `mmOUT_CLAMP_*`, `mmKEY_*`, `mmDEGAMMA_*`, and the first `mmGAMUT_REMAP_*` entries: graphics-plane enable/control, surface addresses and pitch, viewport/source extents, update/flip state, overlay surface setup, prescale/color matrix, input/output CSC, clamp/denorm/keying, degamma, and gamut remap addresses.

This header is normally paired with `dce_10_0_sh_mask.h`, which supplies the bit masks and shifts for the registers named here, and `dce_10_0_enum.h`, which supplies generated symbolic field values.

## Control Flow

The header itself has no runtime control flow. It is a flat list of `#define` constants guarded by `DCE_10_0_D_H`.

Runtime control flow appears in consumers that include this header and use these constants with generated masks and register-access helpers. Common patterns are:

1. compute a per-instance address by adding a CRTC or DCP offset to an unnumbered base macro, such as `mmGRPH_ENABLE + amdgpu_crtc->crtc_offset`;
2. read a register with `RREG32`, `dm_read_reg_soc15`, or a DC register helper;
3. update fields using `REG_SET_FIELD`, `REG_GET_FIELD`, or hand-coded bit operations from the paired shift/mask header;
4. write the register back with `WREG32` or a DC helper;
5. poll or read status registers for vblank, frame count, hotplug, link state, power-gating state, CRC, or clock state.

Concrete examples in this tree include `amdgpu/dce_v10_0.c`, which reads `mmCRTC_STATUS_FRAME_COUNT + crtc_offsets[crtc]` for vblank counters, writes `mmGRPH_ENABLE + amdgpu_crtc->crtc_offset` when enabling a graphics plane, allocates DCE10 PPLLs for CRTC modes, and toggles CRTC interrupt fields through line-buffer interrupt registers outside this chunk. `display/dc/resource/dce100/dce100_resource.c` derives per-pipe offsets from address differences such as `mmCRTC0_CRTC_CONTROL - mmCRTC_CONTROL` and `mmDCP0_GRPH_CONTROL - mmGRPH_CONTROL`. `display/dc/clk_mgr/dce100/dce_clk_mgr.c` reads `mmDENTIST_DISPCLK_CNTL` through the generated register layer to calculate DP reference clock frequency.

Because this header only gives addresses, it does not encode register ordering rules. Callers are responsible for DCE sequencing: disabling display paths before disruptive changes, using update locks for atomic timing/surface updates, waiting for vblank where required, respecting PLL ownership, and preserving reserved bits during read/modify/write.

## State And Persistence Behavior

The header is stateless at runtime. Its constants are compiled into drivers and have no storage, locks, persistence, or side effects.

The registers named by the constants represent persistent hardware state inside the DCE10 display controller. Writes may survive until changed by another driver path, display mode set, hotplug event, suspend/resume, GPU reset, BACO/power-gating transition, or ASIC reset. Significant state categories in this chunk include:

- pipe and display-controller power-gating enable/status;
- PWM/backlight and ABM control plus live luma/histogram results;
- CRTC timing, blanking, sync, scanout status, interrupt position/mask/status, update-lock, CRC, test-pattern, snapshot, and external-sync state;
- display clock, DP reference clock, symclk, pixclk, PLL/CPLL, and clock-gating state;
- DMIF/MCIF/DCI arbitration, VMID, memory-interface timing, request limits, NACK/status, and soft-reset/debug state;
- DCIO/UNIPHY/GPIO/DDC/HPD/power-sequence pad ownership and physical output/link configuration;
- graphics-plane base addresses, pitch, tiling-related control, viewport coordinates, color-processing matrices, clamp/keying, degamma, and gamut-remap state.

Many of these registers are coupled to DRM state. For example, surface address and pitch programming mirrors framebuffer pinning and scanout state; CRTC timing mirrors the active DRM mode; interrupt registers mirror vblank/pageflip/hotplug enablement; clock and PLL registers mirror encoder/link requirements. The header does not keep software shadow copies or restore values; that behavior lives in the DCE, DC, PowerPlay, and reset paths.

## Dependencies And Integration Points

Direct dependencies are just the C preprocessor and the include guard. Practical dependencies and integration points are broader:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h` supplies field masks/shifts for the register names in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_enum.h` supplies generated enumerated field values used with those masks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v10_0.c` is the main legacy DCE10 display implementation using these addresses for CRTC, plane, PLL, audio, HPD, interrupt, mode-set, cursor, LUT, and reset flows.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.c` includes this header and selects DCE10 IP blocks for VI ASICs.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce100/dce100_resource.c` uses these addresses to build DCE100 offset tables for DC timing-generator and DCP instances.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce100/dce100_hwseq.c` includes this header for DCE100 hardware sequencing.
- Power and firmware-related consumers include `gmc_v8_0.c`, `gfx_v8_0.c`, `mxgpu_vi.c`, `pm/powerplay/hwmgr/{tonga_baco.c,fiji_baco.c}`, and `pm/powerplay/smumgr/{iceland_smumgr.c,tonga_smumgr.c,polaris10_smumgr.c,fiji_smumgr.c}`.

The macro values are generation-specific. Adjacent DCE headers contain many same-named macros but not always identical addresses, especially for GPIO/DCIO and newer offset/base-index formats. Code must include the header matching the active ASIC generation; mixing DCE10 addresses with DCE6/DCE8/DCE11/DCE12 masks or offsets can silently target the wrong register.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. These constants are untyped integers, so the compiler cannot verify that a CRTC address is used with a CRTC mask, that DCP and CRTC instance offsets are not mixed, or that an unnumbered base macro is valid for the intended instance.

Replicated instance blocks need careful offset handling. DCE10 has CRTC0 through CRTC6 address definitions in this chunk, while the DCP graphics-plane section here covers DCP0 through DCP5. Code that assumes the same instance count or stride across blocks can address non-existent or different hardware.

Several base macros alias instance 0. This is convenient for offset arithmetic but dangerous if callers use an unnumbered macro without adding the selected `crtc_offset` or DCP offset. The resulting code compiles and runs against CRTC0/DCP0 even when another pipe was intended.

Reserved macro ranges are not harmless names. `mmUNIPHY_MACRO_CNTL_RESERVED*`, `mmDCRX_PHY_MACRO_CNTL_RESERVED*`, `mmDPHY_MACRO_CNTL_RESERVED*`, `mmCPLL_MACRO_CNTL_RESERVED*`, and `mmPLL_MACRO_CNTL_RESERVED*` may be needed by ASIC-specific golden-register or firmware sequences, but casual writes can disturb display PHY, clock, or link behavior.

Display timing and surface registers are live hardware controls. Incorrect updates to CRTC totals/syncs, update locks, master locks, interrupt positions, surface addresses, pitch, tiling, viewport, or color matrices can cause hangs, underflow, blank displays, corrupted scanout, missed pageflips, or bad color.

Clock and PLL constants are especially sensitive. DENTIST, DPREFCLK, CPLL, PLL, symclk, pixclk, and DCCG registers influence link clocks and scanout timing; driver changes must coordinate with PLL ownership, DP shared-PPLL rules, spread-spectrum behavior, and suspend/resume state.

The chunk boundary splits a logical feature area. The DCP color pipeline begins here and continues beyond line 3028, so final file-level research should merge this chunk with the following one before drawing complete conclusions about color/gamma/cursor/scaler/register coverage.

## Test Signals

Useful validation signals include:

- build coverage for all translation units that include `dce_10_0_d.h`, especially `amdgpu/dce_v10_0.c`, VI setup, DCE100 DC resource/hwseq code, and PowerPlay/SMU DCE10-era files;
- generated-header checks that macro names are unique and address aliases are intentional instance aliases rather than accidental duplicate definitions;
- consistency checks that each register used with `REG_SET_FIELD` or `REG_GET_FIELD` has matching field definitions in `dce_10_0_sh_mask.h`;
- static checks that CRTC and DCP offset arithmetic uses the correct base macro and instance count;
- mode-setting tests across all supported heads, including enable/disable, DPMS, hotplug, suspend/resume, GPU reset, and multi-monitor configurations;
- vblank/pageflip interrupt tests, because CRTC status/interrupt/update-lock registers in this family drive DRM event delivery;
- framebuffer scanout tests covering primary surface base/pitch/format/tiling, panning, pageflips, and cursor interactions;
- color pipeline tests for degamma, CSC, clamp, keying, and gamut-remap programming once this chunk is merged with the following DCP color-register chunk;
- DP/HDMI/VGA output tests covering PLL selection, DP reference clock calculation from `DENTIST_DISPCLK_CNTL`, UNIPHY routing, GPIO/DDC/HPD behavior, and backlight/PWM behavior;
- hardware power-management tests for DCE disable/enable, pipe power gating, BACO, and SMU/PowerPlay transitions that may write DCE registers from golden tables or restore paths.

### subset-b-001500: lines 3029-6046

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

### subset-b-001501: lines 6047-7358

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_d.h lines 6047-7358

## Scope

This chunk is the final section of the DCE 10.0 register-address header. It contains no executable code, functions, structs, or enums; its exported surface is a dense set of preprocessor constants mapping DCE 10.0 display, audio, PHY, I2C, and XDMA register names to MMIO or indexed-register offsets. It closes the file's include guard at line 7358.

## Purpose

The constants in this chunk are the address layer used by AMDGPU DCE 10 display code and related VI/SMU/powerplay paths. The companion `dce_10_0_sh_mask.h` supplies field masks and shifts; this file supplies register selectors such as `mmAZALIA_F0_CODEC_ENDPOINT_INDEX`, `mmDC_I2C_CONTROL`, `mmBLND_CONTROL`, and repeated per-instance aliases. Call sites include `amdgpu/dce_v10_0.c`, `amdgpu/vi.c`, `amdgpu/gmc_v8_0.c`, `amdgpu/gfx_v8_0.c`, `pm/powerplay/*`, and DC resource/hwseq code under `display/dc/.../dce100`.

## Important Macro Families

- BPHYC PLL and VGA PPLL registers at lines 6049-6184 define generic names plus `BPHYC_PLL0/1/2_*` aliases. The pattern maps PLL instance 0 at `0x1700..0x1723`, PLL1 offset by `0x2a`, and PLL2 offset by `0x54`. Covered controls include ref/fb/post dividers, spread-spectrum amount/control, deep-sleep/id clock control, analog/vreg/unlock/debug/update registers, VGA25/VGA28/VGA41 PPLL dividers, and spare/debug/status registers.
- UNIPHY PHY registers at lines 6185-6376 define `mmUNIPHY_*` generic names and `BPHYC_UNIPHY0..6_*` instance aliases. Instances are spaced by `0x20` from `0x48c0` through `0x4980`. Covered controls include transmitter control, power, PLL feedback/control/spread-spectrum, data synchronization, BIST/test outputs, TMDP registers, TPG seed/control, and debug.
- DMIF display pipe gateway registers at lines 6377-6488 define `DPG_*` control, watermark, urgency, DPM, stutter, NB p-state, repeater, hardware debug, and indexed debug registers. Per-pipe aliases cover `DMIF_PG0..6` with bases `0x1b30`, `0x1d30`, `0x1f30`, `0x4130`, `0x4330`, `0x4530`, and `0x4730`.
- Azalia/HDA audio definitions span lines 6489-6950. They include root/function codec parameter verbs (`ixAZALIA_F2_*`), DCE-side Azalia controller MMIO registers (`mmAZALIA_*`), HDA global/CORB/RIRB/stream descriptor offsets, endpoint index/data windows, output and input converter/pin controls, audio descriptors, sink info, CRC controls, stream and endpoint indirect register windows, and per-channel CRC selectors.
- Blender registers at lines 6951-7030 define `BLND_CONTROL`, secondary controls, update, underflow interrupt, vertical update lock, update status, debug, and indexed debug registers for `BLND0..6`, following the same pipe base pattern as DMIF/CRTC-style display instances.
- Writeback/converter registers at lines 7031-7061 define `WB_*` and `CNV_*` controls for writeback enable/config, converter mode/window/source size/update, color-space conversion matrix, rounding/clamp, CRC test results, debug, input selection, soft reset, and indexed converter test debug. These are single-address definitions in the `0x5e18..0x5e36` range in this chunk.
- DCFE and DCFEV registers at lines 7062-7088 define front-end clock control, soft reset, and debug config for `DCFE0..5`, plus virtual front-end `DCFEV_*` clock/reset/DMIFV memory power controls.
- HPD, DCO, interrupt, and I2C registers at lines 7089-7196 define hot-plug-detect status/control/fast-train/filter registers for `HPD0..5`, display-controller scratch registers, display interrupt status continuations, DCO memory power/clock/reset/debug registers, DCE I2C/DDC transaction/data/status/speed/setup registers, VGA DDC, EDID detect, generic I2C controls, and pin debug/selection.
- XDMA registers at lines 7197-7356 define global XDMA control/status/power/debug registers, master controls and per-master-pipe aliases for pipes 0-5 spaced by `0x10`, and slave controls plus slave channel aliases for channels 0-5 spaced by `0x8`. They cover local and remote surface base addresses, high address halves, remote GPU address fields, cache base/cache controls, channel start/dim/height, perf counters, urgent controls, NACK status, and slave latency/flip/channel state.

## APIs, Types, and Integration Points

The API surface is entirely macro-based. Users pass `mm*` constants to register access helpers such as `RREG32`, `WREG32`, indirect indexed audio helpers, register-sequence programming tables, and DC `reg_helper` macros. For example, `amdgpu/dce_v10_0.c` uses `mmAZALIA_F0_CODEC_ENDPOINT_INDEX + block_offset` and `mmAZALIA_F0_CODEC_ENDPOINT_DATA + block_offset` under `adev->reg.audio_endpt.lock` to access endpoint indirect registers.

The `ix*` constants are not direct MMIO registers in the same style as `mm*`; they are indexed-selector values or HDA verb/register indices used through an index/data window or codec command path. The repeated generic-plus-instance aliases let call sites either compute an instance offset (`base + block_offset`) or use a fully expanded instance macro when tables need literal addresses.

## Control Flow

This chunk has no runtime control flow. Its effective control flow appears in consumers:

- direct MMIO access through `RREG32/WREG32` using an `mm*` address;
- indirect access sequences that write an index register, then read or write the corresponding data register;
- per-instance dispatch using arrays or offsets added to generic base registers;
- register initialization tables that pair these address constants with masks and values from the companion mask header.

## State and Persistence Behavior

The header itself stores no state. The named registers represent hardware state that persists in the GPU display/audio/XDMA blocks until overwritten, reset, power-gated, or lost across device reset/suspend. Several macro groups point at stateful hardware domains:

- PLL/UNIPHY settings affect link clocks, transmitter power, spread spectrum, and PHY debug/test modes.
- DMIF and BLND registers affect per-pipe memory fetch arbitration, stutter/urgency, blending updates, and underflow reporting.
- Azalia registers control HDA command rings, stream descriptors, endpoint/pin/converter state, CRC/debug, sink information, and audio hotplug/status behavior.
- I2C/DDC registers drive EDID and AUX-adjacent display-detection workflows.
- XDMA master/slave registers configure cross-device display memory movement, addresses, caches, and perf/latency counters.

## Dependencies

The correctness of this chunk depends on the DCE 10.0 ASIC register map. It is normally paired with:

- `dce_10_0_sh_mask.h` for bit fields;
- AMDGPU register helpers and locking discipline around indexed register windows;
- display instance offset tables for CRTC/DMIF/BLND/DCFE/HPD-like blocks;
- HDA/Azalia codec logic that understands the distinction between MMIO window addresses and `ix*` indexed codec selectors;
- power-management and reset code that preserves or reprograms volatile display/audio state across BACO, suspend/resume, and GPU reset.

## Risks and Edge Cases

- Address aliasing is intentional but risky: many generic names equal instance 0, and several HDA offsets share the same low offset for different subfields, such as CORB/RIRB control/status/size and immediate-command index/data aliases. Consumers must use the correct access width, field mask, and indexed path.
- Instance spacing is not uniform across all groups. UNIPHY uses `0x20`, HPD uses `0x8`, XDMA master pipes use `0x10`, XDMA slave channels use `0x8`, and display pipe families jump from low pipe bases to `0x41xx+` for later pipes. Hard-coded arithmetic outside existing offset tables can easily select the wrong block.
- `mm*` and `ix*` constants are semantically different even when values overlap. Treating an `ixAZALIA_*` selector as a direct MMIO address, or vice versa, would corrupt unrelated registers.
- Several register groups control clocks, resets, power, I2C transactions, DMA addresses, and hotplug/audio status. Incorrect values can cause display blanking, missed hotplug interrupts, bad EDID reads, audio stream failure, underflows, or DMA to the wrong address.
- This file is generated-style hardware data with no compile-time type safety. Duplicate numeric values, stale ASIC documentation, or copy/paste drift across DCE versions will compile cleanly but fail only on affected hardware paths.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build coverage for all DCE 10 include users, especially `amdgpu/dce_v10_0.c`, DC DCE100 resource/hwseq code, VI init, and SMU/powerplay paths.
- Display bring-up on DCE 10 ASICs with multiple connected outputs, validating HPD interrupts, EDID reads over every DDC/I2C path, mode set, vblank/page flip, and suspend/resume.
- Audio-over-HDMI/DP tests that exercise Azalia endpoint index/data windows, stream descriptors, converter/pin controls, hotplug, channel allocation, HBR/lipsync, and CRC/debug paths.
- Multi-pipe stress tests for underflow, watermark, stutter, DPM, and blend update behavior across all pipe instances.
- PHY/link tests across UNIPHY/PLL instances and VGA PPLL compatibility paths, including link training, spread-spectrum programming, power-gating, and reset recovery.
- XDMA master/slave validation on configurations that use XDMA display paths, checking remote address programming, perf/latency counters, NACK reporting, and channel start/flip behavior.

## Chunk Boundary Notes

This report covers only lines 6047-7358. Earlier chunks define the rest of the DCE 10.0 register map and may include the companion families needed to understand CRTC, GRPH, SCL, DIG, DP, AUX, and other display blocks. The final per-file report should merge this chunk with earlier chunk reports and preserve that this tail section closes `DCE_10_0_D_H`.
