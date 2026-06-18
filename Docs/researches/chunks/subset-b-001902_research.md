# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 12383-14898

## Purpose

This chunk is generated AMDGPU DCN 3.1.6 register shift/mask metadata. It contains no executable code; it exports C preprocessor constants that describe bit offsets (`__SHIFT`) and bit masks (`_MASK`) for display-controller MMIO register fields. Driver code pairs these definitions with `dcn_3_1_6_offset.h` so common register helpers can read, write, and update individual hardware fields for this ASIC generation.

The requested range starts in the tail of the `CURSOR0_1_DMDATA_*` group, then covers the rest of perfmon 8, complete HUBP/HUBPREQ/HUBPRET/cursor/perfmon register-field groups for HUBP instances 2 and 3, and the start of DPP0 converter, cursor, scaler, and color-management fields. It ends inside `CM0_CM_POST_CSC_C11_C12`, so adjacent chunks are required for complete DPP0 color-management coverage. The slice contains 2,113 `#define` lines, split evenly into 1,057 shift macros and 1,056 mask macros, plus 373 generated comments/register headings.

Although the source lives under a local `ceph-client` tree, this file is AMD display hardware metadata. It does not implement distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, typedefs, enums, variables, includes, locks, allocation paths, or direct MMIO accesses in this chunk. The exported interface is entirely macro based:

- `<REGISTER>__<FIELD>__SHIFT`: least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`: mask used to isolate, clear, or insert the field.
- `// addressBlock: ...` comments: generated grouping metadata identifying the display sub-block that owns the following register definitions.

Major register families in this range:

- Tail of `CURSOR0_1_DMDATA_STATUS`, `DMDATA_SW_CNTL`, and `DMDATA_SW_DATA`: display metadata completion, underflow, clear, software update/repeat/size, and payload fields for cursor/sideband metadata on instance 1.
- `DC_PERFMON8`, `DC_PERFMON9`, and `DC_PERFMON10`: perf counter source selection, counted-value type, increment mode, run-enable mode, hardware stop/counter-off selectors, active/state bits, interrupt enables/status/acks, high/low values, and perfmon global control.
- `HUBP2` and `HUBP3`: surface format, address/tiling configuration, primary/secondary viewport coordinates, request-size configuration for luma/chroma/meta planes, HUBP control/status, blanking, reset, timeout, underflow, clock-control, VMPG, debug, and DCFCLK/DPPCLK measurement windows.
- `HUBPREQ2` and `HUBPREQ3`: surface pitch, VMID, primary/secondary luma and chroma surface addresses, metadata addresses, DCC/TMZ surface control, flip control/interrupts, in-use and earliest-in-use address latches, expansion mode, TTU/QoS, VM aperture/TLB controls, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor request settings, and HUBPREQ memory power controls/status.
- `HUBPRET2` and `HUBPRET3`: HUBPRET control, memory power control/status, read-line control/value/status, and interrupt status/ack/mask fields.
- `CURSOR0_2` and `CURSOR0_3`: cursor enable/mode/pitch/lines-per-chunk, address high/low, size, position, hot spot, stereo offsets, destination offset, cursor memory power, DMDATA address/control/QoS/status, and software DMDATA fields.
- `CNVC_CFG0` and `CNVC_CUR0`: DPP0 pixel format, format expansion/alpha/output FP controls, FP bias/scale, color-keyer channels, 2-bit alpha LUT, pre-dealpha/pre-realpha, pre-CSC mode and matrix coefficients, converter coefficient format, pre-degamma, and cursor0 color/control/FP scale-bias fields.
- `DSCL0`: DPP0 scaler coefficient RAM select/data, scaler mode/taps, DSCL control/autocal/update, manual replicate factors, luma/chroma horizontal and vertical ratios and initial phases, black color, extended overscan, OTG blanking, recout/MPC size, line-buffer data and memory controls/status, DSCL memory power, output-buffer control, and OBUF memory power.
- Start of `CM0`: color-management bypass/update-pending and post-CSC mode/current fields, followed by the first post-CSC coefficient pair (`C11`/`C12`) where the range stops.

## Control Flow

This header has no runtime branches or sequencing. Runtime control flow is provided by AMD display code that includes the generated header:

1. DCN 3.1.6 resource and DMUB code include `dcn_3_1_6_offset.h` for register addresses and this `dcn_3_1_6_sh_mask.h` file for field layout.
2. Register-list macros paste symbolic register and field names into generated constants. Offsets come from the offset header; masks and shifts come from this file.
3. Helpers such as `FD_MASK`, `FD_SHIFT`, `TF_SF`, `IPP_SF`, HUBP/HUBBUB field macros, DMUB field macros, and `REG_READ`/`REG_WRITE`/`REG_UPDATE` style accessors materialize typed register tables or perform field updates.
4. Higher-level display flows program planes, cursors, page flips, memory request timing, virtual-memory controls, scaler ratios, converter/color controls, and perf counters through those tables.

The macros do not encode ordering constraints. Consumers must still sequence plane address updates, update locks, flip interrupt clears, cursor/DMDATA updates, DCC/TMZ setup, VM aperture/TLB programming, scaler coefficient RAM writes, line-buffer partitioning, memory-power transitions, clock gating, and perf counter clear/freeze/ack operations according to hardware rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files or kernel memory. It describes MMIO-backed hardware state. The represented state includes:

- Plane-fetch state in HUBP/HUBPREQ for instances 2 and 3: surface format/layout, tiling, viewport windows, pitch, luma/chroma addresses, metadata addresses, DCC and TMZ protection, active/in-use address latches, flip pending/interrupt state, blanking, destination geometry, and request granularity.
- Display memory scheduling and QoS state: TTU controls, QoS watermarks, global TTU settings, prefetch/vblank/flip/nominal timing registers, per-line delivery estimates, cursor request adjustments, and reference-clock-to-pixel-clock ratios.
- Virtual-memory state: VMID selection, system aperture low/high limits, L1 TLB controls, DMDATA VM controls, and VMPG page-size configuration.
- Cursor and DMDATA state: cursor image address/size/position/hotspot/stereo, cursor memory power, metadata address/control/status/QoS, and software-supplied metadata payloads.
- Perfmon state: counter event selection, counter state, counted values, interrupt status/ack, high/low readback values, run-enable modes, and perfmon global control.
- DPP0 processing state: pixel conversion, color keying, alpha/dealpha/re-alpha, pre-CSC matrix, pre-degamma, cursor colors, scaler taps/ratios/initial phases/coefficient RAM, line-buffer partitioning, scaler/OBUF memory power, recout/MPC geometry, overscan, and the beginning of post-CSC color-management state.

Persistence and side effects are hardware-defined. Configuration fields usually remain programmed until modeset, plane update, power gating, suspend/resume, or ASIC reset. Status, pending, underflow, timeout, interrupt, ack, clear, memory-power state, in-use, and earliest-in-use fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only exposes bit positions and masks; it does not state access type.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.6 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies matching MMIO offsets.
- DCN 3.1.6 base-address definitions in the resource and DMUB translation units.
- Common AMD display register helper macros that derive field masks and shifts from generated names.

Observed include/integration points in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes the DCN 3.1.6 offset/mask headers and constructs the DCN 3.1.6 resource pool using shared DCN31 HUBP, DPP, scaler, cursor, IRQ, and related building blocks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`, which includes the same generated headers and builds `dmub_srv_dcn316_regs` with `FD_MASK` and `FD_SHIFT` over `DMUB_DCN31_FIELDS()`.
- Shared DPP/IPP/HUBP code such as `dcn10_dpp.h`, `dcn10_ipp.h`, `dcn10_dpp.c`, and DCN31 HUBP/resource code, which consume families like `CNVC_CFG0`, `CNVC_CUR0`, `DSCL0`, `CURSOR0_*`, `HUBP*`, and `HUBPREQ*` through generation-specific register tables.
- IRQ and atomic/page-flip paths that rely on HUBPREQ flip interrupt and pending/status fields.
- Display mode validation and watermark programming, which compute timing and delivery values that are ultimately written to TTU, prefetch, vblank, nominal, and per-line delivery registers represented here.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong mask or shift is still a valid C constant and can silently program the wrong MMIO bits.
- The chunk boundary is artificial. It starts after the `CURSOR0_1_DMDATA_QOS_CNTL` group has already begun and ends mid-register at `CM0_CM_POST_CSC_C11_C12`; adjacent chunks are required for complete file-level claims.
- Instance repetition is copy-sensitive. `HUBP2`/`HUBP3`, `HUBPREQ2`/`HUBPREQ3`, `HUBPRET2`/`HUBPRET3`, `CURSOR0_2`/`CURSOR0_3`, and `DC_PERFMON9`/`10` are structurally similar but not interchangeable.
- Surface address, pitch, metadata, DCC, and TMZ fields are high impact. Incorrect fields can cause corrupted planes, chroma corruption, blank output, protected-memory faults, metadata/DCC corruption, or display VM faults.
- Flip and update fields are handshake-sensitive. Bad pending, lock, clear, enable, or interrupt masks can cause missed page flips, stuck IRQs, frame pacing failures, or races during atomic commits.
- TTU, prefetch, vblank, nominal, and per-line delivery fields are bandwidth/timing-sensitive. Errors may only appear under high resolution, high refresh, multi-display, DCC, scaling, cursor, overlay, or low-memory-clock workloads.
- Scaler and line-buffer fields are mode-sensitive. Wrong tap, ratio, init, coefficient RAM, line-buffer partition, recout, MPC size, or overscan masks can distort images, misalign chroma, underflow, or fail only for specific scaling ratios and formats.
- Memory power, clock, reset, underflow, timeout, interrupt ack, and status fields may have side effects. Writes while blocks are gated, reset, scanning, or pending update can be ignored or disruptive.
- Field names containing repeated words such as `*_MASK_MASK` in perf/status families are generated from hardware field names and should not be manually simplified without updating all consumers.

## Test Signals

Useful validation combines generated-header checks with display behavior:

- Build AMDGPU/DC with DCN 3.1.6 enabled. Missing or renamed macros should fail in `dcn316_resource.c`, `dmub_dcn316.c`, and shared DCN31/HUBP/DPP/IPP users.
- Mechanically verify that each visible `__SHIFT` macro in lines 12383-14898 has the expected companion `_MASK` macro for the same register field where the generated schema defines one.
- Diff this slice against AMD's authoritative DCN 3.1.6 register database and against nearby generated generations where hardware compatibility is expected.
- Exercise enough active planes to use HUBP/HUBPREQ instances 2 and 3: primary plus overlays, chroma formats, DCC-enabled buffers, protected buffers, cursor planes, rapid page flips, multi-display, and suspend/resume.
- Run modes that stress timing and scaler paths: high resolution, high refresh, fractional scaling, 4:2:0/chroma planes, nonzero overscan, cursor movement, bandwidth-limited memory clocks, and multi-plane composition.
- Check page-flip and IRQ behavior with DRM page-flip tests, looking for missed flips, stuck pending bits, interrupt storms, or stale in-use addresses.
- Monitor kernel logs and hardware debug output for HUBP/HUBPREQ underflow, timeout, VM fault, DCC corruption, cursor artifacts, scaler artifacts, memory-power wait failures, and resume-only failures.
- Validate perfmon programming by enabling display performance counters and confirming event selection, clear/freeze/run, interrupt status/ack, and high/low counter readbacks behave plausibly.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `CURSOR0_1_DMDATA_*` area. This chunk completes instance 1 DMDATA status/software data, covers complete instance 2 and 3 HUBP/HUBPREQ/HUBPRET/cursor/perfmon field groups, and starts DPP0 converter/scaler/color-management coverage. The next chunk must continue `CM0_CM_POST_CSC_C11_C12` and the rest of the DPP0 color-management register set before the merge lane writes a complete per-file report for `dcn_3_1_6_sh_mask.h`.
