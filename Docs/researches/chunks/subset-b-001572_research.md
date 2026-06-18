# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_8_0_sh_mask.h lines 4183-8156

## Scope And Purpose

This chunk is a generated AMD DCE 8.0 register field mask/shift table. It contains no executable C logic. Its purpose is to publish compile-time bitfield metadata used by AMDGPU display code when composing and decoding MMIO register values for DCE 8 hardware.

The file is under a local `ceph-client` source mirror, but this path is Linux AMDGPU display-driver hardware metadata. It does not implement Ceph filesystem behavior.

The range begins at the tail of the DVO voltage-reference/skew-control area, then covers a broad middle section of the DCE 8.0 display register map:

- UNIPHY test-pattern, transmitter, PLL, synchronization, BIST, link, and channel crossbar fields.
- I2S/SPDIF GPIO masks, output values, enables, readback values, and drive strength.
- Graphics and overlay plane state: enable, pixel format, tiling, surface addresses, pitch, viewport, updates, DFQ status, page-flip interrupts, compression metadata, XDMA underflow detection, and recovery addresses.
- Color and composition pipeline fields: input/output CSC, common matrices, denorm, rounding, clamps, key ranges, degamma, gamut remap, DCP spatial dither, LUT, CRC, regamma, alpha, cursor, and stereo controls.
- DIG/HDMI/TMDS/LVDS/audio packetizer fields for link output, infoframes, ACR, audio sample/channel status, CRC/ramp/debug controls, and lane enables.
- HPD1-HPD6 interrupt, sense, control, fast-train, and toggle-filter fields.
- DC and generic I2C/DDC fields for arbitration, status, interrupt control, speed/setup, transactions, data, pin selection, pin debug, and VGA EDID detection.
- Global display interrupt status registers from `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE9`.
- Display output power-management, timer, stereo-sync selection, debug, and per-AUX debug fields for AUX1-AUX6.
- DMCU control/status, firmware address/checksum, RAM access, event trigger, interrupt/status/mask/routing, scratch, counters, clock-gating, and master/slave mailbox fields.

The chunk ends in the middle of the DMCU mailbox family at `SLAVE_COMM_DATA_REG1`; following slave communication registers continue in the next source range.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, or storage objects in this range. The public interface is the generated preprocessor naming contract:

- `<REGISTER>__<FIELD>_MASK` gives the field mask in a 32-bit register value.
- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position for the same field.
- Companion address macros such as `mmGRPH_CONTROL`, `mmHDMI_CONTROL`, `mmDC_HPD1_INT_STATUS`, and `mmDMCU_CTRL` come from the matching DCE 8.0 register address headers.

Important macro groups in this chunk:

- `UNIPHY*`: static test pattern and seed registers for AB/CD/EF/GH links, TX pre-emphasis and voltage swing controls, transmitter power/reference controls, PLL feedback/ref/divider/spread-spectrum controls, data synchronization, link enable, channel crossbar, BIST, and test output status.
- `DC_GPIO_I2S_SPDIF_*`: mask/A/EN/Y/drive-strength fields for I2S data, MCLK, BCLK, LRCK, and SPDIF pins across two audio pin groups.
- `GRPH_*` and `OVL_*`: primary graphics plane and overlay configuration, including format/depth/tile fields, endian/channel swap, surface addresses, pitch, viewport offsets/start/end, update locks, flip queue state, page-flip interrupt status/control, compression fields, stereosync flip, rotation, and XDMA underflow/recovery status.
- `PRESCALE_*`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `COMM_MATRIX*`, `DENORM_CONTROL`, `OUT_*`, `KEY_*`, `DEGAMMA_*`, `GAMUT_REMAP_*`, `REGAMMA_*`, and `ALPHA_CONTROL`: color processing, matrix coefficients, clamp/rounding, keying, gamut/regamma LUT region, and alpha-control bitfields.
- `CUR*` and `CUR2_*`: first and second cursor enable/type/mode, surface address, size, position, hot spot, color, update, request filtering, and stereo offset controls.
- `DC_LUT_*` and `DCP_CRC_*`: display LUT access/control/autofill/offset fields and DCP CRC source/window/result metadata.
- `DIG_*`, `HDMI_*`, `AFMT_*`, `TMDS_*`, `LVDS_*`, and `DOUT_*`: digital front/back-end, HDMI packetization, audio formatter, TMDS/LVDS signaling, lane enable, scratch, and output/debug fields.
- `DC_HPDn_*`: hotplug detect status, ACK, RX interrupt bits, enable/mask/polarity, fast training, sense, and connect/disconnect filter timing for HPD1 through HPD6.
- `DC_I2C_*` and `GENERIC_I2C_*`: DDC/I2C engine control, arbitration, interrupt control, software status, DDC1-DDC6/VGA hardware status, speed/setup, transaction descriptors, data, pin selection, and pin debug fields.
- `DISP_INTERRUPT_STATUS*`: global interrupt aggregator bits for vblank/vline, HPD, CRTC, page flip, audio, AUX, DMCU, and related display events spread over the base and continue registers.
- `DP_AUXn_DEBUG_[A-Q]`: per-AUX debug probe fields for AUX1 through AUX6.
- `DMCU_*`, `MASTER_COMM_*`, and `SLAVE_COMM_*`: display microcontroller run/reset/status, firmware locations/checksum, IRAM/ERAM access, microcontroller events, internal/soft-service interrupts, host/uC/XIRQ routing, scratch, counters, clock gating, and mailbox bytes.

## Control Flow

This chunk has no runtime control flow. Each line is a preprocessor definition consumed by C code that performs register reads, writes, and read-modify-write operations.

Runtime flow is in DCE 8 consumers. In this tree the header is included by legacy AMDGPU paths such as `amdgpu/dce_v8_0.c`, `amdgpu/cik.c`, `amdgpu/gmc_v7_0.c`, `amdgpu/gfx_v7_0.c`, power-management code, and display-core DCE80 files under `display/dc/dce80`, `display/dc/gpio/dce80`, `display/dc/irq/dce80`, `display/dc/hwss/dce80`, and `display/dc/resource/dce80`.

Representative flows visible in `amdgpu/dce_v8_0.c`:

- Vblank/vline/HPD interrupt tables pair `mmDISP_INTERRUPT_STATUS*` registers with `DISP_INTERRUPT_STATUS*__..._MASK` bits from this range.
- Page flips program `GRPH_FLIP_CONTROL`, `GRPH_PITCH`, `GRPH_PRIMARY_SURFACE_ADDRESS[_HIGH]`, and related graphics plane fields through CRTC offsets.
- HPD handling reads `DC_HPD1_INT_STATUS__DC_HPD1_SENSE_MASK`, toggles `DC_HPD1_INT_CONTROL__DC_HPD1_INT_POLARITY_MASK`, ACKs with `DC_HPD1_INT_CONTROL__DC_HPD1_INT_ACK_MASK`, and enables/disables `DC_HPD1_CONTROL__DC_HPD1_EN_MASK` with per-HPD offsets.
- HDMI/audio setup writes ACR, AVI infoframe, VBI packet, HDMI deep-color, infoframe line, GC, audio packet, AFMT 60958 channel-status, channel-enable, and audio-sample-send fields.
- Framebuffer programming composes `GRPH_CONTROL` values from depth, format, tiling, bank, pipe-config, and array-mode shifts, then writes surface address, pitch, viewport, swap, LUT-bypass, CSC, prescale, degamma, gamut, regamma, and output CSC controls.
- Page-flip IRQ enable/ack paths use `GRPH_INTERRUPT_CONTROL__GRPH_PFLIP_INT_MASK_MASK`, `GRPH_INTERRUPT_STATUS__GRPH_PFLIP_INT_OCCURRED_MASK`, and `GRPH_INTERRUPT_STATUS__GRPH_PFLIP_INT_CLEAR_MASK`.

Display-core DCE80 code uses the same generated field vocabulary through register tables and offset instances. For example, GPIO factory/translation code maps HPD status and filter fields, timing/resource code computes per-controller DCP offsets, and IRQ service code maps generated status/mask/ack fields into display IRQ sources.

Because the header is declarative, it does not enforce sequencing. Consumers must order operations around update locks, page flips, hotplug ACKs, I2C arbitration, DMCU firmware/RAM access, HDMI/AFMT packet enablement, PLL/link bring-up, and power-gated or clock-gated display blocks.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The macros describe hardware MMIO state.

The represented hardware state spans:

- Display fetch and plane state: primary/secondary graphics and overlay addresses, pitch, viewport, format/tile metadata, flip/update status, compression metadata, and XDMA recovery fields.
- Color pipeline state: prescale, CSC matrices, denorm, clamps, keying, degamma/gamut/regamma LUTs, alpha, dither, random seeds, and CRC capture.
- Cursor state: first and second cursor surfaces, geometry, hot spots, colors, update locks, filtering, and stereo offsets.
- Link/PHY state: UNIPHY transmitter, PLL, synchronization, link, channel mapping, BIST/test output, DVO residual fields, TMDS/LVDS/DIG lane and pattern controls.
- HDMI/audio state: control/status, packet control, ACR values, infoframe payloads, generic packets, audio source/channel status, sample transmission, CRC/ramp/debug controls.
- Connector sideband state: HPD sense/interrupt/filter state, I2C/DDC arbitration and transaction state, AUX debug state, and EDID-detect controls.
- Global interrupt state: display interrupt aggregator status bits and DMCU interrupt/status/mask/routing fields.
- DMCU state: microcontroller control/status, program counter and firmware address ranges, IRAM/ERAM access windows, event triggers, scratch/counters, clock-gating, and host/uC communication bytes.

Persistence is field-specific and not encoded here. Some fields are durable programming knobs that remain until rewritten, reset, modeset, suspend/resume, power-gating transition, or GPU reset. Others are read-only status, sticky interrupt bits, write-one-to-clear bits, self-clearing request/update bits, counters, or hardware-latched values. The generated names often hint at semantics (`*_STATUS`, `*_CLEAR`, `*_ACK`, `*_MASK`, `*_EN`, `*_UPDATE_PENDING`, `*_UPDATE_TAKEN`, `*_RESET`, `*_SENSE`, `*_INT_OCCURRED`), but the header does not declare access type, reset value, read side effects, or write side effects.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract for DCE 8.0. It is meaningful only with the matching address and value headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/`, especially:

- `dce_8_0_d.h` for `mm...` and indexed register address constants.
- `dce_8_0_enum.h` for symbolic field values such as graphics formats, endian modes, CSC modes, gamma modes, and related enumerated register values.
- Register accessor helpers used by legacy AMDGPU code (`RREG32`, `WREG32`, `WREG32_P`, `WREG32_OR`) and display-core register-field helper macros.

Direct include points found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v8_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cik.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v7_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ci_baco.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/ci_smumgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce80/dce80_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce80/irq_service_dce80.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce80/dce80_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce100/dce_clk_mgr.c`

Practical integration points are modeset resource setup, display pipe and plane programming, page flips, vblank/vline and page-flip IRQ handling, hotplug handling, DDC/I2C access for EDID, HDMI/DP/TMDS/LVDS output programming, audio packet setup, display color management, hardware cursor setup, power-management transitions, DMCU firmware/interrupt/mailbox communication, and debug/CRC validation.

## Risks And Edge Cases

- Numeric masks and shifts are hardware ABI. A one-bit error can compile cleanly but corrupt neighboring fields, leave interrupts uncleared, program the wrong format/link mode, or wedge a display block.
- The file is generated and highly repetitive. Manual edits to instance-indexed families such as HPD1-HPD6, DDC1-DDC6, AUX1-AUX6, or `DISP_INTERRUPT_STATUS_CONTINUE*` are error-prone and should be avoided in favor of regeneration from the authoritative register database.
- This chunk starts and ends at generated chunk boundaries, not semantic module boundaries. The DVO fields are a tail from the previous area, and `SLAVE_COMM_DATA_REG1` is incomplete relative to the broader DMCU mailbox family.
- Interrupt fields mix enable, mask, status, ACK, occurred, and clear semantics. HPD, page-flip, vblank/vline, audio, AUX, global display, and DMCU interrupt users must preserve correct polarity and clear behavior.
- Update and flip fields are sequencing-sensitive. Incorrect use of `GRPH_UPDATE`, `OVL_UPDATE`, cursor update locks, stereosync flip fields, or page-flip controls can cause torn updates, missed flips, stale surfaces, or IRQ timeouts.
- Plane format fields are tightly coupled to memory layout. Incorrect `GRPH_CONTROL`, `GRPH_SWAP_CNTL`, tiling, bank, pipe-config, pitch, compression, or address fields can cause display corruption, underflow, or GPU memory faults.
- Color pipeline fields are mode- and format-sensitive. CSC, prescale, denorm, clamp, gamut, regamma, dither, keying, and alpha settings must match pixel format, color depth, output encoding, and DRM color-management state.
- I2C/DDC and HPD fields interact with physical connectors and shared sideband buses. Arbitration mistakes, stale status bits, or wrong pin selection can break EDID reads, hotplug detection, or link training.
- PHY and PLL fields can affect signal integrity. UNIPHY pre-emphasis, voltage swing, PLL dividers, spread spectrum, lane routing, and test/BIST controls should only be touched by validated bring-up paths.
- DMCU fields are firmware-facing. Wrong firmware ranges, RAM access sequencing, interrupt routing, or mailbox byte handling can hang microcontroller transactions or break power/backlight/ABM-style display services.

## Test Signals

Useful validation is mainly compile-time plus hardware/display behavior:

- Build AMDGPU with DCE 8.0 and DCE80 display-core code enabled; missing or renamed generated macros should fail in `dce_v8_0.c`, DCE80 timing/resource/IRQ/GPIO code, CIK/GMC/GFX support code, and power-management users.
- Compare generated masks/shifts against `dce_8_0_d.h`, `dce_8_0_enum.h`, adjacent chunks of this same header, and neighboring DCE generations to catch accidental generation drift or instance-index drift.
- Exercise modesets on DCE 8 hardware across all available CRTCs: plane enable/disable, page flips, cursor movement, overlay if supported, scaling/color setup, suspend/resume, and multi-display routing.
- Validate IRQ behavior: vblank/vline delivery, page-flip completion, HPD connect/disconnect storms and ACKs, AUX/DDC interrupts, audio/status interrupts, and DMCU interrupt routing/clear paths.
- Test connector sideband behavior: EDID reads through DDC1-DDC6/VGA paths, HPD sense and delayed sense, fast-training controls, and AUX debug/status where DisplayPort is present.
- Test HDMI/audio output: ACR values, AVI/audio infoframes, audio packet enablement, 60958 channel status, deep color, VBI/generic packet controls, and audio CRC/status where observable.
- Watch negative signals in kernel logs and display behavior: stuck page flips, missed vblank, HPD flapping, EDID failures, black screens, underflow warnings, color shifts, cursor corruption, link retraining loops, HDMI audio silence, resume failures, or DMCU mailbox timeouts.
