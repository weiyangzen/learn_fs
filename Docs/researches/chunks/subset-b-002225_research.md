# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 17729-20256

## Purpose

This chunk is generated AMD DCN 4.2.0 display register-field metadata. It contains C preprocessor constants for bit shifts and masks, not executable logic. Runtime AMDGPU display and DMUB code combine these constants with `dcn_4_2_0_offset.h` and register helper macros to read, write, and update individual fields inside DCN 4.2.0 memory-mapped display registers.

The requested range covers 2,093 `#define` lines: 1,047 `__SHIFT` macros and 1,046 `_MASK` macros. It starts at `SDPIF_REQUEST_RATE_LIMIT`, moves through DCHUBBUB return-path, arbitration, VM, performance, HUBP0, HUBPREQ0, HUBPRET0, cursor, and perfmon definitions, and ends inside `HUBP1_DCHUBP_VMPG_CONFIG`. The final `FORCE_ONE_ROW_FOR_FRAME_MASK` for that last register is on the next physical line, outside this chunk, so the missing mask is a chunk-boundary artifact.

Although the repository path is under `ceph-client`, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Register Families In This Chunk

The chunk is organized by generated `addressBlock` comments:

- `dce_dc_dchubbubl_hubbub_ret_path_dispdec`: SDPIF memory power, return-path memory power, DCHUBBUB CRC capture, DCC statistics, compression-buffer and DET sizing, memory power modes/status, reserved compbuf space, and return-path debug index/data.
- `dce_dc_dchubbubl_hubbub_dispdec`: DCHUBBUB arbitration, QoS, DRAM/self-refresh/p-state watermark sets A-D, HostVM controls, watermark-change handshake, MALL controls, timeout enables, global timer, VTG controls, soft reset, clock controls, performance measurement, timeout interrupt status, and FMON controls.
- `dce_dc_dchubbubl_dchubbub_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON5_*` perf counter, perfmon state, control, current-value, high, and low fields.
- `dce_dc_dchubbubl_hubbub_vmrq_if_dispdec`: `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` page-table controls/base/start/end fields, default fault address fields, and VM fault control/status/address fields.
- `dce_dc_dcbubp0_dispdec_hubp_dispdec`: HUBP0 surface format, tiling, viewport, request-size, control, clock, VM page, MALL, debug, measurement-window, and MALL status fields.
- `dce_dc_dcbubp0_dispdec_hubpreq_dispdec`: HUBPREQ0 pitch, VMID, primary/secondary luma/chroma surface and metadata addresses, surface control, flip control, flip interrupts, in-use addresses, TTU/QoS, DMDATA VM, VM aperture/TLB, prefetch, vblank, flip, nominal and per-line delivery timing, cursor settings, memory power, p-state force, and request status fields.
- `dce_dc_dcbubp0_dispdec_hubpret_dispdec`: HUBPRET0 control, memory power, read-line programming/value/status, and interrupt fields.
- `dce_dc_dcbubp0_dispdec_cursor0_dispdec`: cursor plane control/address/size/position/hot-spot/stereo, cursor memory power, DMDATA address/control/QoS/status/software data, and HUBP 3DLUT control/address/DLG fields.
- `dce_dc_dcbubp0_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`: `DC_PERFMON6_*` perf counter and perfmon field definitions for HUBP-related monitoring.
- `dce_dc_dcbubp1_dispdec_hubp_dispdec`: beginning of HUBP1 display pipe metadata, covering surface config, address config, tiling, primary/secondary viewports, request-size config, HUBP control, clock control, and most of VM page config.

The range contains both global DCHUBBUB register metadata and the full first HUBP/HUBPREQ/HUBPRET/CURSOR instance for pipe 0, then starts the analogous HUBP1 instance. The repeated HUBP0/HUBP1 shape is important because higher-level display code often instantiates hardware blocks by pipe index.

## Important APIs, Types, And Macros

No functions, structs, enums, variables, locks, allocations, or persistence APIs are declared here. The exported interface is the generated macro naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted register-word mask for isolating that field during read-modify-write.

These names are consumed through AMD display register helper layers, including `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WAIT`, `SF`, `SR`, `SRI`, `HUBBUB_SF`, `HUBP_SF`, `IPP_SF`, `TF_SF`, `FD_SHIFT`, and `FD_MASK` style macros. The companion offset header supplies addresses; this header supplies field layout inside each address.

Important field groups include:

- DCHUBBUB memory sizing and power: `DCHUBBUB_COMPBUF_CTRL`, `DCHUBBUB_DET0_CTRL` through `DCHUBBUB_DET3_CTRL`, `DCHUBBUB_MEM_PWR_MODE_CTRL`, `DCHUBBUB_MEM_PWR_STATUS`, `DCHUBBUB_SDPIF_MEM_PWR_*`, `DCHUBBUB_RET_PATH_MEM_PWR_*`, and `COMPBUF_MEM_PWR_CTRL_*`.
- DCHUBBUB arbitration and bandwidth: `DCHUBBUB_ARB_DF_REQ_OUTSTAND`, `DCHUBBUB_ARB_SAT_LEVEL`, `DCHUBBUB_ARB_QOS_FORCE`, `DCHUBBUB_ARB_DRAM_STATE_CNTL`, watermark registers A-D, `DCHUBBUB_ARB_HOSTVM_CNTL`, `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`, and `DCHUBBUB_ARB_MALL_CNTL`.
- VM request metadata: repeated `DCN_VM_CONTEXT<n>_*` fields for page-table depth, block size, base address, start logical page, and end logical page, plus `DCN_VM_FAULT_*`.
- HUBP surface fetch metadata: `HUBP0_DCSURF_*`, `HUBP0_DCHUBP_*`, `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCN_*`, and equivalent beginning `HUBP1_*` definitions.
- Flip and interrupt metadata: `HUBPREQ0_DCSURF_FLIP_CONTROL`, `HUBPREQ0_DCSURF_FLIP_CONTROL2`, `HUBPREQ0_DCSURF_SURFACE_FLIP_INTERRUPT`, `HUBPRET0_HUBPRET_INTERRUPT`, and DCHUBBUB timeout/performance interrupt fields.
- Cursor and metadata planes: `CURSOR0_0_CURSOR_*`, `CURSOR0_0_DMDATA_*`, and `CURSOR0_0_HUBP_3DLUT_*`.
- Performance/debug: `DCHUBBUB_CRC_*`, `DCHUBBUB_DCC_STAT*`, `DCHUBBUB_PERFORMANCE_MEASUREMENT_*`, `FMON_CTRL`, `DC_PERFMON5_*`, `DC_PERFMON6_*`, HUBP debug muxes, HUBP measure-window controls, and status registers.

## Control Flow And Hardware Behavior

This header has no C control flow. It describes hardware control surfaces that other code sequences with MMIO operations.

For DCHUBBUB, driver code programs buffer allocations, watermarks, arbitration policy, HostVM behavior, MALL behavior, and power modes. A typical flow writes requested DET or compression-buffer sizes, waits for `*_SIZE_CURRENT` fields when the hardware reports a committed size, checks error/status bits such as `CONFIG_ERROR`, then programs watermark sets A-D and requests a watermark change through `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL`.

For VM contexts, runtime code supplies page-table layout and logical aperture information per VMID. The fields here encode page-table depth/block size and high/low portions of page table base, start, and end logical page numbers. Fault control and status fields expose whether invalid/missing PTE/PDE activity is reported, which VMID/client caused it, and the faulting address.

For HUBP/HUBPREQ, the control flow is mode-set and flip oriented. Software programs surface format, tiling, viewport dimensions, request size, VMID, luma/chroma addresses, metadata addresses, DCC/TMZ/encryption-related surface-control bits, TTU/QoS and prefetch/vblank/flip/nominal timing parameters, then arms or observes flip control and flip interrupt state. The macros also describe underflow, timeout, blanking, outstanding-request, and reset fields that mode-set, recovery, and diagnostics paths may poll or clear.

For cursor and DMDATA paths, software uses these fields to configure cursor enable/mode/pitch/size/position/hot spot, cursor memory addresses, DM data addresses, QoS, software data injection, and 3DLUT access. These are typically per-pipe state programmed during cursor updates, plane updates, or color-management updates.

For perfmon and debug, fields describe selectable counters, event selectors, current values, high/low counter reads, interrupt/status fields, CRC one-shot/continuous capture, DCC statistics, FMON, and test-debug index/data windows. Those paths are usually diagnostic, validation, or performance-measurement flows rather than normal scanout setup.

## State And Persistence Behavior

The header itself stores no state and persists no data. It is compile-time metadata.

The underlying registers are live DCN hardware state. Configuration fields such as watermarks, buffer sizes, VM page-table bases, surface addresses, tiling, viewport dimensions, DCC/TMZ flags, MALL selection, cursor geometry, and clock/power enables generally persist until reprogrammed, the block is reset, display power is gated, suspend/resume restores state, or the ASIC resets.

Status and handshake fields are more transient. Examples include `*_CURRENT` size fields, `*_DONE` bits, outstanding-request bits, flip-pending/flip-ready/flip-status bits, underflow and timeout status, VM fault status, perf counter state, CRC one-shot pending, memory power state, MALL status, and HUBPRET interrupt status. Clear fields and interrupt-clear fields likely have side effects by hardware convention, but access type is not encoded in this generated header.

Several blocks cross software and firmware ownership boundaries. DMUB and kernel Display Core can both rely on this generated metadata for DCN 4.2.0 register access. The header does not state which actor owns a given register at a given time, so sequencing, locking, and ownership are provided by higher-level DC/DMUB code and firmware protocols.

## Dependencies And Integration Points

Direct dependencies are the generated AMD DCN 4.2.0 register database and companion headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_offset.h` supplies matching MMIO offsets and base-index values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.c` includes both `dcn_4_2_0_offset.h` and `dcn_4_2_0_sh_mask.h` for DCN42 DMUB register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn42.h` defines DCN42 register offset/shift/mask storage used by the DMUB service layer.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubbub/dcn42/dcn42_hubbub.h` references DCHUBBUB fields such as `DCHUBBUB_COMPBUF_CTRL` and `DCHUBBUB_ARB_WATERMARK_CHANGE_CNTL` through hubbub register-table macros.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dpp/dcn42/dcn42_dpp.h` consumes cursor-control fields through transform/DPP register tables.
- Existing HUBP, hubbub, VMID, IRQ, cursor, and perfmon code from earlier DCN generations shows the same integration pattern: block-specific register tables token-paste register names into generated offset, shift, and mask constants, then runtime helpers perform read-modify-write or polling.

Functional integration points include display mode set, plane address programming, page flip, cursor update, color management/3DLUT setup, memory compression/DCC handling, secure/TMZ surface handling, VM fault reporting, DET/compbuf allocation, bandwidth watermark programming, MALL/sub-viewport behavior, memory power management, underflow/timeout recovery, CRC capture, and display performance monitoring.

## Risks And Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask can compile cleanly while reading or writing the wrong MMIO bits, corrupting adjacent fields or leaving hardware in an unexpected state.
- The macros are untyped preprocessor constants. The compiler cannot verify that a field belongs to the register being updated, that a value fits in the field width, or that reserved bits are preserved.
- Address and field metadata must match. Using `dcn_4_2_0_sh_mask.h` with the wrong offset header or with a mismatched silicon register table can silently program unrelated registers.
- Chunk boundaries are artificial. This range ends before `HUBP1_DCHUBP_VMPG_CONFIG__FORCE_ONE_ROW_FOR_FRAME_MASK`; adjacent chunks must be merged before making whole-register completeness claims for HUBP1.
- Many fields are side-effect-sensitive. Interrupt clear bits, flip-clear bits, timeout/underflow clears, VM fault acknowledgement, soft reset, memory power force/disable, and debug index/data windows should not be written by generic code without hardware sequencing.
- Repeated indexed blocks can hide copy/generation errors. HUBP0 and HUBP1 are expected to have parallel field layouts for shared hardware features; a single missing or shifted field can produce pipe-specific failures.
- Watermark, arbitration, and p-state fields affect display underrun margins. Incorrect values may only fail under high bandwidth, low memory clocks, self-refresh entry/exit, MALL use, multiple displays, high refresh rates, or suspend/resume.
- Surface address, VM, DCC, and TMZ fields are security- and correctness-sensitive. Bad programming can fetch from the wrong memory, trigger VM faults, expose stale data, break encrypted surfaces, or corrupt scanout.
- Status fields often reflect clocked or power-gated domains. Reads while HUBP, DCHUBBUB, cursor, or memory power domains are disabled can be stale, blocked, or undefined depending on hardware rules not expressed in this header.
- Perfmon, FMON, CRC, and test-debug fields are diagnostic surfaces. Leaving them enabled or mis-selecting sources can perturb validation, hide real underflows, or produce misleading measurements.

## Test Signals

Useful validation signals for this chunk include:

- Build AMDGPU display code with DCN 4.2.0 support enabled; missing or renamed macros should fail in DMUB DCN42, hubbub, DPP/cursor, HUBP, VMID, IRQ, and register-table construction paths.
- Mechanically compare this range against the authoritative generated DCN 4.2.0 register database and `dcn_4_2_0_offset.h`, allowing for the known end-boundary split in `HUBP1_DCHUBP_VMPG_CONFIG`.
- Check every `__SHIFT` macro has the expected `_MASK` partner within the merged source-file view, and verify each mask's least significant set bit matches the declared shift.
- Exercise mode-set and page-flip tests across pipe 0 and pipe 1, including primary and secondary surfaces, stereo/viewport variants, DCC-enabled buffers, chroma planes, metadata addresses, and VMID changes.
- Run cursor movement, cursor format, cursor memory power, DMDATA, and 3DLUT/color-management tests that cover the `CURSOR0_0_*` and HUBP register fields.
- Run memory-pressure and bandwidth tests that stress DET/compbuf sizing, watermark sets A-D, p-state and self-refresh entry/exit, MALL/sub-viewport behavior, high refresh rates, multi-display, and suspend/resume.
- Validate VM fault paths by inducing controlled invalid mappings or aperture violations and confirming `DCN_VM_FAULT_STATUS` and fault address fields report expected VMID/client/address information.
- Verify interrupt and status behavior for flip completion, HUBPRET events, timeout detection, underflow, memory power status, and watermark-change completion; confirm clear bits do not drop unrelated events.
- Use CRC, DCC statistics, perfmon, FMON, and debug counter tests to confirm measurement fields select sources correctly and read high/low values coherently.

## Cross-Chunk Notes

Earlier chunks contain the preceding DCHUBBUB SDPIF pipe security/no-allocate fields that lead into this range. Later chunks continue HUBP1 beyond `HUBP1_DCHUBP_VMPG_CONFIG` and should include the rest of HUBP1 MALL, debug, HUBPREQ, HUBPRET, cursor, and perfmon metadata. The final per-file research document should merge adjacent chunks before making whole-file claims about all DCN 4.2.0 register families or all pipe instances.
