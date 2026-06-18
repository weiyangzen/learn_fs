# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 4039-7906

## Scope And Purpose

This chunk is a generated-style register shift/mask header segment for AMDGPU DCE 11.2 display hardware. It contains only C preprocessor constants, with paired `*_MASK` and `*__SHIFT` macros that describe bitfields inside display-engine MMIO registers. The chunk starts in the `DC_GPIO_DDC2_*` definitions and ends at `DMCU_INTERRUPT_STATUS__DCPG_IHC_DCFE0_POWER_UP_INT_OCCURRED__SHIFT`; earlier GPIO and display-control definitions, plus later DMCU interrupt/status fields, are outside this work item.

There are no functions, structs, enums, or executable branches here. The public contract is the macro namespace consumed by AMDGPU display, power-management, and firmware-loading code. Consumers combine these field constants with the sibling DCE 11.2 address header (`dce_11_2_d.h`) and register helpers such as `REG_SET_FIELD`, `RREG32`, and `WREG32` to read, compose, update, or poll hardware register values without embedding raw bit positions in driver code.

## Important APIs, Types, And Macro Families

The chunk exposes several large register families:

- GPIO and display connector pads: `DC_GPIO_DDC2` through `DC_GPIO_DDC6`, `DC_GPIO_DDCVGA`, `DC_GPIO_SYNCA`, `DC_GPIO_GENLK`, `DC_GPIO_HPD`, `DC_GPIO_PWRSEQ`, `DC_GPIO_I2CPAD`, `DC_GPIO_I2S_SPDIF`, `DC_GPIO_RECEIVER_EN0/1`, `DC_GPIO_AUX_CTRL_*`, `DC_GPIO_HPD_CTRL_*`, and `DC_GPIO_TX12_EN` describe DDC/AUX, VGA DDC, sync, genlock/swaplock, hotplug detect, backlight/power sequencing, I2C, audio pad, receiver-enable, slew/spike/filter, pad strength, and transmit-enable bits.
- Reserved PHY/macros: `DAC_MACRO_CNTL_RESERVED*`, `UNIPHY_MACRO_CNTL_RESERVED*`, `DCRX_PHY_MACRO_CNTL_RESERVED*`, and `DPHY_MACRO_CNTL_RESERVED*` map full 32-bit reserved register words. These still matter because generated tables or low-level bring-up code may preserve, save/restore, or compare reserved hardware state.
- Graphics plane, cursor, LUT, color, and transformation blocks: `GRPH_*`, `CUR_*`, `DC_LUT_*`, `DEGAMMA_CONTROL`, `DENORM_CONTROL`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `GAMUT_REMAP_*`, `COMM_MATRIX*`, `PRESCALE_*`, `REGAMMA_*`, `ALPHA_CONTROL`, `KEY_*`, `OUT_CLAMP_*`, and `OUT_ROUND_CONTROL` describe scanout surface format/addressing, page flip state, cursor surfaces, LUT programming, color-space matrices, gamut remap, gamma/regamma ramps, alpha blending, color keying, clamp, denorm, and rounding controls.
- Display core diagnostics and synchronization: `DCP_CRC_*`, `DCP_DEBUG*`, `DCP_TEST_DEBUG_*`, `DCP_GSL_CONTROL`, `DCP_LB_DATA_GAP_BETWEEN_CHUNK`, `DCP_SPATIAL_DITHER_CNTL`, `DCP_RANDOM_SEEDS`, `GRPH_XDMA_CACHE_UNDERFLOW_*`, and `GRPH_SURFACE_COUNTER_*` provide CRC capture, debug selectors, global-swap-lock coordination, line-buffer spacing, dither setup, random seed control, XDMA underflow detection, and surface counters.
- Display virtual memory: `DVMM_PTE_CONTROL` covers single-PTE use, page width/height, minimum PTEs before flip, and PTE buffer modes for display memory translation.
- DIG/TMDS/HDMI/AFMT output blocks: `DIG_FE_CNTL`, `DIG_BE_CNTL`, `DIG_LANE_ENABLE`, `DIG_OUTPUT_CRC_*`, `DIG_TEST_PATTERN`, `DIG_FIFO_STATUS`, `DIG_DISPCLK_SWITCH_*`, `TMDS_*`, `HDMI_*`, `AFMT_*`, `PHY_AUX_CNTL`, and `DVO_*` define digital encoder source selection, front/back-end enablement, lane enablement, CRC/test-pattern generation, FIFO calibration, display-clock switch interrupts, TMDS control symbols and DC balancing, HDMI scrambling/deep color/infoframe/generic packet/ACR/VBI/audio controls, Audio Format packet storage, AUX PHY, and legacy DVO analog-reference fields.
- DMCU firmware and interrupt interface: `DMCU_CTRL`, `DMCU_STATUS`, `DMCU_PC_START_ADDR`, `DMCU_FW_*`, `DMCU_RAM_ACCESS_CTRL`, `DMCU_ERAM_*`, `DMCU_IRAM_*`, `DMCU_EVENT_TRIGGER`, `DMCU_UC_INTERNAL_INT_STATUS`, `DMCU_SS_INTERRUPT_CNTL_STATUS`, and the first part of `DMCU_INTERRUPT_STATUS` define the display microcontroller reset/enable state, firmware address/checksum fields, host access to ERAM/IRAM, software interrupt generation, internal uC interrupt status, static-screen interrupts, ABM-ready/update interrupts, MCP/SCP/uC interrupts, external software interrupt, register read timeout, and the first DCPG/IHC power event in this chunk.

The naming convention is consistent: `REGISTER__FIELD_MASK` gives the raw bit mask, while `REGISTER__FIELD__SHIFT` gives the right shift needed to decode or encode the field. Names ending in `_MASK_MASK` are intentional because the underlying field name itself ends in `MASK`.

## Control Flow And Data Flow

This header has no runtime control flow. It enables compile-time substitution in register access paths. A typical data flow is:

1. Driver code reads a register address from `dce_11_2_d.h` with `RREG32()`.
2. The raw value is decoded with this header's `*_MASK` and `*__SHIFT` constants, or updated with `REG_SET_FIELD()`.
3. The composed value is written back with `WREG32()` or used as a polling predicate.

The chunk implies several hardware protocols even though the protocol code lives elsewhere:

- DDC/AUX/HPD/GPIO code masks pad output, enables input receivers, selects AUX-vs-DDC pad mode, handles pull-down/pull-up and drive strength, then reads `*_Y` or receiver status fields for connector detection and I2C/AUX transactions.
- Graphics scanout setup composes `GRPH_CONTROL`, pitch, primary/secondary surface address, endian/crossbar, tiling, compression, viewport, update, and flip-control fields before arming a page flip.
- Color-management paths program LUT indexes/data, input/output CSC matrices, degamma, prescale, gamut-remap, regamma region descriptors, clamp, and rounding fields in a hardware-defined order.
- HDMI/AFMT paths fill AVI/audio/MPEG/generic infoframes, channel-status words, ISRC payload bytes, ACR values, deep-color/scrambling controls, and send/continuous-send bits around encoder enablement.
- DMCU loading paths assert or release reset, enable host access to ERAM/IRAM, write firmware and interrupt-vector data, set start/end/checksum registers, trigger software interrupts, and check status/interrupt bits.

## State And Persistence Behavior

The header itself stores no state. State lives in DCE hardware registers, display microcontroller RAM, firmware-programmed registers, and connector-facing pad circuitry.

Important state classes represented by this chunk include:

- Mutable connector/pad state: DDC/AUX mode, clock/data enables, receiver enables, hotplug receiver state, pad drive strength, slew/spike controls, HPD controls, power-sequence GPIOs, and backlight/digital-on pins.
- Scanout and flip state: graphics surface addresses, high address bits, format, tiling, compression pitch, viewport boundaries, pending primary/secondary stereo surfaces, update locks, flip rate, and current in-use surface addresses.
- Color pipeline state: LUT indexes and data, black/white offsets, CSC matrices, prescale values, degamma/regamma/gamut modes, regamma piecewise-linear regions, alpha/key/clamp controls, and output rounding.
- Diagnostics and interrupt state: DCP/DIG CRC enable/result/last/current values, debug index/data ports, XDMA underflow counters and interrupt mask/ack bits, surface counter min/max, HDMI error status, display-clock-switch allowed interrupt bits, and DMCU static-screen or power/event interrupt bits.
- DMCU firmware state: reset/enable bits, program-counter start address, firmware start/end/ISR/checksum fields, ERAM/IRAM access control and data windows, internal interrupt status, and uC-to-host event state.

Many registers are sticky, latched, write-one-to-clear, or sequenced by hardware. For example, interrupt status fields often pair `*_OCCURRED` and `*_CLEAR` names on the same bit, and underflow/HDMI/DIG status registers include separate status, mask, and ack fields. Incorrect constants can therefore leave stale interrupts, clear the wrong event, or make a polling path wait forever.

## Dependencies And Integration Points

This header integrates with:

- The sibling DCE 11.2 address definitions in `include/asic_reg/dce/dce_11_2_d.h`.
- Generic AMDGPU register helpers and field macros that expect the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming scheme.
- DCE 11.2 display code under `drivers/gpu/drm/amd/display/dc/`, including `display/dc/dce112/dce112_compressor.c`, `display/dc/hwss/dce112/dce112_hwseq.c`, `display/dc/resource/dce112/dce112_resource.c`, and `display/dc/clk_mgr/dce112/dce112_clk_mgr.c`, which include this exact header.
- Power-management code such as `pm/powerplay/smumgr/vegam_smumgr.c`, which includes `dce_11_2_d.h` and this shift/mask header for DCE 11.2 register programming.
- Older AMDGPU DCE implementations (`dce_v6_0.c`, `dce_v8_0.c`, `dce_v10_0.c`) that use equivalent field names for AFMT, HDMI, GRPH, REGAMMA, and related display blocks. They are useful examples of how these macro families are consumed even when they target earlier DCE generations.
- Firmware and user-visible feature plumbing around DMCU/ABM/static-screen behavior. DMCU firmware IDs and ABM status are exposed through AMDGPU firmware query paths, coredump output, and display power-management policy, while the actual register programming uses DCE-specific fields like those defined here.

## Risks And Edge Cases

The highest risk is mismatch between this generated header and the DCE 11.2 register database. Since these constants are used in read-modify-write sequences, a one-bit error can mutate a neighboring field while appearing syntactically valid.

Specific risk areas in this chunk are:

- Connector GPIO and HPD fields: wrong DDC/AUX/HPD/power-sequence bits can break EDID reads, DisplayPort AUX transactions, hotplug detection, panel power sequencing, backlight enablement, or pad electrical characteristics.
- Surface and flip fields: incorrect `GRPH_*` masks can program bad scanout addresses, pitch, tiling, compression, endian/crossbar, stereo flip, or update-lock state, producing corruption, blank displays, hangs, or missed vblank/flip completion.
- Color and LUT fields: malformed CSC, LUT, regamma, gamut, clamp, or dither masks can silently change color output, HDR/SDR conversion, gamma ramps, or cursor blending.
- HDMI/AFMT packet fields: errors in deep-color, scrambling, ACR, audio channel status, infoframe, ISRC, generic packet, or VBI fields can produce link compatibility problems or missing audio/video metadata.
- Interrupt and status fields: several names map status, mask, ack, occurred, and clear semantics onto adjacent or identical bits. Treating a clear bit as a status bit, or vice versa, can lose interrupts or cause repeated interrupts.
- DMCU RAM and firmware fields: bad ERAM/IRAM address, byte-enable, checksum, reset, host-access, or interrupt bits can prevent DMCU firmware load, ABM, PSR/static-screen flows, or uC/host signaling from working.
- Reserved register ranges: the large `*_RESERVED*` families are easy to dismiss, but save/restore or generated power tables may rely on them. Writing reserved fields without the matching ASIC sequence can be unsafe.
- Chunk boundary risk: this document covers only lines 4039-7906. The chunk begins after earlier DCE 11.2 definitions and ends mid-`DMCU_INTERRUPT_STATUS`; conclusions about the full header require the remaining chunks.

## Test Signals

There are no standalone unit tests for this header. Practical validation is indirect:

- Build coverage for AMDGPU display and power-management objects that include `dce_11_2_sh_mask.h`; this catches missing or renamed macros but not incorrect numeric values.
- Register-database comparison against the authoritative DCE 11.2 generated header or ASIC documentation, especially for GPIO, GRPH, HDMI/AFMT, REGAMMA, and DMCU fields.
- Display bring-up on DCE 11.2 hardware: connector detection, EDID/DDC, DP AUX, HPD IRQs, panel power/backlight sequencing, mode set, vblank, page flip, cursor, and suspend/resume should work without timeouts.
- Plane and color tests: framebuffer formats, tiling/compression, stereo or synchronized flips where supported, gamma/degamma/regamma LUT programming, CSC/gamut remap, alpha/keying, and cursor blending should match expected output.
- HDMI/audio tests: deep color, scrambling, ACR/N values, audio channel map/status, AVI/audio/MPEG infoframes, generic packets, and audio playback should be validated on compatible sinks.
- Diagnostic tests: CRC capture, DCP/DIG test patterns, FIFO calibration/status, XDMA underflow counters/interrupts, display-clock-switch interrupt handling, and surface counters provide signals that masks and ack bits line up with hardware.
- DMCU/ABM/static-screen tests: firmware load, ERAM/IRAM read/write windows, uC reset/release, software interrupt delivery, static-screen interrupt clear/status behavior, ABM ready/update events, and DCPG/IHC power interrupts should be exercised where platform firmware supports them.
