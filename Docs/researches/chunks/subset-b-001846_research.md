# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_sh_mask.h lines 32148-34607

## Purpose

This chunk is generated AMD DCN 3.1.4 register field metadata. It contains no executable C logic; it exposes preprocessor constants that describe bit shifts and masks for MMIO-backed display timing-generator, OPTC miscellaneous, ODM memory-power, and display perfmon registers.

The requested range covers 2,460 source lines and contains 2,142 `#define` entries: 1,066 `__SHIFT` macros and 1,076 `_MASK` macros. It starts in the middle of `OTG1_OTG_TRIGA_CNTL`, continues through the rest of the OTG1 timing-generator block, includes complete OTG2 and OTG3 timing-generator blocks, covers `dce_dc_optc_optc_misc_dispdec`, and ends at the first field of `DC_PERFMON15_PERFMON_CNTL` in the `dce_dc_optc_optc_dcperfmon_dc_perfmon_dispdec` block.

Although the local path is under a `ceph-client` source mirror, this file is AMDGPU display-driver hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, allocations, or direct register accesses in this range. The public API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit position for a named hardware field.
- `<REGISTER>__<FIELD>_MASK`: bit mask for the same field.

These constants are consumed together with `dcn_3_1_4_offset.h` and AMD display register helper macros such as `SR`, `SF`, `HWS_SF`, `REG_GET`, `REG_SET`, `REG_SET_2`, and `REG_UPDATE`. The masks and shifts are intentionally untyped; correctness depends on token-pasting the register and field names into the proper generated macro.

Major register families in this slice:

- OTG1 tail: completes `OTG1_OTG_TRIGA_CNTL` and covers manual triggers, trigger B, force-count-now, flow control, core OTG enable/control/status, interlace and stereo controls, snapshot fields, interrupt control, update locks, vertical interrupts, CRC configuration/data, static-screen controls, 3D structure fields, global sync and GSL controls, master update-lock timing windows, dynamic refresh-rate fields, M_CONST DTO, DSC start position, pipe update status, and spare register.
- Full OTG2 and OTG3 blocks: complete per-instance timing generator definitions for horizontal and vertical timing, blank/sync windows, timing dividers, vtotal min/max/mid and DRR controls, trigger A/B, flow control, stereo/interlace, status counters, snapshots, interrupts, CRC windows/data, global sync events, GSL windows, update-lock windows, DSC start position, and pipe update status.
- OPTC misc block: `GSL_SOURCE_SELECT`, `OPTC_CLOCK_CONTROL`, `ODM_MEM_PWR_CTRL`, `ODM_MEM_PWR_CTRL3`, `ODM_MEM_PWR_STATUS`, and `OPTC_MISC_SPARE_REGISTER`.
- DC perfmon block start: `DC_PERFMON15_PERFCOUNTER_CNTL`, `DC_PERFMON15_PERFCOUNTER_CNTL2`, `DC_PERFMON15_PERFCOUNTER_STATE`, and the first `DC_PERFMON15_PERFMON_CNTL__PERFMON_STATE__SHIFT` field.

The OTG fields define the low-level vocabulary for programming display scanout timing: total and active/blank counts, sync polarity/mode, live status position, frame/vblank/hv counters, vertical interrupts, update barriers, CRC sampling windows, global update lock, GSL synchronization, DRR vtotal windows, and DSC start position. OPTC misc fields provide shared global sync source routing, display-clock gating state, and ODM memory power controls. The perfmon fields define event selection, counted-value type, counter gating/stop policy, interrupt enable/status, and per-counter state selection for DC performance counters.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this generated header and constructs register tables or direct register writes from the macros:

1. DCN314 code includes `dcn/dcn_3_1_4_offset.h` and `dcn/dcn_3_1_4_sh_mask.h`.
2. Resource, timing-generator, IRQ, hwseq, and DMUB code expands register-table macros such as `SR(...)`, `SF(...)`, and `HWS_SF(...)`.
3. Register helper macros combine a selected register offset with these shift/mask constants to read, set, or update individual MMIO fields.
4. Higher-level display sequencing decides when to enable OTGs, program timing totals, lock updates, arm vertical interrupts, change DRR timing, collect CRCs, route GSL readiness, control ODM memory power, and configure perf counters.

The generated constants do not encode required order. Consumers must still follow hardware sequencing rules around blanking periods, double-buffered updates, vupdate/vready/vstartup events, update locks, interrupt ack/clear fields, power gating, DRR changes, and multi-pipe synchronization.

## State And Persistence Behavior

This chunk stores no software state and persists nothing on its own. It describes fields in hardware registers whose state is owned by the display engine.

Persistent or configuration-like hardware state represented here includes:

- Timing values: horizontal and vertical totals, blank intervals, sync intervals, sync polarity, timing divider mode, interlace/stereo modes, DSC start position, M_CONST DTO phase/modulo, and request mode.
- Enable and routing state: `OTG_MASTER_EN`, `OTG_OUT_MUX`, trigger source selections, flow-control source/polarity, GSL enable/master/source routing, global update lock selection, DIG update position, and OPTC display-clock gate/test-clock settings.
- Power policy: ODM memory force/disable fields, unassigned and vblank power modes, and per-bank memory power status fields.
- Perfmon setup: selected perf event, count mode, run-enable mode, hardware stop selection, count-off source, restart and interrupt enable policy, counter select, and per-counter state selectors.

Volatile or event-like hardware state includes:

- Current scanout status: vblank/hblank/active/sync bits, vertical/horizontal counters, nominal vertical count, frame/vf/hv counters, current field/eye, current master enable state, and pipe update pending flags.
- Sticky events and interrupts: trigger occurred bits, force-count-now occurred/clear, force-vsync-next-line occurred/clear, snapshot occurred/clear/manual trigger, vertical interrupt status/clear, vtotal-min event ack/mask, DRR timing/vtotal-reach event clear, global vstartup/vupdate/vready event clear/status, perf counter interrupt status/ack, and count-off interrupt state.
- Measurement outputs: pixel readback values, CRC data registers, CRC one-shot pending bits, global sync status bits, ODM power-state readback, and perf counter active/state readback.

Persistence and side effects are hardware-defined. Many configuration fields retain values until modeset, reset, suspend/resume restore, power-gating transition, or ASIC reset. Status and interrupt fields may be read-only, sticky, self-clearing, write-one-to-clear, or clear-on-write. This mask header does not identify access permissions or side effects; caller logic and hardware documentation must supply that knowledge.

## Dependencies And Integration Points

This generated mask chunk must match `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_1_4_offset.h`, which provides the corresponding register offsets and base-index selectors. A mismatch between the offset and mask files can compile but write the wrong bits in the wrong register.

Direct include sites for this DCN314 mask header in the tree include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c`, which builds DMUB service register tables for DCN 3.1.4.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn314/irq_service_dcn314.c`, which maps DCN314 hardware interrupt registers and fields into DAL IRQ sources.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn314/dcn314_resource.c`, which constructs the DCN314 resource pool and hardware register/field tables.

The OTG and GSL fields integrate with timing-generator code under `display/dc/optc`, especially `dcn314_optc.h` and the inherited DCN timing-generator functions. `GSL_SOURCE_SELECT` is exposed in DCN314 OPTC register definitions and is used by shared timing-generator sequencing for global sync lock source routing. ODM memory-power fields integrate with hwseq/resource code through `ODM_MEM_PWR_CTRL3` register definitions and `HWS_SF` field mappings. The DC perfmon fields integrate with the broader DC perfmon infrastructure that programs event selectors and counter state through generated register tables.

The chunk is source-tree-aligned with generated ASIC register metadata, not with Ceph. It should be merged with adjacent chunks for complete file-level claims because it begins mid-register in OTG1 and ends mid-register in the perfmon15 block.

## Risks And Edge Cases

- Shift/mask drift is the primary risk. These are raw constants, so a wrong bit position or mask can compile cleanly while corrupting unrelated hardware fields.
- Chunk boundaries are partial. The range starts after earlier `OTG1_OTG_TRIGA_CNTL` fields and stops after only `DC_PERFMON15_PERFMON_CNTL__PERFMON_STATE__SHIFT`; final per-file analysis must reconcile neighboring chunks.
- OTG instances are highly repetitive. Copy or generator errors can affect only one timing generator, producing failures limited to one pipe, connector, or multi-display topology.
- Many fields are sequencing-sensitive. Update locks, double-buffer pending flags, vstartup/vupdate/vready events, vertical interrupts, DRR timing updates, and clear/ack fields can race with scanout if updated outside the intended blanking or lock window.
- Interrupt and status fields are side-effect-prone. Blind read-modify-write can accidentally clear sticky events or acknowledge interrupts if the field access type is not respected.
- DRR and vtotal fields affect visible timing. Incorrect min/max/mid vtotal, trigger windows, or vtotal-reach masks can cause VRR/FreeSync instability, frame pacing issues, flicker, or stuck timing updates.
- CRC and pixel-readback fields are test-critical but easy to misconfigure. Wrong CRC window, selection, interlace/stereo mode, or one-shot pending handling can make display validation report false failures.
- GSL/global update lock fields coordinate multiple pipes. Incorrect source selection, timing windows, or master mode can break synchronized flips, ODM/MPC multi-pipe updates, or stereo/interlaced update ordering.
- ODM memory power control can affect power and stability. Incorrect force/disable/vblank power fields may leave memory blocks powered unnecessarily or power them down while still needed.
- Perfmon fields pack many control bits in one register. Incorrect event selection, counter select, interrupt enable, or stop/run mode can produce misleading counters or interrupt storms.

## Test Signals

Useful validation signals are a mix of generated-header consistency checks and hardware/display behavior:

- Build AMDGPU display, DCN314 resource, IRQ, OPTC, hwseq, and DMUB paths that include `dcn_3_1_4_sh_mask.h`; missing or renamed macros should fail in register table construction.
- Mechanically verify that every complete field in lines 32148-34607 has a consistent shift/mask pair, accounting for the intentional partial `OTG1_OTG_TRIGA_CNTL` and `DC_PERFMON15_PERFMON_CNTL` boundaries.
- Diff this range against AMD's authoritative DCN 3.1.4 register database and neighboring DCN generated headers where field layouts are expected to match.
- Exercise DCN314 modesets across one, two, and three active OTGs, including enable/disable, blank/unblank, hotplug, suspend/resume, link retraining, and display clock changes.
- Validate scanout timing through mode programming that stresses horizontal/vertical totals, sync polarity, interlace, stereo, DSC start position, and horizontal timing divider behavior.
- Test synchronized updates: atomic flips, cursor updates, multi-plane updates, ODM or multi-pipe configurations, global update lock, GSL source selection, and vupdate keepout windows.
- Exercise DRR/VRR paths and watch for vtotal-min, DRR timing update, and vtotal-reach interrupts, plus visible flicker, frame pacing errors, or stuck pending update bits.
- Use debug CRC and pixel-readback paths to confirm CRC window selection, one-shot/continuous CRC behavior, stereo/interlace CRC modes, and CRC data readout.
- Check IRQ handling for vertical interrupts, snapshot interrupts, trigger interrupts, force-count-now, force-vsync-next-line, vstartup/vupdate/vready events, and perfmon count-off/per-counter interrupts.
- Monitor power-management behavior around ODM memory power controls and OPTC display-clock gating with runtime PM, blanked displays, idle optimization, and resume.
- Use DC perfmon tooling or debug hooks to confirm event selection, counter active state, interrupt status/ack, and count-off behavior on DC perfmon15.

## Cross-Chunk Notes

Previous chunks own the beginning of the DCN314 OPTC/OTG metadata and the earlier part of `OTG1_OTG_TRIGA_CNTL`. Later chunks own the remainder of the DC perfmon15 block after `DC_PERFMON15_PERFMON_CNTL__PERFMON_STATE__SHIFT`. The final per-file research document should merge those boundaries before making complete claims about all DCN314 OTG, OPTC misc, and perfmon register fields.
