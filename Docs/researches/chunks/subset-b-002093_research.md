# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 13241-15458

## Purpose

This chunk is generated AMD DCN 3.5.1 shift/mask register-field metadata. It has no executable C logic; it publishes preprocessor constants that encode bit offsets and field masks for display hub pipe, request, return, cursor, display metadata, and display perfmon MMIO registers. Consumers pair this header with `dcn_3_5_1_offset.h` so AMDGPU display register-helper macros can update or extract individual hardware fields without hard-coding bit positions in driver code.

The requested range is a mid-file slice containing 2,218 `#define` entries: 1,109 `__SHIFT` macros and 1,109 `_MASK` macros. The range starts at the tail of `HUBP1_DCSURF_TILING_CONFIG` with `PIPE_ALIGNED_MASK`, whose matching shift is in the previous chunk, and stops inside `CURSOR0_3_DMDATA_CNTL` after `DMDATA_MODE_MASK`, before the `DMDATA_SIZE_MASK` line in the next chunk. The apparent `*_MASK_MASK` names in interrupt and perfmon groups are expected generated names for fields whose semantic field name itself ends in `MASK`.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, or locks in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used to pack or unpack a hardware field.
- `<REGISTER>__<FIELD>_MASK`: the mask used to isolate, preserve, or clear the field during MMIO read-modify-write operations.

Major macro families in this slice are:

- `HUBP1`, `HUBP2`, and `HUBP3`: surface format, address/tiling, viewport, request-size, control, clock, VMPG, and DCFCLK/DPPCLK measurement-window fields. These describe per-plane hub pipe behavior, including surface dimensions, swizzle mode, chunk sizes, blank/reset/status bits, timeout/underflow reporting, clock-gating state, and perf measurement windows.
- `HUBPREQ1`, `HUBPREQ2`, and `HUBPREQ3`: hub pipe request-side surface state. Each instance covers pitch, VMID, primary/secondary luma and chroma addresses, meta-surface addresses, surface control, flip control, flip interrupts, in-use and earliest-in-use addresses, expansion mode, TTU/QoS timing, VM aperture and L1 TLB controls, blank offsets, destination dimensions, prefetch, vblank/flip/nominal timing parameters, per-line delivery, cursor request settings, memory power control/status, and additional flip/vblank VM/PTE/meta timing fields.
- `HUBPRET1`, `HUBPRET2`, and `HUBPRET3`: hub pipe return-side control and status. These fields cover DET buffer base selection, 3-to-2 packing disablement, component crossbar source selection, return-side memory power, read-line window programming, vblank/read-line interrupt mask/type/clear/status bits, current read-line value snapshots, and read-line/vblank inside/outside status.
- `CURSOR0_1`, `CURSOR0_2`, and partial `CURSOR0_3`: hardware cursor and display metadata fields. Complete cursor instance 1 and 2 blocks include cursor enable, mode, pitch, size, position, hot spot, stereo offsets, destination X offset, cursor memory power, DMDATA GPU address, DMDATA control, QoS, status, software data control, and software data payload. Instance 3 begins the same pattern and ends mid-`DMDATA_CNTL` because of the artificial chunk boundary.
- `DC_PERFMON7` and `DC_PERFMON8`: display perfmon control, state, counter value, interrupt/status/ack, and high/low readout fields. These are used to select events, counter value sources, increment/run modes, hardware count-off behavior, restart/interrupt behavior, and per-counter state readback.

The chunk is heavily instance-repeated. `HUBPREQ1-3` and `HUBPRET1-3` carry nearly identical field layouts, while `HUBP1` begins in the previous chunk and `CURSOR0_3` continues in the next chunk.

## Control Flow

This header has no runtime control flow. Runtime sequencing comes from AMDGPU display code:

1. DCN 3.5.1 resource, IRQ, and DMUB code includes `dcn_3_5_1_offset.h` and this shift/mask header.
2. Register-list macros such as `SRI(...)`, `HUBP_REG_LIST_DCN30_RI(...)`, and `HUBP_MASK_SH_LIST_DCN35(...)` token-paste register and field names into per-block offset, shift, and mask tables.
3. DCN 3.5.1 resource construction initializes `hubp_regs`, `hubp_shift`, and `hubp_mask` arrays for the available HUBP instances.
4. Runtime HUBP, cursor, flip, VM, prefetch, TTU/QoS, and interrupt paths call helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE`; those helpers use the numeric masks and shifts from this file to touch only the intended bits.

The macros do not encode ordering rules. Consumers must still sequence surface address programming, flip arming, VM aperture/TLB updates, prefetch and delivery timing, cursor metadata updates, memory power transitions, clock gating, interrupt clear/ack behavior, and suspend/resume restore correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It describes MMIO-backed DCN 3.5.1 hardware state:

- Plane fetch configuration for pixel format, rotation, mirroring, tiling, viewport dimensions, pitch, luma/chroma addresses, meta addresses, DCC-related metadata, and stereo/primary/secondary surfaces.
- VM and memory request state for VMID selection, system aperture bounds, L1 TLB controls, request chunk sizing, PTE/meta/VM group timing, and VMPG page-size selection.
- Flip and vblank state for immediate/async flip modes, master update lock status, GSL/triple-buffer control, flip interrupt masking/clearing/status, in-use address reporting, earliest-in-use tracking, and flip/vblank timing parameters.
- QoS, TTU, prefetch, and delivery timing for surfaces, cursors, and DMDATA, including per-line delivery and destination-position dependent request timing.
- HUBP control/status for blanking, soft reset, outstanding requests, underflow and timeout status, clock enable/gating state, and perf measurement windows.
- Cursor state for enable/mode/pitch, dimensions, screen position, hot spot, stereo offsets, source address, cursor memory power, and destination offsets.
- DMDATA state for metadata memory address, TMZ bit, update/repeat/mode/size fields, QoS level and deadline delta, completion/underflow status, and software-injected metadata data.
- HUBPRET read-line/vblank state and interrupts, including line-window start/end, line snapshots, vblank status, read-line inside/outside flags, and memory power state.
- DC perfmon state for selected events, run/count modes, active status, state selectors, current counter values, high/low counter readback, and interrupt status/ack bits.

Persistence is hardware-defined. Configuration fields generally remain until the next modeset, page flip, cursor update, power-gating event, suspend/resume path, driver reset, or ASIC reset. Status, interrupt, clear, underflow, timeout, perfmon, and memory-power fields may be read-only, sticky, self-clearing, write-one-to-clear, clock-domain dependent, or valid only while the relevant display block is powered. This generated header does not distinguish those access semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.5.1 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h`, which provides the matching MMIO offsets and base-index selectors.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes both generated headers and initializes DCN 3.5.1 HUBP register, shift, and mask tables with `HUBP_REG_LIST_DCN30_RI` and `HUBP_MASK_SH_LIST_DCN35`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn35/dcn35_hubp.h`, which defines the DCN 3.5 HUBP shift/mask list extension and `struct dcn35_hubp2_shift` / `struct dcn35_hubp2_mask`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hubp/dcn20/dcn20_hubp.h` and inherited DCN 3.x HUBP headers, which define the common HUBP/HUBPREQ/CURSOR/DMDATA register-list and field-list shapes consumed by DCN 3.5.1.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which maps HUBP flip interrupt source IDs for instances including HUBP1-3 to DAL page-flip IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, which uses the same generated shift/mask style to populate DMUB-facing DCN 3.5 register field tables.

The primary integration point is token-pasted register-table construction. Hardware-specific register names such as `HUBPREQ2_DCSURF_FLIP_CONTROL`, `CURSOR0_1_DMDATA_CNTL`, or `HUBPRET3_HUBPRET_INTERRUPT` become fields in driver-owned tables; generic HUBP code then uses those tables without embedding DCN 3.5.1 numeric bit positions.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong shift or mask can compile cleanly while writing the wrong MMIO bits, corrupting adjacent fields, missing an interrupt, or reading stale status.
- The generated header must match the companion offset header and silicon register database. Manual edits or partial regeneration can make a register address correct but its field layout wrong.
- The chunk boundary is artificial. `HUBP1_DCSURF_TILING_CONFIG__PIPE_ALIGNED_MASK` begins without its shift in this range, and `CURSOR0_3_DMDATA_CNTL__DMDATA_SIZE__SHIFT` ends without its mask until the next line/chunk.
- Repeated instances are easy to miscompare. A generator or copy error in only `HUBPREQ2`, `HUBPRET3`, or `CURSOR0_1` may only fail on a specific pipe, display, cursor plane, or multi-monitor topology.
- Fields with semantic names ending in `MASK` produce generated names such as `PERFCOUNTER_OFF_MASK_MASK` and `PIPE_VBLANK_INT_MASK_MASK`. Tooling that naively strips `_MASK` can report false mismatches.
- Flip, interrupt, underflow, timeout, and clear fields are side-effect-sensitive. Confusing status, mask, type, ack, or clear bits can cause missed page-flip completion, interrupt storms, stuck vblank/read-line reporting, or hidden underflow diagnostics.
- Surface address and VM fields are high risk because low/high halves, chroma variants, meta-surface addresses, VMID, aperture, and TLB settings must agree with memory manager, DCC, TMZ, and plane format state.
- Timing and QoS fields interact with bandwidth calculations outside this header. Bad prefetch, TTU, delivery, PTE/meta/VM group, or deadline masks can produce underruns that only appear at high resolution, high refresh, multi-plane, rotated, or compressed modes.
- Power and clock gating fields may be ignored or hazardous when programmed while the relevant HUBP, request, return, cursor, memory, or clock domain is gated or reset.

## Test Signals

Useful validation combines generated-header checks with DCN 3.5.1 hardware behavior:

- Build AMDGPU display support with DCN 3.5.1 enabled. Missing or renamed macros should fail in DCN 3.5.1 resource construction, HUBP register table initialization, IRQ service code, or DMUB register-field initialization.
- Mechanically verify that every expected field in lines 13241-15458 has the right `__SHIFT`/`_MASK` pairing while accounting for the known boundary exceptions and field names that naturally end in `MASK`.
- Diff this range against AMD's authoritative DCN 3.5.1 register database and nearby generated headers such as `dcn_3_5_0_sh_mask.h` or later DCN 3.x variants where HUBP/HUBPREQ/HUBPRET/CURSOR layouts are expected to match.
- Exercise enough active displays and planes to use HUBP/HUBPREQ/HUBPRET instances 1 through 3, including primary and secondary surfaces, luma/chroma planes, DCC/meta surfaces, cursor planes, and multi-display page flips.
- Validate page-flip behavior with immediate, async, GSL, triple-buffer, vblank, and high-refresh scenarios; watch for missed flip interrupts, stale in-use addresses, underflows, and frame pacing defects.
- Test cursor and DMDATA behavior through cursor enable/disable, movement, hot-spot changes, stereo offsets, large cursor sizes, TMZ metadata, software metadata updates, and suspend/resume.
- Exercise VM and memory paths with different VMIDs, large addresses, system aperture bounds, compressed surfaces, rotated/mirrored surfaces, and memory pressure.
- Check HUBPRET vblank/read-line interrupts and snapshots for correct line windows, status transitions, interrupt clearing, and behavior while the request path is disabled or blanked.
- Use perfmon/debug tooling where available to confirm `DC_PERFMON7` and `DC_PERFMON8` event selection, counter state, interrupt/ack behavior, and high/low readout consistency.
- Watch kernel logs, display diagnostics, and hardware counters for page-flip timeouts, HUBP underflow/timeout status, interrupt storms, cursor corruption, blank displays, wrong viewport placement, DCC/meta faults, VM faults, and resume-only regressions.

## Cross-Chunk Notes

The previous chunk owns the beginning of the `HUBP1` field set, including most of `HUBP1_DCSURF_TILING_CONFIG` and the `PIPE_ALIGNED` shift. This chunk then covers the rest of HUBP/HUBPREQ/HUBPRET/CURSOR/perfmon instance groups for pipes 1 and 2, most of pipe 3, and stops inside `CURSOR0_3_DMDATA_CNTL`. The next chunk continues with `CURSOR0_3_DMDATA_CNTL__DMDATA_SIZE_MASK`, the rest of `CURSOR0_3` DMDATA fields, and subsequent DCN 3.5.1 register-field families. The final per-file research document should merge adjacent chunks before making whole-file claims about all HUBP instances, all cursor instances, or complete shift/mask pairing across `dcn_3_5_1_sh_mask.h`.
