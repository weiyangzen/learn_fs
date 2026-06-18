# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_2_0_sh_mask.h lines 20257-22731

## Scope

This chunk is part of the generated DCN 4.2.0 ASIC shift/mask header for AMD display hardware. It contains preprocessor constants only. Every exported item is a `#define` for a hardware register field's `__SHIFT` bit offset or `_MASK` value; there are no C functions, structs, enums, branches, allocations, locks, or direct MMIO accesses in this range.

The line range covers 2,122 macro definitions: 1,061 `__SHIFT` definitions and 1,061 matching `_MASK` definitions. It starts inside the tail of the `HUBP1_DCHUBP_VMPG_CONFIG` register, completes the remaining HUBP1/HUBPREQ1/HUBPRET1/cursor/perfmon field metadata, covers the corresponding HUBP2/HUBPREQ2/HUBPRET2/cursor/perfmon metadata, and then begins the HUBP3/HUBPREQ3 sequence through `HUBPREQ3_DCSURF_SECONDARY_SURFACE_ADDRESS`.

The visible address blocks are:

- `dce_dc_dcbubp1_dispdec_hubpreq_dispdec`
- `dce_dc_dcbubp1_dispdec_hubpret_dispdec`
- `dce_dc_dcbubp1_dispdec_cursor0_dispdec`
- `dce_dc_dcbubp1_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_dcbubp2_dispdec_hubp_dispdec`
- `dce_dc_dcbubp2_dispdec_hubpreq_dispdec`
- `dce_dc_dcbubp2_dispdec_hubpret_dispdec`
- `dce_dc_dcbubp2_dispdec_cursor0_dispdec`
- `dce_dc_dcbubp2_dispdec_hubp_dcperfmon_dc_perfmon_dispdec`
- `dce_dc_dcbubp3_dispdec_hubp_dispdec`
- start of `dce_dc_dcbubp3_dispdec_hubpreq_dispdec`

## Purpose

The purpose of this chunk is to publish the exact bit layout for several repeated DCN 4.2 display pipe front-end blocks. Runtime driver code combines these field constants with companion register-offset constants to read and update hardware registers through AMD display register helpers. The chunk is silicon metadata, not driver logic.

The covered hardware themes are:

- HUBP front-end surface and viewport programming for pipes 2 and 3, plus the tail of pipe 1 MALL/debug/status metadata.
- HUBPREQ request-side surface address, pitch, VM, flip, timing, QoS, prefetch, memory-power, pstate-force, and status metadata for pipes 1 and 2, plus the beginning of pipe 3.
- HUBPRET return-side control, memory-power, read-line, interrupt, and status metadata for pipes 1 and 2.
- Cursor0 metadata for pipes 1 and 2, including cursor surface geometry, cursor memory power, display metadata transport, and HUBP 3D LUT programming.
- DC performance monitor metadata for perfmon instances 7 and 8.

These constants let higher-level DCN code avoid hard-coded bit arithmetic when configuring scanout, memory fetch, page-table traffic, cursor fetch, flip interrupts, MALL usage, display metadata, and performance counters.

## Important Macros and Field Families

The generated macro naming contract is the public API of this header:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the 32-bit register value.
- Prefixes such as `HUBPREQ1`, `HUBP2`, `CURSOR0_2`, and `DC_PERFMON8` bind otherwise repeated fields to a specific hardware instance.

Important families in this chunk include:

- `HUBP1_DCHUBP_MALL_*`, `HUBP2_DCHUBP_MALL_*`, and `HUBP3_DCHUBP_MALL_*`: select MALL use, cursor MALL use, sub-viewport MALL retrieval start lines, MALL request/response/in-use flags, local cursor retrieve/prefetch state, CRQ/MRQ/DRQ outstanding state, and one-row-for-frame status.
- `HUBP2_DCSURF_*` and `HUBP3_DCSURF_*`: surface format, rotation, horizontal mirror, swizzle, tiling, meta/independent block sizing, primary and secondary viewport start/dimension, chroma viewport start/dimension, request size, detile buffer heights, swath heights, chunk heights, minimum chunk sizes, pte row heights, and meta row heights.
- `HUBP2_DCHUBP_CNTL` and `HUBP3_DCHUBP_CNTL`: HUBP enable, blank enable, cursor enable, VM context selection, soft reset, timeout status/clear/interrupt enable, and underflow status/clear fields.
- `HUBP2_HUBP_CLK_CNTL` and `HUBP3_HUBP_CLK_CNTL`: HUBP clock enable, DISPCLK/DPPCLK/DCFCLK gate-disable and clock-on status fields, fine-grain clock-gating disable, and test clock selection.
- `HUBPREQ1_*` and `HUBPREQ2_*`: surface pitch, VMID, primary/secondary surface addresses, primary/secondary metadata addresses, TMZ/DCC surface controls, flip controls, flip interrupt controls, surface in-use latches, timing/QoS parameters, VM apertures, TLB controls, prefetch/vblank/flip/nominal delivery parameters, cursor delivery parameters, memory-power controls/status, pstate-force controls, and status registers.
- `HUBPRET1_*` and `HUBPRET2_*`: control fields for detile buffer address, crossbar source, DST_Y prefetch behavior, read-line enables/modes, read-line values, read-line status, and HUBPRET interrupt mask/type/clear/status/ack fields.
- `CURSOR0_1_*` and `CURSOR0_2_*`: cursor enable, request mode, 2x magnify, cursor mode, TMZ, pitch, rotation/mirroring bypass, lines per chunk, address, size, position, hot spot, stereo offsets, destination offset, cursor memory-power state, display metadata address/control/QoS/status/software data, and HUBP 3D LUT control/address/deadline fields.
- `DC_PERFMON7_*` and `DC_PERFMON8_*`: event selection, counter value selection, increment mode, run-enable, restart, interrupt enable/status/ack, counter state for eight counters, perfmon state, count-off controls, clock enable, run start/stop selection, captured values, and read selectors.
- `HUBPREQ3_DCSURF_*` at the end of the chunk: the first pipe-3 request-side fields for pitch, VMID, and primary surface address metadata; the rest of the pipe-3 HUBPREQ block continues in the next chunk.

## Control Flow and Runtime Integration

There is no executable control flow in this header. Runtime behavior is indirect:

1. DCN 4.2 source files include `dcn/dcn_4_2_0_offset.h` together with this `dcn/dcn_4_2_0_sh_mask.h` header.
2. Register table macros in DCN code pair address constants from the offset header with shift/mask constants from this header.
3. Helper macros such as `FD_MASK`, `FD_SHIFT`, `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and DMUB register-table expansion macros compose the actual read/modify/write operations.
4. The hardware-visible behavior occurs in the display engine registers; this header only supplies the compile-time field metadata used to generate correct register values.

Observed direct include sites for this header include DCN 4.2 resource construction, IRQ service mapping, GPIO translation/factory code, and DMUB register initialization. For example, `dmub_srv_dcn42_regs_init()` expands `DMUB_DCN42_FIELDS()` into masks and shifts using `FD_MASK(reg, field)` and `FD_SHIFT(reg, field)`, which depend on definitions from this file.

The represented programming flow for these fields is typically:

- Program HUBP surface format, viewport, tiling, request-size, and clock/enable state for a pipe.
- Program HUBPREQ surface addresses, metadata addresses, DCC/TMZ controls, VMID/aperture/TLB details, and delivery-time/QoS parameters.
- Arm or lock surface flips, control flip timing, then observe or clear flip interrupt/status bits.
- Program cursor state, cursor address/geometry, display metadata payloads, and optionally HUBP 3D LUT settings.
- Use HUBPRET and HUBPREQ status/read-line fields for synchronization and diagnostics.
- Use perfmon fields to select events, run counters, read captured values, and acknowledge counter interrupts.

## State and Persistence Behavior

The header owns no mutable state. All state represented by these macros lives in hardware registers and persists only according to the display engine's register-reset and power-state rules.

The represented hardware state includes:

- Surface state: format, rotation, swizzle, tiling, meta address mode, DCC enable, DCC independent block selection, primary/secondary surface addresses, meta-surface addresses, pitch, chroma pitch, viewport start and dimensions, and in-use/earliest-in-use address latches.
- Protection and compression state: TMZ bits for luma/chroma and primary/secondary metadata surfaces, plus DCC enable and DCC block-independence fields. Misprogramming these fields can affect protected memory access and decompression behavior.
- Flip state: update lock, flip type, vupdate skip count, pending status, stereo-sync mode, pending delay, minimum pending time, GSL enable/mask, triple-buffer enable, immediate-flip buffer tracking, flip interrupt masks/types, occurrence bits, status bits, and clear bits.
- VM and memory-fetch state: VMID, DMDATA VM controls, system aperture low/high addresses, L1 TLB policy, VM group/request timing during vblank and flip, PTE/meta chunk timing, pstate force bits, self-refresh status, QoS urgent status, and MPTE/chunk request progress.
- Power state: HUBP clock gates and clock-on status, HUBPREQ request SRAM power controls/status for DPTE/MPTE/meta/PDE/TPTE memories, HUBPRET detile-buffer memory power controls/status, and cursor CROB memory power controls/status.
- MALL state: selection of MALL use, cursor MALL use, sub-viewport MALL retrieval line selection, MALL prefetch/retrieve frame state, outstanding request state, and busy state across CRQ/MRQ/DRQ paths.
- Cursor and metadata state: cursor enable/mode/geometry, surface address, stereo offsets, hot spot, memory-power state, display metadata address, display metadata update/repeat/mode/size, QoS, done/underflow/clear status, software metadata data, and 3D LUT control/address/done state.
- Diagnostic state: HUBP debug mux selections, measurement-window controls, HUBPREQ debug buses, HUBPRET read-line values/status, DC perfmon event/counter control, counter state, counter interrupts, and captured values.

Register state may be reset or lost across GPU reset, display engine reset, pipe reset, power gating, suspend/resume, mode set, or DCN resource reinitialization. Higher-level display state remains the software source of truth and must reprogram these registers when the hardware context is rebuilt.

## Dependencies

This chunk depends on the matching generated address metadata in `dcn_4_2_0_offset.h`. Shift/mask constants alone do not identify MMIO addresses or base indices.

Other important dependencies are:

- AMD display register-helper infrastructure that consumes generated field names through `FD_MASK`, `FD_SHIFT`, `REG_FIELD`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and related macros.
- DCN 4.2 resource and hardware object code, especially HUBP, hubbub, IRQ, DMUB, GPIO, and resource initialization paths that include this header.
- DCN 4.2 hardware register-generation inputs. Because this is generated silicon metadata, manual edits are unsafe unless synchronized with the source register database and companion offset headers.
- Display mode programming and validation logic that computes surface addresses, pitch, tiling, DCC, cursor, prefetch, vblank, flip, and QoS values before register writes occur.
- Interrupt service code that maps HUBP flip events to DAL IRQ sources and relies on the corresponding interrupt mask/status/clear fields being correct.
- Debug and performance tooling that expects perfmon and debug-bus fields to match silicon behavior.

## Integration Points

Primary integration is the macro-name ABI between generated headers and DCN runtime code. A field reference such as `HUBPREQ2_DCSURF_FLIP_CONTROL__SURFACE_FLIP_PENDING` or `CURSOR0_2_DMDATA_STATUS__DMDATA_UNDERFLOW_CLEAR` must resolve to the correct shift and mask for the register helper layer.

Subsystem-level integration points include:

- Plane programming: surface format, viewport, tiling, pitch, rotation/mirror, DCC, TMZ, meta-address, and request-size fields feed scanout setup for each HUBP instance.
- Memory management: VMID, system aperture, TLB, PTE/meta timing, and request memory-power fields connect display scanout to GPU virtual memory and page-table fetch behavior.
- Flip scheduling and IRQs: flip control and flip interrupt fields integrate with page-flip handling, vupdate/vblank timing, stereo synchronization, triple buffering, GSL, and IRQ service status/clear handling.
- Clock and power management: HUBP clock-gating fields, memory-power force/disable/status fields, MALL usage state, UCLK pstate force/status fields, and self-refresh/pstate-allow status bits connect display pipe operation to power-management policy.
- Cursor and metadata: cursor address/shape/position fields and DMDATA fields integrate cursor plane programming with display metadata transport, QoS, underflow detection, and protected-memory operation.
- Color pipeline support: HUBP 3D LUT control, address, TMZ, width, crossbar, and deadline fields connect HUBP-side LUT fetch/setup to later color-pipeline processing.
- Diagnostics: HUBP debug muxes, measurement windows, HUBPREQ/HUBPRET status, read-line status, MALL status, and DC perfmon fields integrate with debugfs-style inspection, trace/debug captures, and performance counter collection.

## Risks and Failure Modes

- Incorrect shift or mask values corrupt adjacent register fields. In these blocks, that can cause bad scanout addresses, wrong protected-memory attributes, DCC mismatch, viewport errors, missed flips, cursor corruption, or memory-fetch underflow.
- Repeated instance prefixes are easy to confuse. `HUBPREQ1`, `HUBPREQ2`, and `HUBPREQ3` contain mostly identical field names; a prefix/offset mismatch can break only one display pipe and escape simple single-monitor testing.
- The chunk starts and ends inside larger generated sequences. The first line is the tail of a HUBP1 VMPG register and the last line is inside the beginning of the HUBPREQ3 address block; the final per-file report must reconcile neighboring chunks before drawing whole-file conclusions.
- Clear, status, and interrupt-ack fields need exact write semantics. Treating clear/ack bits as normal persistent configuration can lose interrupts, repeatedly retrigger interrupts, or hide flip/DMDATA/perfmon events.
- Surface address high fields are narrow while low fields are 32-bit. Consumers must preserve address split semantics and avoid truncation when programming primary, secondary, metadata, cursor, DMDATA, or 3D LUT addresses.
- TMZ and DCC fields affect security and memory interpretation. Stale or wrong masks can lead to protected-buffer access failures, decompression artifacts, or memory faults.
- Timing and QoS fields affect underflow margins. Bad vblank/flip/nominal delivery timing, TTU, refcyc, prefetch, or QoS urgent metadata can produce intermittent underflow tied to resolution, refresh rate, memory clock, cursor state, or multi-plane composition.
- Clock-gating and memory-power masks can wedge register access or fetch paths if force/disable/status fields are misidentified.
- High-bit fields such as `0x80000000L` are common for done/status/debug/ack bits. Consumers should avoid signed or narrow arithmetic assumptions when composing register values.
- Perfmon control and interrupt fields share registers with state/captured values. Bad masks can make diagnostics misleading even when normal display output appears correct.

## Test Signals

Useful validation signals for changes affecting this chunk include:

- Build coverage: DCN 4.2 display, DMUB, IRQ, GPIO, and resource code compiles without missing or renamed generated macros.
- Register table validation: `dcn_4_2_0_offset.h` and this shift/mask header remain in sync for HUBP/HUBPREQ/HUBPRET/cursor/perfmon instances 1, 2, and 3.
- Plane scanout tests: primary and secondary surfaces across formats, tiling modes, rotations, mirroring, DCC on/off, TMZ on/off, chroma planes, and meta surfaces.
- Multi-pipe tests: one, two, three, and more active display pipes to catch repeated-instance prefix errors in `HUBPREQ1/2/3`, `HUBP2/3`, `CURSOR0_1/2`, and `DC_PERFMON7/8`.
- Page-flip tests: immediate and synchronized flips, vupdate skip, pending delay, triple buffering, GSL, stereo-sync, flip-away events, and interrupt clear/status handling.
- Underflow and QoS tests: high-resolution/high-refresh modes, memory-clock changes, pstate transitions, self-refresh entry/exit, cursor movement, DMDATA traffic, and MALL use.
- Suspend/resume and reset tests: verify HUBP/HUBPREQ/HUBPRET/cursor/perfmon registers are reinitialized correctly after hardware state is lost.
- Cursor tests: different cursor sizes, modes, hot spots, stereo cursor offsets, protected cursor memory, cursor memory power transitions, DMDATA update/repeat/software paths, and DMDATA underflow clear.
- 3D LUT tests: HUBP 3D LUT enable, addressing, width, crossbar selection, TMZ, address split, deadline parameter, and done status.
- Perfmon diagnostics: event selection, counter run/stop/restart, counter interrupt status/ack, captured value high/low reads, and perfmon clock-enable behavior for instances 7 and 8.
- Debug readback: HUBP/HUBPREQ/HUBPRET status registers, MALL status, read-line status, MPTE/chunk request status, and clock-on/gate status should match expected hardware behavior during mode set, flip, vblank, and pstate transitions.

## Chunk Notes

This report intentionally covers only lines 20257-22731 of `dcn_4_2_0_sh_mask.h`. It is a chunk artifact for an oversized generated header, so the complete per-file report must later merge this with neighboring chunks. The partial HUBPREQ3 block at the end should be interpreted with the following chunk before final per-file conclusions are made.
