# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h lines 12327-14826

## Purpose

This chunk is part of AMDGPU's generated DCN 2.0 register field mask header. It contains no executable C logic; it publishes compile-time bit positions and already-shifted masks for Display Core Next 2.0 hardware registers. Consumers combine these `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros with matching register offsets from `dcn_2_0_0_offset.h` and the display register helper macros.

The assigned range spans 2,105 macros. It starts inside the `DC_PERFMON9` block for the HUBP2 display pipe, covers the HUBP XFC tail for pipe 2, then defines the repeated HUBP/HUBPREQ/HUBPRET/cursor/perfmon/XFC field layouts for pipes 3 and 4. It ends at the start of pipe 5 HUBP fields, after `HUBP5_DCHUBP_CNTL`.

Major hardware areas represented here are:

- `DC_PERFMON9`, `DC_PERFMON10`, and `DC_PERFMON11` display performance monitor fields for HUBP instances 2, 3, and 4.
- `HUBPXFC2`, `HUBPXFC3`, and `HUBPXFC4` cross-FIFO/compressed-buffer read, delay, slave timing, scaler, MPC, and underflow-status fields.
- `HUBP3`, `HUBP4`, and the start of `HUBP5` DCSURF/DCHUBP fields for surface format, tiling, viewport, request sizing, hubp control, clock control, virtual memory page size, debug, and clock-domain measurement windows.
- `HUBPREQ3` and `HUBPREQ4` fields for pitch, VMID, surface and metadata addresses, flip and queue controls, pacing, in-use address readback, TTU/QoS, VM apertures and page-table registers, TLB control, blank/prefetch/nominal delivery parameters, cursor fetch settings, memory power control, and status.
- `HUBPRET3` and `HUBPRET4` return-path fields for memory power, read-line control/readback, interrupts, and status.
- `CURSOR0_3` and `CURSOR0_4` fields for cursor image addressing, size, position, hot spot, stereo offsets, destination offset, cursor memory power, and DMDATA memory/software payload control.

Although the repository path is under `ceph-client`, this chunk is AMDGPU display hardware metadata. It has no Ceph filesystem protocol behavior and no distributed filesystem state.

## Important APIs, Types, And Macros

There are no functions, structs, enums, or storage objects in this range. The macro namespace is the API surface.

Every field appears as a pair:

- `REGISTER__FIELD__SHIFT`: the field's low bit position within a 32-bit MMIO register.
- `REGISTER__FIELD_MASK`: the field mask in its final register position.

The pipe-specific prefixes are the main structure:

- `HUBP3_*`, `HUBP4_*`, and `HUBP5_*` describe the hub pipe's local DCSURF/DCHUBP register fields. Key fields include pixel format, rotation, mirror, address configuration, tiling mode, primary/secondary viewport rectangles, luma/chroma request sizes, blank/disable/underflow control, VTG selection, TTU mode, timeout handling, clock gating status, virtual-memory page size, debug, and measurement-window controls for DCFCLK and DPPCLK.
- `HUBPREQ3_*` and `HUBPREQ4_*` describe the request side of a hub pipe. They expose surface pitch, primary/secondary luma and chroma base addresses, metadata addresses, surface control, flip control, flip interrupt/status, in-use and earliest-in-use addresses, expansion mode, TTU watermarks, global TTU controls, per-surface and per-cursor TTU controls, VM system apertures, VM context page-table/protection-fault registers, L1 TLB control, prefetch and vblank timing parameters, flip/nominal delivery timing, cursor settings, and memory power control/status.
- `HUBPRET3_*` and `HUBPRET4_*` describe the return path. They include enable/control, memory power control/status, read-line controls, line readback values, interrupt fields, and status fields.
- `CURSOR0_3_*` and `CURSOR0_4_*` describe the first cursor plane attached to HUBP3/HUBP4. They cover enable/mode/pitch/lines-per-chunk, surface address high/low, size, position, hot spot, stereo offsets, destination offset, memory power, and DMDATA address/control/QoS/status/software data registers.
- `DC_PERFMON9_*`, `DC_PERFMON10_*`, and `DC_PERFMON11_*` describe display performance counters. They include counter event selection, counted-value selection, increment mode, hardware/run-enable controls, counter-off interrupt controls, counter state selection, current value readback, high/low counter registers, and interrupt status/ack fields for counters 0-7.
- `HUBPXFC2_*`, `HUBPXFC3_*`, and `HUBPXFC4_*` describe XFC-related buffering. They include MXFC/SXFC enable, 64-bpp and bandwidth-reduction modes, read VMID, chunk size, XBUF base0/base1 addresses, pitch, delay configuration, prefetch margin, underflow watermark/status/clear counters, slave VTG offsets, slave scaler ratio/init, and MPC destination start.

The chunk also contains repeated luma/chroma variants with `_C` suffixes, for example `DCSURF_SURFACE_PITCH_C`, `DCSURF_PRIMARY_SURFACE_ADDRESS_C`, `DCHUBP_REQ_SIZE_CONFIG_C`, `PREFETCH_SETTINGS_C`, and chroma viewport fields. These are part of planar or multi-plane surface programming.

## Control Flow

This header has no runtime control flow. It is preprocessor data used by runtime display-driver code.

A typical consumer flow is:

1. The DCN 2.0 resource code selects an instance register address from `dcn_2_0_0_offset.h`.
2. The matching shift/mask value from this header is placed into a per-block register table, commonly through macros such as `HUBP_MASK_SH_LIST_DCN20(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN20(_MASK)`.
3. HUBP, cursor, VM, IRQ, DMUB, or GMC code uses register helpers such as `REG_SET`, `REG_UPDATE`, `REG_UPDATE_N`, `REG_GET`, or `REG_WAIT`.
4. Those helpers apply the stored shift/mask values to read, insert, clear, wait for, or write the desired hardware field.

The control-sensitive hardware actions represented by this chunk include enabling/disabling hub pipes, blanking, waiting for outstanding requests to drain, programming surface format/tiling/viewport/pitch/address metadata, switching luma/chroma surfaces on flips, programming VM apertures and page-table ranges, clearing underflow or timeout status, setting cursor location and image memory, programming DMDATA payload delivery, configuring prefetch/TTU timing, controlling memory power states, and collecting perfmon counter values. The macros themselves do not enforce valid sequencing or legal values.

## State And Persistence Behavior

The file stores no software state and has no persistence mechanism. It describes state held in DCN 2.0 hardware registers.

The hardware state represented here includes:

- Surface state: pixel format, rotation, mirroring, tiling, address layout, viewport rectangles, pitch, base addresses, metadata addresses, stereo surface controls, surface control bits, flip mode, flip status, and in-use address readback.
- Fetch and timing state: request sizes, chunk/group sizes, prefetch parameters, vblank/flip/nominal delivery timing, per-line delivery, TTU watermarks, TTU enable/mode, reference-clock to pixel-clock ratios, and cursor fetch adjustments.
- VM state: VMID selection, system apertures, default addresses, context0 page-table base/start/end, protection-fault default/fault addresses, and L1 TLB controls.
- Cursor and DMDATA state: cursor enable/mode/pitch/position/hot spot, stereo offsets, destination offset, cursor memory power, DMDATA address, DMDATA update/repeat/mode/size, QoS, underflow, and software-injected data.
- Power/status/debug state: HUBP clock enables/gating status, HUBP/HUBPREQ/HUBPRET/CURSOR memory power controls and status, read-line status, debug registers, timeout/underflow status and clear bits.
- Performance monitor state: counter event selection, run modes, counted values, interrupt enable/status/ack, counter high/low values, and read selectors.
- XFC state: XBUF read addresses/pitch, transfer and precharge delays, underflow watermark/status/counters, slave timing offsets, scaler ratio/init, and MPC destination start.

Persistence follows hardware reset and power-management semantics rather than file semantics. Some fields are latched programming values, some are live status bits, some are readback-only addresses or counters, some are sticky status bits requiring explicit clear/ack writes, and some may be reset by display power gating, mode set, suspend/resume, firmware activity, or ASIC reset. This generated header does not encode read-only, write-one-to-clear, self-clearing, or ordering rules.

## Dependencies And Integration Points

This chunk depends on the generated DCN 2.0 register-header ecosystem:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_offset.h` supplies the matching MMIO register addresses and base indices.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_2_0_0_sh_mask.h` supplies the field layouts, including this chunk.
- Display core register helpers consume these constants through generated field macros and per-block shift/mask tables.

Direct include sites found in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn20/dcn20_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn20/irq_service_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn20/dcn20_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn20.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gmc_v10_0.c`

The closest high-level integration point for the fields in this chunk is the DCN 2.0 HUBP resource setup. `dcn20_resource.c` builds six `dcn_hubp2_registers` entries with `HUBP_REG_LIST_DCN20(id)` and fills `dcn_hubp2_shift`/`dcn_hubp2_mask` with `HUBP_MASK_SH_LIST_DCN20(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN20(_MASK)`. `dcn20_hubp.h` defines those lists by mapping generic fields such as `CURSOR_ENABLE`, `DMDATA_UPDATED`, `VMID`, `HUBP_VREADY_AT_OR_AFTER_VSYNC`, and `SURFACE_TRIPLE_BUFFER_ENABLE` to concrete register-field macros from this generated header.

Runtime users are mainly HUBP code under `display/dc/hubp/`. The lower-level HUBP implementation uses `REG_SET`, `REG_UPDATE`, `REG_GET`, and `REG_WAIT` for `DCHUBP_CNTL`, `DCSURF_*`, `HUBPRET_CONTROL`, TTU/prefetch parameters, VM aperture/page-table registers, cursor registers, and DMDATA registers. IRQ integration also depends on matching generated field names for flip, vblank/vline, VM fault, underflow, and perfmon interrupt status/ack fields.

## Risks And Edge Cases

The primary risk is silent hardware misprogramming. A wrong shift or mask compiles cleanly but can update the wrong bit, leave the intended field unchanged, corrupt an adjacent field during read-modify-write, or cause wait loops to observe the wrong status bit.

High-risk fields in this chunk include:

- Surface addressing and metadata fields, because incorrect low/high address or pitch masks can fetch from the wrong framebuffer or compression metadata.
- Format, tiling, viewport, request-size, and chunk/group-size fields, because they affect memory layout, swath fetch, and bandwidth calculations.
- Flip and in-use fields, because incorrect flip programming can cause tearing, stale-frame display, incorrect flip interrupts, or use-after-free of scanout buffers.
- VM aperture, page-table, VMID, and protection-fault fields, because mismatches can cause GPU VM faults, memory isolation failures, or invalid display fetches.
- Underflow, timeout, memory-power, and clock-gating bits, because incorrect status/clear or power sequencing can hide real failures or produce intermittent blanking.
- Cursor/DMDATA fields, because bad cursor addressing or size can display corrupt cursors and bad DMDATA update/QoS fields can trigger underflow or missed metadata delivery.
- TTU, vblank, prefetch, and per-line delivery fields, because they are timing-sensitive and depend on mode timing, clocks, memory latency, and bandwidth model output.
- Perfmon fields, because wrong counter select, status, or ack fields can break diagnostics without affecting normal modeset behavior.
- XFC fields, because read base, delay, prefetch margin, and underflow watermark/status fields affect compressed-buffer transfer behavior and underflow reporting.

The repetition across instances 3 and 4 creates copy-generation risk. `HUBP3` and `HUBP4`, `HUBPREQ3` and `HUBPREQ4`, `HUBPRET3` and `HUBPRET4`, `CURSOR0_3` and `CURSOR0_4`, `DC_PERFMON10` and `DC_PERFMON11`, and `HUBPXFC3` and `HUBPXFC4` largely mirror each other. A mismatched suffix, missing chroma variant, or one-off mask width error may only fail on a specific pipe or display topology.

The chunk boundaries are artificial. The first lines continue `DC_PERFMON9_PERFCOUNTER_STATE` from the previous chunk, and the final lines stop after `HUBP5_DCHUBP_CNTL` before the remaining `HUBP5` fields. The final per-file reconciliation should treat these as line-splitting artifacts, not logical source omissions.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware behavior:

- Kernel/driver builds for DCN 2.0 display paths should compile all generated field names referenced by DCN 2.0 resource, HUBP, IRQ, GPIO, clock, DMUB, and GMC code.
- A generated-register audit should compare every `*_MASK`/`*__SHIFT` pair in this line range against AMD's source register database and the companion addresses in `dcn_2_0_0_offset.h`.
- Static checks should verify each mask is consistent with its shift and field width, and that mirrored instance families remain symmetric where the hardware database expects symmetry.
- Display modeset tests should exercise pipes 3 and 4, plus pipe 5 once later chunks provide the remaining fields, across primary and overlay-like surface programming.
- Plane tests should cover luma/chroma pitch, viewport, metadata address, tiling, rotation, mirror, stereo, and flip-control combinations.
- Cursor tests should cover enable/disable, hotspot, negative/edge positions, different cursor sizes and pitches, stereo cursor offsets, memory power state transitions, and DMDATA delivery.
- VM tests should exercise VMID programming, system aperture boundaries, page-table base/start/end, protection-fault handling, and suspend/resume restoration.
- Bandwidth/timing tests should verify prefetch, vblank, flip, nominal, TTU, per-line delivery, and request-size fields under high-resolution, multi-plane, high-refresh, and memory-pressure scenarios.
- IRQ and status tests should verify flip, underflow, timeout, VM fault, read-line, DMDATA underflow, and perfmon status/ack bits transition as expected.
- Power-management tests should stress clock gating, HUBP/HUBPREQ/HUBPRET/CURSOR memory power controls, hotplug, modeset, runtime suspend, and system suspend/resume.
- Perfmon diagnostics should confirm event selection, counter running state, count-off interrupts, counter high/low reads, and interrupt ack behavior for the covered performance monitor instances.
- XFC-specific tests should verify XBUF base/pitch programming, prefetch margin, delay settings, underflow watermark/status/counter behavior, and slave timing/scaler/MPC configuration.

Regression symptoms from bad constants include blank or flickering display, wrong colors or format, corrupt scanout, cursor corruption, lost or repeated flips, spurious underflow/timeout reports, missed interrupts, GPU VM faults, broken DMDATA delivery, failed resume, unstable high-refresh modes, inaccurate perfmon data, or failures isolated to HUBP3/HUBP4/HUBP5 instance-specific display configurations.

## Cross-Chunk Notes

Earlier chunks of `dcn_2_0_0_sh_mask.h` define preceding DCN 2.0 display register field families, HUBP0-HUBP2 portions, and the start of `DC_PERFMON9_PERFCOUNTER_STATE`. Later chunks complete the remainder of `HUBP5` and continue through subsequent DCN 2.0 register field groups. The final merged per-file research document should describe this source as one generated hardware register layout contract, with this chunk contributing the mid-file HUBP/HUBPREQ/HUBPRET/cursor/perfmon/XFC instance coverage.
