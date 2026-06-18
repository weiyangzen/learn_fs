# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_sh_mask.h lines 9865-12377

## Purpose

This chunk is generated AMD DCN 3.0.1 register field metadata. It contains no executable C logic; it publishes `#define` constants for field shifts and field masks used to compose or extract MMIO register fields for Vangogh/DCN301 display hardware.

The requested range starts in the tail of the `DC_PERFMON6` block, then covers replicated HUBP pipeline metadata for display pipe instances 1 and 2, and begins the same metadata for instance 3. The covered blocks include:

- `DC_PERFMON6`, `DC_PERFMON7`, and `DC_PERFMON8` performance monitor controls, counter state, counter readback, interrupt status, and counter-offset interrupt fields.
- `HUBP1`, `HUBP2`, and `HUBP3` surface, viewport, request-size, hub-pipe control, clock, debug, VM page-size, and performance-measurement fields.
- `HUBPREQ1`, `HUBPREQ2`, and most of `HUBPREQ3` request-side surface address, pitch, VMID, DCC/TMZ, flip, interrupt, in-use-address, TTU/QoS, VM/TLB, prefetch, vblank, flip, nominal delivery, cursor delivery, and memory-power fields.
- `HUBPRET1` and `HUBPRET2` return-side DET buffer, crossbar, memory-power, read-line, vblank/read-line interrupt, and read-line status fields.
- `CURSOR0_1` and `CURSOR0_2` cursor surface, size, position, hot spot, stereo, memory power, display metadata, software metadata, QoS, and underflow/status fields.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display-driver hardware metadata. It is unrelated to Ceph protocol or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, or locks in this chunk. The public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of a named field within a 32-bit hardware register.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same named field.

The shift/mask pairs are intended to match the register offsets in `dcn_3_0_1_offset.h`. Runtime code uses token-pasting helper macros to bind field names into typed register tables. In `dcn301_resource.c`, `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)` populate `struct dcn_hubp2_shift` and `struct dcn_hubp2_mask` for all HUBP instances. In DMUB code, `FD_SHIFT(reg, field)` and `FD_MASK(reg, field)` from `dmub_reg.h` expand directly to these symbols.

Notable field groups in this range:

- Surface geometry and memory layout: `SURFACE_PIXEL_FORMAT`, `ROTATION_ANGLE`, mirror/alpha enable, tiling `SW_MODE`, `DIM_TYPE`, `META_LINEAR`, pipe alignment, primary/secondary viewport starts and dimensions, and luma/chroma request-size fields such as swath height, chunk size, meta chunk size, DPTE group size, and VM group size.
- HUBP runtime control: blanking, disable, VTG select, vready, timeout status/clear/interrupt enable, underflow status/clear, outstanding-request status, TTU disable/mode, clock enable/gating/status, VMPG size, debug, and DCFCLK/DPPCLK measurement-window controls.
- Surface addressing and protection: primary/secondary luma and chroma base addresses, high address halves with VMID bits, meta-surface addresses, `PRIMARY_SURFACE_TMZ`, `SECONDARY_SURFACE_TMZ`, DCC enable, and DCC independent-block fields.
- Flip and interrupt handling: update lock, flip type, vupdate skip count, pending status, stereo-sync fields, GSL enable/mask, triple buffering, pending minimum time, flip/flip-away interrupt mask/type/clear/occurred/status fields, and current/earliest in-use address snapshots.
- TTU, QoS, VM, and delivery timing: expansion modes for data/chroma/meta/page requests, low/high QoS watermarks, global TTU controls, fixed QoS and ramp disable fields for surface and cursor traffic, DMDATA VM fault/underflow/late/done status, system aperture, L1 TLB control, blank offsets, destination timing, prefetch ratios, vblank/flip/nominal PTE/meta/VM request timing, per-line delivery, and ref-frequency-to-pixel-frequency fields.
- Return and cursor blocks: HUBPRET DET base/crossbar, memory-power force/disable/status, read-line windows and vblank/read-line interrupts; cursor enable/mode/TMZ/pitch/position/size/hotspot/stereo, CROB memory power, DMDATA address/control/QoS/status/software-data fields.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by the display driver:

1. DCN301 resource and DMUB code include `dcn_3_0_1_offset.h` and this matching `dcn_3_0_1_sh_mask.h`.
2. Resource table macros paste register names and instance IDs into symbols such as `HUBP2_DCSURF_SURFACE_CONFIG__SURFACE_PIXEL_FORMAT_MASK` or `HUBPREQ1_DCSURF_FLIP_CONTROL__SURFACE_FLIP_PENDING__SHIFT`.
3. Driver code stores the resulting shifts and masks in block-specific tables and later uses helpers such as `REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_SET_N`, and `REG_UPDATE_N` to update individual hardware fields.
4. Higher-level display paths sequence the writes around modesets, plane updates, flips, cursor updates, memory-power transitions, VM/TLB programming, QoS/watermark programming, and interrupt handling.

The macros do not encode required ordering. For example, the presence of fields for surface addresses, DCC/TMZ, update locks, flip pending status, and interrupt clear bits does not itself enforce the ordering needed to avoid tearing, underflow, stale metadata, or missed interrupts.

## State And Persistence Behavior

The chunk stores no software state and persists nothing. It describes hardware state in memory-mapped display registers.

State represented by these fields includes:

- Per-HUBP plane configuration: pixel format, rotation, mirroring, alpha plane enablement, tiling, viewport geometry, request sizes, VTG binding, blank/disable state, clock state, underflow/timeout status, and debug/measurement windows.
- Per-HUBPREQ fetch/request state: primary/secondary luma/chroma and metadata addresses, VMIDs, VM system aperture, L1 TLB mode, DCC/TMZ controls, flip state, in-use address reporting, TTU/QoS parameters, prefetch/vblank/flip/nominal timing, and request memory-power state.
- Per-HUBPRET return state: DET buffer allocation, component crossbar routing, internal memory power, read-line windows, read-line snapshots, vblank state, and read-line interrupt state.
- Per-cursor state for cursor 0 on pipes 1 and 2: cursor enable/mode, address, size, position, hot spot, stereo offset, TMZ, CROB memory power, DMDATA addressing/control/QoS/status, and software-injected DMDATA.
- Perfmon state: selected performance counters, start/stop controls, high/low counter readback, current counter value, interrupt status/ack bits, and counter offset behavior.

Persistence is hardware-defined. Configuration fields generally retain their programmed value until modeset reprogramming, plane disable, power gating, suspend/resume, or ASIC reset. Status, interrupt, counter, clear, ack, underflow, timeout, pending, and power-status fields may be read-only, sticky, self-clearing, write-one-to-clear, or update only at display timing boundaries. This generated header does not distinguish those semantics; consuming code and hardware documentation must.

## Dependencies And Integration Points

This chunk must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_1_offset.h`, which provides the matching `mm...` register offsets and `_BASE_IDX` constants.
- DCN301 base-address definitions from `vangogh_ip_offset.h`, consumed through `BASE(mm..._BASE_IDX)`.
- DCN shared register-list macros from the AMD display stack, especially the HUBP/HUBPREQ/HUBPRET/CURSOR lists used by DCN 3.0 and reused by DCN301.

Direct include sites in this tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn301.c`

`dcn301_resource.c` constructs `hubp_regs[]`, `hubp_shift`, and `hubp_mask` tables through `HUBP_REG_LIST_DCN30(id)` and `HUBP_MASK_SH_LIST_DCN30(...)`; those tables drive plane, cursor, VM, flip, watermark, underflow, and power-management code in the DC display core. `dmub_dcn301.c` includes this header so DMUB register helpers can derive field masks and shifts through `FD_MASK` and `FD_SHIFT` when programming common DMUB-facing DCN301 registers.

The repeated instance names matter. Instance 1 and 2 blocks are complete in this range; instance 3 starts at `HUBP3` and reaches `HUBPREQ3_REF_FREQ_TO_PIX_FREQ` at the final requested line, so later chunks are required for the rest of pipe 3.

## Risks And Edge Cases

- Generated mask drift is high impact. A wrong shift or mask can compile cleanly but silently update the wrong bits in a display register.
- Register-offset and mask headers are a pair. If `dcn_3_0_1_offset.h` and this header come from different generator revisions, the driver may address the intended register while applying fields from a different layout.
- Repeated pipe instances are copy-sensitive. `HUBP1`, `HUBP2`, and `HUBP3` are structurally similar, but an instance-specific typo can affect only one plane or only multi-display configurations that allocate that pipe.
- Bitfield width errors can corrupt neighboring controls. Examples in this range include packed address-high plus VMID fields, DCC/TMZ control bits, flip interrupt mask/type/clear/status fields, QoS levels, and underflow/timeout clear bits.
- Clear/ack/status fields are side-effect-sensitive. Misusing perfmon interrupt ack, flip clear, DMDATA underflow clear, HUBP underflow clear, timeout clear, or HUBPRET interrupt clear bits can lose diagnostic state or leave interrupts stuck.
- Plane update timing is fragile. Incorrect update-lock, flip-pending, in-use-address, triple-buffering, GSL, prefetch, vblank, flip, nominal, or per-line-delivery fields can cause tearing, black frames, missed flips, underflow, or failures that appear only at high bandwidth.
- VM, DCC, TMZ, and meta-surface fields cross security and memory-management boundaries. Incorrect masks can fetch from the wrong VMID, mark protected memory incorrectly, break DCC metadata reads, or cause page-table/request faults.
- Power fields may be ignored or harmful when clocks/resets are not in the expected state. The memory-power and clock-control fields require sequencing by higher-level power-management code.
- Chunk boundaries are artificial. The range begins after the start of `DC_PERFMON6_PERFMON_CNTL` and ends at the declaration comment for `HUBPREQ3_REF_FREQ_TO_PIX_FREQ`; adjacent chunks are needed for full-file completeness.

## Test Signals

Useful validation combines generated-header checks with display hardware behavior:

- Build AMDGPU/DC with DCN301 support enabled. Missing or renamed field macros should fail in `dcn301_resource.c`, DMUB register table construction, and shared HUBP/HUBPREQ/HUBPRET/CURSOR register-list users.
- Mechanically verify that each `__SHIFT` macro in lines 9865-12377 has a matching `_MASK` macro for the same `<REGISTER>__<FIELD>` where the source defines both, and diff the chunk against AMD's authoritative DCN 3.0.1 generated register database.
- Cross-check this mask chunk against `dcn_3_0_1_offset.h` to ensure every register represented here has a matching offset/base-index definition.
- Exercise plane allocation across pipes 1, 2, and 3 with multi-monitor modesets, plane enable/disable, scaling, rotation, mirroring, alpha, luma/chroma formats, DCC-enabled surfaces, and protected/TMZ surfaces.
- Run flip and vblank tests that cover immediate and synchronized flips, update locks, stereo/GSL fields, triple buffering, flip interrupts, flip-away interrupts, and in-use-address reporting.
- Stress memory and timing paths with high-resolution/high-refresh modes, cursor movement, DMDATA updates, VM faults, page-table pressure, DCC metadata traffic, prefetch/watermark changes, and suspend/resume.
- Monitor kernel logs, debugfs counters, and display diagnostics for HUBP underflow, timeout, DMDATA underflow/late/fault, stuck flip pending, missed vblank/read-line interrupts, cursor corruption, blank frames, perfmon interrupt issues, and resume failures.

## Cross-Chunk Notes

The previous chunk owns the beginning of `DC_PERFMON6_PERFMON_CNTL` and earlier DCN301 register-field metadata. Later chunks continue after `HUBPREQ3_REF_FREQ_TO_PIX_FREQ` and are needed to complete the pipe 3 HUBPREQ/HUBPRET/CURSOR/perfmon material and the rest of `dcn_3_0_1_sh_mask.h`. The final per-file research document should merge adjacent chunks before making whole-file claims about all HUBP instances or all DCN301 display register fields.
