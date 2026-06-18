# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h lines 7651-15208

## Scope

This chunk is a middle slice of the Vega10 AMD GPU register-value header. It contains generated-style `typedef enum` declarations and a few `#define` constants for hardware register fields, not executable logic. The range starts inside the Azalia F0 codec input-pin capability declarations and then covers complete display, audio, clocking, color, cache, shader-input, and shader-queue enum sections through the beginning of the `SQDEC` value block.

## Purpose

The declarations in this slice provide symbolic names for raw numeric values that must be written to, or decoded from, Vega10 display/audio/GFX registers. They are used as ABI-like constants between the driver and GPU hardware blocks. Their purpose is readability and correctness for register programming paths: instead of using unexplained integers for DisplayPort training, AUX timing, DSI mode selection, Azalia audio stream setup, display clock routing, color-management mode selection, color buffer compression/perf events, texture-cache operations, SPI performance counters, and SQ debug/performance controls, driver code can use named constants tied to the hardware spec.

## Major Blocks And Types

- `AZALIA_F0_CODEC_INPUT_PIN_PARAMETER_CAPABILITIES_*` and `AZALIA_F0_CODEC_INPUT_PIN_CONTROL_RESPONSE_HBR_HBR_CAPABLE` continue the previous Azalia F0 codec section with HDMI, balanced I/O, input/output, headphone drive, jack detection, trigger, impedance-sense, and HBR capability values.
- `UNP_*` enums describe underlay graphics enablement, depth, tiling, bank geometry, address translation, color expansion, video format, endian swap, RGB crossbar selection, update-lock behavior, stereosync/interlace flip handling, CRC source/line selection, rotation, pixel drop, and buffer mode.
- `DP_*` and `DPHY_*` enums cover DisplayPort link/video programming: link-training completion, embedded panel mode, pixel encoding, dynamic range, YCbCr range, component depth, MSA overrides, lane count, stream disable/overflow interrupts, scrambler/8b10b/PRBS/CRC controls, fast training, secondary packets, MST encoder controls, HBR2 pattern modes, and GSP send/priority controls.
- `COL_MAN_*` enums model display color-management pipeline choices: update locks, input CSC mode/type/rounding, prescale, input gamma, output CSC, denorm clamp, regamma, global passthrough, degamma, and gamut-remap modes.
- `DP_AUX_*` enums define AUX-channel ownership, software transaction triggers, arbitration priority, interrupt acknowledgements, PHY TX/RX timing windows, detection thresholds, GTC sync windows/attempts, error acknowledgement, and reset state values.
- `DSI_*` enums configure MIPI DSI command/video modes: source and destination formats, flag clear, bit swapping, clock gating, ULPS entry/exit, lane enables, display/DSI/byte/escape clock resets, CRTC selection, packet byte order, video traffic/power/pulse modes, RGB swap, command packet type/order, data buffer selection, FIFO watermarks, command triggers, TE source/mux/mode/polarity, reset panel, CRC, EOT behavior, BIST, and debug clock selection.
- `DCIOCHIP_*`, `DCIO_*`, `DCO_*`, `DOUT_I2C_*`, `DPCSRX_*`, and `DPCSTX_*` enums describe display I/O pads, HPD selection, GPIO mask/drive/invert modes, AUX electrical trim values, generic signal routing, UNIPHY ref/fb divider debug selections, pad external signal muxing, DVO/LVTMA/backlight PWM controls, genlock/swaplock/global-sync routing, GPU timer position/read selection, soft resets, DPHY lane selection, DPCS interrupt behavior, debug async block selection, DisplayPort clock receiver/transmitter symbol-clock selection, and DDC/I2C controller arbitration/transaction controls.
- `GENERIC_AZ_*`, `AZ_*`, `STREAM_*`, `CORB_*`, `RIRB_*`, `IMMEDIATE_COMMAND_STATUS_*`, and `DMA_POSITION_*` enums cover the Azalia controller: generic register enable/status bits, 64-bit address capability, unsolicited response enable, flush/reset/status, codec-present state, per-stream stopped flags, CORB/RIRB reset and size selection, immediate command status, and DMA position-buffer enablement.
- `AZALIA_F2_CODEC_*`, `CC_RCU_DC_AUDIO_*`, `AOUT_*`, `I2S_*`, and `SPDIF_*` enums cover display audio endpoints and output: PCM/not-PCM stream type, sample rate/multiple/divisor, bits per sample, channel count, digital converter status/control bits, output/input pin enable and unsolicited response, downmix/multichannel mute/mode, codec reset, port connectivity, audio output FIFO/CRC, I2S word/alignment/bit-order/LRCLK settings, and SPDIF inversion.
- `DCCG_*`, `DCI_*`, `Lpt*`, `ENABLE`, `ENABLE_CLOCK`, `REFCLK_*`, `PIPE_*`, `CRTC_*`, and related clock enums define display clock gating, deep color, reference clock source selection, microsecond/millisecond timebase source, pixel-rate source and PLL routing, DP DTO controls, pixel add/drop, symbol clock forcing, DVO clock skew/in-phase controls, MVP source, audio DTO selection, DCCG debug/perf modes, clock-branch and PLL soft resets, low-power tiling pipe/bank values, and DCEF clock gating overrides.
- `CB*`, `SurfaceNumber`, `SurfaceSwap`, `BlendOp`, `CombFunc`, `BlendOpt`, `Cmask*`, and `MemArbMode` enums provide color-buffer render target state values: surface numeric format and swizzle, render mode including resolve/decompress/DCC decompress, rounding/source export format, blend factors and combine functions, blend optimization overrides, CMASK encodings, CMASK addressing, memory arbitration, and color-buffer performance-counter selectors/filters.
- `TC_OP_MASKS`, `TC_OP`, `TC_NACKS`, and `TC_EA_CID` enumerate texture-cache/global-memory operations and diagnostics: read/write, 32-bit and 64-bit atomics with and without return, denorm-flush variants, L1/L2 writeback/invalidate operations, metadata invalidation, NOP/ack operations, fault NACK categories, and EA client IDs for render targets, FMASK, DCC, depth/stencil, TCP/SQC, CPF/CPG/IA/WD/PA, and UTCL2/TPI.
- `SPI_*` enums describe shader processor input behavior and performance counters: sample interpolation selection, fog mode, point-sprite overrides, a long `SPI_PERFCNT_SEL` range for VS/GS/ES/HS/LS/CS/PS allocation, stalls, resource fullness, clock-gating, export counts, and shader export formats.
- `SQ_*`, `SH_MEM_*`, and `ENUM_SQ_EXPORT_RAT_INST` enums define shader queue/resource state: texture clamp/filter/aniso/depth-compare/border-color settings, buffer/image/flat resource types, image filter mode, XYZW/0/1 component selection, wave types, thread-trace token/misc/instruction/register/issue/capture fields, SQ performance selectors including SQC cache/TLB/replay counters, CAC power selectors, indirect command op/mode, EDC info source, floating-point round mode, interrupt word encoding, RAT export store/atomic instructions, instruction-buffer states, instruction-stream states, wave IB ECC states, and shader memory address/alignment modes.
- The final `#define` values in this chunk expose `SQ_WAVE_TYPE_PS0`, SQ indirect register partition offsets/sizes, and SQ GFX decoder address range/shift constants.

## APIs, Functions, And Control Flow

There are no functions, callbacks, structs, or runtime control-flow constructs in this chunk. The C API surface is a collection of globally visible enum typedef names and preprocessor constants. Control flow exists only in consumers that include this header and select these values while programming registers or decoding register values.

Because each enum maps exact integer encodings to symbolic names, consumers should treat these as hardware contract constants rather than ordinary software enums whose values can be reordered. Many enums are binary field values, while dense tables such as `CBPerfSel`, `TC_OP`, `SPI_PERFCNT_SEL`, and `SQ_PERF_SEL` define large numeric selector spaces with reserved gaps and hardware-specific ordering.

## State And Persistence

The header itself has no mutable state and performs no persistence. State changes occur when other driver paths write these values into MMIO registers, packetized command streams, saved context state, debug registers, perf-counter selectors, or audio/display control registers. Once programmed into hardware, the values can persist in GPU block registers until reset, mode-set reprogramming, context switch, power transition, or explicit driver update.

Several enum groups represent fields that are stateful in hardware:

- Update-lock and double-buffer-like controls for UNP and color management affect when display surface/color changes become visible.
- DP/DPHY/AUX/DSI reset, training, stream-disable, overflow, CRC, BIST, and interrupt acknowledgement values control hardware sequences with timing-sensitive side effects.
- Azalia CORB/RIRB, stream synchronization, flush, controller reset, immediate command, DMA-position, and pin/converter controls influence audio DMA and codec command state.
- DCCG/DCIO clock, soft-reset, PWM, genlock, swaplock, and timer selections affect display timing and power state.
- CB/TC/SPI/SQ perf-counter selector values control what hardware events are counted, sampled, or traced.
- SQ indirect partition and GFX decoder constants define memory/register layouts used by debug and wave-state inspection code.

## Dependencies And Integration Points

This file is a low-level include consumed by AMDGPU/DRM code that needs Vega10 register encodings. It depends only on the C compiler's enum and macro handling, but semantically it depends on the Vega10 hardware register specification and companion register headers that define field masks, shifts, and register addresses. Typical integration points are:

- Display Core or legacy display programming paths for DP, DSI, AUX, DCIO, DCCG, UNP, color-management, backlight PWM, HPD, I2C/DDC, and clock/reset fields.
- HDMI/DisplayPort audio setup paths for Azalia controller/endpoint, AOUT, I2S, SPDIF, and port connectivity fields.
- Graphics command setup and render backend programming for CB surface/blend/compression mode values.
- Cache/memory operation and fault-diagnostic paths for `TC_OP`, NACK, and EA client IDs.
- Performance monitoring, thread tracing, debug, and profiling infrastructure for CB/SPI/SQ selector enums, trace token types, indirect SQ command modes, SQ register partitions, and decoder address constants.
- Generated register access helpers or manually written register-update macros that combine enum constants with field shifts/masks from adjacent Vega10 headers.

## Risks And Edge Cases

- Numeric drift is the primary risk. Changing an enum value, removing a reserved entry, or reordering declarations can silently program the wrong hardware behavior while still compiling.
- Some names contain apparent typos inherited from the hardware/spec source, such as `STEAM_NOT_STOPPED`, `RESETET`, `ATTAMPS`, `DISBALE`, and `COL_MAN_MULTIPLE_UPDAT_EDISABLE`. These should not be "fixed" casually because downstream code may reference the exact symbols.
- Enum names are globally visible C identifiers. Short generic names in this slice, including `ENABLE`, `ENABLE_CLOCK`, `RoundMode`, `BlendOp`, and `SourceFormat`, can collide with other headers if include ordering or namespace assumptions change.
- Several enums contain reserved values that are still named. Drivers should avoid programming reserved encodings unless matching existing hardware sequences require them.
- Large selector enums such as `CBPerfSel`, `SPI_PERFCNT_SEL`, and `SQ_PERF_SEL` are especially vulnerable to incomplete updates when porting from another ASIC generation; counters may appear to work while measuring a different event.
- Write-one-to-clear or acknowledgement-like values, for example DP overflow/interrupt ACK and AUX error ACK fields, are side-effectful when written by consumers. Treating them as passive status values can clear interrupts unexpectedly.
- Clock, PHY, reset, and training fields are timing-sensitive. Incorrect combinations in DCCG, DCIO, DP AUX/DPHY, DSI, or DOUT I2C paths can cause link-training failures, blank display, DDC/EDID failures, audio loss, or hangs in polling loops.
- This chunk begins and ends mid-file. The preceding chunk owns earlier Azalia F0 context, and the following chunk begins after the `SQDEC value` marker with additional graphics front-end enum sections. Whole-file research needs both boundaries reconciled.

## Test Signals

Useful validation signals for consumers of this chunk are compile-time and hardware-behavior oriented:

- Build coverage for all AMDGPU/DRM objects that include `vega10_enum.h`; this catches missing or renamed symbols but not wrong numeric encodings.
- Static comparison against the generated source or hardware XML/register database, especially for dense selector enums and reserved-value positions.
- Display smoke tests across DP/eDP/DSI paths: link training, stream enable/disable, MST sideband operation, AUX/DDC EDID reads, HPD handling, deep color/YCbCr modes, color-management programming, backlight PWM, and suspend/resume.
- Audio-over-display tests for Azalia stream setup, codec reset, channel counts, sample rates, pin enable, silent keepalive, and unsolicited responses.
- Perf-counter and tracing tests that select representative CB, SPI, SQ, and SQC events and verify counters move under known workloads.
- GPU debug tests for SQ indirect register partition reads, wave-state decoding, thread-trace token parsing, EDC source reporting, and RAT export instruction decoding.
- Cache/memory operation tests for TC writeback/invalidate and atomic encodings where those values are used in command packets or diagnostics.

## Chunk Notes For Merge Lane

This chunk should be merged with neighboring chunks as one source-file report for `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/vega10_enum.h`. It is intentionally chunk-scoped and does not create the final source-tree-aligned per-file document. The most important cross-chunk boundary is that this range starts inside Azalia F0 codec pin capability declarations and ends immediately after SQ indirect/GFX decoder constants at the `SQDEC value` marker.
