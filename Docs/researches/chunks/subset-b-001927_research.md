# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h lines 10194-12822

## Scope

This chunk is part of the generated DCN 3.2.0 register offset header used by the AMD display driver. It covers the middle of the DCN32 display register map, starting in the tail of the legacy `DIG4` HDMI/TMDS register block and ending at the first register of the HPO DP stream encoder 3 DME block. The range contains 2,369 `#define` lines: 1,184 register-offset macros plus 1,185 `_BASE_IDX` macros. The extra base-index line is the opening `regDIG4_HDMI_ACR_44_0_BASE_IDX`, whose register macro is in the previous chunk.

The covered address blocks are:

- Legacy DIO output sideband/audio blocks: `AFMT0` through `AFMT4`, `DME0` through `DME4`, `VPG0` through `VPG4`, and the tail of `DIG4`.
- AUX/DDC and DIO/DCIO support: `DP_AUX0` through `DP_AUX4`, DOUT I2C, DIO misc/link controls, DCIO generics, GPIO/DDC/HPD/PWRSEQ/AUX pad controls, and `DCIO_UNIPHY0` through `DCIO_UNIPHY4` reserved macro-control registers.
- Embedded-panel and compression blocks: `PWRSEQ0`, `DSC_TOP0..3`, `DSCCIF0..3`, and `DSCC0..3`.
- HPO stream-output blocks: HPO top, DP stream mapper, HPO HDMI stream encoder 0 sideband blocks (`AFMT5`, `DME5`, `VPG5`), full HPO DP stream encoder instances 0 through 2 (`DP_STREAM_ENC`, `APG`, `DME`, `VPG`, `DP_SYM32_ENC`), and the start of HPO DP stream encoder instance 3 (`DP_STREAM_ENC3`, `APG3`, `DME9_DME_CONTROL`).

The file has no executable C code. Its purpose is to provide ASIC-specific symbolic MMIO offsets and register-base-index selectors for DCN 3.2.0. Runtime code combines these macros with companion field shift/mask macros from `dcn_3_2_0_sh_mask.h`.

## Important API Surface

The API surface is the generated macro namespace:

- `reg<block>_<register>` expands to a register offset.
- `reg<block>_<register>_BASE_IDX` expands to the register base index used by AMD register helpers. Most macros in this slice use base index `2`; the HPO HDMI stream encoder 0 and HPO top/mapper registers use base index `3`.

Important register families in this chunk include:

- `regDIG4_*`: HDMI audio clock regeneration (`HDMI_ACR_*`), AFMT backend coupling, DIG backend enable/control, TMDS control characters, DC balancer controls, DIG version, and forced DIG disable for legacy encoder 4.
- `regAFMT[0-5]_AFMT_*`: audio formatter VBI packet control, audio packet controls, HDMI/DP audio info words, IEC 60958 channel status words, audio CRC control/result/status, ramp controls, infoframe control, interrupt status, audio source selection, and AFMT memory power.
- `regDME[0-9]_DME_*`: metadata-engine control and memory-control registers. In this slice, legacy DIO uses `DME0..4`, HPO HDMI uses `DME5`, HPO DP instances 0 through 2 use `DME6..8`, and instance 3 begins with `DME9_DME_CONTROL`.
- `regVPG[0-8]_VPG_*`: video packet generator generic packet access/data, frame and immediate update controls, generic status, memory power, ISRC access/data, and MPEG info packet words.
- `regDP_AUX[0-4]_AUX_*`: AUX engine control, software control/status/data, link-service status/data, DPHY TX/RX controls and statuses, GTC sync controls/statuses, and PHY wake control for five AUX/DDC-capable links.
- `regDC_I2C_*`, `regDIO_*`, and `regDCIO_*`: DOUT I2C arbitration/status, DIO memory/clock/power/soft-reset/link controls, DCIO reference/clock controls, channel crossbar controls, pin straps, pattern generation, genlock/swaplock pad controls, and soft reset.
- `regDC_GPIO_*`, `regPHY_AUX_CNTL`, and `regAUXI2C_PAD_ALL_PWR_OK`: GPIO mask/value/output-enable/readback registers for generic, DDC, VGA DDC, genlock, HPD, PWRSEQ, AUX, pad-drive, pull-up, RX-enable, and pad power-good handling.
- `regDCIO_UNIPHY[0-4]_UNIPHY_MACRO_CNTL_RESERVED*`: per-UNIPHY reserved macro-control offsets. The header does not describe field semantics, but the stable generated names allow shared link-encoder code to address PHY-instance register space if a field list references them.
- `regPANEL_PWRSEQ_*`, `regBL_PWM_*`, and `regDC_GPIO_PWRSEQ_*`: panel power sequencing, delay/reference-divisor programming, backlight PWM controls, lock/update grouping, and PWRSEQ GPIO controls.
- `regDSC_TOP[0-3]_*`, `regDSCCIF[0-3]_*`, and `regDSCC[0-3]_*`: DSC top control/debug, DSC interface config, DSC compressor config/status/interrupts, PPS config words 0 through 22, memory power, squared-error/readback counters, max absolute error, rate-buffer fullness, rate-control-buffer fullness, and debug bus/data registers.
- `regHPO_TOP_*` and `regDP_STREAM_MAPPER_CONTROL[0-3]`: HPO clock/hardware control and mapping of DP streams to HPO link targets.
- `regDP_STREAM_ENC[0-3]_*`: HPO DP stream encoder clock, pixel input mux, audio mux, clock-ramp FIFO status/control, and spare registers.
- `regAPG[0-3]_*`: audio packet generator controls, debug generation, packet control, audio CRC control/result, status, memory power, and spare registers for HPO DP streams.
- `regDP_SYM32_ENC[0-2]_*`: HPO DP 128b/132b-oriented symbol stream controls, video FIFO, MSA double-buffer and MSA words, pixel-format double buffering, hblank control, generic secondary-data packet controls, SDP/audio/metadata controls, VBID and stream control, Panel Replay control, video CRC control/results/status, memory power, and spare.

## Control Flow and State Behavior

There is no local control flow in this header. The control flow is generated indirectly when resource constructors and hardware blocks token-paste these macro names into register tables, then call common read/write helpers.

Important sequencing modeled by this offset slice includes:

- Stream sideband programming is instance-oriented. Legacy `AFMT0..4`, `DME0..4`, and `VPG0..4` correspond to DIO/DIG instances; HPO HDMI uses `AFMT5/DME5/VPG5`; HPO DP stream instances use `DP_STREAM_ENC0..3`, `APG0..3`, `VPG6..8` in this slice, and `DME6..9`. Resource code must map stream encoders to the correct sideband blocks rather than assuming all suffixes match.
- AUX and I2C offsets are used by transaction state machines. The registers named here expose software command/data paths, arbitration, interrupts, DPHY controls, TX/RX status, and wake controls. Runtime code sequences requests by programming control/data registers, waiting on status/interrupt bits defined in the shift/mask header, and handling retries/timeouts.
- PWRSEQ and backlight state is latched by panel-power and PWM hardware. `BL_PWM_GRP1_REG_LOCK`, panel delay/reference registers, target/current state registers, and GPIO PWRSEQ controls represent persistent hardware state that must be programmed in the right order around panel power on/off and backlight enable/disable.
- DSC programming is double-buffered and status-driven. `DSCC_CONFIG*`, `DSCC_PPS_CONFIG*`, `DSCC_STATUS`, and `DSCC_INTERRUPT_CONTROL_STATUS` are consumed by DSC setup paths that configure slice/PPS/rate-control state, wait for update completion, and monitor rate-buffer overflow/underflow/error signals.
- HPO DP stream enablement spans several blocks. The stream mapper chooses the HPO link target, `DP_STREAM_ENC*` selects pixel/audio sources and FIFO behavior, `DP_SYM32_ENC*` programs pixel format/MSA/SDP/VBID/CRC, `APG*` drives audio packet state, and `VPG*`/`DME*` carry video packets and metadata. A mode set that changes one part without the matching block can route packets or audio to the wrong stream.
- Memory power registers appear in AFMT, VPG, DME, APG, DP_SYM32, and DSCC families. They model low-power state separate from pure functional configuration; register writes may be ignored or delayed if the relevant memory block is not powered as expected.

## Dependencies and Integration Points

This header is paired with `dcn_3_2_0_sh_mask.h`. The offset macros provide register addresses, while the shift/mask header provides field-level bit positions. Both are included directly by DCN32-specific code such as `display/dmub/src/dmub_dcn32.c` and `display/dc/irq/dcn32/irq_service_dcn32.c`.

The main display-resource integration is `display/dc/resource/dcn32/dcn32_resource.c`, which expands these symbols into typed register tables:

- `VPG_DCN3_REG_LIST_RI(id)` initializes `vpg_regs[10]`, covering legacy `VPG0..4`, HPO HDMI `VPG5`, and HPO DP VPG instances.
- `AFMT_DCN3_REG_LIST_RI(id)` initializes `afmt_regs[6]`, covering `AFMT0..5`.
- `APG_DCN31_REG_LIST_RI(id)` initializes `apg_regs[4]`, covering `APG0..3`.
- `SE_DCN32_REG_LIST_RI(id)` initializes legacy stream encoder registers such as the `DIG4` tail present at the beginning of this chunk.
- `DCN2_AUX_REG_LIST_RI(id)` initializes five AUX register sets, matching `DP_AUX0..4`.
- `LE_DCN31_REG_LIST_RI(id)` and `UNIPHY_DCN2_REG_LIST_RI(id, phyid)` integrate DIO link encoder and UNIPHY/DCIO register offsets.
- `DCN3_1_HPO_DP_STREAM_ENC_REG_LIST_RI(id)` initializes four HPO DP stream encoder register sets from `DP_STREAM_MAPPER_CONTROL*`, `DP_STREAM_ENC*`, and `DP_SYM32_ENC*`.
- `DSC_REG_LIST_DCN20_RI(id)` initializes four DSC register sets from `DSC_TOP*`, `DSCCIF*`, and `DSCC*`.

Other integration points include:

- `display/dc/hpo/dcn31/dcn31_hpo_dp_stream_encoder.h`, whose register-list macro consumes `DP_STREAM_MAPPER_CONTROL*`, `DP_STREAM_ENC*`, and `DP_SYM32_ENC*` offsets and whose mask/shift list consumes the companion field macros.
- `display/dc/dsc/dcn20/dcn20_dsc.h`, which defines the shared DSC register list used by DCN32 resource code for `DSC_TOP`, `DSCC`, and `DSCCIF`.
- `display/dc/dce/dce_link_encoder.h` and DCN link-encoder headers, which provide AUX, HPD, link, and UNIPHY register-list patterns.
- `display/dc/gpio/dcn32/*`, `display/dc/dio/dcn32/*`, `display/dc/hpo/dcn32/*`, panel/backlight paths, and IRQ handling, which rely on these generated offsets through resource-created register structures.

## State and Persistence

The macros themselves do not store state, but they name hardware state that persists in MMIO registers until rewritten, reset, power-gated, or latched by display timing:

- GPIO, HPD, DDC, AUX, DIO, and DCIO registers persist physical I/O configuration, pad state, arbitration state, and soft-reset state.
- Panel power sequence and backlight PWM registers persist panel enable, target power state, delay timing, PWM period/duty behavior, and lock/update settings across the panel sequence.
- AFMT, APG, VPG, and DME registers persist packet-generator, audio, metadata, CRC, status, interrupt, and memory-power state per stream-sideband block.
- DSC registers persist compressor configuration, PPS payload values, memory-power state, status, overflow/underflow state, and debug/error counters.
- HPO mapper, stream encoder, and SYM32 encoder registers persist HPO DP stream routing, pixel/audio source selection, MSA/pixel format, SDP behavior, CRC setup, Panel Replay control, and stream enable-related state.

Because these offsets are generated for one ASIC revision, they are effectively an internal ABI between DCN32 register tables and the hardware. A wrong offset or base index can compile cleanly while targeting the wrong MMIO aperture.

## Risks and Edge Cases

- The chunk starts and ends mid-block. `DIG4_HDMI_ACR_44_0` is split from its `_BASE_IDX` at the beginning, and `DME9_DME_CONTROL` is split from `DME9_DME_MEMORY_CONTROL` at the end. The final per-file report must reconcile adjacent chunks before claiming complete DIG4 or HPO stream encoder 3 coverage.
- Instance numbering is nontrivial. Legacy DIO uses `AFMT/DME/VPG0..4`; HPO HDMI uses suffix 5; HPO DP stream encoder 0 uses `DME6` and `VPG6`, stream encoder 1 uses `DME7` and `VPG7`, stream encoder 2 uses `DME8` and `VPG8`, and stream encoder 3 begins with `DME9`. Code must follow resource mapping, not numeric intuition.
- Base-index drift is high impact. Most offsets here use `_BASE_IDX 2`, but HPO top/mapper and HPO HDMI stream encoder sideband blocks use `_BASE_IDX 3`. Incorrect base indices can point an otherwise correct offset at the wrong register aperture.
- Reserved UNIPHY macro-control registers are opaque. They are useful for generated access tables, but without field semantics they should not be casually programmed outside established link-encoder sequences.
- Status, interrupt, acknowledge, and clear semantics are not visible in the offset header. AUX, AFMT/APG CRC/status, DIO/DCIO soft reset, PWRSEQ, DSC interrupt/status, and HPO CRC/status registers require the companion shift/mask header and hardware programming sequence to avoid read-modify-write mistakes.
- Generated repetition makes review hard. AFMT, VPG, AUX, DSCC, HPO DP stream encoder, APG, DME, and DP_SYM32 blocks differ mostly by instance suffix and offset stride; a single generator error could affect only one connector, stream, DSC instance, or HPO path.
- DSC registers include diagnostic/error counters and underflow/overflow state. Treating them as ordinary configuration registers can hide compression failures or accidentally clear diagnostic signals depending on field semantics in the companion header.

## Test Signals

Useful validation signals for code paths using this slice include:

- Build coverage for DCN32 with `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h` included, catching missing or renamed `regAFMT*`, `regVPG*`, `regDME*`, `regDP_AUX*`, `regDCIO_UNIPHY*`, `regDSCC*`, `regDP_STREAM_ENC*`, `regAPG*`, and `regDP_SYM32_ENC*` symbols.
- Resource-table sanity checks in `dcn32_resource.c` confirming expected instance counts and offsets for five AUX engines, five legacy stream encoders, five link encoders, six AFMT blocks, ten VPG blocks, four APG blocks, four HPO stream encoders, and four DSC blocks.
- Connector bring-up tests across legacy DIO paths that exercise AUX/DDC, HPD/GPIO, DIG4 HDMI/TMDS, AFMT audio/infoframe, VPG generic packets, and DME metadata without link-training or packet-routing regressions.
- eDP/panel tests that cycle panel power, backlight PWM, PWRSEQ GPIO, and BL PWM lock/update paths while checking for correct panel state and no stuck power-sequence status.
- DSC mode-set tests on all four DSC instances that program PPS/config registers, enable compressed output, watch `DSCC_STATUS` and interrupt/status fields, and verify no rate-buffer underflow/overflow events.
- HPO DP 2.0/UHBR tests using stream encoders 0 through 2 fully and stream encoder 3 through the next chunk, validating stream mapper targets, pixel/audio muxing, SYM32 MSA/pixel-format/SDP programming, APG audio packets, VPG packets, DME metadata, CRC readback, and memory-power transitions.
- Suspend/resume and display hotplug tests that cover AUX wake/status, DCIO/DIO soft reset, GPIO/HPD state, and HPO/DSC memory-power restoration.
