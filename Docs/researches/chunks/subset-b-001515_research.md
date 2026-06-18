# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_0_sh_mask.h lines 7721-11767

## Purpose

This chunk is a large middle section of the generated AMD DCE 11.0 shift/mask header. It defines preprocessor constants for packed bit fields in display-controller registers: each exported symbol is a `REGISTER__FIELD_MASK` or `REGISTER__FIELD__SHIFT` value used by AMDGPU display code to compose or decode 32-bit MMIO register values without hard-coding bit positions.

The range covers several major DCE hardware surfaces:

- DMCU interrupt routing for display perfmon events and DisplayPort receiver events.
- DisplayPort link, video stream, MSA/VBID, secondary-data-packet, MST, DPHY training/CRC, and AUX channel control/status.
- DVO output and FIFO/CRC diagnostics.
- Frame buffer compression (FBC), formatter (FMT), line buffer (LB/LBV), multi-VPU/MVP, scaler (SCL/SCLV), and color-management blocks.
- Underlay graphics (UNP) surface, tiling, DVMM/PTE, flip, interrupt, CRC, and rotation controls.
- Legacy VGA sequencer/CRTC/graphics/attribute registers and VGA display mux/control state.
- Pixel/display PLL and VGA PPLL fields, plus the beginning of UNIPHY transmitter and power-control fields.

This file does not implement policy or algorithms. Its purpose is to preserve the ASIC register layout as C macros so higher-level display, power, hotplug, AUX/I2C, color, flip, and clock code can perform read-modify-write operations against the correct hardware bits.

## Important APIs, Types, And Functions

There are no C functions, structs, enums, or callable APIs in this chunk. The important interface is the generated macro namespace:

- `DMCU_PERFMON_INTERRUPT_TO_UC_EN_MASK*` and `DMCU_PERFMON_INTERRUPT_TO_UC_XIRQ_IRQ_SEL*`: enable and IRQ-route perfmon counter/off interrupts for DCI, DCO, DCCG, DCFE0-5, WB, DCRX, and DCFEV paths.
- `DMCU_DPRX_INTERRUPT_STATUS1`, `DMCU_DPRX_INTERRUPT_TO_UC_EN_MASK1`, and `DMCU_DPRX_INTERRUPT_TO_UC_XIRQ_IRQ_SEL1`: status/clear, microcontroller enable, and XIRQ selection fields for DPRX stream events, DPHY errors, AUX/I2C/CPU events, and AUX message timeouts.
- `DP_*`: DisplayPort link and video stream fields, including `DP_LINK_CNTL`, pixel format/colorimetry, lane configuration, M/N video timing, framing, HBR2 pattern, VBID/MSA placement, stream-disable interrupt, DPHY training pattern/symbol/8b10b/PRBS/scrambler/CRC/fast-training state, secondary packet/audio timestamp controls, MST rate and slot allocation, and DP debug windows.
- `AUX_*` and `DP_AUX_DEBUG_*`: AUX transaction control, software and low-speed status/data, arbitration, interrupt enables, DPHY TX/RX timing/status, GTC sync control/status/data, phase override, and debug readback registers.
- `DVO_*`: digital video output enable, source select, output/clock/sync/color format, FIFO error calibration/status, CRC, and debug fields.
- `FBC_*`: frame buffer compression enable/source/coherency/clock gating, compression modes and LUTs, CSM region offsets, privileged/address-translation debug controls, decompression error handling, and status.
- `FMT_*`: clamp, dynamic expansion, pixel encoding/subsampling/source selection, truncation, spatial and temporal dithering, programmable dither matrices, CRC collection/masks/results, and debug fields.
- `LB_*` and `LBV_*`: primary and video line-buffer data format, memory sizing, desktop height, vline/vblank interrupt/status, sync reset, keyer colors, buffer level/urgency/empty/full status, and debug fields. `LBV_*` adds chroma counters and video-plane variants.
- `MVP_*`: multi-VPU/mixer controls, AFR flip, FIFO watermarks/status, slave timing counters, in-band control, CRC, flow/swap-lock debug, and async FIFO debug fields.
- `SCL_*` and `SCLV_*`: scaler coefficient RAM indexing/data, mode/tap/filter controls, horizontal/vertical ratios and init phases, update locking, sharpening, viewport/overscan, mode-change detection, host-conflict status, and video/chroma variants.
- `COL_MAN_*`, `INPUT_CSC_*`, `OUTPUT_CSC_*`, `GAMMA_CORR_*`, and `INPUT_GAMMA_*`: color-management update locks, input/output CSC matrices, prescale, denorm clamps, gamma/PWL region definitions, LUT access/autofill, FIFO error flags, and input gamma controls.
- `UNP_*`: underlay enable, tiling/depth/banking/format, surface addresses and in-use addresses, pitch, source rectangles, update locking, DVMM PTE controls/arbitration, flip interrupts, stereosync flips, CRC, rotation, outstanding request limits, and debug fields.
- `GEN*`, `SEQ*`, `CRT*`, `GRA*`, `ATTR*`, and `VGA_*`: legacy VGA miscellaneous, DAC, sequencer, CRTC, graphics controller, attribute controller, render/memory/cache/HDP/control/status/interrupt/test fields, and per-pipe `D1VGA_CONTROL` through `D6VGA_CONTROL`.
- `BPHYC_*`, `PLL_*`, `VGA25_PPLL_*`, `VGA28_PPLL_*`, `VGA41_PPLL_*`, `DISPPLL_BG_CNTL`, `PPLL_*`: DAC analog controls, PLL dividers, spread-spectrum/delta-sigma settings, ID clock, reset/power/calibration/lock status, analog and regulator trims, update/debug state, and VGA-specific PLL triplets.
- `UNIPHY_TX_CONTROL1` through `UNIPHY_TX_CONTROL4` and the first `UNIPHY_POWER_CONTROL` fields: transmitter pre-emphasis, voltage swing, pull-down/drive trim, operating point, bandgap power-down, logic reset, and bias reference selection.

The companion register-address constants are in the matching generated DCE 11.0 register definition headers, typically `dce_11_0_d.h` and related generated AMD ASIC headers. Consumers pair those register offsets with these masks/shifts through AMDGPU register helpers.

## Control Flow

This header has no runtime control flow. Its operational flow is compile-time macro expansion:

1. A DCE 11.0 display, power, AUX, or diagnostic source file includes the generated register address and shift/mask headers.
2. The source chooses a register offset such as a DP, AUX, FMT, LB, UNP, VGA, PLL, or UNIPHY register.
3. It uses a `*_MASK` constant to isolate or clear the target field and the matching `*__SHIFT` constant to align a field value.
4. The resulting value is read from or written to hardware through AMDGPU MMIO helpers such as direct register access, indexed register access, or higher-level display helper macros.

Runtime sequencing is owned by callers. For example, a caller programming a mode would coordinate surface addresses, underlay update locks, line-buffer/scaler settings, formatter bit depth, DP stream enablement, and PLL/PHY state. This chunk only provides the bit encodings that make those sequences target the intended hardware fields.

Several field families imply hardware handshakes that callers must respect:

- `*_UPDATE_LOCK`, `*_UPDATE_PENDING`, and `*_UPDATE_TAKEN` fields gate atomic or double-buffered updates in scaler, color-management, underlay, and PLL blocks.
- `*_ACK`, `*_CLEAR`, and `*_OCCURRED` fields implement interrupt/status clear protocols for DMCU/DPRX, DP stream disable, AUX/GTC sync, line-buffer, MVP, FMT/UNP CRC, FIFO errors, and VGA interrupts.
- PLL and link-training fields such as `PLL_LOCKED`, `PLL_CALIB_DONE`, DPHY fast-training status, and DP stream status are state machines that must be polled or observed by higher layers.

## State And Persistence Behavior

The chunk stores no software state, allocates no memory, and performs no MMIO by itself. It is a declarative mapping from hardware field names to masks and shifts.

When used by callers, the affected state is persistent device register state:

- Display mode state: DP stream enable, pixel format, M/N timing, MSA/VBID, MST slot allocation, formatter pixel encoding, dither/truncation mode, line-buffer memory, scaler ratio/taps/coefficients, viewport/overscan, and color-management matrices/LUTs.
- Surface and flip state: underlay tiling/depth/address/pitch/source rectangles, primary/secondary/bottom surface pending bits, update locks, page-flip interrupt masks/types, DVMM PTE buffering, and rotation.
- Error and diagnostic state: sticky interrupt/status bits, CRC enable/result fields, FIFO underflow/overflow status, FBC decompression errors, DPRX DPHY/AUX timeouts, and debug mux/index/data windows.
- Link and clock state: AUX channel arbitration/status/data, DPHY training and test patterns, PLL reset/power/divider/spread-spectrum/lock/update state, VGA PLL settings, and UNIPHY transmitter drive/power trims.
- Legacy compatibility state: VGA sequencer, CRTC, graphics, attribute, DAC, memory base, cache/HDP, render, and per-pipe mux controls.

Most register values persist until overwritten, reset by a block-level reset, power-gated, or lost during GPU reset/suspend. Status and interrupt bits may be write-one-to-clear or acknowledge-driven depending on the register; the paired `*_ACK`/`*_CLEAR` masks in this chunk are the only local clue, so caller-side protocol must match the hardware programming guide.

## Dependencies

This chunk depends on the surrounding generated AMD register ecosystem:

- The top-level include guard, license text, and prior/later DCE 11.0 definitions in `dce_11_0_sh_mask.h`.
- Matching DCE 11.0 register-address headers that define `mm*` or indexed register constants for these field names.
- AMDGPU display and power-management register-access helpers that understand mask/shift pairs and perform 32-bit MMIO read-modify-write operations.
- DCE 11.0 hardware semantics for display pipes, DIG/DP/AUX, DMCU, FBC, FMT, LB, SCL, color management, underlay, VGA, PLL, and UNIPHY blocks.
- Linux DRM/AMDGPU call paths that decide when to program mode state, hotplug/AUX transactions, page flips, gamma/CSC updates, power transitions, and display clock/PHY changes.

The chunk also has implicit dependency on ASIC register-generation correctness. A stale or mismatched mask can compile cleanly while causing silent hardware misprogramming.

## Integration Points

The main integration point is the AMDGPU DCE 11.0 display stack. These macros are consumed by code that sets modes, programs display planes, services vblank/vline/page-flip interrupts, performs AUX/I2C/DP link operations, controls power states, and handles diagnostics.

Specific integration surfaces include:

- DisplayPort encoder/link handling: `DP_*`, `AUX_*`, and `DMCU_DPRX_*` fields support link training, stream enable/disable, AUX transactions, MST slot allocation, audio/SDP packets, CRC/debug tests, and receiver-side event routing.
- Display pipe programming: `FMT_*`, `LB_*`, `LBV_*`, `SCL_*`, `SCLV_*`, and color-management fields support DRM mode-setting, plane format conversion, scaling, overscan, dithering, gamma/CSC, CRC capture, and vblank/vline timing behavior.
- Surface update and flip handling: `UNP_*` fields expose underlay/overlay-like surface addresses, tiling metadata, update locks, DVMM request behavior, flip interrupt control, stereosync flips, and in-use readback state.
- Power and clock management: `PLL_*`, `PPLL_*`, `DISPPLL_BG_CNTL`, `BPHYC_*`, and `UNIPHY_*` fields connect display mode programming to pixel-clock generation, analog calibration, PHY transmitter settings, and suspend/resume or BACO-style power sequences.
- Legacy boot/console compatibility: VGA register macros allow early display, VGA arbitration, console handoff, and compatibility paths to program or inspect legacy VGA state.
- Diagnostics and validation: CRC, debug index/data, status, error, and FIFO fields are integration points for bring-up, hardware validation, debugfs-like inspection, and automated display test flows.

The chunk starts in the middle of the larger DMCU perfmon/DPRX region and ends in the middle of `UNIPHY_POWER_CONTROL`. The per-file reconciliation lane must merge adjacent chunks for a complete register-family view.

## Risks And Edge Cases

- Mask/shift mistakes are high impact because many callers use read-modify-write operations. A wrong field definition can corrupt adjacent control bits while still compiling.
- Status and clear bits often share masks, as seen in the DPRX status/clear pattern. Callers must distinguish read status from write-clear semantics; treating clear bits like ordinary writable state can drop interrupts.
- Update-lock fields must be used coherently. Programming scaler, color-management, underlay, or PLL fields without honoring pending/taken/lock semantics can produce tearing, partial mode updates, or clock glitches.
- DP/AUX and DPHY fields are timing-sensitive. Wrong timeout, training, PRBS, scrambler, fast-training, or AUX arbitration settings can break link training, EDID/DPCD access, MST, or HDCP-related AUX traffic.
- FMT/FBC/LB/SCL/color-management fields are visually sensitive. Incorrect dither depth, truncation, clamp range, CSC/gamma region, viewport, tap coefficient, or line-buffer memory setting can cause banding, color shifts, underruns, blanking artifacts, or scaling defects.
- UNP surface and DVMM fields include address, tiling, privileged access, translation enable, PTE buffering, and outstanding request controls. Bad values can fetch from the wrong memory, fault display reads, or expose stale/wrong pixels.
- PLL/UNIPHY and analog fields are hardware-sensitive. Incorrect reset, power-down, divider, spread-spectrum, calibration, voltage swing, or pre-emphasis programming can cause no-display, unstable links, EMI problems, or suspend/resume regressions.
- Legacy VGA fields overlap compatibility behavior. Incorrect VGA memory base, sequencer reset, CRTC timing, cache/HDP, or per-pipe VGA mux values can break firmware console handoff or multi-display boot paths.
- Several repeated register families (`LB` versus `LBV`, `SCL` versus `SCLV`, VGA25/28/41 PPLLs, D1-D6 VGA controls) are copy-patterned. Generation drift or suffix confusion can map a valid-looking field to the wrong block variant.
- This chunk is part of a generated header. Manual edits risk divergence from the hardware register database and should be avoided unless regenerating or applying a verified ASIC-header update.

## Test Signals

Useful validation signals for this chunk are build-time, static, display-functional, and hardware-observable:

- Kernel/AMDGPU builds including DCE 11.0 register headers should compile without missing macro or duplicate-definition errors.
- Static generation checks should verify each `REGISTER__FIELD_MASK` has the matching `REGISTER__FIELD__SHIFT`, masks do not unintentionally overlap within a register, and repeated families preserve expected field positions.
- Register read-modify-write unit or simulator tests should confirm that helper macros using these constants change only intended bits for representative DP, AUX, FMT, LB, SCL, UNP, VGA, PLL, and UNIPHY fields.
- Display mode tests should cover multiple pixel formats, bit depths, RGB/YCbCr range/colorimetry, dithering/truncation modes, scaling ratios, viewport/overscan settings, gamma/CSC programming, and FBC enable/disable.
- DP tests should exercise AUX DPCD/EDID reads, hotplug/disconnect, link training at multiple rates/lane counts, HBR2 patterns, MST slot allocation, stream disable interrupts, audio/SDP packet programming, and CRC/debug paths.
- Flip and vblank tests should verify page-flip completion interrupts, vblank/vline status/ack behavior, underlay in-use surface readback, stereosync/stack-interlace flip modes, and update-lock sequencing.
- Error-path tests should induce or simulate AUX timeouts, DPHY errors, FIFO underrun/overflow, FBC decompression errors, line-buffer empty/full events, and scaler coefficient host conflicts, then confirm status/ack fields behave as expected.
- Clock/PHY tests should validate PLL lock/calibration/readback, spread-spectrum settings, PPLL update state, suspend/resume, power-gating/BACO paths, and UNIPHY voltage-swing/pre-emphasis programming across supported connector types.
- VGA compatibility tests should include firmware console handoff, fbcon/simpledrm to amdgpu transition, VGA disable/enable paths, and multi-pipe VGA source selection on DCE 11.0 ASICs.
