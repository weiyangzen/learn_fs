# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_sh_mask.h lines 9829-12382

## Purpose

This chunk is generated AMD DCN 3.1.6 register field metadata. It contains no executable C logic; it publishes preprocessor constants for bit shifts and bit masks used to encode or decode fields inside DCN display-controller MMIO registers. Consumers pair these `__SHIFT` and `_MASK` macros with the matching register offsets from `dcn_3_1_6_offset.h` and the AMD display register helper macros.

The requested range contains 2,554 source lines and 2,084 `#define` entries. It starts in the DCHUBBUB/VM section at the local-HBM aperture and SDPIF security fields, covers DCHUBBUB return-path, VM request, and perfmon field definitions, then covers HUBP/HUBPREQ/HUBPRET/CURSOR field definitions for display pipes 0 and 1. Although this repository path is under a `ceph-client` source mirror, this file is AMDGPU display-driver ASIC register metadata and does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or exported symbols in this range. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a register field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

Major field families in this chunk:

- DCHUBBUB/VM aperture and security fields: `DCN_VM_LOCAL_HBM_ADDRESS_*`, `DCN_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`, `DCHUBBUB_SDPIF_PIPE_SEC_LVL`, `DCHUBBUB_SDPIF_PIPE_DMDATA_SEC_LVL`, and SDPIF memory power status/control.
- DCHUBBUB return path: DCC video-format enable, DCC constant tables `DCHUBBUB_RET_PATH_DCC_CFG0_0` through `DCHUBBUB_RET_PATH_DCC_CFG7_1`, return-path memory power control/status, DCHUBBUB CRC enable/source/pipe/surface selection, CRC result fields, DCC statistics, compressed-buffer sizing, DET buffer sizing for DET0 through DET3, memory-power mode/status, and reserved compbuf space.
- DCHUBBUB VM request interface: repeated `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` page-table depth/block-size fields, base/start/end page-table address fields, default-address fields, and VM fault control/status/address fields.
- `DC_PERFMON6` and `DC_PERFMON7`: perfcounter select/clear/status, perfmon enable/state, current-value capture, high/low counter values, and integer/misc capture fields.
- HUBP0/HUBP1 core pipe fields: surface format/rotation/tiling/swizzle/DCC metadata controls, viewport start and dimension fields for luma and chroma planes, request-size controls, HUBP clock control, VM page config, debug fields, and DCFCLK/DPPCLK measurement-window controls.
- HUBPREQ0/HUBPREQ1 memory request fields: luma/chroma pitch, VMID settings, primary/secondary and meta-surface 64-bit addresses, surface control, flip control and flip interrupts, current and earliest in-use addresses, expansion mode, TTU/QoS watermarks and deadlines, DMDATA VM control, system aperture limits, MX L1 TLB control, blank/destination/prefetch/vblank/flip/nominal timing parameters, per-line delivery, cursor request timing, ref-to-pixel frequency ratio, destination Y delta request limits, and HUBPREQ memory power state.
- HUBPRET0/HUBPRET1 return fields: DET plane base, pack/crossbar controls, DMROB/PIXCDC memory power state, read-line interval/window configuration, vblank and read-line interrupts, current/snapshot line values, and read-line status bits.
- CURSOR0_0 and partial CURSOR0_1 fields: cursor enable/request/magnify/mode/TMZ/pitch/lines-per-chunk/perfmon controls, cursor surface address, size, position, hot spot, stereo offsets, destination offset, cursor ROB memory power state, DMDATA address/control/QoS/status/software fields for pipe 0, and the beginning of the same pipe-1 cursor/DMDATA family through `CURSOR0_1_DMDATA_QOS_CNTL`.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMD display code:

1. DCN 3.1.6 resource and DMUB code include `dcn_3_1_6_offset.h` and `dcn_3_1_6_sh_mask.h`.
2. Resource code builds per-block register tables and shift/mask tables for hubbub, HUBP, cursor, perfmon, DMUB, and related DCN components.
3. Driver helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_READ`, `REG_WRITE`, and polling/wait helpers use the generated masks and shifts to change individual fields without hand-coded bit math at every call site.
4. Hardware sequencing code performs modeset, plane update, flip, cursor update, VM setup, power-gating, QoS, timing, and diagnostic operations by writing these fields in the order required by DCN hardware.

The macros themselves do not encode ordering constraints. For example, flip-control fields do not express when a surface update lock must be acquired, CRC fields do not express when results are valid, and memory-power fields do not express when a block is safe to gate. Those semantics live in the consuming DCN code and hardware programming guides.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on disk. It describes MMIO-backed GPU display state. The represented hardware state includes:

- Aperture, VM context, page-table, default-address, and fault-reporting state for display memory requests.
- Surface, metadata, pitch, viewport, tiling, DCC, and flip state for HUBP/HUBPREQ pipes 0 and 1.
- Timing-derived request state such as prefetch, vblank, flip, nominal, per-line delivery, QoS, TTU deadlines, and destination geometry.
- Return-path buffers and compression state, including DCC constants/statistics, DET/compbuf allocation, crossbar mapping, and read-line/vblank status.
- Cursor image address, size, position, hot spot, stereo, metadata, memory-power, QoS, and software DMDATA update state.
- Diagnostic and observability state for CRC, perfmon counters, debug registers, and fault status.
- Power-management state for SDPIF, return path, compbuf, DET, HUBPREQ, HUBPRET, and cursor memory blocks.

Persistence is hardware-defined. Configuration fields generally remain until modeset/reprogramming, suspend/resume restoration, power gating, or ASIC reset. Status, interrupt, counter, `*_CURRENT`, `*_DONE`, clear, sticky, fault, and power-status fields may be read-only, self-clearing, write-one-to-clear, or otherwise side-effect-sensitive; this header names and locates fields but does not classify access permissions.

## Dependencies And Integration Points

This generated chunk must match:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_6_offset.h`, which supplies the register offsets for the same DCN 3.1.6 register names.
- AMD display register helper infrastructure that combines offsets with field masks/shifts for `REG_SET`, `REG_UPDATE`, `REG_GET`, and related helpers.
- DCN 3.1/3.1.6 block implementations for hubbub, HUBP, cursor, perfmon, resource construction, and DMUB register access.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c`

Those include sites use token-pasted register names and block-specific shift/mask structs, so generated symbol spelling is part of the local ABI between this header and the DCN code. This chunk also aligns structurally with neighboring generated DCN headers for later ASIC revisions; many families such as `HUBPREQ0_DCSURF_FLIP_CONTROL__*`, `DCN_VM_CONTEXT0_CNTL__*`, `DCHUBBUB_CRC_CTRL__*`, and `CURSOR0_0_CURSOR_CONTROL__*` appear across other DCN versions with compatible naming.

## Risks And Edge Cases

- Bitfield drift is the central risk. These constants are untyped preprocessor values, so an incorrect shift or mask can compile cleanly while changing the wrong field in a live MMIO register.
- Repeated pipe families are copy-sensitive. HUBP/HUBPREQ/HUBPRET/CURSOR pipe 0 and pipe 1 definitions are structurally similar but instance-specific; a single bad field can affect only one display pipe, plane, cursor, or multi-display topology.
- VM and aperture fields are high risk because wrong page-table, aperture, default-address, or VMID fields can produce display faults, black screens, stale scanout, incorrect memory isolation, or hard-to-debug GPU VM errors.
- Surface address, meta-address, pitch, tiling, DCC, and flip fields are sequencing-sensitive. Incorrect field definitions can manifest only during page flips, stereo flips, DCC-enabled surfaces, rotated/swizzled formats, chroma planes, or specific plane formats.
- Timing/QoS/prefetch fields affect underflow margins. Bad masks in TTU, vblank, flip, nominal, or per-line delivery parameters can cause intermittent underflow, stutter, or failures that depend on clock state and display mode.
- Power-control fields can be hazardous. Incorrect force/disable/low-power-state masks may leave SRAMs powered when they should gate, or gate memory while display requests are active.
- Status, interrupt, fault, and clear fields may have side effects. Treating clear bits or sticky status as ordinary configuration fields can lose interrupt/fault evidence or wedge status handling.
- The requested chunk boundaries are artificial. It starts after earlier VM/framebuffer/AGP definitions and ends partway through the `CURSOR0_1` DMDATA field family, so adjacent chunks are required for complete file-level conclusions.

## Test Signals

Useful validation combines generated-header consistency with DCN hardware behavior:

- Build AMDGPU/DC with DCN 3.1.6 support enabled; missing or renamed macros should fail in `dcn316_resource.c`, `dmub_dcn316.c`, or the shared DCN block constructors that consume shift/mask tables.
- Mechanically verify that every visible field has a paired shift and mask macro where expected, and that masks match the declared bit positions and widths.
- Diff this chunk against AMD's authoritative DCN 3.1.6 register database and nearby generated headers where field compatibility is expected.
- Exercise modesets and plane updates across pipes 0 and 1 with luma/chroma surfaces, DCC-enabled surfaces, rotation/swizzle/tiled layouts, stereo-flip paths, immediate and delayed flips, cursor movement, cursor format changes, and cursor DMDATA updates.
- Stress VM paths with page-table programming, system-aperture limits, VM fault reporting, multiple VMIDs, TMZ-protected cursor or DMDATA surfaces, and suspend/resume.
- Validate timing and bandwidth behavior at high resolutions/refresh rates: watch for underflow, missed flips, wrong vblank timing, QoS deadline problems, or prefetch failures.
- Check diagnostics: CRC capture values, DCC statistic completion, perfmon counter enable/read/clear behavior, read-line/vblank interrupts, surface-flip interrupts, and VM fault status/address reporting.
- Test power-management transitions for HUBBUB, HUBPREQ/HUBPRET, DET/compbuf, SDPIF, and cursor memory blocks during idle, active display, display-off, clock gating, and resume.

## Cross-Chunk Notes

Earlier chunks in `dcn_3_1_6_sh_mask.h` contain the preceding DCHUBBUB force-IO, framebuffer, and AGP VM fields that lead into this range. Later chunks continue the `CURSOR0_1` DMDATA fields and the remaining DCN 3.1.6 shift/mask namespace. The final per-file research document should merge adjacent chunks before making complete claims about all pipes, all cursor instances, or the full DCN 3.1.6 register-field map.
