# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h lines 7454-9969

## Scope

This chunk is part of AMD DCN 3.6 generated ASIC register metadata. It contains C preprocessor definitions for register-field bit shifts and masks, not executable code. The covered range starts in the `dce_dc_dchubbubl_hubbub_sdpif_dispdec` block after `DCHUBBUB_SDPIF_CFG0`, continues through DCHUBBUB return path, VM request, DC perfmon, HUBP0/HUBPREQ0/HUBPRET0/CURSOR0_0, and ends at the beginning of HUBPREQ1 VM aperture definitions.

The definitions are consumed by AMD display driver register-list and field-list macros. Adjacent integration code maps register offsets from `dcn_3_6_0_offset.h` and shift/mask symbols from this header into typed register tables used by `REG_GET`, `REG_UPDATE`, `REG_UPDATE_2`, and related accessor macros.

## Purpose

The purpose of this header range is to encode the hardware contract for selected DCN 3.6 display hub fields:

- DCHUBBUB SDPIF and VM address aperture programming, including SDP request status, credit control, pipe security levels, no-allocation flags, physical request controls, and local HBM lock range fields.
- DCHUBBUB return-path memory power, CRC, DCC statistics, compression buffer, DET buffer, debug, and memory power mode/status fields.
- DCN VM context registers for contexts 0-15, default addresses, fault controls, fault status, and fault address capture.
- DC performance monitor 6 fields.
- HUBP0 surface, tiling, viewport, request sizing, control, clock, virtual memory page, MALL, measurement, and MALL status fields.
- HUBPREQ0 surface address, metadata address, surface control, flip sequencing, flip interrupts, in-use tracking, TTU/QoS, VM/aperture, timing/prefetch/delivery, cursor settings, memory power, pstate, and status fields.
- HUBPRET0 read-return control, memory power, read-line, and interrupt fields.
- CURSOR0_0 cursor control, surface address, size, position, hot spot, stereo, memory power, and DMData fields.
- DC performance monitor 7 fields.
- HUBP1 surface/control fields and the first part of HUBPREQ1, through `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_HIGH_ADDR`.

This is source-tree-aligned low-level display metadata. Its correctness determines whether higher-level DCN 3.6 driver code writes the intended bits when programming display memory fetch, VM, cursor, CRC, performance counters, and power controls.

## Important APIs, Types, And Macros

There are no C functions or types declared in this chunk. The important interface is the naming convention for generated preprocessor symbols:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a hardware field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask within the 32-bit MMIO register.
- Register group comments such as `//HUBPREQ0_DCSURF_FLIP_CONTROL` and address-block comments divide the generated definitions into hardware blocks.

Important register families in this chunk include:

- `DCHUBBUB_SDPIF_CFG1`, `DCHUBBUB_SDPIF_CFG2`, `DCHUBBUB_SDPIF_PIPE_*`, and `SDPIF_REQUEST_RATE_LIMIT` for display fabric request behavior.
- `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, `DCN_VM_CONTEXT{0..15}_*`, `DCN_VM_DEFAULT_ADDR_*`, `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and `DCN_VM_FAULT_ADDR_*` for display VM and fault reporting.
- `DCHUBBUB_CRC_CTRL`, `DCHUBBUB_CRC0_VAL_*`, and `DCHUBBUB_CRC1_VAL_*` for hub CRC capture.
- `DCHUBBUB_DCC_STAT*`, `DCHUBBUB_COMPBUF_CTRL`, `DCHUBBUB_DET{0..3}_CTRL`, `DCHUBBUB_MEM_PWR_MODE_CTRL`, `DCHUBBUB_MEM_PWR_STATUS`, and `COMPBUF_MEM_PWR_CTRL_*` for compression, DET, and memory power state.
- `DC_PERFMON6_*` and `DC_PERFMON7_*` for performance-counter control, state, counter values, high/low count latches, and interrupt/status fields.
- `HUBP0_*` and `HUBP1_*` for hub pipe surface format, tiling, viewport, request size, underflow/status/control, clock gating, VMPG, MALL, and measurement windows.
- `HUBPREQ0_*` and `HUBPREQ1_*` for surface pitch/address/control, flips, VM, TTU/QoS, prefetch, vblank/nominal/flip parameters, per-line delivery, cursor settings, memory power, pstate force, and status.
- `HUBPRET0_*` for hub pipe return path control and interrupts.
- `CURSOR0_0_*` for cursor plane setup and DMData.

The key consumers are display driver macros and structures such as `HUBBUB_REG_LIST_DCN35`, `HUBBUB_MASK_SH_LIST_DCN35`, `HUBP_MASK_SH_LIST_DCN35`, and older inherited HUBP/HUBBUB mask lists. For DCN 3.6, `dcn36_resource.h` includes `DCHUBBUB_CRC_CTRL` in `HWSEQ_DCN36_REG_LIST()`, while `dcn35_hubbub.h` lists many DCHUBBUB registers present in this chunk, including `DCN_VM_FB_LOCATION_*`, `DCN_VM_AGP_*`, `DCHUBBUB_DET*`, `DCHUBBUB_COMPBUF_CTRL`, `DCN_VM_FAULT_*`, `SDPIF_REQUEST_RATE_LIMIT`, `DCHUBBUB_SDPIF_CFG0`, `DCHUBBUB_SDPIF_CFG1`, and memory/power/debug registers. HUBP inherited lists in `dcn10_hubp.h`, `dcn20_hubp.h`, `dcn30_hubp.h`, `dcn31_hubp.h`, `dcn32_hubp.h`, and `dcn35_hubp.h` consume fields like `HUBP0_DCHUBP_CNTL`, `HUBPREQ0_DCSURF_SURFACE_CONTROL`, `CURSOR0_0_CURSOR_CONTROL`, `HUBPREQ0_UCLK_PSTATE_FORCE`, and `HUBP0_DCHUBP_MALL_CONFIG`.

## Control Flow

This chunk has no runtime control flow. Its definitions influence control flow indirectly when driver code expands register accessor macros:

- Initialization paths such as `hubbub35_init()` update SDPIF fields. For example, the driver writes `DCHUBBUB_SDPIF_CFG0.SDPIF_PORT_CONTROL` and `DCHUBBUB_SDPIF_CFG1.SDPIF_MAX_NUM_OUTSTANDING`; the bit positions and masks for those fields come from this header range.
- HUBP programming paths use inherited field-list macros to program surface configuration, DCC/TMZ flags, tiling, viewport, cursor, TTU, VM, and flip state through `REG_UPDATE`-style wrappers.
- VM fault state paths use the `DCN_VM_FAULT_CNTL` and `DCN_VM_FAULT_STATUS` fields to clear errors, choose status mode, enable interrupts, and read/write fault indicators.
- CRC and perfmon paths use these masks to enable capture, select sources, latch one-shot/continuous counters, read values, and clear status bits.

The runtime sequence is therefore: a DCN resource constructor selects DCN 3.6 offset and shift/mask tables; component constructors store pointers to those tables; later display programming calls pass register and field names to accessor macros; the generated shifts and masks here are used to isolate or compose field values in MMIO writes and reads.

## State And Persistence Behavior

The file itself persists no software state. It describes persistent hardware register state across several domains:

- Control fields such as `SDPIF_PORT_CONTROL`, `SDPIF_FORCE_SNOOP`, `DCHUBBUB_CRC_EN`, `DCHUBBUB_CRC_CONT_EN`, HUBP blank/disable/underflow controls, cursor enable/mode, MALL selection, VMPG settings, TTU/QoS, and VM L1 TLB controls remain in hardware until reprogrammed, reset, or power-gated.
- Status and sticky fields include SDPIF response/credit errors, force-IO status, DCC stats, memory power status, VM fault status/address, perfmon status/counter values, HUBP underflow/no-outstanding/status, flip occurred/status bits, HUBPRET interrupt status, and cursor DMData status.
- Clear fields such as `SDPIF_RESPONSE_STATUS_CLEAR`, `SDPIF_REQ_CREDIT_ERROR_CLEAR`, `DCN_VM_ERROR_STATUS_CLEAR`, `DMDATA_VM_FAULT_STATUS_CLEAR`, `DMDATA_VM_UNDERFLOW_STATUS_CLEAR`, `SURFACE_FLIP_CLEAR`, `SURFACE_FLIP_AWAY_CLEAR`, and several interrupt clear fields are write-sensitive. Incorrect masks can fail to clear a latched fault or accidentally clear unrelated status.
- Address and VM fields store page table base/start/end, system aperture boundaries, surface addresses, metadata addresses, cursor surface addresses, and in-use address captures. These values persist as programmed display fetch state and must match current plane/cursor memory layout and VMID ownership.
- Power-control fields represent forced memory power modes, shutdown enables, request/ack/status, and clock-gating replication disable bits. Misprogramming can leave blocks powered unexpectedly or inaccessible during display updates.

## Dependencies And Integration Points

Primary dependencies:

- `dcn_3_6_0_offset.h` supplies register offsets and base indices that pair with the shift/mask symbols in this file.
- AMD DC register access macros in the display stack require exact symbol names. Macros such as `SR`, `SRII`, `HUBBUB_SF`, `HUBP_SF`, and `TF_SF` expand register and field names into structure initializers that depend on these generated defines existing.
- DCN 3.5 and earlier component code is reused by DCN 3.6 in places. The chunk is therefore integrated through inherited DCN 3.x HUBBUB and HUBP field lists, not just files named `dcn36`.
- DMUB and hardware sequencer code interacts with cursor and hub state. `dmub_cmd.h` mirrors cursor control bitfields, and DCN 3.5/4.0 hardware sequencer code serializes cursor state using fields with names matching `CURSOR0_0_CURSOR_CONTROL`.

Concrete integration examples in this tree:

- `display/dc/resource/dcn36/dcn36_resource.h` includes `DCHUBBUB_CRC_CTRL` in the DCN 3.6 hardware sequencer register list.
- `display/dc/hubbub/dcn35/dcn35_hubbub.h` lists DCHUBBUB registers from this chunk and maps additional masks through `HUBBUB_MASK_SH_LIST_DCN35`.
- `display/dc/hubbub/dcn35/dcn35_hubbub.c` writes `DCHUBBUB_SDPIF_CFG0.SDPIF_PORT_CONTROL` and `DCHUBBUB_SDPIF_CFG1.SDPIF_MAX_NUM_OUTSTANDING` during hubbub initialization.
- `display/dc/hubp/dcn35/dcn35_hubp.h` inherits DCN 3.2/3.1/3.0 HUBP fields and adds DCN 3.5 clock-gating fields; the inherited field lists consume many `HUBP0_*`, `HUBPREQ0_*`, and `CURSOR0_0_*` symbols defined in this chunk.
- `display/dc/hubbub/dcn20/dcn20_hubbub.c` reads `DCN_VM_FAULT_CNTL.DCN_VM_ERROR_STATUS_MODE`, relying on the VM fault field definitions shared by later generations.

## Risks

- Generated-header drift is high impact. If a shift or mask mismatches DCN 3.6 hardware, the driver can write the wrong field while compiling cleanly.
- Cross-generation reuse increases copy/paste risk. Nearby DCN 3.2, 3.5.1, and DCN 3.6 headers contain similar field names, but some fields differ, such as the `DF_CSTATE_DISALLOW` bit in `DCHUBBUB_SDPIF_CFG0` for this chunk. Reusing a different-generation mask table can subtly alter power or fabric behavior.
- Status-clear fields are especially sensitive. A one-bit mask error can leave sticky VM/fabric/flip/interrupt status uncleared, or can clear an adjacent diagnostic bit and hide a real fault.
- Address high/low fields, VM context bounds, VMID fields, and in-use capture fields span multiple registers. Incorrect field widths can truncate addresses, point display fetches at the wrong memory, or make fault reports misleading.
- HUBPREQ surface-control fields combine TMZ, DCC enable, DCC independent block, and metadata TMZ state for primary/secondary surfaces. Incorrect masks can break protected content, DCC metadata fetch, or chroma plane setup.
- HUBP/HUBPREQ0 and HUBP/HUBPREQ1 symmetry is easy to damage. Instance-specific prefixes must keep the same field layout where hardware expects replicated pipes, but the chunk ends mid-HUBPREQ1, so merge/reconciliation must combine this with the following chunk before making whole-file conclusions.
- Memory power and clock-gating fields can interact with display underrun behavior. Wrong force/shutdown/status masks could cause intermittent blanking, underflow, or resume failures that only appear under low-power or multi-plane workloads.
- Perfmon fields are broad and include many selector/status bits. A mismatch may not affect normal display output but can invalidate performance diagnostics or automated telemetry.

## Test Signals

Useful validation signals for changes touching this header or its generator:

- Compile coverage for DCN 3.6 display code with all generated register lists enabled. Missing or renamed shift/mask symbols should fail during structure initialization or macro expansion.
- Boot/probe smoke tests on DCN 3.6 hardware, confirming resource creation, hubbub/HUBP construction, and display bring-up without MMIO access faults.
- Display plane tests covering primary and secondary surfaces, DCC enabled/disabled, chroma planes, cursor enable/move/resize, page flips, triple buffering, and stereo/GSL flip paths. These exercise `HUBPREQ*_DCSURF_*`, `HUBP*_DCSURF_*`, `CURSOR0_0_*`, and flip interrupt fields.
- VM and fault-injection tests covering invalid surface addresses, VMID changes, page table base/start/end programming, aperture low/high bounds, and fault clear/readback through `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and fault address registers.
- Low-power and clock-gating tests across idle, blanking, PSR/sub-VP/MALL, resume, and zero-frame-buffer paths. These exercise SDPIF, HUBP/HUBPREQ/HUBPRET memory power, MALL, and pstate force fields.
- CRC tests that enable one-shot and continuous hub CRC capture, select pipe/surface/data source, and compare `DCHUBBUB_CRC{0,1}_VAL_*` readback against expected frame contents.
- Performance-counter diagnostics using `DC_PERFMON6_*` and `DC_PERFMON7_*`, including start/stop, counter selection, interrupt status, counter clear, and high/low readback.
- Regression comparison against vendor-generated headers for the same ASIC revision. For this kind of file, a mechanical diff against trusted register XML/header output is often the strongest signal.

## Notes For Merge Lane

This chunk should be merged with the adjacent `dcn_3_6_0_sh_mask.h` chunks before producing the final per-file report. The range begins after the `DCHUBBUB_SDPIF_CFG0` comment and ends mid-HUBPREQ1, at `HUBPREQ1_DCN_VM_SYSTEM_APERTURE_HIGH_ADDR`, so both boundaries are partial register-block boundaries. Whole-file analysis should account for earlier DCHUBBUB arbitration/global timer fields and later HUBPREQ1/HUBP2+ replicated pipe definitions.
