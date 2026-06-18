# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_sh_mask.h lines 7582-10080

## Scope

This chunk is a middle slice of the generated DCN 3.2.0 register shift/mask header `dcn_3_2_0_sh_mask.h`. It contains C preprocessor constants only: `_SHIFT` macros for register-field low-bit positions, `_MASK` macros for raw in-register field masks, register comments, and generated `// addressBlock:` markers. There are no functions, structs, enums, branches, loops, allocations, or direct software state transitions in this range.

The slice starts at the tail of `HUBPRET0_HUBPRET_READ_LINE_STATUS`, then covers the full `CURSOR0_0` cursor block, the full HUBP/HUBPREQ/HUBPRET/CURSOR field families for pipe instances 1 and 2, and the beginning of instance 3 through `HUBPREQ3_PREFETCH_SETTINGS__DST_Y_PREFETCH__SHIFT`. The next chunk is required to finish the `HUBPREQ3_PREFETCH_SETTINGS` masks and the remaining instance-3 request timing fields.

This file is generated hardware-description data. The API surface is the macro namespace, not executable behavior. Runtime behavior appears when AMD Display Core combines these shift/mask constants with matching register offsets from `dcn_3_2_0_offset.h` and MMIO helper macros such as `REG_GET`, `REG_SET`, `REG_UPDATE`, `REG_WRITE`, `REG_FIELD`, `FD_MASK`, `FD_SHIFT`, `SF`, and `DMUB_SF`.

## Purpose And Hardware Surface

The purpose of this chunk is to describe bit layouts for DCN 3.2 HUBP-related display pipe registers. HUBP is the hub pipe front end that fetches scanout surfaces, metadata, cursor data, and display metadata from memory and feeds later display pipe stages. Companion offset headers define where each register lives; this header defines how software packs writes and decodes readbacks.

Major hardware areas represented here:

- `HUBPRET0` read-line status tail fields for vblank and read-line window membership.
- `CURSOR0_0`, `CURSOR0_1`, and `CURSOR0_2` cursor control, address, size, position, hot spot, stereo, destination offset, memory power, and display metadata data paths.
- `HUBP1`, `HUBP2`, and the beginning of `HUBP3` hub pipe configuration for surface format, tiling, address swizzle, viewports, request sizes, blank/reset/control, clock gating, VM page configuration, MALL use, SubVP MALL start lines, measurement windows, and MALL status.
- `HUBPREQ1`, `HUBPREQ2`, and the beginning of `HUBPREQ3` request-side surface addressing, metadata addressing, surface control, flip control, flip interrupts, in-use address tracking, request expansion, TTU/QoS programming, DMDATA VM control, VM aperture and L1 TLB configuration, blanking offsets, destination timing, and prefetch setup.
- `HUBPRET1` and `HUBPRET2` return-side DET/crossbar controls, memory power controls, read-line compare windows, vblank/read-line interrupts, current read-line values, and read-line status.

The repeated instance naming is intentional. `HUBP1_*`, `HUBPREQ1_*`, `HUBPRET1_*`, and `CURSOR0_1_*` describe pipe instance 1, while `HUBP2_*` and `HUBP3_*` describe later instances with the same field layout. Consumers usually bind these instance-specific macros into per-pipe register tables instead of hand-selecting macros by name.

## Important Definitions

The exported API follows the generated AMD register-field convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit of a field.
- `<REGISTER>__<FIELD>_MASK` gives the raw field mask in the 32-bit register.
- `//<REGISTER>` comments group the fields by hardware register.
- `// addressBlock: <block>` comments identify the generated hardware address block for the following registers.

The cursor blocks define the field ABI for hardware cursors and cursor-associated display metadata:

- `CURSOR0_x_CURSOR_CONTROL` contains enable, request mode, 2x magnification, cursor mode, TMZ, pitch, rotation/mirroring bypass, and lines-per-chunk fields.
- `CURSOR0_x_CURSOR_SURFACE_ADDRESS` and `_HIGH` split the cursor surface address into low 32 bits and high 16 bits.
- `CURSOR0_x_CURSOR_SIZE`, `POSITION`, `HOT_SPOT`, `STEREO_CONTROL`, and `DST_OFFSET` encode cursor dimensions, signed/position-like X/Y fields, hot spot coordinates, stereo offsets, and destination X offset.
- `CURSOR0_x_CURSOR_MEM_PWR_CTRL` and `_STATUS` expose cursor ROB memory power force/disable/low-power state controls and state readback.
- `CURSOR0_x_DMDATA_*` defines a separate display-metadata path: low/high address, TMZ, update/repeat/mode/size control, QoS mode/level/deadline delta, done/underflow/clear status, software-updated metadata control, and 32-bit software metadata data.

The HUBP blocks define surface geometry and hub pipe local behavior:

- `HUBP*_DCSURF_SURFACE_CONFIG` packs pixel format, rotation, horizontal mirror, and alpha-plane enable.
- `HUBP*_DCSURF_ADDR_CONFIG` and `HUBP*_DCSURF_TILING_CONFIG` describe address decomposition, pipe interleave, compressed fragment limits, packers, swizzle mode, dimension type, meta-linear mode, and pipe alignment.
- Primary and secondary viewport start/dimension registers exist for both luma/data and chroma planes via `_C` suffixed fields.
- `HUBP*_DCHUBP_REQ_SIZE_CONFIG` and `_C` encode swath height, PTE row height, chunk sizes, meta chunk sizes, DPTE group size, and VM group size for data and chroma fetches.
- `HUBP*_DCHUBP_CNTL` contains blanking, no-outstanding-request status, soft reset, VTG select, vready, VM stop-data behavior, unbounded request mode, segment allocation error status, TTU disable/mode, timeout status/threshold/clear/interrupt, and underflow status/clear.
- `HUBP*_HUBP_CLK_CNTL` exposes hub pipe clock enable, gate disables, clock-on status bits, fine-grain clock-gating repeat disable, and test clock select.
- `HUBP*_DCHUBP_VMPG_CONFIG`, `MALL_CONFIG`, `MALL_SUB_VP`, and `HUBP_MALL_STATUS` define VM page behavior, MALL routing for surfaces/cursor, SubVP MALL line selection, and status bits for static-screen or p-state MALL use, prefetch/retrieve progress, busy request queues, one-row-for-frame mode, and outstanding MALL activity.
- `HUBP*_HUBP_MEASURE_WIN_CTRL_DCFCLK` and `_DPPCLK` define measurement window enable/source/period/mode fields used for clock-domain measurement or diagnostics.

The HUBPREQ blocks define the request-side fetch and flip ABI:

- `HUBPREQ*_DCSURF_SURFACE_PITCH` and `_C` pack surface and metadata pitch for data and chroma planes.
- `HUBPREQ*_VMID_SETTINGS_0` contains the VMID for memory accesses.
- Primary/secondary surface and metadata address registers are split into low 32-bit and high 16-bit fields, with `_C` variants for chroma.
- `HUBPREQ*_DCSURF_SURFACE_CONTROL` packs TMZ, DCC enable, DCC independent block selection, and metadata TMZ state for primary and secondary luma/chroma planes.
- `HUBPREQ*_DCSURF_FLIP_CONTROL`, `FLIP_CONTROL2`, and `SURFACE_FLIP_INTERRUPT` define update lock, flip type, vupdate skip count, pending status, master update lock status, stereo sync mode, pending delay/min time, GSL, triple buffering, in-use read latch behavior, interrupt mask/type/clear/status, and flip-away interrupt status.
- `HUBPREQ*_DCSURF_SURFACE_INUSE`, `_EARLIEST_INUSE`, and their high/chroma variants expose low/high address and VMID readback for the currently or earliest in-use surface.
- `HUBPREQ*_DCN_EXPANSION_MODE`, `DCN_TTU_QOS_WM`, `DCN_GLOBAL_TTU_CNTL`, and the `DCN_SURF*` / `DCN_CUR*` TTU registers program request expansion and time-to-use/QoS behavior for data surfaces and cursors.
- `HUBPREQ*_DCN_DMDATA_VM_CNTL` defines DMDATA VM reference cycles, fault status/clear, underflow/late status, underflow clear, and done state.
- `HUBPREQ*_DCN_VM_SYSTEM_APERTURE_*` and `DCN_VM_MX_L1_TLB_CNTL` define system aperture low/high addresses, L1 TLB enable, system access mode, unmapped access behavior, and advanced driver model enable.
- Timing and request scheduling registers include blank offsets, destination dimensions, destination-after-scaler position, prefetch settings, vblank parameters, flip parameters, nominal parameters, per-line delivery values, cursor settings, reference-frequency-to-pixel-frequency ratio, destination-Y DRQ limit, UCLK p-state force, and request/status registers.

The HUBPRET blocks define return-side composition and line interrupt behavior:

- `HUBPRET*_HUBPRET_CONTROL` contains DET buffer plane base, 3-to-2 packing disable, crossbar source selection for alpha/Y/Cb/Cr, and spare bits.
- `HUBPRET*_HUBPRET_MEM_PWR_CTRL` and `_STATUS` expose DMROB and PIXCDC memory power force/disable/low-power and state readbacks.
- `HUBPRET*_HUBPRET_READ_LINE_CTRL0/1`, `READ_LINE0/1`, `READ_LINE_VALUE`, and `READ_LINE_STATUS` define read-line intervals, compare windows, snapshot/current line readback, vblank status, and inside/outside window status.
- `HUBPRET*_HUBPRET_INTERRUPT` exposes masks, interrupt types, clear bits, raw status, and interrupt status for vblank plus two read-line interrupt windows.

## Control Flow And State Behavior

There is no executable control flow in this header. The runtime flow is generated-register-table driven:

1. DCN 3.2 display code includes `dcn_3_2_0_offset.h` and `dcn_3_2_0_sh_mask.h`.
2. Register-list macros bind offset symbols such as `regHUBP1_*`, `regHUBPREQ2_*`, or `regCURSOR0_1_*` to the corresponding shift/mask symbols in this file.
3. DC, DMUB, IRQ, clock, resource, HUBP, cursor, and GPIO-related code uses register helpers to read, update, or write MMIO fields.
4. Hardware latches persistent configuration fields, returns live status/debug/telemetry fields, or triggers side effects such as status clears and interrupts.

State represented here is hardware state rather than software-owned persistence:

- Persistent or semi-persistent configuration fields include cursor enable/mode/pitch/TMZ/address/size/hot spot, DMDATA address/mode/size/QoS, surface format/tiling/viewport/request sizing, VMID, surface and metadata addresses, TMZ/DCC controls, flip mode, GSL/triple buffering, TTU/QoS, VM aperture/TLB settings, MALL routing, SubVP MALL line configuration, read-line windows, interrupt masks/types, memory power controls, and clock-gating controls.
- Volatile telemetry fields include no-outstanding-request status, in-blank state, underflow and timeout status, clock-on status, MALL status, flip pending and interrupt status, in-use and earliest-in-use addresses, DMDATA VM fault/underflow/late/done status, hub request status registers, read-line current/snapshot values, vblank/read-line status, memory power states, and MALL busy/outstanding indicators.
- Side-effecting or sequencing-sensitive fields include soft reset, timeout status clear, underflow clear, surface update lock, flip clear/away clear, DMDATA VM fault and underflow clears, cursor/DMDATA update bits, memory power force/disable fields, clock enable/gating fields, and read-line/vblank interrupt clear bits.

The macros do not encode ordering. Callers must still respect the display pipe power state, clock state, VM/TLB setup, DCC and TMZ security requirements, flip/update-lock sequencing, cursor address validity, vblank timing, MALL/SubVP programming constraints, and any hardware-specific rules around clearing sticky status or enabling interrupts.

## Dependencies And Integration Points

This chunk depends on the matching DCN 3.2.0 offset header at `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_2_0_offset.h`. The offset header supplies register addresses and base indices; this file supplies field masks and shifts. A mismatch between the two can compile while producing incorrect MMIO writes or bogus readback decoding.

Direct include sites for the generated DCN 3.2.0 offset and shift/mask headers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn32.c`, where `dmub_srv_dcn32_regs_init()` populates DMUB register offsets, masks, and shifts via `DMUB_DCN32_REGS()` and `DMUB_DCN32_FIELDS()`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn32/irq_service_dcn32.c`, where DCN 3.2 interrupt service code maps source IDs such as HUBP flip interrupts, vblank, vline, vupdate, HPD, HPDRX, and DMCUB outbox sources into DAL IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn32/dcn32_resource.c`, which builds the DCN 3.2 resource pool and per-block register structures for HUBP, DPP, OPTC, DIO, HPO, APG, audio, AUX/I2C, VMID, and related display resources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn32/dcn32_clk_mgr.c`, which consumes generated register field definitions for DCN 3.2 clock manager programming and readback.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.c` and `hw_translate_dcn32.c`, which bind DCN 3.2 GPIO, HPD, DDC, and AUX hardware definitions to generated register data.

Functional integration points for this specific chunk include:

- HUBP constructors and hardware sequencing, where per-instance HUBP/HUBPREQ/HUBPRET macros are assembled into register tables used for scanout fetch, cursor programming, surface flips, MALL/SubVP behavior, VM setup, and underflow/timeout handling.
- Page-flip and IRQ handling, where `HUBPREQ*_DCSURF_SURFACE_FLIP_INTERRUPT` and related flip pending/status fields are part of the hardware ABI behind DCN 3.2 page flip events.
- Cursor update paths, where `CURSOR0_x_*` fields program cursor image memory, size, position, hot spot, stereo offsets, TMZ state, and DMDATA sideband metadata.
- Display mode validation and programming paths, where DML-derived swath, chunk, PTE, meta, prefetch, vblank, flip, nominal, TTU, QoS, and per-line delivery values are written through these masks.
- Power management paths, where clock gating, memory power, MALL, p-state force, self-refresh allowance, and status fields are used to coordinate low-power entry and exit with active display pipes.
- DMUB firmware-service paths, because the generated masks and shifts are copied into DMUB-visible DCN32 register tables during `dmub_srv_dcn32_regs_init()`.

## Risks And Maintenance Notes

- Generated-header drift is the primary risk. Wrong numeric shifts or masks can compile cleanly but corrupt MMIO programming for surface addresses, DCC/TMZ state, cursor data, flip timing, TTU/QoS, VM/TLB settings, MALL behavior, or interrupt clears.
- This chunk has partial boundaries. It starts after the beginning of the `HUBPRET0` block and ends before the masks for `HUBPREQ3_PREFETCH_SETTINGS`; file-level reports must merge adjacent chunks before claiming completeness for pipe 0 or pipe 3.
- The repeated instance layout makes copy/paste mistakes easy. A valid `HUBP2_*` field used with a `HUBP1_*` offset, or a `CURSOR0_2_*` mask used with pipe 1, can silently target the wrong pipe or decode the wrong register value.
- Many low/high address registers split addresses into 32-bit low and 16-bit high fields. Incorrect reconstruction, truncation, or VMID association can point scanout, cursor, or metadata fetches at the wrong physical/virtual address.
- TMZ and DCC fields appear on primary, secondary, chroma, and metadata surfaces. Mixing data-plane and chroma-plane fields can cause security attribute mismatches, decompression faults, blank output, or underflow.
- Several fields are status-plus-clear patterns. Writing clear bits such as underflow clear, timeout status clear, flip clear, flip-away clear, DMDATA fault clear, DMDATA underflow clear, or read-line/vblank interrupt clear must avoid clobbering neighboring mask/type/status fields.
- Flip programming is timing-sensitive. `SURFACE_UPDATE_LOCK`, pending delay/min time, stereo sync, GSL, triple buffering, in-use latch behavior, and flip interrupt bits must be coordinated with vupdate/vblank and current pipe ownership.
- MALL/SubVP fields are power and memory-system sensitive. Misprogramming MALL use, SubVP start lines, one-row-for-frame behavior, or p-state/self-refresh status interpretation can produce intermittent underflow or memory power regressions.
- Clock and memory power fields can make subsequent register programming unreliable if the block is gated, reset, or in low-power state. The header cannot express these sequencing requirements.
- The `HUBPREQ*_HUBPREQ_STATUS_REG2` fields are repeated for surface 0, surface 1, and cursor status groups plus global pipe state. Consumers should avoid treating transient status bits as stable policy without checking pipe state and timing.

## Test Signals

High-signal validation for changes touching this chunk includes:

- Compile coverage for AMDGPU Display Core with DCN 3.2 enabled. Missing or malformed macros should surface in `dmub_dcn32.c`, `irq_service_dcn32.c`, `dcn32_resource.c`, `dcn32_clk_mgr.c`, and DCN32 GPIO/translation code.
- Static comparison against the authoritative DCN 3.2 register database or a regenerated `dcn_3_2_0_sh_mask.h`, especially for repeated HUBP/HUBPREQ/HUBPRET/CURSOR instance fields.
- Cross-revision spot checks against nearby generated headers such as DCN 3.1.x, DCN 3.2.1, and DCN 3.5.x where HUBP fields are expected to be compatible, while preserving intentional DCN 3.2.0 differences.
- Display smoke tests on DCN 3.2 hardware with multiple active pipes: modeset, page flip, cursor move/update, plane enable/disable, suspend/resume, hotplug, and vblank/vline interrupt delivery.
- Plane and cursor stress tests using rotations, mirroring, alpha-plane configurations, DCC-enabled and DCC-disabled surfaces, chroma formats, TMZ-secured surfaces, metadata planes, and large cursor images.
- Underflow and timing diagnostics during bandwidth-heavy modes, multi-display modes, VRR/flip-heavy workloads, and p-state transitions. Expected signals are stable HUBP request status, no unexpected underflow/timeout bits, coherent flip pending/interrupt behavior, and no stuck update locks.
- MALL/SubVP validation using static-screen, p-state-change, cursor-local-fetch, and SubVP scenarios. Useful signals are correct MALL status transitions, no busy/outstanding bits left stuck, and no visible corruption during retrieve/prefetch transitions.
- VM/TLB and address-programming validation, including correct VMID, aperture, surface address, meta address, in-use address, and earliest-in-use address readbacks.
- Register-dump comparisons before and after cursor, flip, MALL, and timing operations. Masked writes should affect only intended fields, and readback decoding should match this header's shifts and masks.

## Open Questions For Merge

- The final per-file report should reconcile this chunk with the previous lines that define the start of `HUBPRET0` and with the following lines that finish `HUBPREQ3` and later pipe instances.
- This chunk documents generated field layout only. Any final behavioral claims about exact programming order, DML timing derivation, MALL/SubVP policy, or interrupt acknowledgment should be corroborated with the functional DCN32 source files that consume these macros.
