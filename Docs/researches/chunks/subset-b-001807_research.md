# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_2_sh_mask.h lines 12400-14927

## Purpose

This chunk is a generated AMD DCN 3.1.2 register field map. It defines C preprocessor constants for bit shifts and masks used by the AMDGPU display driver when programming display pipe fetch, cursor, performance monitor, format conversion, scaler, and color-management hardware. The definitions in this slice do not implement executable logic; they are the ABI between higher-level DC display code and MMIO register layouts for this ASIC generation.

The chunk starts in the tail of the pipe-2 HUBPREQ register block and then covers:

- Pipe-2 HUBPRET read/interrupt/power fields.
- Pipe-2 cursor and display metadata fields.
- Pipe-2 DC performance monitor fields.
- Pipe-3 HUBP/HUBPREQ/HUBPRET/cursor/performance monitor fields.
- DPP0 CNVC format converter and cursor conversion fields.
- DPP0 DSCL scaler fields.
- The beginning of DPP0 CM gamma correction and blend-gamma LUT fields.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or callable APIs in this chunk. The important exported surface is the naming convention of macros:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask for the same field.
- `HUBP3_*`, `HUBPREQ3_*`, `HUBPRET3_*`, and `CURSOR0_3_*` identify pipe-3 DC hub pipe fetch, request, return, and cursor registers.
- `HUBPREQ2_*`, `HUBPRET2_*`, and `CURSOR0_2_*` identify the corresponding pipe-2 blocks where this chunk starts.
- `DC_PERFMON9_*` and `DC_PERFMON10_*` expose display performance counter fields for the pipe-2 and pipe-3 perfmon address blocks.
- `CNVC_CFG0_*` and `CNVC_CUR0_*` expose DPP0 format-conversion and cursor-conversion fields.
- `DSCL0_*` exposes DPP0 scaler, line-buffer, output rectangle, and scaler memory-power fields.
- `CM0_CM_GAMCOR_*` and `CM0_CM_BLNDGAM_*` expose color-management gamma correction and blend-gamma controls/LUTs.

These macros are consumed indirectly by generated register-list and field-list macros in display code. For example, DPP definitions use `TF_SF(...)` field entries for `CM0_CM_GAMCOR_CONTROL`, `CNVC_CFG0_PRE_DEGAM`, `DSCL0_SCL_MODE`, and related fields, while HUBP and cursor code uses the pipe-indexed HUBP/HUBPREQ/HUBPRET/CURSOR field names through `REG_SET`, `REG_UPDATE`, `REG_GET`, and similar AMD display register helpers.

## Register Families In This Chunk

### Pipe-2 HUBPREQ/HUBPRET/CURSOR Tail

The chunk begins with the remaining pipe-2 HUBPREQ fields:

- `HUBPREQ2_HUBPREQ_MEM_PWR_STATUS` reports memory-power state for DPTE, MPTE, META, and PDE request buffers.
- `HUBPREQ2_VBLANK_PARAMETERS_5/6` and `HUBPREQ2_FLIP_PARAMETERS_3..6` hold reference-cycle timing for VM and page-table/meta traffic during vblank and flip.

The pipe-2 HUBPRET block then defines:

- `HUBPRET2_HUBPRET_CONTROL` fields for DET buffer plane base, 3-to-2 packing disable, and channel crossbar source selection.
- `HUBPRET2_HUBPRET_MEM_PWR_CTRL/STATUS` fields for DMROB and PIXCDC memory power force/disable/low-power/status.
- `HUBPRET2_HUBPRET_READ_LINE*` and `HUBPRET2_HUBPRET_INTERRUPT` fields for read-line windows, vblank/read-line interrupt mask/type/clear/status, and current/snapshot read-line status.

The pipe-2 cursor block defines:

- Cursor enable, request mode, 2x magnification, mode, TMZ protection, pitch, rotation/mirroring bypass, chunking, and perfmon latency measurement.
- Cursor surface address high/low, size, position, hotspot, stereo offsets, destination offset, cursor memory power status/control, and DMDATA address/control/QoS/status/software-data fields.

### Pipe-2 Performance Monitor

`DC_PERFMON9_*` defines selectable performance-counter controls, low/high values, test/debug controls, counter limits, state control, run/stop selection, interrupt status/ack fields, and 48-bit-ish value composition through low and high/misc registers. These fields let diagnostic code measure display events tied to the pipe-2 HUBP perfmon block.

### Pipe-3 HUBP

`HUBP3_*` starts a full pipe-3 fetch-pipe definition:

- Surface format, rotation, mirroring, alpha plane enable.
- Address/tiling configuration including pipe interleave, compressed fragments, swizzle mode, dimension type, meta-linear, and pipe alignment.
- Primary and secondary luma/chroma viewport start/dimension registers.
- Request sizing for luma and chroma: swath height, linear PTE row height, chunk/min-chunk, meta chunk/min-meta chunk, DPTE group, and VM group.
- Control/status fields for blanking, no-outstanding-request status, soft reset, VTG select, vready timing, stop-data-during-VM behavior, unbounded request mode, segment allocation error, TTU configuration, timeout/underflow status and clear.
- Clock gating and clock-on status for DISPCLK, DPPCLK, and DCFCLK domains.
- VM page size and HUBPREQ debug registers.
- DCFCLK and DPPCLK measurement-window controls for perfmon start/stop events and period selection.

### Pipe-3 HUBPREQ

`HUBPREQ3_*` covers the request side of pipe-3 memory fetch:

- Surface pitch and meta pitch for luma/chroma.
- VMID selection.
- Primary/secondary luma/chroma surface addresses and metadata surface addresses, split into low and high 32-bit register halves.
- Surface control for TMZ, DCC enable, DCC independent-block mode, and metadata TMZ flags.
- Flip control for update locking, flip type, pending status, stereo sync, pending delay, and master update lock status.
- TTU controls for surface 0/1 and cursor 0/1 request delivery timing, fixed QoS level, and QoS ramp disable.
- DCN VM aperture low/high and L1 TLB controls.
- Display logic timing and prefetch fields: blank offsets, `REFCYC_PER_HTOTAL`, after-scaler coordinates, VRATIO prefetch, vblank/flip/nominal PTE/meta timing, line-delivery timing, cursor chunk adjustment, reference-to-pixel frequency ratio, and DRQ limit.
- HUBPREQ memory power control/status for DPTE, MPTE, META, and PDE request memories.

### Pipe-3 HUBPRET, Cursor, And Perfmon

The pipe-3 HUBPRET block mirrors pipe 2, with DET buffer, crossbar, memory power, read-line, vblank/read-line interrupt, and status fields.

`CURSOR0_3_*` mirrors the pipe-2 cursor layout: cursor control, address, size, position, hotspot, stereo control, destination offset, cursor memory power, and DMDATA transport/QoS/status/software data fields.

`DC_PERFMON10_*` mirrors the pipe-2 perfmon definitions for pipe 3.

### DPP0 CNVC And Cursor Conversion

`CNVC_CFG0_*` defines DPP0 format conversion and pre-color processing:

- Surface pixel format and alpha-plane enable.
- Format control for expansion mode, 16-bit conversion, alpha enable, bypass and MSB alignment, positive clamping, update pending, and RGB crossbar mapping.
- Floating-point conversion bias/scale for R/G/B channels.
- Color keyer enable/mode and low/high threshold registers for alpha, red, green, and blue.
- 2-bit alpha LUT entries.
- Pre-dealpha and pre-realpha enable/alpha-blend enable.
- Pre-CSC mode and current mode.
- Pre-CSC matrix coefficients for A and B register banks, packed two 16-bit coefficients per register.
- Pre-degamma mode and LUT select.

`CNVC_CUR0_*` defines converted cursor control and cursor color state for DPP0: enable, expansion, pixel inversion, ROM enable, mode, pixel-alpha modulation, update pending, two 24-bit cursor colors, and floating-point cursor scale/bias.

### DPP0 DSCL

`DSCL0_*` defines DPP0 scaler and line-buffer programming:

- Coefficient RAM tap select/data with tap-pair index, phase, filter type, even/odd coefficient values, and enable bits.
- Scaler mode, coefficient RAM bank select/current/readback, chroma coefficient mode, and alpha coefficient mode.
- Luma/chroma horizontal and vertical tap counts.
- Boundary mode and 2-tap hardcoded coefficient/sharpening controls.
- Manual replicate factors.
- Horizontal/vertical luma and chroma scale ratios plus initial phase integer/fraction values, including bottom-field variants.
- Black color, scaler update pending, autocal mode/pipe identity, overscan, OTG blanking, recout start/size, MPC size, and line-buffer data format.
- Line-buffer memory configuration, partition counts, vertical counters, and scaler/LB memory power force/disable/status fields.
- OBUF memory-power controls appear near the end of the DSCL section.

### DPP0 Color Management

The CM section begins with gamma correction:

- `CM0_CM_GAMCOR_CONTROL`, `CM0_CM_GAMCOR_LUT_INDEX`, `CM0_CM_GAMCOR_LUT_DATA`, and `CM0_CM_GAMCOR_LUT_CONTROL` select gamma-correction mode/bank, LUT address/data, write color mask, read color selection, debug read, host selection, and config mode.
- `CM0_CM_GAMCOR_RAMA_*` and `CM0_CM_GAMCOR_RAMB_*` define double-buffered RAM A/B piecewise-linear region setup for B/G/R: start point, start segment, start slope, start base, end base, end value, end slope, per-channel offset, and packed region definitions.
- Region registers are emitted as pairs, `REGION_0_1` through `REGION_32_33`, with LUT offset and segment-count fields for two regions per register.

The chunk then enters blend gamma:

- `CM0_CM_BLNDGAM_CONTROL`, `CM0_CM_BLNDGAM_LUT_INDEX`, `CM0_CM_BLNDGAM_LUT_DATA`, and `CM0_CM_BLNDGAM_LUT_CONTROL` expose mode/bank, LUT address/data, write color mask, read color select, host select, and config mode.
- It begins the `CM0_CM_BLNDGAM_RAMA_*` region programming block and ends at `CM0_CM_BLNDGAM_RAMA_REGION_18_19`, so the remaining blend-gamma region fields continue in the next chunk.

## Control Flow

This header has no runtime control flow. The effective control flow is in consumers:

1. DC resource construction picks register addresses from matching `dcn_3_1_2_offset.h` entries and field masks/shifts from this header.
2. Display pipe programming computes field values from mode timing, surface layout, cursor state, scaling parameters, color pipeline state, and memory/QoS requirements.
3. Register helper macros combine these `_SHIFT` and `_MASK` constants to read, write, or update packed fields.
4. Hardware state changes through MMIO writes and later exposes status bits through the corresponding status macros.

For double-buffered color LUTs and scaler coefficient RAM, the driver writes index/control/data fields and selects the active bank. Current-mode/current-select and update-pending fields are the observable completion handshakes.

## State And Persistence Behavior

The state described by these macros is hardware register state, not software-owned persistent storage. It persists in the display engine until changed by another driver write, reset, power-gating transition, suspend/resume reprogramming, or hardware status update.

Important state categories:

- Surface state: addresses, metadata addresses, pitch, tiling, viewport, DCC, TMZ, VMID, and flip/update-lock state.
- Timing/QoS state: TTU delivery, prefetch, vblank/flip/nominal PTE/meta timing, line-delivery, DRQ limit, and reference-to-pixel-frequency conversion.
- Cursor state: image address, size, position, hotspot, mode, DMDATA, and memory-power state.
- Diagnostic state: perfmon counter values, limits, run/stop selection, and interrupt ack/status bits.
- Color/scaler state: scaler coefficients/ratios, CNVC/pre-CSC/pre-degamma settings, gamma/blend-gamma LUT content, active RAM bank, and update-pending/current fields.
- Power state: HUBPREQ/HUBPRET/cursor/DSCL memory force/disable/status fields and clock-gating controls.

Status, pending, done, underflow, timeout, and interrupt fields can be hardware-mutated. Clear/ack fields are write-side controls and must be handled as write-one style side effects according to the register spec.

## Dependencies

This chunk depends on the AMDGPU display register programming framework:

- Matching address macros in `dcn_3_1_2_offset.h`; masks and shifts are only useful when paired with the correct MMIO address.
- Register helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WRITE`, and generated `*_SF`/`*_SRI` list macros used throughout `drivers/gpu/drm/amd/display`.
- DPP register/field list definitions in files such as `display/dc/dpp/dcn30/dcn30_dpp.h`, which reference many `CM0`, `CNVC_CFG0`, `CNVC_CUR0`, and `DSCL0` fields from this chunk.
- HUBP, IRQ, DMUB, and HW sequencing code that consumes pipe-indexed HUBP/HUBPREQ/HUBPRET/CURSOR and perfmon fields.
- Hardware-generated register specifications for DCN 3.1.2; the source is not hand-authored business logic.

## Integration Points

- HUBP/HUBPREQ/HUBPRET fields integrate with plane address programming, page-table/DCC metadata fetch, flip scheduling, VM/TLB setup, underflow handling, clock/power gating, and display diagnostics.
- Cursor fields integrate with DRM cursor plane updates, protected content/TMZ, cursor DMDATA transport, cursor memory power management, and cursor color conversion.
- Perfmon fields integrate with display debug/performance tooling and counter-based interrupt/status handling.
- CNVC fields integrate with input pixel format conversion, pre-CSC, pre-degamma, alpha handling, color keying, and DMUB-assisted cursor state capture.
- DSCL fields integrate with scaling setup, scaler coefficient downloads, line-buffer partitioning, overscan/recout/MPC sizing, and scaler memory power.
- CM fields integrate with color management APIs that program gamma correction, blend gamma, shaper/gamut paths, and LUT bank switching.

## Risks And Edge Cases

- Mask/shift drift from the ASIC specification is high impact: a one-bit error can silently program the wrong hardware field, corrupt display output, break flips, or disable memory blocks.
- Pipe-indexed duplication is easy to misuse. A pipe-3 field name must be paired with pipe-3 addresses; mixing pipe 2/3 address and mask sets can program the wrong display pipe.
- Low/high address halves require correct ordering and synchronization with update locks. Partial address updates can point the display engine at invalid memory.
- Protected content/TMZ bits appear on surfaces, metadata, cursors, and DMDATA. Incorrect settings can break protected playback or violate memory-access expectations.
- Clear/ack/status fields share packed registers with mask/type bits in interrupt and perfmon controls. Read-modify-write helpers must avoid acknowledging interrupts or clearing error states unintentionally.
- Double-buffered LUT and coefficient RAM fields require correct bank selection and update sequencing. Writing the inactive bank without switching, or switching before upload completion, produces wrong color/scaler output.
- Hardware-mutated fields such as `*_CURRENT`, `*_UPDATE_PENDING`, `*_DONE`, `*_UNDERFLOW`, timeout, and memory-power status cannot be treated as ordinary cached software state.
- This chunk ends mid-family in the blend-gamma RAMA region list; any analysis or generated tables for `CM0_CM_BLNDGAM_RAMA_*` must include the next chunk before concluding the full register family.

## Test Signals

Useful validation signals for changes touching this header or its consumers:

- Compile coverage for AMDGPU display with DCN 3.1.2 enabled; generated field names must still satisfy all `TF_SF`, `SRI`, and register-helper references.
- Boot/runtime smoke on DCN 3.1.2 hardware or emulator: modeset, page flip, plane enable/disable, cursor movement, cursor format changes, suspend/resume, and hotplug.
- Display correctness under scaling: identity, upscaling, downscaling, chroma formats, interlaced/bottom-field initialization if supported, overscan, and MPC sizing.
- Color pipeline checks: pre-degamma, pre-CSC, gamma correction, blend gamma, LUT bank switching, and current/update-pending handshakes.
- Memory/QoS stress: DCC surfaces, metadata fetch, VM/TLB enabled surfaces, vblank and flip prefetch timing, underflow/timeout status, and recovery clear paths.
- Protected-content tests where TMZ cursor/surface/metadata/DMDATA bits are expected.
- Perfmon tests that program counter selection/limits, read low/high values, and verify interrupt status/ack behavior without disturbing unrelated fields.
