# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001529`: lines 1-2497, `Docs/researches/chunks/subset-b-001529_research.md`
- `subset-b-001530`: lines 2498-5107, `Docs/researches/chunks/subset-b-001530_research.md`
- `subset-b-001531`: lines 5108-7637, `Docs/researches/chunks/subset-b-001531_research.md`
- `subset-b-001532`: lines 7638-10215, `Docs/researches/chunks/subset-b-001532_research.md`
- `subset-b-001533`: lines 10216-12711, `Docs/researches/chunks/subset-b-001533_research.md`
- `subset-b-001534`: lines 12712-15215, `Docs/researches/chunks/subset-b-001534_research.md`
- `subset-b-001535`: lines 15216-17814, `Docs/researches/chunks/subset-b-001535_research.md`
- `subset-b-001536`: lines 17815-18209, `Docs/researches/chunks/subset-b-001536_research.md`

## Chunk Research

### subset-b-001529: lines 1-2497

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 1-2497

## Scope And Purpose

This chunk is the opening portion of AMDGPU's DCE 12.0 generated register-offset header. It contains the license, include guard, address-block comments, and 2,418 `mm*` preprocessor definitions: 1,209 register offset macros and 1,209 paired `*_BASE_IDX` macros. The chunk starts with small standalone `dispdec` VGA page-address aliases, then maps a large set of DCE display-controller blocks up through the beginning of the DCRX receiver/clock block at line 2497.

There are no functions, structs, enums, or executable algorithms here. The header's public contract is the macro namespace used by display, GPIO, interrupt, memory-controller, and hardware-sequencing code to compute SOC15 MMIO addresses. Consumers typically combine `mmREGISTER_BASE_IDX` with the ASIC base table and add `mmREGISTER`, then combine the resulting address with bitfield definitions from `dce_12_0_sh_mask.h`.

## Important APIs, Types, And Macro Families

The API surface is a generated list of register-address macros. Each register has a value macro such as `mmDC_I2C_CONTROL` and a matching segment selector such as `mmDC_I2C_CONTROL_BASE_IDX`. Local call sites expand these with helper macros like `BASE(mm ## reg_name ## _BASE_IDX) + mm ## reg_name` or `BASE(mm ## block ## id ## _ ## reg_name ## _BASE_IDX) + mm ## block ## id ## _ ## reg_name`.

Major families covered in this chunk are:

- Initial indexed and isolated blocks: `mmdispdec_VGA_MEM_WRITE_PAGE_ADDR`, `mmdispdec_VGA_MEM_READ_PAGE_ADDR`, `DC_PERFMON0`, `DC_PERFMON13`, `DC_PERFMON1`, `DC_PERFMON9`, `PPLL_*`, and `PLL_MACRO_CNTL_RESERVED*`. These expose VGA page addressing, display performance counters, and display PLL or reserved PLL macro windows.
- Writeback and capture blocks: `MCIF_WB0`, `MCIF_WB1`, and `MCIF_WB2` cover buffer-manager control/status, pitch, four luma/chroma buffer address pairs, arbitration, watermark, QoS, self-refresh, warm-up, and buffer sizing. `CWB0` and `CWB1` provide capture/writeback control, fence parameters, and CRC masks/results.
- Main `dce_dc_dispdec` address block: from line 548 onward, the header maps the broad display-controller register space. It includes legacy VGA aliases, DAC palette/index/data aliases, pixel-clock and symbol-clock controls, DP/MIPI DTOs, AV sync counters, DCCG controls, CRTC pixel-rate controls, audio DTOs, display version, clock gating, reset, and timing-source support registers.
- Frame-buffer compression and display power gating: `FBC_*`, `PIPE0` through `PIPE5` power-gating config/enable/status, `DSI_PG_*`, `DCFEV0/1_PG_*`, `DCPG_INTERRUPT_*`, `DC_IP_REQUEST_CNTL`, and `DC_PGCNTL_STATUS_REG`.
- Memory-interface and virtual-memory display paths: `DMIF*`, `PIPE*_ARBITRATION_CONTROL3`, `PIPE*_MAX_REQUESTS`, `MCIF_CONTROL`, `MCIF_WRITE_COMBINE_CONTROL`, outstanding counters, `DCI_MEM_PWR_*`, `DVMM_*`, `DCHUB_*`, `DCHUB_FB_LOCATION`, `DCHUB_AGP_*`, cursor memory controls, and viewport/aperture-related hub controls.
- Writeback pipeline processing: `WB_*`, `CNV_*`, and `WBSCL_*` define writeback enable/configuration, color-space conversion matrices and clamps, source/window sizes, soft reset/warm-up controls, scaler coefficient RAM, tap control, filter ratios, clamp/rounding, overflow status, CRCs, and backpressure counters.
- DMCU, backlight, adaptive backlight, and microcontroller communication: `DMCU_*`, `MASTER_COMM_*`, `SLAVE_COMM_*`, `BL1_PWM_*`, `DC_ABM1_*`, DMCU interrupt masks/status, firmware address/checksum registers, ERAM/IRAM access registers, and histogram/luma statistic result registers.
- Audio and display-output support: `AZALIA_*` and codec function registers cover display audio DMA, DTO, CRC, capability, codec power/reset, channel-count, GTC offset, and port-connectivity registers. `DAC_*` covers analog output enable/source, CRC, autodetect, forced output, power, comparator, DFT, and FIFO status.
- I2C, scratch, interrupt, and output controller state: `DC_I2C_*`, `GENERIC_I2C_*`, `DCO_SCRATCH*`, `DCE_VCE_CONTROL`, `DISP_INTERRUPT_STATUS*`, `DCO_MEM_PWR_*`, `DCO_CLK_CNTL*`, `DIG_SOFT_RESET*`, `FMT_MEMORY*_CONTROL`, and PSP/generic DCO interrupt registers.
- DCIO, GPIO, panel power, and physical output links: `DC_GENERICA/B`, `DC_PAD_EXTERN_SIG`, `UNIPHYA` through `UNIPHYG`, `DCIO_*`, `LVTMA_PWRSEQ_*`, `BL_PWM_*`, genlock/swaplock controls, GPU timer controls, impedance calibration, semaphores, `DC_GPIO_*` groups for generic pins, DDC1-6, DDCVGA, sync, genlock, HPD, power sequence, I2C pads, I2S/SPDIF, AUX control, and DAC macro controls.
- Receiver and DPHY blocks at the end of the chunk: `DISP_DSI_DUAL_CTRL`, `DPHY_MACRO_CNTL_RESERVED*`, `DPRX_AUX_*`, `DPRX_DPHY_*`, and the first `DCRX_*` registers define MIPI/DP receiver-related reserved macro windows, AUX buffers/indexed data registers, DPCD/message/KSV storage, DPHY lane training/status/error counters, and DCRX gate/reset/light-sleep/clock controls.

The chunk contains intentional duplicate numeric offsets because several register names share an address in different addressing views, indexed register aliases, or different base-index segments. Examples include VGA/DAC legacy aliases around offsets `0x002d` through `0x0033`, PLL macro reserved aliases overlapping PPLL and clock-control offsets, and `BPHYC_DAC_*` aliases overlapping `DAC_MACRO_CNTL_RESERVED*`.

## Control Flow And Data Flow

This header has no runtime control flow. Its data flow is compile-time substitution of symbolic register names into MMIO address calculations. For SOC15-era display code, address construction generally follows this pattern:

1. Select a base segment with `BASE(mmREG_BASE_IDX)`.
2. Add the register offset from `mmREG`.
3. Use the resulting address with `dm_read_reg_soc15`, `generic_reg_set_soc15`, `generic_reg_update_soc15`, IRQ table setup, GPIO translation, or AMDGPU SOC15 register helpers.
4. Use the sibling shift/mask header to isolate fields in the raw register value.

Several hardware protocols are implied by the register groupings even though this file does not implement the sequencing. MCIF writeback requires programming pitch, buffer addresses, buffer sizes, watermarks, and arbitration before enabling capture. DMCU firmware flows require start/end/ISR addresses, RAM access registers, communication mailboxes, and interrupt masks/status. DC GPIO translation maps raw register offsets and masks back to logical GPIO IDs such as HPD, DDC, sync, genlock, and generic pins. IRQ service tables compute enable/status/ack registers from block instance macros, so any wrong offset can route interrupts to the wrong hardware register.

## State And Persistence Behavior

The header itself stores no state and creates no persistent objects. The state described by these constants lives in DCE 12.0 hardware registers, firmware-controlled microcontroller RAM/registers, display hub apertures, GPIO pads, and link/audio/output blocks.

Important state classes described by the chunk include:

- Display and legacy VGA state: VGA memory page addresses, render/mode/surface controls, DAC palette and analog-output state, source select, and VGA interrupt/status registers.
- Clock, reset, and power state: DCCG clock controls, pixel-rate and PHYPLL controls, DISPCLK/SCLK gate controls, soft-reset registers, FBC state, per-pipe power-gating config/enable/status, DCI/DCO/MCIF memory power controls, and DCRX clock/light-sleep controls.
- Writeback and memory-interface state: MCIF writeback buffer addresses, sizes, line status, QoS, arbitration, watermarks, DMIF request limits, outstanding counters, display hub framebuffer locations, aperture locations, and DVMM fault/PTE state.
- Firmware and backlight state: DMCU firmware address ranges, ERAM/IRAM access windows, command/data mailboxes, interrupt masks/status, PWM/backlight duty-cycle registers, ABM control, luma histogram bins, and filtered min/max statistics.
- Connector, link, and pad state: DCIO/UNIPHY routing, panel power sequencing, GPIO mask/A/enable/Y registers, HPD/DDC pin state, AUX/I2C pad power and strength, DPHY/DPRX lane-training and error counters, AUX buffers, DPCD/EDID/KSV indexed data, and display-audio Azalia DMA/codec status.

Because these are direct hardware addresses, persistence depends on the hardware domain. Some registers are volatile status counters or latches, some are sticky until cleared, and others persist until block reset, display reset, suspend/resume, firmware reload, or full GPU reset.

## Dependencies And Integration Points

This file is paired with `dce_12_0_sh_mask.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`. The offset header gives the register address and base-index selector; the shift/mask header gives field layout; the SOC15/IP headers define the segment base values.

Observed direct include sites in this repository include:

- `display/dc/dce120/dce120_timing_generator.c`, where DCE 12.0 register addresses feed timing-generator reads and register updates through `dm_read_reg_soc15`, `generic_reg_update_soc15`, and `generic_reg_set_soc15`.
- `display/dc/gpio/dce120/hw_translate_dce120.c`, where `REG()` and `REGI()` macros translate raw register offsets into logical GPIO IDs and pin-enable selectors.
- `display/dc/irq/dce120/irq_service_dce120.c`, where `SRI()` composes per-instance register addresses for HPD, HPD RX, page-flip, vblank, and vupdate IRQ table entries.
- `display/dc/hwss/dce120/dce120_hwseq.c`, `display/dc/resource/dce120/dce120_resource.c`, and related DCE 12.0 display code that include this header for ASIC-specific register programming.
- `amdgpu/gmc_v9_0.c`, which includes DCE 12.0 offset and mask headers alongside memory-controller headers for display/MMHUB-related setup and diagnostics.

Integration also depends on naming consistency. Code generation and macro expansion rely on exact `mm` prefixes, block/instance names such as `MCIF_WB0`, and paired `_BASE_IDX` names. A rename or missing paired macro causes build-time failures; a wrong value compiles but can redirect MMIO to the wrong register or segment.

## Risks And Edge Cases

The central risk is mismatch between this generated register map and the actual DCE 12.0 ASIC register database. A wrong offset or base index is not type-checkable and can corrupt unrelated display hardware state.

Specific high-risk areas in this chunk are:

- Base-index selection. Many small offsets overlap numerically across base segments, so `mmREG` alone is not a full address. Using the wrong `*_BASE_IDX` can silently target a different address space.
- Intentional register aliases. VGA, DAC, PLL, PPLL, FBC, and DAC macro names share offsets in places. Tooling that assumes one name per offset would report false conflicts or generate incorrect deduplicated mappings.
- Power/reset/clock registers. Incorrect values for `DCCG_*`, `PIPE*_PG_*`, `DCI_MEM_PWR_*`, `DCO_*`, `DIG_SOFT_RESET*`, `DCIO_SOFT_RESET`, or `DCRX_*` can blank displays, wedge register access, or break suspend/resume.
- Writeback memory programming. Misaddressing `MCIF_WB*`, `WB_*`, `CNV_*`, or `WBSCL_*` can write frames to wrong surfaces, use stale watermarks, overflow scaler paths, or produce incorrect CRC/test results.
- Firmware and mailbox registers. Wrong `DMCU_*`, `MASTER_COMM_*`, or `SLAVE_COMM_*` offsets can prevent firmware load, lose interrupts, or desynchronize host/microcontroller communication.
- GPIO and connector handling. Bad `DC_GPIO_*`, `DC_I2C_*`, `GENERIC_I2C_*`, HPD, AUX, DDC, or UNIPHY/DCIO offsets can break monitor detection, EDID reads, link routing, panel power sequencing, or hotplug interrupts.
- Audio and receiver blocks. Incorrect `AZALIA_*`, `DPRX_AUX_*`, `DPRX_DPHY_*`, and `DPHY_*` offsets can break display audio, AUX transactions, DP receiver emulation/test paths, DPCD/EDID indexed data, or lane error reporting.
- Chunk boundary. This research covers only lines 1-2497. The full `dce_12_0_offset.h` continues beyond the initial `DCRX_PHY_MACRO_CNTL_RESERVED*` area, so full-file conclusions require later chunk research before reconciliation.

## Test Signals

There are no direct unit tests for this header. Useful validation is indirect:

- Build coverage of DCE 12.0 display, GPIO, IRQ, hardware-sequencing, and GMC code catches missing or renamed macros and broken macro-pasting patterns.
- Register-address smoke tests or debug traces can verify that `BASE(mmREG_BASE_IDX) + mmREG` matches the expected SOC15 physical address for representative registers from each segment, especially duplicated-offset families.
- Display bring-up tests should exercise CRTC timing, clock programming, vblank/vupdate interrupts, page-flip interrupts, FBC, per-pipe power gating, suspend/resume, and display reset paths.
- Connector tests should cover HPD interrupts, DDC/I2C EDID reads across all DDC lines, AUX transactions, panel power/backlight PWM, GPIO translation, and UNIPHY routing.
- Writeback/capture tests should validate MCIF writeback buffer programming, WB/CNV/WBSCL scaling and color conversion, CRC result registers, backpressure counters, and watermark/QoS behavior.
- DMCU and ABM tests should load firmware, exchange host/microcontroller commands, verify DMCU interrupt status/masks, drive PWM/ABM state, and check luma histogram/statistic registers.
- Audio and receiver diagnostics should verify Azalia DMA/codec register programming, audio DTO behavior, DPRX AUX buffer/index access, DPCD/EDID indexed data, lane training/status, and DPHY error counters.

For source-level review, compare this chunk against the authoritative AMD DCE 12.0 register database or a known-good upstream generated header. Runtime tests should focus on the consumers that combine these offsets with `dce_12_0_sh_mask.h` fields and SOC15 base addresses.

### subset-b-001530: lines 2498-5107

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 2498-5107

## Chunk Scope

This chunk is a generated AMD DCE 12.0 register-offset header segment. It contains 2,406 `#define` lines representing 1,203 MMIO register offset macros plus one `_BASE_IDX` companion macro for each register. The range starts at `mmDCRX_PHY_MACRO_CNTL_RESERVED16` on line 2498 and ends at `mmDCP2_GRPH_SURFACE_OFFSET_Y` on line 5106. It is partial at both ends: DCRX/DP receiver definitions begin in the preceding chunk, and the `DCP2` display pipe instance continues after this chunk.

## Purpose

The chunk provides symbolic register addresses for the DCE 12.0 display engine in AMDGPU. These offsets are consumed by DCE 12 display, interrupt, GPIO, resource, and memory-management code through `dce/dce_12_0_offset.h`, typically together with `dce/dce_12_0_sh_mask.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`. The macros are not functions; they are compile-time constants that let shared DCE helper code address the correct SOC15 display registers for Vega-era DCE 12 hardware.

The generated pattern is:

- `mm<REGISTER_NAME>`: a register offset in the DCE register space.
- `mm<REGISTER_NAME>_BASE_IDX`: the register base-index selector, almost always `2` in this chunk.

## Register Families Covered

The first large section is the tail of the DCRX/DisplayPort receiver physical macro control space. Lines 2498-3257 define `mmDCRX_PHY_MACRO_CNTL_RESERVED16` through `mmDCRX_PHY_MACRO_CNTL_RESERVED379` at offsets `0x2c16` through `0x2d81`. The reserved naming indicates hardware-reserved or PHY-internal controls exposed by the ASIC register database. These should be treated as ABI-like hardware addresses even though most higher-level driver code should not directly program them without an ASIC-specific sequence.

Lines 3258-3271 define display audio transport controls and CRC test registers:

- `mmI2S0_CNTL`, `mmI2S1_CNTL`, and status/CRC data registers.
- `mmSPDIF0_CNTL`, `mmSPDIF1_CNTL`, and CRC test data registers.
- `mmCRC_I2S_CONT_REPEAT_NUM` and `mmCRC_SPDIF_CONT_REPEAT_NUM`.
- `mmZCAL_MACRO_CNTL_RESERVED0` through `mmZCAL_MACRO_CNTL_RESERVED4`.

Lines 3272-3527 define Azalia audio index/data windows:

- `AZF0STREAM0` through `AZF0STREAM15`, each with `AZALIA_STREAM_INDEX` and `AZALIA_STREAM_DATA`.
- `AZF0ENDPOINT0` through `AZF0ENDPOINT7`, each with `AZALIA_F0_CODEC_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_ENDPOINT_DATA`.
- `AZF0INPUTENDPOINT0` through `AZF0INPUTENDPOINT7`, each with `AZALIA_F0_CODEC_INPUT_ENDPOINT_INDEX` and `AZALIA_F0_CODEC_INPUT_ENDPOINT_DATA`.

Lines 3528-4305 define the first full display pipe instance, pipe 0:

- `DCP0` graphics plane, cursor, color pipeline, LUT, gamma, regamma, CRC, DVMM/PTE, flip, XDMA, alpha, and surface counter registers.
- `LB0` line buffer format, memory, vline/vblank status, keyer color, buffer urgency/status, and MVP control registers.
- `DCFE0` clock, reset, memory power, misc, and flush registers.
- `DC_PERFMON3` display performance counter and performance monitor registers.
- `DMIF_PG0` display memory interface pipe arbitration, watermark, urgency, stutter, low-power, repeater, and DVMM status registers.
- `SCL0` scaler coefficient RAM, mode, tap/filter setup, viewport, overscan, update, and mode-change detection registers.
- `BLND0` blender control, update, underflow interrupt, update lock, and status registers.
- `CRTC0` timing generator registers for horizontal/vertical timing, sync, trigger, flow control, blanking, interlace, status counters, snapshots, update locks, test patterns, MVP, vertical interrupts, CRC windows/data, external timing sync, static screen, 3D, GSL, range timing, and DRR.
- `FMT0` formatter clamp, dynamic expansion, bit-depth, dither seeds, CRC masks/signatures, side-by-side stereo, and 4:2:0 hblank early-start registers.

Lines 4306-5083 repeat the same pipe topology for pipe 1 at the `0x800` instance base: `DCP1`, `LB1`, `DCFE1`, `DC_PERFMON4`, `DMIF_PG1`, `SCL1`, `BLND1`, `CRTC1`, and `FMT1`. The offsets advance by `0x200` from the corresponding pipe-0 macro values in this chunk, while the address-block comments show the hardware instance base as `0x800`.

Lines 5084-5107 begin pipe 2 at base address `0x1000`, defining only the opening `DCP2` graphics-plane registers visible in this chunk: graphics enable/control, LUT bypass, swap control, primary/secondary surface addresses and high parts, pitch, and surface X/Y offsets.

## Important APIs, Types, And Macros

No C functions, structs, or enums are declared in this range. The important exported interface is the macro namespace itself. Downstream code uses macros such as `mmCRTC0_CRTC_CONTROL`, `mmCRTC1_CRTC_CONTROL`, `mmDCP0_GRPH_ENABLE`, and their `_BASE_IDX` constants in SOC15 register access helpers.

Representative integration patterns visible elsewhere in the tree:

- `display/dc/resource/dce120/dce120_resource.c` builds `dce120_tg_offsets[]` by subtracting `mmCRTC0_CRTC_CONTROL` from each pipe's `mmCRTCx_CRTC_CONTROL`. This makes the generated per-pipe spacing part of the timing-generator object model.
- `display/dc/dce120/dce120_timing_generator.c` reads `mmCRTC0_CRTC_CONTROL` with a per-instance offset through `dm_read_reg_soc15()` and decodes fields using `dce_12_0_sh_mask.h`.
- `display/dc/irq/dce120/irq_service_dce120.c`, GPIO factory/translation code, and hardware sequencing code include this header so DCE 12 register lists resolve to numeric SOC15 addresses.

## Control Flow

This header has no runtime control flow. Its operational flow is indirect:

1. DCE 12 modules include this file and the matching shift/mask header.
2. Resource construction computes per-instance offsets from a canonical pipe-0 macro.
3. Register helper macros and functions combine the base register macro, `_BASE_IDX`, SOC15 IP base, and instance offset.
4. Display code reads or writes hardware state for timing generation, plane programming, scaler setup, color management, interrupts, and audio endpoint access.

Because the offset macros are constant inputs to register access, a wrong value changes runtime behavior silently: code still compiles, but it reads or writes a different hardware register.

## State And Persistence Behavior

The file itself stores no software state and performs no persistence. The macros describe stateful hardware registers. Relevant hardware state categories exposed in this chunk include:

- Persistent-until-reprogrammed display pipe configuration: plane surface addresses, pitch, viewport, scaler coefficients, color matrices, LUT/regamma data, cursor state, timing totals, sync positions, blanking, formatter bit depth, and blender controls.
- Volatile hardware status: line buffer levels, vblank/vline status, CRTC counters, interrupt status, CRTC snapshots, performance counter values, CRC data, underflow status, and DMIF/DVMM status.
- Power/reset controls: `DCFE*_DCFE_CLOCK_CONTROL`, `DCFE*_DCFE_SOFT_RESET`, memory power controls/status, DCRX clock/light-sleep/gate controls inherited from the adjacent DCRX section, and the reserved PHY/ZCAL regions.

Many registers in DCE are double-buffered or latched by update-lock/update-control registers. The header only names the offsets; correctness depends on callers observing the programming sequence in the display core.

## Dependencies

This chunk depends on the ASIC register generator contract and the DCE 12 register map. The immediate compile-time dependencies are consumers that expect:

- Stable macro names shared with generated register-list macros in DCE 12 display objects.
- Matching field definitions in `dce_12_0_sh_mask.h`.
- SOC15 addressing helpers that understand `_BASE_IDX` values and DCE IP base selection.
- Instance spacing consistency between pipe blocks, especially the pipe offset computations from `mmCRTCx_CRTC_CONTROL - mmCRTC0_CRTC_CONTROL`.

The chunk has no include dependencies of its own beyond the file-level include guard defined earlier in the header.

## Integration Points

Primary integration is the AMDGPU display core for DCE 12:

- Timing generator: `CRTC0` and `CRTC1` offsets support mode timing, blanking, vblank/vupdate interrupts, CRC capture, DRR, test pattern, stereo/3D, and external timing sync.
- Plane and color management: `DCP0`/`DCP1` offsets support scanout surface programming, flips, cursor programming, input/output CSC, gamut remap, degamma/regamma, LUT access, alpha, dithering, and CRC.
- Memory/display fetch: `DMIF_PG0`/`DMIF_PG1`, `LB0`/`LB1`, and `DCFE0`/`DCFE1` support buffer fetch arbitration, watermarks, urgency, low-power, line buffer status, and display frontend flush/reset.
- Scaler and formatter: `SCL0`/`SCL1`, `BLND0`/`BLND1`, and `FMT0`/`FMT1` support viewport scaling, overscan, blending, output formatting, clamping, bit depth, dithering, stereo, and output CRC.
- Audio: `I2S`, `SPDIF`, and `AZF0*` stream/endpoint index/data windows expose display audio routing/control surfaces.
- Diagnostics: `DC_PERFMON3` and `DC_PERFMON4`, DCP/FMT/CRTC CRC registers, audio CRC registers, and numerous status registers are test and debug hooks.

## Risks

The main risk is offset drift. These constants are hardware ABI data; hand edits or generator mistakes can cause register writes to hit the wrong block, especially because pipe instances are regular and errors may look like programming the wrong CRTC or plane.

The `_BASE_IDX` values are as important as the offsets. A correct hex offset with a wrong base index can address the wrong SOC15 segment.

Reserved DCRX PHY and ZCAL registers are risky because their names do not document semantics. Any caller using them must rely on vendor sequencing or adjacent shift/mask documentation. Blind use can affect link training, receiver PHY state, or display/audio stability.

Partial chunk boundaries are a reconciliation risk. The DCRX block begins before line 2498, and `DCP2` continues after line 5107, so file-level conclusions about the complete DCE 12 register map require adjacent chunk reports.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/display runtime signals:

- Kernel build of AMDGPU display code succeeds with `dce_12_0_offset.h` and `dce_12_0_sh_mask.h` included together.
- Static checks confirm every non-`_BASE_IDX` macro in this chunk has a companion `_BASE_IDX`; this chunk has 1,203 such pairs.
- Pipe-offset sanity checks confirm `CRTC1`, `DCP1`, `LB1`, `SCL1`, `BLND1`, and `FMT1` offsets maintain the expected pipe spacing from pipe 0 and match `dce120_tg_offsets[]` assumptions.
- Display smoke tests on DCE 12 hardware: modeset, page flip, cursor update, vblank interrupt, CRC capture, scaling, color/gamma programming, and suspend/resume.
- Audio-over-display tests for I2S/SPDIF/Azalia stream and endpoint programming.
- Debug/perf validation through `DC_PERFMON3/4`, CRTC/FMT/DCP CRC reads, and underflow/urgency status monitoring.

### subset-b-001531: lines 5108-7637

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h

## Scope
This chunk covers lines 5108-7637 of `dce_12_0_offset.h`, the third generated slice of the AMD DCE 12.0 display-controller offset header. The covered region starts inside the `DCP2` register block at `mmDCP2_GRPH_X_START` and ends at `mmDCP5_DVMM_PTE_CONTROL_BASE_IDX`, so it is primarily the repeated register vocabulary for display pipes 2, 3, 4, and the beginning of pipe 5.

## Purpose
The chunk defines preprocessor constants for memory-mapped DCE 12.0 register offsets and their SOC15 base-segment indices. It has no executable code; its purpose is to let AMDGPU display code refer to hardware registers by generated symbolic names such as `mmDCP3_GRPH_PRIMARY_SURFACE_ADDRESS`, `mmCRTC4_CRTC_CONTROL`, or `mmSCL2_SCL_MODE` instead of hard-coded numeric offsets.

Every register name in this chunk has a paired `*_BASE_IDX` macro, and all paired base indices in this slice are `2`. Consumers combine `DCE_BASE__INST0_SEG2` from `vega10_ip_offset.h` with the `mm...` offset to form the final MMIO address used by SOC15 register helpers.

## Important APIs, types, and functions
There are no C functions, types, enums, or variables. The API surface is the macro namespace guarded by `_dce_12_0_OFFSET_HEADER`.

The important register groups in this chunk are:

- `mmDCP2_*`, `mmDCP3_*`, `mmDCP4_*`, and partial `mmDCP5_*`: display controller pipe registers for primary graphics surfaces, flip/update control, surface addresses, compression metadata, outstanding request limits, prescale values, input and output color-space conversion, gamut remap, dithering, cursor registers, LUT access, CRC, DVMM PTE controls, regamma LUT programming, and surface counters.
- `mmLB2_*`, `mmLB3_*`, and `mmLB4_*`: line-buffer and MVP line-buffer registers for data format, memory power control/status, debug state, vertical counter state, blanking control, and MVP output format.
- `mmDCFE2_*`, `mmDCFE3_*`, and `mmDCFE4_*`: front-end clock control, memory power control/status, power-on delay, debug, and flush registers.
- `mmDMIF_PG2_*`, `mmDMIF_PG3_*`, and `mmDMIF_PG4_*`: display memory interface pipe arbitration, watermark mask, urgency, stutter, low-power, buffer, DVMM debug, and status registers.
- `mmDC_PERFMON5_*`, `mmDC_PERFMON6_*`, and `mmDC_PERFMON7_*`: display performance monitor control, counter state, counter-value, and high/low counter registers.
- `mmSCL2_*`, `mmSCL3_*`, and `mmSCL4_*`: scaler coefficient RAM, tap/control, viewport, scale ratio, filter init, recout, overscan, bypass, and mode-change mask registers.
- `mmBLND2_*`, `mmBLND3_*`, and `mmBLND4_*`: blender control, VGA control, memory power, underflow, and update status registers.
- `mmCRTC2_*`, `mmCRTC3_*`, and `mmCRTC4_*`: timing-generator and scanout registers for blanking, totals, sync, active area, interlace, stereo, master update, vertical interrupt positions, status, count, trigger delay, black/color, overscan, static screen, 3D structure, global swap lock, manual flow control, CRC, test pattern, double-buffering, and dynamic refresh-rate control.
- `mmFMT2_*`, `mmFMT3_*`, and `mmFMT4_*`: output formatter clamp, dynamic expansion, bit depth, dithering seeds, temporal dithering pattern, memory control, 420 memory control, and early hblank registers.

## Control flow
This header chunk has no runtime control flow. Its only local control-flow effect is participation in the header include guard declared near the start of the file.

Runtime control flow is in consumers that expand register-list macros. `dce120_resource.c` includes this offset header with `dce_12_0_sh_mask.h`, `soc15_hw_ip.h`, and `vega10_ip_offset.h`. It defines `BASE(seg)` as `DCE_BASE__INST0_SEG##seg`, then expands macros such as `SRI(reg_name, block, id)` into `BASE(mm..._BASE_IDX) + mm...`. That is how instance-specific structures such as `mi_regs[]`, `ipp_regs[]`, `xfm_regs[]`, timing-generator offsets, and hardware sequencer register tables receive concrete MMIO offsets.

For this chunk specifically, `dce120_resource.c` builds six pipe instances. Entries for instance IDs 2, 3, and 4 consume the complete `DCP/LB/DCFE/DMIF/SCL/BLND/CRTC/FMT` sets in this slice, while instance 5 starts here and continues in the next chunk. `dce120_timing_generator.c` then uses the computed CRTC offset in helpers such as `dm_read_reg_soc15()`, `generic_reg_update_soc15()`, and `generic_reg_set_soc15()` so common CRTC0 field definitions can be applied to CRTC2/3/4 by adding the pipe offset.

## State and persistence behavior
The macros persist no software state. They address volatile GPU hardware state in the DCE display pipeline. The state reachable through this chunk includes:

- scanout framebuffer addresses, pitches, format, compression surfaces, and in-use surface-address state;
- flip/update and lock state used to coordinate surface updates with vblank;
- cursor position, hotspot, size, colors, address, stereo, request filtering, and cursor update lock state;
- input gamma, degamma, LUT, regamma, color-space conversion, gamut remap, clamp, rounding, dither, and CRC state;
- scaler coefficients, viewport dimensions, scaling ratios, filter setup, recout dimensions, and overscan;
- timing-generator totals, sync, blanking, trigger, interrupt, status, CRC, test pattern, dynamic refresh-rate, and global swap-lock state;
- DMIF pipe arbitration, watermark, urgency, stutter, low-power, DVMM, and buffer state;
- DCFE/LB/FMT/BLND power and formatting state;
- display performance counter configuration and counter values.

Any persistence across suspend/resume, GPU reset, modeset, or display hotplug is owned by higher-level AMDGPU DC resource, hardware-sequencer, timing-generator, memory-input, transform, IPP, OPP, and DMIF programming paths. The header only supplies the generated numeric ABI those paths use.

## Dependencies
The chunk itself depends only on the C preprocessor and the file-level include guard. Correct use depends on:

- `dce_12_0_sh_mask.h`, which supplies field shifts and masks matching these DCE 12.0 register names;
- `vega10_ip_offset.h`, especially `DCE_BASE__INST0_SEG2`, used by `BASE(mm..._BASE_IDX)` in DCE120 resource setup;
- `soc15_hw_ip.h` and AMDGPU SOC15 register helper infrastructure;
- display DC headers that define the register-list expansion macros, including `dce_mem_input.h`, `dce_ipp.h`, `dce_transform.h`, `dce_opp.h`, `dce_hwseq.h`, and DCE120 timing-generator/resource code;
- ASIC/IP selection that actually uses the DCE 12.0 layout. Cross-generation DCE and DCN headers carry similar names but not necessarily identical offsets.

## Integration points
The direct include sites for this header include `amdgpu/gmc_v9_0.c`, `display/dc/resource/dce120/dce120_resource.c`, `display/dc/dce120/dce120_timing_generator.c`, and `display/dc/hwss/dce120/dce120_hwseq.c`.

`dce120_resource.c` is the main structural integration point. It turns the `mm...` constants into `struct dce_mem_input_registers`, `struct dce_ipp_registers`, `struct dce_transform_registers`, hardware sequencer registers, stream encoder registers, audio registers, and timing-generator offsets. For the registers in this chunk:

- memory input setup uses DCP and DMIF_PG macros from `MI_DCE12_REG_LIST(id)`;
- IPP setup uses DCP cursor, prescale, gamma, degamma, and LUT macros;
- transform setup uses LB, DCP color/remap/regamma, SCL, and related formatting macros;
- OPP/output formatting uses FMT macros;
- timing-generator code uses CRTC offsets for pipe-specific register reads and updates;
- hardware sequencing and modeset paths rely on the same generated offsets when coordinating display pipe updates.

`dce120_timing_generator.c` shows the pipe-offset model clearly: it reads `mmCRTC0_CRTC_STATUS` plus `tg110->offsets.crtc`, where `offsets.crtc` is calculated as `mmCRTCn_CRTC_CONTROL - mmCRTC0_CRTC_CONTROL`. Thus the CRTC2/3/4 constants in this chunk are part of the arithmetic that maps generic CRTC0-oriented helper code onto a selected pipe.

## Risks and edge cases
The main risk is generated-register drift. These values are hardware ABI data; a single wrong offset or base index can redirect reads and writes to the wrong display pipe or wrong register within a pipe. That can cause black screens, unstable modesets, missed vblank/update events, corrupted color processing, stale cursor state, broken scaling, or unsafe power/clock behavior.

The repeated pipe layout is regular but should not be inferred by consumers. This chunk shows mostly complete blocks for instances 2-4 and only the beginning of instance 5. Code must continue to use generated symbols rather than deriving offsets from a fixed stride unless the owning register-list code already encodes that relationship.

All base indices in this chunk are `2`. Consumers that open-code offsets without adding `DCE_BASE__INST0_SEG2` will address the wrong MMIO location. Conversely, any future regenerated header that changes a base index requires the resource-list expansion macros to keep using `BASE(mm..._BASE_IDX)`.

Some register names imply side effects or synchronization-sensitive access. Surface update, flip, interrupt status/control, CRC, test pattern, master update lock, global swap lock, DMIF low-power/stutter, memory power control, and DVMM/PTE registers should be programmed only through the display-core sequencing that understands vblank, double-buffering, power state, and reset ordering.

The chunk boundary is inside a repeated DCP instance. `DCP2` begins in the previous chunk and `DCP5` continues in the next chunk, so per-file reconciliation must merge adjacent chunk research before making whole-file conclusions about complete instance coverage.

## Test signals
Useful validation signals are mostly compile-time and display integration oriented:

- Build AMDGPU DC with DCE12 support and confirm `dce120_resource.c`, `dce120_timing_generator.c`, `dce120_hwseq.c`, and `gmc_v9_0.c` compile with this offset header and `dce_12_0_sh_mask.h`.
- Modeset testing on DCE 12.0 hardware with active pipes 2, 3, and 4, checking that scanout, scaling, color management, cursor, vblank, and page flips work on each pipe.
- Multi-monitor tests that exercise pipe instances beyond 0/1, since this chunk primarily covers instances 2-4 and the start of 5.
- Suspend/resume and GPU reset tests verifying that DCP, CRTC, SCL, FMT, DMIF, LB, DCFE, BLND, and color/LUT state is restored by higher-level DC sequences.
- Hardware register traces comparing `BASE(mm..._BASE_IDX) + mm...` for representative registers such as `mmDCP3_GRPH_PRIMARY_SURFACE_ADDRESS`, `mmCRTC4_CRTC_CONTROL`, `mmSCL2_SCL_MODE`, and `mmFMT4_FMT_BIT_DEPTH_CONTROL` against AMD's generated register database.
- Negative signals include wrong-pipe register writes, cursor only failing on higher-index pipes, incorrect color transform after enabling CRTC2-4, missed vblank interrupts, underruns/underflows in BLND/DMIF status, or scaler/FMT behavior diverging only on pipe instances covered by this chunk.

### subset-b-001532: lines 7638-10215

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 7638-10215

## Purpose

This chunk is a generated AMD DCE 12.0 display-engine register-offset map. It contains only C preprocessor `#define` constants; there are no functions, structs, enums, local variables, branches, or executable statements. The constants name direct MMIO-style register offsets and each offset's `*_BASE_IDX` selector for SOC15 base-address calculation.

The covered range starts in the tail of the DCP5 graphics/color pipeline and then defines the remaining pipe-5 display blocks, virtual display blocks, hotplug/AUX blocks, and the beginning of the first digital encoder and DisplayPort block. Major register families in this chunk are:

- the tail of `DCP5`, covering DCP CRC, DVMM/PTE arbitration, flip-rate, GSL, line-buffer gap, stereo sync, hardware rotation, XDMA underflow/recovery, regamma piecewise-linear tables, alpha control, and surface counters;
- pipe-5 `LB5`, `DCFE5`, `DMIF_PG5`, `SCL5`, `BLND5`, `CRTC5`, and `FMT5` registers for line-buffer, frontend, display memory interface, scaler, blender, timing generator, and formatter programming;
- virtual pipe instances `UNP0/LBV0/SCLV0/COL_MAN0/DCFEV0/DMIFV_PG0/BLNDV0/CRTCV0` and `UNP1/LBV1/SCLV1/COL_MAN1/DCFEV1/DMIFV_PG1/BLNDV1/CRTCV1`;
- hotplug detect instances `HPD0` through `HPD5`;
- display performance monitor instances `DC_PERFMON8`, `DC_PERFMON11`, `DC_PERFMON12`, and `DC_PERFMON2`;
- AUX channel instances `DP_AUX0` through `DP_AUX5`;
- the first digital encoder block `DIG0`, including DIG front/back-end, HDMI, AFMT audio/infoframe, TMDS, CRC, FIFO, and lane-enable registers;
- the first entries of `DP0`, from DP link control through video M/N timing.

The practical purpose is to give DCE 12.0 AMDGPU/DC code stable symbolic names for hardware register offsets. Runtime code combines these constants with SOC15 segment bases, companion field masks, and per-instance offset tables to program display modes, scanout, interrupts, hotplug, AUX transactions, color processing, audio packets, and link state.

## Important APIs, Types, And Macros

There are no runtime APIs or C types in this chunk. The interface is the generated macro namespace:

- `mmBLOCK_REGISTER` macros hold register offsets, for example `mmCRTC5_CRTC_CONTROL`, `mmDP_AUX5_AUX_CONTROL`, `mmDIG0_HDMI_CONTROL`, and `mmUNP1_UNP_GRPH_ENABLE`.
- Every register macro in this range is paired with `mm..._BASE_IDX`, almost always `2`, which consumers pass through `DCE_BASE__INST0_SEG...` style SOC15 base selectors before adding the offset.
- Instance-specific names encode the hardware block and instance directly. For example `mmHPD3_DC_HPD_INT_CONTROL` belongs to HPD instance 3, while `mmDP_AUX4_AUX_SW_CONTROL` belongs to AUX instance 4.
- The chunk does not define bit fields. Callers must use the companion `dce_12_0_sh_mask.h` masks/shifts and generated field helpers.

Important macro families in the covered lines include:

- `mmDCP5_*`: register-gamma LUT/index/data, regamma control regions A/B, alpha, graphics flip/XDMA recovery/status/timeout/average-delay, DCP CRC and surface-counter registers.
- `mmLB5_*`, `mmLBV0_*`, and `mmLBV1_*`: line-buffer data format, memory control/size, desktop height, vline/vblank status, interrupt masks, sync reset selection, keyer colors, buffer urgency/status, no-outstanding-request status, and MVP flip controls.
- `mmDCFE5_*`, `mmDCFEV0_*`, and `mmDCFEV1_*`: display-controller frontend clocking, soft reset, memory power control/status, misc, flush, optional mode control, and request-counter controls.
- `mmDMIF_PG5_*`, `mmDMIFV_PG0_*`, and `mmDMIFV_PG1_*`: pipe arbitration, minimum/maximum requests, urgent/watermark controls, retry watermarks, DVMM status, and pre-processing checks.
- `mmSCL5_*`, `mmSCLV0_*`, and `mmSCLV1_*`: scaler coefficient RAM, tap controls, viewport start/size, overscan, ratios, filter initialization, autohorizontal ratio, rounding, bypass, and mode-change masks.
- `mmBLND5_*`, `mmBLNDV0_*`, and `mmBLNDV1_*`: blender control, feedthrough, alpha mode, viewport start/size, underflow interrupt, and register-update status.
- `mmCRTC5_*`, `mmCRTCV0_*`, and `mmCRTCV1_*`: timing-generator totals, blanking, sync A/B, trigger, control, blank, interlace, status, frame counter, vertical interrupt, update lock, master update, static-screen, CRC, test pattern, stereo, flow-control, snapshots, and DRR/GSL controls.
- `mmFMT5_*`: formatter clamp, dynamic expansion, bit-depth control, control, debug, temporal dither, memory power, CRC, force-output control, and 4:2:0 hblank controls.
- `mmUNP0_*` and `mmUNP1_*`: uniphy graphics enable/control, address/pitch/viewport, update, stereosync, surface-address in-use, DFQ, tiling, color-format, memory power, and rotation registers.
- `mmCOL_MAN0_*` and `mmCOL_MAN1_*`: color-management update, input CSC, prescale, gamut remap, output CSC, gamma correction LUT index/data/control, denorm, alpha, global alpha, color-keyer, cursor, degamma/regamma LUTs, and debug registers.
- `mmHPD0_*` through `mmHPD5_*`: hotplug interrupt status/control, RX interrupt timer, and toggle filter controls.
- `mmDP_AUX0_*` through `mmDP_AUX5_*`: AUX transaction control, arbitration, software data/control, status, DPHY timing/control, interrupt control, retry, GTC sync, and GTC sync status.
- `mmDIG0_*`: digital encoder control/status/test/CRC/FIFO, HDMI packet and ACR controls, AFMT audio/infoframe/generic/ISRC/60958/ramp registers, backend enable, TMDS controls, DIG version, lane enable, and AFMT control.
- `mmDP0_*`: start of DP link/video state, including link control, pixel format, MSA colorimetry/misc, DP config, video stream control, steer FIFO, timing, and M/N registers.

## Control Flow

This header chunk has no control flow. It influences runtime behavior by supplying addresses to code that performs register reads, writes, and read-modify-write operations.

The usual DCE 12.0 flow in consumers is:

1. include `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`;
2. select a SOC15 display base with `mm..._BASE_IDX`;
3. add the register offset from `mm...`;
4. optionally add or select a per-instance offset such as a CRTC pipe offset;
5. read/write the register with DC or AMDGPU helpers such as `dm_read_reg_soc15`, `generic_reg_update_soc15`, `generic_reg_set_soc15`, or resource-table register wrappers;
6. apply field masks/shifts from `dce_12_0_sh_mask.h`.

Concrete patterns in this tree include `display/dc/dce120/dce120_timing_generator.c`, which includes this offset header and reads CRTC status/frame-counter registers through `dm_read_reg_soc15`, and updates timing-generator fields through `generic_reg_update_soc15`. `display/dc/resource/dce120/dce120_resource.c` builds DCE120 instance offsets such as `mmCRTC5_CRTC_CONTROL - mmCRTC0_CRTC_CONTROL` and expands register tables with macros that add `BASE(mm..._BASE_IDX)` to `mm...`. `display/dc/irq/dce120/irq_service_dce120.c` uses instance-specific DCP, CRTC, and HPD register macros to build IRQ enable/status/ack descriptors. GPIO and AUX/link resource code follows the same base-plus-offset convention.

Because this file is only an address map, sequencing rules live outside it. Callers are responsible for update locks, vblank-safe programming, AUX transaction ordering, hotplug interrupt acknowledgment, DP/HDMI link training and packet setup, memory-interface watermarks, and reset/power-gating coordination.

## State And Persistence Behavior

The header itself stores no runtime state and performs no I/O. Its constants are compiled into driver code.

The registers named here control or expose persistent hardware state in DCE 12.0 display blocks. That state can persist until later driver writes, display modesets, hotplug handling, AUX transactions, power-gating transitions, suspend/resume restore, GPU reset, or firmware/BIOS interaction. Relevant state categories include:

- display pipe state: CRTC timing, blanking, sync, frame count, vertical interrupts, update locks, static-screen, DRR, CRC, scaler viewport/filter/tap settings, line-buffer status, formatter clamp/dither/CRC, blender viewport/alpha/underflow status, and DCP regamma/color/alpha state;
- scanout and memory-interface state: UNP graphics surface addresses, pitch, tiling, viewport, DFQ, hardware rotation, memory power, DMIF/DMIFV arbitration, watermarks, request limits, DVMM, and outstanding-request state;
- virtual-pipe state: duplicated UNP/LBV/SCLV/COL_MAN/DCFEV/DMIFV/BLNDV/CRTCV programming for virtual display paths 0 and 1;
- link and connector state: HPD interrupt/timer/filter state, AUX software transaction registers, DP AUX DPHY timing and GTC sync state, DIG0 HDMI/AFMT/TMDS/lane-enable state, and the start of DP0 link/video programming;
- diagnostic state: performance counters, CRC registers, debug registers, underflow status, retry/watermark status, and surface-counter outputs.

The macros do not encode access attributes. Some target registers are read-only status, some are write-only or self-clearing controls, some are sticky interrupt/status bits, and some are double-buffered or latched on update boundaries. Consumers must preserve reserved fields and follow the hardware-specific programming sequence.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus the include guard from the full `dce_12_0_offset.h` file. Practical integration depends on the generated AMD DCE 12.0 register set:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h` supplies masks and shifts for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c` includes this header for timing-generator status and programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c` includes this header to build DCE120 resource register tables and instance offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c` uses this header for HPD, page-flip, vblank, and vupdate IRQ register descriptors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce120/hw_translate_dce120.c` and `hw_factory_dce120.c` include this header for GPIO/HPD/DDC mapping.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c` include the companion DCE 12.0 masks and participate in generation-specific programming.
- SOC15 base headers such as `soc15_hw_ip.h` and `vega10_ip_offset.h` provide the segment-base macros used with `*_BASE_IDX`.

The path sits under a repository named `ceph-client`, but this file is AMDGPU display-driver register metadata. It does not implement Ceph filesystem behavior.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. These constants are untyped integers; using the wrong instance macro, wrong base index, wrong generation header, or wrong field-mask header can compile cleanly while touching the wrong display register.

This chunk has many repeated instance families with similar names. `HPD0` through `HPD5`, `DP_AUX0` through `DP_AUX5`, virtual pipe 0 versus 1, and pipe-5 versus base pipe macros differ by predictable but non-identical offsets. Copy/paste or generator errors can make an interrupt, AUX transaction, or pipe update affect the wrong connector or display path.

The chunk begins at line 7638 in the middle of the `DCP5` register family. Earlier DCP5 graphics, cursor, LUT, CSC, keying, degamma, gamut, and overlay registers are in the previous chunk. It ends at line 10215 after the first `DP0` video M/N entries, so the remainder of the DP0 block and later DP/DIG instances are in following chunks. File-level reconciliation should merge these boundaries before treating the DCP5 or DP0 feature coverage as complete.

Timing and latch hazards are not visible in this file. CRTC, scaler, line-buffer, formatter, color-management, and scanout-address registers may need update locks, vblank coordination, or pipe-disabled programming. AUX, HPD, DP, HDMI, AFMT, TMDS, and DIG registers have protocol-specific ordering and clear-on-write behavior. DMIF/UNP memory and watermarks can cause underflow, hangs, or corrupted scanout if programmed inconsistently with bandwidth and surface state.

Virtual-pipe registers are easy to confuse with physical pipe registers. `UNP*`, `LBV*`, `SCLV*`, `COL_MAN*`, `DCFEV*`, `DMIFV*`, `BLNDV*`, and `CRTCV*` have similar logical roles to physical DCP/LB/SCL/CRTC blocks but are not interchangeable addresses.

## Test Signals

Useful validation signals include:

- build coverage for all DCE120 translation units that include `dce_12_0_offset.h` or `dce_12_0_sh_mask.h`, especially timing-generator, resource, IRQ, GPIO, HW sequence, and GMC paths;
- generated-header checks that each `mm...` macro has the expected `mm..._BASE_IDX`, and that every register used with `REG_SET_FIELD`, `FD`, `generic_reg_update_soc15`, or IRQ table macros has a matching field definition in `dce_12_0_sh_mask.h`;
- static checks around instance arithmetic, especially pipe-5 offsets, `CRTCV0/1`, `HPD0-5`, `DP_AUX0-5`, `DIG0`, and `DP0`;
- modeset tests across all physical and virtual display paths covered by this chunk: enable/disable, vblank counter reads, update-lock behavior, DRR/static-screen, scaler/viewport changes, formatter/color-management changes, and suspend/resume;
- interrupt tests for HPD, HPD RX, page flip, vblank, vupdate, underflow, and AUX/connector events;
- DisplayPort and HDMI tests covering AUX transactions, hotplug debounce/filtering, DP link programming, HDMI/AFMT InfoFrame/audio packet programming, TMDS control, and lane-enable behavior;
- scanout stress tests covering surface address/pitch/tiling changes, XDMA underflow/recovery, UNP/DMIF watermarks, memory power transitions, and rotation;
- diagnostic tests for CRC, performance monitors, surface counters, DCP/CRTC/FMT debug paths, and DP AUX GTC sync status.

Regression symptoms from bad constants include wrong connector hotplug status, missed or stuck interrupts, AUX timeouts, blank displays, DP/HDMI link-training or audio failures, page-flip/vblank drift, underflow reports, incorrect color/gamma, corrupted scanout, or failures that only appear on pipe 5 or virtual display paths.

## Cross-Chunk Notes

This is a middle chunk of `dce_12_0_offset.h`. It starts after earlier DCE12 common, DCP, and pipe-instance definitions and continues the generated address map through DCP5, pipe 5, virtual pipes, HPD/AUX, DIG0, and the opening of DP0. The final per-file research should combine this with adjacent chunks so split logical blocks such as DCP5 and DP0 are described as complete register families.

### subset-b-001533: lines 10216-12711

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 10216-12711

## Purpose

This chunk is generated AMDGPU DCE 12.0 display-controller register metadata. It contains no executable C code; it publishes preprocessor constants that name memory-mapped display registers and their SOC15 base-index segment. Driver code combines each `mm...` offset with `DCE_BASE__INST0_SEG...` to form the final MMIO address for Vega/DCE120 display hardware.

The selected range covers the digital-output and PHY-facing part of the DCE register map. It starts inside the `DP0` register block, then defines complete repeated `DIG1` through `DIG6` and `DP1` through `DP6` blocks, then continues into `DCIO_UNIPHY0`, combo-PHY common/TX/PLL registers, and the beginning of `DCIO_UNIPHY1`. The file path lives under a local `ceph-client` source mirror, but this header is AMDGPU display hardware metadata; it has no Ceph filesystem semantics.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, or storage objects in this chunk. The macro namespace is the API surface.

Each hardware register is represented by paired macros:

- `mm<register>`: register offset within a generated DCE address space.
- `mm<register>_BASE_IDX`: SOC15 base segment selector, usually `2` in this chunk.

Important register families in this line range are:

- `mmDP0_*`: the tail of the DisplayPort 0 block, beginning at `DP_LINK_FRAMING_CNTL` and covering HBR2 eye pattern controls, VBID/video interrupts, DPHY training/scrambling/CRC, DisplayPort secondary-data packets, audio `M`/`N` values, MST/MSE slot allocation timing/status registers, and DPHY byte/symbol swap or HBR2 pattern controls.
- `mmDIG1_*` through `mmDIG6_*`: repeated digital front-end and HDMI/AFMT register groups. Each instance defines DIG control/status/test/CRC/FIFO registers, HDMI control/status/audio/ACR/infoframe/generic-packet registers, AFMT interrupt/audio/ISRC/AVI/MPEG/generic/60958/audio-source registers, TMDS control/debug/sync/balancer registers, `DIG_VERSION`, `DIG_LANE_ENABLE`, and `AFMT_CNTL`.
- `mmDP1_*` through `mmDP6_*`: repeated DisplayPort link/stream register groups matching the DP0 tail plus the full block start. They include link control, pixel format, MSA colorimetry/config/misc/timing, video stream timing and `M`/`N`, DPHY training and diagnostic controls, secondary-data/audio packet controls, MST/MSE rate and slot-allocation controls, and SAT status registers.
- `mmDCIO_UNIPHY0_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159`: reserved or macro-control aperture entries for UNIPHY0. The names do not expose field intent, but they preserve the generated hardware address layout.
- `mmDC_COMBOPHYCMREGS0_*`: combo-PHY common registers for fuse values, bias/impedance, test muxes, spare control, AFE common control, PDDQ, OPM control, mailbox, and display reserved-for-future-use registers.
- `mmDC_COMBOPHYTXREGS0_*`: combo-PHY transmitter lane registers for lanes 0-3, including command-bus TX control, DFX observation, transmitter control, coefficient/current/slew-rate control, BIST control/status, and lane-specific RFU registers.
- `mmDC_COMBOPHYPLLREGS0_*`: combo-PHY PLL registers for frequency control, spread-spectrum fractional values, debug bus control, clock/control/test, calibration controls, loop and regulator configuration, observation, and DFT output.
- `mmDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED87`: the beginning of the UNIPHY1 reserved macro-control aperture. Later lines continue this block.

The chunk is heavily repetitive by design. Counts from the requested range show 164 `#define` entries per `DIG1`-`DIG6` family, 112 per `DP1`-`DP6` family, 320 for `DCIO_UNIPHY0`, 32 for combo-PHY common, 128 for combo-PHY TX, 24 for combo-PHY PLL, and 176 for the partial `DCIO_UNIPHY1` slice. Counts include both offset and `_BASE_IDX` macros.

## Control Flow

This header has no runtime control flow. Runtime behavior appears in consumers that expand register-list macros into static register-address tables and then pass those addresses to SOC15 register helpers.

The typical DCE120 flow is:

1. A display module includes `dce_12_0_offset.h` and `dce_12_0_sh_mask.h`.
2. Resource setup macros such as `SR(reg_name)` and `SRI(reg_name, block, id)` concatenate tokens like `mmDIG1_AFMT_AVI_INFO0` or `mmDP2_DP_SEC_CNTL`, add `DCE_BASE__INST0_SEG<BASE_IDX>`, and store the resulting address in a hardware object register table.
3. Higher-level stream encoder, link encoder, IRQ, timing-generator, or memory-controller code reads or writes those addresses through `dm_read_reg_soc15()`, `generic_reg_set_soc15()`, `generic_reg_update_soc15()`, or related register-helper paths.
4. Field-level packing/unpacking uses the companion `dce_12_0_sh_mask.h` masks and shifts, not this offset header.

For this specific chunk, `dce120_resource.c` maps `DIG` and `DP` instance offsets into `stream_enc_regs[]` and `link_enc_regs[]`. `dce_stream_encoder.h` consumes many of the `DIG` AFMT/HDMI and `DP` video/audio/MSE registers to program HDMI/DP packet generation, audio metadata, DisplayPort stream timing, and MST-related state.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes stateful hardware registers in the DCE display block.

The hardware state represented here includes digital front-end enable/status, output CRC/test-pattern state, HDMI packet and audio clock-recovery programming, AFMT infoframe and audio-channel metadata, TMDS encoding/control state, DisplayPort link and stream format, MSA timing/colorimetry/VBID, DPHY training/scrambling/CRC diagnostics, secondary-data packet scheduling, DisplayPort audio `M`/`N` values, MST/MSE slot-allocation tables/status, UNIPHY macro-control space, and combo-PHY common/TX/PLL controls.

Persistence depends on the underlying register. Some registers are read-only status snapshots, some are sticky interrupt/status bits or diagnostic counters, and many are control registers that remain programmed until the display driver, firmware/BIOS, hotplug handling, link retraining, stream disable, suspend/resume, power-gating, GPU reset, or full system reset changes them. The offset header does not encode access permissions, reset values, write-one-to-clear behavior, polling requirements, or ordering constraints.

## Dependencies And Integration Points

The direct companion file is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h`, which supplies field masks and shifts for the register addresses defined here. SOC15 base constants are supplied by `soc15_hw_ip.h` and ASIC offset headers such as `vega10_ip_offset.h`.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce120/dce120_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce120/dce120_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce120/irq_service_dce120.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce120/dce120_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v9_0.c`

The most relevant consumers for this chunk are display resource and encoder construction. `dce120_resource.c` uses `SRI()` to build per-instance stream encoder and link encoder register tables. `dce_stream_encoder.h` lists `DIG` AFMT/HDMI and `DP` registers that map directly to this chunk, including AVI/generic/audio infoframes, HDMI ACR controls, DP pixel format, DP video timing, DP secondary/audio packet controls, and DP MSE controls. Link encoder setup also depends on DP DPHY-related addresses, including a local fallback for `DP_DPHY_INTERNAL_CTRL` when the generated header does not define it.

## Risks And Edge Cases

The main risk is silent hardware misaddressing. A wrong offset or `_BASE_IDX` can compile successfully while making the display stack program the wrong register, the wrong instance, or the wrong SOC15 segment.

High-risk areas include repeated instance blocks. `DIG1`-`DIG6` and `DP1`-`DP6` are structurally similar, so generation or copy errors can swap an engine instance while preserving plausible names and values. Such errors may only show when a specific display pipe, connector, or MST topology uses the affected instance.

The line boundaries are not semantic boundaries. The chunk begins after the start of `DP0`; earlier lines define the first DP0 offsets. The chunk ends in the middle of `DCIO_UNIPHY1`; later lines continue `RESERVED88` onward. The final per-file merge should treat these as chunking artifacts, not missing hardware support.

PHY and DPHY registers are especially sensitive. Incorrect DP training, scrambling, CRC, HBR2 pattern, UNIPHY macro-control, combo-PHY TX, or combo-PHY PLL addresses can break link bring-up, cause unstable high-rate DisplayPort links, corrupt lane mapping, or make diagnostic/test controls touch unintended lanes. Reserved UNIPHY macro-control names also carry risk because the generated names do not document semantics; consumers must rely on AMD hardware documentation and established driver sequences.

Packet-generation registers can create user-visible failures even when the display link stays lit. Bad HDMI/AFMT/DP secondary-packet offsets may break audio, AVI infoframes, colorimetry metadata, HDR/vendor packets carried through generic-packet paths, or MST stream allocation.

## Test Signals

Useful validation signals include:

- Kernel build coverage for DCE120/Vega display code that includes `dce_12_0_offset.h`; malformed or missing macros should fail compile-time token expansion in `SR()`/`SRI()` register tables.
- Static register-map comparison against AMD's generated DCE 12.0 source database, especially for the repeated `DIG`/`DP` instance deltas and the partial chunk boundaries.
- Display bring-up tests across all available encoders/connectors, including HDMI and DisplayPort outputs mapped to different DIG/DP instances.
- HDMI audio and infoframe validation, including ACR `N`/`CTS` behavior, channel status, AVI/MPEG/generic packets, and AFMT update/conflict status.
- DisplayPort link-training and high-bit-rate tests that inspect negotiated lane count/rate, DPHY training status, scrambling/CRC diagnostics, HBR2 patterns, and recovery after hotplug.
- MST tests that validate MSE rate, SAT programming/update/status, link timing, and multiple stream allocation.
- Suspend/resume, runtime power-management, and GPU reset tests that confirm DCE register tables still address the intended hardware after power transitions.
- Hardware debug or register-dump checks that read selected `DIGn`, `DPn`, UNIPHY, combo-PHY TX, and PLL addresses and confirm expected per-instance spacing.

Regression symptoms from bad constants include blank displays on only one connector, audio loss while video remains active, wrong colorimetry/infoframe metadata, MST stream allocation failures, DP links stuck at lower rates, repeated retraining, hotplug IRQ side effects from misaddressed display blocks, or PHY diagnostics showing activity on the wrong lane or encoder.

## Cross-Chunk Notes

Earlier chunks of `dce_12_0_offset.h` define the file guard, copyright, display performance, CRTC, HPD, DCP, AUX/I2C, DIG0, and the beginning of DP0. Later chunks continue `DCIO_UNIPHY1` and the rest of the DCE 12.0 offset namespace. The final per-file research document should describe the full header as one generated DCE register-address contract paired with `dce_12_0_sh_mask.h`.

### subset-b-001534: lines 12712-15215

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 12712-15215

## Purpose

This chunk is part of AMD's generated DCE 12.0 register-offset header. It does not implement runtime logic; it provides preprocessor constants that map display-engine register names to MMIO register offsets and base-index selectors used by the AMDGPU display stack.

The assigned range covers the display PHY register-map area for DCE 12.0. It starts in the tail of the `DCIO_UNIPHY1` reserved macro-control table, then defines repeated COMBOPHY common, transmit-lane, and PLL register blocks for PHY instances 1 through 5, and ends in the beginning of the `DCIO_UNIPHY6` reserved macro-control table.

The highest-value content is the repeated PHY programming surface:

- `DCIO_UNIPHY[1-6]_UNIPHY_MACRO_CNTL_RESERVED*` reserved macro-control offsets.
- `DC_COMBOPHYCMREGS[1-5]_COMMON_*` common combo-PHY control and fuse offsets.
- `DC_COMBOPHYTXREGS[1-5]_*_LANE[0-3]` per-lane TX command, margin/de-emphasis, and RFU offsets.
- `DC_COMBOPHYPLLREGS[1-5]_*` per-PHY PLL frequency, bandwidth, calibration, loop, regulator, observe, and DFT offsets.

These constants let display code address the low-level physical link hardware behind DisplayPort/HDMI-style outputs without embedding numeric offsets throughout the driver.

## Important APIs, Types, And Functions

There are no functions, structs, or callable APIs in this range. The exported interface is the macro namespace:

- `mm...` register-offset macros, such as `mmDC_COMBOPHYTXREGS5_CMD_BUS_TX_CONTROL_LANE2`, whose values are register offsets in the DCE 12.0 MMIO space.
- Matching `mm..._BASE_IDX` macros, all `2` in this slice, selecting the register base segment expected by AMD display register-access helpers.
- Address-block comments generated into the header, such as `dce_dc_dc_combophytxregs5_dispdec`, which group the following macros by hardware block.
- `base address` comments, which document the underlying block base used by the register generator. In this slice, COMBOPHY instances 1-2 use base address `0x320`, instances 3-5 use `0xfa0`, and `DCIO_UNIPHY6` uses `0x12c0`.

The macros are intended to be combined with the AMD display register-access infrastructure included by DCE 12.0 modules, alongside the companion `dce_12_0_sh_mask.h` bit-field definitions. Files that include this offset header include DCE 12.0 timing-generator, IRQ, GPIO, hardware-sequencer, resource, and GMC code.

## Control Flow

This chunk has no C control flow. The "flow" is compile-time symbol availability:

1. A DCE 12.0 source file includes `dce/dce_12_0_offset.h`.
2. Hardware-specific register tables or direct register-access macros use these `mm...` and `mm..._BASE_IDX` constants.
3. The driver's register access layer combines the offset and base index to read or write the corresponding MMIO register.

The generated layout is highly regular. Each PHY instance repeats the same groups:

- COMBOPHY common registers: `COMMON_FUSE1` through `COMMON_FUSE3`, `COMMON_MAR_DEEMPH_NOM`, `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, `COMMON_LANE_RESETS`, `COMMON_ZCALCODE_CTRL`, and `COMMON_DISP_RFU1` through `COMMON_DISP_RFU7`.
- COMBOPHY TX registers: four lanes, each with `CMD_BUS_TX_CONTROL`, `MARGIN_DEEMPH`, `CMD_BUS_GLOBAL_FOR_TX`, and `TX_DISP_RFU0` through `TX_DISP_RFU12`.
- COMBOPHY PLL registers: `FREQ_CTRL0` through `FREQ_CTRL3`, `BW_CTRL_COARSE`, `BW_CTRL_FINE`, `CAL_CTRL`, `LOOP_CTRL`, `VREG_CFG`, `OBSERVE0`, `OBSERVE1`, and `DFT_OUT`.
- UNIPHY reserved macro-control tables: sequential `UNIPHY_MACRO_CNTL_RESERVEDn` offsets with matching base-index macros.

The range boundaries are partial: line 12712 begins at `DCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED88`, after reserved entries 0-87 in the previous chunk; line 15215 ends at `DCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED39_BASE_IDX`, before the rest of `DCIO_UNIPHY6` in the next chunk.

## State And Persistence Behavior

The header stores no runtime state and performs no persistence. Its constants describe hardware state locations. Any persistence is in the GPU hardware registers that other driver code reads or writes using these offsets.

The state represented by this chunk is physical display-link state:

- COMBOPHY common registers can represent PHY fuses, lane power management, TX control, TMDP behavior, lane resets, impedance/calibration controls, and reserved display RFU fields.
- COMBOPHY TX lane registers can represent lane-specific transmit command bus settings, de-emphasis/margin programming, and reserved per-lane controls.
- COMBOPHY PLL registers can represent frequency programming, bandwidth controls, calibration, loop behavior, regulator configuration, observation/status, and design-for-test outputs.
- UNIPHY reserved tables reserve contiguous macro-control address space that may be hardware-defined or used by generated sequences outside hand-written driver logic.

Because these are raw hardware offsets, changing a value changes the address that later code touches. Such an edit can redirect display bring-up writes to the wrong register and cause link-training, hotplug, clock, or power-management failures.

## Dependencies

This file depends on the DCE 12.0 hardware register map produced by AMD's ASIC register-generation flow. The header guard `_dce_12_0_OFFSET_HEADER` protects the generated macro namespace from repeated inclusion.

Runtime users depend on surrounding AMDGPU display infrastructure:

- `dce_12_0_sh_mask.h` supplies the companion bit masks and shifts for register fields.
- DCE 12.0 display modules include this header to instantiate register offset tables for timing generation, IRQ routing, GPIO/DDC/AUX handling, resource construction, hardware sequencing, and memory-controller/display integration.
- Register read/write helpers depend on the `_BASE_IDX` values to select the correct MMIO base aperture. In this chunk the base index is consistently `2`.
- The constants assume DCE 12.0 silicon layout. They should not be shared with DCE, DCN, or DPCS register blocks unless the including code intentionally maps the matching ASIC generation.

The source tree also contains newer or different generated register maps with similar UNIPHY names, for example DPCS headers that use `reg...` prefixes and different offsets. Those are not interchangeable with this `mm...` DCE 12.0 namespace.

## Integration Points

The main integration point is the AMD display core's DCE 12.0 backend. PHY-related code uses the register definitions indirectly through hardware register tables and helper macros rather than hand-coding every numeric offset.

This chunk lines up with display-output programming responsibilities:

- Link initialization and training need TX lane and de-emphasis controls from `DC_COMBOPHYTXREGS*`.
- PHY power sequencing and resets need common lane power-management, TX control, TMDP, lane reset, and calibration controls from `DC_COMBOPHYCMREGS*`.
- Pixel/link clock setup and validation can depend on PLL frequency, bandwidth, calibration, loop, regulator, and observe registers from `DC_COMBOPHYPLLREGS*`.
- Board- or ASIC-specific sequences may refer to UNIPHY reserved macro-control offsets when applying generated PHY programming tables.

The repeated instance numbering is important for connector routing. Instances 1 through 5 expose similar common/TX/PLL register sets at different offsets, while the range's partial UNIPHY1 and UNIPHY6 sections are only slices of larger reserved tables.

## Risks And Edge Cases

- This is generated register-map data. Manual edits are high risk because a one-word offset or base-index mistake can compile cleanly while programming the wrong hardware register.
- The chunk starts and ends inside UNIPHY reserved tables. A line-bounded review must not treat the visible reserved ranges as complete definitions for UNIPHY1 or UNIPHY6.
- The visible repeated COMBOPHY blocks are easy to miscompare. Instances 1-5 share naming patterns but have different offset ranges; copy/paste or generator drift can create subtle instance skew.
- Most macros in the UNIPHY sections are named `RESERVED`. Their semantics are not self-documenting, but their positions can still matter for firmware, BIOS table sequences, or generated display initialization scripts.
- All `_BASE_IDX` values in this slice are `2`. Any accidental change to a different base index would route otherwise-correct offsets through the wrong MMIO aperture.
- The PLL register sequence skips one numeric offset between `LOOP_CTRL` and `VREG_CFG` for each instance. Tests or scripts that assume fully contiguous named PLL registers need to tolerate reserved holes.
- Similar macro families exist in other ASIC headers with different prefixes and offsets. Mixing DCE 12.0 `mm...` constants with DPCS `reg...` constants would be an integration bug.
- Since this header contains no type checking, incorrect use of an offset in the wrong block or instance is detected only by display behavior, hardware readback, or generated-table validation.

## Test Signals

Useful validation is mostly build-time, static, and hardware bring-up oriented:

- AMDGPU display code that includes `dce_12_0_offset.h` should compile without duplicate macro definitions or missing symbols.
- Static register-map checks should verify that every `mm...` macro has a matching `mm..._BASE_IDX` macro and that all base indices in this chunk remain `2`.
- Generator-diff checks should compare these offsets against AMD's authoritative DCE 12.0 register database and flag manual drift.
- Instance-pattern checks should confirm that `DC_COMBOPHYCMREGS[1-5]`, `DC_COMBOPHYTXREGS[1-5]`, and `DC_COMBOPHYPLLREGS[1-5]` expose the expected repeated register names with consistent per-instance spacing and the known PLL reserved hole.
- Hardware validation should cover display link bring-up on DCE 12.0 ASICs: connector detection, HPD/IRQ handling, AUX/DDC access, link training, mode set, suspend/resume, and hotplug after low-power states.
- Register readback or tracing during display initialization should show accesses landing in the expected PHY instance and lane when programming COMBOPHY common, TX, and PLL registers.
- Negative validation should ensure DCE 12.0 paths do not include or use similarly named DPCS `reg...` headers for these PHY registers.

### subset-b-001535: lines 15216-17814

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 15216-17814

## Scope And Purpose

This chunk is a generated-style AMD DCE 12.0 register offset header section. It contains C preprocessor constants only: symbolic register offsets and their paired `_BASE_IDX` values for MMIO register spaces, plus `ix...` constants for Azalia indexed registers. There are no C functions, structs, enums, or runtime branches in this range.

The mapped range starts in the middle of the `dce_dc_dcio_uniphy6_dispdec` register block, at `mmDCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED40`, and ends in the middle of `azf0inputendpoint3_inputendpointind`, at `ixAZF0INPUTENDPOINT3_AZALIA_F0_CODEC_INPUT_PIN_CONTROL_LPIB`. Full conclusions for those two boundary blocks require adjacent chunk research.

The purpose of this chunk is to expose DCE 12.0 display-engine hardware addresses for late UNIPHY6 registers, full UNIPHY8 PHY/PLL register groups, DSI0/DSI1 controller blocks, DisplayPort receiver secondary-data blocks, one display performance monitor, ZCAL/calibration registers, and the Azalia HD-audio root, stream, endpoint, and input-endpoint indirect register maps. AMDGPU display code includes this header with `dce_12_0_sh_mask.h` and uses these constants as the compile-time address layer for `dm_read_reg_soc15()`, `dm_write_reg_soc15()`, indirect Azalia helpers, and generated register tables.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace itself. The `mm...` names are direct MMIO register offsets, almost always followed by a matching `_BASE_IDX` macro selecting the SOC15 base segment. In this chunk, most display block offsets use base index `2`; Azalia root and stream descriptor offsets use base index `1`; the `ix...` endpoint constants are indexed-register offsets and do not have `_BASE_IDX` companions.

Important macro families in this chunk include:

- Partial UNIPHY6 reserved macro-control table: `mmDCIO_UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED40` through `RESERVED159` provide contiguous reserved or undocumented PHY macro-control offsets from `0x2616` through `0x268d`, all with base index `2`.
- UNIPHY6 common, TX, and PLL controls: `mmDC_COMBOPHYCMREGS6_COMMON_*` defines common fuse, deemphasis, lane power-management, TX control, lane reset, ZCAL-code, and RFU offsets; `mmDC_COMBOPHYTXREGS6_*_LANE0` through `LANE3` define per-lane command-bus, margin/deemphasis, global TX, and RFU offsets; `mmDC_COMBOPHYPLLREGS6_*` defines PLL frequency, bandwidth, calibration, loop, regulator, observe, and DFT offsets.
- Full UNIPHY8 reserved macro-control table and split PHY views: `mmDCIO_UNIPHY8_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED159` map a contiguous reserved region from `0x26b6` through `0x2755`. The same physical address range is also named through `mmDC_COMBOPHYCMREGS8_COMMON_*`, `mmDC_COMBOPHYTXREGS8_*_LANE*`, and `mmDC_COMBOPHYPLLREGS8_*`, giving consumers semantic names for common, lane TX, and PLL subblocks.
- DSI controllers: `mmDSI0_*` and `mmDSI1_*` define parallel MIPI DSI controller blocks. Each block includes display DSI control/status, clock, trigger, command, timing, PHY, lane, escape-mode, packet, virtual-channel, power, memory, and debug-style registers. The two blocks are separated by a regular offset stride: DSI0 starts at `0x27be`, while DSI1 starts at `0x28be`.
- DPRX secondary-data blocks: `mmDPRX_SD0_*` and `mmDPRX_SD1_*` provide DisplayPort receiver secondary-data control, video stream ID, SDP receive/acknowledge, MSA/VBID, timestamp, audio/MST/MSE activity, CRC, packet status, debug, and multi-stream allocation handled-state offsets. These support receiver-side DP status and packet tracking.
- Performance monitor and calibration: `mmDC_PERFMON10_*` defines the perf-counter control, state, count, high/low, and interrupt-misc offsets for display performance monitor instance 10. `mmCOMP_EN_CTL`, `mmZCAL_CTRL`, and `mmZCAL_FUSES` expose common impedance/calibration control and fuse state.
- Sparse or empty address block markers: the chunk contains `addressBlock` comments for VGA page-address and `dce_dc_dispdec[948..986]` ranges, but no `#define` lines inside this mapped interval. Those comments preserve generated register-database structure across chunk boundaries.
- Azalia root/controller MMIO registers: `mmCORB_*`, `mmRIRB_*`, `mmIMMEDIATE_COMMAND_*`, `mmAZROOT_*`, `mmAZENDPOINT_*`, `mmDMA_*`, `mmWALL_CLOCK_COUNTER`, and aliases expose the HD-audio command output ring buffer, response input ring buffer, immediate command interface, codec write control, endpoint index/data ports, DMA position buffer, and wall-clock counter.
- Azalia output stream descriptor MMIO registers: `mmAZSTREAM0_*` through `mmAZSTREAM7_*` define eight output stream descriptor blocks. Each block repeats control/status, link-position, cyclic-buffer length, last-valid index, FIFO size, format, BDL pointer, and link-position alias offsets.
- Azalia stream indirect registers: `ixAZF0STREAM0_*` through `ixAZF0STREAM15_*` define 16 stream-indexed FIFO/response/request counters: FIFO size control, FIFO information, FIFO index, FIFO data, and cumulative request count.
- Azalia output endpoint indirect registers: `ixAZF0ENDPOINT0_*` through `ixAZF0ENDPOINT7_*` define eight endpoint maps, each with 71 converter and pin-control offsets. They cover audio widget capabilities, converter format and stream ID, digital converter state, supported formats/rates, stripe/ramp/GTC controls, pin capabilities, unsolicited response, pin sense, widget control, speaker/channel metadata, audio descriptors 0-13, multichannel and HBR controls, lipsync, sink info, hotplug, configuration defaults, channel-status overrides, LPIB snapshots, coding/format-change state, wireless display identification, remote keepalive, and audio enabled/disabled/format-change interrupt status.
- Azalia input endpoint indirect registers: `ixAZF0INPUTENDPOINT0_*` through the partial `ixAZF0INPUTENDPOINT3_*` block define input converter and input pin-control offsets. Complete input endpoints 0-2 include format, stream ID, digital converter, supported formats/rates, input pin capabilities, unsolicited response, input pin sense, widget control, multichannel/HBR, channel allocation, hotplug, configuration default, LPIB snapshots, input status control, and infoframe offsets.

## Control Flow And Data Flow

This header chunk has no executable control flow. Its data flow is compile-time substitution into register access sequences. A caller selects a macro such as `mmDSI0_DISP_DSI_CTRL` or `mmAZSTREAM0_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`, combines it with the appropriate SOC15 base index or per-instance offset machinery, and then reads or writes the resulting hardware register.

The implied hardware flows are:

- PHY programming flows use the UNIPHY and COMBOPHY names to configure or inspect common PHY fuses, lane power, TX command/margin state, lane resets, PLL frequency/bandwidth/calibration, and debug/DFT observation state. The generated header intentionally exposes both reserved raw macro-control names and semantic common/TX/PLL aliases over overlapping address ranges.
- DSI bring-up uses DSI control, clock, lane, command, timing, packet, and PHY offsets to enable a panel link, send commands, configure escape/low-power behavior, program display timings, and monitor status/error/debug registers.
- DPRX flows read or program secondary-data and MSA/VBID state, track received SDP/audio/MST/MSE activity, handle ACT and allocation notifications, and inspect CRC or packet-status fields for validation and diagnostics.
- Performance-monitor flows configure monitor 10, start or stop counter collection, read high/low counter values, and handle interrupt/misc state.
- Azalia controller flows use CORB/RIRB and immediate-command registers to exchange HD-audio codec verbs and responses. Endpoint index/data registers provide another path to the codec endpoint indirect register space.
- Azalia stream flows program stream descriptor control/status, buffer length, last-valid index, FIFO size, audio format, BDL pointers, and link positions. The indirect `ixAZF0STREAM*` registers provide FIFO status and request-count views for more stream instances than the direct descriptor block list in this chunk.
- Azalia endpoint flows configure converter formats, bind channels/streams, expose sink and pin capabilities, handle hotplug or unsolicited responses, report audio enable/disable/format-change status, and snapshot LPIB timing state.

Because all behavior is driven by consumers, call ordering is external. The header only fixes the numeric contract that those consumers rely on.

## State And Persistence Behavior

The header stores no runtime state. Mutable and persistent state lives in the ASIC's MMIO and indexed register blocks. Values written through these offsets can remain active until explicitly reprogrammed, reset, power-gated, or overwritten by firmware/driver flows.

State classes represented by this chunk include:

- PHY configuration and calibration state: UNIPHY/COMBOPHY lane resets, lane power, TX control, margin/deemphasis, ZCAL, PLL frequency, PLL loop/bandwidth, regulator config, observe, and DFT registers affect physical display-link behavior.
- DSI controller state: command queues, lane/PHY control, clocks, timing, escape mode, virtual channel, packet generation, memory power, and debug/status values define panel-link operation and command-mode/video-mode behavior.
- DPRX receiver state: SDP, MSA, VBID, audio, MST, ACT, MSE allocation, CRC, timestamp, and handled-state registers capture receiver-side stream metadata and events.
- Performance-counter state: perfmon control, state, current values, high/low snapshots, and interrupt-misc state are mutable and can be latched or cleared according to hardware semantics outside this file.
- Azalia command/response state: CORB/RIRB pointers, base addresses, immediate-command output/response, codec write control, endpoint index/data, DMA position buffer address, and wall-clock counters are host-controller state used by audio command transport.
- Azalia audio-stream state: stream descriptor control/status, link-position counters, cyclic-buffer size, last-valid index, FIFO size, stream format, BDL pointer, FIFO data, and request counts track active audio DMA streams.
- Azalia codec endpoint state: converter format, stream/channel ID, pin widget controls, audio descriptors, sink information, multichannel/HBR/lipsync settings, hotplug and unsolicited response settings, LPIB snapshots, coding type, format-change status, wireless display identification, and audio enable/disable interrupt status reflect codec and display-audio endpoint behavior.

Incorrect constants are persistent in effect even though the header itself is static. A wrong offset for a PLL or TX register can misprogram physical links; a wrong DSI register can break panel command or timing setup; a wrong Azalia stream or endpoint index can route audio to the wrong converter or corrupt stream descriptor state until the block is reset or reinitialized.

## Dependencies And Integration Points

This file is an ASIC-specific generated register-address dependency. It is included by DCE 12.0 display code such as `dce120_timing_generator.c`, `dce120_hwseq.c`, `irq_service_dce120.c`, GPIO factory/translate code, and `dce120_resource.c`, normally alongside `dce_12_0_sh_mask.h`, `soc15_hw_ip.h`, `vega10_ip_offset.h`, and register helper headers. Those consumers use patterns such as register structs, `REG(reg)` macros, `dm_read_reg_soc15()`, `dm_write_reg_soc15()`, and per-instance offset calculations.

The most direct consumer pattern for the Azalia portion is the generic DCE audio layer. `dce_audio.c` defines `REG(reg)` for direct audio MMIO offsets and `IX_REG(reg)` for endpoint/stream indirect offsets, then routes reads and writes through helpers like `read_indirect_azalia_reg()` and `write_indirect_azalia_reg()`. The `mmAZ*` and `ixAZF0*` constants in this chunk are therefore part of the display-audio programming contract even when the higher-level audio code is shared across DCE/DCN generations.

Major integration surfaces are:

- DRM/KMS display bring-up and link-resource construction, where DCE 12.0 resource code selects clock sources, link encoders, stream encoders, AUX engines, I2C engines, timing generators, and hardware sequencer registers.
- Display physical-link programming for UNIPHY/COMBOPHY PHY and PLL state, including board/ASIC-sensitive sequences provided by link encoder, BIOS, firmware, or low-level display code.
- MIPI DSI panel support and diagnostics for control, command, lane, PHY, packet, timing, and memory-power registers.
- DisplayPort receiver/secondary-data handling for stream metadata, MST allocation, ACT handling, MSA/VBID tracking, CRC, and audio packet status.
- Display performance monitoring and calibration/debug paths that consume perfmon, ZCAL, observe, and DFT registers.
- Display-audio support, including HD-audio CORB/RIRB transport, immediate commands, stream descriptor programming, endpoint/pin capability handling, hotplug/unsolicited response state, audio format changes, HBR/multichannel controls, and LPIB timing snapshots.
- Generated-header consumers outside active runtime code, including register dumps, ASIC validation tooling, bring-up scripts, and comparisons against AMD's register database.

## Risks And Edge Cases

The primary risk is drift between this generated header and the DCE 12.0 register specification. The compiler can catch missing macro names, but it cannot tell whether an offset or base index points to the wrong hardware register.

Specific risks in this chunk include:

- Chunk boundaries are partial. The first definitions continue an earlier `UNIPHY6_UNIPHY_MACRO_CNTL_RESERVED` run, and the final input endpoint 3 block stops before the rest of that endpoint's input pin controls. Adjacent chunks are needed for complete block-level audits.
- Several semantic register groups alias the same physical offsets. For example, UNIPHY8 raw reserved macros and COMBOPHYCM/TX/PLL names cover overlapping ranges. That is intentional in generated ASIC headers, but a consumer must use the semantic name matching the intended hardware subblock.
- Repeated per-lane and per-instance definitions are copy-sensitive. COMBOPHYTXREGS6/8 lanes 0-3, DSI0/DSI1, DPRX_SD0/SD1, AZSTREAM0-7, AZF0STREAM0-15, AZF0ENDPOINT0-7, and AZF0INPUTENDPOINT0-3 differ mainly by instance number and base offset; off-by-one mistakes are hard to detect in review.
- Base index mismatches are high impact. Most display PHY/DSI/DPRX/perfmon/ZCAL definitions use base index `2`, while Azalia direct registers use base index `1` and Azalia indexed registers omit base indices. Mixing these access paths can read or write an unrelated hardware block.
- Reserved/RFU definitions expose undocumented or hardware-reserved state. Even when names are present, generic code should not assume those registers are safe to write without ASIC-specific sequencing guidance.
- DSI and PHY sequencing is timing-sensitive. Misprogramming lane resets, PLL controls, escape-mode controls, or command/timing registers can produce panel bring-up failures, unstable links, or hangs waiting for status bits.
- DPRX/MST/ACT state is event-sensitive. Wrong offsets for ACT handled, MSE allocation, VBID/MSA, SDP, or audio packet status can cause missed stream changes, false diagnostics, or broken MST receiver behavior.
- Azalia audio endpoint maps are dense and repeated. Confusing stream descriptor MMIO offsets with `ix` endpoint indices, or output endpoints with input endpoints, can misroute audio, report wrong pin capabilities, break HBR/multichannel audio, or hide format-change/hotplug events.
- CORB/RIRB and DMA-position registers are host-controller state. Wrong offsets can corrupt audio command transport, DMA buffer accounting, or wall-clock/link-position synchronization.

## Test Signals

There are no unit tests for this header alone. Useful validation is mostly build coverage, generated-header comparison, register readback, and hardware integration testing:

- Build AMDGPU/DC configurations that include DCE 12.0 support. This catches missing or renamed macros and obvious include-order errors.
- Compare lines 15216-17814 against the authoritative AMD DCE 12.0 register database or a known-good upstream generated copy, paying special attention to the partial UNIPHY6 and input endpoint 3 boundaries.
- Verify SOC15 base-index handling with register readback: display PHY/DSI/DPRX/perfmon/ZCAL offsets should resolve through the display base segment, while Azalia direct registers should resolve through the Azalia/audio base segment and `ixAZF0*` names should be accessed only through indexed-register helpers.
- Exercise display link bring-up on hardware using the affected UNIPHY/COMBOPHY instances, including modes that require lane power changes, PLL programming, TX margin/deemphasis setup, reset sequencing, and suspend/resume restoration.
- Exercise DSI0 and DSI1 panel paths where available, covering command transmission, timing programming, low-power/escape behavior, lane/PHY setup, memory power, and status/error readback.
- Exercise DPRX secondary-data and MST/ACT handling with stream metadata changes, VBID/MSA changes, audio packets, MSE allocation changes, and CRC/status readback.
- Validate `DC_PERFMON10` with perf counter start/stop/read and interrupt/status behavior if monitor instance 10 is exposed by the platform.
- Exercise display audio over HDMI/DP: CORB/RIRB codec commands, immediate commands, output streams 0-7, indirect streams 0-15, endpoints 0-7, input endpoints where supported, hotplug/unsolicited response, HBR/multichannel formats, LPIB snapshots, and audio enable/disable/format-change interrupts.
- Run suspend/resume and display hotplug/audio hotplug tests, since these paths reveal stale register programming, wrong base indices, and state that is not restored correctly.

### subset-b-001536: lines 17815-18209

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_offset.h lines 17815-18209

## Scope And Purpose

This chunk is the closing section of the generated AMD DCE 12.0 register offset header. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. The range starts at the tail of the `azf0inputendpoint3_inputendpointind` block, covers full input endpoint 4 through 7 indirect register windows, the `f2codecind` Azalia codec window, descriptor and sink-info indirect windows, Azalia CRC result windows, legacy VGA indexed windows, and then closes the header guard with `#endif`.

The purpose of these definitions is to give DCE 12.0 display/audio code stable symbolic names for indirect-register offsets. The `ix*` naming distinguishes these from direct MMIO `mm*` offsets elsewhere in the same header. Consumers combine these constants with AMDGPU/DC register access helpers and matching shift/mask headers to program HDMI/DP audio widgets, inspect audio stream status and CRCs, expose sink capability data, and access legacy VGA sequencer/CRT/graphics/attribute indexed registers.

## Important APIs, Types, And Macro Families

The public interface is the macro namespace. Each `#define` maps a symbolic register name to a numeric indirect offset. There are no C APIs or types in this chunk, but the macro families are part of the ABI between generated ASIC register descriptions and driver code.

Important macro groups:

- `ixAZF0INPUTENDPOINT3_*` tail entries for input endpoint 3: LPIB timer snapshot, input status control, and infoframe offsets complete the previous chunk's endpoint.
- `ixAZF0INPUTENDPOINT4_*` through `ixAZF0INPUTENDPOINT7_*`: four repeated input endpoint indirect blocks. Each endpoint exposes input converter capability/control offsets (`AUDIO_WIDGET_CAPABILITIES`, `CONVERTER_FORMAT`, `CHANNEL_STREAM_ID`, `DIGITAL_CONVERTER`, `STREAM_FORMATS`, and `SUPPORTED_SIZE_RATES`) plus input pin capability/control offsets for unsolicited responses, pin sense, widget control, multichannel enable state, HBR, channel allocation, hotplug control, forced unsolicited responses, configuration defaults, LPIB snapshots, input status, and infoframes.
- `ixAZALIA_F2_CODEC_ROOT_*` and `ixAZALIA_F2_CODEC_FUNCTION_*`: root and function-node offsets for vendor/device ID, revision, subordinate node count, power state, subsystem ID response words, converter synchronization, function reset, group type, size/rate support, stream formats, and power states.
- `ixAZALIA_F2_CODEC_CONVERTER_*`: output converter control, format, stream/channel ID, digital converter controls, stripe control, ramp rate, GTC embedding, and capability/format parameter offsets.
- `ixAZALIA_F2_CODEC_PIN_*` and `ixAZALIA_F2_PIN_CONTROL_CODEC_CS_OVERRIDE_*`: output pin widget offsets for connection list, widget control, unsolicited response, pin sense, configuration defaults, speaker/channel allocation, downmix, audio descriptors, multichannel enables, lip-sync, HBR, sink-info index/data, codec channel-status override words, association information, digital output status, LPIB snapshot/readback, coding type, format-changed indication, wireless display identification, and remote keepalive.
- `ixAZALIA_F2_CODEC_INPUT_*`: input converter and input pin offsets for format/stream/digital-converter programming, capabilities, pin sense/config defaults, channel allocation, multichannel enable state, HBR, LPIB, input status, infoframe, channel status low/high, and input pin parameters.
- `ixAUDIO_DESCRIPTOR0` through `ixAUDIO_DESCRIPTOR13`: descriptor-indirect offsets that hold HDMI/DP audio Short Audio Descriptor-like capability records.
- `ixAZALIA_F2_CODEC_PIN_CONTROL_MANUFACTURER_ID`, `PRODUCT_ID`, `SINK_DESCRIPTION_LEN`, `PORTID0`, `PORTID1`, and `ixSINK_DESCRIPTION0` through `ixSINK_DESCRIPTION17`: sink-info indirect offsets used to expose monitor/audio sink identity and description bytes.
- `ixAZALIA_INPUT_CRC0_CHANNEL*`, `ixAZALIA_INPUT_CRC1_CHANNEL*`, `ixAZALIA_CRC0_CHANNEL*`, and `ixAZALIA_CRC1_CHANNEL*`: per-channel CRC result offsets for input and output Azalia audio validation paths.
- `ixSEQ*`, `ixCRT*`, `ixGRA*`, and `ixATTR*`: legacy VGA sequencer, CRT controller, graphics controller, and attribute controller indexed offsets.

## Control Flow And Data Flow

This header section has no runtime control flow. Data flow is compile-time substitution: C source includes `dce_12_0_offset.h`, passes an `ix...` constant to an indirect-register read/write helper, and the helper selects the corresponding hardware register inside an indexed address block.

The implied hardware flows are:

- Audio endpoint setup writes converter format, stream/channel ID, digital converter, multichannel, HBR, channel allocation, and widget-control offsets for each endpoint that participates in HDMI/DisplayPort audio.
- Hotplug and sink capability discovery reads pin sense, configuration defaults, audio descriptor records, sink-info index/data, manufacturer/product IDs, port IDs, and sink-description bytes.
- Audio playback/capture progress and diagnostics read or snapshot LPIB and LPIB timer registers, input status, digital output status, infoframe state, channel status, and CRC result windows.
- Codec lifecycle operations can use F2 function power-state, reset, converter synchronization, and parameter offsets to discover capabilities or bring the codec block into a programmed state.
- Legacy VGA paths use the sequencer, CRT controller, graphics controller, and attribute-controller indexed offsets when emulating or preserving VGA-compatible display state.

Because the values are offsets, not full behavior, ordering requirements live in the calling driver code and the hardware specification. For example, a caller normally chooses the endpoint or indexed block, writes an index/address register, then reads or writes the selected data register; this chunk supplies the index values for that transaction.

## State And Persistence Behavior

The file stores no state. The mutable state represented by these constants exists in DCE 12.0 hardware registers and can persist until rewritten, reset, power-gated, or reinitialized by display/audio bring-up.

State categories represented in this chunk include:

- Audio format and routing configuration: converter format, channel/stream IDs, digital converter controls, stripe/ramp/GTC controls, multichannel enable registers, HBR selection, channel allocation, and channel status.
- Sink and connector-observed state: pin sense, hotplug control, unsolicited response state, configuration defaults, audio descriptor data, sink manufacturer/product IDs, sink description, and port IDs.
- Runtime audio progress and status: LPIB snapshots, LPIB timer snapshots, input status control, infoframe registers, digital output status, coding type, format-changed state, remote keepalive, and wireless display identification.
- Capability and discovery state: root/function/converter/pin parameters for supported size/rates, stream formats, widget capabilities, pin capabilities, power states, group type, and subordinate node counts.
- Diagnostic state: Azalia input/output CRC channels and legacy VGA indexed register readbacks.
- Legacy display state: VGA sequencer, CRT controller, graphics controller, and attribute controller registers that can affect boot console compatibility, handoff, and VGA aperture behavior.

Wrong offsets can cause state changes to land in the wrong register within an indirect block. That can leave audio silent, misreport sink capabilities, break hotplug/audio ELD style discovery, corrupt channel allocation, hide status/CRC failures, or disturb VGA compatibility state until the relevant block is reprogrammed or reset.

## Dependencies And Integration Points

This header is included by DCE 12.0 display code such as `display/dc/dce120/dce120_timing_generator.c`, `display/dc/hwss/dce120/dce120_hwseq.c`, `display/dc/irq/dce120/irq_service_dce120.c`, `display/dc/resource/dce120/dce120_resource.c`, DCE 12.0 GPIO factory/translation code, and `amdgpu/gmc_v9_0.c`. This specific chunk's Azalia and VGA offsets are part of the same generated namespace even when direct references are sparse in this repository snapshot; other DCE/DCN generations expose nearly identical names for their audio and VGA paths.

Primary integration points:

- DRM/KMS connector and encoder audio support for HDMI/DisplayPort, including sink capability discovery and audio packet configuration.
- AMD DC resource and hardware sequencing code that includes DCE 12.0 register offsets alongside matching shift/mask headers.
- Interrupt and hotplug handling paths that may interact with Azalia pin sense, unsolicited response, hotplug control, and format/status change registers.
- Audio validation, diagnostics, or bring-up code that reads descriptor, sink-info, LPIB, infoframe, channel-status, and CRC result registers.
- Legacy VGA compatibility and handoff code that must preserve or program indexed VGA state while modern display pipes are active.
- Generated ASIC register-header maintenance: this chunk must remain consistent with sibling DCE and DCN offset headers and the corresponding `dce_12_0_sh_mask.h` field definitions.

## Risks And Edge Cases

The main risk is generated-header drift from the ASIC register database. These constants are opaque numeric offsets, so the compiler can catch missing names but cannot prove that `0x3776`, `0x779c`, or a VGA index value selects the intended register.

Specific risks:

- Chunk boundary: lines 17815-17817 are only the end of input endpoint 3; endpoint 3's converter and earlier pin offsets are in the previous chunk.
- Repeated endpoint blocks: input endpoint 4 through 7 are structurally identical and differ only by endpoint number, making copy/paste or generation errors hard to notice in review.
- Alias-like offsets: `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR` and `ixAZALIA_F2_CODEC_PIN_CONTROL_AUDIO_DESCRIPTOR_DATA` both map to `0x3776`, so callers must understand whether they are treating the register as an index selector or data window.
- Naming overlap between F0 endpoint-specific offsets and F2 codec offsets can lead to using an offset from the wrong indexed address block.
- Sink-info and descriptor windows are indexed data areas; off-by-one descriptor or description offsets can produce plausible but wrong audio capability data.
- LPIB, timer snapshot, CRC, and channel-status registers are diagnostic/status oriented; stale reads or writes to the wrong block can make audio validation misleading.
- Legacy VGA register names are short and historically overloaded. Misusing `SEQ`, `CRT`, `GRA`, or `ATTR` offsets can affect boot-console compatibility or VGA state restoration.
- The final `#endif` means this chunk also closes the include guard; accidental insertion after it would not be protected by `_dce_12_0_OFFSET_HEADER`.

## Test Signals

There are no unit tests for this header section alone. Useful validation signals are build coverage, generated-header comparison, and hardware/display-audio behavior:

- Build AMDGPU/DC configurations that include `dce_12_0_offset.h`; this catches missing or renamed macros and header guard problems.
- Compare this range against the authoritative DCE 12.0 register database or a known-good upstream generated header, especially the repeated endpoint 4-7 blocks, F2 codec offsets, descriptor/sink-info windows, CRC offsets, and VGA index values.
- Exercise HDMI/DisplayPort audio on DCE 12.0 hardware: verify stream format, channel allocation, HBR/multichannel modes, channel status, infoframes, and audible output.
- Test hotplug and sink capability discovery with monitors exposing different audio descriptors and sink-info data; confirm the driver reports the expected formats, rates, channels, and connector identity.
- Validate LPIB snapshot/readback, format-changed status, remote keepalive, and input/output CRC channels through debug or hardware validation paths.
- Run suspend/resume and power-state transitions that reset or reprogram the Azalia F2 function and endpoints.
- Exercise VGA handoff or legacy VGA-compatible modes to verify sequencer, CRT controller, graphics controller, and attribute-controller indexed state remains readable and restorable.
