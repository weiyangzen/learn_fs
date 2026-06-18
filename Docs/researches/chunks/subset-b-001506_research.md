# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_10_0_sh_mask.h lines 11653-15163

## Purpose

This chunk is a generated-style DCE 10.0 register bitfield map. It defines `_MASK` and `__SHIFT` constants for 32-bit MMIO registers in the AMD display controller block, starting in the generic display PLL control fields and ending partway through the `DISP_INTERRUPT_STATUS_CONTINUE5` fields.

The range is not executable code. Its purpose is to let the DCE 10.0 driver, power-management code, and common register helpers read and write named hardware fields without open-coded bit positions. The covered register families describe display clock PLLs, VGA/PPLL variants, UNIPHY transmitter and link PLL controls, display pipe/gating watermarks, the Azalia/HD-audio controller and codec endpoint register windows, blender/writeback/converter blocks, DCFE/DCFEV clocks and memory power state, HPD interrupt control, scratch registers, VCE display control, and the display interrupt status cascade for pipes/connectors 1 through the start of 6.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this range. The important exported interface is the macro naming contract:

- `REGISTER__FIELD_MASK`: the bit mask for `FIELD` inside `REGISTER`.
- `REGISTER__FIELD__SHIFT`: the low-bit shift for the same field.
- Full-register fields, such as `PPLL_SPARE0__PLL_SPARE0_MASK` or `AZALIA_STREAM_DEBUG__STREAM_DEBUG_DATA_MASK`, use `0xffffffff` and shift `0`.
- Repeated instance fields use duplicated register families, for example `VGA25_PPLL_*`, `VGA28_PPLL_*`, `VGA41_PPLL_*`, `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR13`, `SINK_DESCRIPTION0` through `SINK_DESCRIPTION17`, and `DISP_INTERRUPT_STATUS_CONTINUE*`.

The consumers are the AMDGPU register helpers and driver code that include this header alongside `dce_10_0_d.h`, which supplies the `mm...` register addresses. In `amdgpu/dce_v10_0.c`, the file is included directly and the interrupt map uses these constants, for example `DISP_INTERRUPT_STATUS__LB_D1_VBLANK_INTERRUPT_MASK` through `DISP_INTERRUPT_STATUS_CONTINUE5__LB_D6_VBLANK_INTERRUPT_MASK` and matching HPD masks. The same style is used with `REG_SET_FIELD`, `RREG32`, `WREG32`, and audio endpoint accessors in the display driver.

## Covered Register Families

The clock and PHY portion covers:

- `PLL_CNTL`, `PLL_ANALOG`, `PLL_VREG_CNTL`, `PLL_UNLOCK_DETECT_CNTL`, `PLL_DEBUG_CNTL`, `PLL_UPDATE_LOCK`, `PLL_UPDATE_CNTL`, `PLL_XOR_LOCK`, and `PLL_ANALOG_CNTL`. These fields cover PLL reset/power down, reference-clock selection, calibration, lock status, spread/update state, debug muxing, analog trims, and lock detector controls.
- `VGA25_PPLL_*`, `VGA28_PPLL_*`, and `VGA41_PPLL_*` reference, feedback, post-divide, and analog controls. These duplicate the PPLL programming shape for legacy VGA-related clocks.
- `DISPPLL_BG_CNTL`, `PPLL_DIV_UPDATE_DEBUG`, `PPLL_STATUS_DEBUG`, `PPLL_DEBUG_MUX_CNTL`, and spare PPLL words. These expose display PLL bandgap, divider-update handshake/debug, calibration/power-good status, and debug bus muxes.
- `UNIPHY_TX_CONTROL1` through `UNIPHY_TX_CONTROL4`, `UNIPHY_POWER_CONTROL`, `UNIPHY_PLL_FBDIV`, `UNIPHY_PLL_CONTROL1`, `UNIPHY_PLL_CONTROL2`, `UNIPHY_PLL_SS_*`, `UNIPHY_DATA_SYNCHRONIZATION`, `UNIPHY_REG_TEST_OUTPUT*`, `UNIPHY_ANG_BIST_CNTL`, `UNIPHY_TMDP_REG0` through `UNIPHY_TMDP_REG6`, `UNIPHY_TPG_*`, and `UNIPHY_DEBUG`. These describe DisplayPort/HDMI/LVDS PHY drive strength, pre-emphasis, voltage swing, PLL enable/reset/reference source, spread spectrum, data synchronization, BIST, impedance calibration, test-pattern generation, and debug readback fields.

The display pipe, audio, and memory/power portion covers:

- `DPG_PIPE_*` fields for arbitration weights, urgency watermarks, DPM and memory-clock-change gates, stutter/self-refresh behavior, non-latch stutter controls, repeater programming, and DPG debug/test access.
- Azalia root/function/codec/stream/controller fields, including immediate command interfaces, HD-audio global capabilities/control/status, CORB/RIRB DMA rings, stream descriptors, wall-clock and DMA position buffers, output/input converter fields, pin sense/configuration defaults, ELD-like sink description and audio descriptor storage, channel/speaker allocation, LPIB snapshots, hot-plug/unsolicited response controls, GTC embedding/debug counters, CRC engines, clock gating, DTO phase/module, DMA cache/isochronous attributes, memory power control/status, FIFO/latency counters, and stream debug.
- `BLND_*`, `SM_CONTROL2`, `WB_*`, and `CNV_*` fields for blender mode, alpha/flow control, stereo sync mode, update locks/status, underflow interrupts, writeback enable/error-correction/debug, and converter mode/window/source-size/color-space-conversion/CRC/debug controls.
- `DCFE_*` and `DCFEV_*` clock control, soft reset, debug, DMIFV clock, and DMIFV memory power control/status fields.
- `DC_HPD_*` fields for hot-plug sense, RX interrupt status, ack, polarity, enable, HPD logic enable, fast-training enable, and connect/disconnect debounce delays.
- `DCO_SCRATCH0` through `DCO_SCRATCH7` and `DCE_VCE_CONTROL`, which provide scratch words and display/VCE shared control bits.
- `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE5`, ending at `CRTC6_FORCE_VSYNC_NEXT_LINE_INTERRUPT`. These define the cascade of latched display events for scalers, blender underflow, line-buffer vline/vblank, CRTC snapshot/trigger/vsync/timing-sync/vertical events, DIG DP fast-training or stream-disable events, HPD/AUX completion events, DMCU/ABM events, writeback conflicts/overflows, performance monitor events, and continuation bits to the next status word.

## Control Flow

This header has no control flow. At compile time, it expands into constants used by higher-level code to build bit masks and shifts. At runtime, the behavior appears in consumers:

1. A driver reads a DCE 10.0 register address from `dce_10_0_d.h`.
2. It uses a mask and shift from this header directly, or through helpers such as `REG_SET_FIELD` and field-read macros.
3. It performs MMIO access with helpers such as `RREG32()` and `WREG32()`, sometimes adding per-instance offsets such as CRTC, HPD, DIG, or audio endpoint offsets.

The display interrupt status definitions are a concrete control-flow dependency. `dce_v10_0.c` builds an `interrupt_status_offsets[]` table mapping each status register to its vblank, vline, and HPD mask. IRQ handling can then index by CRTC/HPD instance and test the correct status bits rather than branching on individual register names.

## State And Persistence Behavior

The macros hold no software state and allocate nothing. They describe persistent hardware state stored in MMIO registers. Writes performed by consumers affect display engine state until overwritten, reset, power-gated, or reinitialized by firmware/driver paths.

The state represented by this chunk is broad and hardware-visible:

- PLL/PPLL/UNIPHY fields persist clock generation, link PHY calibration, drive levels, spread-spectrum, and lock/update handshakes.
- DPG/DCFE/DCFEV/Azalia memory power fields persist clock and power gating decisions that interact with display underflow avoidance and runtime power management.
- Azalia stream descriptor, CORB/RIRB, DMA position, codec endpoint, audio descriptor, sink description, and channel-allocation fields persist the HDMI/DP audio programming visible to the audio codec model and display sinks.
- HPD and display interrupt status/control fields persist latched hardware events and enable/ack state used by interrupt handling.
- Debug, CRC, scratch, and test-pattern fields persist diagnostic configuration and readback until changed or reset.

Because the constants encode raw hardware layout, any mismatch is effectively a state corruption bug in the consumer: a read may sample the wrong status bit, or a write may alter unrelated hardware fields.

## Dependencies

This chunk depends on the DCE 10.0 register-address header `dce_10_0_d.h`; the masks are only meaningful when paired with the corresponding `mm...` or indexed `ix...` register offsets. It also depends on AMDGPU's register helper conventions, especially field-setting/extraction macros that concatenate `REGISTER`, `FIELD`, `_MASK`, and `__SHIFT` names.

The major integration dependencies are:

- `drivers/gpu/drm/amd/amdgpu/dce_v10_0.c`, which directly includes this header for DCE 10.0 display, audio, HPD, watermark, and interrupt handling.
- ASIC initialization and virtualized GPU support paths, including `vi.c`, `mxgpu_vi.c`, `gfx_v8_0.c`, and `gmc_v8_0.c`, which include the DCE 10.0 mask header as part of the VI-generation register environment.
- Power-management code under `pm/powerplay`, including Tonga/Fiji/Iceland/Polaris SMU and BACO paths, which include the header and use DCE/DPG/clock/power field definitions when coordinating display watermarks, stutter state, and low-power transitions.
- Display/audio protocols outside this file: HDMI/DP audio capabilities, HD-audio CORB/RIRB mechanics, HPD/AUX interrupt semantics, and link PHY/PLL programming rules.

## Integration Points

The most visible integration point in the covered lines is the display interrupt cascade. `DISP_INTERRUPT_STATUS` through `DISP_INTERRUPT_STATUS_CONTINUE5` map events for CRTC/display pipes 1-6 and DIG/HPD/AUX blocks. The masks let IRQ code detect vblank/vline/HPD and let diagnostic code distinguish underflow, DP training, stream-disable, timing-sync, and ABM/DMCU events.

The HPD fields integrate connector detection and link training. `DC_HPD_INT_STATUS`, `DC_HPD_INT_CONTROL`, `DC_HPD_CONTROL`, `DC_HPD_FAST_TRAIN_CNTL`, and `DC_HPD_TOGGLE_FILT_CNTL` are used around connector hotplug sense, interrupt polarity, ack/enable, and debounce timing. Incorrect bit definitions here can cause missed hotplug events, interrupt storms, or inverted connect/disconnect detection.

The Azalia fields integrate the display engine with the HD-audio codec model. `dce_v10_0.c` uses indexed endpoint accesses for codec pin and converter registers, and these masks support sink audio descriptors, speaker/channel allocation, LPIB snapshots, HBR, unsolicited responses, codec power state, and audio stream format programming. This is the bridge between DRM connector/audio setup and the GPU's HDMI/DP audio function.

The PLL and UNIPHY fields integrate modesetting with clock/link programming, mostly through AtomBIOS or display helpers that need exact divider, lock, calibration, drive-strength, voltage-swing, and pre-emphasis fields. Even when a given consumer does not open-code every field in this header, the definitions form the ABI between generated register maps and clock/link management code.

The DPG/DCFE/DCFEV fields integrate display timing with power management. Watermark, stutter, NB p-state, memory power, and clock-gating fields coordinate scanout latency tolerance with SMU/DPM decisions. These definitions are therefore cross-owned by display and power-management paths.

## Risks And Edge Cases

- This is generated register metadata with no runtime validation. A single wrong mask or shift can silently target the wrong hardware bit.
- The chunk starts mid-register family at `PLL_CNTL`; earlier `PLL_REF_DIV`, `PLL_FB_DIV`, post-divide, spread-spectrum, and IDCLK fields are in the previous chunk. A merged per-file report should preserve that boundary.
- The chunk ends mid-family at `DISP_INTERRUPT_STATUS_CONTINUE5__CRTC6_FORCE_VSYNC_NEXT_LINE_INTERRUPT`; the rest of pipe-6 status and `DISP_INTERRUPT_STATUS_CONTINUE6` continue after this range.
- The macros are not namespaced by C types. Collisions are avoided only by generated naming discipline. Manual additions must preserve the exact `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` spelling expected by helper macros.
- Repeated audio descriptor, sink description, multichannel, and interrupt-status families are copy/paste sensitive. An off-by-one instance name or bit position can affect only one connector, stream, or pipe and be difficult to spot in broad testing.
- Some fields represent write-one-to-clear, sticky status, or hardware handshake state in consumers. Treating all masks as ordinary read/write fields can break interrupt acknowledgement, PLL update sequencing, HPD ack, or CRC/test completion.
- PLL, PPLL, UNIPHY, and HPD controls are timing-sensitive. Wrong programming can produce link instability, blank displays, failed DP training, or audio clock drift rather than clean software errors.
- Power-management fields such as DPG stutter, NB p-state, DCFEV memory power, and Azalia memory power interact with active scanout and audio DMA. Incorrect masks can manifest as underflow, hangs during suspend/resume, or rare display corruption.
- Many full-register masks intentionally use `0xffffffff`; consumers must still know whether the underlying register is read-only, write-only, sticky, or indexed through an address/data pair.

## Test Signals

Useful validation signals are mostly compile-time, hardware bring-up, and display/audio behavior:

- A DCE 10.0 kernel build should compile with this header included by `dce_v10_0.c`, PM, and VI-generation files, proving macro names match helper expectations.
- Static checks can compare every `_MASK`/`__SHIFT` pair for matching register/field names and verify repeated families have consistent instance coverage.
- Modesetting tests should cover HDMI, DisplayPort, and legacy/VGA-adjacent paths that exercise PPLL/UNIPHY programming, including link training, resolution changes, blank/unblank, and suspend/resume.
- IRQ tests should verify vblank, vline, HPD connect/disconnect, AUX completion, DP fast-training, stream-disable, and underflow events are detected and acknowledged on the correct pipe/connector.
- Audio tests should validate HDMI/DP audio enumeration, sink ELD/audio descriptor programming, sample-rate and channel layouts, HBR/non-audio modes, hotplug audio enable/disable, and LPIB position reporting.
- Power-management tests should watch for display underflow, audio glitches, or missed interrupts while toggling stutter, NB p-state changes, clock gating, BACO/suspend, and runtime DPM states.
- Register-dump comparison against known-good DCE 10.0 hardware documentation or generated headers should flag any drift in PLL, UNIPHY, Azalia, HPD, DCFE, and interrupt masks.
