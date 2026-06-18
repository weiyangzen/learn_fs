# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_sh_mask.h lines 12288-14786

## Chunk Scope

This chunk covers a generated AMD DCN 3.0.0 ASIC register shift/mask header slice. The file is guarded by `_dcn_3_0_0_SH_MASK_HEADER` and contains no executable functions, types, storage, or inline logic; it exports preprocessor constants that describe bit positions and bit masks for memory-mapped display hardware registers. Within lines 12288-14786, the slice contains 2,113 `#define` entries, split into 1,056 `__SHIFT` constants and 1,076 `*_MASK` constants, organized under 15 `addressBlock` comments and about 350 register comments.

The chunk starts mid-register at `HUBPREQ3_BLANK_OFFSET_0__DLG_V_BLANK_END_MASK`, continues through HUBP/HUBPREQ/HUBPRET/CURSOR/PERFMON blocks for display pipe instances 3, 4, and 5, and ends at the beginning of the DPP0 CNVC format-conversion block with `CNVC_CFG0_FCNV_FP_BIAS_G`.

## Purpose

The purpose of this chunk is to provide compile-time bitfield metadata for DCN 3.0 display programming. Driver code combines these constants with matching offset definitions from `dcn_3_0_0_offset.h` to program display pipe registers through generated field tables and register access helpers.

The register families represented here map the display pipeline data path:

- `HUBP*` and `HUBPREQ*` define hub pipe surface, VM, request sizing, flip, TTU/QoS, prefetch, blanking, delivery, and memory power fields.
- `HUBPRET*` defines hub pipe return/read-line, interrupt, crossbar, DET/DMROB/PIXCDC memory power, and status fields.
- `CURSOR0_*` defines cursor surface address, size, position, hot spot, stereo, cursor memory power, and display metadata fields.
- `DC_PERFMON9`, `DC_PERFMON10`, and `DC_PERFMON11` define per-pipe display performance monitor counter selection, state, interrupt, and counter value fields.
- `DPP_TOP0` begins display pipe processor top-level clock/reset/CRC/host-read fields.
- `CNVC_CFG0` begins DPP conversion and pixel-format fields.

## Important APIs, Types, And Constants

There are no C APIs or types in this chunk. The exported interface is naming-convention based:

- `REGISTER__FIELD__SHIFT` gives the bit offset to use when packing or unpacking a field.
- `REGISTER__FIELD_MASK` gives the already-positioned field mask for read/modify/write operations.
- Register comments such as `//HUBPREQ4_DCSURF_SURFACE_CONTROL` group adjacent shift/mask pairs.
- `// addressBlock: ...` comments identify the hardware block instance that owns the following register definitions.

Important block groups in this range:

- `HUBPREQ3_*` completes instance 3 timing/request definitions: blank offsets, destination dimensions, scaler positions, prefetch ratios, vblank/flip/nominal PTE and meta chunk timing, per-line delivery, cursor settings, frequency conversion, DRQ limits, and request-side memory power state.
- `HUBPRET3_*`, `HUBPRET4_*`, and `HUBPRET5_*` define return-side control, DET buffer base, 3-to-2 packing disable, crossbar source selection, memory power controls/status, read-line windows, vblank/read-line interrupts, read-line snapshots, and read-line status.
- `CURSOR0_3_*`, `CURSOR0_4_*`, and `CURSOR0_5_*` define cursor enable/mode/TMZ/snoop/system/pitch/lines-per-chunk fields, 48-bit-ish address split into low/high registers, geometry, stereo offsets, memory power state, and `DMDATA` address/control/QoS/status/software data fields.
- `HUBP4_*` and `HUBP5_*` define surface config, address/tiling config, primary/secondary luma and chroma viewports, request-size config, HUBP control, clock gating/status, VM page size, and measurement windows.
- `HUBPREQ4_*` and `HUBPREQ5_*` are large repeated blocks for surface pitch, VMID, primary/secondary luma/chroma surface and meta-surface addresses, TMZ/DCC surface controls, flip controls, flip interrupts, in-use/earliest-in-use latched addresses, TTU/QoS controls for surface and cursor requests, display metadata VM control, VM aperture and L1 TLB controls, blanking, vblank/flip/nominal timing, delivery timing, cursor request settings, and request memory power.
- `DC_PERFMON9_*`, `DC_PERFMON10_*`, and `DC_PERFMON11_*` define event selection, counted-value selection, increment mode, hardware stop/control, run enable, counter active/interrupt fields, 8 counter state selectors, report control, counter-off interrupt handling, clock enable, start/stop selectors, high/low counter value fields, and interrupt status/ack bits.
- `DPP_TOP0_*` covers DPP clock enable and clock gate disable fields, soft reset fields for CNVC/DSCL/CM/OBUF, CRC values and CRC control, and host-read rate control.
- `CNVC_CFG0_*` starts conversion configuration: surface pixel format and alpha-plane enable, format expansion/conversion/alpha/bypass/clamp/crossbar/update-pending fields, and the first floating-point bias register.

## Control Flow And Data Flow

This header does not implement runtime control flow. Its data flow is compile-time:

1. Source files include `dcn/dcn_3_0_0_offset.h` and `dcn/dcn_3_0_0_sh_mask.h`.
2. Component-specific register-list macros select register offsets by instance id, for example `HUBP_REG_LIST_DCN30(id)` in DCN 3.0 resource setup.
3. Component-specific mask/shift list macros expand field names with `__SHIFT` or `_MASK`, for example `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)`.
4. The expanded values populate static register, shift, and mask tables such as the DCN 3.0 HUBP tables in resource code.
5. Runtime register helpers use the tables to pack field values into hardware register writes, extract status bits from reads, and perform read/modify/write updates.

For DPP/CNVC, `dcn30_dpp.h` uses macros such as `TF_SF(CNVC_CFG0_FORMAT_CONTROL, CNVC_BYPASS, mask_sh)` and `TF_SF(DPP_TOP0_DPP_CONTROL, DPP_CLOCK_ENABLE, mask_sh)` to map these constants into transform/DPP field tables. For HUBP/HUBPREQ/HUBPRET, `dcn30_resource.c` builds per-instance tables with `HUBP_REG_LIST_DCN30(id)`, `HUBP_MASK_SH_LIST_DCN30(__SHIFT)`, and `HUBP_MASK_SH_LIST_DCN30(_MASK)`.

## State And Persistence Behavior

The chunk itself has no persistent software state. It describes persistent hardware state in memory-mapped registers:

- Surface address and meta-address fields persist in HUBPREQ until a flip or update sequence replaces them.
- `SURFACE_INUSE` and `SURFACE_EARLIEST_INUSE` expose latched hardware addresses and VMIDs for active or earliest queued surfaces.
- Flip state fields such as `SURFACE_FLIP_PENDING`, flip occurred/status bits, and clear bits expose transient hardware state around page flips.
- VM/TLB and aperture fields control address translation behavior for display metadata and surface fetches.
- Memory power control/status fields reflect or force power states for request, return, cursor, DET, DMROB, PIXCDC, DPTE, MPTE, META, and PDE memories.
- PERFMON counter and interrupt fields hold hardware performance-monitor state until read, reset, acknowledged, or reprogrammed.

Because these are raw bit descriptions, persistence semantics depend on the underlying hardware register behavior and on the driver code that writes or clears the bits.

## Dependencies

Direct dependencies are implicit rather than included in this chunk:

- Matching register offset headers, especially `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_0_offset.h`, must define the corresponding register addresses.
- DC register helper macros and structures in the display core consume the field tables produced from these constants.
- DCN HUBP, DPP, IRQ, DMUB, clock, GPIO, and resource code include this header for DCN 3.0/3.0.2 support.
- The constants assume the hardware register layout for DCN 3.0.0; they are not self-validating and must remain synchronized with ASIC-generated register specs.

Observed include/integration points include `display/dc/resource/dcn30/dcn30_resource.c`, `display/dc/irq/dcn30/irq_service_dcn30.c`, `display/dc/irq/dcn302/irq_service_dcn302.c`, `display/dc/clk_mgr/dcn30/dcn30_clk_mgr.c`, `display/dc/gpio/dcn30/*`, and `display/dmub/src/dmub_dcn30.c` / `dmub_dcn302.c`.

## Integration Points

This chunk is primarily integrated through macro expansion rather than direct symbol references:

- HUBP register programming: `display/dc/hubp/dcn30/dcn30_hubp.h` extends earlier HUBP mask/shift lists with DCN 3.0 fields, while `display/dc/resource/dcn30/dcn30_resource.c` instantiates the lists for hardware pipe ids.
- Resource creation: DCN 3.0 resource code creates HUBP objects and assigns per-instance register/mask/shift tables, so instance-specific constants such as `HUBP4_*`, `HUBPREQ4_*`, and `CURSOR0_4_*` become runtime access metadata.
- DPP format programming: `display/dc/dpp/dcn30/dcn30_dpp.h` consumes `DPP_TOP0_*` and `CNVC_CFG0_*` fields in transform/DPP field lists for clock, pixel-format, alpha, clamp, crossbar, and floating-point bias/scale programming.
- IRQ handling: HUBP flip interrupt sources for pipes 4 and 5 are handled in DC IRQ services; the mask/shift constants here describe the underlying per-HUBPREQ flip interrupt status/clear fields.
- DMUB and clock/GPIO code include the same header for register-level firmware/mailbox or display infrastructure operations where DCN 3.0 register fields are needed.

The per-instance naming is significant. The same logical field appears with numeric prefixes, for example `HUBPREQ4_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN_MASK` and `HUBPREQ5_DCSURF_SURFACE_CONTROL__PRIMARY_SURFACE_DCC_EN_MASK`. Driver macros choose the instance by composing register names from a block prefix and id.

## Risks And Edge Cases

- Generated-header drift is the main risk. If a mask or shift no longer matches the ASIC register spec or the paired offset header, the compiler will still succeed while runtime register programming corrupts unrelated bits.
- Some macros encode status-clear bits adjacent to status bits, such as flip, underflow, PERFMON interrupt, and DMDATA VM fault/underflow clears. Incorrect read/modify/write policy can acknowledge or clear events unexpectedly.
- Surface address fields are split into low and high registers and have separate luma/chroma and meta variants. Mixing `_C`, meta, primary, secondary, in-use, or earliest-in-use registers can program the wrong plane or inspect the wrong latched state.
- TMZ, snoop, system, DCC, and VM/TLB fields affect memory security and address translation. Wrong masks could produce display faults, underflow, secure-memory exposure, or silent corruption.
- Clock-gating, memory-power, and soft-reset fields can make blocks inaccessible or unstable if programmed with stale assumptions.
- PERFMON fields are repeated per pipe with large selector fields; event selection and interrupt acknowledgement can be miswired if instance numbers are confused.
- The chunk begins and ends mid-logical-file. `HUBPREQ3_BLANK_OFFSET_0` starts before this chunk, and `CNVC_CFG0_FCNV_FP_BIAS_G` continues after it. The merge lane must combine adjacent chunk reports before drawing whole-file conclusions.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware/display regression signals:

- Build coverage that compiles DCN 3.0 and DCN 3.0.2 display paths including `dcn30_resource.c`, `dcn302_resource.c`, `dcn30_dpp.h` consumers, IRQ services, DMUB sources, clock manager, and GPIO files.
- Static checks that every mask/shift field referenced by `HUBP_MASK_SH_LIST_DCN30`, `TF_SF`, `TF2_SF`, and related macros resolves against this header.
- Display bring-up on DCN 3.0 hardware with multiple active pipes, especially pipes 3, 4, and 5, validates the repeated instance tables.
- Page-flip and vblank/read-line interrupt tests exercise `HUBPREQ*_DCSURF_FLIP_CONTROL`, `HUBPREQ*_DCSURF_SURFACE_FLIP_INTERRUPT`, and `HUBPRET*_HUBPRET_INTERRUPT` fields.
- Cursor movement, cursor format, stereo cursor, and display metadata tests exercise `CURSOR0_[3-5]_*` and `DMDATA_*` definitions.
- DCC/TMZ/VM surface tests exercise surface-control, aperture, TLB, address, and meta-address fields.
- CRC capture and DPP format-conversion tests exercise `DPP_TOP0_DPP_CRC_*`, `CNVC_CFG0_CNVC_SURFACE_PIXEL_FORMAT`, and `CNVC_CFG0_FORMAT_CONTROL`.
- Power-management and clock-gating tests exercise HUBP/HUBPREQ/HUBPRET/CURSOR memory power fields plus `DPP_TOP0_DPP_CONTROL` and `DPP_TOP0_DPP_SOFT_RESET`.
