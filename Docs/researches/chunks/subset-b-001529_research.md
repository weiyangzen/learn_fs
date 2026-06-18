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
