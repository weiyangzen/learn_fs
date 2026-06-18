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
