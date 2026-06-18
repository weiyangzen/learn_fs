# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_0_2_sh_mask.h lines 9816-12326

## Scope And Purpose

This chunk covers 2,511 lines from the generated AMD DCN 3.0.2 shift/mask header. It contains C preprocessor constants only: 2,106 `#define` entries, including 1,054 `__SHIFT` definitions and 1,069 `_MASK` definitions, plus generated register and address-block comments. There are no functions, structs, enums, global storage objects, or runtime branches in this range.

The range is a hardware-register field map for display pipe memory input blocks. It starts at the tail of the `HUBP1_DCSURF_ADDR_CONFIG` field group, completes most of HUBP/HUBPREQ/HUBPRET/cursor/perfmon instance 1, covers complete instance 2 and most of instance 3, and ends inside `HUBPRET3_HUBPRET_MEM_PWR_CTRL`. In display-driver terms, this is the bit-layout contract used by DCN 3.0.2 HUBP and HUBPREQ programming code to pack and extract surface, viewport, flip, prefetch, cursor, DMDATA, VM, QoS, timing, memory-power, interrupt, and perfmon fields.

Although this repository path is under `sources/distributed-fs/ceph-client`, this file is imported Linux AMD GPU display-driver register metadata, not Ceph filesystem logic.

## Register Blocks Covered

The first section finishes and then continues the `dce_dc_dcbubp1_dispdec_hubp_dispdec` block. It includes `HUBP1_DCSURF_TILING_CONFIG`, primary and secondary viewport start/dimension registers for luma and chroma planes, request sizing for luma/chroma, `DCHUBP_CNTL`, HUBP clock control, VMPG page-size config, and DCFCLK/DPPCLK measurement-window controls. These fields describe surface swizzle/tiling, viewport geometry, memory request granularity, blank/disable/underflow/timeout state, VTG selection, TTU enablement, clock gating/status, and perfmon measurement windows.

`dce_dc_dcbubp1_dispdec_hubpreq_dispdec` covers HUBPREQ instance 1. It defines surface pitch, VMID, primary/secondary luma/chroma surface addresses, primary/secondary metadata addresses, TMZ and DCC controls, flip control and flip interrupt status, in-use and earliest-in-use address readbacks, request expansion modes, TTU QoS watermarks, global/surface/cursor TTU controls, DMDATA VM control, VM system aperture and L1 TLB controls, blank/destination/prefetch timing, vblank/flip/nominal request timing parameters, per-line delivery timing, cursor request settings, reference-to-pixel frequency ratio, DRQ limit, HUBPREQ memory power control/status, and the DCN 2.1-era VM group timing additions.

`dce_dc_dcbubp1_dispdec_hubpret_dispdec` covers HUBPRET instance 1. It maps DET buffer base, 3-to-2 packing disable, crossbar source selection, DET/DMROB/PIXCDC memory power control and status, pipe read-line ranges, vblank/read-line interrupt mask/type/clear/status bits, read-line value snapshots, and read-line status bits.

`dce_dc_dcbubp1_dispdec_cursor0_dispdec` covers cursor instance `CURSOR0_1`. It defines cursor enable/mode/magnify/TMZ/snoop/system/pitch/lines-per-chunk/perfmon bits, cursor base address, size, position, hot spot, stereo offsets, destination X offset, CROB memory power control/status, DMDATA hardware address flags, DMDATA control/QoS/status, software DMDATA control, and software DMDATA data payload.

`dce_dc_dcbubp1_dispdec_hubp_dcperfmon_dc_perfmon_dispdec` covers `DC_PERFMON7`, the HUBP instance 1 perfmon block. It includes counter event selection, counted-value selection, increment mode, run/stop control, interrupt enable/status/ack, counter state selection for counters 0-7, perfmon state/report count/counter-off interrupt control, run-enable start/stop selection, captured value high/low fields, and read selection.

The instance 2 blocks repeat the same structure under `HUBP2`, `HUBPREQ2`, `HUBPRET2`, `CURSOR0_2`, and `DC_PERFMON8`. This range includes the full HUBP2/HUBPREQ2/HUBPRET2/cursor/perfmon field families, including surface address and metadata registers, DCC/TMZ control, flip sequencing, DMDATA VM status, TTU timing, request memory-power state, read-line interrupts, cursor DMDATA, and perfmon control/readback.

The instance 3 blocks begin at `dce_dc_dcbubp3_dispdec_hubp_dispdec`. The chunk covers `HUBP3` and `HUBPREQ3` in the same detail as the earlier instances, including surface geometry, request sizing, flip, VM, TTU, DMDATA, prefetch, vblank/flip/nominal timing, memory-power, and VM-group timing fields. It then starts `HUBPRET3`, covering `HUBPRET3_HUBPRET_CONTROL` and the beginning of `HUBPRET3_HUBPRET_MEM_PWR_CTRL`; the remaining HUBPRET3 fields continue in the next chunk.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro naming convention:

- `<BLOCK><instance>_<REGISTER>__<FIELD>__SHIFT` gives the field's low bit position in a 32-bit MMIO register.
- `<BLOCK><instance>_<REGISTER>__<FIELD>_MASK` gives the already-shifted field mask.
- Address-block comments such as `// addressBlock: dce_dc_dcbubp2_dispdec_hubpreq_dispdec` group fields by replicated hardware block.
- Register comments such as `//HUBPREQ2_DCSURF_FLIP_CONTROL` delimit logical MMIO registers.

The main field families are:

- `HUBP*_DCSURF_*`: surface pixel format, address configuration, tiling, luma/chroma primary and secondary viewport geometry.
- `HUBP*_DCHUBP_*`: request-size configuration, blank/disable/status control, clock control, VMPG page-size config, and measure-window controls.
- `HUBPREQ*_DCSURF_*`: pitch, VMID, base addresses, metadata addresses, DCC/TMZ control, flip control, flip interrupts, and in-use/earliest-in-use readback.
- `HUBPREQ*_DCN_*`: request expansion, TTU QoS, per-surface/per-cursor delivery timing, DMDATA VM, system aperture, and L1 TLB controls.
- `HUBPREQ*_{BLANK,DST,PREFETCH,VBLANK,FLIP,NOM,PER_LINE,CURSOR,REF_FREQ,DST_Y}_*`: display timing and delivery-parameter fields that feed DLG/TTU programming.
- `HUBPRET*_HUBPRET_*`: return-side DET/crossbar setup, memory power, read-line windows, read-line/vblank interrupt state, and live read-line snapshots.
- `CURSOR0_*_*`: cursor image address/geometry/control, cursor memory power, and cursor-attached DMDATA hardware/software payload controls.
- `DC_PERFMON7` and `DC_PERFMON8`: HUBP perfmon counter control, state, interrupts, and readback fields.

This chunk is consumed indirectly by AMD display register helpers. In DCN 3.0.2 resource setup, `display/dc/resource/dcn302/dcn302_resource.c` includes `dcn/dcn_3_0_2_sh_mask.h` and builds `hubp_shift` and `hubp_mask` from `HUBP_MASK_SH_LIST_DCN30(__SHIFT)` and `HUBP_MASK_SH_LIST_DCN30(_MASK)`. The matching register addresses come from `dcn/dcn_3_0_2_offset.h`, using macros such as `SRI(DCN_DMDATA_VM_CNTL, HUBPREQ, id)` and `HUBP_REG_LIST_DCN30(id)`.

## Control Flow And Runtime Use

This header has no runtime control flow. Its effective flow is preprocessor and MMIO-helper expansion:

1. DCN 3.0.2 resource code includes the matching offset and shift/mask headers.
2. Register-list macros instantiate per-pipe register-address tables for HUBP/HUBPREQ/HUBPRET/cursor blocks.
3. Shift/mask-list macros populate field tables by resolving tokens like `HUBP0_DCHUBP_CNTL__HUBP_BLANK_EN__SHIFT` or `HUBPREQ0_DCSURF_FLIP_CONTROL__SURFACE_UPDATE_LOCK_MASK`.
4. Runtime HUBP code calls helpers such as `REG_UPDATE`, `REG_GET`, `REG_SET`, `REG_WRITE`, and `REG_WAIT`; those helpers use the populated tables to read, mask, shift, update, and write 32-bit MMIO registers.

Representative runtime consumers are the DC hubp implementations under `display/dc/hubp/`. DCN 1.x/2.x/3.x HUBP code updates `DCHUBP_CNTL` for blanking, disable/reset, VTG selection, underflow clear, and no-outstanding-request polling; updates `DCSURF_FLIP_CONTROL` and `DCSURF_FLIP_CONTROL2` for surface update locks, stereo-sync flips, GSL, and triple buffering; writes cursor and DMDATA registers; and reads status fields for flip pending, DMDATA done, and HUBP state snapshotting. The exact DCN 3.0.2 shift/mask constants in this chunk make those generic paths hit the correct instance-specific bit positions.

## State And Persistence Behavior

The header itself stores no state and persists nothing. It describes state held in GPU display-engine MMIO registers:

- Surface and viewport fields represent the programmed scanout buffer shape, luma/chroma geometry, swizzle, DCC/TMZ settings, metadata surfaces, and primary/secondary surface address state. These usually persist until the next plane programming update, flip, HUBP disable, or display reset.
- Flip-control fields represent synchronization state around surface updates: update locks, flip type, vupdate skip count, pending flags, stereo-sync controls, pending delay/minimum time, GSL enable, and triple-buffer enable. Some fields are control bits; others are live status bits.
- HUBP control fields represent pipeline enable/blanking, VTG routing, TTU behavior, timeout/underflow status, and clear bits. Underflow and timeout clear fields have event-style semantics, so writes are not durable configuration in the same way as VTG or blanking fields.
- Request timing fields encode DLG/TTU and memory-request timing for vblank, flip, and nominal scanout: PTE/meta/VM group cycles, destination-Y intervals, prefetch ratios, per-line delivery, and DRQ limits. These persist as the timing program for a mode until recalculated or reset.
- VM and address fields represent VMID, L1 TLB enable/mode, system aperture bounds, DMDATA VM timing, VM fault/underflow/late status, and status-clear bits.
- Cursor fields represent cursor image address, size, position, hot spot, stereo offsets, DMDATA payload source, DMDATA QoS, update toggles, memory-power state, and completion/underflow status.
- HUBPRET fields represent return-side DET/crossbar setup, memory-power state, vblank/read-line interrupt configuration and status, and current/snapshot read-line position.
- Perfmon fields represent selected counted events, counter state, run/stop gating, interrupt state/acknowledge, and counter readback values.

Persistence is hardware-defined. Control fields remain programmed until later MMIO writes or reset events. Status fields reflect live hardware and may be sticky until a corresponding clear/ack bit is written. This header does not encode access direction; writable controls, read-only status, and write-to-clear fields all use the same macro style.

## Dependencies And Integration Points

This chunk depends on the generated DCN 3.0.2 register database staying synchronized across files:

- `dcn_3_0_2_offset.h` supplies the register addresses and base indices for the register names whose fields are defined here.
- `display/dc/resource/dcn302/dcn302_resource.c` includes this header and builds the DCN 3.0.2 HUBP register, shift, and mask tables.
- `display/dc/hubp/dcn30/dcn30_hubp.h`, `dcn20_hubp.h`, `dcn21_hubp.h`, and related hubp headers define `HUBP_REG_LIST_*` and `HUBP_MASK_SH_LIST_*` macros that expect the generated names to exist with the `HUBP0`/`HUBPREQ0`/`CURSOR0_0` token forms.
- The generic register helpers in `reg_helper.h` consume the populated shift/mask fields for MMIO reads and updates.
- Higher-level display workflows integrate through plane programming, page flips, cursor updates, DMDATA metadata programming, VM fault handling, watermarks/DLG/TTU calculation, suspend/resume restore, and underflow diagnostics.
- IRQ metadata under `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h` names related HUBP flip, flip-away, VM-context-error, vblank/vline, and perfcounter interrupt sources for instances 1-3; this header provides the bitfield side for some per-block interrupt/status registers.

The key integration contract is preprocessor naming plus numeric correctness. Missing or renamed macros usually break compilation when resource tables are built. Wrong masks or shifts can compile and only fail as incorrect hardware behavior on a specific pipe.

## Risks And Edge Cases

- The chunk boundaries are partial. It starts after the beginning of `HUBP1_DCSURF_ADDR_CONFIG` and ends inside `HUBPRET3_HUBPRET_MEM_PWR_CTRL`; final per-file reconciliation must combine adjacent chunks before claiming complete coverage of those two register groups.
- Instance replication hides drift. HUBP/HUBPREQ/HUBPRET/cursor/perfmon blocks for instances 1, 2, and 3 are mechanically similar, so a one-bit error in one instance may appear as a pipe-specific display failure rather than a compile-time problem.
- Shift/mask errors in address, VMID, TMZ, DCC, and metadata fields can cause scanout from the wrong memory, incorrect protected-memory handling, bad DCC interpretation, VM faults, or stale metadata fetches.
- Flip-control fields mix controls and status. Mispacking `SURFACE_UPDATE_LOCK`, `SURFACE_FLIP_PENDING`, stereo-sync fields, GSL, or triple-buffer fields can deadlock updates, miss vblank synchronization, or produce stale scanout.
- Several registers pack luma and chroma values together. Mistakes in `_C` fields, viewport fields, pitch fields, and chroma timing fields can affect multi-plane formats such as NV12/P010 differently from RGB formats.
- Timing fields are tightly width-limited, often using 7-bit, 13-bit, 17-bit, 21-bit, or 23-bit masks. Callers must clamp/calibrate values before packing; this header only supplies masks and cannot validate display-mode math.
- Clear/ack/status fields such as underflow clear, timeout clear, flip interrupt clear, DMDATA VM fault clear, DMDATA underflow clear, read-line interrupt clear, and perfcounter interrupt ack have side effects. Treating them like ordinary persistent configuration can clear evidence or leave interrupts stuck.
- Cross-generation reuse is risky. Nearby DCN 3.2+ headers add or rename some HUBP fields such as soft reset, unbounded request mode, segment allocation error, or cursor request mode. DCN 3.0.2 code must use the header matching its offset table and ASIC resource path.
- Full-register masks such as surface address low words and perfmon low-value words require unsigned 32-bit handling. Sign extension or host-width assumptions around `0xFFFFFFFFL` can distort debug or register-composition code on unusual build targets.

## Test Signals

Build-time signals:

- Compile DCN 3.0.2 AMD display resource and HUBP code that includes `dcn_3_0_2_sh_mask.h`; missing generated names should surface through `HUBP_REG_LIST_DCN30` and `HUBP_MASK_SH_LIST_DCN30` expansion.
- Preprocess `dcn302_resource.c` to confirm `hubp_shift` and `hubp_mask` resolve the expected `HUBP*`, `HUBPREQ*`, and `CURSOR0_*` macros against `dcn_3_0_2_offset.h`.
- Statically compare this generated header with the authoritative register database and adjacent instance blocks to catch one-instance mask/shift drift.

Runtime and hardware signals:

- Exercise multi-pipe scanout on DCN 3.0.2 hardware, especially pipes 1-3, with RGB and multi-plane YUV formats to validate viewport, pitch, chroma, DCC, and address fields.
- Run page-flip tests with immediate, vblank-synchronized, stereo-sync, GSL, and triple-buffer paths; monitor `SURFACE_FLIP_PENDING`, flip interrupts, and in-use/earliest-in-use address readbacks.
- Move and resize hardware cursors, enable/disable cursor surfaces, and exercise DMDATA hardware/software modes while checking `DMDATA_DONE`, underflow, QoS, address, and update toggles.
- Validate underflow handling by checking `HUBP_UNDERFLOW_STATUS` and `HUBP_UNDERFLOW_CLEAR`, plus timeout status/clear behavior if the platform exposes it.
- Test modes with different timing and memory-pressure profiles to verify DLG/TTU fields: prefetch ratio, vblank/flip/nominal PTE/meta/VM group cycles, per-line delivery, and DRQ limit.
- Exercise suspend/resume, display reset, and power-gating paths while watching HUBP/HUBPREQ/HUBPRET/cursor memory-power status fields and restored plane/cursor state.
- Use perfmon/debug tooling, where available, to program `DC_PERFMON7` and `DC_PERFMON8` counters, verify interrupt ack/status behavior, and confirm readback high/low values increment for selected events.

## Open Cross-Chunk Questions

- The previous chunk should be merged with this one to present the complete `HUBP1_DCSURF_ADDR_CONFIG` field group.
- The next chunk should be merged with this one to present complete `HUBPRET3_HUBPRET_MEM_PWR_CTRL` and the remaining HUBPRET3 read-line/interrupt/status groups.
- Whole-file reconciliation should verify whether all expected DCN 3.0.2 HUBP instances are present and whether the repeated instance layouts are intentionally identical or contain ASIC-specific deltas.
