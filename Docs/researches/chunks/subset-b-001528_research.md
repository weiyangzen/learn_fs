# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h lines 15027-18695

## Scope And Purpose

This chunk is the final generated-style section of the AMD DCE 11.2 register shift/mask header. It contains C preprocessor constants only: each hardware register field is exposed as a `REGISTER__FIELD_MASK` constant and a matching `REGISTER__FIELD__SHIFT` constant. There are no functions, structs, enums, storage definitions, or executable branches in this range.

The range starts at the shift for `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE__MULTICHANNEL7_ENABLE`; its matching mask is immediately before the assigned range. It then covers the tail of Azalia HDMI/DP audio input-pin status, display blender and writeback/capture blocks, DCFE/DCFEV power and flush control, HPD and display interrupt status, DCO clock/power/reset control, display I2C/DDC engines, video blender and CRTCV timing/CRC, XDMA scanout transport, display PHY lane/PLL controls, PPLL controls, DPCSTX transmitter controls, and the closing `#endif` for `DCE_11_2_SH_MASK_H`.

The purpose is to let DCE 11.2 display, power, and firmware-facing code compose or extract fields in MMIO registers using symbolic masks instead of hard-coded bit positions. These macros are normally paired with register address definitions from `dce_11_2_d.h`, enumerated legal values from `dce_11_2_enum.h`, and AMDGPU/DC register helpers such as `REG_SET_FIELD`, `REG_UPDATE`, `REG_GET`, `set_reg_field_value`, `RREG32`, and `WREG32`.

## Important APIs, Types, And Macro Families

The public API surface is the macro namespace itself. Important families in this assigned range are:

- `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_*`: final input-pin audio controls for multichannel channel 7, channel allocation, input activity/layout, unsolicited response enables, infoframe validity and payload bits, IEC/channel-status low/high words, LPIB snapshot locking, and LPIB/timer snapshots. These support HDMI/DP audio status and stream-position reporting.
- `BLND_*` and `BLNDV_*`: main and video blender controls for global gain/alpha, stereo mode/polarity, feedthrough, multiplied alpha, PTI/new-pixel modes, update pending/taken/lock bits, underflow interrupt occurred/ack/mask/pipe index, vertical update locks across DCP/CUR/SCL/BLND blocks, update-pending status, and indexed debug access.
- `WB_*` and `CNV_*`: writeback enable, clock-gating and memory-power controls, writeback soft reset and warm-up mode, capture/conversion mode, crop window, source size, capture update locks, CSC matrix coefficients, round offsets, clamps, CRC test controls/results, input pipe/source selection, and debug data.
- `DCFE_*` and `DCFEV_*`: display front-end clock gating, soft-reset, debug selection, memory power-control/status, flush controls, DMIFV clock/memory/debug controls, and miscellaneous state for normal and video front-end paths.
- `DC_HPD_*`: hotplug interrupt status/control, HPD signal control, fast-training controls, and toggle filter timing.
- `DISP_INTERRUPT_STATUS*`: base and continuation status registers covering a large display interrupt fan-in. The continuation registers encode line/vblank, page-flip, underflow, AUX/I2C, DMCU, DCO, DCFE, WB, HPD-like, and other display-block interrupt occurred bits across multiple pipes and subblocks.
- `DCO_*`, `FMT_MEMORY*_CONTROL`, `DPDBG_*`, `DCE_VCE_CONTROL`, and `DIG_SOFT_RESET*`: display controller output memory power/status, clock control, power management, soft reset, stereosync, HDMI RX status timing, PSP/generic interrupt handshakes, formatter memory controls, DisplayPort debug, and DIG reset controls.
- `DC_I2C_*` and `GENERIC_I2C_*`: DDC and generic I2C engine control, arbitration, interrupt control, software status, per-DDC hardware status/speed/setup for DDC1-6 and VGA DDC, transaction descriptors, data ports, EDID detect, read-request interrupt state, pin selection, and pin debug.
- `CRTCV_*`: video timing generator fields for horizontal/vertical totals, blanking, sync, enable/control flags, start-line behavior, overscan/black colors, CRC control/window/result registers, and indexed test debug.
- `XDMA_*`: XDMA display-transport and peer/cross-adapter scanout controls, including PCIe/memory client config, local tiling, interrupts, clock/memory power, interface status, power gating, master/slave control/status, local and remote surface addresses, pitch/dimensions, urgent controls, NACK status, GSL/vsync checks, pipe controls, read commands, cache config, performance measurement, read/write latency, flip pending, channel controls, and debug windows.
- PHY lane controls: `CMD_BUS_TX_CONTROL_LANE*`, `MARGIN_DEEMPH_LANE*`, `CMD_BUS_GLOBAL_FOR_TX_LANE*`, `TX_DISP_RFU*_LANE*`, `COMMON_*`, and `COMP_EN_CTL` describe per-lane command bus enable/reset/calibration, transmit pre/de-emphasis margins, reserved lane words, common lane power management/resets, common transmitter control, TMDP/zcal, and impedance/compensation calibration.
- Display PLL controls: `FREQ_CTRL*`, `BW_CTRL_*`, `CAL_CTRL`, `LOOP_CTRL`, `VREG_CFG`, `OBSERVE*`, `DFT_OUT`, `PLL_WRAP_CNTRL*`, and the `PPLL_*` mirrors describe fractional/integer frequency control words, denominators, reference/VCO/pre/post dividers, spread-spectrum enable, bandwidth coefficients, calibration controls, loop behavior, regulator settings, observation/debug muxes, update locking/pending/ready flags, reference clock routing, clock-out selectors, DFT/analog spares, and status/debug readback.
- `DPCSTX_*`: DisplayPort/clocked serial transmitter reset, symbol clock gating/enables, lane FIFO and link-mode controls, TX PLL update request/pending, CBUS delays/reset, register/TX FIFO error status and clear/mask fields, indexed PLL update/data windows, indexed register/data windows, debug muxing, and test debug data.

Generated field names ending in `MASK` produce identifiers such as `DPCSTX_REG_ERROR_STATUS__DPCS_REG_FIFO_ERROR_MASK_MASK`; the doubled suffix is intentional and means "mask for the hardware field named `..._MASK`."

## Control Flow And Data Flow

This header has no runtime control flow. Its data flow is compile-time macro expansion into register access code. A typical consumer selects an MMIO address from `dce_11_2_d.h`, combines it with an instance offset where needed, clears a field using `*_MASK`, inserts or extracts a value with `__SHIFT`, and reads or writes the register through DC/AMDGPU helpers.

The implied hardware flows are:

- Audio status code reads or writes Azalia input-pin fields to represent channel allocation, layout/activity, infoframe validity, channel status words, and LPIB snapshots.
- Blender/writeback/capture paths program update locks, alpha/stereo/crop/CSC/clamp fields, then observe update pending/taken, underflow, and CRC/debug fields.
- DCFE/DCFEV and DCO sequencing code gates clocks, asserts/deasserts soft reset, manages memory power state, flushes front-end FIFOs, and checks status fields.
- HPD, display interrupt, DCO PSP/generic, I2C, and read-request interrupt fields feed interrupt handlers or polling loops that must distinguish status, mask, clear, ack, and routing semantics.
- I2C/DDC consumers configure bus speed/setup/transaction/data registers, arbitrate ownership, then poll status or interrupt bits for DONE/NACK/timeout/error conditions.
- CRTCV timing and CRC fields are programmed as part of video timing, test-pattern, validation, and display CRC capture sequences.
- XDMA master/slave fields configure local and remote surfaces, dimensions, urgent thresholds, channel start, and cache/client behavior for display data movement, then expose NACK, latency, flip, and performance status.
- PHY, PLL, and DPCSTX fields are part of low-level link bring-up: lane reset/power/calibration, clock divider/frequency programming, PLL update handshakes, symbol-clock enabling, FIFO start, and debug/error reporting.

## State And Persistence Behavior

The header stores no mutable state. Persistent state lives in DCE 11.2 hardware registers and in firmware-visible or driver-visible state machines that those registers control.

State represented by this chunk includes:

- Durable configuration until reprogram/reset: blender alpha/stereo behavior, writeback/capture crop and CSC, DCFE/DCO clock and memory-power controls, HPD filters, I2C speed/setup, CRTCV timing/CRC window configuration, XDMA surfaces and urgent thresholds, PHY lane settings, PLL dividers/calibration settings, and DPCSTX transmitter modes.
- Shadowed or synchronized update state: `BLND_UPDATE`, `BLNDV_UPDATE`, `CNV_UPDATE`, vertical update locks, register-update status bits, TX PLL update pending/request, and PPLL update lock/point/pending/ready fields. These are intended to make multi-register display changes visible at controlled hardware update points.
- Latched or transient status: audio input activity and LPIB snapshots, underflow occurred bits, display interrupt continuation bits, HPD status, DCO PSP/generic interrupt status, I2C software/hardware status, read-request interrupts, CRTCV CRC results, XDMA NACK/latency/flip/performance status, PHY/DPCSTX FIFO error status, PLL lock/ready/status, and compensation calibration done.
- Diagnostic and validation state: indexed debug registers across BLND, CNV, DCO, XDMA, CRTCV, DPCSTX, DFT/observe outputs, FMT memory controls, DP debug interrupts, and PHY reserved/RFU words.

Wrong constants can persist in active hardware until a modeset, reset, suspend/resume restore, or explicit reprogramming path fixes them. PLL, PHY, DPCSTX, and XDMA mistakes can blank a link or corrupt scanout. Interrupt mask/clear mistakes can drop events or cause repeated interrupts. Update-lock mistakes can leave stale or partially-applied display state.

## Dependencies And Integration Points

Direct companion headers are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_enum.h`

Direct include sites in this repository include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`, which builds DCE 11.2 register, shift, and mask tables such as `MI_DCE11_2_MASK_SH_LIST(__SHIFT)` and `MI_DCE11_2_MASK_SH_LIST(_MASK)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`, which pairs DCE 11.2 display addresses/masks with GMC 8.1 masks for framebuffer compression and tiling-related programming.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`, which uses DCE 11.2 register tables for hardware sequencing.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c`, which constructs clock-manager register/mask/shift tables and programs display clocks through BIOS/DMCU flows.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`, which includes DCE 11.2 headers alongside SMU/GMC/BIF/GFX headers for Vegam power-management and firmware control paths.

Functional integration surfaces include DRM/DC modeset and pipe programming, display clock and power gating, HPD and display interrupt handling, HDMI/DP audio status, DDC/EDID I2C transactions, video timing/CRC validation, writeback/capture, cross-adapter/XDMA scanout, display PHY and PLL programming, DisplayPort transmitter control, firmware and SMU coordination, and hardware bring-up diagnostics.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. These are untyped constants, so the compiler cannot prove that a mask belongs to the register being accessed, that a matching shift is used, or that a value fits within the field width.

Specific risks in this chunk:

- The first register group is partial: line 15027 includes `MULTICHANNEL7_ENABLE__SHIFT`, but the matching `MULTICHANNEL7_ENABLE_MASK` is in the previous chunk.
- The assigned range includes the final `#endif`; file-level reconciliation should treat it as the header guard close, not a register definition.
- There are many repeated pipe/lane/register families: `DISP_INTERRUPT_STATUS_CONTINUE*`, DDC1-6, lane0-3 PHY controls, TX RFU words, `FMT_MEMORY0-5`, `DCO_SCRATCH0-7`, BLND versus BLNDV, and normal DCFE versus DCFEV. Copy/paste or generated-table drift can affect only one instance and be hard to spot.
- Status/mask/ack/clear naming is dense. Fields with `*_MASK_MASK`, `*_INT_MASK`, `*_CLEAR`, `*_ACK`, `*_OCCURRED`, `*_PENDING`, and `*_TAKEN` have different semantics; treating a clear or ack bit as ordinary configuration can lose events.
- Update-lock fields must align with hardware timing. Bad BLND/CNV/PPLL/DPCSTX update masks can cause partially-applied display state, PLL update stalls, or link bring-up failures.
- PLL/PHY/DPCSTX fields are ASIC- and board-sensitive. Incorrect dividers, calibration bits, lane resets, CBUS delays, FIFO start timing, or symbol-clock gates can produce unstable links, no display output, or hard-to-debug compliance failures.
- I2C/DDC fields are protocol-visible. Bad transaction lengths, speed/setup, arbitration, or status interpretation can break EDID reads, AUX/I2C-over-DDC-like access, or hotplug handling.
- XDMA fields bridge display, memory, and PCIe-like paths. Wrong remote/local addresses, pitch/dimension, urgent thresholds, NACK handling, or channel start bits can corrupt scanout, hang a data path, or produce cross-GPU display failures.
- Reserved/RFU lane and common display fields are addressable but not self-documenting. They should be treated as generated hardware documentation, not as safe-to-write policy.

## Test Signals

There are no meaningful unit tests for this header alone. Useful validation comes from generated-header checks, build coverage, and hardware integration:

- Build configurations that include DCE 11.2 DC, DCE112 resource/hwseq/compressor/clock-manager code, Vegam SMU paths, and register-helper macros.
- Run a generated-header consistency check pairing each `REGISTER__FIELD_MASK` with `REGISTER__FIELD__SHIFT`, allowing the known chunk-boundary partial `AZALIA_F2_CODEC_INPUT_PIN_CONTROL_MULTICHANNEL7_ENABLE` field and ignoring the final header guard.
- Cross-check register names in this range against `dce_11_2_d.h` and legal encodings in `dce_11_2_enum.h`.
- Exercise DCE 11.2 modesets, multi-pipe display, page flips, writeback/capture, video-plane paths, suspend/resume, and power-gating transitions while monitoring DCFE/DCO/BLND/CNV update and underflow status.
- Validate HPD, DDC/EDID, generic I2C, display interrupt, and read-request interrupt behavior with connect/disconnect, NACK, timeout, and interrupt-clear scenarios.
- Validate HDMI/DP audio channel allocation, channel-status, infoframe validity, HBR/multichannel behavior, and LPIB snapshot reporting where the hardware exposes the Azalia input-pin path.
- Use display CRC and CRTCV CRC windows to detect timing, capture, blending, and color-conversion mistakes.
- Test XDMA master/slave paths where available with local and remote scanout, latency/perf counters, NACK injection or observation, flip-pending behavior, and urgent threshold stress.
- Validate PHY/PLL/DPCSTX programming through DP/HDMI link bring-up, link training, hotplug, suspend/resume, symbol-clock gating, FIFO error counters, PLL ready/update pending readback, and compliance/debug patterns.
