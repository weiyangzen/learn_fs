# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 36969-39480

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata. It contains no executable C code; it publishes C preprocessor constants that name bit positions (`__SHIFT`) and bit masks (`_MASK`) for DCN display-controller MMIO registers. Driver code combines these macros with the matching `dcn_3_0_1_offset.h` register offsets through AMD display helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `SRI`, `SR`, and block-specific field-list macros.

The requested range starts in the tail of `DC_GPIO_RXEN`, then covers GPIO pull-up and AUX/DDC pad controls, three complete UNIPHY reserved macro-control address blocks, DSC compressor instances 0 through 2, DSC-local perfmon blocks 17 through 19, the first display writeback top/perfmon/control-processing registers, and ends inside the `DWB_GAMUT_REMAPA_C11_C12` field definitions. The slice has 2,101 `#define` lines, with 1,043 shift definitions and 1,058 mask definitions.

Although the path is under a local `ceph-client` source mirror, the content is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, allocations, or persistence APIs in this chunk. The public interface is the macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position for a field in a 32-bit MMIO register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.
- Address-block comments such as `dce_dc_dsc0_dispdec_dscc_dispdec`: generator breadcrumbs that group registers by display hardware block.

Major macro families in this slice:

- `DC_GPIO_RXEN`, `DC_GPIO_PULLUPEN`, `DC_GPIO_AUX_CTRL_3`, `DC_GPIO_AUX_CTRL_4`, `DC_GPIO_AUX_CTRL_5`, and `AUXI2C_PAD_ALL_PWR_OK`: GPIO receiver enables, pull-ups, AUX termination/swap/hysteresis, AUX drive tuning, DDC I2C mode and voltage-domain controls, and AUX/I2C pad power-good bits for PHYs 1 through 6.
- `DCIO_UNIPHY[1-3]_UNIPHY_MACRO_CNTL_RESERVED[0-47]`: repeated full-register reserved fields, each exposing a shift of zero and a 32-bit mask. These preserve symbolic access to reserved UNIPHY macro-control apertures for generated register tables and debug paths.
- `DSC_TOP[0-2]`: DSC clock enable, display-clock gate-disable, DSCCLK gate-disable, debug enable, and test-clock mux fields.
- `DSCCIF[0-2]`: DSC client-interface underflow recovery/status/interrupt, input pixel format, bits per component, double-buffer update pending, picture width, and picture height fields.
- `DSCC[0-2]`: DSC compressor configuration, status, interrupt/status/enable fields, PPS payload fields (`DSCC_PPS_CONFIG0` through `DSCC_PPS_CONFIG22`), memory power control, squared-error and max-absolute-error counters, rate-buffer/fullness counters, and test debug bus rotation.
- `DC_PERFMON17`, `DC_PERFMON18`, `DC_PERFMON19`, and `DC_PERFMON20`: event selection, counted-value selection, increment/run modes, counter active/interrupt state, perfmon report count, count-off interrupt control, high/low counter-value access, and per-counter interrupt status/ack fields.
- `DWB_*` and `FC_*`: display writeback enable/clock controls, memory power controls, frame-capture mode/rate/crop/stereo/current-enable state, window/source geometry, update lock/pending state, CRC controls and values, output format range controls, MMHUBBUB backpressure counters, host-read throttling, overflow status/counters, soft reset, debug select, HDR multiplier, gamut-remap mode, coefficient format, and the first two gamut-remap matrix coefficients.

## Control Flow

This header has no runtime control flow. Runtime sequencing lives in the display driver:

1. DCN 3.0.1 resource and DMUB code include `dcn_3_0_1_offset.h` with this matching `dcn_3_0_1_sh_mask.h`.
2. Resource code builds register and field tables by token-pasting instance IDs into names such as `DSCC2_DSCC_PPS_CONFIG22__RANGE_MAX_QP14_MASK` or `DWB_ENABLE_CLK_CTRL__DWB_ENABLE__SHIFT`.
3. Block code uses those tables through register helpers to program DSC, DWB, GPIO/AUX/DDC, perfmon, and related display hardware.
4. Hardware then observes the programmed fields during modeset, link bring-up, DSC enablement, writeback capture, interrupt handling, debug capture, and suspend/resume restoration.

The macros do not encode ordering. Consumers must still enable clocks before touching gated blocks, program DSC PPS fields before enabling compressed streams, honor double-buffer/update-pending behavior, clear or acknowledge sticky interrupt/status fields correctly, and avoid writes to reserved or read-only hardware fields.

## State And Persistence Behavior

The chunk stores no software state. It describes MMIO-backed GPU state:

- GPIO/AUX/DDC pad state controls receiver enablement, pull-ups, AUX termination and polarity, pad drive/hysteresis, DDC I2C modes, voltage-domain enables, and power-good reporting.
- UNIPHY reserved macro-control fields represent opaque hardware state. The generated masks allow symbolic full-register access but do not document safe values.
- DSC state includes clock/debug gates, input format and dimensions, slice count and dimensions, DSC PPS parameters, rate-control thresholds, QP ranges, memory-power state, underflow/overflow interrupt state, fullness counters, and visual-error counters.
- Perfmon state includes selected events, per-counter states, run/start/stop gates, interrupt status/ack bits, and 48-bit-style high/low counter value exposure.
- DWB state includes capture enable/rate/window/source geometry, CRC mask/value state, output-format limits, overflow state and interrupt policy, soft reset, debug muxing, HDR coefficient, and color-remap matrix state.

Persistence is hardware-defined. Configuration fields generally last until modeset reprogramming, block reset, power gating, suspend/resume, or ASIC reset. Status, counter, interrupt, ack, and update-pending fields may be read-only, sticky, write-one-to-clear, self-clearing, or timing-sensitive. This generated header only provides bit encodings; semantic access rules come from the hardware spec and the consuming AMD display code.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.0.1 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which provides the corresponding register offsets.
- Shared AMD display register helper infrastructure that expands `REG_*`, `SR`, `SRI`, `DSC_SF`, `SF_DWB2`, and related macros into offset plus field-mask operations.
- Adjacent chunks of the same header, because this range starts in the middle of `DC_GPIO_RXEN` and ends inside the DWB color-processing block.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

Important shared consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dsc/dcn20/dcn20_dsc.h` and `.c`, which use `DSC_SF`, `REG_SET`, `REG_UPDATE`, and `REG_GET` field tables for DSC clocking, PPS programming, DSCCIF input configuration, and status.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.h`, `.c`, and `dcn30_dwb_cm.c`, which use DWB field definitions for capture control, CRC, output formatting, gamut remap, and color matrix programming.
- GPIO/DCIO/AUX/DDC handling code in the DCN family, which relies on matching GPIO and pad-control field names when mapping logical pins and AUX/DDC channels to hardware.

## Risks And Edge Cases

- Shift/mask drift is the central risk. These are untyped integer macros, so incorrect masks or positions can compile cleanly while updating the wrong bits in live display hardware.
- The repeated DSC instance families are copy-sensitive. `DSCC0`, `DSCC1`, and `DSCC2` are structurally similar, but an instance-specific typo can break only one pipe or only high-bandwidth modes requiring DSC on that instance.
- `DCIO_UNIPHY*_RESERVED*` full-register masks are risky by nature. The header exposes them as 32-bit fields, but the safe write semantics of reserved registers are not documented here.
- Interrupt/status fields in `DSCC*_DSCC_INTERRUPT_CONTROL_STATUS`, perfmon status/ack registers, and `DWB_OVERFLOW_STATUS` may be sticky or write-one-to-clear. Generic read-modify-write code can accidentally clear or preserve stale status if it does not follow hardware semantics.
- DSC PPS fields are dense and format-sensitive. Bad values or masks for bits-per-pixel, slice geometry, rate-control thresholds, QP ranges, offsets, and native 4:2:0/4:2:2 flags can cause visual corruption, link failures, or modeset-only regressions.
- DWB frame-capture and color-processing fields interact with source timing and buffer readback. Incorrect capture-rate/window/source/gamut-remap masks can produce cropped output, stale frames, wrong color, CRC mismatch, or overflow.
- Power and clock fields for DSC, DWB, and memory blocks are sequencing-sensitive. Writes may be ignored, harmful, or lost if the block is gated, reset, or transitioning power state.
- Chunk boundaries are artificial. The beginning lacks the earlier `DC_GPIO_RXEN` field definitions, and the end stops before the rest of the DWB color-processing matrix fields.

## Test Signals

Useful validation is mostly generated-header consistency plus display hardware behavior:

- Build AMDGPU/DC with DCN 3.0.1 support enabled; missing or renamed macros should fail in `dcn301_resource.c`, `dmub_dcn301.c`, DSC register-table construction, DWB register-table construction, and GPIO/DCIO code paths.
- Mechanically verify every `__SHIFT` field in lines 36969-39480 has a compatible `_MASK` in the same register family, accounting for the intentionally partial `DC_GPIO_RXEN` and final `DWB_GAMUT_REMAPA_C11_C12` boundaries.
- Diff this slice against AMD's authoritative generated DCN 3.0.1 register database and nearby generation targets such as DCN 3.0.0, DCN 3.2.0, and DPCS headers where fields are expected to match.
- Exercise AUX/DDC and GPIO paths: hotplug, EDID reads, DisplayPort AUX DPCD transactions, I2C-over-AUX, pull-up behavior, pad power-good reporting, and suspend/resume.
- Exercise DSC on capable displays across all available DSC instances: high-bandwidth modes, different bits-per-component/pixel formats, native 4:2:0/4:2:2 paths, DSC enable/disable during modeset, and visual integrity under rate-buffer stress.
- Watch DSC interrupt/status and error counters for underflow, overflow, rate-buffer fullness, squared-error, and max-absolute-error anomalies.
- Use perfmon debug workflows to verify selected DC perfmon events count, report, interrupt, acknowledge, and read high/low values correctly.
- Exercise DWB capture paths: enable/disable capture, crop/window/source-size programming, stereo eye selection, CRC generation, output format limits, overflow interrupt handling, color remap, HDR multiplier, and host-read throttling.
- Monitor kernel logs and display diagnostics for AUX timeouts, hotplug storms, link-training failures, DSC corruption, stuck interrupts, DWB overflow, CRC mismatches, blanking, and resume failures.

## Cross-Chunk Notes

Previous chunks own the beginning of the DC GPIO and RX-enable definitions. Later chunks continue the DWB color-processing block after `DWB_GAMUT_REMAPA_C11_C12` and cover the rest of the DCN 3.0.1 field-mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all DCN 3.0.1 GPIO, DSC, perfmon, or DWB fields.
