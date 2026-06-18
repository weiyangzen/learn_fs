# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 7167-9804

## Scope

This chunk is part of the generated AMD DCN 3.0.0 ASIC register shift/mask header. It covers lines 7167-9804 and contains 2,055 `#define` entries: 1,030 `__SHIFT` constants and 1,025 `_MASK` constants across 483 distinct register names. There are no C functions, structs, enums, storage objects, or executable branches; the API surface is the generated macro namespace used by AMDGPU Display Core register helper code.

The slice starts in the tail of `DC_PERFMON4_PERFMON_CNTL` after the matching `DC_PERFMON4_PERFCOUNTER_*` fields from the prior chunk, and it ends at the beginning of `DC_PERFMON6_PERFCOUNTER_CNTL`. The final per-file report should merge adjacent chunks before treating performance-monitor instances 4 and 6 as complete.

## Purpose

The purpose of this chunk is to map DCN 3.0.0 display/audio register fields to exact bit positions and positioned masks. Runtime code combines these constants with register offsets from `dcn_3_0_0_offset.h` and register helper macros such as `REG_SET`, `REG_UPDATE`, `REG_GET`, and field-list symbol-pasting helpers.

Major hardware surfaces represented here are:

- Display performance monitor tails and instances: the end of `DC_PERFMON4`, the full `DC_PERFMON5` block for DCHUBBUB, and the start of `DC_PERFMON6` for HUBP0.
- Display HDA/Azalia audio: codec endpoint index/data windows for endpoints 0-7, input endpoints 0-7, stream index/data windows for streams 8-15, controller DMA/cache/clock/DTO controls, CRC/debug registers, codec root/function parameters, power/reset controls, port connectivity, and GTC group offsets.
- DCHUBBUB SDPIF/return/hubbub blocks: request credit/status, VM physical request controls, forced-I/O status capture, framebuffer/AGP/HBM aperture registers, per-pipe security levels for DCC metadata/cursor/GPUVM/surface/DMDATA, DCC return constants, CRC controls/results, arbitration watermarks, DRAM-state timing, global timer, timeout detection, soft reset, clock controls, surface-check registers, VTG controls, and FMON controls.
- VM request interface: `DCN_VM_CONTEXT0` through `DCN_VM_CONTEXT15` page-table control/base/start/end fields, default address fields, and VM fault control/status/address fields.
- HUBP0/HUBPREQ0/HUBPRET0: surface format, tiling, viewport, request sizing, enable/blank/underflow/timeout, clock and measurement windows, pitch, VMID, luma/chroma primary/secondary surface and metadata addresses, DCC/TMZ control, flip control/interrupt/in-use tracking, TTU/QoS/vblank/flip/nominal timing, prefetch, cursor request timing, memory power control/status, return-path read-line windows, vblank/read-line interrupts, and read-line status.
- Cursor and DMDATA for pipe 0: cursor enable/mode/pitch/address/size/position/hotspot/stereo/destination offset, cursor memory power, DMDATA address attributes, QoS, underflow/done status, and software DMDATA injection.

Although the repository path is under a `ceph-client` source mirror, this source slice is AMD GPU display/audio register metadata. It does not implement Ceph filesystem logic, distributed storage behavior, or filesystem persistence.

## Important API Surface

The exported interface is the generated two-macro pattern:

- `<REGISTER>__<FIELD>__SHIFT`: low bit number for the field.
- `<REGISTER>__<FIELD>_MASK`: already-positioned bit mask for the same field.

Important macro families in this chunk include:

- `DC_PERFMON4_*`, `DC_PERFMON5_*`, and the first `DC_PERFMON6_PERFCOUNTER_CNTL` fields for event selection, counted-value selection, increment/run-enable modes, counter state, monitor clocking, current-value interrupt status/ack, and high/low counter readback.
- `AZF0ENDPOINT*`, `AZF0INPUTENDPOINT*`, and `AZF0STREAM8` through `AZF0STREAM15` index/data macros for indirect Azalia endpoint, input endpoint, and stream register access.
- `AZALIA_*` controller fields for clock gating, audio DTO, SOCCLK deep-sleep exit, DMA snoop/isochronous attributes, RIRB/DP/CORB DMA behavior, cyclic buffer position/sync, payload capabilities, stream arbiter latency, input/output CRC controls/results, memory power, codec parameters, codec power/reset, converter synchronization, port connectivity, and GTC offsets.
- `DCHUBBUB_SDPIF_*`, `VM_REQUEST_PHYSICAL`, `DCHUBBUB_FORCE_IO_STATUS_*`, `DCN_VM_FB_*`, `DCN_VM_AGP_*`, `DCN_VM_LOCAL_HBM_*`, and per-pipe `DCHUBBUB_SDPIF_PIPE_*_SEC_LVL` fields for display hub memory access, security level tagging, and aperture setup.
- `DCHUBBUB_RET_PATH_DCC_CFG*`, `DCHUBBUB_CRC_*`, `DCHUBBUB_ARB_*`, `DCHUBBUB_TIMEOUT_*`, `DCHUBBUB_CLOCK_CNTL`, `DCFCLK_CNTL`, `VTG*_CONTROL`, and `FMON_CTRL*` for compression return constants, CRC validation, arbitration/watermark programming, clock/reset behavior, timeout interrupts, vertical timing generator control, and fabric-monitor diagnostics.
- `DCN_VM_CONTEXT[0-15]_*`, `DCN_VM_DEFAULT_ADDR_*`, and `DCN_VM_FAULT_*` for display VM page-table layout, logical page range limits, default-address behavior, and fault status/address capture.
- `HUBP0_DCSURF_*`, `HUBP0_DCHUBP_*`, and `HUBP0_HUBP_*` for surface format/rotation/alpha, tiling, viewport, request chunk sizing, blank/disable/underflow/timeout state, clock gating/readback, VMPG configuration, and DCFCLK/DPPCLK performance windows.
- `HUBPREQ0_DCSURF_*`, `HUBPREQ0_DCN_*`, `HUBPREQ0_PREFETCH_*`, `HUBPREQ0_VBLANK_*`, `HUBPREQ0_FLIP_*`, `HUBPREQ0_NOM_*`, and `HUBPREQ0_PER_LINE_DELIVERY*` for scanout address programming, DCC/TMZ surface controls, frame-boundary flip sequencing, request timing, and QoS.
- `HUBPRET0_HUBPRET_*` for return-path detile/ROB/CDC memory power, read-line interval/window programming, vblank/read-line interrupt mask/type/clear/status fields, and current read-line readback.
- `CURSOR0_0_*` for cursor fetch/display state and DMDATA transport.

Generated names that end in repeated words, such as `*_MASK_MASK`, are expected when the hardware field itself is named `MASK` and the generated suffix also denotes a mask constant.

## Control Flow

This header chunk has no local control flow. The runtime sequence is supplied by Display Core and DMUB code that includes the DCN 3.0.0 offset and mask headers, builds per-block register tables, and then writes or reads fields through MMIO helpers.

Typical external flow is:

1. DCN30 resource, IRQ, clock, GPIO, and DMUB sources include `dcn_3_0_0_offset.h` and `dcn_3_0_0_sh_mask.h`.
2. Block-specific field-list macros paste names from this header into shift/mask tables for HUBBUB, HUBP, DPP/cursor, IRQ, clock-manager, and DMUB register access.
3. Modeset and plane programming paths write HUBP/HUBPREQ/HUBPRET surface, viewport, tiling, DCC/TMZ, VMID, timing, flip, cursor, and memory-power fields.
4. Clock and power paths program DCHUBBUB/HUBP/Azalia clock gates, memory power controls, and status polling.
5. IRQ/debug paths enable, query, and clear flip, vblank, read-line, timeout, CRC, fault, underflow, and performance-monitor state.

Ordering constraints are implicit. Callers must coordinate update locks, flip timing, VM page-table/aperture setup, address high/low pairs, DCC metadata, security/TMZ bits, interrupt clear bits, and memory power transitions in the sequence required by the hardware.

## State And Persistence Behavior

The file itself stores no state. The macros describe memory-mapped hardware state that persists in DCN 3.0.0 display/audio blocks while those blocks remain powered and programmed.

Persistent or semi-persistent hardware state represented here includes:

- Azalia audio controller, endpoint, stream, DMA, payload, DTO, CRC, codec power/reset, and connectivity configuration.
- DCHUBBUB aperture, security-level, DCC return, arbitration watermark, DRAM-state, timeout, FMON, CRC, clock, and reset state.
- VM context page-table base/start/end configuration, default addresses, and fault status/address capture.
- HUBP0 surface format, tiling, viewport, request sizing, clocking, blank/disable state, timeout and underflow state.
- HUBPREQ0 surface pitch, luma/chroma and metadata addresses, DCC/TMZ controls, VMID, flip locks/pending/interrupts, in-use/earliest-in-use readbacks, TTU/QoS, vblank/flip/nominal timing, prefetch, and request memory power state.
- HUBPRET0 return path control, memory power, read-line windows, read-line/vblank interrupts, and read-line status.
- Cursor and DMDATA address, format, position, QoS, software data, underflow, and memory power state.
- Performance-monitor counter state, thresholds, interrupt status/ack, and readback values.

Many fields are not ordinary configuration values. Fields named `STATUS`, `CLEAR`, `ACK`, `PENDING`, `INUSE`, `FAULT`, `UNDERFLOW`, or `*_INT_*` can be live readback, sticky state, write-one-to-clear, or edge-sensitive control depending on the hardware register. This header encodes bit layout only; it does not encode access type, reset value, latch timing, or legal programming sequences.

## Dependencies And Integration Points

This chunk depends on the DCN 3.0.0 register contract and is meaningful only with the matching register offset header:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`
- AMD Display Core register helper infrastructure that turns register and field names into shift/mask table entries.

Observed local include points for this header include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn30/dcn30_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn30/irq_service_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn302/irq_service_dcn302.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn30.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn302.c`

Other integration points are the generic HUBBUB/HUBP/DPP/cursor and DMUB command definitions. For example, cursor fields from `CURSOR0_0_CURSOR_CONTROL` are represented in `display/dc/dpp/dcn30/dcn30_dpp.h` and `display/dmub/inc/dmub_cmd.h`, while DCHUBBUB arbitration watermarks are used through HUBBUB field tables in display hub code.

Cross-generation headers such as `dcn_3_2_0_sh_mask.h`, `dcn_3_5_1_sh_mask.h`, and `dcn_4_1_0_sh_mask.h` contain similar names but not always identical fields. Copying masks or assumptions between generations is risky; for example, later cursor control blocks add fields not present in this DCN 3.0.0 slice.

## Risks And Edge Cases

- Wrong shifts or masks compile cleanly but can silently program the wrong display/audio bits. Highest-risk fields include VM page-table bases/ranges, default/fault addresses, surface and metadata addresses, DCC/TMZ enables, DMA snoop/isochronous attributes, flip controls, interrupt clears, memory power controls, and clock/reset fields.
- Chunk boundaries split related performance-monitor blocks. `DC_PERFMON4` is incomplete at the start of this slice and `DC_PERFMON6` is incomplete at the end, so isolated reasoning can miss counter-control fields.
- Address fields are split across low 32-bit and high narrow masks, often 16-bit or 4-bit high fragments. Treating high and low halves uniformly can truncate physical, metadata, VM, cursor, DMDATA, or fault addresses.
- Repeated instance/index windows are easy to mix up. Azalia endpoints/input endpoints, stream 8-15 windows, VM contexts 0-15, VTG0-5 controls, DCC constant pairs, and pipe security-level fields rely on exact prefix matching.
- Status, clear, ack, and interrupt-mask fields frequently share registers. Generic read-modify-write sequences can accidentally acknowledge events, clear sticky status, or fail to clear an event if the mask is stale.
- HUBP/HUBPREQ/HUBPRET timing fields are tightly packed and mode-sensitive. Bad request sizing, TTU, prefetch, vblank, flip, nominal, per-line delivery, read-line, or watermark values can produce underflow, timeout, tearing, missed flips, or display blanking only under specific modes.
- VM and security fields interact with GPUVM, HostVM, TMZ, DCC metadata, cursor, and DMDATA fetches. Incorrect fields may surface as page faults, protected-content failures, corrupted scanout, or forced-I/O status captures rather than simple validation errors.
- Azalia DMA and clock/power fields affect audio stream delivery and power transitions. Incorrect values can cause underflow filler behavior, lost interrupts, bad payload reporting, or audio dropouts.
- Full-width masks such as `0xFFFFFFFFL` should stay inside existing 32-bit register helper paths to avoid signedness or width surprises in ad hoc code.

## Test Signals

Useful validation signals for code that consumes this chunk include:

- Build coverage for DCN30/DCN302 Display Core and DMUB sources that include `dcn_3_0_0_sh_mask.h`.
- Static generated-header validation that every intended field has matching `__SHIFT` and `_MASK` definitions, masks align with shifts and field widths, and repeated families remain consistent where the hardware spec requires it.
- Diff checks against the authoritative DCN 3.0.0 register database and the matching `dcn_3_0_0_offset.h`, especially around the `DC_PERFMON4` and `DC_PERFMON6` chunk boundaries.
- Modeset and multi-plane tests on DCN 3.0 hardware with luma/chroma formats, DCC-enabled surfaces, TMZ-protected surfaces, metadata address changes, rotations/mirroring, alpha-plane state, and viewport changes on HUBP0.
- Flip tests covering update locks, immediate and vupdate-synchronized flips, pending/min-time behavior, triple-buffer/GSL bits, in-use/earliest-in-use readbacks, and flip/flip-away interrupt status/clear handling.
- VM tests that exercise multiple VMIDs and contexts, page-table ranges, default-address behavior, display VM faults, forced-I/O status capture, HostVM/security levels, and protected cursor/DMDATA/surface fetches.
- HUBBUB watermark, DRAM-state, timeout, soft-reset, clock-gating, memory-power, suspend/resume, and runtime power-management tests that verify status bits converge and no underflow/timeout bits remain stuck.
- Cursor and DMDATA tests for movement, hotspot, size, stereo offsets, TMZ/system/snoop attributes, software DMDATA injection, QoS, underflow clear, and memory power transitions.
- Azalia/HD-audio tests for stream setup, DMA snoop/isochronous configuration, cyclic buffer position/sync, payload capability reporting, codec power/reset, DTO programming, CRC/debug readback, and audio through suspend/resume.
- Diagnostic tests for DCHUBBUB and Azalia CRC, FMON, DC performance monitors, timeout interrupts, vblank/read-line interrupts, and surface-check registers.

## Chunk Notes

This is generated register metadata rather than functional logic. The main research value is the hardware coverage map and risk profile: display audio control, DCHUBBUB memory/VM/arbitration/security, HUBP0 scanout and flip sequencing, return-path/read-line interrupts, cursor/DMDATA fetches, and performance diagnostics. The merge lane should combine this with neighboring chunks before presenting complete per-file coverage for `dcn_3_0_0_sh_mask.h`.
