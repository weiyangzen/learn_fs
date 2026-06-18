# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_sh_mask.h lines 3623-7461

## Purpose

This chunk is part of the generated AMDGPU DCE 6.0 register field mask/shift header. It contains no executable C code; it publishes compile-time constants for decoding and programming bit fields in Southern Islands / DCE 6.0 display-engine registers.

Each register field is represented by paired macros:

- `REGISTER__FIELD_MASK` gives the already-positioned bit mask.
- `REGISTER__FIELD__SHIFT` gives the least-significant bit position for inserting or extracting the field.

Driver code combines these masks and shifts with register address constants from the matching `dce_6_0_d.h` header and with AMDGPU register helpers such as `RREG32()`, `WREG32()`, and `REG_SET_FIELD()`. The header is therefore a hardware-layout contract: correctness depends on exact bit positions rather than local algorithms in this file.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or runtime APIs in this chunk. The macro namespace is the API surface consumed by display, interrupt, GPIO, power, graphics plane, and HDMI/audio code.

Major macro groups in this line range are:

- Display GPIO and pin control: `DC_GPIO_GENLK_*`, `DC_GPIO_HPD_*`, `DC_GPIO_I2CPAD_*`, `DC_GPIO_PWRSEQ_*`, and `DC_GPIO_SYNCA_*` define masks for genlock, swaplock, hotplug detect, I2C DDC pads, panel power sequencing pins, and sync outputs. These fields cover output values, output enables, input reads, mask bits, pull-up/pull-down controls, and pad drive strengths.
- GPU timer and hotplug detect: `DC_GPU_TIMER_*` gives timing read and event-position fields for vsync, page flip, and vertical update; `DC_HPD1_*` through `DC_HPD6_*` define connection timers, HPD enable, interrupt status/ack/enable/polarity, RX interrupt handling, fast-train delays, and toggle filtering.
- Display clock, reset, and power control: `DCI_*`, `DCO_*`, `DENTIST_DISPCLK_CNTL`, `DIG_SOFT_RESET`, `DCI_SOFT_RESET`, `DCO_SOFT_RESET`, memory power-state fields, light-sleep disables, clock ramp controls, and `DISPCLK_FREQ_CHANGE_CNTL` describe display clocking, display controller resets, memory power gating, and clock-change sequencing.
- Interrupt routing and status: `DISP_INTERRUPT_STATUS*`, `DMCU_INTERRUPT_STATUS*`, `DMCU_INTERRUPT_TO_HOST_EN_MASK*`, `DMCU_INTERRUPT_TO_UC_EN_MASK*`, `DMCU_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*`, and `DC_I2C_INTERRUPT_CONTROL*` expose display, DMCU, HPD, I2C, and pipeline interrupt status and routing fields.
- DMCU and debug access: `DMCU_*`, `DCIO_DEBUG*`, `DCI_TEST_DEBUG_*`, `DCP_TEST_DEBUG_*`, `DCPG_TEST_DEBUG_*`, `DMIF_TEST_DEBUG_*`, and `DOUT_SCRATCH*` define microcontroller RAM/ERAM/IRAM access, firmware address/checksum state, internal interrupt state, debug index/data windows, and scratch fields.
- Display pipe, DCP, DMIF, LUT, and FBC controls: `DCP_*`, `DC_LUT_*`, `DEGAMMA_CONTROL`, `DENORM_CONTROL`, `DMIF_*`, `DPG_PIPE_*`, `FBC_*`, and `FMT_*` cover color processing, dithering, CRC, LUT access, display memory interface address/arbitration/status, pipe stutter/NB p-state controls, frame buffer compression, formatter CRC, and bit-depth controls.
- Digital output, DisplayPort, DVO, and HDMI packet fields: `DIG_*`, `DOUT_*`, `DP_*`, `DVO*`, `HDMI_*`, `GENFC_*`, and `GENMO_*` describe digital encoder controls, FIFO/status/test-pattern controls, DP secondary packets/MSE/audio framing/PHY symbols, DVO FIFO and mode controls, legacy VGA fields, HDMI ACR/audio/infoframe/generic-packet controls, deep-color state, keepout, AVMUTE, and packing phase.
- Legacy VGA and graphics plane fields: `GRA00` through `GRA08`, `GRPH8_*`, and `GRPH_*` define VGA graphics-controller fields plus primary display-surface state: depth, format, tiling, bank/pipe layout, pitch, primary/secondary/compressed surface addresses, DFQ status/reset, page-flip interrupts, LUT bypass, stereo flip, endian/component swap, update locking and pending/taken bits, visible surface offsets, and source rectangle coordinates.

The range starts in the middle of the `DC_GPIO_GENLK_MASK` block and ends inside the HDMI infoframe-control block. Earlier and later chunks complete the full `dce_6_0_sh_mask.h` namespace.

## Control Flow

This file has no runtime control flow. Every line is a preprocessor definition.

Runtime behavior appears in consumers that follow a read-modify-write pattern:

1. Select a register address from `dce_6_0_d.h`, such as `mmDC_HPD1_CONTROL`, `mmHDMI_GC`, or `mmGRPH_CONTROL`.
2. Read the register through AMDGPU's MMIO helpers.
3. Extract, clear, or insert a field using the `*_MASK` and `*__SHIFT` macros, often through `REG_SET_FIELD()`.
4. Write the result back when the register is writable and the display block is in a valid state for the operation.

Control-sensitive fields in this chunk include HPD interrupt enable/ack/polarity, DMCU interrupt routing, display clock ramp/frequency-change controls, soft resets, memory power-state controls, DPG stutter and NB p-state controls, graphics surface update locking/pending fields, page-flip interrupt controls, HDMI packet send/continuous/auto-send controls, and DP secondary-packet framing fields. The header itself does not enforce sequencing; that responsibility stays in the display and power-management code.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes state held in display-engine hardware registers.

The represented hardware state includes connector GPIO levels, HPD sense and interrupt latches, DDC/I2C transaction status, display clock and reset bits, DMCU program/RAM/debug state, display interrupt status and masks, LUT and color-pipeline controls, DMIF arbitration and status, FBC controls, display-pipe stutter policy, graphics surface addresses and tiling, page-flip/update-pending state, DP and HDMI packet generator state, and legacy VGA register fields.

Persistence is hardware-specific. Some fields are read-only status snapshots, some are sticky interrupt/status bits cleared by ack fields, some are latched until the next vblank or surface update, and some are programmed control bits that remain until a later driver/firmware write, modeset, suspend/resume, display reset, ASIC reset, or power-gating transition. The mask header does not encode access permissions, volatility, write-one-to-clear behavior, or timing requirements.

## Dependencies And Integration Points

This chunk depends on the generated DCE 6.0 address header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_6_0_d.h`

Direct include points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/dce_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v6_0.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/si.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce60/dce60_timing_generator.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_factory_dce60.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce60/dce60_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dce60/irq_service_dce60.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce60/dce60_resource.c`

Concrete consumers in `dce_v6_0.c` use this chunk's fields to enable and disable HPD pins with `DC_HPD1_CONTROL__DC_HPD1_EN_MASK`, configure HPD interrupt controls, program HDMI audio and infoframe packet controls with `HDMI_*` fields, mute HDMI through `HDMI_GC__HDMI_GC_AVMUTE`, and construct display surface format/swap values with `GRPH_CONTROL__GRPH_DEPTH__SHIFT`, `GRPH_CONTROL__GRPH_FORMAT__SHIFT`, and `GRPH_SWAP_CNTL__*` fields.

Although the source tree path is under a local `ceph-client` mirror, this file is AMDGPU Linux kernel display-register metadata. It has no Ceph filesystem semantics, no distributed-storage protocol behavior, and no persistent filesystem state.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Incorrect masks or shifts can compile successfully while reading the wrong status bit, failing to update the intended field, or corrupting adjacent bits in packed display registers.

High-risk areas include HPD and DDC fields. Bad HPD masks can cause missed monitor hotplug events, interrupt storms, wrong connector sense, or broken eDP/LVDS behavior. Bad I2C/DDC transaction or arbitration fields can break EDID reads and connector detection.

Clock, reset, and power fields are also sensitive. Incorrect `DENTIST_DISPCLK_CNTL`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCI_*`, `DCO_*`, or soft-reset definitions can destabilize modesets, suspend/resume, dynamic power management, display memory power gating, or DMCU communication.

Graphics surface fields carry direct scanout risk. Wrong `GRPH_CONTROL`, address, pitch, tiling, endian-swap, component-crossbar, update-lock, or page-flip interrupt definitions can produce corrupted display output, scanout from the wrong address, bad big-endian behavior, missed flip completion, or hangs while waiting for update-pending bits.

HDMI/DP packet fields affect protocol compliance. Bad ACR, infoframe, audio packet, generic packet, deep color, keepout, AVMUTE, DP secondary-packet, or MSE fields can cause missing audio, incorrect color/deep-color signaling, bad infoframes, link protocol errors, or display compatibility regressions.

The chunk boundaries are artificial. The first lines continue a `DC_GPIO_GENLK_MASK` register started earlier, and the final lines stop in the HDMI infoframe area before the header continues. The later per-file merge should not interpret these line-range boundaries as real module boundaries.

## Test Signals

Useful validation signals are mostly compile-time and hardware-behavior oriented:

- Kernel build coverage for Southern Islands / DCE 6.0 AMDGPU paths that include `dce_6_0_sh_mask.h`.
- Static comparison of every generated `*_MASK` and `*__SHIFT` pair against AMD's register database and the adjacent address definitions in `dce_6_0_d.h`.
- Connector hotplug tests across HPD1-HPD6, including connect/disconnect, interrupt ack/polarity, eDP/LVDS cases, and repeated DPMS or suspend/resume cycles.
- DDC/EDID reads through all relevant GPIO/I2C pads, including timeout, NACK, arbitration, and software/hardware I2C status paths.
- Modeset and page-flip tests that exercise all supported framebuffer formats, tiling modes, endian/component swap paths, surface address changes, update locks, flip interrupts, and vblank synchronization.
- HDMI audio/video tests covering ACR N/CTS programming, audio packet enablement, infoframe transmission, AVMUTE, generic packets, deep color, and keepout behavior.
- DisplayPort secondary-packet and MSE tests, plus PHY symbol/status checks where available.
- Power-management and reset tests that cover display clock frequency changes, stutter/NB p-state transitions, memory power states, DMCU interrupts, and resume from system/runtime suspend.
- CRC/FBC/debug validation where lab or debugfs tooling can compare expected display CRCs, frame-buffer compression state, interrupt status, and debug-index/data reads.

Regression symptoms from bad constants include no display after modeset, corrupted scanout, wrong colors or byte order, missed or repeated hotplug interrupts, EDID read failures, missing HDMI audio, incorrect HDMI/DP infoframes, page-flip timeouts, vblank/interrupt loss, display clock instability, suspend/resume display failures, and DMCU or FBC diagnostics reporting inconsistent state.

## Cross-Chunk Notes

Earlier chunks of `dce_6_0_sh_mask.h` define AFMT, audio, cursor, CRTC, viewport, scaler, and the beginning of the GPIO namespace. Later chunks continue HDMI/infoframe, memory-display latency/watermark, overlay, scaler, stereo, vblank/vline, viewport, and related DCE 6.0 display fields. The final per-file research document should treat the full header as one generated DCE 6.0 register-layout contract rather than as independent algorithms per chunk.
