# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 22732-25252

## Purpose

This chunk is a generated AMD DCN 4.2.0 register shift/mask slice. It contains no executable C; its exported interface is a large set of preprocessor constants that describe bit positions and masks for fields inside DCN display hardware registers. The covered range starts in the middle of the `HUBPREQ3` surface-address block, crosses several display-pipe sub-blocks for hub request/return, cursor, performance monitor, DPP top, converter/color, scaler/sharpener, and CM0 color management, and ends at the start of `DC_PERFMON10_PERFCOUNTER_CNTL2`.

The range contains 2,113 `#define` lines: 1,058 `__SHIFT` constants and 1,055 `_MASK` constants. It is a chunk boundary, not a semantic boundary: the first register has its shift in the previous chunk, and the `DC_PERFMON10` block continues in the next chunk. Although the repository path includes `ceph-client`, this file is AMDGPU display hardware metadata, not distributed filesystem code.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, or direct MMIO operations here. The important API is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives a field's bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the register word.
- Paired offset headers, especially `dcn_4_2_0_offset.h`, provide the matching register addresses.

The field macros are consumed through AMD display register helpers and token-pasting tables such as `FD_MASK`, `FD_SHIFT`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and DPP `TF_SF`/`TF2_SF` field lists. For DCN42 specifically, `display/dmub/src/dmub_dcn42.c` includes both `dcn/dcn_4_2_0_offset.h` and this header, then initializes DMUB register masks and shifts with `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`. DPP code follows the same pattern; `display/dc/dpp/dcn401/dcn401_dpp.h` references many of this chunk's `CM0`, `CNVC_CFG0`, and `DSCL0` fields in transfer-function/scaler register tables.

## Register Families In This Chunk

Major register groups covered by the range are:

- `HUBPREQ3_*`: pipe 3 hub request fields for surface and metadata addresses, TMZ/DCC control, flip control, flip interrupts, in-use/earliest-in-use addresses with VMID, request expansion, TTU QoS watermarks, VM aperture/TLB control, blank and destination dimensions, prefetch/vblank/flip/nominal delivery timing, cursor timing, memory power control/status, UCLK p-state forcing, and status registers.
- `HUBPRET3_*`: hub return control fields for DET buffer addressing, channel crossbar selection, memory power control/status, read-line window configuration, vblank/read-line interrupts, read-line snapshots, and read-line status.
- `CURSOR0_3_*`: cursor plane 3 fields for enable/mode/TMZ/pitch, address, size, position, hot spot, stereo offsets, destination offset, cursor memory power, display metadata address/control/status/software data, and HUBP 3D LUT address/control/timing.
- `DC_PERFMON9_*` and partial `DC_PERFMON10_*`: display performance monitor counter selection, counted-value selection, increment/run/interrupt modes, per-counter state, perfmon global state, count-off interrupt controls, counter interrupt status/ack, and high/low counter values.
- `DPP_TOP0_*`: DPP top-level control, soft reset, CRC value/control, and host-read control.
- `CNVC_CFG0_*`: conversion/configuration fields for surface pixel format, format control, floating-point bias/scale, color keying, alpha LUTs, pre-dealpha, pre-degamma, pre-realpha, pre-CSC mode and matrix coefficients, and coefficient formats.
- `CM_CUR0_*`: cursor color-management fields for cursor color values, FP scale/bias, matrix mode, and two cursor matrix banks.
- `DSCL0_*`: scaler and image-sharpening fields for coefficient RAM, scaler mode/taps/ratios/init values, overscan, OTG blanking, recout/MPC sizes, line-buffer data/memory, scaler/OBUF memory power, EASF horizontal/vertical filtering, super-conversion matrices, ringing-estimation gains/reductions, BF/PWL tables, `ISHARP` control/delta/noise/LBA tables, and delta LUT memory power.
- `CM0_*`: color-management fields for bypass and post-CSC, bias, gamma-correction control/LUT, RAMA/RAMB gamma-correction region programming for regions 0-33, HDR multiplier, gamma/histogram memory power/status, dealpha, coefficient formats, debug index/data, histogram selection/scales/biases, histogram lock/index/data/status, and histogram-ready interrupt control.

## Control Flow And Hardware Behavior

This header does not implement control flow. Runtime control flow is created when DCN42 driver, DMUB, IRQ, DPP, cursor, scaler, and color-management code uses these constants to compose register reads and writes.

The fields describe several hardware sequencing surfaces:

- Surface programming and flip sequencing use `HUBPREQ3_DCSURF_*` address/control fields, `SURFACE_UPDATE_LOCK`, pending/away interrupt bits, stereo flip selection, GSL, triple buffering, in-use address readbacks, and VMID fields.
- Hub request timing uses TTU, QoS, prefetch, vblank, flip, nominal delivery, per-line delivery, cursor settings, and p-state fields to keep memory request scheduling aligned with display scanout.
- Hub return and cursor blocks expose vblank/read-line interrupt status/clear/mask fields, cursor address/TMZ/mode state, metadata transfer status, and 3D LUT completion.
- DPP/CNVC/CM/DSCL fields encode the per-pixel processing pipeline: source format conversion, pre-CSC, cursor color transforms, scaling/filtering, sharpening, post-CSC, gamma correction, HDR multiplication, histogram collection, and optional bypass/dealpha behavior.
- Performance monitor fields configure event selection, run/stop conditions, counter active state, counter interrupts, and counter high/low values for display performance diagnostics.

Consumers normally perform read-modify-write operations: fetch a register, clear a field with the `_MASK`, shift the new value by `__SHIFT`, write the updated word, or extract status by applying the mask and shifting back. Interrupt and status paths poll or acknowledge bits using the same definitions, but the header does not encode which fields are read-only, sticky, write-one-to-clear, or self-clearing.

## State And Persistence Behavior

The header itself has no runtime state and persists nothing. It is a compile-time hardware ABI description.

The represented hardware registers are live display state. Configuration fields such as surface addresses, DCC/TMZ enables, QoS levels, VM/TLB controls, scaler ratios, CSC coefficients, LUT region tables, color-key settings, gamma-correction regions, memory-power force/disable bits, and perfmon counter selections typically persist until reprogrammed by modeset, plane update, cursor update, color-management update, power-management code, DMUB firmware, suspend/resume, or GPU reset.

Status and handshake fields are more transient. Examples include flip pending/occurred/status bits, in-use/earliest-in-use address readbacks, read-line/vblank status, cursor metadata done/underflow, 3D LUT done, perfmon active/counter interrupt status, current CSC/gamma mode readbacks, memory-power state bits, histogram ready/in-use/skipped/overflow/incomplete state, and scaler update-pending state. Clear or ack fields, such as flip interrupt clears, hub return interrupt clears, metadata underflow clear, perf counter interrupt acks, and histogram-ready interrupt control, are side-effect-sensitive and must be used with the hardware programming model.

## Dependencies And Integration Points

This chunk depends on the AMD generated register ecosystem staying synchronized:

- `dcn_4_2_0_offset.h` supplies the address/base-index side for these fields.
- DCN42 code includes the header from `dmub_dcn42.c`, `dcn42_clk_mgr.c`, `hw_factory_dcn42.c`, `hw_translate_dcn42.c`, `irq_service_dcn42.c`, and `dcn42_resource.c`.
- DPP and color-management code integrates many `CM0`, `CNVC_CFG0`, and `DSCL0` fields through transfer-function and scaler register lists.
- Cursor, hubp/hubpret, IRQ, DMUB, and perf diagnostics code can consume the corresponding generated names through the same register-helper macros.

Functional integration points include atomic plane flips, display scanout memory requests, cursor updates, display metadata transfer, vblank/read-line interrupts, DPP reset/CRC/debug, format conversion, color keying, pre/post color-space conversion, scaling, sharpening, gamma correction, histogram collection, memory power gating, and display performance monitoring.

## Risks And Edge Cases

- Generated-header drift is the central risk. A wrong mask or shift can compile successfully while programming the wrong hardware bits.
- The chunk is partial at both ends. The initial `HUBPREQ3_DCSURF_SECONDARY_SURFACE_ADDRESS` register is missing its shift in this range, and `DC_PERFMON10_PERFCOUNTER_CNTL2` continues in the following chunk.
- Many fields are side-effect-sensitive. Confusing interrupt status, clear, mask, and type bits can drop flip/vblank/read-line/perf/histogram events or create interrupt storms.
- Surface address, VMID, TMZ, DCC, VM aperture, TLB, and p-state fields affect memory access and protected-surface behavior; bad masks can cause scanout faults, blanking, stale frames, or security-sensitive address/protection mistakes.
- Timing fields for TTU, prefetch, vblank, flip, per-line delivery, scaler init, and QoS are workload- and mode-dependent. Incorrect values can appear only under high-resolution, high-refresh, multi-plane, cursor, or bandwidth-stress modes.
- Color/scaler/gamma fields are numerically dense. Off-by-one masks in CSC coefficients, LUT indices/data, RAMA/RAMB region tables, EASF/ISHARP PWL tables, or histogram coefficients can produce subtle image-quality defects rather than obvious failures.
- Memory power force/disable/state fields span HUBPREQ, HUBPRET, cursor, DSCL/OBUF, CM gamma, and histogram memories. Incorrect sequencing around power-gated blocks can produce stale status reads or lost writes.
- Perfmon registers use repeated counter fields and high/low value pairs. Incorrect counter select, ack, or active-state masks can make diagnostics misleading without affecting normal display output.

## Test Signals

Useful validation signals for this chunk include:

- Build DCN42 AMDGPU display code that includes `dcn_4_2_0_sh_mask.h`, especially DMUB, IRQ, GPIO, clock-manager, and resource paths.
- Static generated-header checks that every `__SHIFT` has a matching `_MASK`, masks are aligned with shifts, and every register in this chunk has a matching offset/base-index entry in `dcn_4_2_0_offset.h`.
- Modeset and atomic plane-flip tests covering primary and secondary surfaces, DCC, TMZ, stereoscopic/flip pending paths, GSL/triple buffering, and multi-plane scanout.
- Bandwidth and timing stress tests across high refresh, high resolution, cursor movement, vblank/read-line interrupts, FCLK/UCLK p-state changes, and suspend/resume.
- Cursor tests covering address, size, hot spot, stereo offset, metadata transfer, underflow clear, memory power, and HUBP 3D LUT completion.
- Color pipeline tests for CNVC format conversion, color keying, pre/post CSC, cursor matrix/color transforms, gamma correction RAMA/RAMB programming, HDR multiplier, histogram collection/readback, and dealpha behavior.
- Scaler and sharpening tests covering coefficient RAM programming, tap counts, ratios/init values, overscan, line-buffer partitioning, EASF, ISHARP, PWL table writes, and scaler update-pending state.
- Perfmon diagnostics that program `DC_PERFMON9` and adjacent `DC_PERFMON10` counters, verify active/state transitions, read high/low values, and acknowledge only intended counter interrupts.

## Cross-Chunk Notes

The preceding chunk is needed to complete the first `HUBPREQ3_DCSURF_SECONDARY_SURFACE_ADDRESS` shift/mask pair and earlier HUBPREQ3 setup. The following chunk is needed for the rest of `DC_PERFMON10` and any later DPP performance-monitor definitions. Final per-file analysis should reconcile these boundaries before drawing conclusions about missing fields or complete register families.
