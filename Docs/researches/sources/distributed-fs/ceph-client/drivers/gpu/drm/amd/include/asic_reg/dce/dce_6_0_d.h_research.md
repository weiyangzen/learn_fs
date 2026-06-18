# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_d.h

## Scope And Purpose

This file is an AMD DCE 6.0 display-engine register address header. It is guarded by `DCE_6_0_D_H` and contains only preprocessor constants: no functions, structs, enums, inline helpers, or executable logic. The constants map symbolic `mm...` MMIO register names and `ix...` indexed-register names to numeric offsets or indices for DCE 6.0-era display hardware.

The header's purpose is to let AMDGPU/Radeon display code use stable, generation-specific names for hardware registers instead of raw numeric offsets. The register space represented here covers display timing, display pipes, scalers, graphics planes, cursors, color conversion, LUT/regamma, line buffers, audio over display, HDMI/TMDS, DisplayPort link and AUX channels, CRTC/VGA legacy state, DCCG clocks and PLLs, DCIO/UNIPHY link PHY state, GPIO/DDC/HPD, DMIF/MCIF memory interfaces, frame-buffer compression, DMCU firmware access, ABM/backlight, XDMA, and low-level debug/test registers.

The file is generated-style and source-tree-aligned with companion ASIC register headers. Numeric values are the actual ABI between driver code and hardware; changing one macro is a behavioral change even though the file has no C control flow.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself. There are two major prefixes:

- `mm*`: memory-mapped register offsets used with normal register read/write helpers such as `RREG32`, `WREG32`, `dm_read_reg`, `dm_write_reg`, or higher-level AMD display register macros.
- `ix*`: indexed register selectors, mostly for VGA/legacy indexed blocks, Azalia codec endpoint indices, AUX/debug selectors, and similar index/data access windows.

Important families include:

- Legacy and indexed VGA families: `ixATTR*`, `ixCRT*`, `ixGRA*`, `ixSEQ*`, plus `mmVGA_*`, `mmCRTC8_*`, `mmSEQ8_*`, `mmGRPH8_*`, `mmGEN*`, and DAC index/data aliases. These support VGA compatibility paths and indexed access registers.
- Azalia/display-audio families: `ixAZALIA_*`, `ixAUDIO_DESCRIPTOR*`, `ixSINK_DESCRIPTION*`, `mmAZALIA_*`, `mmAZF0ENDPOINT*`, `mmAZF0STREAM*`, `mmAFMT_*`, and per-DIG `AFMT` aliases. These define HDA/Azalia converter, pin, endpoint, stream, audio descriptor, infoframe, CRC, packet, DTO, and latency/debug state.
- CRTC/timing generators: generic `mmCRTC_*` aliases and replicated `mmCRTC0_*` through `mmCRTC5_*` addresses. They cover totals, blanking, sync, interlace/stereo, snapshots, counters, status, trigger controls, update locks, test patterns, GSL, master update, and vblank/vupdate interrupt status.
- Display controller planes: generic `mmDCP_*`, `mmGRPH_*`, `mmOVL_*`, `mmCUR_*`, `mmPRESCALE_*`, `mmINPUT_CSC_*`, `mmOUTPUT_CSC_*`, `mmGAMUT_REMAP_*`, `mmDC_LUT_*`, and `mmREGAMMA_*`, plus replicated `mmDCP0_*` through `mmDCP5_*`. These represent graphics surface programming, overlay, color-keying, cursor, CSC, gamma/LUT, dithering, CRC, and debug registers.
- Scalers and formatters: generic `mmSCL_*`, `mmVIEWPORT_*`, `mmEXT_OVERSCAN_*`, `mmFMT_*`, and replicated `mmSCL0_*` through `mmSCL5_*` and `mmFMT0_*` through `mmFMT5_*`. These cover coefficient RAM, scale ratios, filter init, tap/bypass/mode-change controls, viewport/overscan, output clamp, bit depth, dithering, CRC, and formatter debug.
- Line buffers and multi-view/plane support: `mmLB*_*`, `mmMVP_*`, `ixMVP_DEBUG_*`, and the tail aliases for `mmDATA_FORMAT`, `mmDESKTOP_HEIGHT`, `mmDC_LB_MEMORY_SPLIT`, `mmDC_LB_MEM_SIZE`, `mmINT_MASK`, `mmVLINE_STATUS`, and `mmVBLANK_STATUS`. These constants describe line-buffer memory/layout/status and MVP synchronization or flip insertion behavior.
- Digital outputs: `mmDIG*_*`, `mmHDMI_*`, `mmTMDS_*`, `mmDP*_*`, `mmDP_AUX*_*`, and `ixDP_AUX*_DEBUG_*`. These cover DIG front/back-end programming, HDMI ACR/infoframe/audio/packet state, TMDS state, DisplayPort link training, DPHY, stream timing, M/N, secondary packets, MST/MSE, AUX native/software transactions, and DP debug windows.
- DCIO, PHY, GPIO, DDC, HPD, and panel control: `mmDCIO_*`, `mmUNIPHY*`, `mmAUX*`, `mmPHY_AUX_CNTL`, `mmDC_GPIO_*`, `mmDC_HPD*`, `mmDC_I2C_*`, `mmGENERIC_I2C_*`, `mmLVTMA_PWRSEQ_*`, `mmBL_PWM_*`, and impedance calibration registers. These are integration points for display connector detection, I2C/EDID, hotplug, link PHY setup, panel power sequencing, and backlight.
- Clocks, PLLs, and power/reset: `mmDCCG_*`, `mmDCCG_PLL0_*` through `mmDCCG_PLL2_*`, `mmPLL_*`, `mmDENTIST_DISPCLK_CNTL`, `mmDP_DTO*`, `mmDCCG_AUDIO_DTO*`, `mmSYMCLK*`, `mmPIXCLK*`, `mmDCFE*_SOFT_RESET`, `mmDIG_SOFT_RESET`, `mmDCO_SOFT_RESET`, `mmDCI_SOFT_RESET`, `mmUNIPHY_SOFT_RESET`, and clock-gating registers.
- Memory interface and display fetch: `mmDMIF_*`, `mmDMIF_PG0_*` through `mmDMIF_PG5_*`, `mmDPG_*`, `mmPIPE0_*` through `mmPIPE5_*`, `mmMCIF_*`, `mmDCPG_*`, `mmDC_PGFSM_*`, `mmDC_PGCNTL_STATUS_REG`, and `mmLOW_POWER_TILING_CONTROL`. These govern display memory request arbitration, urgency, stutter, p-state behavior, VMID, tiling, and power gating.
- Compression, firmware, and auxiliary blocks: `mmFBC_*` for frame-buffer compression, `mmDMCU_*` and master/slave communication registers for display microcontroller RAM/firmware/control/status, `mmDC_ABM1_*` and `mmBL1_PWM_*` for adaptive backlight/histogram/PWM, `mmXDMA_*` for cross-DMA display surfaces, and `mmDVO_*` for DVO output.

The final section is explicitly labeled `Registers that spilled out of sid.h`. It adds aliases for line-buffer data format, desktop height, memory split/size, priority counters, `DPG_PIPE_ARBITRATION_CONTROL3`, interrupt/status registers, and scaler horizontal filter init registers. These are part of the public register set even though they are separated from the main generated ordering.

## Control Flow And Data Flow

There is no runtime control flow in this header. The operational flow is compile-time substitution:

1. A DCE 6.0 display source file includes this header, often alongside a matching shift/mask header.
2. Code names a register macro such as `mmCRTC_H_TOTAL`, `mmDCP0_GRPH_ENABLE`, `mmDP0_DP_LINK_CNTL`, or `ixAZALIA_F0_CODEC_PIN_CONTROL_WIDGET_CONTROL`.
3. The C preprocessor replaces the macro with the numeric register offset or index.
4. Register accessor code reads, writes, or read-modify-writes that address, optionally adding per-instance offsets or using explicit instance aliases.
5. Companion mask/shift definitions or block-specific helper code handle individual bit fields and access sequencing.

The implied hardware data flow spans the display pipeline. Plane programming writes graphics or overlay surface addresses, pitch, format, viewport, cursor, LUT, CSC, prescale, and regamma state. Timing code writes CRTC totals, sync, blanking, stereo/interlace, update-lock, and interrupt registers. Scaler and formatter code writes filter coefficients, scale ratios, overscan, dither, clamp, and CRC controls. Output code programs DIG, HDMI, TMDS, DP, AUX, UNIPHY, GPIO, DDC, HPD, and panel/backlight registers. Memory and power code programs DMIF/MCIF/DPG/PIPE, FBC, DCPG, DCI, DCO, DCCG, and PLL state.

## State And Persistence Behavior

The header itself stores no state. Its constants are compiled into driver code.

The addressed hardware registers hold mutable display state that can persist until changed by a mode set, hotplug handling, suspend/resume restore, power-gating transition, display engine reset, GPU reset, firmware action, or explicit driver reprogramming. Important state classes include:

- Active scanout state: CRTC timing, blanking, sync, frame counters, surface addresses, pitch, viewport, cursor state, update locks, and master update controls.
- Color and image processing state: LUT indices/data, regamma regions, CSC matrices, gamut remap, prescale, denorm, dithering, clamp, scaler coefficients, filter ratios, and formatter settings.
- Link and connector state: DP link/training/MST/secondary packet registers, HDMI/TMDS packet/audio/timing registers, AUX transaction state, HPD interrupt/status, DDC/I2C transaction state, UNIPHY control, and LVTMA panel power sequencing.
- Clock and power state: DCCG DTOs, PLLs, symbol/pixel clocks, clock gates, soft resets, DCPG/pipe power-gating state, DMIF stutter/p-state controls, FBC control, and backlight/ABM state.
- Diagnostic and status state: CRC results, debug index/data windows, status/interrupt registers, FIFO status, underflow/latency counters, DMCU status/interrupts, and XDMA status.

This file does not encode whether a register is read-only, write-only, write-one-to-clear, indexed, shadowed, double-buffered, or timing sensitive. Consumers must know those semantics from hardware docs, shift/mask headers, and surrounding display component code.

## Dependencies

The direct syntactic dependency is only the C preprocessor. Practical use depends on:

- Companion DCE 6.0 mask/shift headers, especially for bitfield names, masks, and shifts.
- AMDGPU/Radeon register access helpers that understand MMIO and indexed-register access patterns.
- ASIC-specific display code that chooses the DCE 6.0 register database only for compatible hardware.
- Register instance-offset conventions. Generic macros such as `mmCRTC_H_TOTAL`, `mmDCP_CRC_CONTROL`, `mmSCL_CONTROL`, `mmFMT_CONTROL`, `mmDP_LINK_CNTL`, and `mmDIG_FE_CNTL` generally alias instance 0, while explicit `0..5` suffixed families name concrete replicated instances.
- Hardware sequencing knowledge for DCE 6.0 display blocks, including modeset ordering, update-lock usage, PLL programming, link training, I2C/AUX transactions, and power gating.

The header's numeric constants are tightly coupled to the DCE 6.0 register map. Neighboring generation headers use similar names with different offsets or additional blocks, so mixing DCE generation headers can compile but program the wrong hardware.

## Integration Points

This header integrates at the low level where display component code touches hardware registers. It is expected to be included by DCE 6.0-era AMD display code and by generated register-table code that maps block-level operations to addresses.

Key integration points are:

- Modeset and timing generator paths use `mmCRTC*` and `mmMASTER_UPDATE_*` macros to program CRTC timing, synchronization, status, and update behavior.
- Plane, memory-input, and transform paths use `mmDCP*`, `mmGRPH*`, `mmOVL*`, `mmCUR*`, `mmSCL*`, `mmLB*`, `mmFMT*`, LUT, CSC, and regamma macros to configure scanout, scaling, color, cursor, line-buffer, and formatter behavior.
- Link encoder and connector paths use `mmDIG*`, `mmDP*`, `mmHDMI*`, `mmTMDS*`, `mmDP_AUX*`, `mmDC_HPD*`, `mmDC_I2C*`, `mmGENERIC_I2C*`, `mmUNIPHY*`, and GPIO macros for hotplug, EDID, AUX/I2C, link training, PHY setup, and output packet programming.
- Audio paths use `mmAZALIA*`, `ixAZALIA*`, `mmAFMT*`, `ixAUDIO_DESCRIPTOR*`, and `ixSINK_DESCRIPTION*` to expose display audio capabilities and program HDMI/DP audio packets.
- Power-management and resume paths use DCCG/PLL/DTO, soft-reset, DCPG, DCI/DCO, FBC, ABM, backlight, and DMCU registers to gate, restore, or validate display hardware.
- Debug and validation paths use CRC, status, performance, latency, FIFO, debug-index/data, and test-pattern registers throughout the file.

Because this header names both generic instance-0 aliases and explicit per-instance aliases, integration code must be consistent: either use a generic base plus the correct block offset, or use an explicit instance macro directly. Doing both can double-apply an offset.

## Risks And Edge Cases

The largest risk is silent numeric drift. The compiler can detect a missing macro but cannot detect a wrong address value. A single bad offset can make a write land in a neighboring register or pipe, leading to display corruption, link failure, bad clocks, missed interrupts, or broken suspend/resume.

Specific risks include:

- Repeated register windows are dense and similar. CRTC0-5, DCP0-5, SCL0-5, FMT0-5, DIG0-5, DP0-5, AUX0-5, LB0-5, DMIF_PG0-5, PIPE0-5, and UNIPHY0-5 differ mostly by instance and base address.
- Generic aliases often equal instance 0. Code adding dynamic offsets must not start from an already-explicit instance macro.
- Indexed registers require the correct index/data access protocol. `ixAZALIA*`, `ixDP_AUX*_DEBUG_*`, and VGA indexed constants are not normal flat MMIO addresses.
- Debug, test, reserved, PLL, PHY, and DMCU RAM access registers may have side effects or undocumented sequencing constraints.
- Active scanout registers can be timing sensitive. Surface address, update lock, CRTC timing, scaler, LUT, CRC, and interrupt status registers may require vblank-safe or block-specific update ordering.
- The `sid.h` spillover section is easy to miss in generated comparisons; omitting it would break aliases for line-buffer, status, arbitration, and scaler filter init registers.
- Address ordering in the file is functional, not strictly numeric. Consumers should not infer register ranges from source order.

## Test Signals

There are no standalone unit tests for this header. Useful validation signals are build coverage, generated-register comparison, and hardware behavior tests:

- Build DCE 6.0-enabled AMDGPU/Radeon configurations to catch missing or renamed macros.
- Compare the full 4,540-line header against the authoritative AMD DCE 6.0 register database or a known-good upstream copy, including the final `sid.h` spillover aliases.
- Run modeset tests across all available pipes to validate CRTC timing, update locks, plane surface addresses, cursor state, scaler, formatter, CSC/LUT/regamma, vblank, and CRC readback.
- Exercise HDMI, DVI/TMDS, DisplayPort, AUX/I2C/EDID, HPD, and display audio paths to validate DIG, DP, HDMI, AFMT, Azalia, GPIO, and UNIPHY addresses.
- Test suspend/resume, display power gating, clock changes, PLL programming, FBC, ABM/backlight, and DMCU communication to catch bad persistence or restore behavior.
- Use register-dump comparisons after known-good modesets to verify generic-plus-offset accesses match explicit per-instance aliases.
- Validate interrupt and status paths for vblank, vline, HPD, AUX/I2C, underflow, FBC, DMCU, Azalia, and display memory-interface events.
