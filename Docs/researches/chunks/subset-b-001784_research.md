# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_3_sh_mask.h lines 7369-9903

## Purpose

This chunk is generated C preprocessor metadata for DCN 3.0.3 display-register bitfields. It contains `_SHIFT` and `_MASK` definitions used by AMDGPU DC display code to pack, unpack, and update MMIO register fields without hard-coding bit positions at call sites. The covered range starts at the tail of `HUBP0_HUBP_MEASURE_WIN_CTRL_DPPCLK` masks, then covers HUBP/HUBPREQ/HUBPRET/CURSOR/perfmon definitions for display pipe 0 and pipe 1, and finally begins the DPP0 top, converter, scaler, and color-management register field map.

There are no functions, structs, or runtime algorithms in this slice. Its behavioral importance is indirect: every macro value becomes part of the hardware programming ABI between the DRM display driver and DCN 3.0.3 display blocks.

## Important APIs, Types, And Register Groups

- `HUBPREQ0_*` and `HUBPREQ1_*` describe hubp request-side surface programming. They include pitch, VMID, primary/secondary luma and chroma surface addresses, primary/secondary metadata addresses, TMZ and DCC surface-control bits, flip controls, flip interrupts, in-use/earliest-in-use address snapshots, request expansion modes, TTU/QoS timing, VM aperture and L1 TLB control, blank/prefetch/vblank/flip/nominal delivery timing, cursor delivery timing, and request memory power control/status.
- `HUBPRET0_*` and `HUBPRET1_*` describe hubp return-side programming. They cover DET buffer base/crossbar controls, DET/DMROB/PIXCDC memory power control and state, pipe read-line windows, vblank/read-line interrupts, read-line values, and read-line status flags.
- `CURSOR0_0_*` and `CURSOR0_1_*` define hardware cursor fetch and metadata fields for pipes 0 and 1. They include enable/mode/magnification/TMZ/snoop/system/pitch settings, cursor address low/high, size, position, hot spot, stereo offsets, destination offset, cursor memory power control/status, DMDATA address/control/QoS/status, and software DMDATA payload registers.
- `DC_PERFMON5_*` and `DC_PERFMON6_*` define per-pipe display performance monitor controls. They expose event selection, counted value selection, increment modes, hardware stop selection, counter state multiplexing for counters 0-7, perfmon state, report count, count-off interrupt control, clock enable, run-enable start/stop selectors, counter interrupt status/ack fields, and high/low readback fields.
- `HUBP1_*` at the pipe-1 hubp block mirrors earlier pipe-0 hubp definitions from outside this chunk for surface config, address/tiling config, primary/secondary viewport geometry, request sizing, hubp control/status, hubp clocks, VMPG config, and DCFCLK/DPPCLK measurement windows.
- `DPP_TOP0_*` starts the DPP0 display pipe processor top block, covering DPP clock/gating, soft resets for CNVC/DSCL/CM/OBUF, CRC readback/control, and host-read throttling.
- `CNVC_CFG0_*` defines the DPP0 converter configuration: surface pixel format, format expansion/conversion/alpha/bypass/crossbar controls, FP bias/scale values, color-key controls and RGBA thresholds, 2-bit alpha LUT, pre-dealpha, pre-CSC mode and coefficient pairs including B-bank coefficients, coefficient format, pre-degamma, and pre-realpha.
- `CNVC_CUR0_*` defines converter-side cursor controls, cursor palette colors, and cursor FP scale/bias.
- `DSCL0_*` defines scaler state: coefficient RAM selection/data, scaler modes, tap counts, 2-tap sharpening, manual replicate factors, horizontal/vertical scale ratios and initial phases for luma/chroma/top/bottom, black color, update pending, autocal, overscan, OTG blanking, recout/MPC sizing, line-buffer format and partitioning, scaler/line-buffer memory power state, and OBUF control/power.
- `CM0_*` begins DPP0 color management: CM bypass/update pending, post-CSC mode and coefficient matrices with B-bank values, gamut remap mode and coefficient matrices with B-bank values, output bias, gamma-correction controls, LUT index/data/control, and RAMA piecewise-linear gamma region setup.

All macros use the naming pattern `<register>__<field>__SHIFT` and `<register>__<field>_MASK`. They are consumed as constants by register helper macros in the AMD display stack, typically alongside register-address headers and generated register-list tables.

## Control Flow

The chunk has no C control flow. The effective control flow appears in callers that:

1. Choose a register for a DCN block instance, such as `HUBPREQ1_DCSURF_FLIP_CONTROL`.
2. Use the matching `_SHIFT` and `_MASK` definitions to construct field values.
3. Issue MMIO read/modify/write operations through AMDGPU/DC register helper macros.
4. Poll or inspect status fields such as flip pending, DMDATA done, memory power state, read-line status, underflow/timeout status, or perfmon interrupt status.

The field families imply several important programming sequences: surface update locks before address/format flips; programming VMID, surface addresses, pitches, metadata, DCC/TMZ, and timing before enabling fetch; clearing flip/read-line/vblank/DMDATA interrupt bits after handling; enabling DPP/CNVC/DSCL/CM clocks and releasing soft reset before DPP programming; and selecting scaler/gamma LUT indices before writing associated data.

## State And Persistence Behavior

The macros themselves are compile-time constants and have no persistence. The hardware registers they describe are persistent device state until changed by driver writes, reset, suspend/resume, display mode changes, or power gating.

Stateful hardware surfaces visible in this range include framebuffer base addresses and VMID selection, DCC/TMZ/security bits, flip pending/occurred/away status, read-line/vblank interrupt state, DMDATA done/underflow/fault/late state, memory power control and status for request buffers, DET/DMROB/PIXCDC/CROB/scaler/LUT/line-buffer/OBUF memories, perfmon counter state/readback values, DPP CRC values, scaler coefficient RAM, line-buffer partitioning, CM post-CSC/gamut/gamma LUT state, and RAMA gamma-region tables.

Several fields are status-or-ack style rather than ordinary configuration. Examples include `*_CLEAR`, `*_STATUS`, `*_INT_STATUS`, `*_ACK`, `*_UPDATE_PENDING`, `*_DONE`, and `*_CURRENT` fields. Callers must preserve the expected write-one-to-clear or read-only semantics from the hardware spec; the masks alone do not encode those access rules.

## Dependencies And Integration Points

This header depends on the wider generated ASIC register set for DCN 3.0.3. It is meaningful only with the corresponding address-definition headers, DC register-list structures, and helper macros that combine shifts/masks with MMIO access. Integration points are the AMDGPU DRM display manager and DCN resource/HUBP/DPP/HUBBUB programming code under the AMD display driver.

The pipe-indexed duplication is intentional. Pipe 0 uses `HUBPREQ0`, `HUBPRET0`, `CURSOR0_0`, and `DC_PERFMON5`; pipe 1 uses `HUBP1`, `HUBPREQ1`, `HUBPRET1`, `CURSOR0_1`, and `DC_PERFMON6`; DPP0 uses `DPP_TOP0`, `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, and `CM0`. Higher-level code usually abstracts this duplication through per-instance register lists, but the generated macro names must remain exact for those lists to compile.

The bit widths encode hardware limits that callers must respect: 48-bit-style surface addresses split into 32-bit low and 16-bit high fields, 14-bit viewport/pitch dimensions in many places, 23-bit/27-bit timing and scale-ratio fields, 4-bit VMID/QoS fields, 9-bit cursor/gamma LUT indices, and paired 16-bit matrix coefficients in many color registers.

## Risks And Edge Cases

- Incorrect shift or mask constants can silently corrupt adjacent fields during read/modify/write operations. This is especially risky for packed registers with configuration, status, clear, and interrupt-enable bits in the same 32-bit word.
- The chunk contains security-sensitive memory attributes such as TMZ, system, snoop, and VM/TLB fields. Misprogramming these can expose protected buffers incorrectly or cause display fetch faults.
- Surface address, pitch, metadata, DCC, and flip-control fields are tightly coupled. A valid mask can still be used in an invalid sequence, causing underflow, stale frame display, wrong chroma plane fetch, or hangs around flip pending/in-use state.
- Many memory power controls have matching status fields, but the masks do not enforce sequencing or polling. Powering down DET, request, cursor, scaler, LUT, line-buffer, or OBUF memory while a pipe is active can cause data loss or underflow.
- Pipe 0 and pipe 1 definitions are near-duplicates; copy-generation drift between `HUBPREQ0` and `HUBPREQ1`, `HUBPRET0` and `HUBPRET1`, `CURSOR0_0` and `CURSOR0_1`, or `DC_PERFMON5` and `DC_PERFMON6` would be hard to catch by compile tests alone.
- DPP color/scaler fields use dense fixed-point encodings. Driver-side values must be range-checked before packing, because the masks will truncate oversized coefficients, phase values, scale ratios, LUT indices, and RAMA region counts.
- This chunk ends mid-register at `CM0_CM_GAMCOR_RAMA_REGION_14_15`; only the shift macros for region 14 LUT offset, region 14 segment count, and region 15 LUT offset are visible here. The matching region 15 segment shift and masks continue in the next chunk, so whole-file research must reconcile that boundary before treating the `REGION_14_15` definition as complete.

## Test Signals

- Build coverage: any renamed or malformed macro should break compilation in DCN 3.0.3 register-list or register-helper users.
- Register mask validation: generated-header comparison against the vendor register database can catch drift in shift/mask values, especially for duplicated pipe blocks.
- Runtime display tests: modeset, plane enable/disable, page flip, stereo flip, cursor movement/format changes, DCC/TMZ surfaces, suspend/resume, and multi-pipe configurations exercise the HUBP/HUBPREQ/HUBPRET/CURSOR portions.
- Fault and interrupt tests: induced VM faults, DMDATA underflow, vblank/read-line interrupt handling, flip interrupt/away interrupt handling, and HUBP timeout/underflow paths should observe and clear the status fields defined here.
- Perf/debug tests: DPP CRC readback, perfmon counter start/stop/count-off interrupts, HUBP DCFCLK/DPPCLK measurement windows, and host-read throttling verify the debug/performance monitor masks.
- Color and scaler tests: pre-CSC/post-CSC/gamut matrix programming, pre-degamma/gamma correction LUT programming, RAMA piecewise-linear regions, scaler coefficient RAM writes, luma/chroma scaling, overscan, line-buffer partitioning, and OBUF modes provide coverage for the DPP0/CNVC/DSCL/CM definitions.
