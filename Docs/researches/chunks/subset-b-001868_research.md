# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_sh_mask.h lines 7528-10046

## Purpose

This chunk is generated AMD DCN 3.1.5 register field metadata. It contains no executable C logic; it publishes preprocessor constants that describe bit positions (`__SHIFT`) and bit masks (`_MASK`) for display-controller MMIO registers. Driver code includes this header with the matching `dcn_3_1_5_offset.h` so register-table builders can compute addresses from the offset header and manipulate individual fields from this mask header.

The requested range starts in the middle of the `DCN_VM_CONTEXT8_CNTL` group, then covers VM context page-table fields for contexts 8 through 15, DCN VM default/fault registers, `DC_PERFMON6`, HUBP/HUBPREQ/HUBPRET/cursor blocks for HUBP instances 0 and 1, `DC_PERFMON7` and `DC_PERFMON8`, all visible HUBP2 fields, and the beginning of `HUBPREQ2`. It defines 2,099 macros and 394 register/address-block comments in this slice.

Although the path is under a local `ceph-client` source mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocation paths, locks, or direct register reads/writes in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the least-significant bit position of a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: the bit mask used to isolate or update that field.
- Address-block comments such as `// addressBlock: dce_dc_dcbubp0_dispdec_hubpreq_dispdec`: generated grouping metadata that identifies the hardware block owning the following registers.

Major register families in this range:

- `DCN_VM_CONTEXT8` through `DCN_VM_CONTEXT15`: page table depth/block-size fields plus page directory base, start logical page, and end logical page high/low fields. Context 8 begins mid-group because line 7528 is already inside the context-8 control mask definitions.
- `DCN_VM_DEFAULT_ADDR_MSB/LSB`, `DCN_VM_FAULT_CNTL`, `DCN_VM_FAULT_STATUS`, and `DCN_VM_FAULT_ADDR_MSB/LSB`: default address, VM fault control, sticky/status, faulting VMID/table-level/pipe, interrupt status, and fault address fields.
- `DC_PERFMON6`, `DC_PERFMON7`, and `DC_PERFMON8`: display perfmon counter control, counter selection, clear/freeze/enable controls, state, accumulator values, high/low counter values, interrupt/mask controls, and overflow/interrupt status fields.
- `HUBP0`, `HUBP1`, and visible `HUBP2`: surface format/address/tiling/viewport fields, request sizing, blanking/soft reset/underflow/timeout controls, HUBP clock gating/status controls, virtual memory page size, debug windows, and DCFCLK/DPPCLK performance measurement windows.
- `HUBPREQ0` and `HUBPREQ1`: surface pitch and VMID fields, primary/secondary luma and chroma surface addresses, metadata addresses, DCC/TMZ surface-control fields, flip controls and interrupts, in-use and earliest-in-use address latches, TTU/QoS controls, VM aperture and L1 TLB controls, blanking/destination/prefetch/vblank/flip/nominal timing parameters, cursor request settings, memory power control/status, and later vblank/flip parameter extensions.
- `HUBPRET0` and `HUBPRET1`: HUBPRET control, memory power, read-line control/value/status, and interrupt status/ack/mask fields.
- `CURSOR0_0` and `CURSOR0_1`: cursor control, surface address, size, position, hot spot, stereo control, destination offset, memory power, and DMDATA address/control/QoS/status/software data fields.
- Beginning of `HUBPREQ2`: surface pitch, VMID, primary/secondary surface address, and primary/secondary metadata address fields through `HUBPREQ2_DCSURF_SECONDARY_META_SURFACE_ADDRESS_HIGH`.

Representative field groups include:

- VM context masks using full 32-bit low address fields and 4-bit high logical-page fields.
- Fault controls such as `DCN_VM_ERROR_STATUS_CLEAR`, `DCN_VM_ERROR_STATUS_MODE`, `DCN_VM_ERROR_INTERRUPT_ENABLE`, `DCN_VM_RANGE_FAULT_DISABLE`, and `DCN_VM_PRQ_FAULT_DISABLE`.
- HUBP control/status fields such as `HUBP_BLANK_EN`, `HUBP_NO_OUTSTANDING_REQ`, `HUBP_SOFT_RESET`, `HUBP_VTG_SEL`, `HUBP_DISABLE_STOP_DATA_DURING_VM`, `HUBP_UNBOUNDED_REQ_MODE`, `HUBP_SEG_ALLOC_ERR_STATUS`, `HUBP_TIMEOUT_STATUS`, and `HUBP_UNDERFLOW_STATUS`.
- Surface/request fields such as `PITCH`, `META_PITCH`, primary/secondary address low/high halves, DCC enable/block size fields, TMZ protection fields, `SURFACE_FLIP_PENDING`, and flip interrupt status/enable/clear bits.
- TTU and prefetch fields that encode delivery time, QoS watermark, vblank timing, flip timing, and per-line delivery parameters used by display memory scheduling.

## Control Flow

This header has no runtime control flow. Runtime sequencing is supplied by AMDGPU display code:

1. DCN 3.1.5 resource, IRQ, and DMUB code includes `dcn_3_1_5_offset.h` and this `dcn_3_1_5_sh_mask.h` file.
2. Register-list macros paste symbolic register names into offset names and field names. Offsets come from the companion offset header; field masks and shifts come from this file.
3. Macros such as `FD_MASK(reg, field)`, `FD_SHIFT(reg, field)`, `HUBBUB_SF(...)`, `TF_SF(...)`, `IPP_SF(...)`, `DMUB_SF(...)`, and IRQ register-entry helpers materialize per-ASIC register tables.
4. Driver code later uses those tables with register helpers such as `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, `REG_GET`, and polling/wait helpers to configure VM fault handling, HUBP surface fetching, cursor planes, flip interrupts, memory power, perf counters, and DMUB-visible register state.

The macros do not encode hardware ordering requirements. Consumers must still sequence page-table setup, VM fault clearing, HUBP blanking/reset, plane address updates, flip locking, DCC/TMZ programming, cursor updates, memory power transitions, clock gating, interrupt clear/ack, and suspend/resume restoration correctly.

## State And Persistence Behavior

The chunk stores no software state and persists nothing in files or memory. It describes MMIO-backed GPU state. The represented state includes:

- DCN VM context configuration for page table depth, block size, base page-directory address, and logical page ranges for contexts 8 through 15.
- DCN VM default address and VM fault state, including status bits, VMID, translation response VMID, table level, pipe, interrupt status, and fault address.
- Perfmon state for counter-source selection, counter enable, clear, freeze, accumulation, interrupt masking, and overflow/interrupt reporting.
- HUBP plane-fetch state for surface format/layout, tiling, viewport coordinates, request granularity, clock/power/debug controls, outstanding-request status, timeout, underflow, and virtual-memory page size.
- HUBPREQ state for active and pending surface addresses, metadata addresses, surface pitch, VMID selection, DCC/TMZ protection, flip control, in-use address latching, TTU/QoS/prefetch timing, VM aperture/TLB behavior, cursor request adjustment, and memory power status.
- HUBPRET read-line and memory power state.
- Cursor position, size, format, address, hot spot, stereo, memory power, and DMDATA sideband state.

Persistence is hardware-defined. Many configuration registers retain values until modeset, plane update, power gating, suspend/resume, or ASIC reset. Status, interrupt, overflow, clear, ack, in-use, earliest-in-use, timeout, underflow, and memory-power status fields may be read-only, sticky, self-clearing, write-one-to-clear, or timing-sensitive. This generated header only gives bit positions and masks; it does not express access type or side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN 3.1.5 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_5_offset.h`, which supplies the matching MMIO register offsets.
- DCN base-address definitions such as `DCN_BASE__INST0_SEG*` in the DCN 3.1.5 resource, IRQ, and DMUB translation units.
- Common AMD display register helper macros that derive field masks/shifts from generated names.

Direct include sites in this tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn315/irq_service_dcn315.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn315.c`

Important consumer areas:

- HUBBUB code uses `DCN_VM_FAULT_*` masks/shifts through `HUBBUB_SF(...)` field lists to read and control display VM fault reporting.
- HUBP and IPP/DPP code uses `HUBP*`, `HUBPREQ*`, and `CURSOR0_*` fields for plane fetch, cursor programming, surface pitch/address, DCC/TMZ, request sizing, blanking, reset, and memory power.
- IRQ service code uses `HUBPREQ` flip interrupt registers to map HUBP flip events to DC IRQ sources.
- DMUB code uses `DMUB_DCN315_FIELDS()` with `FD_MASK`/`FD_SHIFT` to expose the same generated fields to firmware-facing register tables.
- Display mode, watermarks, and validation logic feed values that ultimately land in TTU, prefetch, vblank, flip, nominal, and per-line delivery registers described here.

## Risks And Edge Cases

- Field drift is the central risk. These macros are untyped constants, so an incorrect shift or mask can compile cleanly while setting the wrong bit field in MMIO.
- The chunk boundary is artificial. The first line is only the tail of `DCN_VM_CONTEXT8_CNTL`, and the last line stops inside `HUBPREQ2`; adjacent chunks are required for complete file-level claims.
- Repeated instance families are copy-sensitive. `HUBP0`/`HUBP1`/`HUBP2`, `HUBPREQ0`/`HUBPREQ1`/`HUBPREQ2`, `HUBPRET0`/`HUBPRET1`, `CURSOR0_0`/`CURSOR0_1`, and `DC_PERFMON6`/`7`/`8` are structurally similar but not interchangeable.
- VM context and VM fault fields affect GPU/display memory translation. Wrong masks can hide faults, clear the wrong sticky state, misreport VMID/pipe/table level, or program incorrect page-table ranges.
- Surface address and pitch fields are high impact. Bad masks can corrupt plane fetch addresses, chroma addresses, metadata addresses, DCC metadata, or pitch values, causing blank displays, corruption, underflow, or GPU faults.
- Flip-control and interrupt fields are sequencing-sensitive. Incorrect pending, lock, clear, or enable masks can cause missed page flips, stuck IRQs, frame pacing problems, or races during atomic commits.
- DCC and TMZ fields mix compression and protected-memory behavior. Incorrect values can produce display corruption, protection faults, or security-sensitive protected-surface exposure.
- TTU, prefetch, vblank, nominal, and per-line delivery fields are timing-sensitive. Incorrect masks can cause underflow only under specific modes, memory clocks, scaling, multi-plane, or multi-display workloads.
- Clock, reset, blank, memory-power, timeout, underflow, and perfmon fields may have side effects. Writes while a block is gated, reset, or actively scanning can be ignored or disruptive.

## Test Signals

Useful validation combines generated-header consistency checks and hardware behavior:

- Build AMDGPU/DC with DCN 3.1.5 support enabled. Missing or renamed masks/shifts should fail in `dcn315_resource.c`, `irq_service_dcn315.c`, `dmub_dcn315.c`, and shared HUBBUB/HUBP/DPP/IPP users.
- Mechanically verify that each visible `__SHIFT` macro in lines 7528-10046 has the expected companion `_MASK` macro for the same register field where the generated schema defines one.
- Diff this slice against AMD's authoritative DCN 3.1.5 register database and adjacent generated headers such as DCN 3.1/3.2 where hardware compatibility is expected.
- Exercise systems with enough active planes to use HUBP/HUBPREQ instances 0, 1, and 2: primary plane, overlays, chroma formats, cursor plane, page flips, scaling, DCC-enabled buffers, protected buffers, and suspend/resume.
- Validate DCN VM behavior by checking VM fault logging, fault clear behavior, fault interrupt enable/disable, VMID reporting, and page-table range programming under display memory pressure.
- Run display modes that stress request timing: high resolution, high refresh, multiple displays, DCC, cursor movement, overlays, bandwidth-limited memory clocks, and rapid atomic commits.
- Check flip IRQ behavior through DRM page-flip tests and kernel logs for missed/stuck flip interrupts.
- Monitor for HUBP underflow, timeout, no-outstanding-request hangs, DCC corruption, cursor artifacts, page-flip stalls, VM faults, and resume-only failures.
- Validate perfmon fields by enabling display perf counters and confirming counter source selection, clear/freeze, overflow, interrupt status, and high/low values behave plausibly.

## Cross-Chunk Notes

The previous chunk owns the beginning of the DCN VM context area, including the start of `DCN_VM_CONTEXT8_CNTL`. Later chunks continue `HUBPREQ2` after `HUBPREQ2_DCSURF_SECONDARY_META_SURFACE_ADDRESS_HIGH` and cover the rest of the generated DCN 3.1.5 shift/mask namespace. The final per-file report should merge adjacent chunks before making complete statements about all VM contexts, all HUBP/HUBPREQ instances, or the full `dcn_3_1_5_sh_mask.h` hardware map.
